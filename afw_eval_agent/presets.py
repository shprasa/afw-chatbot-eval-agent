"""Model / API presets — endpoints are fixed per AFW deployment."""

from __future__ import annotations

MODEL_CHOICES: dict[str, dict[str, str]] = {
    "openai": {
        "display": "OpenAI (angel-flight-chatbot-app)",
        "base_url": "https://angel-flight-chatbot-app.azurewebsites.net",
        "backend": "openai",
    },
    "claude": {
        "display": "Claude (angel-flight-chatbot-claude)",
        "base_url": "https://angel-flight-chatbot-claude.azurewebsites.net",
        "backend": "claude",
    },
}

PROMPT_CHOICES: dict[str, dict[str, str]] = {
    "v1": {
        "display": "System Prompt v1",
        "prompt_file": "prompts/prompt_extract_v1.txt",
    },
    "v10": {
        "display": "System Prompt v10",
        "prompt_file": "prompts/prompt_extract_v10.txt",
    },
}

# Eval outputs are stored in-repo under workspace/ (committed to GitHub).
WORKSPACE_SUBDIR = "workspace"
