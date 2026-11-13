# VFX — the 35 mm film look

There is no "generated effect" anywhere in these films. The film look is a **direct CPU
port of a real, MIT-licensed project found on GitHub**, and the port keeps its maths
stage for stage.

## Source

| | |
| --- | --- |
| Repo | [`claudiofabian-sudo/grainlight`](https://github.com/claudiofabian-sudo/grainlight) |
| File | `mpv/portable_config/shaders/35mm-4-equilibrado.glsl` (the "EQUILIBRADO" preset) |
| Also in that repo | `35mm-1-sutil`, `35mm-2-cine2000`, `35mm-3-veterana` — the same pipeline with different presets |
| Licence | MIT — Copyright (c) 2026 GRAINLIGHT contributors (full text in that repo's `LICENSE`) |

Upstream is an mpv `.hook` shader chain: real-time GPU film emulation with organic
grain, gate weave and halation. There is no libavfilter/CPU build of it, so the shader
was ported to numpy + Pillow in `tools/vfx.py`.

## What was ported

| Stage | Upstream | Port |
| --- | --- | --- |
| `35mm-4 gate weave` | slow drift + per-frame jitter | subpixel affine resample per frame |
| projector flicker | `FLICKER 0.0045` | per-frame brightness wobble |
| `35mm-4 grade` | S-curve, print fade, xenon warmth, saturation, lens vignette | identical constants |
| halation | 8-tap blur of highlights, red-shifted | gaussian highlight bloom, `vec3(1.0, 0.30, 0.12)` |
| `grano organico v2` | 3 octaves of PCG-hashed value noise + sparkle, luminance-weighted, decorrelated chroma | same recipe, vectorised |
| dust / hairs | `DUST_PROB 0.15`, `HAIR_PROB 0.35`, 1–2 frame motes | same probabilities |

**Not** ported: the cigarette-burn changeover cues (`CUE_PERIOD`). They are a projector
artefact and would read as a glitch in a 40-second short.

## Preset values used (verbatim from the shader)

```
WEAVE_X 0.00075   WEAVE_Y 0.00100   JITTER 0.00032   FLICKER 0.0045
CONTRAST 0.22     SATUR 1.13        WARMTH 0.045     FADE 0.012
VIGNETTE 0.15     HALATION 0.12     HAL_THR 0.70
GRAIN 0.078       GRAIN_SIZE 2.9    CHROMA_GR 0.32
DUST_PROB 0.15    HAIR_PROB 0.35
```

The port is run at `VFX_STRENGTH = 0.70` because h264 at CRF 23 compresses grain
aggressively; at full strength the encode swallows it and the file balloons.

## Camera

There are **no camera moves**. Frames are static plates (a deliberate choice after the
first cut), cuts are hard, and the only motion in the image comes from the film
emulation itself: weave, flicker, grain and the occasional dust mote. That reads as
"shot on film" rather than "slideshow", which is the effect we wanted.

## Rejected candidates

Browsed on GitHub before choosing: `josephmiclaus/p5.grain` (MIT, but WebGL/p5 only —
grain without the photochemical grade), `artzox/Film-Standalone` (ReShade `.fx`, needs a
GPU game pipeline), `Luci0n/CrowFX-Unity-Image-Effects` and the Unity/Godot grain
shaders (engine-locked). `grainlight` was the only one that is both a complete 35 mm
emulation **and** MIT-licensed, so it is the one that ships.
