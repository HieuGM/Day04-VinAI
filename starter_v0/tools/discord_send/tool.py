from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def send_discord_message(text: str = "", username: str = "", confirmed: bool = False) -> dict[str, Any]:
    if not confirmed:
        return {
            "tool": "discord_send",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    try:
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            raise RuntimeError("Missing DISCORD_WEBHOOK_URL env var")
        text = (text or "").strip()
        if not text:
            raise ValueError("text is required")
        body: dict[str, Any] = {"content": text}
        if username:
            body["username"] = username
        response = requests.post(webhook_url, json=body, timeout=TIMEOUT)
        response.raise_for_status()
        return {"tool": "discord_send", "status": "sent", "status_code": response.status_code}
    except Exception as exc:
        return err("discord_send", exc)
