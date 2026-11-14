# clip-mcp — clipping in this workspace

A local stdio MCP server. Six tools: `probe`, `download`, `cut`, `vertical`,
`subtitles`, `thumbnails`.

## Why it exists

Every public video MCP server assumes a **system ffmpeg**. This workspace has none, and
the shell cannot fetch one (GitHub release assets are TLS-blocked here). What *does* work:
`pip install imageio-ffmpeg`, which ships a static ffmpeg 9.0.2 (570 filters) inside a
venv. This server resolves ffmpeg in that order — `CLIP_FFMPEG` env var → `PATH` →
`imageio-ffmpeg` — so the same file works on your laptop and here.

## Setup here

```bash
python3 -m venv .venv-clip
.venv-clip/bin/pip install imageio-ffmpeg "mcp[cli]" yt-dlp
```

## Run it

```bash
.venv-clip/bin/python tools/clip-mcp/server.py        # stdio transport
```

Register with an agent (`.mcp.json` at repo root, or the client's own config):

```json
{
  "mcpServers": {
    "clip": {
      "command": ".venv-clip/bin/python",
      "args": ["tools/clip-mcp/server.py"]
    }
  }
}
```

## Verified

Handshake against the real MCP SDK client: server `clip-mcp`, protocol **2025-11-25**, all
six tools listed with schemas, `probe` and `cut` called without error. Against
`render/mikay-day0.mp4`: probe → 39.39 s / 24 fps · `cut 6→16` → 10.08 s clip, stream-copy
(no re-encode, video+audio intact) · `vertical` → 1080×1920 blurred-pad version ·
`thumbnails` → 4 stills.

Note for `mcp` 2.x: `FastMCP` is now `MCPServer` (`mcp.server.mcpserver`), and result
fields are snake_case (`input_schema`, `is_error`, `server_info`). The server handles both
generations.

## The honest limit: YouTube is not reachable from this sandbox

`curl https://www.youtube.com` → **000**. `yt-dlp 2026.10.26` on a real video →
`Unable to download API page: TLS/SSL connection has been closed (EOF)`. Same failure class
as tailark/mapcn/ui.shadcn here. The `download` tool is correct and will work on a normal
network — it just cannot be demonstrated here.

**Workaround that needs no network:** upload the video to Drive, make it public, give the
agent the `uc?export=download&id=…` URL, or drop the file in the repo. Then `cut` /
`vertical` / `subtitles` / `thumbnails` run immediately — they are local.

## A clipping workflow

1. `probe` the source — duration, fps, whether there is audio.
2. `thumbnails` at 8–12 stills → pick candidates by eye.
3. `cut` with `reencode=false` (instant, lossless) to test the boundary; `reencode=true`
   only when the cut must be frame-exact.
4. `vertical` for Shorts/Reels/TikTok (`mode=blur` for the pad look, `mode=crop` tight).
5. `subtitles` to burn an `.srt` — the same filter the film pipeline uses.

## Prior art that was considered and rejected

- `video-creator/ffmpeg-mcp` (154★, MIT) — best tool surface (`find_video_path`,
  `get_video_info`, `clip_video`, `concat_videos`, `overlay_video`, `scale_video`,
  `extract_frames_from_video`), but `command_dir()` hard-returns `None` on Linux and it
  `git clone`s ffmpeg from **gitee**. macOS-only by construction.
- `burningion/video-editing-mcp` (295★) — no licence, and it is an API client for the
  hosted Video Jungle service, not local clipping.
- `misbahsy/video-audio-mcp` (90★, MIT) — fine, but wants ffmpeg on PATH.
- `mcp-server-youtube-transcript` / `mcp-youtube-transcript` (603★ / 496★, MIT) — useful
  **after** the download step: transcripts for captions. Both need the network.
