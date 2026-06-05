"""Email notifications when background evaluations finish."""

from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Any


def _smtp_config(secrets: Any | None = None) -> dict[str, str] | None:
    host = port = user = password = from_addr = ""
    if secrets is not None:
        try:
            host = str(secrets.get("SMTP_HOST", "") or "")
            port = str(secrets.get("SMTP_PORT", "") or "")
            user = str(secrets.get("SMTP_USER", "") or "")
            password = str(secrets.get("SMTP_PASSWORD", "") or "")
            from_addr = str(secrets.get("SMTP_FROM", "") or "")
        except Exception:
            pass
    host = host or os.environ.get("SMTP_HOST", "")
    port = port or os.environ.get("SMTP_PORT", "587")
    user = user or os.environ.get("SMTP_USER", "")
    password = password or os.environ.get("SMTP_PASSWORD", "")
    from_addr = from_addr or os.environ.get("SMTP_FROM", user)
    if not host or not user or not password or not from_addr:
        return None
    return {
        "host": host,
        "port": int(port),
        "user": user,
        "password": password,
        "from_addr": from_addr,
    }


def send_email(
    to_addr: str,
    subject: str,
    body: str,
    *,
    secrets: Any | None = None,
) -> tuple[bool, str]:
    to_addr = (to_addr or "").strip()
    if not to_addr or "@" not in to_addr:
        return False, "Invalid email address."

    cfg = _smtp_config(secrets)
    if cfg is None:
        return False, "Email is not configured on this server."

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg["from_addr"]
    msg["To"] = to_addr
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=30) as server:
            server.starttls(context=context)
            server.login(cfg["user"], cfg["password"])
            server.send_message(msg)
        return True, "Notification sent."
    except Exception as exc:
        return False, f"Email failed: {exc}"


def send_eval_complete_email(
    to_addr: str,
    *,
    run_id: str,
    run_label: str,
    dataset: str,
    model_display: str,
    prompt_label: str,
    completed: int,
    total: int,
    secrets: Any | None = None,
) -> tuple[bool, str]:
    subject = f"AFW eval complete — {run_label}"
    body = (
        "Your AFW Screening Chatbot evaluation has finished.\n\n"
        f"Run ID: {run_id}\n"
        f"Run label: {run_label}\n"
        f"Workbook: {dataset}\n"
        f"Model: {model_display}\n"
        f"Prompt: {prompt_label}\n"
        f"Personas: {completed} / {total}\n\n"
        "Open the Evaluation Agent or Dashboard to review results and save to the team repo.\n"
        "https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent\n"
        "https://afw-chatbot-eval-agent.streamlit.app\n"
    )
    return send_email(to_addr, subject, body, secrets=secrets)


def send_eval_failed_email(
    to_addr: str,
    *,
    run_label: str,
    error: str,
    secrets: Any | None = None,
) -> tuple[bool, str]:
    subject = f"AFW eval failed — {run_label}"
    body = (
        "Your AFW Screening Chatbot evaluation did not complete successfully.\n\n"
        f"Run label: {run_label}\n"
        f"Error: {error}\n\n"
        "Open the Evaluation Agent to view the session log.\n"
        "https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent\n"
    )
    return send_email(to_addr, subject, body, secrets=secrets)
