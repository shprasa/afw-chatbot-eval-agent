"""Workspace config, run manifest, and path helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AGENT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIRNAME = "workspace"


def default_workspace() -> Path:
    """All eval outputs live under workspace/ inside the cloned GitHub repo."""
    return AGENT_ROOT / WORKSPACE_DIRNAME


class Workspace:
    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else default_workspace()
        self.config_path = self.root / ".eval_agent_config.json"
        self.datasets = self.root / "datasets"
        self.runs = self.root / "runs"
        self.comparisons = self.root / "comparisons"
        self.templates = self.root / "templates"
        self.powerbi_export = self.root / "powerbi_export"
        self.deliverables = self.root / "deliverables"
        self.local_artifacts = self.root / "_local_artifacts"
        self.local_reports = self.root / "_local_reports"

    def ensure_dirs(self) -> None:
        for d in (
            self.root,
            self.datasets,
            self.runs,
            self.comparisons,
            self.templates,
            self.powerbi_export,
            self.deliverables,
            self.local_artifacts,
            self.local_reports,
        ):
            d.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> dict[str, Any]:
        if self.config_path.is_file():
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        return {}

    def save_config(self, cfg: dict[str, Any]) -> None:
        self.ensure_dirs()
        self.config_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    def load_manifest(self) -> list[dict[str, Any]]:
        path = self.runs / "manifest.json"
        if not path.is_file():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def save_manifest(self, runs: list[dict[str, Any]]) -> None:
        self.runs.mkdir(parents=True, exist_ok=True)
        (self.runs / "manifest.json").write_text(
            json.dumps(runs, indent=2), encoding="utf-8"
        )

    def add_run(self, entry: dict[str, Any]) -> None:
        runs = self.load_manifest()
        runs = [r for r in runs if r.get("run_id") != entry.get("run_id")]
        runs.append(entry)
        runs.sort(key=lambda r: r.get("created_utc", ""), reverse=True)
        self.save_manifest(runs)

    def init_config_if_missing(self) -> dict[str, Any]:
        cfg = self.load_config()
        saved = cfg.get("workspace_root")
        if saved:
            self.root = Path(saved)
            self.config_path = self.root / ".eval_agent_config.json"
            self._refresh_paths()
        if not cfg.get("workspace_root"):
            cfg = {
                "workspace_root": str(self.root),
                "storage": "github_repo",
                "agent_root": str(AGENT_ROOT),
                "created_utc": datetime.now(timezone.utc).isoformat(),
            }
            self.save_config(cfg)
        self.ensure_dirs()
        return cfg

    def _refresh_paths(self) -> None:
        self.datasets = self.root / "datasets"
        self.runs = self.root / "runs"
        self.comparisons = self.root / "comparisons"
        self.templates = self.root / "templates"
        self.powerbi_export = self.root / "powerbi_export"
        self.deliverables = self.root / "deliverables"
        self.local_artifacts = self.root / "_local_artifacts"
        self.local_reports = self.root / "_local_reports"
