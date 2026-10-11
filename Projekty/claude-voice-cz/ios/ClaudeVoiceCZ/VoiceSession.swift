import AVFoundation
import MediaPlayer
import SwiftUI
import UIKit

/// Řízení hlasového rozhovoru. Veškerá logika běží na hlavním vlákně.
///
/// Stavový automat:
///   idle ──start──▶ listening ──ticho po řeči──▶ thinking ──první věta──▶ speaking ──dohráno──▶ listening
///   speaking/thinking ──uživatel promluví──▶ listening   (přerušení / doplnění dotazu)
///   cokoli ──telefonní hovor──▶ suspended ──konec hovoru──▶ listening
final class VoiceSession: ObservableObject {
    enum State: Equatable {
        case idle, listening, thinking, speaking, suspended
    }

    @Published private(set) var state: State = .idle
    /// Právě rozpoznávaný text uživatele (živý náhled).
    @Published private(set) var liveTranscript = ""
    @Published private(set) var lastError: String?
    @Published private(set) var routeDescription = ""
    /// Diagnostika: co mikrofon zachytil, zatímco Claude mluví.
    @Published private(set) var heardWhileSpeaking = ""
    /// Probíhá odpověď na napsanou zprávu mimo hlasový rozhovor (odpověď jen textem).
    @Published private(set) var isTextBusy = false
    /// Fotky připravené k odeslání s další zprávou (mluvenou i psanou).
    @Published private(set) var pendingImages: [String] = []

    let store: ConversationStore
    private let audio = AudioController()
    private let recognizer = SpeechRecognizerService()
    private let deviceTools = DeviceTools()
    private let recorder = UtteranceRecorder()
    /// Pozice v nahrávce, kde začala aktuální promluva (pro přesný přepis přes ElevenLabs).
    private var utteranceStart: Int?
    private var lastUtteranceStart: Int?
    private var sttTask: Task<Void, Never>?
    private var cloudSTT: Bool { defaults.object(forKey: SettingsKey.cloudSTT) as? Bool ?? true }
    private lazy var speech = SpeechOutput(audio: audio)
    private var splitter = SentenceSplitter()

    // Nastavení (upravuje SettingsView přes @AppStorage se stejnými klíči)
    private var defaults: UserDefaults { .standard }
    private var silenceTimeout: Double { defaults.object(forKey: SettingsKey.silenceTimeout) as? Double ?? 1.2 }
    private var bargeInEnabled: Bool { defaults.object(forKey: SettingsKey.bargeIn) as? Bool ?? true }
    private var bargeInMinWords: Int { 2 }
    /// Povely, které přeruší Clauda i samostatně (jedno slovo).
    private static let stopWords: Set<String> = [
        "stop", "stůj", "počkej", "počkejte", "dost", "moment", "momentík", "ticho", "přestaň", "přestaňte",
        "zastav", "počkat", "haló", "hele", "claude", "klaude",
    ]

    /// Je zachycená řeč dost jasná na přerušení odpovědi?
    private func isBargeIn(_ text: String) -> Bool {
        let words = text.lowercased()
            .split(whereSeparator: { !$0.isLetter })
            .map(String.init)
        if words.count >= bargeInMinWords { return true }
        return words.contains { Self.stopWords.contains($0) }
    }
    private var idleMinutes: Double { defaults.object(forKey: SettingsKey.idleMinutes) as? Double ?? 10 }

    private var responseTask: Task<Void, Never>?
    private var endpointTimer: Timer?
    private var idleTimer: Timer?
    private var lastActivity = Date()
    /// Text, který uživatel řekl před pauzou a pak pokračoval (doplnění dotazu).
    private var utterancePrefix = ""
    private var pendingUserEntryID: UUID?
    private var assistantEntryID: UUID?
    private var assistantText = ""
    private var isNotice = false
    /// Aktuální odpověď se nepředčítá (psaní mimo hlasový rozhovor).
    private var textOnly = false
    private var noticeCompletion: (() -> Void)?
    private var resumeAfterInterruption = false
    private var needsResend = false
    private var recognizerFailures: [Date] = []
    private var lastEngineRestart = Date.distantPast
    private var observers: [NSObjectProtocol] = []

    init(store: ConversationStore) {
        self.store = store
        recognizer.onResult = { [weak self] text, isFinal in self?.handleRecognition(text, isFinal: isFinal) }
        recognizer.onTaskEnded = { [weak self] error in self?.handleRecognitionEnded(error) }
        audio.onInputBuffer = { [weak recognizer = self.recognizer, weak recorder = self.recorder] buffer in
            recognizer?.append(buffer)
            recorder?.append(buffer)
        }
        audio.onConfigurationChange = { [weak self] in self?.handleEngineConfigurationChange() }
        observeSystemNotifications()
    }

    var isActive: Bool { state != .idle }

    // MARK: - Start / stop

    func start() {
        guard state == .idle else { return }
        lastError = nil
        Task { @MainActor [self] in
            guard AppConfig.isConfigured else {
                lastError = ClaudeClientError.notConfigured.errorDescription
                return
            }
            guard await AVAudioApplication.requestRecordPermission() else {
                lastError = "Aplikace nemá přístup k mikrofonu. Povolte ho v Nastavení iPhonu → Claude Voice."
                return
            }
            guard await SpeechRecognizerService.requestAuthorization() else {
                lastError = "Aplikace nemá povolené rozpoznávání řeči. Povolte ho v Nastavení iPhonu → Claude Voice."
                return
            }
            applySpeechSettings()
            do {
                try startAudio()
            } catch {
                lastError = "Nepodařilo se spustit zvuk: \(error.localizedDescription)"
                stopAudio()
                return
            }
            state = .listening
            lastActivity = Date()
            startIdleTimer()
            setupRemoteCommands()
            updateNowPlaying()
            recognizer.startTask()
            speakNotice("Poslouchám.")
        }
    }

    func stop() {
        guard state != .idle else { return }
        cancelResponse(keepSpokenPart: true)
        speech.stop()
        recognizer.cancelTask()
        endpointTimer?.invalidate()
        idleTimer?.invalidate()
        utterancePrefix = ""
        liveTranscript = ""
        utteranceStart = nil
        recorder.reset()
        isNotice = false
        noticeCompletion = nil
        stopAudio()
        teardownRemoteCommands()
        state = .idle
    }

    func toggle() { state == .idle ? start() : stop() }

    func newConversation() {
        stop()
        stopTextResponse()
        pendingImages = []
        store.newConversation()
    }

    func openConversation(_ id: UUID) {
        stop()
        stopTextResponse()
        pendingImages = []
        store.open(id)
    }

    // MARK: - Fotky

    /// Přiloží fotku (JPEG) k další zprávě.
    func attachImage(_ jpeg: Data) {
        guard pendingImages.count < 4, let name = store.saveImage(jpeg) else { return }
        pendingImages.append(name)
    }

    func removePendingImage(_ name: String) {
        pendingImages.removeAll { $0 == name }
        if let url = store.imageURL(name) { try? FileManager.default.removeItem(at: url) }
    }

    /// Vezme přiložené fotky pro odesílanou zprávu.
    private func takePendingImages() -> [String]? {
        let images = pendingImages
        pendingImages = []
        return images.isEmpty ? nil : images
    }

    private func startAudio() throws {
        try audio.activateSession()
        try audio.start()
        routeDescription = audio.routeDescription
    }

    private func stopAudio() {
        audio.stop()
        audio.deactivateSession()
    }

    private func applySpeechSettings() {
        speech.voiceIdentifier = defaults.string(forKey: SettingsKey.voiceID)
        if let rate = defaults.object(forKey: SettingsKey.speechRate) as? Double { speech.rate = Float(rate) }
        recognizer.preferOnDevice = defaults.object(forKey: SettingsKey.preferOnDevice) as? Bool ?? false
        speech.onStartedSpeaking = { [weak self] in
            guard let self, !self.isNotice, self.state == .thinking else { return }
            self.state = .speaking
            self.updateNowPlaying()
        }
        speech.onFinished = { [weak self] in self?.handleSpeechFinished() }
        speech.useCloud = defaults.object(forKey: SettingsKey.cloudVoice) as? Bool ?? true
        speech.onCloudExhausted = { [weak self] in
            self?.store.append(.notice, "Kredit přirozeného hlasu je vyčerpán — dočasně mluví hlas iPhonu, za 30 minut to zkusím znovu.")
        }
        speech.onCloudRestored = { [weak self] in
            self?.store.append(.notice, "Přirozený hlas je opět k dispozici.")
        }
    }

    // MARK: - Rozpoznávání řeči

    private func handleRecognition(_ text: String, isFinal: Bool) {
        let words = text.split(whereSeparator: { $0.isWhitespace }).count
        switch state {
        case .listening:
            if isNotice {
                // Uživatel mluví do krátké hlášky — utneme ji.
                guard isBargeIn(text) else { return }
                speech.stop()
                finishNotice()
            }
            if utteranceStart == nil, !text.isEmpty { markUtteranceStart() }
            liveTranscript = composeUtterance(text)
            lastActivity = Date()
            if isFinal {
                commitUtterance()
            } else if !text.isEmpty {
                restartEndpointTimer()
            }
        case .thinking:
            // Uživatel pokračuje v mluvení po pauze → zrušíme dotaz a spojíme ho s pokračováním.
            guard words >= bargeInMinWords else { return }
            reopenPendingUtterance()
            liveTranscript = composeUtterance(text)
            restartEndpointTimer()
        case .speaking:
            heardWhileSpeaking = text
            guard bargeInEnabled, isBargeIn(text) else { return }
            interruptAssistant()
            markUtteranceStart(preRoll: 2.5)
            liveTranscript = composeUtterance(text)
            restartEndpointTimer()
        case .idle, .suspended:
            break
        }
    }

    private func composeUtterance(_ text: String) -> String {
        utterancePrefix.isEmpty ? text : utterancePrefix + " " + text
    }

    private func handleRecognitionEnded(_ error: Error?) {
        guard state != .idle, state != .suspended else { return }
        if state == .listening, !liveTranscript.trimmingCharacters(in: .whitespaces).isEmpty, error == nil {
            commitUtterance()
            return
        }
        if error != nil {
            // Ochrana proti zacyklení, když rozpoznávání opakovaně selhává (např. bez internetu).
            let now = Date()
            recognizerFailures = recognizerFailures.filter { now.timeIntervalSince($0) < 15 } + [now]
            if recognizerFailures.count > 6 {
                lastError = "Rozpoznávání řeči opakovaně selhává (\(error!.localizedDescription))."
                store.append(.notice, "Relace ukončena: rozpoznávání řeči nefunguje.")
                stop()
                return
            }
            // Pokud už byla zachycena část věty, odešleme ji, ať se neztratí.
            if state == .listening, !liveTranscript.trimmingCharacters(in: .whitespaces).isEmpty {
                commitUtterance()
                return
            }
        }
        // Úloha skončila (časový limit, ticho) → plynule navážeme novou.
        if liveTranscript.isEmpty { utteranceStart = nil }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { [weak self] in
            guard let self, self.state != .idle, self.state != .suspended else { return }
            self.recognizer.startTask()
        }
    }

    private func restartEndpointTimer() {
        endpointTimer?.invalidate()
        endpointTimer = Timer.scheduledTimer(withTimeInterval: silenceTimeout, repeats: false) { [weak self] _ in
            self?.commitUtterance()
        }
    }

    /// Konec promluvy uživatele → odeslat Claudovi.
    private func commitUtterance() {
        endpointTimer?.invalidate()
        guard state == .listening else { return }
        let text = liveTranscript.trimmingCharacters(in: .whitespacesAndNewlines)
        liveTranscript = ""
        utterancePrefix = ""
        guard !text.isEmpty else { return }
        lastActivity = Date()
        let entryID = store.append(.user, text, images: takePendingImages())
        pendingUserEntryID = entryID
        let start = utteranceStart
        lastUtteranceStart = start
        utteranceStart = nil
        // Nová úloha rozpoznávání = čistý start pro detekci přerušení.
        recognizer.startTask()
        state = .thinking
        updateNowPlaying()
        // Přesný přepis: nahrávku promluvy přepíše ElevenLabs; při chybě zůstane přepis z iPhonu.
        guard cloudSTT, CloudQuota.isAvailable(.stt), let start, let wav = recorder.wav(from: start) else {
            sendToClaude()
            return
        }
        sttTask?.cancel()
        sttTask = Task { @MainActor [weak self] in
            let result = await CloudVoice.transcribe(wav)
            guard let self, !Task.isCancelled, self.state == .thinking, self.pendingUserEntryID == entryID else { return }
            switch result {
            case .success(let precise):
                if CloudQuota.wasPaused(.stt) {
                    CloudQuota.markWorking(.stt)
                    self.store.append(.notice, "Přesné rozpoznávání řeči je opět k dispozici.")
                }
                if !precise.isEmpty { self.store.update(id: entryID, text: precise) }
            case .failure(.quotaExhausted):
                if !CloudQuota.wasPaused(.stt) {
                    self.store.append(.notice, "Kredit přesného rozpoznávání je vyčerpán — dočasně rozpoznává iPhone, za 30 minut to zkusím znovu.")
                }
                CloudQuota.markExhausted(.stt)
            default:
                break
            }
            self.sendToClaude()
        }
    }

    /// Začátek promluvy v nahrávce (s rezervou, protože rozpoznávání reaguje se zpožděním).
    private func markUtteranceStart(preRoll: Double = 1.5) {
        utteranceStart = max(0, recorder.position - Int(UtteranceRecorder.sampleRate * preRoll))
    }

    // MARK: - Claude

    private func sendToClaude(speak: Bool = true) {
        let messages = store.apiMessages()
        // Stejný čas pro všechna navazující kola odpovědi (server ho vkládá do zprávy uživatele).
        let now = ClaudeClient.isoNow()
        assistantText = ""
        assistantEntryID = nil
        splitter = SentenceSplitter()
        isNotice = false
        textOnly = !speak
        if speak { speech.begin() }

        responseTask?.cancel()
        responseTask = Task { @MainActor [weak self] in
            do {
                var continuation: [String: Any]?
                // Kalendář a připomínky běží v telefonu → odpověď může mít víc navazujících kol.
                for _ in 0..<4 {
                    guard let self else { return }
                    var toolRequest: (calls: [ClientToolCall], pending: [String: Any])?
                    var firstChunkOfRound = true
                    for try await item in ClaudeClient().stream(messages: messages, now: now, continuation: continuation) {
                        guard !Task.isCancelled else { return }
                        switch item {
                        case .text(var chunk):
                            // Text dalšího kola oddělíme mezerou, ať se věty neslepí.
                            if firstChunkOfRound, !self.assistantText.isEmpty, let c = chunk.first, !c.isWhitespace {
                                chunk = " " + chunk
                            }
                            firstChunkOfRound = false
                            self.handleChunk(chunk, speak: speak)
                        case .clientTools(let calls, let pending):
                            toolRequest = (calls, pending)
                        }
                    }
                    guard let request = toolRequest, !Task.isCancelled else { break }
                    var results = request.pending["server_results"] as? [[String: Any]] ?? []
                    for call in request.calls {
                        let r = await self.deviceTools.run(call)
                        results.append(["tool_use_id": call.id, "content": r.content, "is_error": r.isError])
                    }
                    guard !Task.isCancelled else { return }
                    continuation = ["assistant": request.pending["assistant"] ?? [], "tool_results": results]
                }
                guard let self, !Task.isCancelled else { return }
                if let id = self.assistantEntryID { self.store.update(id: id, text: self.assistantText) }
                self.pendingUserEntryID = nil
                if !speak {
                    self.assistantEntryID = nil
                    self.isTextBusy = false
                    return
                }
                if let rest = self.splitter.flush() { self.speech.enqueue(rest) }
                if self.assistantText.isEmpty {
                    self.speech.stop()
                    self.state = .listening
                } else {
                    self.speech.finishInput()
                }
            } catch {
                guard let self, !Task.isCancelled, !(error is CancellationError) else { return }
                if (error as? URLError)?.code == .cancelled { return }
                self.handleResponseError(error)
            }
        }
    }

    private func handleChunk(_ chunk: String, speak: Bool) {
        assistantText += chunk
        if let id = assistantEntryID {
            store.update(id: id, text: assistantText, persist: false)
        } else {
            assistantEntryID = store.append(.assistant, assistantText)
        }
        if speak {
            for sentence in splitter.append(chunk) { speech.enqueue(sentence) }
        }
    }

    // MARK: - Psaní (když aplikace špatně rozumí nebo nelze mluvit)

    /// Odešle napsanou zprávu. V hlasovém rozhovoru se chová jako vyslovená věta (odpověď hlasem),
    /// mimo něj odpoví Claude jen textem.
    func sendText(_ raw: String) {
        let text = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty || !pendingImages.isEmpty else { return }
        lastError = nil
        lastActivity = Date()
        switch state {
        case .idle:
            if isTextBusy { cancelResponse(keepSpokenPart: false) }
            pendingUserEntryID = store.append(.user, text, images: takePendingImages())
            isTextBusy = true
            sendToClaude(speak: false)
        case .suspended:
            lastError = "Rozhovor je pozastavený (hovor). Zkuste to po jeho skončení."
        case .listening, .thinking, .speaking:
            if state == .speaking || state == .thinking { cancelResponse(keepSpokenPart: true) }
            speech.stop()
            isNotice = false
            noticeCompletion = nil
            endpointTimer?.invalidate()
            liveTranscript = ""
            utterancePrefix = ""
            heardWhileSpeaking = ""
            pendingUserEntryID = store.append(.user, text, images: takePendingImages())
            recognizer.startTask()
            state = .thinking
            updateNowPlaying()
            sendToClaude(speak: true)
        }
    }

    /// Zastaví textovou odpověď (rozepsaná část zůstane v přepisu označená jako přerušená).
    func stopTextResponse() {
        guard isTextBusy else { return }
        responseTask?.cancel()
        responseTask = nil
        if let id = assistantEntryID, !assistantText.isEmpty {
            store.update(id: id, text: assistantText, interrupted: true)
        }
        assistantEntryID = nil
        pendingUserEntryID = nil
        isTextBusy = false
    }

    /// Oprava špatně rozpoznané zprávy: smaže ji i vše po ní a odešle opravené znění.
    func correctAndResend(entryID: UUID, newText: String) {
        if state == .speaking || state == .thinking || isTextBusy {
            cancelResponse(keepSpokenPart: false)
            speech.stop()
            isTextBusy = false
            if state != .idle { state = .listening }
        }
        store.removeFrom(id: entryID)
        sendText(newText)
    }

    private func handleResponseError(_ error: Error) {
        let message = (error as? LocalizedError)?.errorDescription ?? "Spojení se serverem selhalo."
        if textOnly {
            if let id = assistantEntryID, !assistantText.isEmpty {
                store.update(id: id, text: assistantText, interrupted: true)
            }
            assistantEntryID = nil
            store.append(.notice, message)
            lastError = message
            isTextBusy = false
            return
        }
        speech.stop()
        if let id = assistantEntryID, !assistantText.isEmpty {
            store.update(id: id, text: assistantText, interrupted: true)
        }
        store.append(.notice, message)
        lastError = message
        state = .listening
        speakNotice("Omlouvám se, nastala chyba. \(message)")
    }

    private func handleSpeechFinished() {
        if isNotice {
            finishNotice()
            return
        }
        guard state == .speaking || state == .thinking else { return }
        assistantEntryID = nil
        heardWhileSpeaking = ""
        state = .listening
        lastActivity = Date()
        updateNowPlaying()
        // Případné zbytky ozvěny z doby mluvení zahodíme a začneme naslouchat načisto.
        liveTranscript = ""
        utteranceStart = nil
        recognizer.startTask()
    }

    /// Ruční přerušení (tlačítko v aplikaci, na sluchátkách nebo v autě).
    func interrupt() {
        if isNotice {
            speech.stop()
            finishNotice()
            return
        }
        guard state == .speaking || state == .thinking else { return }
        if state == .thinking {
            cancelResponse(keepSpokenPart: false)
            speech.stop()
            state = .listening
        } else {
            interruptAssistant()
        }
        liveTranscript = ""
        recognizer.startTask()
        lastActivity = Date()
    }

    /// Uživatel skočil Claudovi do řeči.
    private func interruptAssistant() {
        heardWhileSpeaking = ""
        cancelResponse(keepSpokenPart: true)
        speech.stop()
        state = .listening
        updateNowPlaying()
    }

    /// Uživatel pokračuje v dotazu, zatímco se čeká na odpověď.
    private func reopenPendingUtterance() {
        cancelResponse(keepSpokenPart: false)
        speech.stop()
        if let id = pendingUserEntryID, let entry = store.entries.first(where: { $0.id == id }) {
            utterancePrefix = entry.text
            if let images = entry.images { pendingImages = images + pendingImages }
            store.remove(id: id)
        }
        // Přesný přepis pak zahrne celou promluvu od jejího původního začátku.
        utteranceStart = lastUtteranceStart
        pendingUserEntryID = nil
        state = .listening
        updateNowPlaying()
    }

    private func cancelResponse(keepSpokenPart: Bool) {
        sttTask?.cancel()
        sttTask = nil
        responseTask?.cancel()
        responseTask = nil
        guard let id = assistantEntryID else { return }
        let spoken = speech.spokenSentences.joined(separator: " ")
        if keepSpokenPart && !spoken.isEmpty {
            store.update(id: id, text: spoken, interrupted: true)
        } else {
            store.remove(id: id)
        }
        assistantEntryID = nil
        pendingUserEntryID = nil
    }

    // MARK: - Krátké hlasové hlášky (neukládají se do konverzace)

    private func speakNotice(_ text: String, completion: (() -> Void)? = nil) {
        isNotice = true
        noticeCompletion = completion
        speech.begin()
        speech.enqueue(text)
        speech.finishInput()
    }

    private func finishNotice() {
        isNotice = false
        let completion = noticeCompletion
        noticeCompletion = nil
        completion?()
    }

    // MARK: - Nečinnost

    private func startIdleTimer() {
        idleTimer?.invalidate()
        idleTimer = Timer.scheduledTimer(withTimeInterval: 15, repeats: true) { [weak self] _ in
            guard let self, self.state == .listening, !self.isNotice, self.idleMinutes > 0 else { return }
            if Date().timeIntervalSince(self.lastActivity) > self.idleMinutes * 60 {
                self.speakNotice("Delší dobu jsem nic neslyšel, ukončuji relaci.") { [weak self] in self?.stop() }
            }
        }
    }

    // MARK: - Telefonní hovor, změny zvukové cesty, zamčená obrazovka

    private func observeSystemNotifications() {
        let nc = NotificationCenter.default
        observers.append(nc.addObserver(forName: AVAudioSession.interruptionNotification, object: nil, queue: .main) { [weak self] note in
            self?.handleInterruption(note)
        })
        observers.append(nc.addObserver(forName: AVAudioSession.routeChangeNotification, object: nil, queue: .main) { [weak self] _ in
            guard let self, self.state != .idle else { return }
            self.routeDescription = self.audio.routeDescription
        })
        observers.append(nc.addObserver(forName: AVAudioSession.mediaServicesWereResetNotification, object: nil, queue: .main) { [weak self] _ in
            guard let self, self.state != .idle else { return }
            self.store.append(.notice, "Zvukový systém iOS se restartoval.")
            self.stop()
        })
        observers.append(nc.addObserver(forName: UIApplication.didBecomeActiveNotification, object: nil, queue: .main) { [weak self] _ in
            // Pokud se po hovoru nepodařilo obnovit na pozadí, zkusíme to při návratu do aplikace.
            guard let self, self.state == .suspended else { return }
            self.resumeAfterSuspension()
        })
    }

    private func handleInterruption(_ note: Notification) {
        guard let raw = note.userInfo?[AVAudioSessionInterruptionTypeKey] as? UInt,
              let type = AVAudioSession.InterruptionType(rawValue: raw) else { return }
        switch type {
        case .began:
            guard state != .idle, state != .suspended else { return }
            needsResend = state == .thinking
            if state == .speaking { cancelResponse(keepSpokenPart: true) } else if state == .thinking {
                responseTask?.cancel(); responseTask = nil
                if let id = assistantEntryID { store.remove(id: id); assistantEntryID = nil }
            }
            speech.stop()
            isNotice = false
            noticeCompletion = nil
            recognizer.cancelTask()
            endpointTimer?.invalidate()
            liveTranscript = ""
            audio.stop()
            state = .suspended
            store.append(.notice, "Rozhovor pozastaven (hovor nebo jiná aplikace).")
            updateNowPlaying()
        case .ended:
            guard state == .suspended else { return }
            // Krátká prodleva — iOS předává zvuk zpět po skončení hovoru.
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) { [weak self] in self?.resumeAfterSuspension() }
        @unknown default:
            break
        }
    }

    private func resumeAfterSuspension(attempt: Int = 0) {
        guard state == .suspended else { return }
        do {
            try startAudio()
        } catch {
            audio.stop()
            if attempt < 5 {
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
                    self?.resumeAfterSuspension(attempt: attempt + 1)
                }
            } else {
                lastError = "Po přerušení se nepodařilo obnovit zvuk. Otevřete aplikaci a pokračujte."
            }
            return
        }
        lastActivity = Date()
        recognizer.startTask()
        store.append(.notice, "Rozhovor obnoven.")
        if needsResend {
            needsResend = false
            state = .thinking
            updateNowPlaying()
            sendToClaude()
        } else {
            state = .listening
            updateNowPlaying()
            speakNotice("Jsem zpátky, můžeme pokračovat.")
        }
    }

    /// Engine se zastavil kvůli změně zvukové cesty (Bluetooth, auto, sluchátka).
    private func handleEngineConfigurationChange() {
        guard state != .idle, state != .suspended else { return }
        // Ochrana proti smyčce restartů.
        guard Date().timeIntervalSince(lastEngineRestart) > 1.0 else {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { [weak self] in self?.handleEngineConfigurationChange() }
            return
        }
        lastEngineRestart = Date()
        if state == .speaking { interruptAssistant() }
        if isNotice { speech.stop(); finishNotice() }
        audio.stop()
        do {
            try audio.start()
            routeDescription = audio.routeDescription
            recognizer.startTask()
        } catch {
            lastError = "Po změně zvukového zařízení se nepodařilo obnovit zvuk: \(error.localizedDescription)"
            stop()
        }
    }

    // MARK: - Zamčená obrazovka a tlačítka sluchátek

    private func setupRemoteCommands() {
        let center = MPRemoteCommandCenter.shared()
        // Tlačítko na sluchátkách / v autě / na zamčené obrazovce: přeruší odpověď nebo ukončí relaci.
        for command in [center.pauseCommand, center.togglePlayPauseCommand, center.stopCommand] {
            command.isEnabled = true
            command.removeTarget(nil)
            command.addTarget { [weak self] _ in
                guard let self else { return .success }
                // Během odpovědi tlačítko Clauda jen utne, jinak relaci ukončí.
                if self.state == .speaking || self.state == .thinking || self.isNotice {
                    self.interrupt()
                } else {
                    self.stop()
                }
                return .success
            }
        }
        center.playCommand.isEnabled = false
    }

    private func teardownRemoteCommands() {
        let center = MPRemoteCommandCenter.shared()
        for command in [center.pauseCommand, center.togglePlayPauseCommand, center.stopCommand] {
            command.removeTarget(nil)
        }
        MPNowPlayingInfoCenter.default().nowPlayingInfo = nil
    }

    private func updateNowPlaying() {
        guard state != .idle else { return }
        MPNowPlayingInfoCenter.default().nowPlayingInfo = [
            MPMediaItemPropertyTitle: "Claude",
            MPMediaItemPropertyArtist: stateLabel,
            MPNowPlayingInfoPropertyPlaybackRate: 1.0,
        ]
    }

    var stateLabel: String {
        switch state {
        case .idle: return "Připraveno"
        case .listening: return "Poslouchám"
        case .thinking: return "Přemýšlím"
        case .speaking: return "Mluvím"
        case .suspended: return "Pozastaveno"
        }
    }
}

/// Klíče nastavení (sdílené mezi VoiceSession a SettingsView).
enum SettingsKey {
    static let silenceTimeout = "silenceTimeout"
    static let bargeIn = "bargeIn"
    static let idleMinutes = "idleMinutes"
    static let voiceID = "voiceID"
    static let speechRate = "speechRate"
    static let preferOnDevice = "preferOnDevice"
    static let cloudVoice = "cloudVoice"
    static let cloudSTT = "cloudSTT"
}
