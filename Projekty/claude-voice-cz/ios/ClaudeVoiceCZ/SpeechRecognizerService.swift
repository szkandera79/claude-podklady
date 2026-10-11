import AVFoundation
import Speech

/// Rozpoznávání české řeči (Apple Speech).
/// Mikrofon dodává zvuk průběžně; úlohy rozpoznávání se střídají (po každé promluvě nová úloha).
final class SpeechRecognizerService {
    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "cs-CZ"))
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private let lock = NSLock()
    private var taskID = 0

    /// Upřednostnit rozpoznávání přímo v telefonu (rychlejší, offline), pokud ho iOS pro češtinu nabízí.
    /// Výchozí VYPNUTO: serverové rozpoznávání Applu je pro češtinu přesnější.
    var preferOnDevice = false
    /// Průběžný / konečný výsledek (hlavní vlákno).
    var onResult: ((_ text: String, _ isFinal: Bool) -> Void)?
    /// Úloha skončila (konečný výsledek, chyba nebo časový limit) — hlavní vlákno.
    var onTaskEnded: ((Error?) -> Void)?

    init() {
        recognizer?.defaultTaskHint = .dictation
    }

    var isAvailable: Bool { recognizer?.isAvailable ?? false }
    var supportsOnDevice: Bool { recognizer?.supportsOnDeviceRecognition ?? false }
    var usesOnDevice: Bool { preferOnDevice && supportsOnDevice }

    static func requestAuthorization() async -> Bool {
        await withCheckedContinuation { cont in
            SFSpeechRecognizer.requestAuthorization { cont.resume(returning: $0 == .authorized) }
        }
    }

    /// Volá se ze zvukového vlákna.
    func append(_ buffer: AVAudioPCMBuffer) {
        lock.lock()
        let req = request
        lock.unlock()
        req?.append(buffer)
    }

    /// Zahájí novou úlohu rozpoznávání (předchozí zruší). Volat na hlavním vlákně.
    func startTask() {
        cancelTask()
        guard let recognizer, recognizer.isAvailable else {
            let err = NSError(domain: "ClaudeVoiceCZ", code: 2,
                              userInfo: [NSLocalizedDescriptionKey: "Rozpoznávání češtiny není momentálně dostupné."])
            DispatchQueue.main.async { self.onTaskEnded?(err) }
            return
        }
        let req = SFSpeechAudioBufferRecognitionRequest()
        req.shouldReportPartialResults = true
        req.taskHint = .dictation
        req.addsPunctuation = true
        req.requiresOnDeviceRecognition = usesOnDevice
        // Odborné a vlastní výrazy uživatele — zvyšují šanci, že je rozpoznávání zachytí správně.
        req.contextualStrings = [
            "Claude", "Claude Code", "GitHub", "Anthropic", "ThermaVera", "REO HEATING", "REO", "R290 Smart",
            "RH X50", "RH X40", "RH060", "tepelné čerpadlo", "tepelná čerpadla", "kotelna", "zelená kotelna",
            "kaskáda", "akumulace", "akumulační nádrž", "ohřev teplé vody", "TUV", "ÚT", "SVJ", "bytový dům",
            "bytové družstvo", "CZT", "teplárna", "fotovoltaika", "bivalence", "topná křivka", "COP", "SCOP",
            "kilowatt", "megawatthodina", "návratnost", "dotace", "Nová zelená úsporám", "ETS2", "Veolia",
            "BD Michal", "Jandova", "Ostrava", "Zábřeh", "Michálkovice", "web4u", "Cloudflare",
        ]

        taskID += 1
        let id = taskID
        lock.lock()
        request = req
        lock.unlock()

        task = recognizer.recognitionTask(with: req) { [weak self] result, error in
            let text = result?.bestTranscription.formattedString
            let isFinal = result?.isFinal ?? false
            DispatchQueue.main.async {
                guard let self, id == self.taskID else { return }
                if let text { self.onResult?(text, isFinal) }
                if error != nil || isFinal {
                    self.lock.lock()
                    self.request = nil
                    self.lock.unlock()
                    self.task = nil
                    self.onTaskEnded?(error)
                }
            }
        }
    }

    func cancelTask() {
        taskID += 1
        lock.lock()
        request?.endAudio()
        request = nil
        lock.unlock()
        task?.cancel()
        task = nil
    }
}
