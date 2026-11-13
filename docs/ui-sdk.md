# UI SDK (vercel-labs/ui) — installed, beta, and the licence needs a note

[vercel-labs/ui](https://github.com/vercel-labs/ui) · **Apache-2.0** · 3.4k★ · beta ·
"A library of behaviors for agents to build the next generation of user interfaces."

The thesis is unusual and worth understanding before anyone builds on it: UI SDK ships
**behaviours, not looks**. Keyboard navigation, focus, selection, dismissal, popups, drag
and drop, and the ARIA they need live in `@ui-sdk/core`; adapters exist for React, Vue,
Svelte, Solid and web components. Components render **no styles of their own** — you
supply the look, or opt into `@ui-sdk/core/web.css` for a default.

## Installed in `site/`

| Package | Version | Licence |
|---|---|---|
| `@ui-sdk/react` | 0.1.0-beta.1 | Apache-2.0 |
| `@ui-sdk/core` | 0.1.0-beta.1 | Apache-2.0 |

zero dependencies; peers are `react`, `react-dom`, `@types/react`, `@ui-sdk/core`.
Verified with esbuild — two components compile to 386 KB, **0 errors**:

```tsx
import { Button } from "@ui-sdk/react/button";
import { Dialog } from "@ui-sdk/react/dialog";
```

Both packages are **subpath-only** (`./button`, `./dialog`, `./popover`, `./menu`,
`./autocomplete`, …) — there is no root import, so tree-shaking is structural rather than
hopeful.

**Docs ship inside the packages**, at `node_modules/@ui-sdk/react/docs/` (2.5 MB, 55
component pages + `llms.txt` as the index). That is a genuinely good pattern: the docs
match the installed version exactly, offline.

## The skill is also installed

`.claude/skills/ui-sdk/` — upstream's `packages/core/skills/ui-sdk` (SKILL.md + seven
references: build-interface, create-component, patterns, styles, testing, agent-ready,
web-components). Its first instruction is the right one: read
`node_modules/@ui-sdk/<framework>/docs/llms.txt` before anything else.

## The licence note that matters

`@ui-sdk/*` is **Apache-2.0** — permissive, but *not* the MIT of the rest of this stack.
Two practical consequences, neither a problem here but both worth writing down:

1. Apache-2.0 carries an explicit patent grant and a NOTICE-file obligation. If a page
   ever ships, keep `LICENSE` and any `NOTICE` alongside the code.
2. It is **beta at 0.1.0-beta.1**. Pin the version; there is no stability promise yet.

## Where it fits — and the honest overlap

This project now has three component layers in `site/`:

| Layer | Model | Best for |
|---|---|---|
| **shadcn** (configured, components not vendored) | copy the source, own it | the public film page |
| **Opus** (0.18.1) | finished, opinionated, heavy | admin surfaces |
| **Astryx** (0.7.15, beta) | finished + swizzle | admin surfaces, leaner |
| **UI SDK** (0.1.0-beta.1) | behaviours only, no styles | anything where the look must be *ours* |

UI SDK is the only one of the four that **cannot** impose a look. That is exactly the
right shape for a film page whose palette is dictated by `tools/vfx.py` and Hallmark's
*Darkroom* theme — but it also means it does none of the visual work for you.

**Verdict:** installed and useful as the *accessibility and interaction* layer underneath
a hand-built page — dialogs, popovers, menus, focus management — without dragging in
anyone else's visual language. Not a reason to replace shadcn, and not a page on its own.
Table stakes caveat: beta, subpath-only imports, and docs you must read from
`node_modules` rather than from memory.
