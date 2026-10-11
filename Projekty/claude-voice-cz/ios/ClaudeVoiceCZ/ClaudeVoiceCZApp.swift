import SwiftUI

@main
struct ClaudeVoiceCZApp: App {
    @StateObject private var store: ConversationStore
    @StateObject private var session: VoiceSession

    init() {
        AppConfig.bootstrap()
        let store = ConversationStore()
        _store = StateObject(wrappedValue: store)
        _session = StateObject(wrappedValue: VoiceSession(store: store))
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(store)
                .environmentObject(session)
        }
    }
}
