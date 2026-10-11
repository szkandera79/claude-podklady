// Testy logiky, které nepotřebují iPhone ani Xcode.
// Spuštění: ./LogicTests/run.sh
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
let msgs = ConversationStore.apiMessages(from: [
    E(role: .assistant, text: "úvod"),
    E(role: .user, text: "Ahoj"),
    E(role: .notice, text: "Chyba sítě"),
    E(role: .user, text: "Slyšíš mě?"),
    E(role: .assistant, text: "Ano, slyším", interrupted: true),
    E(role: .user, text: "Super"),
    E(role: .assistant, text: "nedokončeno"),
])
check(msgs.map { $0["role"]! } == ["user", "assistant", "user"], "střídání rolí, začíná i končí uživatelem")
check(msgs[0]["content"] == "Ahoj\nSlyšíš mě?", "sloučení po sobě jdoucích zpráv a vynechání hlášek")
check(msgs[1]["content"]!.contains("přerušil"), "přerušená odpověď je označena")
do {
    var many: [E] = []
    for i in 0..<200 { many.append(E(role: i % 2 == 0 ? .user : .assistant, text: "zpráva \(i)")) }
    many.append(E(role: .user, text: "poslední"))
    let trimmed = ConversationStore.apiMessages(from: many)
    check(trimmed.count <= ConversationStore.maxContextMessages, "oříznutí dlouhé konverzace")
    check(trimmed.first?["role"] == "user" && trimmed.last?["content"] == "poslední", "po oříznutí začíná uživatelem a drží poslední zprávu")
}

print(failures == 0 ? "\nVŠECHNY TESTY PROŠLY" : "\nSELHALO: \(failures)")
exit(failures == 0 ? 0 : 1)
