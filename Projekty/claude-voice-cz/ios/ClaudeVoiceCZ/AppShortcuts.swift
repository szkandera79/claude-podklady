import AppIntents
import Foundation

extension Notification.Name {
    static let startConversationRequested = Notification.Name("startConversationRequested")
}

/// Požadavek na zahájení rozhovoru ze Siri / tlačítka Akce / zkratky (vyřídí ho ContentView).
enum LaunchRequest {
    private static var pending = false

    static func request() {
        pending = true
        NotificationCenter.default.post(name: .startConversationRequested, object: nil)
    }

    /// Vrátí true jednou po každém požadavku.
    static func consume() -> Bool {
        defer { pending = false }
        return pending
    }
}

struct StartConversationIntent: AppIntent {
    static var title: LocalizedStringResource = "Zahájit rozhovor s Claudem"
    static var description = IntentDescription("Otevře Claude Voice a hned začne poslouchat.")
    static var openAppWhenRun: Bool = true

    @MainActor
    func perform() async throws -> some IntentResult {
        LaunchRequest.request()
        return .result()
    }
}

/// Zkratky dostupné hned po instalaci (Siri, Zkratky, tlačítko Akce, Spotlight).
struct ClaudeVoiceShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: StartConversationIntent(),
            phrases: [
                "Talk to \(.applicationName)",
                "Start \(.applicationName)",
                "Open \(.applicationName) conversation",
                "Mluv s \(.applicationName)",
                "Spusť \(.applicationName)",
            ],
            shortTitle: "Rozhovor s Claudem",
            systemImageName: "waveform"
        )
    }
}
