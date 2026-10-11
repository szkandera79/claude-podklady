import PhotosUI
import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var store: ConversationStore
    @EnvironmentObject private var session: VoiceSession
    @State private var showSettings = false
    @State private var showConversations = false
    @State private var showCamera = false
    @State private var photoItems: [PhotosPickerItem] = []
    @State private var draft = ""
    @State private var editingID: UUID?
    @FocusState private var inputFocused: Bool

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
                    Button { showConversations = true } label: { Image(systemName: "list.bullet") }
                        .accessibilityLabel("Seznam konverzací")
                }
                ToolbarItem(placement: .topBarLeading) {
                    Button { session.newConversation() } label: { Image(systemName: "square.and.pencil") }
                        .accessibilityLabel("Nová konverzace")
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showSettings = true } label: { Image(systemName: "gearshape") }
                        .accessibilityLabel("Nastavení")
                }
            }
            .sheet(isPresented: $showSettings) { SettingsView() }
            .sheet(isPresented: $showConversations) { ConversationListView() }
            .fullScreenCover(isPresented: $showCamera) {
                CameraPicker { image in
                    if let jpeg = ImageUtils.jpegForClaude(image) { session.attachImage(jpeg) }
                }
                .ignoresSafeArea()
            }
            .onChange(of: photoItems) { _, items in
                Task { await loadPickedPhotos(items) }
            }
            // Spuštění rozhovoru ze Siri / tlačítka Akce / zkratky
            .onReceive(NotificationCenter.default.publisher(for: .startConversationRequested)) { _ in
                if LaunchRequest.consume(), !session.isActive { session.start() }
            }
            .onAppear {
                if LaunchRequest.consume(), !session.isActive { session.start() }
            }
        }
    }

    @MainActor
    private func loadPickedPhotos(_ items: [PhotosPickerItem]) async {
        guard !items.isEmpty else { return }
        for item in items {
            if let data = try? await item.loadTransferable(type: Data.self),
               let image = UIImage(data: data),
               let jpeg = ImageUtils.jpegForClaude(image) {
                session.attachImage(jpeg)
            }
        }
        photoItems = []
    }

    private var transcript: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 12) {
                    if store.entries.isEmpty && session.liveTranscript.isEmpty {
                        Text("Klepněte na tlačítko níže a mluvte česky. Rozhovor pokračuje i při zamčeném telefonu — ukončíte ho tlačítkem, tlačítkem na sluchátkách nebo na zamčené obrazovce. Můžete také psát do pole dole, přiložit fotku (+) a špatně rozpoznanou zprávu opravit podržením prstu na ní. Siri: „Talk to Claude Voice“.")
                            .font(.callout)
                            .foregroundStyle(.secondary)
                            .padding(.top, 40)
                    }
                    ForEach(store.entries) { entry in
                        MessageBubble(entry: entry, imageURL: store.imageURL)
                            .id(entry.id)
                            .contextMenu {
                                if entry.role == .user {
                                    Button {
                                        editingID = entry.id
                                        draft = entry.text
                                        inputFocused = true
                                    } label: { Label("Opravit a odeslat znovu", systemImage: "pencil") }
                                }
                                if entry.role != .notice {
                                    Button { UIPasteboard.general.string = entry.text } label: {
                                        Label("Kopírovat", systemImage: "doc.on.doc")
                                    }
                                }
                            }
                    }
                    if session.isTextBusy {
                        HStack(spacing: 8) {
                            ProgressView()
                            Text("Claude píše…").font(.footnote).foregroundStyle(.secondary)
                            Button("Zastavit", action: session.stopTextResponse).font(.footnote)
                        }
                        .id("busy")
                    }
                    if !session.liveTranscript.isEmpty {
                        MessageBubble(entry: TranscriptEntry(role: .user, text: session.liveTranscript), isLive: true)
                            .id("live")
                    }
                    Color.clear.frame(height: 1).id("bottom")
                }
                .padding()
            }
            .scrollDismissesKeyboard(.interactively)
            .onChange(of: store.entries) { _, _ in withAnimation { proxy.scrollTo("bottom") } }
            .onChange(of: session.liveTranscript) { _, _ in proxy.scrollTo("bottom") }
        }
    }

    private var inputBar: some View {
        VStack(spacing: 6) {
            if editingID != nil {
                HStack {
                    Label("Opravujete zprávu — po odeslání Claude odpoví znovu", systemImage: "pencil")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button("Zrušit") {
                        editingID = nil
                        draft = ""
                        inputFocused = false
                    }
                    .font(.caption)
                }
            }
            if !session.pendingImages.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(session.pendingImages, id: \.self) { name in
                            ZStack(alignment: .topTrailing) {
                                StoredImage(url: store.imageURL(name), size: 64)
                                Button { session.removePendingImage(name) } label: {
                                    Image(systemName: "xmark.circle.fill")
                                        .symbolRenderingMode(.palette)
                                        .foregroundStyle(.white, .black.opacity(0.6))
                                }
                                .offset(x: 6, y: -6)
                                .accessibilityLabel("Odebrat fotku")
                            }
                        }
                        Text(session.isActive ? "Fotka se odešle s další větou" : "Napište otázku nebo rovnou odešlete")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.top, 6)
                }
            }
            HStack(spacing: 8) {
                Menu {
                    if UIImagePickerController.isSourceTypeAvailable(.camera) {
                        Button { showCamera = true } label: { Label("Vyfotit", systemImage: "camera") }
                    }
                    PhotosPicker(selection: $photoItems, maxSelectionCount: 4, matching: .images) {
                        Label("Vybrat z fotek", systemImage: "photo.on.rectangle")
                    }
                } label: {
                    Image(systemName: "plus.circle.fill").font(.system(size: 30)).foregroundStyle(.secondary)
                }
                .accessibilityLabel("Přiložit fotku")
                TextField(editingID == nil ? "Napište zprávu…" : "Opravené znění…", text: $draft)
                    .textFieldStyle(.roundedBorder)
                    .focused($inputFocused)
                    .submitLabel(.send)
                    .onSubmit(sendDraft)
                Button(action: sendDraft) {
                    Image(systemName: "arrow.up.circle.fill").font(.system(size: 30))
                }
                .disabled(draft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && session.pendingImages.isEmpty)
                .accessibilityLabel("Odeslat zprávu")
            }
        }
        .padding(.horizontal)
    }

    private func sendDraft() {
        let text = draft.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty || !session.pendingImages.isEmpty else { return }
        if let id = editingID, !text.isEmpty {
            session.correctAndResend(entryID: id, newText: text)
        } else {
            session.sendText(text)
        }
        draft = ""
        editingID = nil
        inputFocused = false
    }

    private var controls: some View {
        VStack(spacing: 10) {
            inputBar
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
    var imageURL: (String) -> URL? = { _ in nil }
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
                    if let images = entry.images, !images.isEmpty {
                        HStack(spacing: 6) {
                            ForEach(images, id: \.self) { StoredImage(url: imageURL($0), size: images.count == 1 ? 180 : 86) }
                        }
                    }
                    if !entry.text.isEmpty || entry.images == nil {
                        Text(entry.text.isEmpty ? "…" : entry.text)
                            .textSelection(.enabled)
                    }
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
