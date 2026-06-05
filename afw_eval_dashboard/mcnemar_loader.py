"""Load McNemar comparison JSON outputs for dashboard display."""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

from afw_eval_dashboard.github_loader import resolve_github_settings, _ssl_context, _fetch_raw


def list_comparisons_local(workspace_root: Path) -> list[dict[str, str]]:
    comp_dir = workspace_root / "comparisons"
    if not comp_dir.is_dir():
        return []
    items: list[dict[str, str]] = []
    for p in sorted(comp_dir.glob("mcnemar_*.json"), reverse=True):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            label = f"{data.get('name_a', 'A')} vs {data.get('name_b', 'B')}"
            items.append({"id": p.stem, "label": label, "path": str(p), "source": "local"})
        except Exception:
            items.append({"id": p.stem, "label": p.stem, "path": str(p), "source": "local"})
    return items


def list_comparisons_github(settings: dict[str, str]) -> list[dict[str, str]]:
    token, owner, repo = settings["token"], settings["owner"], settings["repo"]
    api = f"https://api.github.com/repos/{owner}/{repo}/contents/workspace/comparisons"
    req = urllib.request.Request(
        api,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "afw-mcnemar-loader",
        },
    )
    items: list[dict[str, str]] = []
    try:
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=60) as resp:
            entries = json.loads(resp.read().decode())
    except urllib.error.HTTPError:
        return items
    for ent in entries:
        name = ent.get("name", "")
        if not name.endswith(".json") or not name.startswith("mcnemar_"):
            continue
        repo_path = f"workspace/comparisons/{name}"
        raw = _fetch_raw(token, owner, repo, repo_path)
        if not raw:
            continue
        try:
            data = json.loads(raw.decode("utf-8"))
            label = f"{data.get('name_a', 'A')} vs {data.get('name_b', 'B')}"
        except Exception:
            label = name
        items.append({
            "id": name.replace(".json", ""),
            "label": label,
            "path": repo_path,
            "source": "github",
        })
    return items


def load_comparison_json(
    *,
    local_path: Path | None = None,
    github_settings: dict[str, str] | None = None,
    repo_path: str | None = None,
) -> dict[str, Any] | None:
    if local_path and local_path.is_file():
        return json.loads(local_path.read_text(encoding="utf-8"))
    if github_settings and repo_path:
        raw = _fetch_raw(
            github_settings["token"],
            github_settings["owner"],
            github_settings["repo"],
            repo_path,
        )
        if raw:
            return json.loads(raw.decode("utf-8"))
    return None


def comparison_summary_df(data: dict[str, Any]) -> pd.DataFrame:
    rows = [
        ("Group A", data.get("name_a", "")),
        ("Group B", data.get("name_b", "")),
        ("Paired personas", data.get("n_paired", "")),
        ("Accuracy A", f"{100 * float(data.get('accuracy_a', 0)):.1f}%"),
        ("Accuracy B", f"{100 * float(data.get('accuracy_b', 0)):.1f}%"),
        ("ATE (B − A)", f"{float(data.get('ate_b_minus_a_pp', 0)):+.1f} pp"),
        ("A only correct", data.get("a_only_correct", "")),
        ("B only correct", data.get("b_only_correct", "")),
        ("Both correct", data.get("both_correct", "")),
        ("Both wrong", data.get("both_wrong", "")),
        ("McNemar p-value", f"{float(data.get('mcnemar_p_value', 0)):.4f}"),
        (
            "Significant at 0.05",
            "Yes" if data.get("significant_at_0_05") else "No",
        ),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])
