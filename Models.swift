import Foundation

// MARK: - Step kinds

enum StepKind: String, Codable {
    case manual        // user does it; we give exact values + links
    case apiBundleID   // automated: register bundle ID via App Store Connect API
    case apiCapability // automated: enable a capability (IAP)
    case apiAppRecord  // automated: create the app record
    case apiKeySetup   // the in-app credential entry step
}

// MARK: - Micro-step

struct MicroStep: Identifiable, Codable, Hashable {
    var id: String
    var title: String
    var instruction: String
    var exactValue: String?   // shown in a copy box
    var linkLabel: String?
    var linkURL: String?
    var kind: StepKind

    init(_ id: String, _ title: String, _ instruction: String,
         exactValue: String? = nil, linkLabel: String? = nil, linkURL: String? = nil,
         kind: StepKind = .manual) {
        self.id = id; self.title = title; self.instruction = instruction
        self.exactValue = exactValue; self.linkLabel = linkLabel; self.linkURL = linkURL
        self.kind = kind
    }
}

// MARK: - Stage

struct ReleaseStage: Identifiable, Codable, Hashable {
    var id: String
    var title: String
    var subtitle: String
    var steps: [MicroStep]
}

// MARK: - The pipeline: every stage broken into ADHD-sized steps

enum PipelineData {
    static let stages: [ReleaseStage] = [
        ReleaseStage(
            id: "connect", title: "1 · Connect",
            subtitle: "One-time setup. Do this once, never again.",
            steps: [
                MicroStep("c1", "Join the Apple Developer Program",
                          "Enroll as an Individual. $99/year. Nothing ships without this — it's the toll booth.",
                          linkLabel: "Enroll at developer.apple.com",
                          linkURL: "https://developer.apple.com/programs/enroll/"),
                MicroStep("c2", "Create an Admin API key",
                          "App Store Connect → Users and Access → Integrations → App Store Connect API → Team Keys → tap +. Set access level to Admin.",
                          exactValue: "Access level: Admin",
                          linkLabel: "Open API keys page",
                          linkURL: "https://appstoreconnect.apple.com/access/api"),
                MicroStep("c3", "Download the .p8 file",
                          "You get exactly ONE download. Save it somewhere safe — Apple never shows it again. If you lose it, you revoke and make a new key.",
                          exactValue: "AuthKey_XXXXXXXXXX.p8"),
                MicroStep("c4", "Paste credentials into ReleaseBuddy",
                          "Enter your Key ID, Issuer ID, and the .p8 contents on the API Key Setup tab. They go straight into your Mac Keychain — never into a file, never into chat.",
                          kind: .apiKeySetup),
            ]),
        ReleaseStage(
            id: "bundle", title: "2 · Bundle ID",
            subtitle: "Your app's permanent ID. Pick carefully — it can never change.",
            steps: [
                MicroStep("b1", "Choose your bundle ID",
                          "Reverse-DNS, all lowercase, no spaces. Convention: com.yourname.appname. This is forever — typos here haunt you.",
                          exactValue: "com.yourname.appname"),
                MicroStep("b2", "Register it",
                          "Hit Run and ReleaseBuddy registers it via the App Store Connect API. Or do it by hand at the link.",
                          linkLabel: "Register manually",
                          linkURL: "https://developer.apple.com/account/resources/identifiers/list",
                          kind: .apiBundleID),
            ]),
        ReleaseStage(
            id: "caps", title: "3 · Capabilities",
            subtitle: "Flip the switches your app needs.",
            steps: [
                MicroStep("p1", "Enable In-App Purchase",
                          "Hit Run — ReleaseBuddy enables the IAP capability on your bundle ID via the API. Needed if you ever sell anything inside the app, including 'remove ads'.",
                          kind: .apiCapability),
                MicroStep("p2", "Anything else?",
                          "Push Notifications, Sign in with Apple, Game Center — enable in Xcode under Signing & Capabilities AND here in the identifier. One checkbox each; do them now so you don't discover a missing one at 2am before submission."),
            ]),
        ReleaseStage(
            id: "record", title: "4 · App Record",
            subtitle: "Create the app's listing in App Store Connect.",
            steps: [
                MicroStep("r1", "Pick your app name, SKU, and locale",
                          "Name: what users see (30 chars max). SKU: your private code, never shown — use something like APPNAME001. Primary locale: English (U.S.) unless you know otherwise.",
                          exactValue: "SKU example: ACEOFACES001"),
                MicroStep("r2", "Create the record",
                          "Hit Run — ReleaseBuddy creates the app in App Store Connect via the API. This is the moment your app officially exists.",
                          kind: .apiAppRecord),
            ]),
        ReleaseStage(
            id: "build", title: "5 · Build & Upload",
            subtitle: "Xcode does the heavy lifting. You just click in order.",
            steps: [
                MicroStep("u1", "Archive in Xcode",
                          "Open your project. Top menu: Product → Archive. Wait for the build to finish. Go make tea — this takes minutes.",
                          exactValue: "Xcode → Product → Archive"),
                MicroStep("u2", "Distribute to App Store Connect",
                          "In the Organizer window: Distribute App → App Store Connect → Upload. Accept the defaults. Enter your Apple ID password if asked.",
                          exactValue: "Organizer → Distribute App → App Store Connect → Upload"),
                MicroStep("u3", "Wait for processing",
                          "Builds take 10–60 minutes to process. Apple emails you when it's ready. Do NOT submit until the build shows up under TestFlight — it isn't real until then."),
            ]),
        ReleaseStage(
            id: "meta", title: "6 · Screenshots & Metadata",
            subtitle: "The part everyone underestimates. Front-load it.",
            steps: [
                MicroStep("m1", "Capture screenshots",
                          "You need these sizes (points, not pixels, but capture at device resolution): 6.7\" (1290×2796), 6.5\" (1242×2688), 5.5\" (1242×2208), iPad 13\" (2048×2732). Simulator screenshots are fine — no device needed.",
                          exactValue: "1290×2796 · 1242×2688 · 1242×2208 · 2048×2732"),
                MicroStep("m2", "Description + keywords",
                          "App Store Connect → your app → App Information. Description: what it does in plain words. Keywords: comma-separated, 100 chars max, no app name repeats.",
                          linkLabel: "Open App Store Connect",
                          linkURL: "https://appstoreconnect.apple.com/apps"),
                MicroStep("m3", "Privacy policy + support URLs",
                          "Apple REJECTS without these two URLs. They can be dead-simple pages — GitHub Pages is free and fine. Fill them in under App Information.",
                          exactValue: "https://yourname.github.io/appname/privacy"),
            ]),
        ReleaseStage(
            id: "submit", title: "7 · Submit for Review",
            subtitle: "Almost there. Four clicks and a deep breath.",
            steps: [
                MicroStep("s1", "Add a version and pick the build",
                          "App Store → iOS App → + Version. Under Build, tap + and select your processed build.",
                          exactValue: "e.g. version 1.0"),
                MicroStep("s2", "Export compliance",
                          "The scary legal question. For most apps the answer is NO — your app doesn't use custom encryption. (HTTPS/TLS doesn't count.)",
                          exactValue: "Does your app use encryption? → No"),
                MicroStep("s3", "Content rights + age rating",
                          "Confirm you own the content, then fill the age-rating questionnaire honestly. One wrong answer here = a rejection email.",
                          exactValue: "No objectionable content → 4+"),
                MicroStep("s4", "Submit for Review",
                          "Top right: Submit for Review. Status flips to 'Waiting for Review'. Typical wait: 24–48 hours. You did it — the ball is in Apple's court now."),
            ]),
        ReleaseStage(
            id: "liftoff", title: "8 · Liftoff",
            subtitle: "Watch the status. Handle rejection like a pro.",
            steps: [
                MicroStep("l1", "Watch the status",
                          "Waiting for Review → In Review → Pending Developer Release (or Ready for Sale). If you chose manual release, YOU tap the final Release button.",
                          exactValue: "Status page: App Store Connect → your app → App Store"),
                MicroStep("l2", "If rejected: don't panic",
                          "Read the Resolution Center note carefully — it's usually ONE specific thing (metadata, a missing URL, a crash on their device). Fix exactly that, bump the build number, re-upload, resubmit. Rejections are normal; even big studios eat them.",
                          exactValue: "Fix one thing → bump build # → resubmit"),
            ]),
    ]

    static var allSteps: [MicroStep] { stages.flatMap(\.steps) }
}
