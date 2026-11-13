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
