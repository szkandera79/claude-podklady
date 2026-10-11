// Testy logiky, které nepotřebují iPhone ani Xcode.
// Spuštění: ./LogicTests/run.sh
import AVFoundation
import Foundation

var failures = 0
func check(_ cond: Bool, _ msg: String, line: Int = #line) {
    if cond { print("  ✓ \(msg)") } else { print("  ✗ \(msg) (řádek \(line))"); failures += 1 }
}

func split(_ chunks: [String]) -> [String] {
    var s = SentenceSplitter()
    var out: [String] = []
    for c in chunks { out += s.append(c) }
    if let rest = s.flush() { out.append(rest) }
    return out
}

print("SentenceSplitter")
check(split(["Dobrý den, jak se máte? ", "Já se mám dobře."]) == ["Dobrý den, jak se máte?", "Já se mám dobře."], "dvě věty")
check(split(["Dob", "rý den, ", "jak se m", "áte? Já ", "dobře, díky."]) == ["Dobrý den, jak se máte?", "Já dobře, díky."], "věty rozdělené přes více kusů streamu")
check(split(["Schůzka je 15. března v Praze, např. v kanceláři. Pak pojedeme dál."])
      == ["Schůzka je 15. března v Praze, např. v kanceláři.", "Pak pojedeme dál."], "zkratky a data nerozdělují větu")
check(split(["Ano. Rozumím vám dobře."]) == ["Ano. Rozumím vám dobře."], "velmi krátká věta se spojí s další")
check(split(["Cena je 3.5 milionu korun. To je hodně."]) == ["Cena je 3.5 milionu korun.", "To je hodně."], "desetinné číslo")
check(split(["Napsal to J. Novák minulý týden. Opravdu."]) == ["Napsal to J. Novák minulý týden.", "Opravdu."], "iniciála")
do {
    var s = SentenceSplitter()
    check(s.append("Tohle je věta bez konce") == [], "nedokončená věta se nevydá předčasně")
    check(s.append(".") == [], "tečka na konci streamu ještě nestačí")
    check(s.flush() == "Tohle je věta bez konce.", "flush vrátí zbytek")
}

print("SSEParser")
check(SSEParser.parse(line: #"data: {"type":"text","text":"Ahoj"}"#) == .text("Ahoj"), "text")
check(SSEParser.parse(line: #"data: {"type":"done","stop_reason":"end_turn","usage":{}}"#) == .done(stopReason: "end_turn"), "done")
check(SSEParser.parse(line: #"data: {"type":"error","message":"Chyba"}"#) == .error("Chyba"), "error")
check(SSEParser.parse(line: ": keepalive") == nil, "komentář se ignoruje")
check(SSEParser.parse(line: "data: nejson") == nil, "neplatný JSON se ignoruje")

print("ConversationStore.apiMessages")
typealias E = TranscriptEntry
func role(_ m: [String: Any]) -> String { m["role"] as? String ?? "?" }
func text(_ m: [String: Any]) -> String { m["content"] as? String ?? "" }
let msgs = ConversationStore.apiMessages(from: [
    E(role: .assistant, text: "úvod"),
    E(role: .user, text: "Ahoj"),
    E(role: .notice, text: "Chyba sítě"),
    E(role: .user, text: "Slyšíš mě?"),
    E(role: .assistant, text: "Ano, slyším", interrupted: true),
    E(role: .user, text: "Super"),
    E(role: .assistant, text: "nedokončeno"),
])
check(msgs.map(role) == ["user", "assistant", "user"], "střídání rolí, začíná i končí uživatelem")
check(text(msgs[0]) == "Ahoj\nSlyšíš mě?", "sloučení po sobě jdoucích zpráv a vynechání hlášek")
check(text(msgs[1]).contains("přerušil"), "přerušená odpověď je označena")
do {
    var many: [E] = []
    for i in 0..<200 { many.append(E(role: i % 2 == 0 ? .user : .assistant, text: "zpráva \(i)")) }
    many.append(E(role: .user, text: "poslední"))
    let trimmed = ConversationStore.apiMessages(from: many)
    check(trimmed.count <= ConversationStore.maxContextMessages, "oříznutí dlouhé konverzace")
    check(role(trimmed.first!) == "user" && text(trimmed.last!) == "poslední", "po oříznutí začíná uživatelem a drží poslední zprávu")
}

print("Fotky ve zprávách")
do {
    let loader: (String) -> String? = { name in "B64-\(name)" }
    let withPhoto = ConversationStore.apiMessages(from: [E(role: .user, text: "", images: ["a.jpg"])], imageLoader: loader)
    let parts = withPhoto[0]["content"] as? [[String: Any]] ?? []
    check(parts.count == 2 && parts[0]["type"] as? String == "image" && parts[0]["data"] as? String == "B64-a.jpg", "fotka jako obrázek v API")
    check(parts.last?["text"] as? String == "Co je na fotce?", "fotka bez textu dostane výchozí otázku")
    var long: [E] = [E(role: .user, text: "stará fotka", images: ["old.jpg"])]
    for i in 0..<8 { long.append(E(role: i % 2 == 0 ? .assistant : .user, text: "z\(i)")) }
    long.append(E(role: .user, text: "nová", images: ["new.jpg"]))
    let api = ConversationStore.apiMessages(from: long, imageLoader: loader)
    check(text(api[0]).contains("[Uživatel poslal fotku.]"), "starší fotka se nahradí zmínkou")
    check((api.last?["content"] as? [[String: Any]])?.first?["data"] as? String == "B64-new.jpg", "nejnovější fotka se posílá")
}

print("Více konverzací")
do {
    let dir = FileManager.default.temporaryDirectory.appendingPathComponent("cvtest-\(UUID().uuidString)")
    try? FileManager.default.createDirectory(at: dir.appendingPathComponent("images"), withIntermediateDirectories: true)
    let store = ConversationStore(baseDir: dir)
    check(store.conversations.count == 1 && store.entries.isEmpty, "začíná jednou prázdnou konverzací")
    store.append(.user, "První dotaz o kotelně")
    let first = store.currentID
    store.newConversation()
    store.newConversation()
    check(store.conversations.count == 2, "prázdná konverzace se nezdvojuje")
    store.append(.user, "Druhý dotaz")
    store.open(first)
    check(store.entries.first?.text == "První dotaz o kotelně", "otevření starší konverzace")
    let reloaded = ConversationStore(baseDir: dir)
    check(reloaded.conversations.count == 2 && reloaded.conversations.contains { $0.title == "Druhý dotaz" }, "konverzace přežijí restart, názvy podle první zprávy")
    store.delete(first)
    check(store.conversations.count == 1 && store.entries.first?.text == "Druhý dotaz", "smazání aktuální konverzace přepne na další")
    try? FileManager.default.removeItem(at: dir)
}

print("Zvuk pro ElevenLabs")
do {
    let wav = UtteranceRecorder.wavData([0, 1000, -1000, 32767])
    check(wav.count == 44 + 8, "WAV má hlavičku 44 B + data")
    check(String(data: wav.prefix(4), encoding: .ascii) == "RIFF" && String(data: wav[8..<16], encoding: .ascii) == "WAVEfmt ", "WAV hlavička RIFF/WAVE")
    let rate = wav[24..<28].withUnsafeBytes { $0.loadUnaligned(as: UInt32.self) }
    check(UInt32(littleEndian: rate) == 16_000, "WAV 16 kHz")
    let fmt = AVAudioFormat(standardFormatWithSampleRate: 24_000, channels: 1)!
    var pcm = Data(); for v: Int16 in [0, 16384, -32768] { var x = v.littleEndian; pcm.append(Data(bytes: &x, count: 2)) }
    let buf = CloudVoice.pcmBuffer(pcm, format: fmt)
    check(buf?.frameLength == 3, "PCM 16 bit → 3 vzorky")
    let ch = buf!.floatChannelData![0]
    check(ch[0] == 0 && abs(ch[1] - 0.5) < 0.0001 && ch[2] == -1, "převod hodnot na Float")
}

print(failures == 0 ? "\nVŠECHNY TESTY PROŠLY" : "\nSELHALO: \(failures)")
exit(failures == 0 ? 0 : 1)
