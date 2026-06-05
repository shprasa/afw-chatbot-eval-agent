"""Push workspace eval outputs to GitHub (used by CLI and Streamlit agent UI)."""
from __future__ import annotations

import base64
import json
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .config import AGENT_ROOT, Workspace

MAX_FILE_BYTES = 8 * 1024 * 1024  # GitHub contents API limit ~100MB but keep reasonable


def _ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _load_config_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip()
    return values


def resolve_credentials(
    secrets: Any | None = None,
    config_path: Path | None = None,
) -> dict[str, str] | None:
    token = owner = repo = branch = ""
    if secrets is not None:
        try:
            token = token or str(secrets.get("GITHUB_TOKEN", "") or secrets.get("token", ""))
        except Exception:
            pass
        try:
            gh = secrets["github"]
            token = token or str(gh.get("GITHUB_TOKEN", "") or gh.get("token", ""))
            owner = owner or str(gh.get("GITHUB_OWNER", "") or gh.get("owner", ""))
            repo = repo or str(gh.get("GITHUB_REPO", "") or gh.get("repo", ""))
            branch = branch or str(gh.get("GITHUB_BRANCH", "") or gh.get("branch", ""))
        except Exception:
            pass
        try:
            owner = owner or str(secrets.get("GITHUB_OWNER", ""))
            repo = repo or str(secrets.get("GITHUB_REPO", ""))
            branch = branch or str(secrets.get("GITHUB_BRANCH", ""))
        except Exception:
            pass
    token = token or os.environ.get("GITHUB_TOKEN", "")
    owner = owner or os.environ.get("GITHUB_OWNER", "")
    repo = repo or os.environ.get("GITHUB_REPO", "")
    branch = branch or os.environ.get("GITHUB_BRANCH", "main")
    if config_path and not token:
        cfg = _load_config_file(config_path)
        token = cfg.get("GITHUB_TOKEN", "")
        owner = owner or cfg.get("GITHUB_OWNER", "")
        repo = repo or cfg.get("GITHUB_REPO", "")
    if not token:
        return None
    if not owner:
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}", "User-Agent": "afw-publish"},
        )
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=30) as resp:
            owner = json.loads(resp.read().decode())["login"]
    if not repo:
        repo = "afw-chatbot-eval-agent"
    return {"token": token, "owner": owner, "repo": repo, "branch": branch}


def _api(token: str, method: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "afw-publish",
            **({"Content-Type": "application/json"} if payload else {}),
        },
    )
    with urllib.request.urlopen(req, context=_ssl_context(), timeout=120) as resp:
        body = resp.read().decode()
        return json.loads(body) if body else {}


def push_file(
    token: str,
    owner: str,
    repo: str,
    repo_rel: str,
    local: Path,
    message: str,
) -> bool:
    if not local.is_file():
        return False
    if local.stat().st_size > MAX_FILE_BYTES:
        return False
    path = f"/repos/{owner}/{repo}/contents/{repo_rel.replace(chr(92), '/')}"
    payload: dict = {
        "message": message,
        "content": base64.b64encode(local.read_bytes()).decode("ascii"),
    }
    try:
        existing = _api(token, "GET", path)
        if existing.get("sha"):
            payload["sha"] = existing["sha"]
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
    _api(token, "PUT", path, payload)
    return True


def _workspace_publish_paths(ws: Workspace) -> list[Path]:
    paths: list[Path] = []
    manifest = ws.runs / "manifest.json"
    if manifest.is_file():
        paths.append(manifest)
    for run_dir in ws.runs.iterdir() if ws.runs.is_dir() else []:
        if run_dir.is_dir():
            for f in run_dir.rglob("*"):
                if f.is_file() and f.stat().st_size <= MAX_FILE_BYTES:
                    paths.append(f)
    if ws.comparisons.is_dir():
        for f in ws.comparisons.rglob("*"):
            if f.is_file() and f.stat().st_size <= MAX_FILE_BYTES:
                paths.append(f)
    if ws.powerbi_export.is_dir():
        for f in ws.powerbi_export.rglob("*"):
            if f.is_file() and f.stat().st_size <= MAX_FILE_BYTES:
                paths.append(f)
    if ws.datasets.is_dir():
        for f in ws.datasets.glob("*.xlsx"):
            if f.is_file() and f.stat().st_size <= MAX_FILE_BYTES:
                paths.append(f)
    if ws.templates.is_dir():
        for f in ws.templates.glob("*.xlsx"):
            if f.is_file() and f.stat().st_size <= MAX_FILE_BYTES:
                paths.append(f)
    return paths


def repo_relative_path(ws: Workspace, local: Path) -> str:
    try:
        return str(local.relative_to(AGENT_ROOT)).replace("\\", "/")
    except ValueError:
        return f"workspace/{local.relative_to(ws.root)}".replace("\\", "/")


def publish_file(
    local: Path,
    repo_rel: str,
    *,
    message: str = "Update file from eval agent",
    secrets: Any | None = None,
    config_path: Path | None = None,
) -> bool:
    creds = resolve_credentials(secrets=secrets, config_path=config_path or AGENT_ROOT / "github_publish_config.txt")
    if not creds or not local.is_file():
        return False
    return push_file(
        creds["token"],
        creds["owner"],
        creds["repo"],
        repo_rel,
        local,
        message,
    )


def publish_workspace(
    ws: Workspace,
    *,
    message: str = "Update eval workspace from agent",
    secrets: Any | None = None,
    config_path: Path | None = None,
) -> dict[str, Any]:
    """Push workspace runs, comparisons, and powerbi_export to GitHub."""
    creds = resolve_credentials(secrets=secrets, config_path=config_path or AGENT_ROOT / "github_publish_config.txt")
    if not creds:
        raise RuntimeError("GitHub credentials not configured (GITHUB_TOKEN required).")

    token, owner, repo = creds["token"], creds["owner"], creds["repo"]
    pushed: list[str] = []
    skipped: list[str] = []

    for local in _workspace_publish_paths(ws):
        try:
            repo_rel = str(local.relative_to(AGENT_ROOT)).replace("\\", "/")
        except ValueError:
            repo_rel = f"workspace/{local.relative_to(ws.root)}".replace("\\", "/")
        if push_file(token, owner, repo, repo_rel, local, message):
            pushed.append(repo_rel)
        else:
            skipped.append(repo_rel)

    # Registry + app code refresh
    for rel in (
        "config/agent_registry.json",
        "afw_eval_dashboard/app.py",
        "afw_eval_dashboard/analytics.py",
        "afw_eval_dashboard/theme.py",
        "afw_eval_dashboard/mcnemar_loader.py",
        "afw_eval_agent_ui/app.py",
        "streamlit_app.py",
    ):
        local = AGENT_ROOT / rel
        if local.is_file() and push_file(token, owner, repo, rel, local, message):
            pushed.append(rel)

    return {
        "owner": owner,
        "repo": repo,
        "url": f"https://github.com/{owner}/{repo}",
        "pushed": pushed,
        "skipped": skipped,
        "count": len(pushed),
    }
