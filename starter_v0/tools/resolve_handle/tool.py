from __future__ import annotations

# Static map for well-known accounts (lab helper — not a live API).
_HANDLE_MAP: dict[str, str] = {
    "sam altman": "sama",
    "elon musk": "elonmusk",
    "andrej karpathy": "karpathy",
    "openai": "openai",
    "yann lecun": "ylecun",
    "demis hassabis": "demishassabis",
}


def resolve_handle(display_name: str) -> dict[str, object]:
    key = (display_name or "").strip().lower()
    screenname = _HANDLE_MAP.get(key)
    return {
        "tool": "resolve_handle",
        "display_name": display_name,
        "screenname": screenname,
        "found": screenname is not None,
    }
