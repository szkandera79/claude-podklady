import Foundation
import UserNotifications

/// Hlídá platnost instalace (bezplatný Apple účet = 7 dní) a předem upozorní,
/// že je potřeba připojit iPhone k Macu — přeinstalaci pak Mac provede sám.
enum InstallExpiry {
    /// Datum vypršení z profilu, se kterým byla aplikace podepsaná (nil v simulátoru / App Store).
    static var expirationDate: Date? {
        guard let url = Bundle.main.url(forResource: "embedded", withExtension: "mobileprovision"),
              let data = try? Data(contentsOf: url),
              let text = String(data: data, encoding: .isoLatin1),
              let start = text.range(of: "<?xml"), let end = text.range(of: "</plist>") else { return nil }
        let xml = String(text[start.lowerBound..<end.upperBound])
        guard let plist = try? PropertyListSerialization.propertyList(from: Data(xml.utf8), format: nil) as? [String: Any]
        else { return nil }
        return plist["ExpirationDate"] as? Date
    }

    /// Naplánuje upozornění 24 h, 6 h a 1 h před vypršením (při každém spuštění znovu).
    static func scheduleReminders() {
        guard let expiry = expirationDate else { return }
        let center = UNUserNotificationCenter.current()
        center.requestAuthorization(options: [.alert, .sound]) { granted, _ in
            guard granted else { return }
            let ids = ["expiry-24h", "expiry-6h", "expiry-1h"]
            center.removePendingNotificationRequests(withIdentifiers: ids)
            let plan: [(String, TimeInterval, String)] = [
                ("expiry-24h", 24 * 3600, "Zítra vyprší instalace Claude Voice."),
                ("expiry-6h", 6 * 3600, "Za 6 hodin vyprší instalace Claude Voice."),
                ("expiry-1h", 3600, "Za hodinu vyprší instalace Claude Voice."),
            ]
            for (id, before, title) in plan {
                let fire = expiry.addingTimeInterval(-before)
                guard fire > Date() else { continue }
                let content = UNMutableNotificationContent()
                content.title = title
                content.body = "Připojte iPhone kabelem k Macu a odemkněte ho — Mac aplikaci obnoví sám."
                content.sound = .default
                let comps = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: fire)
                let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
                center.add(UNNotificationRequest(identifier: id, content: content, trigger: trigger))
            }
        }
    }
}
