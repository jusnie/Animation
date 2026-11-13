# Scroll choreography: scroll-craft, oil-motion, react-kino

Three things the user pointed at, installed on 2026-11-10. They are not competitors — they
sit at three different levels, and which one you reach for depends on whether you want
**rules**, **footage**, or **React components**.

| | scroll-craft | oil-motion | react-kino |
|---|---|---|---|
| Kind | agent skill + own engine | agent skill + Python pipeline | npm React library + skill |
| ★ | 5,034 | 2,898 | 221 |
| Licence | MIT | MIT | MIT |
| Gives you | the grammar of a scroll page | scroll-scrubbed video you generated | Story/Scene components + editor |
| Needs | node; ffmpeg + Chrome only for verification | Python 3.10+, Pillow, **ffmpeg/ffprobe**, optional ZenMux key | React 18+ |
| Works here today | **yes** (engine + SKILL readable; verification tools degraded) | **partly** — no ffmpeg, so no compile | **yes**, verified |

---

## 1. scroll-craft — installed as a skill, and it is the most valuable of the three

`.claude/skills/scroll-craft/` (348 KB, 20 files): SKILL.md (25 KB), its own runtime
(`scrollcraft.js` 62 KB + `scrollcraft.css` 20 KB), seven references, seven node scripts.

This is the answer to "how does Abigail/Bokoko actually work" without forking anyone's
repo. The SKILL.md is a **page grammar**: visitor journey → page grammar → emotional peak →
one bespoke signature move; dimensional heroes with independent planes; restrained motion;
a separate mobile composition; and a verification pass that screenshots desktop, mobile and
reduced-motion states. Upstream sells nothing and requires no account.

The engine is declarative, not a framework — behaviour lives in `data-sc-*` attributes
(28 of them), which means it can be dropped onto plain HTML or Next.js with no build step:

```
data-sc-parallax   data-sc-pan      data-sc-drift   data-sc-magnet
data-sc-reveal     data-sc-rise     data-sc-lerp    data-sc-kinetic
data-sc-cue        data-sc-dwell    data-sc-linger  data-sc-in
data-sc-count      data-sc-count-at data-sc-mode    data-sc-clip-map
data-sc-progress   data-sc-poster   data-sc-act     data-sc-copy
```

Scripts: `doctor.mjs` (preflight), `workspace.mjs --ensure`, `serve.mjs --root`,
`shoot.mjs` (playwright screenshot pass), `encode.sh`, `kie.mjs` (image/video generation),
`worldflight-assert.mjs` (the "3D scroll world" assertion), plus `templates/FINGERPRINTS.md`.

**Preflight, run here:** node ok → **ffmpeg FAIL** (needs a full build with scale/fps/psnr +
webp muxer) · playwright-core warn · Chrome warn · `KIE_AI_API_KEY` unset (only needed to
*generate* imagery — building from your own photos needs no key and no spend).

That is the same wall as the film pipeline: **no ffmpeg in this sandbox.** Everything
before the encode/screenshot step is readable and usable; the last mile is not.

Not copied: `EXAMPLES.md` (37 KB of worked examples) and `plugins/…/media/` — read the
examples on GitHub rather than in the tree.

## 2. oil-motion — the video-scrub pipeline, and why it is relevant *here* specifically

`.claude/skills/oil-motion/` (297 KB): SKILL.md + `README.en.md`, 16 Python scripts, 4
TypeScript/render assets.

This one is unusual because it does the exact thing this project does — **make frames,
then make motion from frames** — and then hands the result to a web runtime driven by
scroll, pointer, drag, touch, device orientation, audio or data. Its own scope note says it
is *not* for plain CSS/JS/SVG/Lottie/realtime-3D transitions, and *not* for standalone film
editing.

Where it would actually earn its place: if an episode's **animated** shot should be
scrubbed by scroll instead of played on a timer — turn Mikay's frames into a sprite atlas
or video, then bind it to scroll position. `motion_budget.py` even enforces a cost ceiling.

Scripts worth knowing: `compile_scroll_video.py` (the timeline compiler),
`compose_travel_frames.py`, `composite_alpha_keyframe.py`, `chroma_key.py`,
`loop_cleanup.py` (loop seam repair), `optimize_motion.py`, `media_edges.py`,
`production_gate.py`, `motion_budget.py`; plus `assets/interactive-motion.ts`,
`assets/chroma-video-renderer.ts`, `assets/step-gesture.ts` and
`assets/motion-manifest.example.json`.

Python requirements: `Pillow`, `numpy`, `PyYAML`. All 16 scripts pass `py_compile`.
The pipeline itself needs **ffmpeg and ffprobe**, which this sandbox does not have — so,
like AVAL, it is installed and inspectable but cannot produce output here. Note the SKILL
text and README are in Chinese; `README.en.md` is the English one.

## 3. react-kino — the only one of the three that is a real npm library

`site/` now has `react-kino@0.6.0` + `@react-kino/core@0.4.0` (MIT; React/ReactDOM 18+
peers; core has no runtime dependencies).

It is the most *productised* take on the same idea: a **portable document format** for
scroll stories, rendered by React, plus a local visual editor. Verified with esbuild —
`Story` + `Storyboard` + a recipe compile to 136 KB, **0 errors**.

```tsx
import { Story } from "react-kino/story";
import { Storyboard } from "react-kino/studio";
import { createStoryRecipe } from "react-kino/recipes";
import { createRecipeComponents } from "react-kino/recipe-kit";

const doc = createStoryRecipe("editorial");
<Story document={doc} components={createRecipeComponents()} />
```

**Six recipes:** `launch · editorial · case-study · comparison · gallery · portfolio`.
The `portfolio` and `editorial` ones map directly onto what is wanted here; `comparison`
needs `Before`/`After` registrations.

Two design decisions that matter more than the API:

- **The Storyboard editor is not in the runtime entrypoints.** You author in a separate
  route (`react-kino/studio`), export a JSON document, and the page renders data only.
  Documents cannot round-trip JSX — imports are validated and capped at 2 MB. That is a
  genuinely safe design compared to "our editor emits code".
- **Below 640 px and under `prefers-reduced-motion`, a story becomes a natural reading
  layout** with all layers visible. That is the right fallback and it is the one thing
  hand-rolled GSAP scroll sites almost always get wrong.

Also present: `react-kino/` package ships its own skill (`skills/kino/SKILL.md`), committed
here as `.claude/skills/react-kino/` — it says to validate with `kino validate file --json`
and inspect with `kino doctor file --components …`, and explicitly warns that doctor is
document inspection, not a browser test.

**One trap:** `react-kino/document` does **not** export `Document`. Build fails with
`No matching export in dist/document.mjs`. The real runtime names are from the root entry:
`Story`, `Scene`, `useKino`, `useScrollProgress`, `ScrollTransform`, `TextReveal`,
`HorizontalScroll`, `Parallax`, `Marquee`, `StickyHeader`, `VideoScroll`, `Progress`,
`Reveal`, `Counter`, `Panel`, `CompareSlider`.

---

## How these relate to what is already installed

- **Hallmark** decides whether a page is any good; **scroll-craft** supplies the scroll
  grammar; **react-kino** supplies the components and the document format; **Emil
  Kowalski's primitives** and **motion 14** handle the micro-interaction level.
- **oil-motion** overlaps `tools/build_video.py` and AVAL: all three put frames on screen
  from a timeline. Difference — `build_video.py` renders a **film** (fixed duration, audio,
  burned captions), AVAL plays **interactive video** (state machine, per-codec), oil-motion
  makes **scroll-scrubbed** motion (position is the time axis). Three different clocks.
- Nothing here changes the film. This is the site layer only.

## Verdict

**scroll-craft is the one to read first** — it is the closest thing to the Abigail/Bokoko
technique written down as rules instead of code. `react-kino` is the one to reach for when
a page actually gets built, because the document/editor split keeps content out of JSX and
the reduced-motion fallback is free. `oil-motion` is worth keeping for the day a shot needs
to be scrubbed by scroll rather than played — but it cannot run until ffmpeg exists,
exactly like AVAL.
