import Foundation

struct TranscriptEntry: Codable, Identifiable, Equatable {
    enum Role: String, Codable { case user, assistant, notice }
    var id = UUID()
    var role: Role
    var text: String
    /// Odpověď byla přerušena uživatelem (uloží se jen vyslovená část).
    var interrupted = false
    var date = Date()
}

/// Přepis konverzace + kontext pro Clauda. Ukládá se do souboru, takže přežije i zavření aplikace.
final class ConversationStore: ObservableObject {
    @Published private(set) var entries: [TranscriptEntry] = []

    static let maxContextMessages = 150
    static let maxContextChars = 150_000

    private let fileURL: URL?

    init(fileURL: URL? = ConversationStore.defaultFileURL()) {
        self.fileURL = fileURL
        load()
    }

    static func defaultFileURL() -> URL? {
        guard let dir = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first else { return nil }
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        return dir.appendingPathComponent("conversation.json")
    }

    @discardableResult
    func append(_ role: TranscriptEntry.Role, _ text: String, interrupted: Bool = false) -> UUID {
        let entry = TranscriptEntry(role: role, text: text, interrupted: interrupted)
        entries.append(entry)
        save()
        return entry.id
    }

    /// `persist: false` při průběžném streamování (bez zápisu na disk po každém slově).
    func update(id: UUID, text: String, interrupted: Bool? = nil, persist: Bool = true) {
        guard let i = entries.firstIndex(where: { $0.id == id }) else { return }
        entries[i].text = text
        if let interrupted { entries[i].interrupted = interrupted }
        if persist { save() }
    }

    func remove(id: UUID) {
        entries.removeAll { $0.id == id }
        save()
    }

    func clear() {
        entries = []
        save()
    }

    /// Zprávy pro Claude API.
    func apiMessages() -> [[String: String]] {
        Self.apiMessages(from: entries)
    }

    /// Převod přepisu na platnou historii: jen user/assistant, sloučení po sobě jdoucích zpráv
    /// stejné role, začátek i konec uživatelem, oříznutí nejstarších zpráv při překročení limitu.
    static func apiMessages(from entries: [TranscriptEntry]) -> [[String: String]] {
        var merged: [(role: String, text: String)] = []
        for e in entries {
            let text = e.text.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !text.isEmpty else { continue }
            let role: String
            switch e.role {
            case .user: role = "user"
            case .assistant: role = "assistant"
            case .notice: continue
            }
            let content = e.interrupted ? text + " … [uživatel mě v tomto místě přerušil]" : text
            if let last = merged.last, last.role == role {
                merged[merged.count - 1].text += "\n" + content
            } else {
                merged.append((role, content))
            }
        }
        while merged.first?.role == "assistant" { merged.removeFirst() }
        while merged.last?.role == "assistant" { merged.removeLast() }

        // Oříznutí od nejstarších (po dvojicích, aby začátek zůstal u uživatele).
        func totalChars() -> Int { merged.reduce(0) { $0 + $1.text.count } }
        while merged.count > 1 && (merged.count > maxContextMessages || totalChars() > maxContextChars) {
            merged.removeFirst(min(2, merged.count - 1))
            while merged.first?.role == "assistant" { merged.removeFirst() }
        }
        return merged.map { ["role": $0.role, "content": $0.text] }
    }

    private func load() {
        guard let fileURL, let data = try? Data(contentsOf: fileURL),
              let decoded = try? JSONDecoder().decode([TranscriptEntry].self, from: data) else { return }
        entries = decoded
    }

    private func save() {
        guard let fileURL, let data = try? JSONEncoder().encode(entries) else { return }
        try? data.write(to: fileURL, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
    }
}
