import Foundation

/// Skládá průběžně přicházející text odpovědi a vydává celé věty,
/// aby syntéza řeči mohla začít mluvit dřív, než dorazí celá odpověď.
struct SentenceSplitter {
    private var buffer = ""
    /// Minimální délka věty — velmi krátké úseky („Ano.") se spojí s následující větou,
    /// aby řeč nezněla trhaně.
    var minLength = 12

    /// Zkratky, za jejichž tečkou věta nekončí.
    private static let abbreviations: Set<String> = [
        "např", "tzv", "atd", "apod", "resp", "tj", "př", "str", "č", "mj", "cca", "min", "max",
        "ing", "mgr", "dr", "mudr", "judr", "phdr", "prof", "doc", "bc", "sv", "ul", "tel", "kč",
        "mil", "mld", "tis", "hod", "pozn", "vč", "odst", "obr", "tab", "kap", "srov", "angl", "lat",
    ]

    /// Přidá další kus textu a vrátí věty, které jsou již kompletní.
    mutating func append(_ chunk: String) -> [String] {
        buffer += chunk
        var sentences: [String] = []
        while let end = findSentenceEnd() {
            let sentence = String(buffer[..<end]).trimmingCharacters(in: .whitespacesAndNewlines)
            buffer = String(buffer[end...])
            if !sentence.isEmpty { sentences.append(sentence) }
        }
        return sentences
    }

    /// Vrátí zbytek textu po skončení streamu.
    mutating func flush() -> String? {
        let rest = buffer.trimmingCharacters(in: .whitespacesAndNewlines)
        buffer = ""
        return rest.isEmpty ? nil : rest
    }

    private func findSentenceEnd() -> String.Index? {
        let chars = Array(buffer.indices)
        for (pos, idx) in chars.enumerated() {
            let c = buffer[idx]
            let isNewline = c == "\n"
            guard isNewline || ".!?…:;".contains(c) else { continue }
            // Potřebujeme vidět následující znak — jinak nevíme, zda věta opravdu končí.
            guard pos + 1 < chars.count else { return nil }
            let next = buffer[chars[pos + 1]]
            if !isNewline {
                guard next == " " || next == "\n" || next == "\"" || next == "“" || next == ")" else { continue }
            }
            if c == "." && isAbbreviationOrNumber(endingAt: pos, chars: chars) { continue }
            if c == ":" || c == ";" {
                // Dvojtečku a středník bereme jako konec jen u delšího úseku.
                if buffer.distance(from: buffer.startIndex, to: idx) < 60 { continue }
            }
            let end = chars[pos + 1]
            let length = buffer.distance(from: buffer.startIndex, to: end)
            if length < minLength && !isNewline { continue }
            return end
        }
        return nil
    }

    private func isAbbreviationOrNumber(endingAt pos: Int, chars: [String.Index]) -> Bool {
        // Slovo před tečkou
        var start = pos
        while start > 0, buffer[chars[start - 1]].isLetter || buffer[chars[start - 1]].isNumber {
            start -= 1
        }
        guard start < pos else { return false }
        let original = String(buffer[chars[start]..<chars[pos]])
        let word = original.lowercased()
        if Self.abbreviations.contains(word) { return true }
        // Řadová čísla a data: „1. ledna", „15. 3."
        if word.allSatisfy(\.isNumber) && word.count <= 2 { return true }
        // Iniciály: „J. Novák"
        if original.count == 1 && original.first?.isUppercase == true { return true }
        return false
    }
}
