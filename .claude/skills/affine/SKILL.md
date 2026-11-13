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

## Licence — the exact terms, now quoted

`NOASSERTION` on GitHub, and the reason matters:

- everything **outside** `packages/backend` and `packages/common/native` → **MIT**
  (`LICENSE-MIT.txt`)
- `packages/backend` → **AFFiNE Enterprise Edition licence** (`LICENSE-backend-EE.txt`),
  whose words are worth reading rather than paraphrasing:

  > "This software and associated documentation files (the Software) may only be used in
  > production, if you (and any entity that you represent) have agreed to, and are in
  > compliance with, the AFFiNE Subscription Terms of Service … and otherwise have a
  > valid AFFiNE Enterprise Edition subscription for the correct number of user seats."

  Development and testing need no subscription. **Production does.**
- One clause is easy to miss: any part served client-side (CSS, fonts, compiled client
  JS) is **MPL-2.0**, not MIT.

The editor package `@blocksuite/affine` is published as plain **MIT** — that is the part
installed in this repo, and it is unaffected by the EE licence.

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

## Self-hosting, if it comes to that

`developing-server.md` is vendored here. The short version: AFFiNE's server needs
Postgres (or `pgvector/pgvector:pg16` from 0.20 on), Redis and Mailhog via
`.docker/dev/compose.yml`, a Rust toolchain for the native packages, and Yarn 4. There
is no `docker run` one-liner in the repo; the "official image" route is the published
`affine` container, which is the community edition.

Because `packages/backend` is EE-licensed, the honest recommendation stands: **run AFFiNE
as an app for humans, keep `story/`, `docs/` and `references/` as the source of truth.**
Do not fork the backend.
