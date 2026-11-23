# kzmshx-youtube-mcp

An MCP server for extracting YouTube video transcripts and metadata.

## Configuration

```json
{
  "mcpServers": {
    "youtube": {
      "command": "uvx",
      "args": ["kzmshx-youtube-mcp"]
    }
  }
}
```

## Installation (Optional)

If you prefer to install globally:

```bash
pip install kzmshx-youtube-mcp
# or
uv tool install kzmshx-youtube-mcp
```

## Tools

### get_transcript

Get transcript text from a YouTube video.

| Parameter         | Type   | Description                              |
| ----------------- | ------ | ---------------------------------------- |
| `url`             | string | YouTube URL or video ID                  |
| `language`        | string | Language code (default: auto)            |
| `with_timestamps` | bool   | Include timestamps (default: false)      |

**Example:**

```json
// Input
{ "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ" }

// Output
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "transcript": "We're no strangers to love\nYou know the rules and so do I..."
}
```

### get_video_info

Get metadata from a YouTube video.

| Parameter | Type   | Description             |
| --------- | ------ | ----------------------- |
| `url`     | string | YouTube URL or video ID |

**Example:**

```json
// Input
{ "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ" }

// Output
{
  "id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "description": "...",
  "duration": 213,
  "channel": "Rick Astley",
  "upload_date": "2009-10-25",
  "view_count": 1500000000,
  "available_languages": ["en", "ja", "es", "fr"]
}
```

### search_videos

Search YouTube videos by keyword. No API key is needed.

| Parameter     | Type   | Description                             |
| ------------- | ------ | --------------------------------------- |
| `query`       | string | Search keywords                         |
| `max_results` | int    | Number of videos, 1-50 (default: 10)    |
| `language`    | string | Interface language code (default: `en`) |

YouTube machine-translates titles into `language`. Pass the language of the videos you are looking for to get their original titles.

**Example:**

```json
// Input
{ "query": "rick astley", "max_results": 1 }

// Output
{
  "query": "rick astley",
  "videos": [
    {
      "id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up",
      "channel": "Rick Astley",
      "duration": 213,
      "view_count": 1500000000,
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
  ]
}
```

## License

MIT
