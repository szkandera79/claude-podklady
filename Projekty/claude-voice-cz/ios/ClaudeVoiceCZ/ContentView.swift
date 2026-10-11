import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var store: ConversationStore
    @EnvironmentObject private var session: VoiceSession
    @State private var showSettings = false
    @State private var confirmNew = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                transcript
                Divider()
                controls
            }
            .navigationTitle("Claude Voice")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button { confirmNew = true } label: { Image(systemName: "square.and.pencil") }
                        .accessibilityLabel("Nová konverzace")
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showSettings = true } label: { Image(systemName: "gearshape") }
                        .accessibilityLabel("Nastavení")
                }
            }
            .sheet(isPresented: $showSettings) { SettingsView() }
            .confirmationDialog("Začít novou konverzaci? Současný přepis i kontext se smažou.",
                                isPresented: $confirmNew, titleVisibility: .visible) {
                Button("Nová konverzace", role: .destructive) { session.newConversation() }
                Button("Zrušit", role: .cancel) {}
            }
        }
    }

    private var transcript: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 12) {
                    if store.entries.isEmpty && session.liveTranscript.isEmpty {
                        Text("Klepněte na tlačítko níže a mluvte česky. Rozhovor pokračuje i při zamčeném telefonu — ukončíte ho tlačítkem, tlačítkem na sluchátkách nebo na zamčené obrazovce.")
                            .font(.callout)
                            .foregroundStyle(.secondary)
                            .padding(.top, 40)
                    }
                    ForEach(store.entries) { entry in
                        MessageBubble(entry: entry).id(entry.id)
                    }
                    if !session.liveTranscript.isEmpty {
                        MessageBubble(entry: TranscriptEntry(role: .user, text: session.liveTranscript), isLive: true)
                            .id("live")
                    }
                    Color.clear.frame(height: 1).id("bottom")
                }
                .padding()
            }
            .onChange(of: store.entries) { _, _ in withAnimation { proxy.scrollTo("bottom") } }
            .onChange(of: session.liveTranscript) { _, _ in proxy.scrollTo("bottom") }
        }
    }

    private var controls: some View {
        VStack(spacing: 10) {
            if let error = session.lastError {
                Text(error)
                    .font(.footnote)
                    .foregroundStyle(.red)
                    .multilineTextAlignment(.center)
            }
            HStack(spacing: 6) {
                Circle().fill(stateColor).frame(width: 8, height: 8)
                Text(session.stateLabel).font(.subheadline.weight(.medium))
                if session.isActive && !session.routeDescription.isEmpty {
                    Text("· \(session.routeDescription)").font(.footnote).foregroundStyle(.secondary).lineLimit(1)
                }
            }
            if session.state == .speaking && !session.heardWhileSpeaking.isEmpty {
                Text("Slyším: \(session.heardWhileSpeaking)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                    .truncationMode(.head)
                    .padding(.horizontal)
            }
            HStack(spacing: 28) {
            if session.state == .speaking || session.state == .thinking {
                Button(action: session.interrupt) {
                    Image(systemName: "hand.raised.fill")
                        .font(.system(size: 24, weight: .semibold))
                        .foregroundStyle(.white)
                        .frame(width: 64, height: 64)
                        .background(Circle().fill(Color.blue))
                }
                .accessibilityLabel("Přerušit Clauda")
            }
            Button(action: session.toggle) {
                ZStack {
                    Circle()
                        .fill(session.isActive ? Color.red : Color.accentColor)
                        .frame(width: 84, height: 84)
                        .shadow(radius: session.state == .speaking ? 10 : 3)
                        .scaleEffect(session.state == .listening ? 1.06 : 1.0)
                        .animation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true).speed(session.state == .listening ? 1 : 0),
                                   value: session.state)
                    Image(systemName: session.isActive ? "stop.fill" : "mic.fill")
                        .font(.system(size: 32, weight: .semibold))
                        .foregroundStyle(.white)
                }
            }
            .accessibilityLabel(session.isActive ? "Ukončit hlasovou relaci" : "Zahájit hlasovou relaci")
            }
            Text(session.state == .speaking || session.state == .thinking ? "Přerušit · Ukončit"
                 : (session.isActive ? "Ukončit" : "Zahájit rozhovor"))
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(.vertical, 14)
        .frame(maxWidth: .infinity)
        .background(.bar)
    }

    private var stateColor: Color {
        switch session.state {
        case .idle: return .gray
        case .listening: return .green
        case .thinking: return .orange
        case .speaking: return .blue
        case .suspended: return .yellow
        }
    }
}

struct MessageBubble: View {
    let entry: TranscriptEntry
    var isLive = false

    var body: some View {
        switch entry.role {
        case .notice:
            Text(entry.text)
                .font(.caption)
                .foregroundStyle(.secondary)
                .frame(maxWidth: .infinity)
        case .user, .assistant:
            let isUser = entry.role == .user
            HStack {
                if isUser { Spacer(minLength: 40) }
                VStack(alignment: .leading, spacing: 4) {
                    Text(entry.text.isEmpty ? "…" : entry.text)
                        .textSelection(.enabled)
                    if entry.interrupted {
                        Text("přerušeno").font(.caption2).foregroundStyle(.secondary)
                    }
                }
                .padding(10)
                .background(isUser ? Color.accentColor.opacity(isLive ? 0.08 : 0.15) : Color(.secondarySystemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 14))
                .opacity(isLive ? 0.7 : 1)
                if !isUser { Spacer(minLength: 40) }
            }
        }
    }
}
