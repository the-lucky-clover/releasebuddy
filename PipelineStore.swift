import Foundation
import SwiftUI

/// Holds checklist progress, draft app details, and API credentials (Keychain-backed).
@MainActor
final class PipelineStore: ObservableObject {
    @Published var done: Set<String> = [] {
        didSet { UserDefaults.standard.set(Array(done), forKey: "rb.done") }
    }
    @Published var draftAppName: String = "" {
        didSet { UserDefaults.standard.set(draftAppName, forKey: "rb.appName") }
    }
    @Published var draftBundleID: String = "" {
        didSet { UserDefaults.standard.set(draftBundleID, forKey: "rb.bundleID") }
    }
    @Published var draftSKU: String = "" {
        didSet { UserDefaults.standard.set(draftSKU, forKey: "rb.sku") }
    }

    // API credentials live in the Keychain, never in UserDefaults.
    @Published var apiKeyID: String = ""
    @Published var apiIssuerID: String = ""
    @Published var apiPEM: String = ""

    init() {
        done = Set(UserDefaults.standard.stringArray(forKey: "rb.done") ?? [])
        draftAppName = UserDefaults.standard.string(forKey: "rb.appName") ?? ""
        draftBundleID = UserDefaults.standard.string(forKey: "rb.bundleID") ?? ""
        draftSKU = UserDefaults.standard.string(forKey: "rb.sku") ?? ""
        apiKeyID = KeychainStore.get("rb.apiKeyID") ?? ""
        apiIssuerID = KeychainStore.get("rb.apiIssuerID") ?? ""
        apiPEM = KeychainStore.get("rb.apiPEM") ?? ""
    }

    var totalSteps: Int { PipelineData.allSteps.count }
    var doneCount: Int { done.count }
    var progress: Double { totalSteps == 0 ? 0 : Double(doneCount) / Double(totalSteps) }

    func isDone(_ step: MicroStep) -> Bool { done.contains(step.id) }

    func toggle(_ step: MicroStep) {
        if done.contains(step.id) { done.remove(step.id) } else { done.insert(step.id) }
    }

    /// The next not-yet-done step across all stages — the "one thing" to focus on.
    var nextStep: MicroStep? {
        PipelineData.allSteps.first { !done.contains($0.id) }
    }

    var nextStepIndex: Int {
        guard let next = nextStep else { return totalSteps }
        return PipelineData.allSteps.firstIndex(of: next) ?? totalSteps
    }

    func stageProgress(_ stage: ReleaseStage) -> Double {
        let ids = Set(stage.steps.map(\.id))
        guard !ids.isEmpty else { return 0 }
        return Double(done.intersection(ids).count) / Double(ids.count)
    }

    func saveCredentials(keyID: String, issuerID: String, pem: String) {
        apiKeyID = keyID; apiIssuerID = issuerID; apiPEM = pem
        KeychainStore.set(keyID, for: "rb.apiKeyID")
        KeychainStore.set(issuerID, for: "rb.apiIssuerID")
        KeychainStore.set(pem, for: "rb.apiPEM")
    }

    func clearCredentials() {
        apiKeyID = ""; apiIssuerID = ""; apiPEM = ""
        KeychainStore.delete("rb.apiKeyID")
        KeychainStore.delete("rb.apiIssuerID")
        KeychainStore.delete("rb.apiPEM")
    }

    var hasCredentials: Bool { !apiKeyID.isEmpty && !apiIssuerID.isEmpty && !apiPEM.isEmpty }

    func makeClient() -> AppStoreConnect? {
        guard hasCredentials else { return nil }
        return AppStoreConnect(config: ASCConfig(keyID: apiKeyID, issuerID: apiIssuerID, privateKeyPEM: apiPEM))
    }

    func resetProgress() { done = [] }
}
