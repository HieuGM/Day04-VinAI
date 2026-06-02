from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err


def wikipedia_summary(query: str = "", language: str = "en", max_chars: int = 1200) -> dict[str, Any]:
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query is required")
        language = language if language in {"en", "vi"} else "en"
        try:
            max_chars = max(200, min(int(max_chars or 1200), 4000))
        except Exception:
            max_chars = 1200

        headers = {"User-Agent": "day04-research-agent/1.0 (educational lab)"}
        search_response = requests.get(
            f"https://{language}.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 1,
            },
            headers=headers,
            timeout=TIMEOUT,
        )
        search_response.raise_for_status()
        search_items = search_response.json().get("query", {}).get("search", [])
        title = search_items[0]["title"] if search_items else query

        summary_response = requests.get(
            f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'))}",
            headers=headers,
            timeout=TIMEOUT,
        )
        summary_response.raise_for_status()
        data = summary_response.json()
        extract = (data.get("extract") or "")[:max_chars]
        url = ((data.get("content_urls") or {}).get("desktop") or {}).get("page") or ""
        item = {
            "title": data.get("title") or title,
            "url": url,
            "source": f"{language}.wikipedia.org",
            "summary": extract,
            "description": data.get("description") or "",
        }
        return {
            "tool": "wikipedia_summary",
            "query": query,
            "language": language,
            "items": [item],
        }
    except Exception as exc:
        return err("wikipedia_summary", exc)
