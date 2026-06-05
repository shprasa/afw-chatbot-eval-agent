"""Run chatbot_live_eval.py as a subprocess and archive outputs to workspace."""

from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import sys
import threading
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .config import AGENT_ROOT, Workspace
from .powerbi_export import export_powerbi_data
from .registry import get_model, list_prompt_labels, resolve_prompt_reference_file


def _safe_suffix(text: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in "-_" else "_" for c in text.strip())
    return cleaned[:60] or "run"


def build_output_suffix(
    model_key: str,
    prompt_key: str,
    prompt_label: str,
    run_label: str,
) -> str:
    known = list_prompt_labels().get(prompt_key, {}).get("label", "")
    parts = [_safe_suffix(run_label), model_key, prompt_key]
    if prompt_label and prompt_label != known:
        parts.append(_safe_suffix(prompt_label))
    return "_" + "_".join(parts)


def build_env(
    *,
    model_key: str,
    prompt_key: str,
    prompt_label: str,
    prompt_file: Path | None,
    dataset_xlsx: Path,
    dataset_sheet: str,
    output_suffix: str,
    workspace: Workspace,
    resume: bool = False,
    eval_limit: int | None = None,
    parallel_workers: int = 6,
    turn_pause_s: float = 0.4,
) -> dict[str, str]:
    model = get_model(model_key)
    env = os.environ.copy()
    env["CHATBOT_WEB_BASE_URL"] = model["base_url"]
    env["CHATBOT_BACKEND"] = model.get("backend", "openai")
    env["CHATBOT_OUTPUT_SUFFIX"] = output_suffix
    env["CHATBOT_DATASET_XLSX"] = str(dataset_xlsx)
    env["CHATBOT_DATASET_SHEET"] = dataset_sheet
    env["CHATBOT_SOURCE_TAG"] = dataset_xlsx.stem
    env["CHATBOT_PARALLEL_WORKERS"] = str(parallel_workers)
    env["CHATBOT_TURN_PAUSE_S"] = str(turn_pause_s)
    if resume:
        env["CHATBOT_RESUME"] = "1"
    if eval_limit is not None:
        env["CHATBOT_EVAL_LIMIT"] = str(eval_limit)

    ref = prompt_file or resolve_prompt_reference_file(prompt_key)
    if ref and ref.is_file():
        env["CHATBOT_SYSTEM_PROMPT_FILE"] = str(ref)

    env["CHATBOT_ARTIFACTS_DIR"] = str(workspace.local_artifacts)
    env["CHATBOT_REPORTS_DIR"] = str(workspace.local_reports)
    env["PYTHONUNBUFFERED"] = "1"
    return env


def _count_completed_personas(transcript_path: Path) -> int:
    done: set[str] = set()
    if not transcript_path.is_file():
        return 0
    with transcript_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            pid = str(rec.get("persona_id", "")).strip()
            if pid and not rec.get("error"):
                done.add(pid)
    return len(done)


def estimate_eval_plan(
    *,
    dataset_xlsx: Path,
    dataset_sheet: str,
    eval_limit: int | None,
    resume: bool,
    transcript_path: Path,
) -> dict[str, int]:
    df = pd.read_excel(dataset_xlsx, sheet_name=dataset_sheet)
    total = min(len(df), eval_limit) if eval_limit else len(df)
    completed = _count_completed_personas(transcript_path) if resume else 0
    completed = min(completed, total)
    return {
        "total": total,
        "completed": completed,
        "remaining": max(total - completed, 0),
    }


def artifact_paths(suffix: str, workspace: Workspace) -> dict[str, Path]:
    art = workspace.local_artifacts
    rep = workspace.local_reports
    return {
        "predictions": art / f"chatbot_live_predictions{suffix}.csv",
        "transcripts": art / f"chatbot_live_transcripts{suffix}.jsonl",
        "accuracy_json": rep / f"chatbot_live_accuracy{suffix}.json",
        "failure_md": rep / f"chatbot_live_failure_analysis{suffix}.md",
        "prompt_md": rep / f"chatbot_live_prompt_improvements{suffix}.md",
    }


def _rel_repo_path(p: Path | str) -> str:
    try:
        return str(Path(p).resolve().relative_to(AGENT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(p).replace("\\", "/")


def _archive_run(
    *,
    workspace: Workspace,
    suffix: str,
    model_key: str,
    prompt_key: str,
    prompt_label: str,
    prompt_file: Path | None,
    dataset_xlsx: Path,
    dataset_sheet: str,
    run_label: str,
    env: dict[str, str],
) -> dict[str, Any]:
    paths = artifact_paths(suffix, workspace)
    missing = [k for k, p in paths.items() if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"expected outputs missing after run: {missing}")

    model = get_model(model_key)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"{stamp}{suffix}"
    run_dir = workspace.runs / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    archived: dict[str, str] = {}
    for key, src in paths.items():
        dest = run_dir / src.name
        shutil.copy2(src, dest)
        archived[key] = str(dest)

    dataset_copy = run_dir / dataset_xlsx.name
    if not dataset_copy.exists():
        shutil.copy2(dataset_xlsx, dataset_copy)

    rel_artifacts = {k: _rel_repo_path(v) for k, v in archived.items()}
    entry: dict[str, Any] = {
        "run_id": run_id,
        "run_label": run_label,
        "display_name": f"{run_label} | {model['display']} | {prompt_label}",
        "model_key": model_key,
        "model_display": model["display"],
        "api_base_url": model["base_url"],
        "prompt_key": prompt_key,
        "prompt_label": prompt_label,
        "prompt_file": _rel_repo_path(env.get("CHATBOT_SYSTEM_PROMPT_FILE", "")),
        "dataset_xlsx": _rel_repo_path(dataset_xlsx),
        "dataset_sheet": dataset_sheet,
        "output_suffix": suffix,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "artifacts": rel_artifacts,
        "predictions_csv": rel_artifacts["predictions"],
    }
    workspace.add_run(entry)
    (run_dir / "run_manifest.json").write_text(
        json.dumps(entry, indent=2),
        encoding="utf-8",
    )
    try:
        pbi = export_powerbi_data(workspace)
        print(f"Dashboard export updated: {pbi}")
    except Exception as exc:
        print(f"Warning: dashboard export failed: {exc}")
    return entry


def _reader_thread(proc: subprocess.Popen[str], out_queue: queue.Queue[str | None]) -> None:
    if proc.stdout is None:
        out_queue.put(None)
        return
    for line in proc.stdout:
        out_queue.put(line.rstrip())
    out_queue.put(None)


def _progress_event(plan: dict[str, int], transcript_path: Path) -> dict[str, Any]:
    completed = _count_completed_personas(transcript_path)
    total = plan["total"]
    completed = min(completed, total)
    return {
        "type": "progress",
        "completed": completed,
        "total": total,
        "remaining": max(total - completed, 0),
    }


def run_evaluation_streaming(
    *,
    workspace: Workspace,
    model_key: str,
    prompt_key: str,
    prompt_label: str,
    prompt_file: Path | None,
    dataset_xlsx: Path,
    dataset_sheet: str,
    run_label: str,
    resume: bool = False,
    eval_limit: int | None = None,
    parallel_workers: int = 6,
) -> Iterator[dict[str, Any]]:
    workspace.ensure_dirs()
    suffix = build_output_suffix(model_key, prompt_key, prompt_label, run_label)
    env = build_env(
        model_key=model_key,
        prompt_key=prompt_key,
        prompt_label=prompt_label,
        prompt_file=prompt_file,
        dataset_xlsx=dataset_xlsx,
        dataset_sheet=dataset_sheet,
        output_suffix=suffix,
        workspace=workspace,
        resume=resume,
        eval_limit=eval_limit,
        parallel_workers=parallel_workers,
    )
    script = AGENT_ROOT / "chatbot_live_eval.py"
    if not script.is_file():
        raise FileNotFoundError(f"chatbot_live_eval.py not found at {script}")

    model = get_model(model_key)
    paths = artifact_paths(suffix, workspace)
    transcript_path = paths["transcripts"]
    plan = estimate_eval_plan(
        dataset_xlsx=dataset_xlsx,
        dataset_sheet=dataset_sheet,
        eval_limit=eval_limit,
        resume=resume,
        transcript_path=transcript_path,
    )
    yield {
        "type": "start",
        "model_display": model["display"],
        "prompt_label": prompt_label,
        "dataset": dataset_xlsx.name,
        "sheet": dataset_sheet,
        **plan,
    }
    yield _progress_event(plan, transcript_path)

    proc = subprocess.Popen(
        [sys.executable, "-u", str(script)],
        cwd=str(AGENT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    out_queue: queue.Queue[str | None] = queue.Queue()
    reader = threading.Thread(target=_reader_thread, args=(proc, out_queue), daemon=True)
    reader.start()
    stream_open = True

    while stream_open or proc.poll() is None:
        try:
            item = out_queue.get(timeout=0.75)
        except queue.Empty:
            yield _progress_event(plan, transcript_path)
            if not stream_open and proc.poll() is not None:
                break
            continue
        if item is None:
            stream_open = False
            continue
        yield {"type": "log", "line": item}
        yield _progress_event(plan, transcript_path)

    reader.join(timeout=2)
    proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"chatbot_live_eval.py exited with code {proc.returncode}")

    yield _progress_event(plan, transcript_path)
    entry = _archive_run(
        workspace=workspace,
        suffix=suffix,
        model_key=model_key,
        prompt_key=prompt_key,
        prompt_label=prompt_label,
        prompt_file=prompt_file,
        dataset_xlsx=dataset_xlsx,
        dataset_sheet=dataset_sheet,
        run_label=run_label,
        env=env,
    )
    yield {"type": "complete", "entry": entry}


def run_evaluation(
    *,
    workspace: Workspace,
    model_key: str,
    prompt_key: str,
    prompt_label: str,
    prompt_file: Path | None,
    dataset_xlsx: Path,
    dataset_sheet: str,
    run_label: str,
    resume: bool = False,
    eval_limit: int | None = None,
    parallel_workers: int = 6,
) -> dict[str, Any]:
    entry: dict[str, Any] | None = None
    for event in run_evaluation_streaming(
        workspace=workspace,
        model_key=model_key,
        prompt_key=prompt_key,
        prompt_label=prompt_label,
        prompt_file=prompt_file,
        dataset_xlsx=dataset_xlsx,
        dataset_sheet=dataset_sheet,
        run_label=run_label,
        resume=resume,
        eval_limit=eval_limit,
        parallel_workers=parallel_workers,
    ):
        if event.get("type") == "log":
            print(event["line"])
        if event.get("type") == "complete":
            entry = event["entry"]
    if entry is None:
        raise RuntimeError("evaluation finished without a run entry")
    return entry


def import_legacy_run(
    workspace: Workspace,
    predictions_csv: Path,
    *,
    display_name: str,
    model_key: str = "openai",
    prompt_label: str = "legacy import",
    run_label: str = "legacy",
) -> dict[str, Any]:
    predictions_csv = Path(predictions_csv)
    if not predictions_csv.is_file():
        raise FileNotFoundError(predictions_csv)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"{stamp}_import_{_safe_suffix(run_label)}"
    run_dir = workspace.runs / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    dest = run_dir / predictions_csv.name
    shutil.copy2(predictions_csv, dest)
    model = get_model(model_key)
    entry: dict[str, Any] = {
        "run_id": run_id,
        "run_label": run_label,
        "display_name": display_name,
        "model_key": model_key,
        "model_display": model["display"],
        "api_base_url": model["base_url"],
        "prompt_key": "imported",
        "prompt_label": prompt_label,
        "prompt_file": "",
        "dataset_xlsx": "",
        "dataset_sheet": "",
        "output_suffix": "",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "artifacts": {"predictions": str(dest)},
        "predictions_csv": str(dest),
        "imported": True,
    }
    workspace.add_run(entry)
    (run_dir / "run_manifest.json").write_text(
        __import__("json").dumps(entry, indent=2),
        encoding="utf-8",
    )
    return entry
