# mapcn — the skill is installed, the registry is not reachable

[AnmolSaini16/mapcn](https://github.com/AnmolSaini16/mapcn) · MIT · 12.4k★ ·
"Beautiful map components. 100% Free, Zero config, one command setup."

Themeable, shadcn-style map components on **MapLibre GL** + Tailwind. One component file
(`components/ui/map.tsx`) plus ten full-page blocks: `map`, `analytics-map`,
`choropleth`, `analytics-card`, `delivery-tracker`, `uptime-monitor`, `heatmap`,
`community-globe`, `logistics-network`, `store-locator`.

## What is installed

| Thing | Status |
|---|---|
| **The agent skill** — `.claude/skills/mapcn/` (SKILL.md + `references/{blocks,components,patterns}.md`, 36 KB) | ✔ committed |
| **`maplibre-gl@6.18.0`** — mapcn's only real dependency | ✔ in `site/` |
| The `map.tsx` component and the ten blocks | ✘ **could not install** |
| `npx skills add AnmolSaini16/mapcn` | ✘ not run — it installs into every detected agent, and would duplicate what is committed |

## Why the components could not be fetched

mapcn ships as a **shadcn registry**, so the install is:

```bash
cd site && npx shadcn@latest add https://mapcn.dev/r/map.json
```

That fails here for the same reason Tailark did:

```
Request to https://mapcn.dev/r/map.json failed, reason:
Client network socket disconnected before secure TLS connection was established
```

`mapcn.dev` → HTTP 000. The repo itself is on GitHub (reachable), which is why the skill
files could be pulled; the registry host is not.

**On a networked machine** the two commands are enough:

```bash
cd site
npx shadcn@latest add https://mapcn.dev/r/map.json
# then add blocks by name, e.g.
npx shadcn@latest add https://mapcn.dev/r/choropleth.json
```

`maplibre-gl` is already installed, so the only missing piece is the component source.

## Why it is here — and the honest caveat

A film series has one obvious map need: **where the story happens**. Day 0 is an
apartment, a street, a night walk. If the site ever wants a map of Mikay's world — pins
per episode, the route of the walk, a stylised town — mapcn is the cleanest way to get
one that themes with the rest of the site instead of fighting it.

It is, though, a **SaaS-dashboard component set**: analytics maps, delivery trackers,
uptime monitors, store locators. Nine of the ten blocks are the wrong genre. The one
worth wanting is `map` plus `markers` — the primitives — skinned to match the films.

**Verdict: primitives yes, blocks no.** And nothing about the site needs a map yet, so
this is parked at the documentation stage on purpose.

## Reading order if it is picked up

1. `.claude/skills/mapcn/SKILL.md` — how the components compose, theming, light/dark
2. `references/components.md` — the props
3. `references/blocks.md` — the ten pages, to see what *not* to build
4. `references/patterns.md` — markers, popups, routes, GeoJSON, choropleth
