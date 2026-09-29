# ReleaseBuddy — Build Guide

A macOS SwiftUI app that releases apps on the App Store without melting your brain.
One micro-step at a time. The robot does the API parts; you get checkboxes and copy-paste values for the rest.

**Provisional name:** ReleaseBuddy · **Bundle ID:** com.luckyclover.releasebuddy
(Change the name any time — it's just a label.)

## What it does (v1)

- **8 stages, ~20 micro-steps:** Connect → Bundle ID → Capabilities → App Record → Build & Upload → Screenshots & Metadata → Submit → Liftoff
- **"YOUR ONE THING" card:** exactly one next step on screen, big. ADHD kryptonite.
- **Automation via the App Store Connect API** (mirrors the `asc-automation` modules):
  - Register bundle ID
  - Enable In-App Purchase capability
  - Create the app record
  - Test-connection ping
- **JWT signing done natively** with CryptoKit (P-256 / ES256) — no third-party dependencies.
- **Credentials in the Mac Keychain only.** Never UserDefaults, never a file.

## Files

| File | What it is |
|---|---|
| `ReleaseBuddyApp.swift` | App entry, sidebar navigation |
| `Models.swift` | `MicroStep` / `ReleaseStage` + the full pipeline data (every baby step, exact value, and link) |
| `PipelineStore.swift` | Progress persistence, draft app details, Keychain-backed credentials |
| `KeychainStore.swift` | Minimal Keychain wrapper |
| `AppStoreConnect.swift` | JWT + API client (bundle IDs, capabilities, apps) |
| `Views.swift` | PipelineView, FocusStepView, SetupView, SettingsView |

## Build it — baby steps

**Step 1.** Open Xcode.

**Step 2.** File → New → Project.

**Step 3.** Choose **macOS** → **App**. Click Next.

**Step 4.** Fill in exactly:
- Product Name: `ReleaseBuddy`
- Organization Identifier: `com.luckyclover`
- Interface: **SwiftUI**
- Language: **Swift**
- Uncheck Core Data, uncheck Tests.

**Step 5.** Save it anywhere (e.g. `~/Projects/ReleaseBuddy`).

**Step 6.** In Finder, drag these 6 files into the Xcode project navigator (drop them on the ReleaseBuddy folder):
`ReleaseBuddyApp.swift`, `Models.swift`, `PipelineStore.swift`, `KeychainStore.swift`, `AppStoreConnect.swift`, `Views.swift`
- Check **"Copy items if needed"**.
- Delete the default `ContentView.swift` Xcode made (ours is inside ReleaseBuddyApp.swift).

**Step 7.** Click the project (top of navigator) → your app target → General → Minimum Deployments → **macOS 14.0**.

**Step 8.** Signing & Capabilities → select your **Team** (your Apple ID). That's it — no extra capabilities needed. Do NOT turn on App Sandbox for v1 (Keychain access is simpler without it; enable sandbox later when distributing).

**Step 9.** Press **⌘R**. The app launches. Go to **API Key Setup** in the sidebar and paste your credentials.

## Getting your API credentials (also in the app)

1. Enroll in the Apple Developer Program: https://developer.apple.com/programs/enroll/ ($99/yr)
2. App Store Connect → Users and Access → Integrations → App Store Connect API → Team Keys → **+** (Admin access): https://appstoreconnect.apple.com/access/api
3. Download the `.p8` — **one download only**, don't lose it.
4. Paste Key ID + Issuer ID + `.p8` contents into the app → **Test connection**.

## Roadmap (not in v1)

- Create App Store version + submit-for-review via API (endpoints exist; UI not built)
- Screenshot capture helper (simulator automation)
- iPhone companion (read-only progress + nudges)
- Sparkle auto-updates for distribution outside the App Store

## Honest limits

- **Not compiled or run here** — no Xcode in this environment. Send build errors back verbatim.
- Uploading the actual `.ipa` still goes through Xcode's Organizer (stage 5 walks you through it click-by-click).
- Review times and rejections are Apple's domain; the app gets you to the Submit button with everything correct, which is where most rejections are born.
