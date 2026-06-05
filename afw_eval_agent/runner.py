"""Run chatbot_live_eval.py as a subprocess and archive outputs to workspace."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    return env


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
    print(f"\nRunning evaluation → {model['display']}")
    print(f"  Prompt label: {prompt_label}")
    print(f"  Dataset: {dataset_xlsx.name} [{dataset_sheet}]")
    print(f"  Output suffix: {suffix}\n")

    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(AGENT_ROOT),
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"chatbot_live_eval.py exited with code {proc.returncode}")

    paths = artifact_paths(suffix, workspace)
    missing = [k for k, p in paths.items() if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"expected outputs missing after run: {missing}")

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

    def _rel(p: Path | str) -> str:
        try:
            return str(Path(p).resolve().relative_to(AGENT_ROOT.resolve())).replace("\\", "/")
        except ValueError:
            return str(p).replace("\\", "/")

    rel_artifacts = {k: _rel(v) for k, v in archived.items()}
    entry: dict[str, Any] = {
        "run_id": run_id,
        "run_label": run_label,
        "display_name": f"{run_label} | {model['display']} | {prompt_label}",
        "model_key": model_key,
        "model_display": model["display"],
        "api_base_url": model["base_url"],
        "prompt_key": prompt_key,
        "prompt_label": prompt_label,
        "prompt_file": _rel(env.get("CHATBOT_SYSTEM_PROMPT_FILE", "")),
        "dataset_xlsx": _rel(dataset_xlsx),
        "dataset_sheet": dataset_sheet,
        "output_suffix": suffix,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "artifacts": rel_artifacts,
        "predictions_csv": rel_artifacts["predictions"],
    }
    workspace.add_run(entry)
    (run_dir / "run_manifest.json").write_text(
        __import__("json").dumps(entry, indent=2),
        encoding="utf-8",
    )
    try:
        pbi = export_powerbi_data(workspace)
        print(f"Power BI data updated: {pbi}")
        print("Live dashboard: http://localhost:8502 (Run_AFW_Live_Dashboard.bat)")
    except Exception as exc:
        print(f"Warning: Power BI export failed: {exc}")
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
