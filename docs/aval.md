# AVAL — interactive video format, installed and verified

[pixel-point/aval](https://github.com/pixel-point/aval) · MIT · 1.4k★ · "A new
open-source format for interactive video on the web, with a built-in state machine,
frame-accurate transitions, and packed-alpha transparency."

This is the entry in this repo's stack that is **specifically about showing animation on
a web page** — which is what the episode site has to do. Everything else installed for
the site is design opinion or generic tooling. This one is the delivery format.

## What it is

One logical motion is published as a **codec bundle**: a `.avl` file per codec
(AV1, VP9, H.265, H.264) plus `build.json`. The browser picks the first candidate in
AVAL's fixed **AV1 → VP9 → H.265 → H.264** ladder that decodes, so DOM order cannot
change the policy. Inside the file: a state graph, authored triggers, bounded
transitions, reversals, and optional packed-alpha transparency ("packed-alpha", not
WebM alpha).

Two consequences that matter for this project:

1. **It is not a `<video>`.** Loops, state changes and reversals are frame-accurate,
   which is the difference between a hero that cuts cleanly and one that stutters.
2. **Transparency works.** The films are drawn art on a background; a composited AVAL
   could put Mikay over the page's own ground instead of a baked-in plate.

## Installed in `site/`

| Package | Version | Licence | Role |
|---|---|---|---|
| `@pixel-point/aval-react` | 1.0.2 | MIT | `useAval()` + `AvalComponent`; peer `react` |
| `@pixel-point/aval-element` | 1.0.3 | MIT | the custom element underneath |

Verified with esbuild — both import families compile with **0 errors**:

```tsx
import { useAval } from "@pixel-point/aval-react";        // 991 KB eager
import { useAval } from "@pixel-point/aval-react/lazy";   // runtime in its own chunk

export function Motion() {
  const { aval, AvalComponent } = useAval({
    sources: { vp9: "/motion/favorite/vp9.avl", h264: "/motion/favorite/h264.avl" },
    state: "idle",
    autoplay: true,
    autoBind: true,
  });
  return (
    <>
      <AvalComponent width={160} height={160} aria-hidden />
      <button onClick={() => void aval.setState("favorite")}>Favorite</button>
    </>
  );
}
```

`sources` takes **URL strings only**, at least one, and the codec preference is AVAL's —
you do not choose it. `AvalComponent` is bound to its `useAval()` call; mount one at a
time. The reactive `aval` object exposes readiness, requested/visual state, transition
status, authored names, last error, and commands (prepare, state, events, playback);
snapshot changes rerender React, decoded frames do not.

**Required error handling — the docs are emphatic about this:** AVAL *deliberately does
not* create, reveal or hide fallback content. If WebCodecs is missing or no authored codec
decodes, `prepare()` rejects with `AvalPlaybackError` and the element fires one fatal
`error` event. The app must attach that listener **before** registering the element and
branch on `failure.code` (`unsupported-browser`, `unsupported-profile`), never on the
message text. For a film site the sensible fallback is an ordinary `<video>` of the same
MP4.

## Compiling `.avl` — the tool works, the encoder does not

`@pixel-point/aval-compiler@1.1.0` (MIT) is on npm, binary `avl`. It parses and validates
a `motion.json` project fully — I drove it through five distinct schema errors — and then
stops at the encoder:

```
$ npx avl compile motion.json --out out
ERROR FFMPEG_NOT_FOUND — Executable not found: ffmpeg
```

`avl compile`, `avl alpha`, `avl dev`, `avl inspect`, `avl validate` and `avl unpack` all
shell out to ffmpeg. This sandbox has no system ffmpeg, so a bundle cannot be produced
here. On a machine with ffmpeg:

```bash
npx @pixel-point/aval-compiler compile motion.json --out dist/motion
# → dist/motion/vp9.avl + dist/motion/build.json
```

### The project schema (validated by error, not by guesswork)

A minimal working `motion.json` — eleven top-level fields, **all required** even when
empty:

```json
{
  "projectVersion": "1.0",
  "alpha": "opaque",
  "canvas": { "width": 720, "height": 1280, "fit": "contain",
              "pixelAspect": [1, 1], "colorSpace": "srgb" },
  "frameRate": { "numerator": 30, "denominator": 1 },
  "sources": [{ "id": "motion", "type": "video", "path": "motion.mp4",
                "timing": { "mode": "exact" } }],
  "encodings": [{ "codec": "h264", "preset": "medium",
                  "renditions": [{ "id": "motion.1x", "width": 720,
                                   "height": "auto", "crf": 23 }] }],
  "units": [{ "id": "idle.body", "kind": "body", "source": "motion",
              "range": [0, 30], "playback": "loop", "ports": [] }],
  "initialState": "idle",
  "states": [{ "id": "idle", "bodyUnit": "idle.body" }],
  "edges": [],
  "bindings": []
}
```

Field names that the errors taught, and that the README example does not show:

- `units[].range` is an **array** `[startFrame, endFrame]`, not `{startFrame, endFrame}`
- `units[].kind` must be one of `body | bridge | reversible | one-shot`
- looptitude is `"playback": "loop"` — **not** `"loop": true`
- `states[]` uses `bodyUnit`, not `unit`
- `encodings[].preset` and `renditions[].crf` are **required**, not defaulted
- unknown fields are rejected outright (`units[0] contains unknown field loop`)

Full spec: `docs/project/1.0.md` in the upstream repo.

## Verdict for MIKAY

**Worth having, not yet worth using.** Reasons to keep it:

- It is a *delivery* answer to a question this project has not answered yet: how the
  episode page shows motion without shipping a 20 MB MP4 per episode. A `.avl` bundle is
  per-codec and seekable, and the state machine maps naturally onto "idle → play →
  replay" on a film card.
- Packed alpha means the drawn art could sit on the page's own background, which is what
  the Hallmark *Darkroom* palette wants.

Reasons to wait:

- The console player is one thing; **the compiler needs ffmpeg**, and this repo's render
  pipeline does not currently have one (the Python venv that carried imageio-ffmpeg is
  gone — see the render notes).
- WebCodecs support is required and AVAL refuses to fall back by design, so every place
  it is used needs a real `<video>` fallback written by hand.
- Colour fidelity matters here: the films are graded warm and grainy, and AV1/VP9 at
  `crf 40` (the README's own example) is lossy in exactly the shadows this project lives
  in. Any adoption needs a side-by-side against the MP4.
