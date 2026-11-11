#!/usr/bin/env bash
# Render pipeline for the MIKAY films.
#   ./render.sh                  the animated episode (ep0)
#   ./render.sh ep0               one film (ep0 | day0 | day1)
#   ./render.sh day0 video       picture only (audio mix already exists)
set -euo pipefail
cd "$(dirname "$0")"

PY=.venv/bin/python
if [ ! -x "$PY" ]; then
  echo "creating venv..."
  python3 -m venv .venv
  .venv/bin/pip install --quiet imageio-ffmpeg numpy scipy pillow fonttools brotli
fi

FILM="${1:-ep0}"
MODE="${2:-all}"

if [ "$MODE" != "video" ]; then
  mkdir -p audio/sfx
  $PY tools/make_sfx.py
  ( cd tools && ../$PY build_audio.py "$FILM" )
fi

$PY tools/build_video.py "$FILM"

echo
echo "render/mikay-${FILM}.mp4        picture + narration + sound effects + 35mm film look"
echo "render/mikay-${FILM}.srt        subtitles (same strings as the voice track)"
echo "render/mikay-${FILM}_mix.wav    master audio (no music)"
echo "render/audio-plan-${FILM}.json  every cue, its timecode and its gain"
