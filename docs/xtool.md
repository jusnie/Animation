# xtool — a real "no Mac" iOS toolchain, and why it still can't run here

[xtool](https://github.com/xtool-org/xtool) · **MIT** · **15,482★** · Swift · pushed 2026-11-09 ·
"Cross-platform Xcode replacement. Build and deploy iOS apps with SwiftPM on Linux, Windows,
macOS."

This is not a CI service — it is actual software, and it is the most interesting thing in
this whole install run. If it works, the $99/year-plus-a-Mac story changes shape.

## What it does

From its own `--help`:

```
setup     Set up xtool for iOS development
auth      Manage Apple Developer Services authentication
sdk       Manage the Darwin Swift SDK
new       Create a new xtool SwiftPM project
dev       Build and run an xtool SwiftPM project
ds        Interact with Apple Developer Services
devices   List devices     install/uninstall/launch   (over USB)
```

- Builds a **SwiftPM** package into an iOS `.app` using the Darwin Swift SDK
- **Signs and installs** to a physical device over USB via `usbmuxd`/libimobiledevice
- Talks to Apple Developer Services programmatically: register bundle IDs, provisioning
  profiles, App ID capabilities (same jobs forgeQueue charges credits for)
- `XKit` / `XToolSupport` usable as SwiftPM dependencies, so it's a library too
- Ships a **Dockerfile** based on `swift:6.4.2-jammy` and builds to an **AppImage**

## Why it cannot be installed in this workspace

Three hard blockers, all verified:

| Requirement | Status here |
|---|---|
| Swift 6.4 toolchain | **absent** — `swift: command not found` |
| `swift.org` / `download.swift.org` to fetch it | **000** — blocked, as is every non-allowlisted host |
| `usbmuxd` (to reach a device) | **not in Debian's repos** — `E: Unable to locate package usbmuxd` |
| Docker (the documented path) | no Docker in this sandbox |
| A physical iPhone on USB | not applicable to a sandbox |

So even with root, apt, and a GitHub clone — all of which work — the toolchain cannot be
obtained. `swiftlang` is not an apt package, `swiftlang` on PyPI is 404, and the official
tarball host is blocked.

## The constraint that matters even on a real machine

**xtool consumes SwiftPM packages. Capacitor produces an Xcode project.**

Reading the source: `Sources/XToolSupport/DevCommand.swift` builds a SwiftPM `Planner` and
either `Packer` → `.app`, or `XcodePacker` → a *generated* `.xcodeproj` for editors. There
is no `xtool build MyApp.xcodeproj` path. The `XcodeProjects` module parses pbxproj, but it
serves `xtool new`/`xtool dev`, not arbitrary projects.

That means the installed Capacitor setup cannot be handed to xtool. Two ways to square it:

1. **Use the GitHub Actions `macos-latest` workflow already in this repo** — it builds
   `site/ios/App.xcodeproj` with real Xcode, free. For a Capacitor app, this is the only
   path that works without a Mac.
2. **Use xtool for a native SwiftUI app instead** — a genuinely different product from a
   wrapping of the web app. `xtool new`, write SwiftUI, `xtool dev`, `xtool install`. That
   is a *new app*, not this one.

## When xtool is the right answer

- You want to write **Swift/SwiftUI** and have no Mac. Then it's the only serious open option.
- You want to **register bundle IDs / capabilities / signing** from scripts on Linux.
- You want a free, USB-free way to install builds on a device for testing.
- You're on Linux long-term and want one toolchain for build + sign + install.

When it is *not*: a Next.js/Capacitor app. There the Xcode path is the right one, and
GitHub's `macos-latest` gives it to you for free.

## Upstream notes worth keeping

- Binary named `xtool` + `xtoold`; docs at `xtool.sh`.
- Linux users need `libimobiledevice-utils` for `ideviceinfo`-style debugging.
- Docker path needs the host's `usbmuxd` forwarded:
  `socat -dd TCP-LISTEN:27015,range=127.0.0.1/32,reuseaddr,fork UNIX-CLIENT:/var/run/usbmuxd`
- Windows users go through WSL + usbipd (or relay via iTunes).
- Full source read at `/tmp/xtool` (23 MB, swift-tools-version 6.2, deps: xtool-core,
  SwiftyMobileDevice, swift-rcodesign, swift-crypto, swift-certificates, swift-argument-parser,
  swift-openapi-generator).
