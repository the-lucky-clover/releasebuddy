import Foundation
import CryptoKit

// MARK: - Config & errors

struct ASCConfig {
    var keyID: String
    var issuerID: String
    var privateKeyPEM: String
}

enum ASCError: Error, LocalizedError {
    case invalidKey(String)
    case http(Int, String)
    case decoding(String)

    var errorDescription: String? {
        switch self {
        case .invalidKey(let m): return "API key problem: \(m)"
        case .http(let code, let body): return "App Store Connect returned \(code): \(body.prefix(300))"
        case .decoding(let m): return "Couldn't read Apple's response: \(m)"
        }
    }
}

// MARK: - Client

/// Thin async client over the App Store Connect API.
/// Mirrors the asc-automation modules: bundle IDs, capabilities, app records.
final class AppStoreConnect {
    private let config: ASCConfig
    private let base = "https://api.appstoreconnect.apple.com"

    init(config: ASCConfig) { self.config = config }

    // MARK: JWT (ES256)

    private func base64url(_ data: Data) -> String {
        data.base64EncodedString()
            .replacingOccurrences(of: "+", with: "-")
            .replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: "=", with: "")
    }

    private func jwt() throws -> String {
        let header = #"{"alg":"ES256","kid":"\#(config.keyID)","typ":"JWT"}"#
        let now = Int(Date().timeIntervalSince1970)
        let payload = #"{"iss":"\#(config.issuerID)","iat":\#(now),"exp":\#(now + 1200),"aud":"appstoreconnect-v1"}"#
        let h = base64url(Data(header.utf8))
        let p = base64url(Data(payload.utf8))
        let signingInput = Data("\(h).\(p)".utf8)
        let key: P256.Signing.PrivateKey
        do {
            key = try P256.Signing.PrivateKey(pemRepresentation: config.privateKeyPEM)
        } catch {
            throw ASCError.invalidKey("That .p8 doesn't look like a valid P-256 private key. Paste the whole file, BEGIN to END.")
        }
        let sig = try key.signature(for: signingInput)
        return "\(h).\(p).\(base64url(sig.rawRepresentation))"
    }

    private func send(_ method: String, _ path: String, body: Data? = nil) async throws -> Data {
        var req = URLRequest(url: URL(string: base + path)!)
        req.httpMethod = method
        req.setValue("Bearer \(try jwt())", forHTTPHeaderField: "Authorization")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = body
        let (data, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            let code = (resp as? HTTPURLResponse)?.statusCode ?? -1
            throw ASCError.http(code, String(data: data, encoding: .utf8) ?? "")
        }
        return data
    }

    // MARK: - Bundle IDs

    struct BundleID: Decodable {
        var id: String
        var attributes: Attr
        struct Attr: Decodable { var identifier: String; var name: String }
    }
    private struct ListResponse<T: Decodable>: Decodable { var data: [T] }
    private struct SingleResponse<T: Decodable>: Decodable { var data: T }

    /// Returns the bundle ID record if it already exists, else nil.
    func findBundleID(identifier: String) async throws -> BundleID? {
        let q = "filter[identifier]=\(identifier)".addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        let data = try await send("GET", "/v1/bundleIds?\(q)&limit=1")
        let list = try JSONDecoder().decode(ListResponse<BundleID>.self, from: data)
        return list.data.first
    }

    /// Registers a new bundle ID. Throws a friendly error if it already exists.
    @discardableResult
    func createBundleID(identifier: String, name: String) async throws -> BundleID {
        if let existing = try await findBundleID(identifier: identifier) {
            throw ASCError.http(200, "That bundle ID is already registered (id \(existing.id)). Pick a different one — bundle IDs are forever.")
        }
        let body: [String: Any] = [
            "data": [
                "type": "bundleIds",
                "attributes": ["identifier": identifier, "name": name, "platform": "IOS"],
            ] as [String: Any],
        ]
        let data = try await send("POST", "/v1/bundleIds",
                                  body: JSONSerialization.data(withJSONObject: body))
        return try JSONDecoder().decode(SingleResponse<BundleID>.self, from: data).data
    }

    // MARK: - Capabilities

    /// Enables a capability (e.g. IN_APP_PURCHASE) on a bundle ID.
    func enableCapability(bundleID: String, capabilityType: String) async throws {
        guard let record = try await findBundleID(identifier: bundleID) else {
            throw ASCError.invalidKey("Bundle ID \(bundleID) isn't registered yet. Do step 2 first.")
        }
        let body: [String: Any] = [
            "data": [
                "type": "bundleIdCapabilities",
                "attributes": ["capabilityType": capabilityType, "settings": []],
            ] as [String: Any],
        ]
        _ = try await send("POST", "/v1/bundleIds/\(record.id)/bundleIdCapabilities",
                           body: JSONSerialization.data(withJSONObject: body))
    }

    // MARK: - Apps

    struct App: Decodable {
        var id: String
        var attributes: Attr
        struct Attr: Decodable { var name: String; var bundleId: String; var sku: String }
    }

    /// Creates the app record in App Store Connect.
    @discardableResult
    func createApp(bundleID: String, name: String, sku: String) async throws -> App {
        guard let record = try await findBundleID(identifier: bundleID) else {
            throw ASCError.invalidKey("Bundle ID \(bundleID) isn't registered yet. Do step 2 first.")
        }
        let body: [String: Any] = [
            "data": [
                "type": "apps",
                "attributes": ["name": name, "primaryLocale": "en-US", "sku": sku],
                "relationships": [
                    "bundleId": ["data": ["type": "bundleIds", "id": record.id]],
                ],
            ] as [String: Any],
        ]
        let data = try await send("POST", "/v1/apps",
                                  body: JSONSerialization.data(withJSONObject: body))
        return try JSONDecoder().decode(SingleResponse<App>.self, from: data).data
    }

    /// Quick connectivity check: lists one bundle ID.
    func ping() async throws -> Int {
        let data = try await send("GET", "/v1/bundleIds?limit=1")
        let list = try JSONDecoder().decode(ListResponse<BundleID>.self, from: data)
        return list.data.count
    }
}
