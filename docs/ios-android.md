# iOS + Android from one web codebase — Capacitor, verified here

Installed 2026-11-10 because forgeQueue (`forgequeue.8rec.com`) turned out to be a hosted
credit-metered CI service, not something installable. This is the free equivalent: the same
Capacitor project structure those services build from, plus a GitHub Actions workflow that
uses GitHub's own Apple hardware.

## What was actually installed

| Package | Version | Licence |
|---|---|---|
| `@capacitor/core` | 8.6.2 | MIT |
| `@capacitor/cli` | 8.6.2 | MIT |
| `@capacitor/ios` | 8.6.2 | MIT |
| `@capacitor/android` | 8.6.2 | MIT |

Plus the two platform projects, generated and **committed** (`site/ios/` 327 KB,
`site/android/` 435 KB, 93 files):

```
site/capacitor.config.ts
site/ios/App/App.xcodeproj          ← open in Xcode
site/android/app/build.gradle       ← open in Android Studio
```

## Verified in this workspace

`npx cap add ios` → `[success] ios platform added!` · `npx cap add android` →
`[success] android platform added!` · with a throwaway `out/index.html`,
`npx cap sync` → `✔ copy ios` · `✔ update ios` (writes `Package.swift`) · `✔ copy web` ·
`✔ update web` → `index.html` landed in **both** `ios/App/App/public/` and
`android/app/src/main/assets/public/`. So the whole packaging step is proven; only the
native compilers are missing (no Xcode, no Android SDK here — and neither is installable
in this sandbox).

## Config

`webDir: 'out'` — Next.js static export (`output: 'export'` in `next.config`) writes there.
`server.url` is driven by `CAP_SERVER_URL` so a device can live-reload against your laptop:
`CAP_SERVER_URL=http://192.168.x.x:3000 npm run dev`. `androidScheme: 'https'` keeps secure
contexts working (needed for clipboard, camera, service workers).

## The build pipeline that replaces forgeQueue

`.github/workflows/mobile-builds.yml` — manual dispatch or a `v*` tag.

- **Android** on `ubuntu-latest`: Node 22 → `npm ci` → build → `npx cap sync android` →
  `./gradlew assembleDebug` → APK, and `bundleRelease` → AAB when keystore secrets exist.
- **iOS** on `macos-latest` (a real Apple machine): Node 22 → build → `npx cap sync ios` →
  `xcodebuild ... CODE_SIGNING_ALLOWED=NO` → unsigned `.app` artifact.

Cost comparison, honestly: GitHub gives **free macOS minutes on public repos** and 2,000
min/month on private. forgeQueue sells credits, manually provisioned, in early access. Same
underlying idea — someone else's Mac — without a new vendor or a balance to top up.

**What no service removes:** Apple's **$99/year** developer account and App Store review.
A signed `.ipa` needs a certificate, a provisioning profile, and a team ID in secrets; the
workflow has the commented block for exactly that.

## What is still genuinely missing

There is **no app yet** — `site/` has no `src/app/` and no `next.config`. Capacitor is
packaging a placeholder. Order of work:

1. Build the costing planner's web app (rate library → quote screen → PDF/PNG).
2. Add `output: 'export'` to `next.config` and a `public/` manifest → PWA installs today.
3. `npx cap sync` → open Xcode/Android Studio → run on a device.
4. Only then wire signing and the store listings.

Multi-platform multiplies **testing surfaces**, not code. Three broken apps are worse than
one working web app.

## Licensing note

Capacitor is MIT. The generated `ios/` and `android/` projects contain no third-party
binary blobs — they are project files, safe to commit and ship. Build outputs
(`out/`, `.gradle/`, `build/`, `Pods/`, `DerivedData/`) are gitignored.
