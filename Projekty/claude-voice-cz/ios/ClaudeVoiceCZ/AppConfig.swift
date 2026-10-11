import Foundation
import Security

/// Bezpečné uložení přístupového tokenu do Klíčenky iPhonu.
enum KeychainStore {
    private static let service = "ClaudeVoiceCZ"

    static func get(_ key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var result: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
              let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    static func set(_ key: String, _ value: String) {
        let base: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
        ]
        SecItemDelete(base as CFDictionary)
        guard !value.isEmpty else { return }
        var add = base
        add[kSecValueData as String] = Data(value.utf8)
        // Dostupné i při zamčeném telefonu (po prvním odemčení) — nutné pro provoz v kapse.
        add[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        SecItemAdd(add as CFDictionary, nil)
    }
}

/// Nastavení připojení k serveru. Výchozí hodnoty se při prvním spuštění převezmou
/// ze sestavení (Config/Secrets.xcconfig → Info.plist) a token se přesune do Klíčenky.
enum AppConfig {
    private static let urlKey = "serverURL"
    private static let tokenKey = "appToken"

    static func bootstrap() {
        let info = Bundle.main.infoDictionary ?? [:]
        if UserDefaults.standard.string(forKey: urlKey) == nil,
           let url = info["CVServerURL"] as? String, url.hasPrefix("https://") {
            UserDefaults.standard.set(url, forKey: urlKey)
        }
        if KeychainStore.get(tokenKey) == nil,
           let token = info["CVAppToken"] as? String, !token.isEmpty, !token.hasPrefix("$(") {
            KeychainStore.set(tokenKey, token)
        }
    }

    static var serverURL: String {
        get { UserDefaults.standard.string(forKey: urlKey) ?? "" }
        set { UserDefaults.standard.set(newValue.trimmingCharacters(in: .whitespacesAndNewlines), forKey: urlKey) }
    }

    static var appToken: String {
        get { KeychainStore.get(tokenKey) ?? "" }
        set { KeychainStore.set(tokenKey, newValue.trimmingCharacters(in: .whitespacesAndNewlines)) }
    }

    static var isConfigured: Bool { serverURL.hasPrefix("https://") && !appToken.isEmpty }
}
