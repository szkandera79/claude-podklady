import Foundation

struct TranscriptEntry: Codable, Identifiable, Equatable {
    enum Role: String, Codable { case user, assistant, notice }
    var id = UUID()
    var role: Role
    var text: String
    /// Odpověď byla přerušena uživatelem (uloží se jen vyslovená část).
    var interrupted = false
    var date = Date()
    /// Názvy souborů přiložených fotek (ve složce obrázků aplikace).
    var images: [String]? = nil
}

struct ConversationMeta: Codable, Identifiable, Equatable {
    var id: UUID
    var title: String
    var updated: Date
}

/// Konverzace (přepis + kontext pro Clauda). Každá je ve vlastním souboru, takže přežijí i zavření aplikace.
final class ConversationStore: ObservableObject {
    @Published private(set) var entries: [TranscriptEntry] = []
    @Published private(set) var conversations: [ConversationMeta] = []
    @Published private(set) var currentID = UUID()

    static let maxContextMessages = 150
    static let maxContextChars = 150_000
    /// Fotky se Claudovi posílají jen u posledních několika zpráv (šetří čas i peníze).
    static let recentImageMessages = 6

    private let baseDir: URL?

    init(baseDir: URL? = ConversationStore.defaultBaseDir()) {
        self.baseDir = baseDir
        loadIndex()
        migrateLegacy()
        if let first = conversations.first {
            currentID = first.id
            entries = loadEntries(first.id)
        } else {
            startNew()
        }
    }

    static func defaultBaseDir() -> URL? {
        guard let dir = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first else { return nil }
        let base = dir.appendingPathComponent("Conversations", isDirectory: true)
        try? FileManager.default.createDirectory(at: base.appendingPathComponent("images"), withIntermediateDirectories: true)
        return base
    }

    // MARK: Práce s konverzacemi

    /// Nová prázdná konverzace (prázdnou aktuální nezakládá znovu).
    func newConversation() {
        if entries.isEmpty, conversations.contains(where: { $0.id == currentID }) { return }
        startNew()
    }

    func open(_ id: UUID) {
        guard id != currentID, conversations.contains(where: { $0.id == id }) else { return }
        // Prázdnou rozepsanou konverzaci v seznamu nenecháváme.
        if entries.isEmpty {
            conversations.removeAll { $0.id == currentID }
            saveIndex()
        }
        currentID = id
        entries = loadEntries(id)
    }

    func delete(_ id: UUID) {
        let removed = id == currentID ? entries : loadEntries(id)
        for name in removed.flatMap({ $0.images ?? [] }) {
            if let url = imageURL(name) { try? FileManager.default.removeItem(at: url) }
        }
        if let url = fileURL(id) { try? FileManager.default.removeItem(at: url) }
        conversations.removeAll { $0.id == id }
        saveIndex()
        if id == currentID {
            if let next = conversations.first {
                currentID = next.id
                entries = loadEntries(next.id)
            } else {
                startNew()
            }
        }
    }

    private func startNew() {
        currentID = UUID()
        entries = []
        conversations.insert(ConversationMeta(id: currentID, title: "Nová konverzace", updated: Date()), at: 0)
        saveIndex()
    }

    // MARK: Položky aktuální konverzace

    @discardableResult
    func append(_ role: TranscriptEntry.Role, _ text: String, interrupted: Bool = false, images: [String]? = nil) -> UUID {
        let entry = TranscriptEntry(role: role, text: text, interrupted: interrupted, images: images)
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

    /// Smaže zadanou položku a všechny po ní (oprava špatně rozpoznané zprávy).
    func removeFrom(id: UUID) {
        guard let i = entries.firstIndex(where: { $0.id == id }) else { return }
        entries.removeSubrange(i...)
        save()
    }

    func clear() {
        entries = []
        save()
    }

    // MARK: Fotky

    func imageURL(_ name: String) -> URL? {
        baseDir?.appendingPathComponent("images", isDirectory: true).appendingPathComponent(name)
    }

    /// Uloží JPEG a vrátí název souboru.
    func saveImage(_ jpeg: Data) -> String? {
        let name = UUID().uuidString + ".jpg"
        guard let url = imageURL(name) else { return nil }
        do {
            try jpeg.write(to: url, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
            return name
        } catch {
            return nil
        }
    }

    // MARK: Zprávy pro Claude API

    func apiMessages() -> [[String: Any]] {
        Self.apiMessages(from: entries) { [weak self] name in
            guard let url = self?.imageURL(name), let data = try? Data(contentsOf: url) else { return nil }
            return data.base64EncodedString()
        }
    }

    /// Převod přepisu na platnou historii: jen user/assistant, sloučení po sobě jdoucích zpráv
    /// stejné role, začátek i konec uživatelem, oříznutí nejstarších zpráv při překročení limitu.
    /// Fotky se přikládají jen k posledním `recentImageMessages` zprávám; u starších zůstane jen zmínka.
    static func apiMessages(from entries: [TranscriptEntry], imageLoader: (String) -> String? = { _ in nil }) -> [[String: Any]] {
        var merged: [(role: String, text: String, images: [String])] = []
        for e in entries {
            let text = e.text.trimmingCharacters(in: .whitespacesAndNewlines)
            let images = e.role == .user ? (e.images ?? []) : []
            guard !text.isEmpty || !images.isEmpty else { continue }
            let role: String
            switch e.role {
            case .user: role = "user"
            case .assistant: role = "assistant"
            case .notice: continue
            }
            let content = e.interrupted ? text + " … [uživatel mě v tomto místě přerušil]" : text
            if let last = merged.last, last.role == role {
                merged[merged.count - 1].text += (last.text.isEmpty ? "" : "\n") + content
                merged[merged.count - 1].images += images
            } else {
                merged.append((role, content, images))
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

        let firstWithImages = max(0, merged.count - recentImageMessages)
        return merged.enumerated().map { index, m in
            guard !m.images.isEmpty else { return ["role": m.role, "content": m.text] }
            let note = m.images.count == 1 ? "[Uživatel poslal fotku.]" : "[Uživatel poslal \(m.images.count) fotky.]"
            if index < firstWithImages {
                return ["role": m.role, "content": m.text.isEmpty ? note : m.text + "\n" + note]
            }
            var parts: [[String: Any]] = m.images.compactMap { name in
                imageLoader(name).map { ["type": "image", "media_type": "image/jpeg", "data": $0] }
            }
            if parts.isEmpty { return ["role": m.role, "content": m.text.isEmpty ? note : m.text + "\n" + note] }
            parts.append(["type": "text", "text": m.text.isEmpty ? "Co je na fotce?" : m.text])
            return ["role": m.role, "content": parts]
        }
    }

    // MARK: Ukládání

    private func fileURL(_ id: UUID) -> URL? { baseDir?.appendingPathComponent("\(id.uuidString).json") }
    private var indexURL: URL? { baseDir?.appendingPathComponent("index.json") }

    private func loadIndex() {
        guard let url = indexURL, let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode([ConversationMeta].self, from: data) else { return }
        conversations = decoded.sorted { $0.updated > $1.updated }
    }

    private func saveIndex() {
        guard let url = indexURL, let data = try? JSONEncoder().encode(conversations) else { return }
        try? data.write(to: url, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
    }

    private func loadEntries(_ id: UUID) -> [TranscriptEntry] {
        guard let url = fileURL(id), let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode([TranscriptEntry].self, from: data) else { return [] }
        return decoded
    }

    private func save() {
        guard let url = fileURL(currentID), let data = try? JSONEncoder().encode(entries) else { return }
        try? data.write(to: url, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
        // Název = začátek první zprávy uživatele; seznam řazený podle poslední změny.
        let title = entries.first(where: { $0.role == .user })
            .map { String($0.text.trimmingCharacters(in: .whitespacesAndNewlines).prefix(60)) } ?? ""
        var meta = conversations.first(where: { $0.id == currentID }) ?? ConversationMeta(id: currentID, title: "", updated: Date())
        meta.title = title.isEmpty ? (entries.contains { $0.images != nil } ? "Fotka" : "Nová konverzace") : title
        meta.updated = Date()
        conversations.removeAll { $0.id == currentID }
        conversations.insert(meta, at: 0)
        saveIndex()
    }

    /// Převod původní jediné konverzace (conversation.json) do seznamu konverzací.
    private func migrateLegacy() {
        guard let base = baseDir else { return }
        let legacy = base.deletingLastPathComponent().appendingPathComponent("conversation.json")
        guard FileManager.default.fileExists(atPath: legacy.path) else { return }
        if let data = try? Data(contentsOf: legacy),
           let old = try? JSONDecoder().decode([TranscriptEntry].self, from: data), !old.isEmpty {
            let id = UUID()
            if let url = fileURL(id) { try? data.write(to: url, options: .atomic) }
            let title = old.first(where: { $0.role == .user }).map { String($0.text.prefix(60)) } ?? "Konverzace"
            conversations.append(ConversationMeta(id: id, title: title, updated: old.last?.date ?? Date()))
            conversations.sort { $0.updated > $1.updated }
            saveIndex()
        }
        try? FileManager.default.removeItem(at: legacy)
    }
}
