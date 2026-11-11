#!/usr/bin/env python3
"""
Film-look VFX for the MIKAY films.

This is a **direct CPU port of the shader in the `grainlight` repo** — an MIT-licensed
real-time 35 mm film emulation written as mpv .hook shaders:

    https://github.com/claudiofabian-sudo/grainlight
    mpv/portable_config/shaders/35mm-4-equilibrado.glsl   ("EQUILIBRADO" preset)
    MIT License, Copyright (c) 2026 GRAINLIGHT contributors

Upstream is GPU/mpv; there is no CPU/libavfilter build of it, so the maths was ported
stage by stage to numpy + Pillow. Everything that makes the look is kept:

  * 35mm-4 gate weave   — slow drift + per-frame jitter, subpixel
  * projector flicker   — per-frame brightness wobble
  * 35mm-4 grade        — S-curve contrast, print fade, xenon warmth, saturation,
                          projection-lens vignette, halation on highlights
  * organic grain v2    — 3-octave value noise + fine sparkle (PCG-style hashing),
                          luminance-weighted response, decorrelated chroma grain
  * dust / hair specks  — 1-2 frame motes, same probabilities as upstream

Deliberately *not* used: the cigarette-burn cue marks (CUE_PERIOD), which are a
changeover artefact and would read as a glitch in a short film.

Attribution text is kept in docs/VFX.md so the MIT notice travels with the project.
"""
import math

import numpy as np
from PIL import Image, ImageFilter

# ---- preset values, matching 35mm-4-equilibrado.glsl -------------------------------
WEAVE_X = 0.00075
WEAVE_Y = 0.00100
JITTER = 0.00032
FLICKER = 0.0045
CONTRAST = 0.22
SATUR = 1.13
WARMTH = 0.045
FADE_ = 0.012
VIGNETTE = 0.15
HALATION = 0.12
HAL_THR = 0.70
GRAIN = 0.078
GRAIN_SIZE = 2.9     # px at 4K, scaled by height
CHROMA_GR = 0.32
DUST_PROB = 0.15
HAIR_PROB = 0.35


def _h1(n):
    return np.modf(math.sin(n) * 43758.5453123)[0] % 1.0


def _hash2(ix, iy, seed):
    """PCG-ish integer hash, vectorised. Mirrors pcg3d()/hashf() upstream."""
    v = ((ix.astype(np.uint32) * np.uint32(1664525) + np.uint32(1013904223)) ^
         (iy.astype(np.uint32) * np.uint32(22695477)) ^ np.uint32((int(seed) * 747796405) & 0xFFFFFFFF))
    v ^= v >> np.uint32(16)
    v = v * np.uint32(2246822519) & np.uint32(0xFFFFFFFF)
    v ^= v >> np.uint32(13)
    v = v * np.uint32(3266489917) & np.uint32(0xFFFFFFFF)
    v ^= v >> np.uint32(16)
    return (v & np.uint32(0xFFFFFF)).astype(np.float32) / np.float32(16777216.0)


def _gnoise(shape, cell, seed):
    """Value noise at one octave: random lattice, smoothstep-interpolated (bilinear)."""
    h, w = shape
    cell = max(1.0, float(cell))
    gx = max(2, int(math.ceil(w / cell)) + 1)
    gy = max(2, int(math.ceil(h / cell)) + 1)
    lattice = _hash2(*np.meshgrid(np.arange(gx), np.arange(gy))[::-1], seed=seed)
    img = Image.fromarray((lattice * 255).astype(np.uint8), mode="L")
    up = img.resize((w, h), Image.BICUBIC)          # upscale straight to frame size
    return np.asarray(up, dtype=np.float32) / 255.0


def _grain_val(shape, gs, seed):
    """3 octaves + fine sparkle, exactly the mixture used upstream."""
    g = np.zeros(shape, dtype=np.float32)
    g += _gnoise(shape, gs, seed) - 0.5
    g += (_gnoise(shape, gs * 0.53, (seed ^ 0x85EBCA6B) & 0xFFFFFFFF) - 0.5) * 0.55
    g += (_gnoise(shape, gs * 1.91, (seed ^ 0xC2B2AE35) & 0xFFFFFFFF) - 0.5) * 0.60
    spark = _hash2(*np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))[::-1],
                   seed=(seed ^ 0xB5297A4D) & 0xFFFFFFFF) - 0.5
    g += spark * 0.22
    return g * 0.85


class FilmLook:
    """Applies the ported grade per frame. Stateful only through the frame index."""

    def __init__(self, width, height, strength=1.0, grain=True, dust=True, cache=None):
        self.w, self.h = width, height
        self.s = float(strength)
        self.use_grain = grain
        self.use_dust = dust
        self.gs = max(1.1, GRAIN_SIZE * max(height / 2160.0, 0.5))
        self._cache = cache if cache is not None else {}
        # static vignette mask
        ys = np.linspace(0, 1, height, dtype=np.float32)[:, None]
        xs = np.linspace(0, 1, width, dtype=np.float32)[None, :]
        d = np.sqrt(((xs - 0.5) * 1.1) ** 2 + (ys - 0.5) ** 2) * 1.5
        t = np.clip((d - 0.35) / (1.05 - 0.35), 0, 1)
        self.vig = (1.0 - VIGNETTE * self.s * (t * t * (3 - 2 * t))).astype(np.float32)

    # ------------------------------------------------------------------ sub-stages
    def _weave(self, frame, idx):
        """Gate weave + jitter, subpixel, via an affine resample of the frame."""
        t = float(idx)
        drift = (math.sin(t * 0.113) * 0.55 + math.sin(t * 0.041 + 1.3) * 0.45,
                 math.sin(t * 0.097 + 0.7) * 0.50 + math.sin(t * 0.033 + 2.1) * 0.50)
        jit = ((_h1(t * 1.371) - 0.5) * 2.0, (_h1(t * 2.113) - 0.5) * 2.0)
        ox = (drift[0] * WEAVE_X + jit[0] * JITTER) * self.h * self.s
        oy = (drift[1] * WEAVE_Y + jit[1] * JITTER) * self.h * self.s
        if abs(ox) < 0.05 and abs(oy) < 0.05:
            return frame
        return frame.transform(frame.size, Image.AFFINE, (1, 0, -ox, 0, 1, -oy),
                               resample=Image.BILINEAR)

    def _halation(self, arr):
        """Highlight bloom bled into the red channel, as upstream."""
        if HALATION * self.s <= 0:
            return arr
        lum = arr @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        hi = np.clip(lum - HAL_THR, 0, None)
        layer = Image.fromarray((np.clip(hi * 2.2, 0, 1) * 255).astype(np.uint8))
        r = max(2, int(self.h * 0.004))
        blur = layer.filter(ImageFilter.GaussianBlur(r))
        bl = np.asarray(blur, dtype=np.float32)[:, :, None] / 255.0
        tint = np.array([1.0, 0.30, 0.12], dtype=np.float32)
        return arr + bl * tint * (HALATION * self.s)

    def apply(self, frame, idx):
        arr = np.asarray(frame, dtype=np.float32) / 255.0
        arr = self._halation(arr)

        # S-curve (photochemical print response), then print fade
        s = arr * arr * (3.0 - 2.0 * arr)
        arr = arr + (s - arr) * (CONTRAST * self.s)
        arr = arr * (1.0 - FADE_ * self.s) + FADE_ * 0.45 * self.s

        # xenon / tungsten warmth
        warm = np.array([1.0 + WARMTH * 0.6, 1.0 + WARMTH * 0.15, 1.0 - WARMTH * 0.7],
                        dtype=np.float32)
        arr *= 1.0 + (warm - 1.0) * self.s

        # saturation
        lum = (arr @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[:, :, None]
        arr = lum + (arr - lum) * (1.0 + (SATUR - 1.0) * self.s)

        # projection vignette
        arr *= self.vig[:, :, None]

        # grain: lives in the midtones, hides in blacks and highlights
        if self.use_grain and GRAIN * self.s > 0:
            seed = (idx * 2654435761) & 0xFFFFFFFF
            l = np.clip((arr @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)), 0, 1)
            t1 = np.clip((l - 0.02) / 0.18, 0, 1)
            t2 = np.clip((l - 0.45) / 0.55, 0, 1)
            resp = (t1 * t1 * (3 - 2 * t1)) * (1.0 - 0.65 * (t2 * t2 * (3 - 2 * t2))) + 0.06
            key = seed
            if key in self._cache:
                g, cg = self._cache[key]
            else:
                g = _grain_val((self.h, self.w), self.gs, seed)
                cg = np.stack([
                    _gnoise((self.h, self.w), self.gs, (seed ^ 0xA511E9B3) & 0xFFFFFFFF),
                    _gnoise((self.h, self.w), self.gs, (seed ^ 0x63D83595) & 0xFFFFFFFF),
                    _gnoise((self.h, self.w), self.gs, (seed ^ 0x8C0DACF9) & 0xFFFFFFFF),
                ], axis=2) - 0.5
                if len(self._cache) > 6:      # bounded: ~70 MB of float32
                    self._cache.clear()
                self._cache[key] = (g, cg)
            arr = arr + (g[:, :, None] + cg * CHROMA_GR) * (GRAIN * self.s * resp[:, :, None])

        # dust and hairs, 1-2 frame motes
        if self.use_dust and DUST_PROB * self.s > 0:
            arr = self._dust(arr, idx)

        # projector flicker
        fl = 1.0 + ((_h1(idx * 0.719) - 0.5) * 2.0 * FLICKER
                    + math.sin(idx * 0.523) * FLICKER * 0.5) * self.s
        arr *= fl

        return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))

    def _dust(self, arr, idx):
        rng = np.random.default_rng((idx * 7919) & 0xFFFFFFFF)
        for i in range(3):
            if rng.random() >= DUST_PROB:
                continue
            cy, cx = rng.random(), rng.random()
            rad = (0.0012 + 0.0028 * rng.random()) * self.h * 2.0
            hair = rng.random() < HAIR_PROB
            stretch = 6.0 + 5.0 * rng.random() if hair else 1.0
            ang = rng.random() * 6.2831853
            y0, y1 = int(max(0, cy * self.h - rad * stretch - 2)), int(min(self.h, cy * self.h + rad * stretch + 2))
            x0, x1 = int(max(0, cx * self.w - rad * stretch - 2)), int(min(self.w, cx * self.w + rad * stretch + 2))
            if y1 <= y0 or x1 <= x0:
                continue
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            dx, dy = xx - cx * self.w, yy - cy * self.h
            ca, sa = math.cos(ang), math.sin(ang)
            u = dx * ca - dy * sa
            v = (dx * sa + dy * ca) / stretch
            dist = np.sqrt(u * u + v * v)
            a = np.clip(1.0 - (dist - rad * 0.35) / (rad * 0.65), 0, 1)[:, :, None]
            shade = 0.03 if rng.random() < 0.8 else 0.92
            arr[y0:y1, x0:x1] = arr[y0:y1, x0:x1] * (1 - a * 0.8) + shade * (a * 0.8)
        return arr
