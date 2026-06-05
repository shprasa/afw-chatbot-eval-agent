"""Background evaluation jobs — per-user (email) progress and cancellation."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import AGENT_ROOT, Workspace, default_workspace
from .notify import send_eval_complete_email, send_eval_failed_email
from .runner import run_evaluation_streaming

JOBS_DIR = ".eval_jobs"
_PERSONA_START_RE = re.compile(r"persona (\S+) session")
_PERSONA_DONE_RE = re.compile(r"\] (\S+) truth=")


def normalize_owner_email(email: str) -> str:
    value = (email or "").strip().lower()
    if not value or "@" not in value:
        raise ValueError("A valid email address is required.")
    return value


def _email_dir_key(email: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", normalize_owner_email(email)).strip("_")[:80]


def job_dir(ws: Workspace, owner_email: str) -> Path:
    path = ws.root / JOBS_DIR / _email_dir_key(owner_email)
    path.mkdir(parents=True, exist_ok=True)
    return path


def job_state_path(ws: Workspace, owner_email: str) -> Path:
    return job_dir(ws, owner_email) / "active_job.json"


def job_log_path(ws: Workspace, owner_email: str) -> Path:
    return job_dir(ws, owner_email) / "active_job.log"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_job_state(ws: Workspace, owner_email: str) -> dict[str, Any] | None:
    if not (owner_email or "").strip():
        return None
    path = job_state_path(ws, owner_email)
    if not path.is_file():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    stored = normalize_owner_email(str(state.get("owner_email", state.get("notify_email", ""))))
    if stored != normalize_owner_email(owner_email):
        return None
    return state


def save_job_state(ws: Workspace, owner_email: str, state: dict[str, Any]) -> None:
    ws.ensure_dirs()
    state["owner_email"] = normalize_owner_email(owner_email)
    state["notify_email"] = state.get("notify_email") or state["owner_email"]
    state["updated_utc"] = _now()
    job_state_path(ws, owner_email).write_text(json.dumps(state, indent=2), encoding="utf-8")


def append_job_log(ws: Workspace, owner_email: str, line: str) -> None:
    ws.ensure_dirs()
    with job_log_path(ws, owner_email).open("a", encoding="utf-8") as handle:
        handle.write(line.rstrip() + "\n")


def read_job_log_tail(ws: Workspace, owner_email: str, max_lines: int = 150) -> str:
    path = job_log_path(ws, owner_email)
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


def _terminate_pid(pid: int | None) -> None:
    if not pid or pid <= 0:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                check=False,
                capture_output=True,
            )
        else:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
    except (ProcessLookupError, OSError):
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass


def _inflight_from_lines(lines: list[str]) -> int:
    started: set[str] = set()
    done: set[str] = set()
    for line in lines:
        for match in _PERSONA_START_RE.finditer(line):
            started.add(match.group(1))
        for match in _PERSONA_DONE_RE.finditer(line):
            done.add(match.group(1))
    return len(started - done)


def sync_job_state(ws: Workspace, owner_email: str) -> dict[str, Any] | None:
    state = load_job_state(ws, owner_email)
    if not state:
        return None
    if state.get("status") in {"running", "cancelling"} and not _pid_alive(state.get("pid")):
        if state.get("status") == "cancelling" or "cancel" in str(state.get("error", "")).lower():
            state["status"] = "cancelled"
            state["error"] = state.get("error") or "Cancelled by user."
        else:
            state["status"] = "failed"
            state["error"] = state.get("error") or "Background process stopped unexpectedly."
        save_job_state(ws, owner_email, state)
    return state


def job_is_active(state: dict[str, Any] | None) -> bool:
    return bool(state and state.get("status") in {"pending", "running", "cancelling"})


def cancel_job(ws: Workspace, owner_email: str) -> None:
    email = normalize_owner_email(owner_email)
    state = sync_job_state(ws, email)
    if not job_is_active(state):
        raise RuntimeError("No running evaluation to cancel for this email.")

    state["status"] = "cancelling"
    state["error"] = "Cancelled by user."
    save_job_state(ws, email, state)
    append_job_log(ws, email, "CANCELLED by user.")
    _terminate_pid(state.get("pid"))

    state["status"] = "cancelled"
    state["pid"] = None
    save_job_state(ws, email, state)


def clear_job(ws: Workspace, owner_email: str) -> None:
    email = normalize_owner_email(owner_email)
    for path in (job_state_path(ws, email), job_log_path(ws, email)):
        if path.is_file():
            path.unlink()


def start_background_evaluation(
    ws: Workspace,
    *,
    owner_email: str,
    model_key: str,
    prompt_key: str,
    prompt_label: str,
    dataset_xlsx: Path,
    dataset_sheet: str,
    run_label: str,
    resume: bool,
    eval_limit: int | None,
    parallel_workers: int,
) -> None:
    email = normalize_owner_email(owner_email)
    existing = sync_job_state(ws, email)
    if job_is_active(existing):
        raise RuntimeError(
            "You already have an evaluation running for this email. "
            "Wait for it to finish or cancel it first."
        )

    job_log_path(ws, email).write_text("", encoding="utf-8")
    state: dict[str, Any] = {
        "job_id": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        "status": "pending",
        "pid": None,
        "owner_email": email,
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
        "notify_email": email,
        "result_run_id": None,
        "error": None,
        "email_status": None,
    }
    save_job_state(ws, email, state)

    env = os.environ.copy()
    env["AFW_WORKSPACE_ROOT"] = str(ws.root)
    env["AFW_JOB_OWNER_EMAIL"] = email
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
    save_job_state(ws, email, state)


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
    owner_email = os.environ.get("AFW_JOB_OWNER_EMAIL", "").strip()
    if not owner_email:
        return 1
    email = normalize_owner_email(owner_email)
    state = load_job_state(ws, email)
    if not state:
        return 1

    state["status"] = "running"
    state["pid"] = os.getpid()
    save_job_state(ws, email, state)
    job_log_path(ws, email).write_text("", encoding="utf-8")

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
            current = load_job_state(ws, email)
            if current and current.get("status") in {"cancelling", "cancelled"}:
                raise RuntimeError("Cancelled by user.")

            if event["type"] == "log":
                line = event["line"]
                log_lines.append(line)
                append_job_log(ws, email, line)
            _update_progress_from_event(state, event, log_lines)
            save_job_state(ws, email, state)
            if event["type"] == "complete":
                entry = event["entry"]

        if entry is None:
            raise RuntimeError("Evaluation finished without saving a run.")

        state["status"] = "completed"
        state["result_run_id"] = entry["run_id"]
        state["error"] = None
        save_job_state(ws, email, state)

        ok, msg = send_eval_complete_email(
            email,
            run_id=entry["run_id"],
            run_label=state["run_label"],
            dataset=state["dataset"],
            model_display=entry.get("model_display", state["model_key"]),
            prompt_label=state["prompt_label"],
            completed=state.get("completed", state.get("total", 0)),
            total=state.get("total", 0),
        )
        state["email_status"] = msg if ok else f"Failed: {msg}"
        save_job_state(ws, email, state)
        return 0
    except Exception as exc:
        cancelled = "cancel" in str(exc).lower()
        state["status"] = "cancelled" if cancelled else "failed"
        state["error"] = str(exc)
        append_job_log(ws, email, f"ERROR: {exc}")
        save_job_state(ws, email, state)
        if not cancelled:
            ok, msg = send_eval_failed_email(
                email,
                run_label=state.get("run_label", "eval"),
                error=str(exc),
            )
            state["email_status"] = msg if ok else f"Failed: {msg}"
            save_job_state(ws, email, state)
        return 1


def main() -> None:
    root = Path(os.environ.get("AFW_WORKSPACE_ROOT", default_workspace()))
    raise SystemExit(execute_job(root))


if __name__ == "__main__":
    main()
