"""Load Power BI export CSV tables directly from GitHub (for team / cloud dashboard)."""
from __future__ import annotations

import io
import json
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

CSV_TABLES = {
    "runs": "workspace/powerbi_export/csv/Evaluation_Runs.csv",
    "personas": "workspace/powerbi_export/csv/Persona_Results.csv",
    "turns": "workspace/powerbi_export/csv/Turn_Details.csv",
    "summary": "workspace/powerbi_export/csv/Run_Summary_By_Class.csv",
    "mcnemar": "workspace/powerbi_export/csv/McNemar_Comparisons.csv",
    "cases": "workspace/powerbi_export/csv/User_Test_Cases.csv",
    "refresh": "workspace/powerbi_export/csv/Refresh_Log.csv",
}
MANIFEST_PATH = "workspace/powerbi_export/refresh_manifest.json"


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        ctx = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen("https://api.github.com", context=ctx, timeout=10):
            return ctx
    except Exception:
        pass
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _fetch_raw(token: str, owner: str, repo: str, repo_path: str) -> bytes | None:
    api = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_path}"
    req = urllib.request.Request(
        api,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.raw",
            "User-Agent": "afw-team-dashboard",
        },
    )
    try:
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=120) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def _read_csv_bytes(data: bytes | None) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()
    return pd.read_csv(io.BytesIO(data))


def load_config_from_file(config_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not config_path.is_file():
        return values
    for line in config_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip()
    return values


def resolve_github_settings(
    secrets: Any | None = None,
    config_path: Path | None = None,
) -> dict[str, str] | None:
    """Return {token, owner, repo, branch} from Streamlit secrets, env, or local config file."""
    token = owner = repo = branch = ""

    if secrets is not None:
        try:
            gh = secrets.get("github", secrets)
            token = gh.get("GITHUB_TOKEN", "") or gh.get("token", "")
            owner = gh.get("GITHUB_OWNER", "") or gh.get("owner", "")
            repo = gh.get("GITHUB_REPO", "") or gh.get("repo", "")
            branch = gh.get("GITHUB_BRANCH", "") or gh.get("branch", "main")
        except Exception:
            pass

    token = token or os.environ.get("GITHUB_TOKEN", "")
    owner = owner or os.environ.get("GITHUB_OWNER", "")
    repo = repo or os.environ.get("GITHUB_REPO", "")
    branch = branch or os.environ.get("GITHUB_BRANCH", "main")

    if config_path and not token:
        cfg = load_config_from_file(config_path)
        token = cfg.get("GITHUB_TOKEN", "")
        owner = owner or cfg.get("GITHUB_OWNER", "")
        repo = repo or cfg.get("GITHUB_REPO", "")
        if owner.lower() in ("auto", "me", ""):
            owner = ""

    if not token:
        return None

    if not owner:
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}", "User-Agent": "afw-team-dashboard"},
        )
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=30) as resp:
            owner = json.loads(resp.read().decode())["login"]

    if not repo:
        repo = "afw-chatbot-eval-agent"

    return {"token": token, "owner": owner, "repo": repo, "branch": branch}


def load_tables_from_github(settings: dict[str, str]) -> dict[str, pd.DataFrame]:
    token, owner, repo = settings["token"], settings["owner"], settings["repo"]
    tables: dict[str, pd.DataFrame] = {}
    for key, path in CSV_TABLES.items():
        tables[key] = _read_csv_bytes(_fetch_raw(token, owner, repo, path))

    manifest = _fetch_raw(token, owner, repo, MANIFEST_PATH)
    if manifest:
        meta = json.loads(manifest.decode("utf-8"))
        tables["meta"] = pd.DataFrame([meta])
    tables["source"] = pd.DataFrame(
        [{"source": f"https://github.com/{owner}/{repo}", "mode": "github_live"}]
    )
    return tables
