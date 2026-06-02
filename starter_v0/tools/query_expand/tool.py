from __future__ import annotations

import re
from typing import Any


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        normalized = item.lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            output.append(item)
    return output


def expand_search_queries(
    topic: str = "",
    intent: str = "general",
    language: str = "en",
    max_variants: int = 5,
) -> dict[str, Any]:
    topic = _clean(topic)
    intent = intent if intent in {"general", "news", "academic", "social", "policy"} else "general"
    language = language if language in {"en", "vi"} else "en"
    max_variants = max(1, min(int(max_variants or 5), 10))

    if not topic:
        return {
            "tool": "query_expand",
            "error": "missing_topic",
            "queries": [],
        }

    suffixes = {
        "en": {
            "general": ["overview", "key developments", "explainer", "use cases", "risks"],
            "news": ["latest news", "today", "this week", "recent developments", "market impact"],
            "academic": ["survey paper", "benchmark", "method", "arXiv", "limitations"],
            "social": ["discussion", "top posts", "reactions", "X Twitter", "community sentiment"],
            "policy": ["policy", "compliance", "guidelines", "risk controls", "governance"],
        },
        "vi": {
            "general": ["tong quan", "dien bien chinh", "giai thich", "ung dung", "rui ro"],
            "news": ["tin moi nhat", "hom nay", "tuan nay", "dien bien gan day", "tac dong thi truong"],
            "academic": ["bai khao sat", "benchmark", "phuong phap", "arXiv", "han che"],
            "social": ["thao luan", "bai dang noi bat", "phan ung", "X Twitter", "xu huong cong dong"],
            "policy": ["chinh sach", "tuan thu", "huong dan", "kiem soat rui ro", "quan tri"],
        },
    }

    queries = [topic, *[f"{topic} {suffix}" for suffix in suffixes[language][intent]]]
    queries = _unique(queries)[:max_variants]
    return {
        "tool": "query_expand",
        "topic": topic,
        "intent": intent,
        "language": language,
        "queries": queries,
        "count": len(queries),
    }
