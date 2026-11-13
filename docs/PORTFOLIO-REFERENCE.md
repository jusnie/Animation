# Portfolio site: what to build with, and what to read

Reference research for the MIKAY episode/portfolio site. Nothing here is a page — this
file exists so an agent (or a person) can pick up the work without re-browsing GitHub.

Written 2026-11-13 against `site/` as it stands: Next 16 + React 19 + Tailwind 4 +
shadcn config, plus Opus, Astryx and BlockSuite installed. Four design skills and one
anti-slop gate are in `.claude/skills/`.

---

## 1. The decision, up front

**Do not start from a portfolio template.** The high-star ones are all the same card
grid with a hero and an about section; this project is a film series and the page has to
look like the films. The installed stack already beats every template in the search
results.

**Do install the motion and video layer**, because that is the actual gap:

| Package | Version installed | Licence | What it is for |
|---|---|---|---|
| `motion` | 14.14.0 | MIT | Framer Motion, standalone. `whileInView`, layout animation, springs, `useScroll` |
| `lenis` | 1.3.27 | MIT | Smooth scroll. The difference between an intentional page and a janky one |
| `media-chrome` | 4.19.5 | MIT | Web-component video player with seek, PiP and captions — not a bare `<video>` |
| `@pixel-point/aval-react` | 1.0.2 | MIT | AVAL: interactive video with a state machine, codec ladder and packed alpha. See `docs/aval.md` |

All three are installed in `site/` and verified to bundle together (855 KB esbuild
bundle, no errors). Import paths:

```tsx
import { motion, AnimatePresence, useScroll, useSpring } from "motion/react";
import Lenis from "lenis";
import "lenis/dist/lenis.css";      // required, not optional
import "media-chrome";               // registers <media-controller> and friends
```

---

## 2. Repositories worth reading (do not copy wholesale)

Browse these for structure and technique. None of them is the page we want, and none of
them knows about Mikay.

| Repo | ★ | Licence | Read it for |
|---|---|---|---|
| `RyanFitzgerald/devportfolio` | 5.0k | MIT | The best-maintained minimalist portfolio. Astro + Tailwind. Layout logic and type scale, not code |
| `vercel/nextjs-portfolio-starter` | 729 | none declared | Markdown-driven episodes. The right *shape* for us — treat as read-only reference |
| `adrianhajdin/award-winning-website` | 1.1k | (check) | The only high-star repo that teaches award-style scroll motion (GSAP + scroll triggers) |
| `muxinc/media-chrome` | 2.8k | MIT | Its own docs are the best guide to a custom video skin |
| `darkroomengineering/lenis` | 17.2k | MIT | Docs for integrating smooth scroll without breaking anchors or focus |
| **Tailark "Dusk"** (site, not a repo) | — | free tier + paid | Dark marketing blocks on shadcn. Visual reference for spacing and restraint; the free registry items are installable one at a time. See `docs/tailark/` |

Supporting, only if a 3D scene is ever actually wanted: `pmndrs/react-three-fiber`
(33.7k, MIT) and `pmndrs/drei` (10.2k, MIT). For a hand-drawn stick-figure series, 3D is
the wrong instinct — noted so nobody rediscovers it.

### Skip these, with reasons

- `academicpages/academicpages.github.io` (17.8k) — an academic CV, wrong genre
- `hashirshoaeb/home`, `shubh73/devfolio`, `judygab/nextjs-portfolio`,
  `harshgoel05/another-portfolio`, `taqui-786/Portfolio` — interchangeable card grids
- `Naresh-Khatri/3d-portfolio` (1.3k) and the 3D-portfolio glut — keyboard gimmicks;
  impressive in a demo, hostile to a story
- every "Netflix clone" result (all under 40★) — student work
- `videojs/video.js` (40.2k) — heavyweight, `NOASSERTION` licence, and it wants to own
  the whole page; `media-chrome` is lighter and MIT

---

## 3. What the installed skills already say

Before writing a page, these are already in the repo and cheap to run. They disagree
productively — run them, do not just pick one.

```
.claude/skills/ui-ux-pro-max        python3 .../scripts/search.py "<product> <keywords>" --design-system
.claude/skills/design-taste-frontend node .../scripts/start.mjs deal --page <kind>
                                     node .../scripts/theme.mjs  (Hallmark's dealer)
.claude/skills/hallmark             node .../scripts/sloplint.mjs site/src   ← hard floor
.claude/skills/impeccable           npx impeccable detect site/src           ← 62-rule scan
.claude/skills/modern-web-guidance  npx -y modern-web-guidance@latest search "scrollytelling"
```

Their recommendations for this project, already on record in `site/README.md`:

- **UI/UX Pro Max** → Scroll-Triggered Storytelling + Motion-Driven; pure black canvas,
  `#FAFAFA` ink, `#0C0C0C` cards, one high-contrast CTA accent
- **Hallmark** → *Darkroom* — warm print-black ground, fine grain, fibre-white ink,
  hairline condensed capitals, one amber safelight. This is the same 35 mm look already
  ported into `tools/vfx.py`, so the page and the films can share a palette
- **Hallmark's floor** — every colour through a token, no `transition: all`, no invented
  metrics, no uppercase tracked eyebrows, no purple-to-blue gradients

That last point matters most: the films are grainy, warm and hand-made. A page with a
purple gradient hero would be lying about what the project is.

---

## 4. Structure that fits the project

Derived from what already exists in this repo, not from a template:

```
/                 the film. one screen: title, the day0 still, play
/episodes         list, driven by render/*.mp4 + story/*.md
/episodes/[slug]  player + narration text + captions + credits
/about            Mikay, the style, the tools (honest: drawn, not AI-generate-and-hope)
/colophon         what made it: Python, PIL, ffmpeg, the VFX port, the skills
```

Ground rules the rest of this repo already implies:

- **The episodes are markdown and MP4s, not CMS rows.** `story/` and `render/` are the
  source of truth; the site reads them at build time.
- **No background music on the page.** The films have none by request; an autoplaying
  bed would undo that.
- **No zoom effects.** Same standing instruction as the films.
- **Captions belong to the player**, not to the page: the films ship `.srt` files in
  `render/`, so serve those as WebVTT rather than re-typesetting the text.
- **`prefers-reduced-motion` is not optional** — Lenis and Motion both need an off switch,
  and the Hallmark floor requires it.

---

## 5. Pitfalls found while doing this research

- **Lenis needs its CSS.** `lenis/dist/lenis.css` is required; without it the smooth
  scroll silently does nothing visible and `data-lenis-prevent` regions misbehave.
- **`motion` is the new package name.** The old `framer-motion` import path still
  resolves in some versions but `motion/react` is the current one.
- **`media-chrome` is a custom element**, so it must be imported in a client component
  (`"use client"`) and referenced as `<media-controller>` / `<media-play-button>` —
  React 19 handles custom elements without the old `ref` workarounds.
- **Icon naming**: `doticons` exports are all `*Doticon` (`AlarmDoticon`,
  `CirclePlayDoticon`), never bare names.
- **`site/node_modules` is 1.8 GB** and not committed. After a sandbox reset,
  `cd site && npm install` takes about a minute. This was verified twice.
- **Astryx currently breaks on `three`-less imports and uses `<Theme>`, not
  `<ThemeProvider>`; Opus requires `three` as a peer.** Both are documented in
  `site/README.md`; do not re-derive those errors.

---

## 6. Status

- Installed: `motion@14.14.0`, `lenis@1.3.27`, `media-chrome@4.19.5` — MIT, in `site/`.
- **No page has been built.** The instruction is install-and-reference only, and this
  file is the reference.
- Nothing from the template repos has been copied into this repo. They are MIT or
  reference-only, and none of them is the design.
