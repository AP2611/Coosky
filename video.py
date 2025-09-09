import re
from typing import Optional

import requests


YOUTUBE_OEMBED = "https://www.youtube.com/oembed"


def extract_youtube_video_id(url: str) -> Optional[str]:
    if not url:
        return None
    patterns = [
        r"(?:v=|vi=)([a-zA-Z0-9_-]{11})",  # watch?v=ID or ?vi=
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def build_watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def build_embed_url(video_id: str) -> str:
    return f"https://www.youtube.com/embed/{video_id}"


def is_youtube_embeddable(url: str, timeout_seconds: int = 8) -> bool:
    try:
        r = requests.get(YOUTUBE_OEMBED, params={"url": url, "format": "json"}, timeout=timeout_seconds)
        return r.status_code == 200
    except requests.RequestException:
        return False


def normalize_and_validate(url: Optional[str]) -> tuple[Optional[str], bool]:
    if not url:
        return None, False
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return None, False
    watch_url = build_watch_url(video_id)
    embeddable = is_youtube_embeddable(watch_url)
    # Return embed url for UI players when possible
    return (build_embed_url(video_id) if embeddable else watch_url), embeddable


def fallback_search_url(query: str) -> str:
    # Basic YouTube search URL
    from urllib.parse import quote_plus

    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


