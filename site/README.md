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
| Motion / polish | `tailwindcss-animate`, `embla-carousel-react`, `sonner`, `vaul` | latest |
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
