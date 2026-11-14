# Web-dev skills installer — copy-paste for a friend's AI

Source: `jusnie/Tools-Skills`, branch `arena/6265089e-animation`, path `.claude/`.
**11 web-development skills + 4 subagents · 2,111 files · 34 MB payload (~39 MB on disk; 2,111 small files) · sparse clone, so you never pull the repo's 162 MB.**

It also wires in the **88-style design catalog** (glassmorphism, brutalism, bento, Y2K, HUD, liquid glass, editorial…) and a **verified scroll/motion toolkit** (Lenis 1.3.27, GSAP 3.15.1, 17 GSAP presets).

Paste the block in **Part A** into your friend's AI (Claude Code, Cursor, or anything with shell access). It asks one question — project-level or user-level — then installs and verifies.

---

## Part A — the prompt (copy everything inside)

````text
You are installing a web-development skill library into this machine. Follow these steps
exactly. Do not modify any file outside .claude/. Do not invent skill content — everything
comes from the repository below.

SOURCE
  repo:   https://github.com/jusnie/Tools-Skills
  branch: arena/6265089e-animation
  paths:  .claude/skills/  and  .claude/agents/

SKILLS TO INSTALL (11)
  design-taste-frontend, impeccable, hallmark, ui-ux-pro-max, modern-web-guidance,
  frontend-checklist, scroll-craft, react-kino, oil-motion, ui-sdk, mapcn

STEP 0 — ask me one question, then wait:
  "Install project-level (./.claude, this repo only) or user-level (~/.claude, every
   project)?" Default to project-level if I don't answer.

STEP 1 — check prerequisites. Report, do not fail silently:
  git --version        (required)
  node --version       (optional; design-taste's finish-gate needs Node 18+)
  python3 --version    (optional; only oil-motion needs Python 3.10+, Pillow, ffmpeg)
If git is missing, stop and tell me to install git. Do not try a manual file-by-file
download of 2,111 files.

STEP 2 — sparse clone into a temp dir, excluding the 96 MB of video skills:
  git clone --depth 1 --filter=blob:none --sparse \
    -b arena/6265089e-animation \
    https://github.com/jusnie/Tools-Skills.git /tmp/tools-skills-install

  cd /tmp/tools-skills-install && git sparse-checkout set --no-cone \
    '/.claude/agents/' \
    '/.claude/skills/design-taste-frontend/' \
    '/.claude/skills/impeccable/' \
    '/.claude/skills/hallmark/' \
    '/.claude/skills/ui-ux-pro-max/' \
    '/.claude/skills/modern-web-guidance/' \
    '/.claude/skills/frontend-checklist/' \
    '/.claude/skills/scroll-craft/' \
    '/.claude/skills/react-kino/' \
    '/.claude/skills/oil-motion/' \
    '/.claude/skills/ui-sdk/' \
    '/.claude/skills/mapcn/'

STEP 3 — copy into the target from Step 0 (create dirs if absent, never overwrite a
skill that already exists without asking):
  mkdir -p <TARGET>/.claude/skills <TARGET>/.claude/agents
  cp -R /tmp/tools-skills-install/.claude/skills/* <TARGET>/.claude/skills/
  cp -R /tmp/tools-skills-install/.claude/agents/* <TARGET>/.claude/agents/

  If your tool reads .agents/skills/ instead of .claude/skills/, copy to that path too.

STEP 4 — verify, and show me the result as a table:
  a) every installed folder contains a SKILL.md
  b) each SKILL.md starts with YAML frontmatter containing `name:` and `description:`
  c) count: expect 11 skill folders and 4 agent .md files
  d) preserve every LICENSE and LICENSE-*.txt file that came with a skill
  e) print total files and total size
If any check fails, say which skill is broken and stop.

STEP 5 — clean up: rm -rf /tmp/tools-skills-install

STEP 6 — report, in this format:
  | Skill | Version | License | Purpose (one line) | Files |
  plus one line: "Invoke with: <how to trigger a skill in my tool>"

STEP 7 — after installing, prove one skill works: open
  <TARGET>/.claude/skills/design-taste-frontend/SKILL.md
Its `description:` is a YAML folded block (the line after `description: >-`), so quote the
first sentence of that text — it begins "tasteskill 2.5.1" — back to me.

STEP 8 — register the two local references you just installed, and use them instead of guessing:

  A) DESIGN STYLES — .claude/skills/ui-ux-pro-max/data/styles.csv
     88 styles: 50 active, 29 supplemental, 9 deprecated. Columns that matter:
     Style Category, Status, Keywords, Best For, Do Not Use For, Effects & Animation,
     Accessibility, Performance, Implementation Checklist, CSS/Technical Keywords.
     When I name a style (glassmorphism, brutalism, bento, Y2K, HUD, liquid glass,
     editorial, claymorphism, kinetic typography, etc.), grep this CSV first and follow
     its CSS/Technical Keywords and Implementation Checklist verbatim. Never invent a
     style's rules. Skip anything whose Status is deprecated.

  B) MOTION PRESETS — .claude/skills/ui-ux-pro-max/data/motion.csv
     17 presets (hover, scroll reveal, stagger, page transition, parallax, loading,
     carousel), each with Trigger / Duration / Easing / GSAP Snippet / Do / Don't.
     Use its snippet and timings for reveals and transitions instead of inventing them.

  C) Where each skill wins: design-taste-frontend = the anti-slop floor and finish gate;
     ui-ux-pro-max = the style/palette/typography/motion data; hallmark = avoid model
     defaults; scroll-craft = full scroll-driven landing pages; modern-web-guidance =
     platform API correctness; frontend-checklist = the audit pass.

MOTION DEPENDENCY POLICY
  - Ask me before adding any scroll or animation package, and state the exact version.
    Verified latest as of 2026-11-14: lenis 1.3.27, gsap 3.15.1, @gsap/react 2.1.2,
    motion 14.14.0, split-type 0.3.4, animejs 4.5.0, embla-carousel-react 8.6.0,
    swiper 14.4.0, @barba/core 2.10.3, swup 4.10.0, locomotive-scroll 5.1.1,
    rellax 1.12.1, atropos 2.0.2, three 0.187.0, @react-three/fiber 9.8.2,
    tailwindcss 4.3.5.
  - Never install @studio-freight/lenis — deprecated and renamed; the package is `lenis`.
  - Never run two smooth-scroll engines at once (Lenis + locomotive-scroll, or Lenis +
    CSS `scroll-behavior: smooth`). Pick one.
  - Lenis honors prefers-reduced-motion by default (respectReducedMotion defaults to
    true). Do not set it to false.

RULES
  - These skills are third-party MIT / Apache-2.0 works. Keep their LICENSE files and do
    not strip attribution. Do not relicense them as your own.
  - design-taste-frontend declares a Stop hook that shells out to scripts/gate.mjs. Only
    enable it if Node 18+ is present; otherwise tell me the hook is disabled.
  - Do not run any skill's install script, npm install, or pip install without asking.
  - Do not delete or rewrite anything in <TARGET> outside .claude/.
  - If the clone or sparse-checkout fails twice, stop and report the exact error.

````

---

## Part B — what gets installed

### Core design & build — install all six

| Skill | Version | License | What it does | Files / size |
|---|---|---|---|---|
| **design-taste-frontend** | tasteskill 2.5.1 | MIT | "The anti-slop frontend skill." Builds sites at figma.com / x.ai level: one system, plain copy in its own voice, one section per screen, real photography, a hero entrance and one or two dealt moments — with a checker that enforces it in a real browser | 1,566 / 24 MB |
| **impeccable** | 4.9.0 | Apache-2.0 | Design-director skill with 44 playbooks: `shape`, `audit`, `critique`, `polish`, `typeset`, `layout`, `colorize`, `harden`, `optimize`, `animate`, `bolder`, `quieter`, `distill` | 59 / 2.2 MB |
| **ui-ux-pro-max** | — | MIT | Searchable local design data: 79 styles, 192 product palettes, 74 font pairings, 119 UX guidelines, 105 icons, 17 GSAP presets, 25 chart types, 22 stacks | 71 / 3.5 MB |
| **hallmark** | 2.0.0 | MIT | "Designed, not generated": a hard floor against model defaults, a dealt direction so consecutive builds don't converge. Modes: build, `redesign <path>`, `audit <path>` | 137 / 1.7 MB |
| **modern-web-guidance** | GoogleChrome | Apache-2.0 | Modern platform best practices: dialogs, popovers, container queries, view transitions, scroll-driven animations, CWV, image optimization, forms, accessibility. Pinned by hash in `skills-lock.json` | 211 / 1.9 MB |
| **frontend-checklist** | frontendchecklist.io | MIT | The 386-rule Front-End Checklist corpus as an evidence-first audit checklist (offline-readable; the MCP server it assumes is optional) | 3 / 22 KB |

### Motion & scroll — install if the site needs motion

| Skill | License | What it does | Files / size |
|---|---|---|---|
| **scroll-craft** | MIT | Premium scroll-driven landing pages: visitor journey, page grammar, emotional peak, layered hero with independent planes, separate mobile composition | 20 / 303 KB |
| **react-kino** | MIT | Portable React scroll stories via `react-kino/story` + `studio` storyboard editor, validated with `kino validate` / `kino doctor` | 2 / 3 KB |
| **oil-motion** | MIT | Turns AI-generated video / sequence frames into scroll-, pointer-, drag- or audio-driven web animation. Needs Python 3.10+, Pillow, ffmpeg | 24 / 247 KB |

### Component-level — only if the friend's stack matches

| Skill | License | What it does | Files / size |
|---|---|---|---|
| **ui-sdk** | Apache-2.0 (vercel-labs) | Unstyled accessible UI behaviors — keyboard, focus, selection, dismiss, popups, DnD, ARIA — for React/Vue/Svelte/Solid/web components, with `createAgent` + WebMCP agent tools | 9 / 86 KB |
| **mapcn** | MIT | shadcn-style map components on MapLibre GL + Tailwind: markers, popups, routes, arcs, GeoJSON, choropleth, clusters, globe, light/dark theming | 5 / 23 KB |

### Subagents (`.claude/agents/`) — 4 files, 34 KB

`impeccable-asset-producer` · `impeccable-documenter` · `impeccable-finish-reviewer` · `impeccable-manual-edit-applier`

### Deliberately excluded

| Excluded | Why |
|---|---|
| `directing-stickman-videos` (60 MB) | Video/film pipeline, not web |
| `papercut-*` ×9 | Explainer-video production |
| `auto-ontology-mcp` (456 KB) | MCP server, not UI |
| `affine` | Its own SKILL.md says it's "a reference note, not a component library" |

Excluding these is what keeps the install at a 34 MB payload instead of 96 MB.

---

## Part C — Design styles (the "glassmorphism etc" list)

Nothing to install — this already ships as **data** inside `ui-ux-pro-max`, so the AI greps it instead of recalling it:

`.claude/skills/ui-ux-pro-max/data/styles.csv` — **88 styles · 50 active · 29 supplemental · 9 deprecated**

Each row carries `Keywords`, `Primary/Secondary Colors`, `Effects & Animation`, `Best For`, `Do Not Use For`, `Light Mode ✓`, `Dark Mode ✓`, `Performance`, `Accessibility`, `Mobile-Friendly`, `Conversion-Focused`, `Framework Compatibility`, `Era/Origin`, `Complexity`, `CSS/Technical Keywords`, `Implementation Checklist`, `Design System Variables`.

### Query it offline

```bash
# one style with all its rules
grep -i "glassmorph" .claude/skills/ui-ux-pro-max/data/styles.csv

# the active shortlist
python3 -c "
import csv
for r in csv.DictReader(open('.claude/skills/ui-ux-pro-max/data/styles.csv')):
    if r['Status']=='active': print(r['Style Category'])
"
```

### The 50 active styles, grouped by intent

| Intent | Styles |
|---|---|
| **Neutral / product UI** | Minimalism & Swiss Style · Flat Design · Bento Box Grid · Dimensional Layering · Exaggerated Minimalism · Editorial Grid / Magazine · Dark Mode (OLED) |
| **Material & depth** | Glassmorphism · Liquid Glass · Neumorphism · Soft UI Evolution · Claymorphism · Skeuomorphism · Tactile Digital / Deformable UI · E-Ink / Paper · 3D & Hyperrealism · 3D Product Preview |
| **Bold / anti-design** | Brutalism · Neubrutalism · Vibrant & Block-based · Gen Z Chaos / Maximalism · Anti-Polish / Raw Aesthetic · Memphis Design · Bauhaus |
| **Retro & nostalgia** | Retro-Futurism · Y2K Aesthetic · Vintage Analog / Retro Film · Pixel Art |
| **Tech & sci-fi** | Cyberpunk UI · HUD / Sci-Fi FUI · Aurora UI · AI-Native UI · Spatial UI (VisionOS) · Interactive Cursor Design |
| **Calm & organic** | Organic Biophilic · Biomimetic / Organic 2.0 · Nature Distilled · Accessible & Ethical · Inclusive Design |
| **Motion-led** | Motion-Driven · Micro-interactions · Kinetic Typography · Parallax Storytelling |
| **Data & dashboards** | Data-Dense Dashboard (+ 9 supplemental dashboard variants) |
| **Off-the-shelf systems** | Fluent 2 · Shopify Polaris · Adobe Spectrum · Material 3 Expressive (Mobile) |
| **Interface-less** | Zero Interface · Voice-First Multimodal |

### The 29 supplemental — real but narrow

Mostly mobile variants, dashboard archetypes and niche eras: Vaporwave · Swiss Modernism 2.0 · Minimalist Monochrome · Modern Dark (Cinema Mobile) · Terminal CLI (Mobile) · Gradient Mesh / Aurora Evolved · Chromatic Aberration / RGB Split · Academia (Scholarly Mobile) · Sketch Hand-Drawn (Mobile) · Bold Typography (Mobile Poster) · Kinetic Brutalism (Mobile) · Cyberpunk Mobile HUD · Neo Brutalism (Mobile) · Flat Design Mobile (Touch-First) · Claymorphism (Mobile) · Neumorphism (Mobile) · SaaS Mobile (High-Tech Boutique) · Enterprise SaaS (Mobile) · Bitcoin DeFi (Mobile) · Spectrum 2 · Heat Map · Executive Dashboard · Real-Time Monitoring · Drill-Down Analytics · Comparative Analysis Dashboard · Predictive Analytics · User Behavior Analytics · Financial Dashboard · Sales Intelligence Dashboard

### The 9 deprecated — don't build these

`Hero-Centric Design` · `Conversion-Optimized` · `Feature-Rich Showcase` · `Minimal & Direct` · `Social Proof-Focused` · `Interactive Product Demo` · `Trust & Authority` · `Storytelling-Driven` · `Bento Grids (Legacy)`

The portfolio I audited earlier is squarely **Hero-Centric Design** — the style this dataset itself retired. That's the file talking, not me.

### Worked example — glassmorphism, verbatim from the CSV

**CSS keywords:** `backdrop-filter: blur(15px)` · `background: rgba(255,255,255,.15)` · `border: 1px solid rgba(255,255,255,.2)` · `-webkit-backdrop-filter: blur(15px)` · z-index layering for depth

**Checklist:** ☐ blur 10–20px ☐ translucent white 15–30% ☐ 1px light border ☐ vibrant background verified ☐ text contrast 4.5:1

**Acceptance:** `accessibility: risk:conditional | requires: contrast-text-4.5, keyboard, visible-focus, reduced-motion` · `performance: cost:low`

The gotcha that checklist implies: **glass over a flat background is invisible** — it needs colour behind it, and it needs a fallback when `backdrop-filter` is unsupported.

```css
.glass{
  background: rgba(255,255,255,.15);
  border: 1px solid rgba(255,255,255,.2);
  -webkit-backdrop-filter: blur(15px);
  backdrop-filter: blur(15px);
}
@supports not (backdrop-filter: blur(1px)){
  .glass{ background: rgba(20,24,36,.92) }  /* opaque fallback holds 4.5:1 */
}
```

---

## Part D — Scroll & motion toolkit (Lenis etc.)

Full scroll-page work comes from three places: the **scroll-craft** skill (journey, page grammar, layered hero), **react-kino** (React scroll stories), and the packages below. Versions checked against `registry.npmjs.org` on **2026-11-14**.

| Package | Latest | Use it for |
|---|---|---|
| **lenis** | 1.3.27 | Smooth scroll that preserves native scroll semantics |
| **gsap** | 3.15.1 | Timelines + ScrollTrigger |
| **@gsap/react** | 2.1.2 | `useGSAP()` with proper cleanup |
| **motion** | 14.14.0 | React springs + layout animation (Framer Motion successor) |
| **split-type** | 0.3.4 | Split text/lines/chars for reveals |
| **animejs** | 4.5.0 | Small standalone timeline, no framework |
| **embla-carousel-react** | 8.6.0 | Carousels that don't fight scroll |
| **swiper** | 14.4.0 | Full-featured slider |
| **@barba/core** | 2.10.3 | Page transitions (multi-page) |
| **swup** | 4.10.0 | Lighter MPA page transitions |
| **locomotive-scroll** | 5.1.1 | Alternative smooth scroll — don't mix with Lenis |
| **rellax** | 1.12.1 | Tiny parallax |
| **atropos** | 2.0.2 | 3D tilt cards |
| **three** / **@react-three/fiber** | 0.187.0 / 9.8.2 | WebGL scenes |
| **tailwindcss** | 4.3.5 | Styling |

⚠️ **`@studio-freight/lenis` is deprecated** (last version 1.0.42) — renamed to **`lenis`**. Most tutorials still tell you to install the old name.

### Lenis — quickstart verified from the 1.3.27 tarball

```bash
npm i lenis
```
```js
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'          // ships in the package

const lenis = new Lenis()              // respectReducedMotion defaults to true
function raf(time){ lenis.raf(time); requestAnimationFrame(raf) }
requestAnimationFrame(raf)
```

React: `import { ReactLenis } from 'lenis/react'`. Package exports: `.` · `./react` · `./snap` · `./vue` · `./nuxt`.

**GSAP ScrollTrigger sync** — the documented three lines:
```js
lenis.on('scroll', ScrollTrigger.update)
gsap.ticker.add((time) => { lenis.raf(time * 1000) })   // seconds → ms
gsap.ticker.lagSmoothing(0)
```

**Reduced motion is already handled.** Lenis forces `lerp` to 1, makes `scrollTo`/anchor jumps instant, and reacts live without a reload; read `lenis.prefersReducedMotion` to adapt your own animations. Opting out via `respectReducedMotion: false` is not recommended.

**Native behaviour survives** — Lenis wraps the browser's own scroll, so `position: sticky` and anchor links keep working. Put `data-lenis-prevent` on modals and nested scroll areas. Never also set `scroll-behavior: smooth` in CSS; the two fight.

### Scroll-page recipes → `motion.csv`

17 presets with real GSAP snippets: **hover micro-interaction ×3 · scroll reveal ×3 · stagger list ×3 · page transition ×3 · parallax ×2 · loading/skeleton ×2 · carousel ×1**. Every row gives Trigger / Duration / Easing / Snippet / Do / Don't — use those timings instead of inventing "0.3s ease-in-out" and hoping.

For a whole cinematic landing page, **scroll-craft** plans the journey and builds the layered hero; Lenis is the engine underneath it.

---

## Part E — notes

- **Scope.** Project-level (`./.claude`) keeps it per-repo; user-level (`~/.claude`) makes every project see it. Claude Code reads both; `.agents/skills/` is the alternative path some tools use.
- **No `node_modules`, no build step.** Skills are Markdown + static assets + two `.mjs` checkers. Nothing to compile.
- **The gate is the good part.** `design-taste-frontend/scripts/gate.mjs` is a real browser checker — it's what turns "looks generic" into a pass/fail. Node 18+ to use it.
- **Licenses travel with the files.** MIT for design-taste, hallmark, ui-ux-pro-max, frontend-checklist, scroll-craft, react-kino, oil-motion, mapcn; Apache-2.0 for impeccable, modern-web-guidance, ui-sdk. Keep the `LICENSE*` files when redistributing — the installer instructs the AI to preserve them.
- **Verified 2026-11-14:** npm versions from `registry.npmjs.org`; Lenis API/CSS/exports read from the `lenis-1.3.27.tgz` tarball; the style catalog read from `styles.csv` (88 rows, catalog verified 2026-08-13).
- **Runtime:** 34 MB payload / ~39 MB on disk · 2,111 files · sparse clone of one branch. First clone pulls only those paths (`--filter=blob:none --sparse`), not the repo's 162 MB of renders.
