"""Background evaluation jobs — persist progress across Streamlit page navigation."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import AGENT_ROOT, Workspace, default_workspace
from .notify import send_eval_complete_email, send_eval_failed_email
from .runner import run_evaluation_streaming

JOB_STATE_NAME = ".eval_active_job.json"
JOB_LOG_NAME = ".eval_active_job.log"
_PERSONA_START_RE = re.compile(r"persona (\S+) session")
_PERSONA_DONE_RE = re.compile(r"\] (\S+) truth=")


def job_state_path(ws: Workspace) -> Path:
    return ws.root / JOB_STATE_NAME


def job_log_path(ws: Workspace) -> Path:
    return ws.root / JOB_LOG_NAME


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_job_state(ws: Workspace) -> dict[str, Any] | None:
    path = job_state_path(ws)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def save_job_state(ws: Workspace, state: dict[str, Any]) -> None:
    ws.ensure_dirs()
    state["updated_utc"] = _now()
    job_state_path(ws).write_text(json.dumps(state, indent=2), encoding="utf-8")


def append_job_log(ws: Workspace, line: str) -> None:
    ws.ensure_dirs()
    with job_log_path(ws).open("a", encoding="utf-8") as handle:
        handle.write(line.rstrip() + "\n")


def read_job_log_tail(ws: Workspace, max_lines: int = 150) -> str:
    path = job_log_path(ws)
    if not path.is_file():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-max_lines:])


def _pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _inflight_from_lines(lines: list[str]) -> int:
    started: set[str] = set()
    done: set[str] = set()
    for line in lines:
        for match in _PERSONA_START_RE.finditer(line):
            started.add(match.group(1))
        for match in _PERSONA_DONE_RE.finditer(line):
            done.add(match.group(1))
    return len(started - done)


def sync_job_state(ws: Workspace) -> dict[str, Any] | None:
    state = load_job_state(ws)
    if not state:
        return None
    if state.get("status") == "running" and not _pid_alive(state.get("pid")):
        state["status"] = "failed"
        state["error"] = state.get("error") or "Background process stopped unexpectedly."
        save_job_state(ws, state)
    return state


def job_is_active(state: dict[str, Any] | None) -> bool:
    return bool(state and state.get("status") in {"pending", "running"})


def start_background_evaluation(
    ws: Workspace,
    *,
    model_key: str,
    prompt_key: str,
    prompt_label: str,
    dataset_xlsx: Path,
    dataset_sheet: str,
    run_label: str,
    resume: bool,
    eval_limit: int | None,
    parallel_workers: int,
    notify_email: str,
) -> None:
    existing = sync_job_state(ws)
    if job_is_active(existing):
        raise RuntimeError("An evaluation is already running. Wait for it to finish.")

    job_log_path(ws).write_text("", encoding="utf-8")
    state: dict[str, Any] = {
        "job_id": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        "status": "pending",
        "pid": None,
        "started_utc": _now(),
        "updated_utc": _now(),
        "completed": 0,
        "total": 0,
        "remaining": 0,
        "in_flight": 0,
        "run_label": run_label,
        "dataset": dataset_xlsx.name,
        "dataset_sheet": dataset_sheet,
        "model_key": model_key,
        "prompt_key": prompt_key,
        "prompt_label": prompt_label,
        "resume": resume,
        "eval_limit": eval_limit,
        "parallel_workers": parallel_workers,
        "notify_email": (notify_email or "").strip(),
        "result_run_id": None,
        "error": None,
        "email_status": None,
    }
    save_job_state(ws, state)

    env = os.environ.copy()
    env["AFW_WORKSPACE_ROOT"] = str(ws.root)
    env["PYTHONUNBUFFERED"] = "1"
    cmd = [sys.executable, "-m", "afw_eval_agent.background_job"]
    popen_kwargs: dict[str, Any] = {
        "cwd": str(AGENT_ROOT),
        "env": env,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name != "nt":
        popen_kwargs["start_new_session"] = True
    proc = subprocess.Popen(cmd, **popen_kwargs)
    state["status"] = "running"
    state["pid"] = proc.pid
    save_job_state(ws, state)


def _update_progress_from_event(state: dict[str, Any], event: dict[str, Any], log_lines: list[str]) -> None:
    if event["type"] == "start":
        state["total"] = event["total"]
        state["completed"] = event.get("completed", 0)
        state["remaining"] = event.get("remaining", event["total"])
    elif event["type"] == "progress":
        state["completed"] = event["completed"]
        state["total"] = event["total"]
        state["remaining"] = event["remaining"]
        state["in_flight"] = _inflight_from_lines(log_lines)
    elif event["type"] == "complete":
        state["completed"] = state.get("total", event.get("total", 0))
        state["remaining"] = 0
        state["in_flight"] = 0
        state["result_run_id"] = event["entry"]["run_id"]


def execute_job(workspace_root: Path | None = None) -> int:
    ws = Workspace(workspace_root or default_workspace())
    ws.ensure_dirs()
    state = load_job_state(ws)
    if not state:
        return 1

    state["status"] = "running"
    state["pid"] = os.getpid()
    save_job_state(ws, state)
    job_log_path(ws).write_text("", encoding="utf-8")

    log_lines: list[str] = []
    entry: dict[str, Any] | None = None
    try:
        for event in run_evaluation_streaming(
            workspace=ws,
            model_key=state["model_key"],
            prompt_key=state["prompt_key"],
            prompt_label=state["prompt_label"],
            prompt_file=None,
            dataset_xlsx=ws.datasets / state["dataset"],
            dataset_sheet=state["dataset_sheet"],
            run_label=state["run_label"],
            resume=bool(state.get("resume")),
            eval_limit=state.get("eval_limit"),
            parallel_workers=int(state.get("parallel_workers", 6)),
        ):
            if event["type"] == "log":
                line = event["line"]
                log_lines.append(line)
                append_job_log(ws, line)
            _update_progress_from_event(state, event, log_lines)
            save_job_state(ws, state)
            if event["type"] == "complete":
                entry = event["entry"]

        if entry is None:
            raise RuntimeError("Evaluation finished without saving a run.")

        state["status"] = "completed"
        state["result_run_id"] = entry["run_id"]
        state["error"] = None
        save_job_state(ws, state)

        notify_email = str(state.get("notify_email", "")).strip()
        if notify_email:
            ok, msg = send_eval_complete_email(
                notify_email,
                run_id=entry["run_id"],
                run_label=state["run_label"],
                dataset=state["dataset"],
                model_display=entry.get("model_display", state["model_key"]),
                prompt_label=state["prompt_label"],
                completed=state.get("completed", state.get("total", 0)),
                total=state.get("total", 0),
            )
            state["email_status"] = msg if ok else f"Failed: {msg}"
            save_job_state(ws, state)
        return 0
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = str(exc)
        append_job_log(ws, f"ERROR: {exc}")
        save_job_state(ws, state)
        notify_email = str(state.get("notify_email", "")).strip()
        if notify_email:
            ok, msg = send_eval_failed_email(
                notify_email,
                run_label=state.get("run_label", "eval"),
                error=str(exc),
            )
            state["email_status"] = msg if ok else f"Failed: {msg}"
            save_job_state(ws, state)
        return 1


def main() -> None:
    root = Path(os.environ.get("AFW_WORKSPACE_ROOT", default_workspace()))
    raise SystemExit(execute_job(root))


if __name__ == "__main__":
    main()
