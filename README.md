# ReleaseBuddy

A macOS app that releases apps on the App Store — for people too ADHD for this shit.

It does everything a machine can do by itself (App Store Connect API: bundle IDs,
In-App Purchase capability, app records) and walks you through the manual parts
one tiny checkbox at a time, with copy-paste exact values and links.

## Status

v1 scaffold. **Not yet compiled** — build it in Xcode (see BUILD_GUIDE.md).

## Build

1. Xcode → new macOS App project named `ReleaseBuddy` (SwiftUI, no Core Data)
2. Drag the 6 Swift files in, delete Xcode's default `ContentView.swift`
3. Minimum deployment: macOS 14.0 · add your Team under Signing & Capabilities
4. ⌘R

Full baby-steps: [BUILD_GUIDE.md](BUILD_GUIDE.md)

## Files

| File | What it is |
|---|---|
| `ReleaseBuddyApp.swift` | App entry, sidebar navigation |
| `Models.swift` | The full 8-stage / ~20-step pipeline data |
| `PipelineStore.swift` | Progress persistence, Keychain-backed credentials |
| `KeychainStore.swift` | Minimal Keychain wrapper |
| `AppStoreConnect.swift` | Native ES256 JWT + App Store Connect API client |
| `Views.swift` | Pipeline, focus-step, API key setup, settings views |

## The engine

The macOS app above is the friendly face. Under `engine/` live the backend
automation scripts it wraps — usable standalone from the terminal too.

| Directory | What it is |
|---|---|
| `engine/asc-automation/` | App Store Connect autopilot: registers bundle IDs, enables capabilities (e.g. In-App Purchase), and creates app records via the API. Idempotent modules + `run-all.sh` orchestrator. See its [README](engine/asc-automation/README.md). |
| `engine/release-ring/` | One CLI (`ring.py`) + agent fellowship (preflight, lint, assets, docs, shots, github, publisher, reporter) that carries an app to every major store — Apple, Google, Samsung, Amazon. See its [README](engine/release-ring/README.md). |

## Honest limits

- Credentials live in the Mac Keychain only.
- `.ipa` upload still goes through Xcode's Organizer (the app walks you through it).
- Review times and rejections are Apple's domain.
