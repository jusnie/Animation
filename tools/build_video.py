#!/usr/bin/env python3
"""
Builds one MIKAY film as a finished MP4.

Picture : static illustrated frames (no zoom), short cross-dissolves, the ported
          grainlight 35 mm film look from tools/vfx.py, burned-in subtitles, a MIKAY
          badge top-left and a running timecode top-right.
Sound   : render/{slug}_mix.wav from build_audio.py (narration + SFX, no music).

Run:  .venv/bin/python tools/build_video.py [day0|day1]
"""
import json
import os
import re
import subprocess
import sys

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import script_data as S
import vfx

W, H, FPS, FADE = S.W, S.H, S.FPS, S.FADE
FONTS, OUT = S.FONTS, S.OUT
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

MARGIN = 86
DISSOLVE = 0              # hard cuts between beats (line art ghosts in a mix)
TITLE_DUR = 1.5           # opening title card, so the title never sits on her face
VFX_STRENGTH = 0.70      # grainlight 35mm look, dialled in for h264
CRF = 23

TIME_Y = 66
TIME_SIZE = 92
LABEL_SIZE = 30
BADGE_Y = 66
BADGE_H = 78


def font(size, weight="800"):
    return ImageFont.truetype(os.path.join(FONTS, f"Poppins-{weight}.ttf"), size)


# ------------------------------------------------------------------------ subtitles
SENT_SPLIT = re.compile(r"(?<=[.!?])(?<![.]{3})\s+")


def wrap(text, fnt, max_w, draw):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def chunk_text(text, fnt, max_w, draw, max_lines=2):
    sentences = [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]
    chunks = []
    for sent in sentences:
        lines = wrap(sent, fnt, max_w, draw)
        for i in range(0, len(lines), max_lines):
            group = lines[i:i + max_lines]
            if chunks and len(group) == 1:
                prev = chunks[-1].split("\n")
                if (len(prev) < max_lines
                        and draw.textlength(prev[-1] + " " + group[0], font=fnt) <= max_w):
                    chunks[-1] = chunks[-1] + "\n" + group[0]
                    continue
            chunks.append("\n".join(group))
    return chunks


def timed_chunks(text, fnt, start, dur):
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    chunks = chunk_text(text, fnt, W * 0.70, probe)
    total = sum(len(c.replace("\n", " ")) for c in chunks) or 1
    out, t = [], start
    for i, c in enumerate(chunks):
        share = len(c.replace("\n", " ")) / total
        d = max(0.75, dur * share)
        if i == len(chunks) - 1:
            d = max(0.75, start + dur - t)
        out.append(dict(text=c, start=t, end=t + d))
        t += d
    return out


def subtitle_layer(text, fnt, stroke=9):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lines = text.split("\n")
    lh = fnt.size * 1.30
    base_y = H - 138 - lh * len(lines)
    for i, line in enumerate(lines):
        tw = d.textlength(line, font=fnt)
        d.text(((W - tw) / 2, base_y + i * lh), line, font=fnt,
               fill=(255, 255, 255, 255), stroke_width=stroke,
               stroke_fill=(0, 0, 0, 255))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i, line in enumerate(lines):
        tw = sd.textlength(line, font=fnt)
        sd.text(((W - tw) / 2, base_y + i * lh + 7), line, font=fnt,
                fill=(0, 0, 0, 130), stroke_width=stroke, stroke_fill=(0, 0, 0, 100))
    return Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)), layer)


def scrim():
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0.0, (y - H * 0.62) / (H * 0.38))
        g.putpixel((0, y), int(145 * (t ** 1.7)))
    g = g.resize((W, H))
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s.paste((0, 0, 0), (0, 0), g)
    return s


# ------------------------------------------------------------------------- overlays
def badge_layer(spec):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fb, fbig = font(46, "900"), font(120, "900")
    badge = spec["title_badge"]
    bw = d.textlength(badge, font=fb) + 62
    d.rounded_rectangle([MARGIN, BADGE_Y, MARGIN + bw, BADGE_Y + BADGE_H], radius=26,
                        fill=(224, 49, 39, 255), outline=(0, 0, 0, 255), width=6)
    d.text((MARGIN + 31, BADGE_Y + 14), badge, font=fb, fill=(255, 255, 255, 255))
    tx, ty = MARGIN, BADGE_Y + BADGE_H + 16
    big = spec["title_big"]
    d.text((tx + 6, ty + 9), big, font=fbig, fill=(0, 0, 0, 190),
           stroke_width=10, stroke_fill=(0, 0, 0, 190))
    d.text((tx, ty), big, font=fbig, fill=(245, 211, 28, 255),
           stroke_width=10, stroke_fill=(0, 0, 0, 255))
    return layer


def timecode_layer(seconds, label):
    """
    Timecode, upper right. Right-aligned block: big MM:SS on top, the film's day label
    underneath. Digits use a fixed advance, so the block never shifts or jitters.
    """
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fnum, flab = font(TIME_SIZE, "900"), font(LABEL_SIZE, "800")
    m, s = divmod(int(seconds), 60)
    text = f"{m:02d}:{s:02d}"

    digit_w = max(d.textlength(ch, font=fnum) for ch in "0123456789")
    colon_w = d.textlength(":", font=fnum)
    total_w = digit_w * 4 + colon_w
    right = W - MARGIN
    x = right - total_w

    # a soft pill behind the block keeps it readable over any plate
    lh_pill = d.textlength(label, font=flab)
    pad_x, pad_y = 26, 14
    pw = max(total_w, lh_pill) + pad_x * 2
    ph = TIME_SIZE + LABEL_SIZE + 8 + pad_y * 2
    px1 = right - pw + 6
    d.rounded_rectangle([px1, TIME_Y - pad_y, px1 + pw, TIME_Y - pad_y + ph],
                        radius=24, fill=(8, 10, 18, 128),
                        outline=(255, 255, 255, 34), width=2)

    # drop shadow, then the timecode itself
    ty = TIME_Y
    d.text((x + 5, ty + 7), text, font=fnum, fill=(0, 0, 0, 120),
           stroke_width=8, stroke_fill=(0, 0, 0, 120))
    cx = x
    for ch in text:
        if ch == ":":
            d.text((cx + (colon_w - d.textlength(ch, font=fnum)) / 2, ty), ch, font=fnum,
                   fill=(255, 255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0, 230))
            cx += colon_w
        else:
            gw = d.textlength(ch, font=fnum)
            d.text((cx + (digit_w - gw) / 2, ty), ch, font=fnum,
                   fill=(255, 255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0, 230))
            cx += digit_w

    # label under the clock, right-aligned to the same edge, letterspaced by hand
    ly = ty + TIME_SIZE + 6
    lw = sum(d.textlength(c, font=flab) + 4.6 for c in label) - 4.6
    lx = right - lw
    for c in label:
        d.text((lx, ly), c, font=flab, fill=(245, 211, 28, 235),
               stroke_width=5, stroke_fill=(0, 0, 0, 200))
        lx += d.textlength(c, font=flab) + 4.6
    return layer


def corner_scrim():
    """Very soft darkening in the top-right corner so the clock reads on bright frames."""
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    d = np.sqrt(((1 - x) * 1.15) ** 2 + (y * 1.25) ** 2)
    a = np.clip(1.0 - d / 0.55, 0, 1) ** 1.7 * 92
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.putalpha(Image.fromarray(a.astype(np.uint8), mode="L"))
    return layer


def title_card(spec):
    img = Image.new("RGB", (W, H), (7, 9, 15))
    d = ImageDraw.Draw(img)
    fb, fbig = font(46, "900"), font(112, "900")
    badge = spec["title_badge"]
    bw = d.textlength(badge, font=fb) + 62
    bx = (W - bw) / 2
    d.rounded_rectangle([bx, H / 2 - 165, bx + bw, H / 2 - 165 + BADGE_H], radius=26,
                        fill=(224, 49, 39, 255), outline=(0, 0, 0, 255), width=6)
    d.text((bx + 31, H / 2 - 165 + 14), badge, font=fb, fill=(255, 255, 255, 255))
    big = spec["title_big"]
    d.text(((W - d.textlength(big, font=fbig)) / 2, H / 2 - 56), big, font=fbig,
           fill=(245, 211, 28), stroke_width=10, stroke_fill=(0, 0, 0))
    return img


def end_card(spec):
    img = Image.new("RGB", (W, H), (6, 8, 16))
    d = ImageDraw.Draw(img)
    f1, f2 = font(150, "900"), font(40, "700")
    t1, t2 = spec["end_card"]["big"], spec["end_card"]["small"]
    d.text(((W - d.textlength(t1, font=f1)) / 2, H / 2 - 150), t1, font=f1,
           fill=(245, 211, 28), stroke_width=10, stroke_fill=(0, 0, 0))
    d.text(((W - d.textlength(t2, font=f2)) / 2, H / 2 + 60), t2, font=f2,
           fill=(150, 165, 200))
    return img


# ---------------------------------------------------------------------------- build
def main():
    key = sys.argv[1] if len(sys.argv) > 1 else S.DEFAULT_FILM
    spec = S.film(key)
    os.makedirs(OUT, exist_ok=True)
    fnt_sub = font(60, "800")
    timeline, total = S.build_timeline(spec, FFMPEG)

    for seg in timeline:
        seg["subs"] = timed_chunks(seg["text"], fnt_sub, seg["start"], seg["audio_dur"])
        flat = " ".join(x["text"].replace("\n", " ") for x in seg["subs"])
        assert re.sub(r"\s+", " ", flat).strip() == re.sub(r"\s+", " ", seg["text"]).strip(), \
            f"subtitle drift on {seg['id']}"

    # plates are static: one resize, no camera move at all
    plates = {}
    for seg in timeline:
        src = Image.open(S.frame_path(seg["frame"])).convert("RGB").resize((W, H), Image.LANCZOS)
        plates[seg["frame"]] = src
    card = end_card(spec).resize((W, H), Image.LANCZOS)

    look = vfx.FilmLook(W, H, strength=VFX_STRENGTH, cache={})
    sub_imgs = {id(s): subtitle_layer(s["text"], fnt_sub)
                for seg in timeline for s in seg["subs"]}
    scrim_img = scrim()
    corner = corner_scrim()
    badge = badge_layer(spec)
    tc_cache = [timecode_layer(i, spec["title_big"]) for i in range(0, int(total) + 3)]

    mix = os.path.join(OUT, f"{spec['slug']}_mix.wav")
    dst = os.path.join(OUT, f"{spec['slug']}.mp4")
    proc = subprocess.Popen(
        [FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", mix,
         "-c:v", "libx264", "-preset", "medium", "-crf", str(CRF), "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-shortest", dst],
        stdin=subprocess.PIPE)

    written = 0
    prev_plate = None

    def emit(img, fade=0.0):
        nonlocal written
        if fade:
            img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, fade)
        proc.stdin.write(img.tobytes())
        written += 1

    # ---- opening title card
    card_img = title_card(spec)
    for f in range(int(round(TITLE_DUR * FPS))):
        fade_in = min(1.0, (f / FPS) / 0.25)
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), card_img, fade_in)
        emit(look.apply(img, written))
    prev_plate = card_img

    for si, seg in enumerate(timeline):
        plate = plates[seg["frame"]]
        n = int(round(seg["duration"] * FPS))
        for f in range(n):
            tsec = seg["start"] + f / FPS
            img = plate
            if DISSOLVE and prev_plate is not None and f < DISSOLVE:
                img = Image.blend(prev_plate, plate, (f + 1) / (DISSOLVE + 1))
            img = img.convert("RGBA")

            active = next((x for x in seg["subs"] if x["start"] <= tsec < x["end"]), None)
            if active is not None:
                img = Image.alpha_composite(img, scrim_img)
                img = Image.alpha_composite(img, sub_imgs[id(active)])
            if tsec < S.TITLE_SHOW:
                img = Image.alpha_composite(img, badge)
            img = Image.alpha_composite(
                img, tc_cache[min(len(tc_cache) - 1, max(0, int(TITLE_DUR + tsec)))])

            frame = look.apply(img.convert("RGB"), written)
            fade = 1.0
            if f < 2 and prev_plate is card_img:      # step off the title card
                fade = (f + 1) / 3.0
            emit(frame, fade if fade < 1.0 else 0.0)
        prev_plate = plate

    # end card: no timecode, no badge, still graded
    n = int(round(spec["end_hold"] * FPS))
    for f in range(n):
        img = card
        if f < 4:
            img = Image.blend(prev_plate, card, (f + 1) / 5.0)
        frame = look.apply(img.convert("RGB"), written)
        fade = 1.0
        if f / FPS > spec["end_hold"] - 0.7:
            fade = max(0.0, (spec["end_hold"] - f / FPS) / 0.7)
        emit(frame, fade if fade < 1.0 else 0.0)

    proc.stdin.close()
    proc.wait()

    # ---- sidecars ----------------------------------------------------------------
    srt, idx = [], 1

    def ts(x):
        mm, ss = divmod(x, 60)
        return f"00:{int(mm):02d}:{ss:06.3f}".replace(".", ",")

    for seg in timeline:
        for s in seg["subs"]:
            srt.append(f"{idx}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text']}\n")
            idx += 1
    with open(os.path.join(OUT, f"{spec['slug']}.srt"), "w") as fh:
        fh.write("\n".join(srt))
    with open(os.path.join(OUT, f"timing-{key}.json"), "w") as fh:
        json.dump(dict(total=total, fps=FPS, frames=written, vfx="grainlight 35mm port",
                       segments=timeline), fh, indent=2)

    print(f"done: {dst}")
    print(f"length: {total:.1f}s  frames: {written}  size: {os.path.getsize(dst)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
