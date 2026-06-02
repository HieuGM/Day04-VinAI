from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def _clamp_count(value: int | str | None, default: int = 5, maximum: int = 15) -> int:
    try:
        return max(1, min(int(value or default), maximum))
    except Exception:
        return default


def _text(element: ET.Element | None, default: str = "") -> str:
    if element is None or element.text is None:
        return default
    text = re.sub(r"\s+", " ", element.text).strip()
    return text


def _child(element: ET.Element, name: str) -> ET.Element | None:
    found = element.find(name)
    if found is not None:
        return found
    for child in element:
        if child.tag.endswith("}" + name) or child.tag == name:
            return child
    return None


def _atom_link(entry: ET.Element) -> str:
    for child in entry:
        if child.tag.endswith("}link") or child.tag == "link":
            href = child.attrib.get("href")
            if href:
                return href
    return ""


def read_rss_feed(feed_url: str = "", max_items: int = 5) -> dict[str, Any]:
    try:
        feed_url = (feed_url or "").strip()
        if not feed_url:
            raise ValueError("feed_url is required")
        max_items = _clamp_count(max_items)
        response = requests.get(feed_url, headers={"User-Agent": "day04-research-agent"}, timeout=TIMEOUT)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        items: list[dict[str, Any]] = []
        channel = root.find("channel")
        if channel is not None:
            feed_title = _text(_child(channel, "title"), domain(feed_url))
            entries = channel.findall("item")
            for entry in entries[:max_items]:
                link = _text(_child(entry, "link"))
                items.append({
                    "title": _text(_child(entry, "title"), "Untitled"),
                    "url": link,
                    "source": feed_title,
                    "summary": _text(_child(entry, "description")),
                    "published_at": _text(_child(entry, "pubDate")),
                })
        else:
            feed_title = _text(_child(root, "title"), domain(feed_url))
            entries = [child for child in root if child.tag.endswith("}entry") or child.tag == "entry"]
            for entry in entries[:max_items]:
                link = _atom_link(entry)
                items.append({
                    "title": _text(_child(entry, "title"), "Untitled"),
                    "url": link,
                    "source": feed_title,
                    "summary": _text(_child(entry, "summary")) or _text(_child(entry, "content")),
                    "published_at": _text(_child(entry, "published")) or _text(_child(entry, "updated")),
                })

        return {
            "tool": "rss_read",
            "feed_url": feed_url,
            "count": len(items),
            "items": items,
        }
    except Exception as exc:
        return err("rss_read", exc)
