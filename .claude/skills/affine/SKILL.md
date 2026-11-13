---
name: affine
description: "AFFiNE — open-source knowledge base (docs + whiteboard + database in one page tree). Use when the task needs a self-hosted place to write and diagram the episode bible, beat sheets and notes, or when embedding the BlockSuite editor into a site. Not a component library and not a replacement for the film tools."
---

# AFFiNE (toeverything/AFFiNE)

Next-gen knowledge base — "there can be more than Notion and Miro". Docs, an infinite
whiteboard and a database live in one page tree; privacy-first, self-hostable,
74.5k★. Written in TypeScript + Rust.

**This folder is a reference note, not a vendored source tree.** The repo is 124 MB
across 10,277 files and its backend is a Postgres + Rust + Node stack; copying it into
this repo would dwarf everything else here. The editor itself is on npm and *is*
installed — see below.

## Licence — read this part

`NOASSERTION` on GitHub, and the reason matters:

- everything **outside** `packages/backend` and `packages/common/native` → **MIT**
- `packages/backend` → **AFFiNE Enterprise Edition licence**: production use requires
  agreeing to AFFiNE's subscription terms

So the **client, editor and frontend are MIT**; the **server is not**. Self-hosting
production means reading that EE licence first. The editor package `@blocksuite/affine`
is published as plain **MIT**.

## What is installed here (real, working)

`@blocksuite/affine@0.22.4` — BlockSuite-for-AFFiNE, the block editor under the app —
is installed in `site/` (MIT, 69 dependencies, 498 packages added).

```bash
# a store schema alone bundles cleanly — 442 KB, verified with esbuild
import { Schema } from "@blocksuite/affine/store";
```

It exposes ~210 subpath exports: `./store`, `./std`, `./model`, `./schemas`,
`./rich-text`, `./blocks/<every block>/{store,view}`, `./widgets/…`, `./gfx/…`,
`./components/…`, `./shared/…`, `./foundations/…`.

**Two traps found while verifying:**

1. There is **no `./presets`** export in 0.22.x — `AffineEditorContainer` moved out of the
   single package. Editor assembly now happens per-block and per-widget.
2. `./effects` exports are not stable across minors; importing a named export that the
   published build does not have fails at bundle time (`No matching export … EffectsExtension`).

## Why it is here

The project already keeps its memory in files — `story/`, `docs/`, `references/` — and
that is the right home for anything the renderer reads. AFFiNE is for the *human* side of
the same material: a page tree where the episode bible, beat sheets and shot notes can be
written and diagrammed side by side, self-hosted, without a SaaS account.

If that is wanted, the practical route is the app, not the source: run AFFiNE from its
official container image and keep these markdown files as the source of truth it imports.
Embedding `@blocksuite/affine` directly is a much larger job than it looks — it expects a
document provider, a worker (yjs), and its own styling — and it is only worth doing if
the *site* needs an editor, which a film site does not.
