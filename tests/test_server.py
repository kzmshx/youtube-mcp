"""Smoke tests through an in-memory MCP client.

These run on every dependency update, so they check the parts of FastMCP,
youtube-transcript-api, and yt-dlp that this server relies on, without
calling YouTube.
"""

import dataclasses
from typing import Any

import pytest
import yt_dlp
from fastmcp import Client
from youtube_transcript_api import (
    FetchedTranscriptSnippet,
    NoTranscriptFound,
    Transcript,
    TranscriptList,
    YouTubeTranscriptApi,
)

import youtube_mcp.search as search_module
import youtube_mcp.transcript as transcript_module
import youtube_mcp.video_info as video_info_module
from youtube_mcp.server import mcp

VIDEO_ID = "dQw4w9WgXcQ"


class TestLibraryContract:
    """The library APIs used by the tools still exist."""

    def test_transcript_api(self) -> None:
        assert callable(YouTubeTranscriptApi().list)
        assert callable(TranscriptList.find_transcript)
        assert callable(Transcript.fetch)
        assert {"text", "start"} <= {f.name for f in dataclasses.fields(FetchedTranscriptSnippet)}
        assert issubclass(NoTranscriptFound, Exception)

    def test_yt_dlp(self) -> None:
        assert callable(yt_dlp.YoutubeDL({"quiet": True}).extract_info)


class TestTools:
    """Tools are registered and callable over MCP."""

    async def test_list_tools(self) -> None:
        async with Client(mcp) as client:
            tools = {t.name: t for t in await client.list_tools()}
        assert set(tools) == {"get_transcript", "get_video_info", "search_videos"}
        assert "url" in tools["get_transcript"].inputSchema["properties"]
        assert "url" in tools["get_video_info"].inputSchema["properties"]
        assert "query" in tools["search_videos"].inputSchema["properties"]

    async def test_get_transcript(self, monkeypatch: pytest.MonkeyPatch) -> None:
        snippets = [FetchedTranscriptSnippet(text="hello", start=0.0, duration=1.0)]

        class FakeTranscript:
            language_code = "en"

            def fetch(self) -> list[FetchedTranscriptSnippet]:
                return snippets

        class FakeList:
            def find_transcript(self, languages: list[str]) -> FakeTranscript:
                if "en" in languages:
                    return FakeTranscript()
                raise NoTranscriptFound(VIDEO_ID, languages, None)

        class FakeApi:
            def list(self, video_id: str) -> FakeList:
                assert video_id == VIDEO_ID
                return FakeList()

        monkeypatch.setattr(transcript_module, "YouTubeTranscriptApi", FakeApi)
        async with Client(mcp) as client:
            result = await client.call_tool(
                "get_transcript", {"url": f"https://youtu.be/{VIDEO_ID}", "with_timestamps": True}
            )
        assert result.data == {"video_id": VIDEO_ID, "language": "en", "transcript": "[0:00] hello"}

    async def test_get_video_info(self, monkeypatch: pytest.MonkeyPatch) -> None:
        info: dict[str, Any] = {
            "title": "t",
            "description": "d",
            "duration": 1,
            "channel": "c",
            "upload_date": "20250101",
            "view_count": 2,
            "subtitles": {"en": []},
            "automatic_captions": {"ja": []},
        }

        class FakeYDL:
            def __init__(self, opts: dict[str, Any]) -> None:
                pass

            def __enter__(self) -> "FakeYDL":
                return self

            def __exit__(self, *args: object) -> None:
                pass

            def extract_info(self, url: str, download: bool) -> dict[str, Any]:
                assert url.endswith(VIDEO_ID)
                return info

        monkeypatch.setattr(video_info_module.yt_dlp, "YoutubeDL", FakeYDL)
        async with Client(mcp) as client:
            result = await client.call_tool("get_video_info", {"url": VIDEO_ID})
        assert result.data["upload_date"] == "2025-01-01"
        assert result.data["available_languages"] == ["en", "ja"]

    async def test_search_videos(self, monkeypatch: pytest.MonkeyPatch) -> None:
        seen: dict[str, Any] = {}

        class FakeYDL:
            def __init__(self, opts: dict[str, Any]) -> None:
                seen["opts"] = opts

            def __enter__(self) -> "FakeYDL":
                return self

            def __exit__(self, *args: object) -> None:
                pass

            def extract_info(self, url: str, download: bool) -> dict[str, Any]:
                seen["url"] = url
                return {
                    "entries": [
                        {"id": VIDEO_ID, "title": "t", "channel": "c", "duration": 1, "view_count": 2, "url": None},
                        None,
                    ]
                }

        monkeypatch.setattr(search_module.yt_dlp, "YoutubeDL", FakeYDL)
        async with Client(mcp) as client:
            result = await client.call_tool("search_videos", {"query": "q", "max_results": 99, "language": "ja"})
        assert seen["url"] == "ytsearch50:q"  # max_results is capped
        assert seen["opts"]["extract_flat"] is True
        assert seen["opts"]["extractor_args"] == {"youtube": {"lang": ["ja"]}}
        assert result.data == {
            "query": "q",
            "videos": [
                {
                    "id": VIDEO_ID,
                    "title": "t",
                    "channel": "c",
                    "duration": 1,
                    "view_count": 2,
                    "url": f"https://www.youtube.com/watch?v={VIDEO_ID}",
                }
            ],
        }
