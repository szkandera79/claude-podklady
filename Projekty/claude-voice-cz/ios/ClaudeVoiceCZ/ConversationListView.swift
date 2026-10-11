import SwiftUI

/// Seznam uložených konverzací (jako chaty v aplikaci Claude / ChatGPT).
struct ConversationListView: View {
    @EnvironmentObject private var store: ConversationStore
    @EnvironmentObject private var session: VoiceSession
    @Environment(\.dismiss) private var dismiss
    @State private var search = ""

    private var filtered: [ConversationMeta] {
        let q = search.trimmingCharacters(in: .whitespaces).lowercased()
        guard !q.isEmpty else { return store.conversations }
        return store.conversations.filter { $0.title.lowercased().contains(q) }
    }

    var body: some View {
        NavigationStack {
            List {
                ForEach(filtered) { c in
                    Button {
                        session.openConversation(c.id)
                        dismiss()
                    } label: {
                        VStack(alignment: .leading, spacing: 3) {
                            Text(c.title).lineLimit(2).foregroundStyle(.primary)
                            Text(c.updated.formatted(.relative(presentation: .named)))
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                    .listRowBackground(c.id == store.currentID ? Color.accentColor.opacity(0.12) : nil)
                }
                .onDelete { offsets in
                    for i in offsets { store.delete(filtered[i].id) }
                }
            }
            .searchable(text: $search, prompt: "Hledat v konverzacích")
            .overlay {
                if filtered.isEmpty { ContentUnavailableView("Nic nenalezeno", systemImage: "magnifyingglass") }
            }
            .navigationTitle("Konverzace")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Zavřít") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button {
                        session.newConversation()
                        dismiss()
                    } label: { Label("Nová", systemImage: "square.and.pencil") }
                }
            }
        }
    }
}
