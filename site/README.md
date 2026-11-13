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
