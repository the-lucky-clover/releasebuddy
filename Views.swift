import SwiftUI
import AppKit

// MARK: - Pipeline: the checklist with a "ONE THING" focus card

struct PipelineView: View {
    @EnvironmentObject var store: PipelineStore
    @State private var focusStep: MicroStep?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Overall progress
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Release progress")
                                .font(.headline)
                            Spacer()
                            Text("\(store.doneCount) of \(store.totalSteps)")
                                .font(.subheadline).foregroundStyle(.secondary)
                        }
                        ProgressView(value: store.progress)
                            .progressViewStyle(.linear)
                    }
                    .padding()
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 14))

                    // THE ONE THING — ADHD focus: exactly one next step, big.
                    if let next = store.nextStep {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("YOUR ONE THING")
                                .font(.caption).bold()
                                .foregroundStyle(.secondary)
                            Text(next.title)
                                .font(.title2).bold()
                            Text(next.instruction)
                                .font(.body).foregroundStyle(.secondary)
                                .fixedSize(horizontal: false, vertical: true)
                            HStack {
                                Button("Open it") { focusStep = next }
                                    .buttonStyle(.borderedProminent)
                                Text("Step \(store.nextStepIndex + 1) of \(store.totalSteps)")
                                    .font(.caption).foregroundStyle(.secondary)
                            }
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(.yellow.opacity(0.12), in: RoundedRectangle(cornerRadius: 14))
                        .overlay(RoundedRectangle(cornerRadius: 14).stroke(.yellow.opacity(0.5)))
                    } else {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("🎉 All \(store.totalSteps) steps done.").font(.title2).bold()
                            Text("Your app is submitted. Go touch grass — you've earned it.")
                                .foregroundStyle(.secondary)
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(.green.opacity(0.12), in: RoundedRectangle(cornerRadius: 14))
                    }

                    // Stages
                    ForEach(PipelineData.stages) { stage in
                        VStack(alignment: .leading, spacing: 10) {
                            HStack {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(stage.title).font(.headline)
                                    Text(stage.subtitle).font(.caption).foregroundStyle(.secondary)
                                }
                                Spacer()
                                ProgressView(value: store.stageProgress(stage))
                                    .frame(width: 90)
                            }
                            ForEach(stage.steps) { step in
                                StepRow(step: step, focusStep: $focusStep)
                            }
                        }
                        .padding()
                        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 14))
                    }
                }
                .padding()
            }
            .navigationTitle("Release Pipeline")
            .sheet(item: $focusStep) { step in
                FocusStepView(step: step)
                    .environmentObject(store)
                    .frame(minWidth: 560, minHeight: 480)
            }
        }
    }
}

struct StepRow: View {
    @EnvironmentObject var store: PipelineStore
    var step: MicroStep
    @Binding var focusStep: MicroStep?

    var body: some View {
        HStack(spacing: 12) {
            Button {
                withAnimation { store.toggle(step) }
            } label: {
                Image(systemName: store.isDone(step) ? "checkmark.circle.fill" : "circle")
                    .font(.title2)
                    .foregroundStyle(store.isDone(step) ? .green : .secondary)
            }
            .buttonStyle(.plain)

            VStack(alignment: .leading, spacing: 2) {
                Text(step.title)
                    .strikethrough(store.isDone(step))
                    .foregroundStyle(store.isDone(step) ? .secondary : .primary)
                if step.kind != .manual {
                    Text("Automated — the app can do this for you")
                        .font(.caption).foregroundStyle(.blue)
                }
            }
            Spacer()
            Button("Open") { focusStep = step }
                .buttonStyle(.link)
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Focus: one step, full screen, everything it needs

struct FocusStepView: View {
    @EnvironmentObject var store: PipelineStore
    @Environment(\.dismiss) var dismiss
    var step: MicroStep

    @State private var running = false
    @State private var result: String?
    @State private var isError = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(step.title).font(.largeTitle).bold()
                Text(step.instruction)
                    .font(.title3)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)

                if let value = step.exactValue {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("EXACT VALUE — copy it").font(.caption).bold().foregroundStyle(.secondary)
                        HStack {
                            Text(value).font(.body.monospaced()).textSelection(.enabled)
                            Spacer()
                            Button("Copy") {
                                NSPasteboard.general.clearContents()
                                NSPasteboard.general.setString(value, forType: .string)
                            }
                        }
                        .padding()
                        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 10))
                    }
                }

                if let label = step.linkLabel, let urlStr = step.linkURL, let url = URL(string: urlStr) {
                    Link(destination: url) {
                        Label(label, systemImage: "arrow.up.right.square")
                            .font(.headline)
                    }
                    .buttonStyle(.bordered)
                }

                // Automation controls
                if step.kind != .manual && step.kind != .apiKeySetup {
                    automationSection
                }
                if step.kind == .apiKeySetup {
                    Text("Head to the API Key Setup tab in the sidebar — it walks you through it in 3 fields.")
                        .font(.callout).foregroundStyle(.secondary)
                }

                Divider()

                Button(store.isDone(step) ? "Done ✓ — undo?" : "Mark done, show me the next thing") {
                    withAnimation {
                        store.toggle(step)
                        dismiss()
                    }
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .keyboardShortcut(.defaultAction)

                if let result {
                    Text(result)
                        .font(.callout)
                        .foregroundStyle(isError ? .red : .green)
                        .fixedSize(horizontal: false, vertical: true)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background((isError ? Color.red : Color.green).opacity(0.1),
                                    in: RoundedRectangle(cornerRadius: 10))
                }
                Spacer()
            }
            .padding(28)
        }
    }

    @ViewBuilder
    private var automationSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("AUTOMATION").font(.caption).bold().foregroundStyle(.secondary)

            if step.kind == .apiBundleID || step.kind == .apiAppRecord {
                LabeledField(label: "App name", text: $store.draftAppName, placeholder: "My Cool App")
                LabeledField(label: "Bundle ID", text: $store.draftBundleID, placeholder: "com.yourname.appname")
            }
            if step.kind == .apiAppRecord {
                LabeledField(label: "SKU", text: $store.draftSKU, placeholder: "APPNAME001")
            }

            Button(running ? "Working…" : "Run it for me") { runAutomation() }
                .buttonStyle(.borderedProminent)
                .disabled(running || !store.hasCredentials)
            if !store.hasCredentials {
                Text("Add your API key first (sidebar → API Key Setup).")
                    .font(.caption).foregroundStyle(.orange)
            }
        }
        .padding()
        .background(.blue.opacity(0.07), in: RoundedRectangle(cornerRadius: 12))
    }

    private func runAutomation() {
        guard let client = store.makeClient() else {
            result = "No API credentials saved yet."; isError = true; return
        }
        running = true; result = nil
        Task {
            do {
                switch step.kind {
                case .apiBundleID:
                    let id = store.draftBundleID.trimmingCharacters(in: .whitespaces)
                    guard !id.isEmpty else { throw ASCError.invalidKey("Type your bundle ID above first.") }
                    let rec = try await client.createBundleID(identifier: id, name: store.draftAppName.isEmpty ? id : store.draftAppName)
                    result = "Registered \(rec.attributes.identifier). It exists now — forever. No take-backs."
                case .apiCapability:
                    let id = store.draftBundleID.trimmingCharacters(in: .whitespaces)
                    guard !id.isEmpty else { throw ASCError.invalidKey("Type your bundle ID above first (stage 2).") }
                    try await client.enableCapability(bundleID: id, capabilityType: "IN_APP_PURCHASE")
                    result = "In-App Purchase enabled on \(id)."
                case .apiAppRecord:
                    let id = store.draftBundleID.trimmingCharacters(in: .whitespaces)
                    guard !id.isEmpty, !store.draftAppName.isEmpty, !store.draftSKU.isEmpty
                    else { throw ASCError.invalidKey("Fill app name, bundle ID, and SKU above first.") }
                    let app = try await client.createApp(bundleID: id, name: store.draftAppName, sku: store.draftSKU)
                    result = "App record created: \(app.attributes.name). It officially exists."
                default: break
                }
                isError = false
                withAnimation { store.done.insert(step.id) }
            } catch {
                result = error.localizedDescription; isError = true
            }
            running = false
        }
    }
}

struct LabeledField: View {
    var label: String
    @Binding var text: String
    var placeholder: String
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label).font(.caption).foregroundStyle(.secondary)
            TextField(placeholder, text: $text)
                .textFieldStyle(.roundedBorder)
                .font(.body.monospaced())
        }
    }
}

// MARK: - API key setup

struct SetupView: View {
    @EnvironmentObject var store: PipelineStore
    @State private var keyID = ""
    @State private var issuerID = ""
    @State private var pem = ""
    @State private var testing = false
    @State private var testResult: String?
    @State private var testOK = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("Three fields. Then the robot does the boring parts.")
                        .font(.title3).foregroundStyle(.secondary)

                    GroupBox("1 · Key ID") {
                        TextField("e.g. A1B2C3D4E5", text: $keyID)
                            .textFieldStyle(.roundedBorder).font(.body.monospaced())
                        Text("On the API key page in App Store Connect — it's the short code next to your key's name.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    GroupBox("2 · Issuer ID") {
                        TextField("e.g. 11111111-2222-3333-4444-555555555555", text: $issuerID)
                            .textFieldStyle(.roundedBorder).font(.body.monospaced())
                        Text("Top of the same API keys page, labeled 'Issuer ID'.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    GroupBox("3 · The .p8 file contents") {
                        TextEditor(text: $pem)
                            .font(.body.monospaced())
                            .frame(minHeight: 120)
                            .border(.quaternary, width: 1)
                        Text("Open AuthKey_XXXXXXXXXX.p8 in TextEdit, copy EVERYTHING from BEGIN to END. Stored only in your Keychain.")
                            .font(.caption).foregroundStyle(.secondary)
                    }

                    HStack {
                        Button("Save to Keychain") {
                            store.saveCredentials(keyID: keyID.trimmingCharacters(in: .whitespacesAndNewlines),
                                                  issuerID: issuerID.trimmingCharacters(in: .whitespacesAndNewlines),
                                                  pem: pem.trimmingCharacters(in: .whitespacesAndNewlines))
                            testResult = "Saved. Now hit Test."
                            testOK = true
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(keyID.isEmpty || issuerID.isEmpty || pem.isEmpty)

                        Button(testing ? "Testing…" : "Test connection") { test() }
                            .disabled(testing || !store.hasCredentials)
                    }
                    if let testResult {
                        Text(testResult).font(.callout).foregroundStyle(testOK ? .green : .red)
                    }
                    if store.hasCredentials {
                        Button("Remove credentials from Keychain", role: .destructive) {
                            store.clearCredentials()
                            keyID = ""; issuerID = ""; pem = ""
                        }
                        .font(.caption)
                    }
                    Spacer()
                }
                .padding()
            }
            .navigationTitle("API Key Setup")
            .onAppear {
                keyID = store.apiKeyID; issuerID = store.apiIssuerID; pem = store.apiPEM
            }
        }
    }

    private func test() {
        guard let client = store.makeClient() else { return }
        testing = true; testResult = nil
        Task {
            do {
                _ = try await client.ping()
                testResult = "Connected. Apple knows who you are."
                testOK = true
            } catch {
                testResult = error.localizedDescription
                testOK = false
            }
            testing = false
        }
    }
}

// MARK: - Settings

struct SettingsView: View {
    @EnvironmentObject var store: PipelineStore
    var body: some View {
        NavigationStack {
            Form {
                Section("Progress") {
                    HStack {
                        Text("Steps completed")
                        Spacer()
                        Text("\(store.doneCount) / \(store.totalSteps)").foregroundStyle(.secondary)
                    }
                    Button("Reset all progress", role: .destructive) { store.resetProgress() }
                }
                Section("About") {
                    Text("ReleaseBuddy wraps the App Store Connect API so the boring parts run themselves. Manual steps are broken into single actions with exact values and links.")
                        .font(.callout).foregroundStyle(.secondary)
                    Text("Credentials live in your Mac Keychain. Nothing is uploaded anywhere except to Apple, by you, on purpose.")
                        .font(.callout).foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Settings")
            .formStyle(.grouped)
        }
    }
}
