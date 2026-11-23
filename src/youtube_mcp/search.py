"""Video search using yt-dlp."""

from typing import Any

import yt_dlp

MAX_RESULTS = 50


def search_videos(query: str, max_results: int = 10, language: str = "en") -> dict[str, Any]:
    """Search YouTube videos by keyword.

    Args:
        query: Search keywords
        max_results: Number of videos to return (1-50, default: 10)
        language: Interface language code. YouTube machine-translates titles and
            descriptions into this language, so pass the language of the videos
            you are looking for (e.g. "ja") to get their original titles.

    Returns:
        Dict containing the query and a list of videos
    """
    n = max(1, min(max_results, MAX_RESULTS))
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": True,
        "extractor_args": {"youtube": {"lang": [language]}},
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{n}:{query}", download=False)
    except Exception as e:
        return {"query": query, "error": str(e)}

    entries = (info or {}).get("entries") or []
    return {
        "query": query,
        "videos": [
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "channel": e.get("channel") or e.get("uploader"),
                "duration": e.get("duration"),
                "view_count": e.get("view_count"),
                "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
            }
            for e in entries
            if e and e.get("id")
        ],
    }
