"""clip-mcp — a local stdio MCP server for video clipping.

The gap it fills: the public clip/video MCP servers all assume a system ffmpeg that
does not exist in this workspace. This one resolves ffmpeg through imageio-ffmpeg
(pip-installable, ships a static binary), so it works with nothing on PATH.

Tools
  probe       duration / streams / fps of any local file
  download    yt-dlp fetch of a URL (fails cleanly where YouTube is unreachable)
  cut         trim a clip, stream-copy when possible else re-encode
  vertical    reframe to 9:16 with a blurred pad or a centre crop
  subtitles   burn an .srt onto a clip
  thumbnails  grab N stills at even intervals
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from typing import Any

try:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

mcp = _Server("clip-mcp")

FFMPEG = os.environ.get("CLIP_FFMPEG") or shutil.which("ffmpeg") or ""
FFPROBE = os.environ.get("CLIP_FFPROBE") or shutil.which("ffprobe") or ""


def _bootstrap() -> None:
    """Find ffmpeg/ffprobe: env var, PATH, then imageio-ffmpeg's bundled binary."""
    global FFMPEG, FFPROBE
    if FFMPEG and FFPROBE:
        return
    try:
        import imageio_ffmpeg

        if not FFMPEG:
            FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # pragma: no cover - only when the package is missing
        pass
    if FFMPEG:
        # imageio-ffmpeg ships only ffmpeg; probe works through `ffmpeg -i` anyway
        FFPROBE = FFPROBE or FFMPEG


def _run(args: list[str], timeout: int = 600) -> dict[str, Any]:
    _bootstrap()
    if not FFMPEG:
        return {"ok": False, "error": "no ffmpeg found; pip install imageio-ffmpeg"}
    proc = subprocess.run([FFMPEG, *args], capture_output=True, text=True, timeout=timeout)
    return {
        "ok": proc.returncode == 0,
        "code": proc.returncode,
        "stderr_tail": "\n".join(proc.stderr.strip().splitlines()[-6:]),
        "stdout_tail": "\n".join(proc.stdout.strip().splitlines()[-3:]),
    }


def _duration(path: str) -> float:
    """Duration in seconds, parsed from `ffmpeg -i` (no ffprobe needed)."""
    _bootstrap()
    proc = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            stamp = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = stamp.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


@mcp.tool()
def probe(path: str) -> dict[str, Any]:
    """Report duration, video/audio streams, resolution, fps and codec for a local file."""
    _bootstrap()
    if not os.path.isfile(path):
        return {"ok": False, "error": f"not found: {path}"}
    proc = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    info: dict[str, Any] = {"ok": True, "path": path, "duration_s": _duration(path), "streams": []}
    for line in proc.stderr.splitlines():
        if "Stream #" in line:
            info["streams"].append(line.split("Stream #")[1].strip())
        if "Video:" in line and "fps" in line and "fps" not in info:
            frag = [p for p in line.split(",") if "fps" in p]
            if frag:
                info["fps"] = frag[0].strip()
    return info


@mcp.tool()
def download(url: str, out_dir: str = "clips", max_height: int = 1080) -> dict[str, Any]:
    """Download a video with yt-dlp, capped to max_height. Fails cleanly if the host is blocked."""
    if not shutil.which("yt-dlp"):
        return {"ok": False, "error": "yt-dlp not on PATH; pip install yt-dlp"}
    os.makedirs(out_dir, exist_ok=True)
    fmt = f"bv*[height<={max_height}]+ba/b[height<={max_height}]/b"
    proc = subprocess.run(
        ["yt-dlp", "-f", fmt, "--merge-output-format", "mp4",
         "-o", os.path.join(out_dir, "%(title).80s-%(id)s.%(ext)s"), url],
        capture_output=True, text=True, timeout=3600,
    )
    tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-6:])
    if proc.returncode != 0:
        return {"ok": False, "error": "download failed (see tail)", "tail": tail}
    return {"ok": True, "tail": tail}


@mcp.tool()
def cut(src: str, start_s: float, end_s: float, out: str = "clip.mp4", reencode: bool = False) -> dict[str, Any]:
    """Cut [start_s, end_s] out of src. Stream-copies by default; re-encodes when reencode=True."""
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    dur = max(0.05, end_s - start_s)
    if reencode:
        args = ["-y", "-ss", str(start_s), "-i", src, "-t", str(dur),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    else:
        args = ["-y", "-ss", str(start_s), "-i", src, "-t", str(dur), "-c", "copy", out]
    result = _run(args)
    result["out"] = out
    return result


@mcp.tool()
def vertical(src: str, out: str = "clip-vertical.mp4", mode: str = "blur") -> dict[str, Any]:
    """Reframe to 1080x1920. mode=blur pads with a blurred copy; mode=crop centre-crops."""
    if mode == "crop":
        vf = "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos"
        args = ["-y", "-i", src, "-vf", vf]
    else:
        vf = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "gblur=sigma=28[bg];[0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2"
        )
        args = ["-y", "-i", src, "-filter_complex", vf]
    args += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac",
             "-b:a", "192k", "-movflags", "+faststart", out]
    result = _run(args)
    result["out"] = out
    return result


@mcp.tool()
def subtitles(src: str, srt: str, out: str = "clip-subbed.mp4",
              font_size: int = 20, margin_v: int = 90) -> dict[str, Any]:
    """Burn an .srt onto the clip with the subtitles filter."""
    style = f"FontSize={font_size},MarginV={margin_v},Outline=2,Shadow=0,BorderStyle=1"
    args = ["-y", "-i", src, "-vf", f"subtitles={srt}:force_style='{style}'",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "copy",
            "-movflags", "+faststart", out]
    result = _run(args)
    result["out"] = out
    return result


@mcp.tool()
def thumbnails(src: str, count: int = 8, out_dir: str = "thumbs") -> dict[str, Any]:
    """Write `count` evenly spaced stills into out_dir, for picking clip points."""
    os.makedirs(out_dir, exist_ok=True)
    dur = _duration(src)
    if dur <= 0:
        return {"ok": False, "error": "could not read duration"}
    made: list[str] = []
    for i in range(count):
        t = dur * (i + 0.5) / count
        target = os.path.join(out_dir, f"{os.path.splitext(os.path.basename(src))[0]}-{i:02d}.jpg")
        r = _run(["-y", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", "-q:v", "3", target], timeout=120)
        if r["ok"]:
            made.append(target)
    return {"ok": bool(made), "count": len(made), "files": made}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
