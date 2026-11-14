# Web-dev skills installer — copy-paste for a friend's AI

Source: `jusnie/Tools-Skills`, branch `arena/6265089e-animation`, path `.claude/`.
**11 web-development skills + 4 subagents · 2,111 files · 34 MB payload (~39 MB on disk; 2,111 small files) · sparse clone, so you never pull the repo's 162 MB.**

Paste the block in **Part A** into your friend's AI (Claude Code, Cursor, or anything with shell access). It asks one question — project-level or user-level — then installs and verifies.

---

## Part A — the prompt (copy everything inside)

````text
You are installing a web-development skill library into this machine. Follow these steps
exactly. Do not modify any file outside .claude/. Do not invent skill content — everything
comes from the repository below.

SOURCE
  repo:   https://github.com/jusnie/Tools-Skills
  branch: arena/6265089e-animation
  paths:  .claude/skills/  and  .claude/agents/

SKILLS TO INSTALL (11)
  design-taste-frontend, impeccable, hallmark, ui-ux-pro-max, modern-web-guidance,
  frontend-checklist, scroll-craft, react-kino, oil-motion, ui-sdk, mapcn

STEP 0 — ask me one question, then wait:
  "Install project-level (./.claude, this repo only) or user-level (~/.claude, every
   project)?" Default to project-level if I don't answer.

STEP 1 — check prerequisites. Report, do not fail silently:
  git --version        (required)
  node --version       (optional; design-taste's finish-gate needs Node 18+)
  python3 --version    (optional; only oil-motion needs Python 3.10+, Pillow, ffmpeg)
If git is missing, stop and tell me to install git. Do not try a manual file-by-file
download of 2,111 files.

STEP 2 — sparse clone into a temp dir, excluding the 96 MB of video skills:
  git clone --depth 1 --filter=blob:none --sparse \
    -b arena/6265089e-animation \
    https://github.com/jusnie/Tools-Skills.git /tmp/tools-skills-install

  cd /tmp/tools-skills-install && git sparse-checkout set --no-cone \
    '/.claude/agents/' \
    '/.claude/skills/design-taste-frontend/' \
    '/.claude/skills/impeccable/' \
    '/.claude/skills/hallmark/' \
    '/.claude/skills/ui-ux-pro-max/' \
    '/.claude/skills/modern-web-guidance/' \
    '/.claude/skills/frontend-checklist/' \
    '/.claude/skills/scroll-craft/' \
    '/.claude/skills/react-kino/' \
    '/.claude/skills/oil-motion/' \
    '/.claude/skills/ui-sdk/' \
    '/.claude/skills/mapcn/'

STEP 3 — copy into the target from Step 0 (create dirs if absent, never overwrite a
skill that already exists without asking):
  mkdir -p <TARGET>/.claude/skills <TARGET>/.claude/agents
  cp -R /tmp/tools-skills-install/.claude/skills/* <TARGET>/.claude/skills/
  cp -R /tmp/tools-skills-install/.claude/agents/* <TARGET>/.claude/agents/

  If your tool reads .agents/skills/ instead of .claude/skills/, copy to that path too.

STEP 4 — verify, and show me the result as a table:
  a) every installed folder contains a SKILL.md
  b) each SKILL.md starts with YAML frontmatter containing `name:` and `description:`
  c) count: expect 11 skill folders and 4 agent .md files
  d) preserve every LICENSE and LICENSE-*.txt file that came with a skill
  e) print total files and total size
If any check fails, say which skill is broken and stop.

STEP 5 — clean up: rm -rf /tmp/tools-skills-install

STEP 6 — report, in this format:
  | Skill | Version | License | Purpose (one line) | Files |
  plus one line: "Invoke with: <how to trigger a skill in my tool>"

RULES
  - These skills are third-party MIT / Apache-2.0 works. Keep their LICENSE files and do
    not strip attribution. Do not relicense them as your own.
  - design-taste-frontend declares a Stop hook that shells out to scripts/gate.mjs. Only
    enable it if Node 18+ is present; otherwise tell me the hook is disabled.
  - Do not run any skill's install script, npm install, or pip install without asking.
  - Do not delete or rewrite anything in <TARGET> outside .claude/.
  - If the clone or sparse-checkout fails twice, stop and report the exact error.

STEP 7 — after installing, prove one skill works: open
  <TARGET>/.claude/skills/design-taste-frontend/SKILL.md
Its `description:` is a YAML folded block (the line after `description: >-`), so quote the
first sentence of that text — it begins "tasteskill 2.5.1" — back to me.
````

---

## Part B — what gets installed

### Core design & build — install all six

| Skill | Version | License | What it does | Files / size |
|---|---|---|---|---|
| **design-taste-frontend** | tasteskill 2.5.1 | MIT | "The anti-slop frontend skill." Builds sites at figma.com / x.ai level: one system, plain copy in its own voice, one section per screen, real photography, a hero entrance and one or two dealt moments — with a checker that enforces it in a real browser | 1,566 / 24 MB |
| **impeccable** | 4.9.0 | Apache-2.0 | Design-director skill with 44 playbooks: `shape`, `audit`, `critique`, `polish`, `typeset`, `layout`, `colorize`, `harden`, `optimize`, `animate`, `bolder`, `quieter`, `distill` | 59 / 2.2 MB |
| **ui-ux-pro-max** | — | MIT | Searchable local design data: 79 styles, 192 product palettes, 74 font pairings, 119 UX guidelines, 105 icons, 17 GSAP presets, 25 chart types, 22 stacks | 71 / 3.5 MB |
| **hallmark** | 2.0.0 | MIT | "Designed, not generated": a hard floor against model defaults, a dealt direction so consecutive builds don't converge. Modes: build, `redesign <path>`, `audit <path>` | 137 / 1.7 MB |
| **modern-web-guidance** | GoogleChrome | Apache-2.0 | Modern platform best practices: dialogs, popovers, container queries, view transitions, scroll-driven animations, CWV, image optimization, forms, accessibility. Pinned by hash in `skills-lock.json` | 211 / 1.9 MB |
| **frontend-checklist** | frontendchecklist.io | MIT | The 386-rule Front-End Checklist corpus as an evidence-first audit checklist (offline-readable; the MCP server it assumes is optional) | 3 / 22 KB |

### Motion & scroll — install if the site needs motion

| Skill | License | What it does | Files / size |
|---|---|---|---|
| **scroll-craft** | MIT | Premium scroll-driven landing pages: visitor journey, page grammar, emotional peak, layered hero with independent planes, separate mobile composition | 20 / 303 KB |
| **react-kino** | MIT | Portable React scroll stories via `react-kino/story` + `studio` storyboard editor, validated with `kino validate` / `kino doctor` | 2 / 3 KB |
| **oil-motion** | MIT | Turns AI-generated video / sequence frames into scroll-, pointer-, drag- or audio-driven web animation. Needs Python 3.10+, Pillow, ffmpeg | 24 / 247 KB |

### Component-level — only if the friend's stack matches

| Skill | License | What it does | Files / size |
|---|---|---|---|
| **ui-sdk** | Apache-2.0 (vercel-labs) | Unstyled accessible UI behaviors — keyboard, focus, selection, dismiss, popups, DnD, ARIA — for React/Vue/Svelte/Solid/web components, with `createAgent` + WebMCP agent tools | 9 / 86 KB |
| **mapcn** | MIT | shadcn-style map components on MapLibre GL + Tailwind: markers, popups, routes, arcs, GeoJSON, choropleth, clusters, globe, light/dark theming | 5 / 23 KB |

### Subagents (`.claude/agents/`) — 4 files, 34 KB

`impeccable-asset-producer` · `impeccable-documenter` · `impeccable-finish-reviewer` · `impeccable-manual-edit-applier`

### Deliberately excluded

| Excluded | Why |
|---|---|
| `directing-stickman-videos` (60 MB) | Video/film pipeline, not web |
| `papercut-*` ×9 | Explainer-video production |
| `auto-ontology-mcp` (456 KB) | MCP server, not UI |
| `affine` | Its own SKILL.md says it's "a reference note, not a component library" |

Excluding these is what keeps the install at a 34 MB payload instead of 96 MB.

---

## Part C — notes

- **Scope.** Project-level (`./.claude`) keeps it per-repo; user-level (`~/.claude`) makes every project see it. Claude Code reads both; `.agents/skills/` is the alternative path some tools use.
- **No `node_modules`, no build step.** Skills are Markdown + static assets + two `.mjs` checkers. Nothing to compile.
- **The gate is the good part.** `design-taste-frontend/scripts/gate.mjs` is a real browser checker — it's what turns "looks generic" into a pass/fail. Node 18+ to use it.
- **Licenses travel with the files.** MIT for design-taste, hallmark, ui-ux-pro-max, frontend-checklist, scroll-craft, react-kino, oil-motion, mapcn; Apache-2.0 for impeccable, modern-web-guidance, ui-sdk. Keep the `LICENSE*` files when redistributing — the installer instructs the AI to preserve them.
- **Runtime:** 34 MB payload / ~39 MB on disk · 2,111 files · sparse clone of one branch. First clone pulls only those paths (`--filter=blob:none --sparse`), not the repo's 162 MB of renders.
