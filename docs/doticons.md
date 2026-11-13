# doticons — installed, with the export naming gotcha

[eduardconstantin/doticons](https://github.com/eduardconstantin/doticons) · MIT · 78★ ·
"A collection of versatile and visually appealing dot icons crafted in SVG format."

A **dot-matrix icon set**: 244 icons, each glyph built from a grid of dots instead of
strokes. Two sizes ship, 16 px and 32 px, as React components.

## Installed

```bash
cd site && npm i doticons@0.9.0
```

`doticons@0.9.0` (MIT, 7.1 MB unpacked, peer `react >= 17`). Entry points:

```tsx
import { AlarmDoticon, CirclePlayDoticon, HeartDoticon } from "doticons/32";
import { AlarmDoticon as SmallAlarm } from "doticons/16";
```

Verified with esbuild: a three-icon import bundles to 158 KB, 0 errors. Only the icons
you import are pulled in — it is not a barrel that forces the whole set.

## The gotcha that cost a build

**Every export is suffixed `Doticon`.** The file names are `alarm.svg` /
`AlarmDoticon.js`, but the component is `AlarmDoticon`, and:

```tsx
import { Alarm } from "doticons/32";      // ✘ No matching export
import { AlarmDoticon } from "doticons/32"; // ✔
```

`Play` does not exist either — the play glyph is **`CirclePlayDoticon`**. To list what
does exist:

```bash
grep -oE "[A-Za-z]+Doticon" site/node_modules/doticons/32/index.js | sort -u
```

## Why it is here

The rest of the icon stack is **lucide-react** (thin strokes, line art). doticons is the
opposite texture — chunky dots — which is a closer match to a **stick-figure film**
aesthetic than lucide is, and closer than the pixel/sharp sets. It is a *texture*
choice, not a functional one: same job, different grain.

Caveat: 244 icons is a small set. There is no film, reel, clapperboard or subtitle glyph
(nearest: `CirclePlayDoticon`, `CameraDoticon`, `HeartDoticon`). Plan on lucide for
anything semantically specific and doticons for accents and nav.
