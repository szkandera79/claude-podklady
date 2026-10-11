import AVFoundation
import SwiftUI

struct SettingsView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var session: VoiceSession

    @State private var serverURL = AppConfig.serverURL
    @State private var token = AppConfig.appToken
    @State private var usageText: String?

    @AppStorage(SettingsKey.silenceTimeout) private var silenceTimeout = 1.2
    @AppStorage(SettingsKey.bargeIn) private var bargeIn = true
    @AppStorage(SettingsKey.idleMinutes) private var idleMinutes = 10.0
    @AppStorage(SettingsKey.voiceID) private var voiceID = ""
    @AppStorage(SettingsKey.speechRate) private var speechRate = Double(AVSpeechUtteranceDefaultSpeechRate)
    @AppStorage(SettingsKey.preferOnDevice) private var preferOnDevice = false
    @AppStorage(SettingsKey.cloudVoice) private var cloudVoice = true
    @AppStorage(SettingsKey.cloudSTT) private var cloudSTT = true

    private let voices = SpeechOutput.czechVoices()

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("https://…workers.dev", text: $serverURL)
                        .keyboardType(.URL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    SecureField("Přístupový token aplikace", text: $token)
                    Button("Zjistit dnešní spotřebu") { Task { await loadUsage() } }
                    if let usageText { Text(usageText).font(.footnote).foregroundStyle(.secondary) }
                } header: {
                    Text("Server")
                } footer: {
                    Text("Token aplikace není API klíč Anthropicu — ten je bezpečně jen na serveru. Token je uložen v Klíčence iPhonu.")
                }

                if let expiry = InstallExpiry.expirationDate {
                    Section {
                        LabeledContent("Instalace platí do", value: expiry.formatted(date: .abbreviated, time: .shortened))
                    } footer: {
                        Text("Před vypršením přijde upozornění. Stačí pak připojit iPhone kabelem k Macu a odemknout ho — Mac aplikaci obnoví sám.")
                    }
                }

                Section("Konverzace") {
                    VStack(alignment: .leading) {
                        Text("Konec promluvy po tichu: \(silenceTimeout, specifier: "%.1f") s")
                        Slider(value: $silenceTimeout, in: 0.6...3.0, step: 0.1)
                    }
                    Toggle("Přerušovat Clauda vlastní řečí", isOn: $bargeIn)
                    VStack(alignment: .leading) {
                        Text(idleMinutes == 0 ? "Automatické ukončení: vypnuto" : "Ukončit po \(Int(idleMinutes)) min ticha")
                        Slider(value: $idleMinutes, in: 0...30, step: 1)
                    }
                }

                Section {
                    Toggle("Přirozený hlas (ElevenLabs)", isOn: $cloudVoice)
                    Toggle("Přesné rozpoznávání řeči (ElevenLabs)", isOn: $cloudSTT)
                } header: {
                    Text("Kvalita hlasu")
                } footer: {
                    Text("Placená služba podle spotřeby (tarif ElevenLabs). Když kredit dojde nebo služba nejde, aplikace sama přejde na hlas a rozpoznávání iPhonu. Spotřebu ukáže tlačítko „Zjistit dnešní spotřebu“.")
                }

                Section {
                    Picker("Hlas iPhonu (záložní)", selection: $voiceID) {
                        Text("Automaticky (nejlepší)").tag("")
                        ForEach(voices, id: \.identifier) { v in
                            Text("\(v.name) – \(qualityName(v.quality))").tag(v.identifier)
                        }
                    }
                    VStack(alignment: .leading) {
                        Text("Rychlost řeči")
                        Slider(value: $speechRate, in: 0.35...0.65)
                    }
                    Toggle("Rozpoznávat řeč offline v telefonu (méně přesné)", isOn: $preferOnDevice)
                } header: {
                    Text("Hlas a řeč")
                } footer: {
                    Text("Kvalitnější český hlas stáhnete v Nastavení iPhonu → Zpřístupnění → Předčítání obsahu → Hlasy → Čeština (např. Zuzana – vylepšená). Změny se projeví při dalším zahájení rozhovoru.")
                }
            }
            .navigationTitle("Nastavení")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Hotovo") { save(); dismiss() }
                }
            }
        }
    }

    private func save() {
        AppConfig.serverURL = serverURL
        AppConfig.appToken = token
    }

    private func qualityName(_ q: AVSpeechSynthesisVoiceQuality) -> String {
        switch q {
        case .premium: return "prémiový"
        case .enhanced: return "vylepšený"
        default: return "základní"
        }
    }

    private func loadUsage() async {
        save()
        guard let url = URL(string: AppConfig.serverURL)?.appendingPathComponent("v1/usage") else { return }
        var req = URLRequest(url: url)
        req.setValue("Bearer \(AppConfig.appToken)", forHTTPHeaderField: "Authorization")
        do {
            let (data, resp) = try await URLSession.shared.data(for: req)
            guard (resp as? HTTPURLResponse)?.statusCode == 200,
                  let obj = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                usageText = "Server odpověděl chybou — zkontrolujte adresu a token."
                return
            }
            let today = obj["today"] as? Int ?? 0
            let limit = obj["limit"] as? Int ?? 0
            var text = "Claude dnes: \(today.formatted()) z \(limit.formatted()) tokenů"
            if let v = obj["voice"] as? [String: Any], v["enabled"] as? Bool == true {
                let chars = v["tts_chars"] as? Int ?? 0, charLimit = v["tts_limit"] as? Int ?? 0
                let secs = v["stt_seconds"] as? Int ?? 0
                text += "\nHlas tento měsíc: \(chars.formatted()) z \(charLimit.formatted()) znaků · rozpoznávání \(secs / 60) min"
            }
            usageText = text
        } catch {
            usageText = "Server nedostupný: \(error.localizedDescription)"
        }
    }
}
