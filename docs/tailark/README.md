# Tailark — Dusk kit, as a reference

[tailark.com/pages/dusk](https://tailark.com/pages/dusk) · Dusk is one of Tailark's
style kits: "beautifully crafted shadcn blocks, pages, and illustrations" for marketing
sites. Next.js + shadcn, compatible with Radix UI and Base UI.

**Nothing from Tailark is installed.** This file records what Dusk is, what is free, why
the installer cannot run in this environment, and what is and is not worth taking.

---

## 1. What it actually is

Not a repo and not an npm package. Tailark is a **shadcn registry** plus a paid content
library:

- **Free tier ($0)** — "free pages, free blocks, free snippets", lifetime access. The
  registry items are public at `https://oss.tailark.com/r/<item>.json`, and the
  `Dusk` kit's 10 hero blocks, footer, features, FAQ, stats, team, CTA, logo-cloud,
  pricing, testimonials, integrations and content blocks are in it.
- **Essentials ($249) / Complete ($299) / Team ($499)** — one-time payments, unlocking
  hundreds of premium blocks, illustrations, and 90+ finished pages (landing, product,
  solution, pricing, customers, about, contact, blog, brand, legal).

Ten finished Dusk landing pages exist (`dusk/landing/one` … `ten`), but **the finished
pages are the paid tier**. What is free is the blocks and the 30 free pages across all
kits.

## 2. Why it could not be installed here

Three separate blocks, all environmental:

```
$ curl https://oss.tailark.com/r/dusk-hero-section-1.json
→ 000  (TLS socket disconnected before secure connection)

$ curl https://tailark.com/...
→ 000  (same)

$ npx shadcn@latest add https://oss.tailark.com/r/dusk-hero-section-1.json
→ "Client network socket disconnected before secure TLS connection was established"
```

**This sandbox's shell cannot reach tailark.com or oss.tailark.com at all.** Note the
distinction from the earlier shadcn failure: *this* one is not the usual
`ui.shadcn.com` block — the CLI fetches the registry item directly, and the registry
host itself is unreachable.

The documentation pages *are* readable through the browsing tool (which fetches
server-side), so the kit was inspected that way. `docs/tailark/index.json` lists the
block names.

## 3. On a normal network, the install is one command

```bash
cd site
npx shadcn@latest add https://oss.tailark.com/r/dusk-hero-section-1.json
# or a whole kit's blocks, one at a time:
npx shadcn@latest add https://oss.tailark.com/r/dusk-hero-section-8.json
```

They land as `src/components/hero-section-8.tsx`, importing `@/components/ui/button`
and `@/lib/utils` — both already present in this repo's `site/` (the `cn()` helper and
the shadcn config were installed earlier), so the pieces will resolve.

## 4. What the inspected source actually looks like

Worth knowing before anyone pays for it. The free hero blocks are competent and plain:
a nav header, an `h1`, a paragraph, two CTAs, one product image, a logo row. Import
list from `dusk-hero-section-1`:

```tsx
import Link from 'next/link'
import { ArrowRight, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Image from 'next/image'
import { HeroHeader } from '@/components/hero-section-1-header'
```

Two observations from reading the registry JSON:

1. **They are marketing-site blocks for SaaS.** The copy in every example is
   "customer graph", "family money, organised", "trusted by 100,000 families". There is
   no film, gallery, video or editorial block in the free Dusk set. For a stick-figure
   film series the useful ones are: `logo-cloud` (could hold "as seen on"), `stats`,
   `footer`, `faqs`, `team` — not the hero.
2. **The registry JSON's `content` arrives stripped of JSX** when read through a
   browser-rendered view; the real files have far more markup than the excerpt shows.
   Judge the look from `?fullscreen=true` previews, not from the JSON.

## 5. Verdict for this project

**Do not buy it yet, and do not base the page on it.**

- The page needs: a film still as the hero, an episode list, a player, a colophon. Dusk
  supplies none of those — it is a SaaS landing kit.
- The free blocks that *are* relevant (footer, stats, FAQ, logo row) are exactly the
  parts that are quickest to write by hand with the shadcn primitives already installed.
- `docs/PORTFOLIO-REFERENCE.md` already names the real gaps as motion and video, and
  those are installed (`motion`, `lenis`, `media-chrome`).

Use Tailark as **visual reference** — its Dusk previews are a good calibration for
spacing, type scale and restraint in a dark marketing page. If a block is ever wanted,
the free tier is enough to test one, and it can be installed on a machine with network
access in a single command.

## 6. Files here

```
docs/tailark/index.json    block and page names for the Dusk kit + the install command
```

No Tailark code, image, or paid asset is committed to this repository.
