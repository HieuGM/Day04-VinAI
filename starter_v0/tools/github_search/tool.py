from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _clamp_count(value: int | str | None, default: int = 5, maximum: int = 10) -> int:
    try:
        return max(1, min(int(value or default), maximum))
    except Exception:
        return default


def search_github(
    query: str = "",
    search_type: str = "repositories",
    max_results: int = 5,
    sort: str = "best_match",
) -> dict[str, Any]:
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query is required")

        search_type = search_type if search_type in {"repositories", "issues", "users"} else "repositories"
        endpoint = f"https://api.github.com/search/{search_type}"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "day04-research-agent"}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        params: dict[str, Any] = {"q": query, "per_page": _clamp_count(max_results)}
        if sort and sort != "best_match":
            params["sort"] = sort

        response = requests.get(endpoint, headers=headers, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        items: list[dict[str, Any]] = []
        for item in data.get("items", [])[: params["per_page"]]:
            if search_type == "repositories":
                items.append({
                    "title": item.get("full_name"),
                    "url": item.get("html_url"),
                    "source": "github.com",
                    "summary": item.get("description") or "",
                    "stars": item.get("stargazers_count"),
                    "language": item.get("language"),
                    "updated_at": item.get("updated_at"),
                })
            elif search_type == "issues":
                repo_url = (item.get("repository_url") or "").replace("https://api.github.com/repos/", "https://github.com/")
                items.append({
                    "title": item.get("title"),
                    "url": item.get("html_url"),
                    "source": repo_url or "github.com",
                    "summary": item.get("body") or "",
                    "state": item.get("state"),
                    "author": (item.get("user") or {}).get("login"),
                    "updated_at": item.get("updated_at"),
                })
            else:
                items.append({
                    "title": item.get("login"),
                    "url": item.get("html_url"),
                    "source": "github.com",
                    "summary": item.get("type") or "",
                    "score": item.get("score"),
                })

        return {
            "tool": "github_search",
            "query": query,
            "search_type": search_type,
            "count": len(items),
            "items": items,
        }
    except Exception as exc:
        return err("github_search", exc)
