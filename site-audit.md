# Audit — `jhnslcc-studio.github.io`

**Scope:** live site + source repo (`index.html`, 251 lines, 4 images, no build step).
**Context:** repo created 2026-11-13, last push 2026-11-14 — this is a v0.1, roughly one day old. Read everything below with that in mind.

**Verdict:** technically it's better than most AI-generated portfolios — the CSS is hand-tuned, contrast passes AA everywhere, and there's real care in the details. But the *content* is where the slop is: 236 visible words, zero specifics, and a design language that is instantly recognisable as "AI dev portfolio #4,000." It sells the least interesting thing about you and hides the most interesting thing.

---

## 1. What's genuinely good (don't "fix" these)

| Thing | Why it matters |
|---|---|
| Contrast passes AA on **all 11 colour pairs** I measured (lowest 7.01:1) | Most neon-on-black sites fail this badly. You didn't. |
| `prefers-reduced-motion` block actually kills the animations | Rare. Most people fake it. |
| `:focus-visible` with 2px cyan outline | Keyboard users can see where they are. |
| Decorative layers are `aria-hidden`; sprite is hidden | Screen readers aren't read a starfield. |
| Images have real `alt` text and `loading="lazy"` | Better than 90% of portfolios. |
| `aspect-ratio` on `.shot` + `min-height` on the typing line | No layout shift. |
| Single file, no framework, no jQuery, ~20 KB HTML | Loads instantly. |
| `rel="noopener"` on every `target="_blank"` | Correct. |
| Endstone named explicitly, `UTC+8` given | Actual specificity — more of this, please. |

That list is why the rest of this document is about *content and polish*, not "rewrite it."

---

## 2. The AI-slop tells

This is the section you asked for. These are the signals that make a visitor think "template" before they think "developer."

**1. The font pairing.** Orbitron 900 + JetBrains Mono + `#00e5ff` cyan + `#8a5cff` purple on `#05070d`. This exact combination is the single most generated portfolio aesthetic of the last two years. Orbitron specifically reads "gamer template." Swapping one font kills ~40% of the tell.

**2. The slogan H1.** `BUILD. INNOVATE. OPTIMIZE.` — three imperative verbs, all caps, no noun, no keyword. It says nothing, ranks for nothing, and is the most textbook LLM headline there is. A human who builds Minecraft servers would write "I build Minecraft Bedrock servers" because that's the thing they want to be hired for.

**3. Fake code as decoration.** The typewriter cycles:

```js
const focus = 'Minecraft Bedrock';   // fine-ish
plugins.build('Endstone');           // no such API
server.optimize();                   // no such API
commissions.open = true;             // not code, a sentence in costume
```

Two of four lines reference methods that don't exist. A Bedrock dev reading this clocks it in two seconds, and it costs you credibility with the exact audience you want. Either use *real* API calls from your own work (`system.runInterval`, `world.afterEvents.playerSpawn`, `player.runCommandAsync`) or drop the gimmick.

**4. The mislabelled "stats" band.** The markup is literally `<div class="stats">` containing:

> **Bedrock** — Platform I build for · **Endstone** — Plugin framework · **Open** — For commissions

There are no stats in the stats. No number, no unit. This is the page's biggest tell: an LLM-shaped slot that got filled with words instead of data. Either put real numbers there (`6 shipped projects`, `2 yrs`, `<24h` reply) or delete the row — it currently pushes your real CTAs below the fold for nothing.

**5. Six interchangeable service cards.** Every description is 7–11 words, same rhythm, no deliverable:

> "Custom features, mechanics, commands, events, and server-side systems."
> "Custom entities, items, behaviors, and gameplay mechanics."
> "Textures, UI, animations, models, and visual customization."

That's the list-of-four parallel noun phrase cadence — three cards in a row do it. A buyer can't tell what they get, how long it takes, or what it costs.

**6. Decoration with no relationship to content.** Perspective grid floor, six floating wireframe cubes, starfield, cyan glow on everything. It's a mood, not an argument. None of it says "Minecraft" (the grid is generic synthwave; the "voxels" are isometric wireframes, not blocks).

**7. "Full-Stack" for a Minecraft dev.** Borrowed web-dev buzzword. Your GitHub bio does it too. It makes you sound like a bootcamp grad rather than a server engineer.

**8. Identical section skeleton.** Every block is `h2` → one-line `.sub` → grid of 3 cards. After the second one the page is skimmable to the point of having no information.

**9. The "AI SaaS card" micro-labels.** All-caps letter-spaced pill badges reading `CLIENT PROJECT` / `BUILT BY ME`, plus chips. These read as generated.

### The irony

Your CNMB ARENA repo contains this:

> 4 interactive role stands · Slayer (Sharpness III Diamond), Hunter (Netherite Spear + Speed I), Tanker (Mace + Resistance I, +4 Hearts) · custom entity holograms · boss-bar match timer · `/scriptevent` builders · 10-minute timer ending in a sealed castle finale with iron-barred gates

That is *fantastic* portfolio material — specific, technical, checkable, memorable. **None of it is on the website.** The one project page says "Tag team match system with a custom behavior pack and resource pack." You have the good version already written, in the README, one click away, and you didn't use it.

The problem isn't that the site looks AI-made. It's that the site is *generic while the work is specific.*

---

## 3. What's actually broken

### P0 — real bugs

**The sticky header eats your anchor targets.**
`header` is `position:sticky` with 38px logo + 14px padding = **67px tall** (incl. border), but there's no `scroll-padding-top` or `scroll-margin-top` anywhere in the file. Every in-page link — "See my projects", "Contact", the logo's `#top` — lands with the heading hidden underneath the header.

```css
html{scroll-behavior:smooth;scroll-padding-top:80px}
```

**Your headline typing line wraps on most phones.**
`const focus = 'Minecraft Bedrock';` is 34 characters. JetBrains Mono advance width is exactly `0.6em`, so at the mobile size (`clamp` bottoms out at 16px) that string is **326px wide**. Available width at a 360px viewport is `360 − 2×5vw = 324px`. It wraps by two pixels, and the blinking `<i>` cursor jumps to line 2 mid-word. `min-height:1.7em` only reserves one line, so the hero shifts.

```css
.type{white-space:nowrap;overflow:hidden;text-overflow:clip}
```
…or shorten the longest phrase, or drop the clamp floor to 14px.

**No endstop for the typing animation on tab-blur.** Not a bug exactly, but `setTimeout` chains keep running in background tabs. Trivial, but free to fix.

### P1 — performance

You have **four independent full-viewport animated layers stacked**, plus a backdrop blur:

1. `<canvas>` — `requestAnimationFrame` loop, never pauses, clears + redraws the whole viewport every frame, forever, even when the tab is hidden or scrolled past.
2. `.vox-floor` — animates `background-position` on a **200%-wide element**. `background-position` is not compositor-friendly: it repaints a 3840×70vh layer every frame for 7s, forever.
3. Six `.vox-fl` SVGs — animating `transform` while carrying `filter: drop-shadow(...)`, so the filter re-rasterises each frame. One is 200px.
4. `.vox` — another fixed full-screen element with three radial gradients.

…all of it *behind* a `backdrop-filter: blur(8px)` sticky header, so every scroll frame forces a re-blur of animated content. This will scroll-jank on mid-range Android and drain battery on mobile. Fixes:

```js
// pause canvas when hidden or off-screen
document.addEventListener('visibilitychange',()=>{ if(document.hidden) cancelAnimationFrame(raf); else raf=requestAnimationFrame(draw); });
// or simply skip the rAF entirely on small screens
```
```css
@media (max-width:700px){ .vox-floor{animation:none} .vox-fl{animation:none} }
.vox-floor{will-change:transform} /* animate translateY on the grid, not background-position */
```

**Fonts.** Orbitron 700 + 900 and JetBrains Mono 400 + 600 = 4 weights, 2 families, fetched from `fonts.googleapis.com` as a **render-blocking stylesheet** in `<head>`. On a cold mobile connection this is typically 300–600ms of blocked first paint, then swap-shift. Self-host two WOFF2 subsets, or cut to one family.

**Images.** 315 KB of JPEG for two screenshots, served at 1280×660 but displayed at ~550px wide (`max-width:1180 / 2 cols`). No WebP/AVIF, no `srcset`. Should be ~40 KB total.

| file | size | note |
|---|---|---|
| `breeze-bedrock.jpg` | 147 KB | 1280×660, no responsive variants |
| `cnmb-arena.jpg` | 167 KB | same |
| `dev-jhnslcc-logo.png` | **470 KB** | 512×512, only used as `apple-touch-icon` and `og:image` |
| `dev-jhnslcc-logo-small.png` | **23 KB** | 96×96 favicon → should be ~2 KB |

The 512² logo being your `og:image` is a separate problem — see below.

### P1 — social & SEO infrastructure missing

None of these exist in the file:

- `og:type`, `og:url`, `og:site_name`, `og:image:width/height/alt`, `twitter:card` → when someone pastes your link into Discord (your main channel!), the preview is uncontrolled. Discord needs `og:image` at **1.91:1**; you're feeding it a **512×512 square**, so it renders as a small letterboxed thumbnail instead of a full-width card. Make a 1200×630 PNG.
- `<link rel="canonical">`
- `<meta name="theme-color">` and `color-scheme:dark` → missing both, so mobile browser chrome stays white against your near-black page, and native scrollbars render light.
- `robots.txt`, `sitemap.xml`, `404.html` → all absent.
- **JSON-LD `Person` / `ProfessionalService` schema** → zero structured data, so you're invisible to entity search.
- No `favicon.ico` fallback (browsers and some crawlers still request it → 404s).

### P2 — accessibility polish

- **No skip link.** With a sticky header and 6 nav targets, keyboard users tab through the logo + 3 links every visit.
- **Mobile nav deletes the navigation.** `@media(max-width:700px){nav a.hide{display:none}}` — below 700px the *only* nav item left is "Contact". Services and Projects become unreachable except by scrolling. No hamburger, no menu. Fix: keep the links, shrink the type, or add a real toggle.
- **Service icons announce twice.** `<svg class="ico" role="img" aria-label="Plugin icon">` sits directly before `<h3>Plugin development</h3>`, so a screen reader says "Plugin icon, Plugin development." These are decorative — use `aria-hidden="true"`.
- **Alt text is over-written.** `alt="CNMB ARENA waiting lobby showing 1 of 2 players joined and a role boost message"` — inside a link that already says "CNMB ARENA … View the code on GitHub". The link's accessible name becomes a paragraph.
- **Inconsistent clickability.** The Breeze Bedrock card is a `<div>` but gets the same hover glow (`border-color`, `box-shadow`) as the clickable CNMB card. It looks interactive, isn't. Your only *client* project is the one nobody can click.
- **Reduced-motion is read once** at load (`matchMedia(...).matches`); toggling the OS setting later doesn't take effect.

---

## 4. The real problem: it's not a portfolio, it's a business card

**236 visible words.** For a commission page that's starving. And the words you do have answer none of the questions a buyer actually has.

What's missing, roughly in order of cost-to-you:

**1. Your flagship skill has zero proof.** Your bio and site both lead with **Endstone / Python plugins**. Neither of your two showcased projects is an Endstone plugin — CNMB is `@minecraft/server` Script API in JavaScript. There is no public Endstone repo. So the thing you're selling hardest is the thing a client cannot verify. Publish one small Endstone plugin (even 150 lines — a shop, a lobby manager, a kit system) with a README and a screenshot. That single repo is worth more than any redesign.

**2. No prices, no scope, no timeline.** `Pricing: quote per task` is the least useful thing on the page. Buyers self-select out when they can't estimate. Even "from $25 / small plugin, 2–4 days" converts better and filters tyre-kickers.

**3. No process.** What happens after "hi"? Deposit? Revisions? Source files handed over? Support window? A 4-step "how I work" strip answers the questions that kill deals in DM.

**4. No proof of outcome.** No player counts, no uptime, no "server ran 200 concurrent for 3 months," no testimonial, no client name (or "a 40k-member Bedrock network" if NDA'd). No dates on the projects — a reader can't tell if these are from last month or 2019.

**5. Contact friction.** `Copy Discord: DEV_JHNSLCC` → then the user has to open Discord, find you, paste. That's 4 steps to say hello. A 3-field form (platform / what you need / deadline — literally the text above it) landed in Discord webhook or email removes all of it. And a plain `mailto:` in the source means your address is already getting scraped.

**6. One page, no depth.** Every project deserves its own page — CNMB especially, since the README content already exists. That's how you get search traffic ("minecraft bedrock tag team plugin") and how you fix the thinness.

**7. No trademark notice.** You're publicly selling Minecraft services. Add, in the footer: *"Not affiliated with Mojang Studios or Microsoft. Minecraft is a trademark of Mojang Synergies AB."* One line, removes a real (if small) legal exposure, and reads professional.

**8. The domain.** `jhnslcc-studio.github.io` is unmemorable in a Discord DM and gives you no control over headers, redirects, or caching. A $10 `.dev` or `.gg` pays for itself in the first commission.

---

## 5. If you only do five things

1. **Rewrite the H1** to a noun phrase that names the job: *"Minecraft Bedrock server development"* — keep the slogan as a small kicker if you love it. (5 min, biggest SEO + clarity win on the page.)
2. **Delete or fill the fake `stats` row** — real numbers or nothing. (5 min.)
3. **Add `scroll-padding-top:80px`** and the `white-space:nowrap` fix. (2 min, two actual bugs gone.)
4. **Write a real CNMB case study** using your own README — the role stands, the timer, the sealed-castle finale, the `/scriptevent` builders. This is the single highest-leverage change on this list.
5. **Publish one Endstone plugin + a 1200×630 `og:image`.** Covers the credibility gap and makes every Discord share look intentional.

Then: strip one font, pause the canvas, convert images to WebP, add the meta tags + JSON-LD, kill the mobile nav hole.

---

## 6. What I'd change in the design, concretely

Not a redesign — three moves that break the template look while keeping the identity:

- **One font, not two.** Keep JetBrains Mono for the whole thing (it fits "developer who writes code"), or keep a display face and lose the mono. Orbitron + mono is the tell; mono alone reads intentional and technical.
- **Add one human element.** Your face, a claw clip of the arena running, or a real screenshot of the sealed-castle finale. There is currently zero evidence a person is behind this — that's what makes it feel generated.
- **Swap the generic synthwave for something literally Minecraft.** The isometric wireframe cubes could be *actual voxel blocks* — grass/dirt/stone isometric blocks, blocky grid instead of a flat perspective plane. Same effort, instantly on-brand, and no longer looks like every AI SaaS hero.

---

*Audit notes only — nothing in this repo was modified, and I made no changes to `jhnslcc-studio/jhnslcc-studio.github.io`.*
