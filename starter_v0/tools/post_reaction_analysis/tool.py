from __future__ import annotations

from typing import Any

from tools._shared import err


def _num(value: Any) -> int:
    if value is None or value == "":
        return 0
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def _engagement_label(rate: float | None, total_reactions: int) -> str:
    if total_reactions == 0:
        return "insufficient_reaction_data"
    if rate is None:
        if total_reactions >= 1000:
            return "strong_reaction_volume"
        if total_reactions >= 100:
            return "moderate_reaction_volume"
        return "low_reaction_volume"
    if rate >= 0.05:
        return "high_engagement"
    if rate >= 0.02:
        return "moderate_engagement"
    return "low_engagement"


def _interpretation(
    *,
    total_reactions: int,
    engagement_rate: float | None,
    comment_share: float | None,
    amplification_share: float | None,
) -> list[str]:
    notes: list[str] = []
    label = _engagement_label(engagement_rate, total_reactions)

    if label == "insufficient_reaction_data":
        return ["Not enough reaction data to analyze the post reliably."]
    if label == "high_engagement":
        notes.append("The post is performing strongly relative to views.")
    elif label == "moderate_engagement":
        notes.append("The post has a healthy engagement level.")
    elif label == "low_engagement":
        notes.append("The post is receiving limited engagement relative to views.")
    elif label == "strong_reaction_volume":
        notes.append("The post has strong raw reaction volume, but views are needed for an engagement rate.")
    elif label == "moderate_reaction_volume":
        notes.append("The post has moderate raw reaction volume, but views are needed for an engagement rate.")
    else:
        notes.append("The post has low raw reaction volume.")

    if comment_share is not None and comment_share >= 0.35:
        notes.append("Comments make up a large share of reactions, suggesting discussion or controversy.")
    if amplification_share is not None and amplification_share >= 0.25:
        notes.append("Shares, reposts, or quotes are high, suggesting the post travels beyond the original audience.")
    if comment_share is not None and amplification_share is not None and comment_share < 0.1 and amplification_share < 0.1:
        notes.append("Most reactions are lightweight likes, so the post may be agreeable but not very discussion-driving.")

    return notes


def _recommendations(
    *,
    post_text: str,
    engagement_rate: float | None,
    comment_share: float | None,
    amplification_share: float | None,
) -> list[str]:
    tips: list[str] = []
    if engagement_rate is not None and engagement_rate < 0.02:
        tips.append("Make the opening clearer and more specific so the audience understands the value quickly.")
    if comment_share is not None and comment_share < 0.12:
        tips.append("Add a focused question or opinion to invite comments.")
    if amplification_share is not None and amplification_share < 0.12:
        tips.append("Add a concrete takeaway, checklist, or surprising data point to make the post easier to share.")
    if len(post_text.strip()) > 600:
        tips.append("Consider shortening the post or moving details into bullets.")
    if not tips:
        tips.append("Keep the current direction, then test a stronger hook or clearer call to action in the next post.")
    return tips


def analyze_post_reactions(
    post_text: str = "",
    url: str = "",
    platform: str = "social",
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    reposts: int = 0,
    quotes: int = 0,
    views: int = 0,
    bookmarks: int = 0,
) -> dict[str, Any]:
    try:
        likes_n = _num(likes)
        comments_n = _num(comments)
        shares_n = _num(shares)
        reposts_n = _num(reposts)
        quotes_n = _num(quotes)
        views_n = _num(views)
        bookmarks_n = _num(bookmarks)

        amplifications = shares_n + reposts_n + quotes_n
        total_reactions = likes_n + comments_n + amplifications + bookmarks_n
        engagement_rate = _rate(total_reactions, views_n)
        comment_share = _rate(comments_n, total_reactions)
        amplification_share = _rate(amplifications, total_reactions)

        metrics = {
            "likes": likes_n,
            "comments": comments_n,
            "shares": shares_n,
            "reposts": reposts_n,
            "quotes": quotes_n,
            "views": views_n,
            "bookmarks": bookmarks_n,
            "amplifications": amplifications,
            "total_reactions": total_reactions,
            "engagement_rate": engagement_rate,
            "comment_share": comment_share,
            "amplification_share": amplification_share,
        }

        return {
            "tool": "analyze_post_reactions",
            "platform": platform,
            "url": url,
            "post_preview": post_text.strip()[:240],
            "metrics": metrics,
            "engagement_label": _engagement_label(engagement_rate, total_reactions),
            "interpretation": _interpretation(
                total_reactions=total_reactions,
                engagement_rate=engagement_rate,
                comment_share=comment_share,
                amplification_share=amplification_share,
            ),
            "recommendations": _recommendations(
                post_text=post_text,
                engagement_rate=engagement_rate,
                comment_share=comment_share,
                amplification_share=amplification_share,
            ),
            "missing_fields": [] if views_n else ["views"],
        }
    except Exception as exc:
        return err("analyze_post_reactions", exc)
