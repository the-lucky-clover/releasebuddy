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

## Honest limits

- Credentials live in the Mac Keychain only.
- `.ipa` upload still goes through Xcode's Organizer (the app walks you through it).
- Review times and rejections are Apple's domain.
