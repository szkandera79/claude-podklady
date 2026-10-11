import AVFoundation

/// Správa zvuku: audio relace iOS, mikrofon a přehrávání hlasu přes jeden AVAudioEngine.
///
/// Přehrávání i nahrávání běží přes stejný engine se zapnutým „voice processing",
/// takže iOS potlačí ozvěnu: mikrofon „neslyší" Claudův hlas z reproduktoru.
/// To je podmínka pro spolehlivé přerušení odpovědi vlastní řečí.
final class AudioController {
    private let engine = AVAudioEngine()
    private let player = AVAudioPlayerNode()
    /// Jednotný formát, do kterého převádíme hlas syntézy před přehráním.
    let playbackFormat = AVAudioFormat(standardFormatWithSampleRate: 24_000, channels: 1)!

    /// Volá se na zvukovém vlákně s každým blokem z mikrofonu (mono).
    var onInputBuffer: ((AVAudioPCMBuffer) -> Void)?
    /// Engine se zastavil kvůli změně zvukové cesty (např. připojení Bluetooth). Volá se na hlavním vlákně.
    var onConfigurationChange: (() -> Void)?

    private(set) var isRunning = false
    private var inputConverter: AVAudioConverter?
    private var playbackConverter: AVAudioConverter?
    private var configObserver: NSObjectProtocol?

    init() {
        engine.attach(player)
        configObserver = NotificationCenter.default.addObserver(
            forName: .AVAudioEngineConfigurationChange, object: engine, queue: .main
        ) { [weak self] _ in
            guard let self, self.isRunning else { return }
            self.isRunning = false
            self.onConfigurationChange?()
        }
    }

    deinit {
        if let configObserver { NotificationCenter.default.removeObserver(configObserver) }
    }

    // MARK: Audio relace

    func activateSession() throws {
        let session = AVAudioSession.sharedInstance()
        // playAndRecord + voiceChat: obousměrný hovor, potlačení ozvěny, Bluetooth (HFP) a autorádio.
        // Background mode „audio" v Info.plist zajistí běh i při zamčené obrazovce.
        try session.setCategory(
            .playAndRecord,
            mode: .voiceChat,
            options: [.allowBluetoothHFP, .allowBluetoothA2DP, .defaultToSpeaker]
        )
        try? session.setPreferredIOBufferDuration(0.02)
        try session.setActive(true)
    }

    func deactivateSession() {
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }

    /// Popis aktuální zvukové cesty pro zobrazení v aplikaci.
    var routeDescription: String {
        let route = AVAudioSession.sharedInstance().currentRoute
        let output = route.outputs.first?.portName ?? "–"
        let input = route.inputs.first?.portName ?? "–"
        return output == input ? output : "\(input) → \(output)"
    }

    // MARK: Engine

    func start() throws {
        guard !isRunning else { return }
        let input = engine.inputNode
        if !input.isVoiceProcessingEnabled {
            try input.setVoiceProcessingEnabled(true)
        }
        // Neztlumovat zbytečně ostatní zvuk víc, než je nutné.
        input.voiceProcessingOtherAudioDuckingConfiguration =
            AVAudioVoiceProcessingOtherAudioDuckingConfiguration(enableAdvancedDucking: false, duckingLevel: .min)

        engine.connect(player, to: engine.mainMixerNode, format: playbackFormat)

        let inFormat = input.outputFormat(forBus: 0)
        guard inFormat.sampleRate > 0, inFormat.channelCount > 0 else {
            throw NSError(domain: "ClaudeVoiceCZ", code: 1,
                          userInfo: [NSLocalizedDescriptionKey: "Mikrofon není dostupný."])
        }
        // S voice processingem může mít vstup víc kanálů → převedeme na mono.
        let mono = AVAudioFormat(standardFormatWithSampleRate: inFormat.sampleRate, channels: 1)!
        inputConverter = inFormat.channelCount == 1 ? nil : AVAudioConverter(from: inFormat, to: mono)

        input.removeTap(onBus: 0)
        input.installTap(onBus: 0, bufferSize: 1024, format: inFormat) { [weak self] buffer, _ in
            guard let self else { return }
            if let converter = self.inputConverter {
                guard let out = AVAudioPCMBuffer(pcmFormat: mono, frameCapacity: buffer.frameLength) else { return }
                do {
                    try converter.convert(to: out, from: buffer)
                    self.onInputBuffer?(out)
                } catch {
                    return
                }
            } else {
                self.onInputBuffer?(buffer)
            }
        }

        engine.prepare()
        try engine.start()
        player.play()
        isRunning = true
    }

    func stop() {
        isRunning = false
        engine.inputNode.removeTap(onBus: 0)
        player.stop()
        engine.stop()
    }

    // MARK: Přehrávání

    /// Naplánuje blok zvuku k přehrání; `completion` se zavolá po jeho dohrání (na libovolném vlákně).
    func schedule(_ buffer: AVAudioPCMBuffer, completion: @escaping () -> Void) {
        guard isRunning else { completion(); return }
        player.scheduleBuffer(buffer, completionCallbackType: .dataPlayedBack) { _ in completion() }
        if !player.isPlaying { player.play() }
    }

    /// Okamžitě utne přehrávaný hlas (při přerušení uživatelem).
    func stopPlayback() {
        player.stop()
        playbackConverter?.reset()
        if isRunning { player.play() }
    }

    /// Převede blok ze syntézy řeči do formátu přehrávače (vzorkovací frekvence, typ vzorků).
    func convertForPlayback(_ buffer: AVAudioPCMBuffer) -> AVAudioPCMBuffer? {
        if buffer.format == playbackFormat { return buffer }
        if playbackConverter == nil || playbackConverter?.inputFormat != buffer.format {
            playbackConverter = AVAudioConverter(from: buffer.format, to: playbackFormat)
        }
        guard let converter = playbackConverter else { return nil }
        let ratio = playbackFormat.sampleRate / buffer.format.sampleRate
        let capacity = AVAudioFrameCount(Double(buffer.frameLength) * ratio) + 1024
        guard let out = AVAudioPCMBuffer(pcmFormat: playbackFormat, frameCapacity: capacity) else { return nil }
        var supplied = false
        var error: NSError?
        let status = converter.convert(to: out, error: &error) { _, inputStatus in
            if supplied {
                inputStatus.pointee = .noDataNow
                return nil
            }
            supplied = true
            inputStatus.pointee = .haveData
            return buffer
        }
        if status == .error || out.frameLength == 0 { return nil }
        return out
    }
}
