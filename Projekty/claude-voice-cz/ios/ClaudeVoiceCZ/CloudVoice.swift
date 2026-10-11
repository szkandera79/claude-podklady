import AVFoundation
import Foundation

/// Přirozený hlas a přesné rozpoznávání řeči přes server (ElevenLabs).
enum CloudVoice {
    enum Failure: Error { case quotaExhausted, unavailable }

    /// Text → PCM 16 bit, 24 kHz, mono.
    static func speech(_ text: String) async -> Result<Data, Failure> {
        guard let url = URL(string: AppConfig.serverURL)?.appendingPathComponent("v1/tts") else { return .failure(.unavailable) }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 15
        request.setValue("Bearer \(AppConfig.appToken)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: ["text": text])
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            let status = (response as? HTTPURLResponse)?.statusCode ?? 0
            if status == 429 { return .failure(.quotaExhausted) }
            guard status == 200, data.count > 100 else { return .failure(.unavailable) }
            return .success(data)
        } catch {
            return .failure(.unavailable)
        }
    }

    /// WAV (16 kHz mono) → text. Vrací nil při chybě (pak se použije přepis z iPhonu).
    static func transcribe(_ wav: Data) async -> Result<String, Failure> {
        guard let url = URL(string: AppConfig.serverURL)?.appendingPathComponent("v1/stt") else { return .failure(.unavailable) }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 12
        request.setValue("Bearer \(AppConfig.appToken)", forHTTPHeaderField: "Authorization")
        request.setValue("audio/wav", forHTTPHeaderField: "Content-Type")
        request.httpBody = wav
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            let status = (response as? HTTPURLResponse)?.statusCode ?? 0
            if status == 429 { return .failure(.quotaExhausted) }
            guard status == 200,
                  let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let text = obj["text"] as? String else { return .failure(.unavailable) }
            return .success(text)
        } catch {
            return .failure(.unavailable)
        }
    }

    /// Převod PCM 16 bit LE na buffer pro přehrávač (Float32, stejná vzorkovací frekvence).
    static func pcmBuffer(_ data: Data, format: AVAudioFormat) -> AVAudioPCMBuffer? {
        let samples = data.count / 2
        guard samples > 0, let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: AVAudioFrameCount(samples)),
              let channel = buffer.floatChannelData?[0] else { return nil }
        data.withUnsafeBytes { raw in
            let src = raw.bindMemory(to: Int16.self)
            for i in 0..<samples { channel[i] = Float(Int16(littleEndian: src[i])) / 32768 }
        }
        buffer.frameLength = AVAudioFrameCount(samples)
        return buffer
    }
}

/// Průběžně ukládá zvuk z mikrofonu (16 kHz, mono, posledních 90 s), aby šla poslat nahrávka promluvy k přepisu.
final class UtteranceRecorder {
    static let sampleRate: Double = 16_000
    private let maxSamples = Int(16_000 * 90)
    private let target = AVAudioFormat(commonFormat: .pcmFormatInt16, sampleRate: 16_000, channels: 1, interleaved: true)!
    private var converter: AVAudioConverter?
    private var samples: [Int16] = []
    private var dropped = 0 // kolik vzorků bylo zahozeno ze začátku (absolutní pozice = dropped + index)
    private let lock = NSLock()

    /// Absolutní pozice (počet vzorků od startu).
    var position: Int {
        lock.lock(); defer { lock.unlock() }
        return dropped + samples.count
    }

    func reset() {
        lock.lock()
        samples.removeAll(keepingCapacity: true)
        dropped = 0
        lock.unlock()
    }

    /// Volá se ze zvukového vlákna.
    func append(_ buffer: AVAudioPCMBuffer) {
        if converter == nil || converter?.inputFormat != buffer.format {
            converter = AVAudioConverter(from: buffer.format, to: target)
        }
        guard let converter else { return }
        let capacity = AVAudioFrameCount(Double(buffer.frameLength) * 16_000 / buffer.format.sampleRate) + 32
        guard let out = AVAudioPCMBuffer(pcmFormat: target, frameCapacity: capacity) else { return }
        var supplied = false
        var error: NSError?
        converter.convert(to: out, error: &error) { _, status in
            if supplied { status.pointee = .noDataNow; return nil }
            supplied = true
            status.pointee = .haveData
            return buffer
        }
        guard out.frameLength > 0, let ptr = out.int16ChannelData?[0] else { return }
        lock.lock()
        samples.append(contentsOf: UnsafeBufferPointer(start: ptr, count: Int(out.frameLength)))
        if samples.count > maxSamples {
            let extra = samples.count - maxSamples
            samples.removeFirst(extra)
            dropped += extra
        }
        lock.unlock()
    }

    /// Nahrávka od zadané pozice do teď jako WAV. Nil, když je moc krátká.
    func wav(from start: Int) -> Data? {
        lock.lock()
        let from = max(0, start - dropped)
        let slice = from < samples.count ? Array(samples[from...]) : []
        lock.unlock()
        guard slice.count > Int(Self.sampleRate * 0.4) else { return nil }
        return Self.wavData(slice)
    }

    static func wavData(_ pcm: [Int16]) -> Data {
        var d = Data()
        func u32(_ v: UInt32) { var x = v.littleEndian; d.append(Data(bytes: &x, count: 4)) }
        func u16(_ v: UInt16) { var x = v.littleEndian; d.append(Data(bytes: &x, count: 2)) }
        let bytes = UInt32(pcm.count * 2)
        d.append("RIFF".data(using: .ascii)!); u32(36 + bytes)
        d.append("WAVEfmt ".data(using: .ascii)!); u32(16); u16(1); u16(1)
        u32(16_000); u32(32_000); u16(2); u16(16)
        d.append("data".data(using: .ascii)!); u32(bytes)
        pcm.withUnsafeBufferPointer { d.append(Data(buffer: $0)) }
        return d
    }
}

/// Pamatuje si, že kredit ElevenLabs došel, a po 30 minutách dovolí nový pokus
/// (kredit se obnoví s novým fakturačním obdobím — pak se služba zase použije sama).
enum CloudQuota {
    enum Service: String { case voice, stt }
    static let retryInterval: TimeInterval = 30 * 60

    private static func key(_ s: Service) -> String { "cloudPausedUntil.\(s.rawValue)" }

    /// Smí se služba teď použít?
    static func isAvailable(_ s: Service) -> Bool {
        guard let until = UserDefaults.standard.object(forKey: key(s)) as? Date else { return true }
        return Date() >= until
    }

    /// Byla služba pozastavená (kvůli kreditu) — pro hlášku „opět k dispozici“.
    static func wasPaused(_ s: Service) -> Bool {
        UserDefaults.standard.object(forKey: key(s)) != nil
    }

    static func markExhausted(_ s: Service) {
        UserDefaults.standard.set(Date().addingTimeInterval(retryInterval), forKey: key(s))
    }

    static func markWorking(_ s: Service) {
        UserDefaults.standard.removeObject(forKey: key(s))
    }
}
