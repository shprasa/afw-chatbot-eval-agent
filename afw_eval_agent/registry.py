"""Persistent model hosts and prompt labels (saved in repo config/)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import AGENT_ROOT
from .presets import MODEL_CHOICES, PROMPT_CHOICES

REGISTRY_PATH = AGENT_ROOT / "config" / "agent_registry.json"

DEFAULT_PROMPT_LABELS: dict[str, dict[str, str]] = {
    "v1": {
        "label": "System Prompt v1",
        "notes": "Default v1 label — prompt text is deployed on the API host only.",
        "reference_file": "prompts/prompt_extract_v1.txt",
    },
    "v10": {
        "label": "System Prompt v10",
        "notes": "Default v10 label — prompt text is deployed on the API host only.",
        "reference_file": "prompts/prompt_extract_v10.txt",
    },
}


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return s[:48] or "item"


def _default_registry() -> dict[str, Any]:
    models: dict[str, Any] = {}
    for key, m in MODEL_CHOICES.items():
        models[key] = {**m, "builtin": True}
    labels: dict[str, Any] = {}
    for key, p in DEFAULT_PROMPT_LABELS.items():
        labels[key] = {**p, "builtin": True}
    return {
        "version": 1,
        "models": models,
        "prompt_labels": labels,
        "updated_utc": datetime.now(timezone.utc).isoformat(),
    }


def load_registry() -> dict[str, Any]:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.is_file():
        data = _default_registry()
        save_registry(data)
        return data
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    changed = False
    for key, m in MODEL_CHOICES.items():
        if key not in data.get("models", {}):
            data.setdefault("models", {})[key] = {**m, "builtin": True}
            changed = True
    for key, p in DEFAULT_PROMPT_LABELS.items():
        if key not in data.get("prompt_labels", {}):
            data.setdefault("prompt_labels", {})[key] = {**p, "builtin": True}
            changed = True
    if changed:
        save_registry(data)
    return data


def save_registry(data: dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_utc"] = datetime.now(timezone.utc).isoformat()
    REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def list_models() -> dict[str, dict[str, Any]]:
    return load_registry().get("models", {})


def get_model(key: str) -> dict[str, Any]:
    models = list_models()
    if key not in models:
        raise KeyError(f"unknown model key: {key}")
    return models[key]


def add_model(*, display: str, base_url: str, backend: str, key: str | None = None) -> str:
    data = load_registry()
    base_url = base_url.rstrip("/")
    key = key or _slug(display)
    if key in data["models"]:
        raise ValueError(f"model key already exists: {key}")
    data["models"][key] = {
        "display": display,
        "base_url": base_url,
        "backend": backend.strip().lower() or "openai",
        "builtin": False,
        "added_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_registry(data)
    return key


def list_prompt_labels() -> dict[str, dict[str, Any]]:
    return load_registry().get("prompt_labels", {})


def get_prompt_label(key: str) -> dict[str, Any]:
    labels = list_prompt_labels()
    if key not in labels:
        raise KeyError(f"unknown prompt label key: {key}")
    return labels[key]


def add_prompt_label(
    *,
    label: str,
    notes: str = "",
    key: str | None = None,
    reference_file: str = "",
) -> str:
    """Register a prompt version label (backend deploy tag — not prompt text)."""
    data = load_registry()
    key = key or _slug(label)
    if key in data["prompt_labels"]:
        raise ValueError(f"prompt label key already exists: {key}")
    entry: dict[str, Any] = {
        "label": label,
        "notes": notes
        or "Label only — system prompt is changed on the API backend, not in this agent.",
        "builtin": False,
        "added_utc": datetime.now(timezone.utc).isoformat(),
    }
    if reference_file:
        entry["reference_file"] = reference_file
    data["prompt_labels"][key] = entry
    save_registry(data)
    return key


def resolve_prompt_reference_file(prompt_key: str) -> Path | None:
    """Optional local text file for report generation (not sent to API)."""
    try:
        meta = get_prompt_label(prompt_key)
    except KeyError:
        return None
    rel = meta.get("reference_file", "")
    if not rel:
        return None
    for root in (AGENT_ROOT,):
        candidate = root / rel
        if candidate.is_file():
            return candidate
    return None
