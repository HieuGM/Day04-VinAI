from __future__ import annotations

import html
import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err
from tools.format.tool import render_digest

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    parts: list[str] = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append("<br>")
            continue
        if stripped.startswith("### "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<h3>{html.escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<h2>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{html.escape(stripped[2:])}</li>")
        else:
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<p>{html.escape(stripped)}</p>")
    if in_list:
        parts.append("</ul>")
    return "\n".join(parts)


def send_email(
    to_email: str = "",
    subject: str = "",
    text: str = "",
    items: list[dict[str, Any]] | None = None,
    confirmed: bool = False,
) -> dict[str, Any]:
    if not confirmed:
        return {
            "tool": "send_email",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    recipient = to_email.strip()
    if not recipient:
        return {
            "tool": "send_email",
            "status": "missing_email",
            "message": "Ask the user for their Gmail address before sending.",
        }
    if not _EMAIL_RE.match(recipient):
        return {
            "tool": "send_email",
            "status": "invalid_email",
            "message": f"Invalid email address: {recipient}",
        }

    body = text.strip()
    if not body and items:
        digest = render_digest(
            items=items,
            template="daily_ai_vn",
            headline=subject.strip() or "Tin tức AI nổi bật",
        )
        body = (digest.get("markdown") or "").strip()

    if not body:
        return {
            "tool": "send_email",
            "status": "missing_content",
            "message": (
                "Email body is empty. Call lookup first, then send_email in a LATER turn "
                "with `items` from lookup or `text` from format markdown. "
                "Never call send_email in the same turn as lookup."
            ),
        }
    try:
        api_key = os.getenv("RESEND_API_KEY")
        from_addr = os.getenv("RESEND_FROM", "Tomorrow.io <news@tomorrow.io.vn>")
        if not api_key:
            raise RuntimeError("Missing RESEND_API_KEY env var")
        payload = {
            "from": from_addr,
            "to": [recipient],
            "subject": subject.strip() or "Tin tức AI nổi bật",
            "html": _markdown_to_html(body),
            "text": body,
        }
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AI20k-Day04-Research-Agent/1.0",
            },
            json=payload,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "tool": "send_email",
            "status": "sent",
            "to": recipient,
            "email_id": data.get("id"),
        }
    except Exception as exc:
        return err("send_email", exc)
