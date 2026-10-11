import AVFoundation

/// Česká hlasová syntéza (Apple). Věty se syntetizují postupně, jak přicházejí ze streamu,
/// a přehrávají se přes AudioController (kvůli potlačení ozvěny). Vše na hlavním vlákně.
final class SpeechOutput: NSObject, AVSpeechSynthesizerDelegate, @unchecked Sendable {
    private let synthesizer = AVSpeechSynthesizer()
    private let audio: AudioController

    private var queue: [String] = []
    private var currentUtterance: AVSpeechUtterance?
    private var pendingBuffers = 0
    private var generation = 0
    private var inputClosed = true
    private var didNotifyStart = false
    private var didNotifyFinish = true

    /// Věty, které už zazněly (pro uložení vyslovené části při přerušení).
    private(set) var spokenSentences: [String] = []

    var voiceIdentifier: String?
    /// 0.0–1.0, výchozí rychlost řeči iOS je 0.5.
    var rate: Float = AVSpeechUtteranceDefaultSpeechRate

    var onStartedSpeaking: (() -> Void)?
    var onFinished: (() -> Void)?

    init(audio: AudioController) {
        self.audio = audio
        super.init()
        synthesizer.delegate = self
        synthesizer.usesApplicationAudioSession = true
    }

    static func czechVoices() -> [AVSpeechSynthesisVoice] {
        AVSpeechSynthesisVoice.speechVoices()
            .filter { $0.language.hasPrefix("cs") }
            .sorted { $0.quality.rawValue > $1.quality.rawValue }
    }

    private var voice: AVSpeechSynthesisVoice? {
        if let id = voiceIdentifier, !id.isEmpty, let v = AVSpeechSynthesisVoice(identifier: id) { return v }
        return Self.czechVoices().first ?? AVSpeechSynthesisVoice(language: "cs-CZ")
    }

    var isActive: Bool { !didNotifyFinish }

    /// Začátek nové odpovědi.
    func begin() {
        stop()
        generation += 1
        inputClosed = false
        didNotifyStart = false
        didNotifyFinish = false
        spokenSentences = []
    }

    func enqueue(_ sentence: String) {
        let text = sentence.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty, !didNotifyFinish else { return }
        queue.append(text)
        pump()
    }

    /// Stream skončil — po dohrání fronty se zavolá onFinished.
    func finishInput() {
        inputClosed = true
        checkDone()
    }

    /// Okamžité ukončení (přerušení).
    func stop() {
        generation += 1
        queue.removeAll()
        currentUtterance = nil
        pendingBuffers = 0
        inputClosed = true
        didNotifyFinish = true
        if synthesizer.isSpeaking { synthesizer.stopSpeaking(at: .immediate) }
        audio.stopPlayback()
    }

    private func pump() {
        guard currentUtterance == nil, !queue.isEmpty else { return }
        let text = queue.removeFirst()
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = voice
        utterance.rate = rate
        utterance.prefersAssistiveTechnologySettings = false
        currentUtterance = utterance

        let gen = generation
        var isFirstBuffer = true
        synthesizer.write(utterance) { [weak self] buffer in
            DispatchQueue.main.async {
                guard let self, gen == self.generation else { return }
                guard let pcm = buffer as? AVAudioPCMBuffer, pcm.frameLength > 0 else {
                    // Prázdný blok = syntéza této věty skončila.
                    self.utteranceFinished(utterance)
                    return
                }
                guard let out = self.audio.convertForPlayback(pcm) else { return }
                let first = isFirstBuffer
                isFirstBuffer = false
                self.pendingBuffers += 1
                self.audio.schedule(out) { [weak self] in
                    DispatchQueue.main.async {
                        guard let self, gen == self.generation else { return }
                        self.pendingBuffers -= 1
                        if first { self.spokenSentences.append(text) }
                        self.checkDone()
                    }
                }
                if !self.didNotifyStart {
                    self.didNotifyStart = true
                    self.onStartedSpeaking?()
                }
            }
        }
    }

    private func utteranceFinished(_ utterance: AVSpeechUtterance) {
        guard currentUtterance === utterance else { return }
        currentUtterance = nil
        pump()
        checkDone()
    }

    private func checkDone() {
        guard !didNotifyFinish, inputClosed, queue.isEmpty, currentUtterance == nil, pendingBuffers == 0 else { return }
        didNotifyFinish = true
        onFinished?()
    }

    // Pojistka: některé verze iOS nemusí poslat závěrečný prázdný blok.
    // Zpoždění zajistí, že dřív dorazí všechny bloky zvuku této věty.
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { self.utteranceFinished(utterance) }
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        DispatchQueue.main.async { self.utteranceFinished(utterance) }
    }
}
