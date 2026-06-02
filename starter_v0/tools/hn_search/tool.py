from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _clamp_count(value: int | str | None, default: int = 5, maximum: int = 10) -> int:
    try:
        return max(1, min(int(value or default), maximum))
    except Exception:
        return default


def search_hacker_news(query: str = "", search_type: str = "story", max_results: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query is required")
        search_type = search_type if search_type in {"story", "comment", "all"} else "story"
        params: dict[str, Any] = {"query": query, "hitsPerPage": _clamp_count(max_results)}
        if search_type != "all":
            params["tags"] = search_type

        response = requests.get("https://hn.algolia.com/api/v1/search", params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        items: list[dict[str, Any]] = []
        for hit in data.get("hits", [])[: params["hitsPerPage"]]:
            object_id = hit.get("objectID")
            url = hit.get("url") or (f"https://news.ycombinator.com/item?id={object_id}" if object_id else "")
            title = hit.get("title") or hit.get("story_title") or f"HN item {object_id}"
            items.append({
                "title": title,
                "url": url,
                "source": "news.ycombinator.com",
                "summary": hit.get("comment_text") or hit.get("story_text") or "",
                "author": hit.get("author"),
                "points": hit.get("points"),
                "comments": hit.get("num_comments"),
                "created_at": hit.get("created_at"),
            })
        return {
            "tool": "hn_search",
            "query": query,
            "search_type": search_type,
            "count": len(items),
            "items": items,
        }
    except Exception as exc:
        return err("hn_search", exc)
