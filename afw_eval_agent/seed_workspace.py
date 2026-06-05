"""Seed repo workspace/ with benchmark runs, reports, and deliverables."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import AGENT_ROOT, Workspace

# Benchmark arms completed during practicum (120 personas, original style short)
BENCHMARK_ARMS: list[dict[str, str]] = [
    {
        "run_id": "benchmark_openai_v1",
        "run_label": "openai_v1",
        "display_name": "OpenAI v1 | System Prompt v1 | 120 personas",
        "model_key": "openai",
        "prompt_key": "v1",
        "prompt_label": "System Prompt v1",
        "output_suffix": "_original_style_short_openai",
    },
    {
        "run_id": "benchmark_openai_v10",
        "run_label": "openai_v10",
        "display_name": "OpenAI v10 | System Prompt v10 | 120 personas",
        "model_key": "openai",
        "prompt_key": "v10",
        "prompt_label": "System Prompt v10",
        "output_suffix": "_original_style_short_openai_v10",
    },
    {
        "run_id": "benchmark_claude_v1",
        "run_label": "claude_v1",
        "display_name": "Claude v1 | System Prompt v1 | 120 personas",
        "model_key": "claude",
        "prompt_key": "v1",
        "prompt_label": "System Prompt v1",
        "output_suffix": "_original_style_short_claude_v1",
    },
    {
        "run_id": "benchmark_claude_v10",
        "run_label": "claude_v10",
        "display_name": "Claude v10 | System Prompt v10 | 120 personas",
        "model_key": "claude",
        "prompt_key": "v10",
        "prompt_label": "System Prompt v10",
        "output_suffix": "_original_style_short_claude",
    },
]

REPORT_STEMS = (
    "chatbot_live_accuracy",
    "chatbot_live_failure_analysis",
    "chatbot_live_prompt_improvements",
)


def _rel(root: Path, path: Path | str) -> str:
    try:
        return str(Path(path).resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _copy_if(src: Path, dst: Path) -> bool:
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def seed_workspace(
    agent_root: Path | None = None,
    *,
    source_desk: Path | None = None,
    overwrite: bool = False,
) -> Workspace:
    """Populate workspace/runs with benchmark artifacts and reports from disk."""
    root = agent_root or AGENT_ROOT
    ws = Workspace(root / "workspace")
    ws.ensure_dirs()
    desk = source_desk or root.parent if (root / "artifacts").is_dir() else root
    if not (desk / "artifacts").is_dir() and (AGENT_ROOT.parent / "artifacts").is_dir():
        desk = AGENT_ROOT.parent

    art = desk / "artifacts"
    rep = desk / "reports"
    data_xlsx = root / "data" / "AFW_120_User_Test_Cases_Original_Style_Short.xlsx"
    if not data_xlsx.is_file():
        data_xlsx = root / "AFW_120_User_Test_Cases_Original_Style_Short.xlsx"

    if data_xlsx.is_file():
        _copy_if(data_xlsx, ws.datasets / data_xlsx.name)

    try:
        from .template import create_template

        tpl = ws.templates / "AFW_Eval_Test_Cases_Template.xlsx"
        if not tpl.is_file() or overwrite:
            create_template(tpl)
    except Exception:
        pass

    manifest: list[dict[str, Any]] = []
    for arm in BENCHMARK_ARMS:
        suffix = arm["output_suffix"]
        run_dir = ws.runs / arm["run_id"]
        if run_dir.exists() and not overwrite:
            existing = run_dir / "run_manifest.json"
            if existing.is_file():
                manifest.append(json.loads(existing.read_text(encoding="utf-8")))
                continue
        run_dir.mkdir(parents=True, exist_ok=True)
        archived: dict[str, str] = {}
        for stem, ext in [
            ("chatbot_live_predictions", ".csv"),
            ("chatbot_live_transcripts", ".jsonl"),
        ]:
            src = art / f"{stem}{suffix}{ext}"
            dst = run_dir / src.name
            if _copy_if(src, dst):
                archived[stem] = _rel(root, dst)
        for stem in REPORT_STEMS:
            ext = ".json" if "accuracy" in stem else ".md"
            src = rep / f"{stem}{suffix}{ext}"
            key = stem.replace("chatbot_live_", "")
            dst = run_dir / src.name
            if _copy_if(src, dst):
                archived[key] = _rel(root, dst)

        if data_xlsx.is_file():
            _copy_if(data_xlsx, run_dir / data_xlsx.name)

        pred = run_dir / f"chatbot_live_predictions{suffix}.csv"
        if not pred.is_file():
            continue

        from .presets import MODEL_CHOICES

        model = MODEL_CHOICES[arm["model_key"]]
        prompt_rel = f"prompts/prompt_extract_{arm['prompt_key']}.txt"
        dataset_rel = _rel(root, data_xlsx) if data_xlsx.is_file() else ""
        entry: dict[str, Any] = {
            "run_id": arm["run_id"],
            "run_label": arm["run_label"],
            "display_name": arm["display_name"],
            "model_key": arm["model_key"],
            "model_display": model["display"],
            "api_base_url": model["base_url"],
            "prompt_key": arm["prompt_key"],
            "prompt_label": arm["prompt_label"],
            "prompt_file": prompt_rel,
            "dataset_xlsx": dataset_rel,
            "dataset_sheet": "120_test_cases",
            "output_suffix": suffix,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "artifacts": archived,
            "predictions_csv": _rel(root, pred),
            "seeded": True,
        }
        (run_dir / "run_manifest.json").write_text(
            json.dumps(entry, indent=2), encoding="utf-8"
        )
        manifest.append(entry)

    ws.save_manifest(manifest)

    for folder_name, sub in [
        ("powerbi_export", desk / "powerbi_export"),
        ("deliverables", desk / "powerbi_export"),
    ]:
        if not sub.is_dir():
            continue
        dest_root = ws.root / folder_name
        dest_root.mkdir(parents=True, exist_ok=True)
        for f in sub.iterdir():
            if f.is_file() and f.suffix.lower() in {".xlsx", ".docx", ".csv", ".md"}:
                if folder_name == "deliverables" and not f.name.startswith("AFW_"):
                    continue
                _copy_if(f, dest_root / f.name)

    cfg = ws.load_config() or {}
    cfg.update(
        {
            "workspace_root": str(ws.root),
            "storage": "github_repo",
            "agent_root": str(root),
            "updated_utc": datetime.now(timezone.utc).isoformat(),
        }
    )
    ws.save_config(cfg)
    return ws
