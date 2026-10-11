import Foundation

/// Událost ze streamu serveru (vlastní jednoduchý protokol nad Server-Sent Events).
enum ServerEvent: Equatable {
    case text(String)
    case done(stopReason: String?)
    case error(String)
}

enum SSEParser {
    /// Zpracuje jeden řádek SSE. Vrací nil pro řádky, které nenesou data (komentáře, prázdné řádky, neznámé typy).
    static func parse(line: String) -> ServerEvent? {
        guard line.hasPrefix("data:") else { return nil }
        let payload = line.dropFirst(5).trimmingCharacters(in: .whitespaces)
        guard let data = payload.data(using: .utf8),
              let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = obj["type"] as? String
        else { return nil }
        switch type {
        case "text":
            guard let text = obj["text"] as? String else { return nil }
            return .text(text)
        case "done":
            return .done(stopReason: obj["stop_reason"] as? String)
        case "error":
            return .error(obj["message"] as? String ?? "Neznámá chyba")
        default:
            return nil
        }
    }
}
