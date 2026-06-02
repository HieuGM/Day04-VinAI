from __future__ import annotations

import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_recipients(to: str | list[str] | None) -> list[str]:
    if to is None:
        return []
    if isinstance(to, str):
        values = re.split(r"[,;\s]+", to.strip())
    else:
        values = [str(item).strip() for item in to]
    return [value for value in values if value]


def send_resend_email(
    to: str | list[str] | None = None,
    subject: str = "",
    text: str = "",
    html: str = "",
    confirmed: bool = False,
) -> dict[str, Any]:
    if not confirmed:
        return {
            "tool": "email_send",
            "status": "needs_confirmation",
            "message": "Only send email after the user explicitly confirms.",
        }
    try:
        recipients = _normalize_recipients(to)
        if not recipients:
            raise ValueError("At least one recipient email is required")
        invalid = [email for email in recipients if not EMAIL_RE.match(email)]
        if invalid:
            raise ValueError(f"Invalid recipient email(s): {', '.join(invalid)}")

        subject = (subject or "").strip()
        text = (text or "").strip()
        html = (html or "").strip()
        if not subject:
            raise ValueError("subject is required")
        if not text and not html:
            raise ValueError("text or html body is required")

        api_key = os.getenv("RESEND_API")
        from_email = os.getenv("RESEND_FROM")
        if not api_key:
            raise RuntimeError("Missing RESEND_API env var")
        if not from_email:
            raise RuntimeError("Missing RESEND_FROM env var")

        body: dict[str, Any] = {
            "from": from_email,
            "to": recipients,
            "subject": subject,
        }
        if text:
            body["text"] = text
        if html:
            body["html"] = html

        response = requests.post(
            "https://api.resend.com/emails",
            json=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "tool": "email_send",
            "status": "sent",
            "id": data.get("id"),
            "to": recipients,
            "subject": subject,
        }
    except Exception as exc:
        return err("email_send", exc)
