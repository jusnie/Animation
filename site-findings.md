# Complete findings list — `jhnslcc-studio.github.io`

Every error and every improvement, enumerated. Source audited: `jhnslcc-studio/jhnslcc-studio.github.io@main` — one `index.html` (251 lines, 20 KB) + 4 images, no build step.

**Severity:** `BLOCK` = visibly broken for a real visitor · `HIGH` = costs you money or credibility · `MED` = should fix · `LOW` = polish.

**Totals: 34 errors · 41 improvements.**

---

# PART 1 — ERRORS (something is objectively broken or wrong)

## 1A. Functional bugs — will bite real visitors

| # | Sev | Error | Fix |
|---|---|---|---|
| **E01** | `BLOCK` | **Anchor targets land under the sticky header.** `header` is `position:sticky`, 38px logo + 2×14px padding + 1px border = **67px tall**. No `scroll-padding-top` and no `scroll-margin-top` exists anywhere in the file, so every in-page link ("See my projects", "Request a quote", "Contact", the logo's `#top`) positions the target at `y:0` — directly behind the header. | `html{scroll-behavior:smooth;scroll-padding-top:80px}` |
| **E02** | `BLOCK` | **The hero typing line wraps on most phones.** `const focus = 'Minecraft Bedrock';` = 34 chars × 0.6em (JetBrains Mono advance) = **326px at the 16px clamp floor**. Available width at a 360px viewport is `360 − 2×5vw` = **324px**. It wraps by 2px and the blinking `<i>` cursor jumps to line 2 mid-word. | `white-space:nowrap;overflow:hidden` on `.type`, or shorten the phrase, or drop the clamp floor to 14px |
| **E03** | `HIGH` | **Mobile has no navigation.** `@media(max-width:700px){nav a.hide{display:none}}` removes *Services* and *Projects* below 700px, leaving only "Contact". No hamburger, no menu, no fallback. Two of three destinations become unreachable except by scrolling. | Add a toggle, or keep links at smaller type, or drop the `hide` class entirely |
| **E04** | `HIGH` | **Hero content vanishes with JS disabled.** `.type` is an empty `<div>` filled only by JS. No `<noscript>`, no static fallback text. | Ship phrase 0 as static HTML; let JS replace it |
| **E05** | `MED` | **`.shot` crops your screenshots.** Images are 1280×660 (1.939:1) but `.shot` forces `aspect-ratio:16/9` (1.778:1) with `object-fit:cover` → **~4.2% cropped off the top and bottom** of each shot, which is exactly where game HUD and chat text sit. | Set `.shot{aspect-ratio:1280/660}` or re-export at 16:9 |
| **E06** | `MED` | **Copy-success toast never clears.** `role="status"` text stays on screen forever after one click; the button label also never changes to confirm. | Clear after ~4s; swap label to "Copied ✓" |

## 1B. Incorrect / misleading markup

| # | Sev | Error | Fix |
|---|---|---|---|
| **E07** | `HIGH` | **Duplicate `.logo` rule.** Defined once at line ~24 (`font:900 20px…`) and again at line ~107 (`display:inline-flex…`). Two separate rules for the same class in the same stylesheet. | Merge into one |
| **E08** | `MED` | **`role="img"` + `aria-label` on decorative icons.** Each of the 6 `<svg class="ico" role="img" aria-label="Plugin icon">` sits immediately before `<h3>Plugin development</h3>`, so screen readers announce the icon name *then* the heading. Pure duplication. | `aria-hidden="true"`, delete the `role`/`aria-label` |
| **E09** | `MED` | **Alt text over-written, inside a link.** The CNMB `<a>` wraps the image, badge, h3, `<p>` and chips — its accessible name becomes a full paragraph: *"CNMB ARENA waiting lobby showing 1 of 2 players joined and a role boost message, Built by me, CNMB ARENA, Tag team match system…, Behavior pack, Resource pack, JavaScript."* | `alt=""` on the image (link has text), and keep one short `aria-label` on the anchor |
| **E10** | `MED` | **A non-clickable card looks clickable.** The Breeze Bedrock card is a `<div class="card proj">` but inherits `.proj:hover{border-color:var(--cy);box-shadow:…}` — identical affordance to the real link next to it. Your only *client* project is the one nobody can click. | Make it a link to a case study, or scope hover to `a.proj` |
| **E11** | `LOW` | **`<b>` used as a chip style.** `<b>Minecraft Bedrock</b>` for pill tags; `<b>` means "stylistically offset", not "tag". | `<span class="chip">` |
| **E12** | `LOW` | **`<i></i>` used as a text cursor.** `<i>` is for idiomatic text (foreign words, thoughts), not a decorative caret. | `<span class="caret" aria-hidden="true">` |
| **E13** | `LOW` | **Inline `style` where CSS belongs.** 8 inline styles; 6 are legitimate CSS-custom-property positioning (`--x/--y/--s`), but `style="margin-inline:auto"` on the contact `.sub` and `style="position:absolute"` on the sprite are stylesheet material. | Move to classes |
| **E14** | `LOW` | **Hard-coded colour duplicates.** `#c9b8ff` is written literally 2× despite `--pu:#8a5cff` existing; no `--pu-light` token. | `--pu-2:#c9b8ff` |
| **E15** | `LOW` | **Missing `-webkit-backdrop-filter`.** The header uses `backdrop-filter:blur(8px)` unprefixed only, while the file *does* prefix `mask-image`. Inconsistent; older iOS Safari loses the blur. | Add the prefixed twin |
| **E16** | `LOW` | **All-caps H1 in source.** `BUILD. INNOVATE. OPTIMIZE.` is literal uppercase text rather than `text-transform`. Some screen readers spell out letter sequences; also worse for search. | Write sentence case, uppercase via CSS |
| **E17** | `LOW` | **Reduced-motion preference read once.** `matchMedia(...).matches` is evaluated at load; changing the OS setting later has no effect until reload. | Add a `change` listener |
| **E18** | `LOW` | **Stale copyright.** `<footer>DEV_JHNSLCC © 2026</footer>` hard-coded — wrong on 2027-01-01. | `new Date().getFullYear()` |

## 1C. Performance errors

| # | Sev | Error | Fix |
|---|---|---|---|
| **E19** | `HIGH` | **The star canvas never stops.** `requestAnimationFrame(draw)` runs forever: full-viewport `clearRect` + redraw every frame, including when the tab is hidden and when the user has scrolled far past it. | Pause on `visibilitychange`; gate on viewport |
| **E20** | `HIGH` | **`background-position` animation on a 200%-wide element.** `.vox-floor` animates `background-position:0 64px` for 7s, infinite — a **non-compositable** property on a layer ~3840px wide × 70vh. Forces a full repaint every frame, forever. | Animate `transform:translateY()` on an inner layer; add `will-change:transform` |
| **E21** | `HIGH` | **`drop-shadow` on animating elements.** All 6 `.vox-fl` SVGs carry `filter:drop-shadow(0 0 14px …)` *and* animate `transform`, so the filter re-rasterises every frame. One of them is 200px. | Pre-bake the glow into the SVG, or drop the filter |
| **E22** | `HIGH` | **Four stacked full-viewport animated layers behind a backdrop blur.** (1) rAF canvas, (2) repainting grid floor, (3) 6 filtered floating SVGs, (4) gradient `.vox` — all sitting behind a `backdrop-filter:blur(8px)` sticky header, so every scroll frame re-blurs animated content. Guaranteed jank on mid-range Android. | Kill 3 of the 4 on mobile; make the header background opaque under 700px |
| **E23** | `HIGH` | **Render-blocking third-party font stylesheet.** `<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@400;600&display=swap">` blocks first paint on a cross-origin round-trip ×2 (preconnect helps, doesn't solve). 4 weights, 2 families. | Self-host 2 WOFF2 subsets, or cut to one family |
| **E24** | `HIGH` | **470 KB for a 512×512 logo PNG.** `dev-jhnslcc-logo.png` — a simple logo, uncompressed PNG. Should be ~15 KB WebP or ~40 KB optimised PNG. | Convert / downscale to 180×180 |
| **E25** | `MED` | **23 KB for a 96×96 favicon.** `dev-jhnslcc-logo-small.png` is 23 KB — a 96px icon should be ~2 KB. | Re-export, add 32/48 sizes |
| **E26** | `MED` | **315 KB of non-responsive JPEG.** Both screenshots are 1280px wide, displayed at ~537px, with no `srcset`, no WebP/AVIF. ~4.8× oversampled. | Export 640w + 1280w WebP; expect ~60 KB total |
| **E27** | `LOW` | **Remaining timeouts survive tab blur.** The typewriter's `setTimeout` chain keeps scheduling while hidden. | Gate on `document.hidden` |
| **E28** | `MED` | **Missing `width`/`height` attributes on project images.** Only `.shot`'s CSS `aspect-ratio` prevents layout shift; if CSS fails or loads late, images have no intrinsic size. | Add `width="1280" height="660"` |

## 1D. Missing / incorrect metadata

| # | Sev | Error | Fix |
|---|---|---|---|
| **E29** | `HIGH` | **`og:image` is a 512×512 square.** Discord, Slack, WhatsApp, LinkedIn and X all expect **1.91:1**. A square gets letterboxed into a small centered thumbnail — in your primary acquisition channel. Also no `og:image:width/height/alt`. | Ship a dedicated 1200×630 PNG (~80 KB) |
| **E30** | `MED` | **Missing social keys:** `og:type`, `og:url`, `og:site_name`, `og:locale`, `twitter:card`, `twitter:site`, `twitter:image`. Cards render inconsistently across platforms. | Add all 7 |
| **E31** | `MED` | **No canonical URL.** `<link rel="canonical" href="https://jhnslcc-studio.github.io/">` absent; `github.io` serves `/` and `/index.html` as duplicates. | Add canonical |
| **E32** | `MED` | **No `theme-color` / `color-scheme`.** Mobile browser chrome and the scrollbar render **light** against a `#05070d` page. | `<meta name="theme-color" content="#05070d">` + `:root{color-scheme:dark}` |
| **E33** | `MED` | **`robots.txt` and `sitemap.xml` don't exist.** Both 404. | Add both (2 files, 6 lines) |
| **E34** | `LOW` | **No `favicon.ico`, no `<meta name="author">`.** Browsers and some crawlers still request `/favicon.ico` → 404 in your logs. | Add a small `.ico` fallback |

---

# PART 2 — IMPROVEMENTS (not broken, but leaving money and quality on the table)

## 2A. Content & conversion — where the real losses are

| # | Sev | Improvement | Why |
|---|---|---|---|
| **I01** | `HIGH` | **Rewrite the H1 to name the job.** `BUILD. INNOVATE. OPTIMIZE.` is 4 words of slogan with zero keywords. | "Minecraft Bedrock server development" as the H1; keep the slogan as a small kicker. Biggest clarity + SEO win available. |
| **I02** | `HIGH` | **Fill or delete the fake `stats` row.** `<div class="stats">` contains **zero numbers** — just "Bedrock / Endstone / Open". | Either real data (`6 projects shipped`, `48h avg reply`) or remove it. It currently pushes your CTAs below the fold for nothing. |
| **I03** | `HIGH` | **Write a CNMB case study using content you already have.** Your README describes 4 role stands with specific enchants, a boss-bar timer, `/scriptevent` builders, and a sealed-castle finale with iron-barred gates. The site reduces all of it to "Tag team match system." | Free, specific, verifiable proof — highest-leverage change on this list |
| **I04** | `HIGH` | **Publish one Endstone plugin.** You lead with Endstone/Python, but neither showcased project is one (CNMB is `@minecraft/server` JS). Your flagship skill has **zero verifiable proof**. | Even 150 lines + README + screenshot closes the gap |
| **I05** | `HIGH` | **Add prices or price bands.** `Pricing: quote per task` is the least useful line on the page. | "from $25 / small plugin, 2–4 days" converts better *and* filters tyre-kickers |
| **I06** | `HIGH` | **Add a 4-step "how I work."** Deposit → build → revisions → handover? Source files included? Support window? | These are the questions that kill deals in DM |
| **I07** | `HIGH` | **Add a real contact form.** Current flow: click "Copy Discord" → open Discord → search `DEV_JHNSLCC` → paste. 4 steps to say hello. | 3 fields (platform / need / deadline) → webhook or email |
| **I08** | `MED` | **Add proof of outcome.** No player counts, uptime, retention, testimonial, or client name — not even a date on the projects. | "ran 200 concurrent for 3 months" beats every adjective on the page |
| **I09** | `MED` | **Give each project its own page.** One-page site = ~236 words of crawlable text; CNMB also ranks for nothing. | Case-study pages fix thinness *and* earn search traffic |
| **I10** | `MED` | **Add real API code to the typewriter, or cut it.** `plugins.build('Endstone')` and `server.optimize()` **do not exist**. A Bedrock dev spots that in 2 seconds. | Use real calls: `system.runInterval`, `world.afterEvents.playerSpawn` |
| **I11** | `MED` | **De-clone the 6 service cards.** All are 7–11 words with identical rhythm and no deliverable — three in a row use the same "list of four nouns" cadence. | Give each: what you get, typical duration, from-price |
| **I12** | `MED` | **Add an FAQ.** Turnaround, revisions, do you hand over source, do you work with existing packs, payment method. | Removes the top 5 objections |
| **I13** | `MED` | **Add a short "about me" with real background.** Who you are, how long you've been doing this, why Bedrock. | The page currently has a role and a skill list but no person — distinct from I17, which is visual |
| **I14** | `LOW` | **Ship 3–5 more projects, even small ones.** Two projects, one unlinked, is a thin portfolio. | A shop plugin, a kit system, a lobby manager — all count |
| **I15** | `LOW` | **Add availability detail.** "all week (UTC+8)" — add typical reply time and current queue. | Scarcity + trust |

## 2B. Design & copy — killing the generated look

| # | Sev | Improvement | Why |
|---|---|---|---|
| **I16** | `HIGH` | **Drop one of the two fonts.** Orbitron 900 + JetBrains Mono + `#00e5ff`/`#8a5cff` on `#05070d` is *the* most templated portfolio aesthetic of the last two years. Orbitron specifically reads "gamer template." | Keep mono-only, or one display face. Removing one font kills ~40% of the tell *and* half the font bytes. |
| **I17** | `HIGH` | **Add one human element.** Your face, a clip of the arena running, a real screenshot of the castle finale. | Right now there is **no evidence a person exists** behind this — that's what makes it feel generated |
| **I18** | `MED` | **Make the decoration actually Minecraft.** The "voxels" are isometric wireframe cubes and the floor is generic synthwave perspective grid — nothing on the page says "blocks." | Real voxel blocks (grass/dirt/stone), blocky grid. Same effort, on-brand |
| **I19** | `MED` | **Break the identical section skeleton.** Every block is `h2` → one-line `.sub` → grid of 3 cards. | After two sections the page is skimmable to the point of carrying no information |
| **I20** | `MED` | **Kill or earn the pill badges.** All-caps letterspaced `CLIENT PROJECT` / `BUILT BY ME` are an AI-SaaS tell. | Replace with something informative: "2025 · Java Script API · 4 role stands" |
| **I21** | `MED` | **Retire "Full-Stack" for Minecraft work.** Borrowed web-dev buzzword (also in your GitHub bio). | Say "server engineer" / "plugin developer" |
| **I22** | `LOW` | **Tone down the glow budget.** Cyan text-shadow ×2 tiers on the H1 plus glow on buttons, logo, icons, cards, and floor. | One glow per viewport reads intentional; ten reads generated |
| **I23** | `LOW` | **Add a scroll-spy active state to nav.** No indication of where you are. | `aria-current="true"` + underline |
| **I24** | `LOW` | **Add a scroll cue or tighten the hero.** On mobile the H1 + typing + lead push both CTAs below the fold. | Trim `padding:12vh 0 8vh`; move one CTA up |
| **I25** | `LOW` | **Consider `(opens in new tab)` on external links.** 3 `target="_blank"` links, no indication. | Screen-reader and low-vision users lose context |

## 2C. Accessibility improvements

| # | Sev | Improvement | Why |
|---|---|---|---|
| **I26** | `MED` | **Add a skip link.** With a sticky header and 3 nav links, every keyboard visit re-tabs through them. | `<a class="skip" href="#top">Skip to content</a>` |
| **I27** | `MED` | **Add `<meta name="color-scheme" content="dark">`** alongside the CSS property (see E32). | Prevents a white flash before CSS paints |
| **I28** | `LOW` | **Give the toast a dismiss/expiry** (see E06) and keep `aria-live` polite. | Announcements shouldn't persist indefinitely |
| **I29** | `LOW` | **Fix the `.proj` hover-vs-link mismatch** (see E10) — an accessibility issue as much as visual. | Affordance must match behaviour |
| **I30** | `LOW` | **Audit touch targets.** Nav links are 13px text with no vertical padding; `.chips b` are 3px/10px pills. | Aim ≥44×44px hit area on mobile |
| **I31** | `LOW` | **Consider `prefers-contrast`.** Your palette already passes AA — a `more` variant would push it further. | Optional |

## 2D. SEO & discoverability

| # | Sev | Improvement | Why |
|---|---|---|---|
| **I32** | `HIGH` | **Add JSON-LD structured data.** Zero exists. | `Person` + `ProfessionalService` with `serviceType`, `areaServed`, `priceRange`, `sameAs` (GitHub, BuiltByBit) — makes you an entity, not a string |
| **I33** | `MED` | **Rewrite the meta description for intent.** Current 128 chars is fine length-wise but reads as a feature list. | Lead with the job + the differentiator ("Bedrock PvP & minigame systems, shipped") |
| **I34** | `MED` | **Add an `og:image` with text on it** (name + role), not just the logo mark. | Screenshot-style cards get clicked; logos get skipped |
| **I35** | `LOW` | **Add a `404.html`.** GitHub Pages serves its generic one. | Branded 404 with a link home costs 5 minutes |

## 2E. Infrastructure, legal & ops

| # | Sev | Improvement | Why |
|---|---|---|---|
| **I36** | `HIGH` | **Get a real domain.** `jhnslcc-studio.github.io` is unmemorable in a DM and you get no control over headers, caching, redirects, or CSP. | A `.dev`/`.gg` pays for itself with one commission; also enables a `hello@` alias instead of your Gmail |
| **I37** | `HIGH` | **Add a Mojang/Microsoft disclaimer.** You publicly sell Minecraft services. | *"Not affiliated with Mojang Studios or Microsoft. Minecraft is a trademark of Mojang Synergies AB."* — one footer line |
| **I38** | `MED` | **Stop publishing your Gmail in plaintext.** `johnjestersalac123@gmail.com` is in the source of a public page → scraped immediately. | Domain alias + a form, or an obfuscated mailto |
| **I39** | `MED` | **Add analytics (privacy-friendly).** You currently have no idea if anyone visits, or which CTA they use. | Plausible/Umami self-hosted; add a privacy line if you do |
| **I40** | `LOW` | **Add a `manifest.json`.** Minor PWA polish — proper name, icons, theme colour. | Cheap |
| **I41** | `LOW` | **Consider moving off GitHub Pages** for control over security headers (CSP, HSTS, `X-Content-Type-Options`) — GH Pages can't set them. | Cloudflare/Vercel Pages, or keep GH Pages + custom domain |

---

# Do these 8 first, in this order

| Order | Item | Time | Why now |
|---|---|---|---|
| 1 | **E01** scroll-padding | 1 min | Two of your three CTAs currently scroll to a hidden heading |
| 2 | **E02** typing-line wrap | 2 min | Visible breakage on most Android phones |
| 3 | **I01** rewrite H1 | 5 min | Largest clarity + SEO gain per keystroke |
| 4 | **I02** fill or delete `stats` | 5 min | Removes the page's biggest "generated" tell *and* lifts your CTAs above the fold |
| 5 | **E29** real 1200×630 `og:image` | 15 min | Every Discord share currently looks broken |
| 6 | **E03** mobile nav | 30 min | Two-thirds of your nav is invisible on phones |
| 7 | **I03 + I04** CNMB case study + one Endstone repo | 2–4 hrs | The credibility gap, and the only item here that changes what people think of you |
| 8 | **I16 + E19–E22** one font, pause the canvas, compositable grid | 1 hr | Halves page weight and fixes mobile scroll jank |

---

*Read-only audit. Nothing in this repo was modified; no changes were pushed to `jhnslcc-studio/jhnslcc-studio.github.io`.*
