from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def web_search(query: str = "", topic: str = "general", timeframe: str | None = "week", max_results: int = 5) -> dict[str, Any]:
    try:
        key = os.getenv("TAVILY_API_KEY")
        if not key:
            raise RuntimeError("Missing TAVILY_API_KEY env var")

        search_query = (query or "").strip()
        if not search_query:
            if topic == "news":
                search_query = "artificial intelligence AI news"
            else:
                return {
                    "tool": "web_search",
                    "status": "missing_query",
                    "message": "lookup requires a non-empty query. Pass keywords from the user request.",
                }
        if len(search_query) < 4:
            search_query = f"{search_query} news"

        body: dict[str, Any] = {
            "query": search_query,
            "topic": topic,
            "max_results": int(max_results or 5),
            "search_depth": "basic",
        }
        if timeframe:
            body["time_range"] = timeframe
        response = requests.post(
            "https://api.tavily.com/search",
            json=body,
            headers={"Authorization": f"Bearer {key}"},
            timeout=TIMEOUT,
        )
        if not response.ok:
            detail = response.text
            try:
                payload = response.json()
                detail = payload.get("detail") or payload.get("error") or detail
            except Exception:
                pass
            raise RuntimeError(f"Tavily {response.status_code}: {detail}")
        data = response.json()
        items = [{
            "title": item.get("title"),
            "url": item.get("url"),
            "source": domain(item.get("url", "")),
            "summary": item.get("content"),
            "score": item.get("score"),
        } for item in data.get("results", [])]
        return {
            "tool": "web_search",
            "query": search_query,
            "topic": topic,
            "timeframe": timeframe,
            "items": items,
        }
    except Exception as exc:
        return err("web_search", exc)

