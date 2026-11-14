# MIKAY — UI/UX stack

Tooling for the episode site. **Nothing is built here yet** — this folder exists so the
front-end can be started without spending a day wiring a design system.

```
site/
  package.json          the installed stack (see below)
  components.json       shadcn/ui config: new-york style, CSS variables, lucide icons
  postcss.config.mjs    Tailwind v4 pipeline
  tsconfig.json         path alias @/* -> src/*
  src/lib/utils.ts      the cn() helper every shadcn component imports
```

## What is installed

| Layer | Package | Version |
| --- | --- | --- |
| Framework | `next` | 16.4.6 |
| UI runtime | `react` / `react-dom` | 19.3.1 |
| Styling | `tailwindcss` + `@tailwindcss/postcss` | 4.3.5 |
| Component system | `shadcn` CLI + `components.json` | 4.23.0 |
| Accessible primitives | `@radix-ui/themes` (and `@radix-ui/react-*` set) | 3.3.0 |
| Class composition | `clsx`, `tailwind-merge`, `class-variance-authority` | latest |
| Icons | `lucide-react` | 1.72.0 |
| Motion / polish | `tailwindcss-animate`, `embla-carousel-react` | latest |
| Interaction primitives — **Emil Kowalski** | `sonner` 2.0.8 (toasts), `vaul` 1.1.2 (drawers) | pinned |
| State | `zustand` | latest |
| Validation | `zod` | latest |
| Type system | `typescript`, `@types/react`, `@types/react-dom`, `@types/node` | latest |
| Lint | `eslint`, `eslint-config-next` | latest |
| Typefaces | `@fontsource-variable/inter`, `@fontsource/archivo-black`, `@fontsource/baloo-2` | 5.3.0 |

## Component library

`shadcn` is installed and configured, but the generated components are **not vendored**:
the CLI fetches each component's source from `ui.shadcn.com`, and this sandbox can only
reach the npm registry. Run this where the network is open:

```bash
cd site
npx shadcn@latest add button card badge separator accordion dialog dropdown-menu \
                        tabs tooltip sheet input textarea select switch
```

That drops typed, accessible components into `src/components/ui/`. They import
`@/lib/utils`, which is already here, so the `cn()` half of the wiring is done.

## Adding a page later

```bash
cd site
npx create-next-app@latest . --ts --tailwind --app --src-dir --import-alias "@/*" --no-install
```

`create-next-app` will offer to keep the existing `package.json`, `tsconfig.json` and
`postcss.config.mjs` — keep them; they are already the stack above. Then add
`src/app/globals.css` with the shadcn CSS variables and start building.

## Typefaces for the films

The same three faces are already in `assets/fonts/` as `.ttf` for the renderer
(`Poppins 700/800/900`, `Baloo2 700/800`, `ArchivoBlack 400`, `Nunito 900`), so the site
and the burned-in captions can match. In React, import from the matching fontsource
package instead of shipping the ttf files twice.

## Emil Kowalski's primitives

`sonner` and `vaul` are already part of the stack above — they are Emil Kowalski's
libraries, and they are what makes a site feel considered rather than merely styled:
spring-eased toasts, drag-to-dismiss drawers, interruptible transitions.

```tsx
// a toast
import { Toaster, toast } from "sonner";
<Toaster position="bottom-right" richColors closeButton />
toast.success("Episode 2 is live");

// a drawer
import { Drawer } from "vaul";
<Drawer.Root shouldScaleBackground>
  <Drawer.Trigger>Open</Drawer.Trigger>
  <Drawer.Portal><Drawer.Content>…</Drawer.Content></Drawer.Portal>
</Drawer.Root>
```

### His written guidance, installable

`@animationsdev/install` (npm, maintained by `emilkowalski`) installs the
**animations.dev** agent skills — the distilled rules behind his interfaces — into Claude
Code, Cursor, Codex, Windsurf, Gemini CLI, OpenCode or Amp.

It is **not run here**: it needs (a) a coding agent detected on the machine and (b) a
personal install token from animations.dev, and both would be yours, not the repo's.
To add it locally:

```bash
npx @animationsdev/install --token=<your-token> emil --project
```

Supply your own token at that prompt — never commit it. If you do install it, the skill
text lands in `.claude/skills/` (or your agent's equivalent); ignore that folder if you
would rather keep it machine-local.

### What to apply, in one line each

- Animate **transform and opacity only** — never layout properties.
- Keep UI motion **under ~200 ms**; exits faster than entrances.
- Ease **out** on entry, **in** on exit; no linear easing on interactive elements.
- Every interactive state gets a transition: hover, press (`scale(0.98)`), focus ring.
- Respect `prefers-reduced-motion` — ship the instant version first.
- Motion should explain a change of state, not decorate a static page.

## UI/UX Pro Max (design-intelligence skill)

Installed at repo root, not inside `site/`:

```
.claude/skills/ui-ux-pro-max/      3.6 MB, 70 files, MIT
  SKILL.md                        when to use it + the query contract
  data/                           79 styles, 192 palettes, 74 font pairings,
                                  119 UX guidelines, 105 icons, 25 charts, 22 stacks
  scripts/search.py               the local search CLI (stdlib only)
  references/                     quick-reference + pro-rules checklists
```

Source: `nextlevelbuilder/ui-ux-pro-max-skill` **v2.15.0** (MIT). The repo pins the
release tag rather than `main`, so the data is reproducible.

### Querying it

```bash
# whole design direction for a project
python3 .claude/skills/ui-ux-pro-max/scripts/search.py \
        "animation studio short films portfolio dark cinematic" \
        --design-system -p "MIKAY"

# one concern
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "button press feedback" --domain ux

# implementation detail for a known stack
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "card grid responsive" --stack nextjs
```

Domains: `style product color typography ux icons chart gsap landing`. Stacks include
`nextjs react tailwind shadcn html-tailwind svelte astro vue nuxt flutter swiftui` and
more. The script needs only Python 3 — no pip install.

### The direction it recommended for this project

Run against MIKAY it returned **Scroll-Triggered Storytelling** + **Motion-Driven**:
pure-black canvas (`#000000`), off-white text (`#FAFAFA`), near-black cards (`#0C0C0C`),
`#3F3F46` borders, and one high-contrast accent reserved for the CTA. That is a good
match for a film page — dark theatre, content-first, motion carrying the story — and it
does not clash with the yellow/raspberry identity already used in the films.

**Agent wiring:** the skill's own installer (`npx ui-ux-pro-max-cli init --ai claude`)
writes `SKILL.md` files into whichever agents it finds; it could not run here because
this sandbox cannot reach `api.github.com` for its release index. The content it would
have written is what is committed above, so nothing is missing — only the multi-agent
plumbing is.

## Impeccable (design-quality skill + anti-pattern detector)

Paul Bakaus's skill family — the "design vocabulary" layer that pairs with UI/UX Pro Max
above. Also at repo root, also vendored from a pinned tag.

```
.claude/skills/impeccable/    2.3 MB, 60 files, Apache-2.0 — v4.9.0
  SKILL.md                    the router: shape · audit · critique · animate ·
                              bolder · quieter · polish · harden · typeset · …
  reference/                  ~40 playbooks (critique, audit, polish, layout,
                              typeset, colorize, animate, harden, craft-floor …)
  scripts/impeccable          the engine shim (calls npx impeccable)
.claude/agents/               4 sub-agents: finish-reviewer, documenter,
                              asset-producer, manual-edit-applier
```

Source: `pbakaus/impeccable` tag **`skill-v4.9.0`** (Apache-2.0).

### The detector actually runs here

Unlike the skills' own installers, the detection engine installs from npm:

```bash
npx impeccable detect site/src            # regex pass over tsx/ts/css
npx impeccable detect http://localhost:3000   # full pass on a running dev server
npx impeccable detect --list-rules        # the 62 rules
```

Verified: on a test file containing `bg-gradient-to-r from-purple-500 to-pink-500`
it fires `ai-color-palette` — *"Purple/violet gradients and cyan-on-dark are the most
recognizable tells of AI-generated UIs."* On `site/src` today it reports **0
anti-patterns**, which is expected: there are no pages yet, so there is nothing to
grade. Run it again once real UI exists — the element-level rules (tiny text, low
contrast, touch targets) need a parsed page and will be silent until then.

### Not installed: the hooks

Upstream ships a `.claude/settings.json` that runs the detector on every `Edit`/`Write`
and again on `Stop`. I left it out deliberately: committing hooks into a shared repo
means every clone starts shelling out to an npm binary on each edit, and it would fire
on `tools/` when the real UI does not exist yet. Add it locally if you want it:

```bash
npx impeccable install -y --providers=claude --scope=project
```

(That installer downloads its bundle from `impeccable.style`, which this sandbox cannot
reach — hence the vendored copy of the same tagged release.)

### How the two skills divide the work

- **UI/UX Pro Max** — searchable data: which palette, which pairing, which layout for
  this kind of product. Answers *what*.
- **Impeccable** — judgement and enforcement: critique it, grade it, catch the AI tells,
  make it bolder or quieter. Answers *is this good, and how do I fix it*.

## Taste Skill (`design-taste-frontend` 2.5.1)

Leonxlnx's anti-slop frontend skill — the "art direction" layer. Vendored from tag
**`v2.5.1`** (MIT), folder renamed to its skill name so the upstream hook paths resolve.

```
.claude/skills/design-taste-frontend/    28 MB, 1565 files
  SKILL.md                   the rules: plain copy, one system, one section per
                             screen, equal edges, real photographs, real product UI
  scripts/                   start · photos · icons · moments · effects ·
                             consistency · perf · shoot · gate · copy-lint
  references/                21 playbooks (layout-v4, copy-voice, motion, photos,
                             scenes, gate, perf, system …)
  library/                   palettes.json (traded colour systems), type.json
  assets/                    starter.html, system.css, layout/style deals, icons,
                             diagrams, scenes, moments, effects, objects
  assets/photos/             photos.json — the index of 413 vetted photographs
```

### Verified working here

```bash
node .claude/skills/design-taste-frontend/scripts/photos.mjs list
# → 413 photographs. Trades: cafe 20, hotel 39, bike 6, food 6, studio 5, office 3,
#   shop 5, books 5, outdoors 31, wellness 8, farm 3 …

node .claude/skills/design-taste-frontend/scripts/start.mjs deal --page tech
# → palette studio-grey / sky-sand / blue-black-cornflower
#   type    mona / epilogue / sora, tracking -4% at hero size
```

`start.mjs deal` writes a `.taste-skill/` state folder where it runs; that folder is
gitignored (I deleted the stray one my test created at the repo root).

### Two deliberate omissions

1. **`assets/photos/img/` — 12 MB of JPEG/WebP files.** The 413-photo index is
   committed (352 KB); the pixels are not. `photos.mjs fetch` reads them from there, so
   a place/cafe/hotel page built from bundled frames needs them: copy them back from the
   tag if you build one —
   `curl -sL https://codeload.github.com/Leonxlnx/taste-skill/zip/refs/tags/v2.5.1 | …`
2. **The `Stop` hook.** Like Impeccable's, it runs `gate.mjs --hook claude` at the end
   of a session. Same reasoning: not committed. Arm it per build instead, which is what
   the tool actually wants:

```bash
node .claude/skills/design-taste-frontend/scripts/gate.mjs --start site/index.html
```

The gate then holds the build until no fixable FAIL remains (three rounds max), and
`consistency.mjs` / `perf.mjs` / `shoot.mjs` check the page in headless Chrome at
1440 / 1024 / 768 / 390. Needs Node 22+ and a Chrome/Chromium — neither is in this
sandbox, so those checks are for your machine.

### Three layers now, no overlap

| Skill | Answers |
|---|---|
| **UI/UX Pro Max** | *what* — palette, pairing, layout data for the product type (searchable) |
| **Impeccable** | *is it good* — critique, audit, 62-rule anti-slop detector |
| **Taste Skill** | *build it* — art direction, layout deals, real photos/icons, the finish gate |

## Stickman Video Director (`directing-stickman-videos`)

Not a web-design skill — this one is for the films. It is a **director for stickman
story videos**, which is exactly the shape of the MIKAY project: stick figure, narrated,
captioned, sound effects, multi-style.

```
.claude/skills/directing-stickman-videos/      482 files + 7 reference clips
  SKILL.md              the router: mode A (director) vs mode B (autopilot), styles A1–A6 / B1–B5
  references/           43 playbooks — style catalog, autopilot runtime, sound system,
                        portrait contract, per-style acceptance gates
  scripts/              26 Node tools (autopilot, render, captions, style reviews,
                        character-explainer, gemini-media, a6 finishing python)
  assets/               fonts, style boards, approved contact sheets, B5 renderers
  tests/                352 upstream tests
```

Source: `kaomei/stickman-video-director` (MIT), cloned at `main` — the repo has no
release tags, so the commit is whatever `main` was on install.

### The two modes

- **A · Director** — produces an approved storyboard and standalone ~10-second prompts
  for a video generator (Google Flow etc.). **No local rendering, no keys.**
- **B · Autopilot** — storyboard → script → 20-second sound preview → full narrated,
  captioned, SFX'd MP4 rendered locally. Needs an image model, a TTS voice, and ffmpeg.

Five B styles ship: B1 minimal line art, B2 colourful hand-drawn, B3 retro TV,
B4 survival thriller, B5 character explainer. B4's rule set is the closest to what we
already do in `tools/build_video.py`: shots **≤3 seconds**, subtitle timing checked
against actual speech, picture-animation reviews on the real MP4.

### What works here, verified

```bash
cd .claude/skills/directing-stickman-videos
npm install                        # @napi-rs/canvas + sharp
node scripts/autopilot.mjs doctor
# node ✔  canvas ✔  sharp ✔  fonts ✔  ffmpeg ✘  ffprobe ✘  gemini_key ✘

node scripts/autopilot.mjs captions "word word word" out.json --lead 3
```

`captions` is the piece worth stealing first: it emits caption timings with a lead-in,
which is the same problem the `lead_in = 1.5` in `tools/script_data.py` solves.

`npm test` → **199 pass / 152 fail**, and every failure is environmental, not broken:
134 are `ffmpeg`/`ffprobe` missing (no system ffmpeg in this sandbox — our films used a
pip-installed imageio-ffmpeg inside a virtualenv that is no longer present), and 4 are
reference clips I trimmed to stay under the size limit. With ffmpeg on PATH the suite
should go green.

### What I trimmed, and why

The upstream skill folder is 68 MB; committed here is 36 MB of it plus 19 MB of the two
approved B5 review clips in `reference-media/`. Cut:

- `assets/b3/portrait-approved-2026-11-13.mp4` (1.3 MB) and the B3 public showcases
  (3.6 MB) — the B1/B2/B3 style boards and contact sheets are kept instead.
- The repo's own `assets/readme/` (220 MB of README videos and GIFs) was never copied.

`node_modules/` (62 MB) is gitignored; `npm install` in that folder restores it.

## Hallmark (anti-AI-slop gate) 2.0.0

Nutlope's design skill — the bluntest of the four, and the one that actually **fails
your code**. MIT, at `.claude/skills/hallmark/` (137 files, 2 MB).

```
SKILL.md                 "The Floor": 11 non-waivable rules + ~60 numbered gates
references/gates.md      40 KB — the gate catalogue with ids and tiers
references/themes/       50 theme specs + the JPGs each one is argued against
references/genres|macrostructures/   editorial · modern-minimal · atmospheric · playful
scripts/sloplint.mjs     the mechanical gate checker (zero deps, Node 18+)
scripts/theme.mjs        deals a theme; scaffolds tokens
scripts/capture|picture|imagegen|refcheck   screenshot and asset gates
```

### sloplint is the useful part, and it runs here

```bash
node .claude/skills/hallmark/scripts/sloplint.mjs site/src
node .claude/skills/hallmark/scripts/sloplint.mjs --url http://localhost:3000
```

It reads `.html .css .jsx .tsx .vue .svelte .astro` — including Tailwind class strings
and `cn/cva` calls. On a deliberately bad test file it fired:

```
FAIL 2a  purple-to-blue gradient            → one anchor hue, solid ink
FAIL 10a transition-all                     → name the properties
FAIL 26a no :focus-visible styling anywhere → instant 3:1 ring
FAIL 30a emoji icon "🚀"                    → one icon library or SVG
FAIL 63  arrow glued to the label           → a verb as the label
FAIL 67  "FEATURES" uppercase 11px tracked  → sentence case, body face, untracked
REFLEX 26b no :active styling anywhere
```

`site/src` currently returns *"no files found"* — there is no UI to lint yet. That is
the first thing to run the moment a page exists; `--before` records a baseline, `--kept`
checks a redesign against it.

### The theme deal it gave for this project

```bash
node .claude/skills/hallmark/scripts/theme.mjs deal --genre editorial \
  --prompt "dark cinematic portfolio for a stick-figure animated film series …"
```

→ **Midnight** (dark / grotesk-sans / cool: midnight-blue ground, cool white ink, Mona
Sans expanded at 300, one azure signal), **Specimen** (light, Bodoni Moda over Geist,
hairline rules), **Darkroom** (warm print-black, fine grain, Sofia Sans Extra Condensed
hairline capitals, one amber safelight). *Darkroom* is the obvious match for the films —
it describes the same 35mm grain look already ported into `tools/vfx.py`.

The deal writes a `.hallmark/` log beside where it runs; I removed the stray one my
test created. Add `.hallmark/` to a local `.gitignore` if you use it.

### Trimmed

`references/themes/*.jpg` (50 files, 5.4 MB) — the theme *specs* are all committed; the
reference photographs are not. Pull them from the repo if you want to look at a theme
before scaffolding it.

### Four layers now

| Skill | Answers | Runs here? |
|---|---|---|
| **UI/UX Pro Max** | *what* — palette/type/layout data | ✔ data only |
| **Impeccable** | *is it good* — 62-rule detector | ✔ npm engine |
| **Taste Skill** | *build it* — direction + finish gate | ✔ non-browser tools |
| **Hallmark** | *stop it* — hard floor, sloplint gate | ✔ sloplint |

## Modern Web Guidance (Google Chrome)

GoogleChrome's skill — **not** a design opinion. It is the current platform truth for
HTML/CSS/client JS, because model weights carry obsolete patterns. Apache-2.0, cloned at
`main`, at `.claude/skills/modern-web-guidance/` — 211 files, 2.4 MB, **209 guides**.

```
SKILL.md        the search-first workflow (search → retrieve → verify → disclose)
guides/         209 guides in 17 disciplines:
                  ui-behaviors 40 · performance 26 · ui-components 22 · visual-design 22
                  forms 19 · css 18 · security 17 · ui-atoms 13 · html 8 · js 5
                  accessibility 4 · built-in-ai 5 · pwa 2 · webmcp 3 · wasm 1 · privacy 1
```

### How it is meant to be used

Search first, retrieve second — never answer from memory:

```bash
npx -y modern-web-guidance@latest search "light dismiss dialog"
npx -y modern-web-guidance@latest retrieve "scrollytelling"

# broad modernisation pass (covers ~20% of the corpus)
npx -y modern-web-guidance@latest legacy-scan site/src --json
```

All three verified from this sandbox — `search` works, `retrieve "scrollytelling"`
returns the CSS `view-timeline` implementation, and `legacy-scan` on `site/src` reports
**0 findings from 33 qualified guides** (nothing to modernise yet).

`retrieve` takes a guide **id** from search results, not a topic guess: asking for
`"scroll-driven-animations"` errors with *no guide found*, while `"scrollytelling"`
works. Search first.

### Why it belongs in this stack

The four design skills argue about taste. This one settles facts — `dialog` vs
`role="dialog"`, `@starting-style` for entry animation, `content-visibility`,
`fetchpriority`, container queries, view transitions, `:has()`, passkeys, sanitization,
date/timezone handling. It is written as vanilla HTML/CSS/JS and expects adaptation to
the framework, which is what `site/` is.

Useful for MIKAY specifically: its `scroll-choreography`, `scrollytelling` and
`scroll-driven` guides are the modern way to build an episode page where each section
advances the story — CSS-driven, no JS scroll listeners, no jank.

### Partially trimmed

`skills/chrome-extensions/` (24 files, 122 KB) — browser-extension guidance, not
relevant to a film site. Pull it back with the clone command if you ever write an
extension.

## Papercut Explainer (nine skills, MIT)

A second film pipeline — 0xS4N4TG's cut-paper explainer reel builder. Nine chained
Agent Skills that turn a link or an idea into a 20–45 s vertical MP4 in the
"layered construction paper brought to life" style: grainy paper props with drop
shadows, rigid cut-out animation, a slow camera push with stop-motion paper *boil*, a
taped headline banner per beat, and word-by-word torn-paper caption tags. Built with
Remotion + any TTS.

```
.claude/skills/papercut-explainer/    the router + 6 references (style guide, motion
                                      principles, remotion recipes, asset prompts …)
.claude/skills/papercut-strategy/     angle and audience from the source
.claude/skills/papercut-hook/         SAY / WRITE / SHOW / ALIGN + 5 scored hook variants
.claude/skills/papercut-script/       the script and the staging table
.claude/skills/papercut-storyboard/   beats → shots
.claude/skills/papercut-build/        Remotion scenes
.claude/skills/papercut-voice/        TTS direction
.claude/skills/papercut-qa/           the acceptance pass
.claude/skills/papercut-setup/        install-mode probing
```

Every beat runs **three tracks**: the voiceover tells the story, a taped banner adds a
hard fact the voiceover skips, and a fresh paper set illustrates the voiceover's words.

### What is committed, and what is not

The nine skill texts (212 KB) are vendored. The upstream `library/` — a 15 MB Remotion
project with the paper `kit/`, `backdrops-src/`, the episode `template/` and 14 MB of
public textures, plus the audio and voice packs — is **not**. Stages 1–4 (strategy, hook,
script, storyboard) need no library; stages 5–8 do. See
`.claude/skills/papercut-explainer/LIBRARY-README.md` for the clone + `$PAPERCUT_LIB`
instructions.

### Why it is here

Two things transfer to MIKAY even without the library:

1. **`references/style-guide.md`** — a measured style DNA. Colours are pixel-sampled,
   motion is tracked at 30 fps, the paper *boil* is specified in frames. That is the
   level of specificity our `tools/vfx.py` constants already have, and it is a good
   model for specifying Mikay's own look.
2. **`papercut-hook`'s first-three-seconds discipline** — SAY / WRITE / SHOW / ALIGN,
   written out before any script, scored against five variants. Our day0 film opens on
   the apartment with a 1.5 s narration lead-in; this is the framework for arguing about
   whether that opening earns the next ten seconds.

It is a different visual language from the stick-figure films — paper, not line — so it
is a second format for the channel, not a replacement for `tools/build_video.py`.

## Opus (`opus-react` 0.18.1) — the component library

[project-opus.netlify.app](https://project-opus.netlify.app) · MIT · npm `opus-react`.
A production React 19 design system for **data-heavy product surfaces**: 308 documented
components across forms, dashboards, overlays, charts, auth screens, and full
application shells (CRM workspaces, desktop environments, document managers).

```bash
npm install opus-react three
```

| | |
|---|---|
| Package | `opus-react@0.18.1` (130 versions, published 2026-11-11) |
| Licence | MIT |
| Peer deps | `react` / `react-dom` `^18.2 \|\| ^19`, **`three` `^0.185`** |
| Weight | 42 MB unpacked, 150 transitive deps (maplibre, codemirror, fontawesome, remark) |
| Exports | `.` · `./styles.css` · `./index.css` · `./flags.css` |

### Verified in this sandbox

`npm i opus-react` resolved and installed cleanly in `site/`, and a real bundle
compiles against the stack already there:

```tsx
import { OpusThemeProvider, Button, TextField } from "opus-react";
import "opus-react/styles.css";
```

→ esbuild bundle, **0 errors**. The package exposes 343 typed exports; the theme entry
point is `OpusThemeProvider`.

### Two things to know before you build a page

1. **`three` is a required peer dependency**, not optional — importing anything from the
   package pulls it in. It is installed alongside (`three@0.185.1`).
2. **It is heavier than the rest of the stack.** 42 MB unpacked and 150 transitive
   dependencies, because the library bundles maplibre (maps), CodeMirror (a code editor),
   FontAwesome and remark (markdown) for its lab components. If a film site only needs
   a player, cards and a nav, import from the primitives you use and watch the bundle —
   the first component you touch costs ~7 MB before tree-shaking.

### Where it fits

Opus and the four design skills answer different questions. Opus is **finished
components** — it will make the admin/back-of-house surfaces (episode catalogue, upload
queue, analytics) look professional immediately. The skills are for the **public film
page**, where the design has to be yours. Mixing them is fine as long as the public page
does not start reading like a dashboard.

It is the one item in this install with an opinion about *internal tools*, not about
this project — installed because you linked it, and documented here so it is not a
mystery dependency six months from now.

## Astryx (`@astryxdesign/core` 0.7.15) — Meta's design system

[meta/astryx](https://github.com/meta/astryx) · MIT · **Beta** · built on React 19 +
StyleX. Grew inside Meta over eight years, powering 13,000+ apps; 150+ accessible
components, brand-level theming, dark mode, a CLI, and swizzle (eject a component's
source into your project to own it).

```bash
npm install @astryxdesign/core @stylexjs/stylex
```

| | |
|---|---|
| Package | `@astryxdesign/core@0.7.15` (published 2026-11-12) |
| Licence | MIT, but **Beta** — the API can move |
| Peer deps | `react` / `react-dom` `>=19.0.0`, `@stylexjs/stylex` `^0.19` |
| Weight | 31 MB unpacked for core; 44 MB with StyleX installed |
| Exports | `.` · `./reset.css` · `./astryx.css` · `./tailwind-theme.css` |

**122 component directories** — AppShell, CommandPalette, DateRangeInput, MultiSelector,
PowerSearch, Table, TreeList, Toast, TopNav/SideNav/MobileNav, Chat, Markdown, and more.

### Verified in this sandbox, including the trap

A real esbuild bundle compiles with 0 errors:

```tsx
import { Button, Card, TextInput, Theme } from "@astryxdesign/core";
import "@astryxdesign/core/reset.css";
import "@astryxdesign/core/astryx.css";

<Theme><Card><TextInput label="Episode" /><Button>Ship</Button></Card></Theme>
```

**Gotchas that cost time here, so they do not cost time later:**

1. The theme wrapper is **`<Theme>`**, not `<ThemeProvider>` — there is no
   `ThemeProvider` export, and the build fails on it.
2. The text field is **`TextInput`**; there is no `TextField`.
3. **StyleX is a required peer.** `@stylexjs/stylex@0.19.2` is installed alongside.
4. **No Tailwind plugin needed for consumption** — you import pre-built CSS. But it also
   ships `tailwind-theme.css`, which maps Astryx tokens into Tailwind, so the two
   systems can share one palette if asked.

### Astryx or Opus?

Both are now installed and both are data-heavy-product systems. Honestly:

| | Opus | Astryx |
|---|---|---|
| Maturity | 130 versions, self-published | Meta, 8 years internal, **public beta** |
| Components | 308 | 150+ (122 entries inspected) |
| Styling | bundled CSS | StyleX-authored, overridable with anything |
| Extras | maps, code editor, 3D mark | CLI + **swizzle** (own the source) |
| Weight | 42 MB / 150 deps | 31 MB / 7 deps (**far leaner**) |

Astryx's swizzle is the deciding feature: when a film page needs a component to look like
*ours* rather than like a design system's, ejecting its source beats fighting its API.

## Auto Ontology (NVIDIA) — semantic layer, MCP client

[NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology) · Apache-2.0 · public beta ·
12k★. A Python framework for a **semantic, graph-based reasoning layer over data**: it
sits between an LLM and a warehouse so one reviewed definition of a business term
replaces a fresh guess per query.

Installed as `.claude/skills/auto-ontology-mcp/` (460 KB: SKILL.md, the MCP README,
`docs/mcp.md`, the OpenAPI spec the server builds from, and the 4-dependency
`pyproject.toml`).

**What was verified:** the MCP server installs and boots in a Python 3.11 venv —

```
Starting Auto Ontology MCP server — version 1.2.0, listening on http://localhost:3003
Server: auto-ontology, 1.2.0  (FastMCP 3.4.11)
```

It is a pure HTTP client of a deployment (no DB credentials, no secrets in its config;
the deployment signs each caller in). Tools: `ask_question` — text-to-SQL through the
glossary, returning the answer, the SQL and the rows — plus `search_terms`,
`describe_table`, `check_answerable`. Everything reads; nothing writes.

**What was not, and cannot be, installed:** `auto-ontology-server`. It requires Python
**3.12–3.13**, ~450 packages including a git-based dependency, Postgres, and a Docker
Compose stack with a FastAPI backend and a Next.js frontend. This sandbox has Python
3.11, no Postgres, no Docker.

`site/README.md` is the design-stack log; this belongs to the same running list because
it is the only entry here about *data* rather than pixels. There is no MIKAY data set to
put in an ontology yet — episode catalogue, upload queue and QA results would be the
candidates once they are real.

## AFFiNE (`@blocksuite/affine` 0.22.4) — the editor, not the server

[toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) · 74.5k★ · docs +
whiteboard + database in one page tree, self-hostable.

### Licence is **mixed** — the important finding

GitHub reports `NOASSERTION` for a reason:

| Path | Licence |
|---|---|
| everything else (client, frontend, editor) | **MIT** (`LICENSE-MIT`) |
| `packages/backend`, `packages/common/native` | **AFFiNE Enterprise Edition** — *"may only be used in production, if you … have a valid AFFiNE Enterprise Edition subscription for the correct number of user seats"* |
| anything served client-side (CSS, fonts, compiled client JS) | **MPL-2.0** — a clause that is easy to miss |

So the editor is MIT and usable; **the server is not free for production**. Self-hosting
means reading the EE licence first.

### What is installed

`@blocksuite/affine@0.22.4` — BlockSuite-for-AFFiNE — in `site/` (MIT, 69 deps, 498
packages added). Verified with esbuild:

```tsx
import { Schema } from "@blocksuite/affine/store";   // bundles to 442 KB, 0 errors
```

~210 subpath exports: `./store ./std ./model ./schemas ./rich-text
./blocks/<block>/{store,view} ./widgets/… ./gfx/… ./components/… ./foundations/…`

**Two traps found and documented:** there is **no `./presets`** export in 0.22.x
(`AffineEditorContainer` is no longer shipped from the single package — editor assembly
is per-block/per-widget), and `./effects` named exports are not stable across minors.

### The repo itself is not vendored

124 MB across 10,277 files — `packages/frontend` alone is 90 MB. Copying it here would
dwarf every film, skill and asset in the project. It is documented instead, in
`.claude/skills/affine/SKILL.md`.

### Where it fits

The project's memory already lives in files (`story/`, `docs/`, `references/`) because the
renderer reads them. AFFiNE is for the *human* half: a page tree where the episode bible,
beat sheets and shot notes are written and diagrammed side by side, self-hosted, no SaaS.
The practical route is the app (run it from the official image and import these markdown
files), not embedding BlockSuite — that needs a document provider, a yjs worker and its
own styling, and a film site does not have an editor-shaped hole.

## Motion + video layer (installed)

The one real gap in the original stack. All MIT, all verified bundling together
(855 KB esbuild bundle, 0 errors):

| Package | Version | What it does |
|---|---|---|
| `motion` | 14.14.0 | Framer Motion standalone — `whileInView`, layout animation, springs, `useScroll` |
| `lenis` | 1.3.27 | Smooth scroll. Needs `lenis/dist/lenis.css`, which is not optional |
| `media-chrome` | 4.19.5 | Web-component player (`<media-controller>`) with seek, PiP, captions |

```tsx
import { motion, AnimatePresence, useScroll, useSpring } from "motion/react";
import Lenis from "lenis";
import "lenis/dist/lenis.css";
import "media-chrome";
```

These are the pieces the portfolio templates in the wild are actually weak at. The
research behind choosing them — what to read, what to skip and why — is in
[`docs/PORTFOLIO-REFERENCE.md`](../docs/PORTFOLIO-REFERENCE.md).

## Tailark "Dusk" — reference only, not installed

[tailark.com/pages/dusk](https://tailark.com/pages/dusk) is a **shadcn registry** of
marketing blocks, on a free tier plus paid page packs ($249–$499 one-time).

**Could not be installed here:** `oss.tailark.com` and `tailark.com` are unreachable
from this sandbox's shell — TLS sockets close before handshake, so even
`npx shadcn@latest add https://oss.tailark.com/r/dusk-hero-section-1.json` fails at the
fetch. This is a different block than the earlier shadcn one: the registry host itself is
unreachable, not just `ui.shadcn.com`.

On a normal network it is one command per block:

```bash
cd site && npx shadcn@latest add https://oss.tailark.com/r/dusk-hero-section-8.json
```

The blocks land in `src/components/` importing `@/components/ui/button` and
`@/lib/utils`, both of which already exist here.

Substance is in [`docs/tailark/README.md`](../docs/tailark/README.md) and the block list
in [`docs/tailark/index.json`](../docs/tailark/index.json). Short version: Dusk is a SaaS
landing kit with no film, video or editorial blocks — the free ones worth a glance are
footer, stats, FAQ and logo-cloud. Use it to calibrate spacing, not to build the page.

## Three more: doticons, mapcn, Front-End Checklist

### doticons 0.9.0 — installed

`doticons` (MIT, 244 dot-matrix icons, 16 px and 32 px sets) in `site/`. Verified with
esbuild (158 KB for a three-icon import, 0 errors).

```tsx
import { AlarmDoticon, CirclePlayDoticon } from "doticons/32";
```

**Every export is suffixed `Doticon`** — `Alarm` and `Play` do not exist; the play glyph
is `CirclePlayDoticon`. Full note: [`docs/doticons.md`](../docs/doticons.md).

Why: lucide is thin line art; doticons is chunky dots, which sits closer to a
stick-figure film's grain. 244 icons is small — no clapperboard or subtitle glyph — so
expect to use both sets.

### mapcn — skill installed, components not

`AnmolSaini16/mapcn` (MIT, 12.4k★) is shadcn-style map components on `maplibre-gl`.
Committed: `.claude/skills/mapcn/` (SKILL.md + 3 references) and `maplibre-gl@6.18.0`.

The component registry could **not** be fetched — `mapcn.dev` returns 000 from this
sandbox, so `npx shadcn@latest add https://mapcn.dev/r/map.json` fails at the fetch. One
command on a networked machine fixes that. Details, including the honest verdict
(primitives yes, nine of ten blocks are SaaS dashboards): [`docs/mapcn.md`](../docs/mapcn.md).

### Front-End Checklist — skill installed, MCP not

`.claude/skills/frontend-checklist/` (MIT, 74.7k★): the aggregate skill over **386
rules**, plus `references/categories.md` for the taxonomy.

The workflow routes through the `frontendchecklist.io` MCP server (`review_code`,
`audit_url`, `search_rules`…), which is not connected here. Everything in the skill's
"Audit Stance" and rule-derived-highlights sections stands on its own though — it is
evidence-first review discipline (don't flag decorative `alt=""`, don't infer intent from
a fragment, prefer 1–2 strong findings over speculative breadth), and that part is worth
reading before any audit.

It overlaps Hallmark and Impeccable by design; the difference is that those two are
*opinionated about taste*, while this one is a *platform-correctness* checklist.

## AVAL (`@pixel-point/aval-react` 1.0.2) — interactive video delivery

[pixel-point/aval](https://github.com/pixel-point/aval) · MIT · 1.4k★. A web format and
runtime for **short prerendered motion with a state machine**: loops, named states,
authored triggers, bounded transitions, reversals, packed-alpha transparency. One
logical animation ships as a codec bundle (`.avl` per codec), and the browser picks the
first of **AV1 → VP9 → H.265 → H.264** that decodes.

Installed (MIT, both verified bundling with 0 errors):

| Package | Version | Role |
|---|---|---|
| `@pixel-point/aval-react` | 1.0.2 | `useAval()` + `AvalComponent` |
| `@pixel-point/aval-element` | 1.0.3 | the custom element |

```tsx
import { useAval } from "@pixel-point/aval-react";        // eager, 991 KB
import { useAval } from "@pixel-point/aval-react/lazy";   // runtime in its own chunk
```

**Two things to know before using it on a page:**

1. **AVAL will not fall back by design.** No fallback content is created or revealed; if
   WebCodecs is missing or no codec decodes, `prepare()` rejects with `AvalPlaybackError`
   and the element fires one fatal `error` event. Attach that listener before
   registering, branch on `failure.code`, and ship your own `<video>` fallback.
2. **The compiler needs ffmpeg.** `@pixel-point/aval-compiler@1.1.0` (binary `avl`)
   validates a `motion.json` and then stops at `ERROR FFMPEG_NOT_FOUND` here. The full
   validated schema — eleven required top-level fields, `range` as an array,
   `"playback": "loop"` not `"loop": true`, required `preset` and `crf` — is written out
   in [`docs/aval.md`](../docs/aval.md), derived from the compiler's own error messages
   rather than guessed.

Why it is here: it is the only installed thing that answers *how the page shows motion*
rather than *what the page should look like*. Verdict and the caveats (WebCodecs, lossy
shadows vs the film grade) are in `docs/aval.md`.

### Re-installed with the official installer (and why it is not an MCP)

The upstream CLI can now do the install itself; verified here:

```bash
DISABLE_TELEMETRY=1 npx modern-web-guidance@latest install \
    --agent claude-code --scope project -y
# → ✓ modern-web-guidance (copied) → .claude/skills/modern-web-guidance
```

Two things learned: the agent id is **`claude-code`** (not `claude` — 79 ids are accepted
and `claude` is not one of them), and the run writes a **`skills-lock.json`** at the repo
root with `computedHash` of `SKILL.md`, which is a useful integrity pin. It also *deletes*
`LICENSE` from the skill folder on reinstall — restored here.

**This is a skill, not an MCP server.** There is no `.mcp.json` and no MCP server in the
repo; the `webmcp/` guides are about implementing WebMCP *in your own web app*, not about
exposing these guides. The interface is the `search` / `retrieve` / `legacy-scan` CLI,
which is `npx`-runnable and needs no server.


## UI SDK (`@ui-sdk/react` 0.1.0-beta.1) — behaviours, not looks

[vercel-labs/ui](https://github.com/vercel-labs/ui) · **Apache-2.0** (not MIT) · 3.4k★ ·
beta. Keyboard navigation, focus, selection, dismissal, popups, drag and drop, and the
ARIA they need — with **no styles of their own**. React, Vue, Svelte, Solid and web
component adapters over one core.

```tsx
import { Button } from "@ui-sdk/react/button";
import { Dialog } from "@ui-sdk/react/dialog";
```

Installed: `@ui-sdk/react` + `@ui-sdk/core` (zero deps; peers react, react-dom,
@types/react). Verified with esbuild: 386 KB for two components, **0 errors**.

Four things to know:

1. **Subpath-only imports** — there is no root export. `./button`, `./dialog`,
   `./popover`, `./menu`, `./autocomplete`, … Tree-shaking is structural.
2. **Docs ship in the package**: `node_modules/@ui-sdk/react/docs/` (2.5 MB, 55 component
   pages, `llms.txt` as index). Read those instead of the website — they match the
   installed version.
3. **Licence is Apache-2.0**, unlike the MIT of the rest of this stack: patent grant plus
   a NOTICE obligation. Keep `LICENSE`/`NOTICE` with any shipped code.
4. **Beta at 0.1.0-beta.1** — pin it.

The skill is committed too: `.claude/skills/ui-sdk/` (SKILL.md + 7 references).

Where it fits: this is the only component layer in `site/` that **cannot impose a look**,
which is exactly right under a palette set by `tools/vfx.py` and Hallmark's Darkroom —
usable for dialogs, popovers, menus and focus management under a hand-built page. It is
not a replacement for shadcn and not a page in itself. Detail:
[`docs/ui-sdk.md`](../docs/ui-sdk.md).

## Scroll choreography: scroll-craft, oil-motion, react-kino

Three answers to "animate when you scroll", at three different levels — all MIT.

| Where | What | Star count |
|---|---|---|
| `.claude/skills/scroll-craft/` | agent skill + its own 62 KB attribute-driven engine | 5,034★ |
| `.claude/skills/oil-motion/` | agent skill + 16-script Python video-scrub pipeline | 2,898★ |
| `react-kino@0.6.0` + `@react-kino/core@0.4.0` | real React library: Story/Scene + portable document + local editor | 221★ |

```tsx
import { Story } from "react-kino/story";
import { Storyboard } from "react-kino/studio";
import { createStoryRecipe } from "react-kino/recipes";
const doc = createStoryRecipe("editorial");   // launch | editorial | case-study
                                              // comparison | gallery | portfolio
<Story document={doc} components={createRecipeComponents()} />
```

Verified: Story + Storyboard + recipe compile to 136 KB, **0 errors**. Editor lives at
`react-kino/studio` and is not imported by the runtime; documents are data only, imports
capped at 2 MB. Below 640 px and under `prefers-reduced-motion` a story degrades to a
natural reading layout — the fallback hand-rolled GSAP sites usually skip.

**Trap:** `react-kino/document` exports no `Document`. Use the root entry — `Story`,
`Scene`, `useScrollProgress`, `ScrollTransform`, `TextReveal`, `HorizontalScroll`,
`Parallax`, `Marquee`, `StickyHeader`, `VideoScroll`, `Progress`, `Reveal`, `Counter`,
`Panel`, `CompareSlider`.

**scroll-craft** is a page grammar (journey → grammar → emotional peak → one signature
move) plus a declarative engine: 28 `data-sc-*` attributes (`parallax`, `pan`, `drift`,
`magnet`, `reveal`, `kinetic`, `cue`, `dwell`, `linger`, `count`, `clip-map`, `progress`),
with `doctor.mjs` / `serve.mjs` / `shoot.mjs` / `encode.sh` / `worldflight-assert.mjs`.
Preflight here: node ok, **ffmpeg FAIL**, playwright + Chrome warned, no KIE key (only
needed to *generate* imagery).

**oil-motion** turns AI-generated or existing frames into scroll/pointer/drag/touch-driven
web animation. 16 Python scripts pass `py_compile`; needs ffmpeg/ffprobe to actually
compile, so — like AVAL — it is installed and readable but cannot output here. English
README is `README.en.md`.

Detail: [`docs/scroll-choreography.md`](../docs/scroll-choreography.md).

## Costing tool parts list (research, not built)

See [`docs/costing-tool-stack.md`](../docs/costing-tool-stack.md). The one-line version:

- **Licence trap:** `midday` (15k★), `easy-invoice-pdf`, `invoicerr` are all **AGPL-3.0** —
  unusable for a paid SaaS. `al1abb/invoify` (6,391★, **MIT**) is the invoicing app worth
  studying instead.
- **Excel works today, here:** `haris-musa/excel-mcp-server` (4,301★, MIT) pip-installs and
  registers **44 tools** — verified in this workspace. `goal_seek` (backwards costing),
  `trace_formula`, pivot tables, charts, CSV import/export.
- **Sheets needs Vercel:** `taylorwilsdon/google_workspace_mcp` (3,515★, MIT) or `drive.file`
  scoped OAuth + Google Picker. Cannot be tested from this sandbox.
- **AI:** `vercel/ai` `generateObject` + a Zod schema — one endpoint, not a chatbot.

## Capacitor 8.6.2 — one web app, iOS + Android + desktop

Installed because a paid "build iOS without a Mac" service is not something you can
install, and the free path is the same structure. All MIT.

```
@capacitor/core  @capacitor/cli  @capacitor/ios  @capacitor/android   8.6.2
site/capacitor.config.ts        webDir: 'out'  (Next.js static export)
site/ios/App/App.xcodeproj      committed — open in Xcode
site/android/app/build.gradle   committed — open in Android Studio
```

Verified here: `cap add ios` / `cap add android` both succeeded, and `cap sync` copied a
test `out/index.html` into `ios/App/App/public/` **and** `android/app/src/main/assets/public/`.
Only the native compilers are absent (no Xcode, no Android SDK, neither installable in
this sandbox).

Live reload on device: `CAP_SERVER_URL=http://<lan-ip>:3000 npm run dev`.

Builds: `.github/workflows/mobile-builds.yml` — Android APK/AAB on `ubuntu-latest`, unsigned
iOS `.app` on `macos-latest`. Free on public repos, no credits. Apple's $99/yr and App Store
review remain regardless of which CI you use.

Detail: [`docs/ios-android.md`](../docs/ios-android.md).
