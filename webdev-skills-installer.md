# Web-dev skills installer — copy-paste for a friend's AI

Source: `jusnie/Tools-Skills`, branch `arena/6265089e-animation`, path `.claude/`.
**11 web-development skills + 4 subagents · 2,111 files · 34 MB payload (~39 MB on disk; 2,111 small files) · sparse clone, so you never pull the repo's 162 MB.**

It also wires in the **88-style design catalog** (glassmorphism, brutalism, bento, Y2K, HUD, liquid glass, editorial…), a **verified scroll/motion toolkit** (Lenis 1.3.27, GSAP 3.15.1, 17 presets), **SVG + font sources** (1,934 families, 74 pairings, 1,617 icons), **design reference sites**, and a **senior frontend guide subagent** that asks what you want before it changes anything — plus **auto-browsing of GitHub and the web**, so it brings you options instead of guessing.

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

STEP 9 — install the guide subagent. Write this file verbatim to
  <TARGET>/.claude/agents/senior-frontend-guide.md
Its full text is in Part H of the document I gave you. Do not paraphrase it. This agent is
what enforces "ask before changing anything": it interviews, reads, plans, and refuses to
edit until approved.

STEP 10 — ask me before touching CLAUDE.md (it lives outside .claude/). If I agree, append
the CHANGE-FREEZE PROTOCOL block from Part H to it so the rules apply to every task, not
only when the subagent is invoked.

STEP 11 — research and present options before you build. Do not design from memory.
  a) If you have web/browser tools: browse, using the query patterns in Part I.
  b) If you have a shell with `gh` authenticated: use the GitHub commands in Part I.
  c) If you have neither: say so plainly, fall back to the local catalogs, and ask me for
     links or screenshots. Never cite a reference you did not actually open.
  Then give me 2-3 directions with tradeoffs and WAIT for my pick. Aesthetic decisions
  are mine; you supply the evidence.
  Vet every repo before recommending it: license, archived, last push, open issues, deps,
  accessibility. Never recommend something you have not opened.

RULES
  - These skills are third-party MIT / Apache-2.0 works. Keep their LICENSE files and do
    not strip attribution. Do not relicense them as your own.
  - design-taste-frontend declares a Stop hook that shells out to scripts/gate.mjs. Only
    enable it if Node 18+ is present; otherwise tell me the hook is disabled.
  - Do not run any skill's install script, npm install, or pip install without asking.
  - Do not delete or rewrite anything in <TARGET> outside .claude/.
  - If the clone or sparse-checkout fails twice, stop and report the exact error.
  - Do not edit any project file before I approve a written plan. Review-only means zero
    changes. If I say "just fix it", scope it to the files I named and nothing else.

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

## Part E — SVG & icons

Two layers: the curated data you already installed, and the packages you install per project.

### Already local (nothing to install)

| File | Rows | What's inside |
|---|---|---|
| `ui-ux-pro-max/data/icons.csv` | 105 | Curated icons with `Icon Name`, `Library`, **`Import Code`**, `Usage`, `Best For`, `Style` |
| `ui-ux-pro-max/data/phosphor-icons-upstream.json` | 1,512 | Full Phosphor set, for lookup |

`Import Code` is the useful column — a real row reads:

```text
arrow-left   Phosphor   import { ArrowLeft } from '@phosphor-icons/react'   Back button breadcrumb navigation
```

The AI reads a copy-ready import instead of guessing a component name.

### Icon libraries — versions verified 2026-11-14

| Package | Latest | Notes |
|---|---|---|
| **lucide-react** | 1.73.0 | shadcn/ui default; 24×24 stroke, `currentColor` |
| **@phosphor-icons/react** | 2.1.10 | Six weights per icon — the set `icons.csv` indexes |
| **@heroicons/react** | 2.2.0 | Tailwind team; outline + solid |
| **@tabler/icons-react** | 3.52.0 | ~5,000 icons, very consistent stroke |
| **iconoir-react** | 7.12.2 | Rounded, distinctive |
| **simple-icons** | 16.37.0 | Brand/logo marks only |

### The SVG pipeline

| Package | Latest | Use |
|---|---|---|
| **svgo** | 4.1.0 | Strip metadata and whitespace from exports — commonly 40–60% smaller |
| **@svgr/cli** | 8.1.0 | SVG → React component with props |

**Sprite technique:** for site chrome, one inline `<symbol>` set plus `<use href="#id">` beats twenty separate requests. (The portfolio I audited already does this correctly for its six service icons.)

### Animated vector

| Package | Latest | Use |
|---|---|---|
| **lottie-web** | 5.13.0 | After Effects → JSON, renders to canvas/SVG |
| **@lottiefiles/dotlottie-web** | 0.83.2 | Lighter Lottie player (WASM) |
| **@rive-app/react-canvas** | 4.39.0 | Interactive state-machine animation |

### Rules
- If `icons.csv` or a library has the icon, don't hand-draw a 40-line path.
- `stroke="currentColor"` / `fill="currentColor"` so icons inherit the theme.
- Decorative icons: `aria-hidden="true"` **and no `aria-label`** — a labelled icon sitting beside a heading is announced twice.
- Ship a `viewBox`; never fixed `width`/`height` only.
- No `filter: drop-shadow()` on an SVG that animates — it re-rasterizes every frame.

---

## Part F — Fonts & typography

### Already local (nothing to install)

| File | Rows | Columns that matter |
|---|---|---|
| `data/google-fonts.csv` | **1,934** families | Family · Category · Stroke · Classifications · Keywords · Styles · **Variable Axes** · Subsets · Designers |
| `data/typography.csv` | **74** pairings | Pairing Name · Category · Heading · Body · Mood · Best For · **Google Fonts URL** · **CSS Import** |
| `data/google-font-licenses.json` | — | Per-family license, so you can check redistribution |
| `data/ux-guidelines.csv` | **119** | The UX rule corpus |

Real pairings from the file: *Classic Elegant* (Playfair Display + Inter) · *Modern Professional* (Poppins + Open Sans) · *Tech Startup* (Space Grotesk + DM Sans).

### Self-hosting beats the Google CDN

| Package | Latest | Notes |
|---|---|---|
| **@fontsource-variable/inter** | 5.3.0 | One variable file, all weights |
| **@fontsource/inter** | 5.3.0 | Static weights for older fallback |
| **geist** | 1.9.2 | Vercel's family, ships `geist/font` |
| Next.js | built-in | `next/font` self-hosts, preloads, and prevents CLS for free |

### Rules
- **Two families maximum** — one display, one text. Orbitron + JetBrains Mono + cyan glow is the single most generated combination of the last two years.
- **Variable over static**: one 30–60 KB file replaces four weight files.
- `font-display: swap`, and preload only the face used above the fold.
- Subset to `latin` unless the copy needs otherwise.
- A render-blocking `<link>` to `fonts.googleapis.com` costs a cross-origin round trip before first paint. Self-host or accept it knowingly.
- Icon fonts are not icons — use SVG.

---

## Part G — Where to get design reference

Research **before** building. Take the idea, never the markup.

| Site | Best for |
|---|---|
| **Awwwards** | Award-winning sites: motion, craft, interaction detail |
| **Godly** | Curated high-craft web design |
| **Land-book** | Landing-page gallery, filterable by style and industry |
| **SiteInspire** | Editorially curated web design |
| **Httpster** | Modern site gallery, strong typography |
| **Lapa Ninja** | Landing pages + free resources |
| **One Page Love** | Single-page sites specifically |
| **Mobbin** | Real product UI patterns, mobile and web |
| **Refero** | Screenshots of real product interfaces |
| **Collect UI** | Patterns grouped by job — onboarding, empty states, pricing |
| **Page Flows** | Recorded user flows, not just stills |
| **Pttrns / Screenlane** | Mobile screen patterns |
| **Typewolf** | Fonts in the wild, pairing judgement |
| **Fonts In Use** | Typography in production projects |
| **Hoverstat.es** | Hover and micro-interaction states |
| **Dark Mode Design** | Dark-theme references |
| **Minimal Gallery** | Restrained, minimal work |
| **Dribbble / Behance** | Concept exploration only — see caution |
| **web.dev · MDN · Can I Use** | Verify a technique, not inspiration |

**Give the AI this caution:** gallery shots are art-directed, not engineered. A Dribbble card routinely fails contrast, keyboard focus and mobile. Take the idea, then run it through `styles.csv`, `ux-guidelines.csv` and the accessibility gates. Never copy markup, copy or assets.

---

## Part H — "Ask first": the change-freeze protocol + the senior guide agent

### What already exists, and what doesn't

The bundled skills have *partial* consent rules — `impeccable` says "Ask before replacing factual copy or adding claims", `hallmark` won't touch an existing design unless you name it. But **no skill enforces a hard freeze**: told to "polish this page", a model will start editing.

That's the gap this closes — one explicit protocol, plus a subagent that owns it.

### The protocol — append to `CLAUDE.md` so it applies to every task

```text
CHANGE-FREEZE PROTOCOL
1. ASK FIRST. Before reading code, ask up to 4 questions: goal, audience, must-keep,
   definition of done. One round only — do not interrogate.
2. READ ONLY. Inspect the codebase after the answers. No edits while inspecting.
3. PLAN, THEN WAIT. Produce: what I would change, which files, why, what I would leave
   alone, and the risk. End with "Approve?".
4. SCOPE LOCK. Edit only files named in the approved plan. If a new file becomes
   necessary, stop and ask.
5. NEVER SILENTLY: rewrite copy, delete content, rename a class across files, add a
   dependency, reformat untouched code, or "tidy" anything outside scope.
6. DESTRUCTIVE = EXPLICIT. Deleting files or branches, force-push, migrations, major
   version bumps: confirm each one by name.
7. REPORT AFTER. Diff summary: changed / not changed / deliberately deferred, plus any
   new risk introduced.
8. MODES. review = zero edits. plan = zero edits. apply = edits only after approval.
   Nothing but an explicit "go ahead" unlocks apply.
```

### The subagent — save as `.claude/agents/senior-frontend-guide.md`

```markdown
---
name: senior-frontend-guide
description: Use when a frontend task needs a plan, a review, or a second opinion before any code changes. Interviews the user, reads the codebase, proposes a scoped plan, and refuses to edit until approved. Invoke for "review this page", "what would you improve", "plan this rebuild", or before running any polish/redesign skill.
tools: Read, Grep, Glob, Bash
---

You are a senior frontend engineer acting as a guide, not an implementer. You have shipped
production design systems, chased down INP regressions, and been in the room when a
"quick polish" broke checkout. Your value is judgement and restraint.

OPERATING LOOP

1. Ask up to four questions — never more:
   - What is this page for, and who is the visitor?
   - What must not change: copy, brand, structure, analytics, SEO?
   - What does "done" mean — review only, plan only, or shipped code?
   - What is the worry you already have about it?
   If the user says "just look at it", treat it as review mode and say so out loud.

2. Read before judging: layout, CSS system, JS, assets, and actual rendered behaviour.
   Quote evidence — line numbers, measured widths, real byte counts. No vibes.

3. Judge in this order, naming the skill behind each finding:
   - Correctness and accessibility → frontend-checklist, impeccable audit
   - Platform API validity → modern-web-guidance
   - Type, colour, spacing, system → ui-ux-pro-max data + hallmark
   - Generic / model-default feel → design-taste-frontend + hallmark
   - Motion and scroll → scroll-craft + motion.csv presets
   - Weight and speed → measure: asset bytes, blocking requests, animated layers,
     rAF loops. Never assert a performance claim you did not measure.

4. Deliver a plan, not an edit. P0/P1/P2, each item with file, change, reason, and the
   test that proves it improved. State plainly what you would NOT touch.

5. Stop and ask for approval. In review and plan modes you make zero edits, ever.

RULES
- Never rewrite the user's copy without asking; their words are product decisions.
- Never add a dependency to fix what a platform API already does.
- Never claim an accessibility or performance win you have not verified.
- Destructive actions get named and confirmed one by one.
- Prefer the smallest change that removes the problem.
- If you disagree with the direction, say so once with evidence, then build what was asked.
```

**How to use it:** run `senior-frontend-guide` first, get the plan, approve it, *then* let `impeccable` or `design-taste-frontend` touch files. The guide decides what to do; the skills do the craft.

---

## Part I — Auto-browse GitHub & the web, then let the user choose

Designing from memory is how every model produces the same page. This part makes the AI **go look, bring back candidates, and hand the aesthetic decision to you** — with the taste skills as the scoring rubric.

### Tool reality check — say which one you have

| Capability | Do this |
|---|---|
| Browser / web tools | Browse. Use the query patterns below. |
| Shell with `gh` authenticated | Use the GitHub commands below (`gh auth status` to confirm). |
| Neither | Say so, use the local catalogs (Parts C–F), and ask the user for links or screenshots |

Never cite a reference you didn't open. A hallucinated inspiration link is worse than no link.

### GitHub browsing — commands verified 2026-11-14

```bash
# 1. find candidates, ranked by stars
gh search repos "scroll animation" --sort stars --limit 20 \
  --json fullName,description,stargazersCount,updatedAt,license

# 2. sweep topics / awesome lists
gh search repos --topic=awesome-design --limit 10 --json fullName,stargazersCount

# 3. how did someone actually implement it?
#    NOTE: `gh search code` does not exist — code search is REST only
gh api "search/code?q=lenis+ScrollTrigger+language:ts&per_page=10" \
  --jq '.items[] | "\(.repository.full_name)  \(.path)"'

# 4. vet a repo before you recommend it
gh api repos/OWNER/REPO --jq \
  '{license:.license.spdx_id, archived, stars:.stargazers_count,
    pushed:.pushed_at, issues:.open_issues_count, forks:.forks_count}'
```

**Rate limits measured today (authenticated):** search **30 req/min**, code search **10 req/min** (it is a separate quota). Cache what you find; never loop these.

### Vetting rubric — a repo passes or it isn't an option

| Check | Pass | Reject / flag |
|---|---|---|
| **License** | MIT · Apache-2.0 · BSD · ISC | none at all · `NOASSERTION` · GPL/AGPL for code you ship |
| **Archived** | `false` | `archived: true` = dead project |
| **Last push** | within ~18 months | stale |
| **Stars vs activity** | active | 5k stars, last commit 2022 |
| **Open issues** | proportionate | thousands open, unmaintained |
| **Deps & types** | typed, tree-shakeable | pulls a framework to do one thing |
| **Accessibility** | keyboard + ARIA in the source | mouse-only |

**Licence honesty:** a repo with **no licence is not usable** — default is all rights reserved. **GPL/AGPL in a shipped front end** carries obligations MIT does not; flag it, never copy silently. `NOASSERTION` means the licence file needs reading by a human. When you do adapt something, record repo + commit + licence in a `CREDITS.md`.

### Web browsing — query patterns by intent

| You need | Search like | Best source |
|---|---|---|
| A visual direction | `"<style> website examples"` | Awwwards · Land-book · Godly · SiteInspire |
| A component pattern | `"<component> UX pattern best practice"` | Mobbin · Collect UI · Page Flows |
| Correct API usage | `"<api> mdn"` / `"<feature> web.dev"` | MDN · web.dev |
| Browser support | `"<feature> caniuse"` | Can I Use |
| Type pairing judgement | `"<font> pairing alternatives"` | Typewolf · Fonts In Use |
| Real implementation | `"<thing> github"` then the GitHub commands above | GitHub code search |
| Library weight | `"<lib> bundle size"` | bundlephobia |

### The selection protocol — the user picks, the AI scores

1. **Brief in one sentence:** goal, audience, must-not-change (from Part H's questions).
2. **Gather 3–5 candidates** from GitHub and the web. For each: what it is, why it might fit, licence, weight, risk.
3. **Score them with the skills, not vibes:**
   - `hallmark` / `design-taste-frontend` → does it avoid model defaults, or is it the generic look?
   - `ui-ux-pro-max` `styles.csv` → does it match a real style *and* that style's constraints?
   - `modern-web-guidance` → is this the modern platform way to do it?
   - `frontend-checklist` → a11y and performance red flags
4. **Present 2–3 directions, never one answer.** A comparison table with tradeoffs. Never make an aesthetic choice on the user's behalf.
5. **Wait for the pick**, then fold it into the approved plan (Part H).
6. **Record provenance:** decision + sources into `DESIGN.md` or `docs/decisions.md`, so the next session doesn't re-litigate it.

### What "taste" means here — four tests, so it isn't a vibe

Every candidate gets scored on:

- **Distinct** — could you name the site from the screenshot alone? If it looks like every other AI portfolio, it fails.
- **Coherent** — one system (type scale, spacing, radius, colour) or a pile of one-offs?
- **Restrained** — one signature move, not five competing effects.
- **Earned** — does each effect map to content (motion showing hierarchy, glass showing layering), or is it decoration?

### Anti-patterns
- Presenting 10 options. Three, maximum.
- Recommending the most-starred repo without opening it.
- Cloning a repo's design wholesale — take the idea, write your own code.
- Browsing *after* deciding. Research is step 2, not step 9.
- Forgetting the licence check because the demo looked good.

---

## Part J — notes

- **Scope.** Project-level (`./.claude`) keeps it per-repo; user-level (`~/.claude`) makes every project see it. Claude Code reads both; `.agents/skills/` is the alternative path some tools use.
- **No `node_modules`, no build step.** Skills are Markdown + static assets + two `.mjs` checkers. Nothing to compile.
- **The gate is the good part.** `design-taste-frontend/scripts/gate.mjs` is a real browser checker — it's what turns "looks generic" into a pass/fail. Node 18+ to use it.
- **Licenses travel with the files.** MIT for design-taste, hallmark, ui-ux-pro-max, frontend-checklist, scroll-craft, react-kino, oil-motion, mapcn; Apache-2.0 for impeccable, modern-web-guidance, ui-sdk. Keep the `LICENSE*` files when redistributing — the installer instructs the AI to preserve them.
- **Verified 2026-11-14:** npm versions from `registry.npmjs.org`; Lenis API/CSS/exports read from the `lenis-1.3.27.tgz` tarball; local data counted directly — `styles.csv` 88 rows (50 active / 29 supplemental / 9 deprecated), `icons.csv` 105, `phosphor-icons-upstream.json` 1,512, `google-fonts.csv` 1,934, `typography.csv` 74, `ux-guidelines.csv` 119; every GitHub command in Part I run for real (and `gh search code` confirmed *not* to exist), with live rate limits 30/min search, 10/min code search.
- **Runtime:** 34 MB payload / ~39 MB on disk · 2,111 files · sparse clone of one branch. First clone pulls only those paths (`--filter=blob:none --sparse`), not the repo's 162 MB of renders.
