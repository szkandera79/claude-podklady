import Foundation

enum ClaudeClientError: LocalizedError {
    case notConfigured
    case http(Int, String)
    case server(String)

    var errorDescription: String? {
        switch self {
        case .notConfigured: return "Aplikace není připojená k serveru. Doplňte adresu a token v Nastavení."
        case .http(401, _): return "Server odmítl přístupový token."
        case .http(429, let msg): return msg.isEmpty ? "Denní limit spotřeby byl vyčerpán." : msg
        case .http(let code, let msg): return msg.isEmpty ? "Chyba serveru (\(code))." : msg
        case .server(let msg): return msg
        }
    }
}

/// Požadavek serveru na nástroj v telefonu.
struct ClientToolCall {
    let id: String
    let name: String
    let input: [String: Any]
}

enum StreamItem {
    case text(String)
    /// Claude chce použít nástroje v telefonu; `pending` se pošle zpět beze změny v navazujícím požadavku.
    case clientTools(calls: [ClientToolCall], pending: [String: Any])
}

/// Klient serverového prostředníka. Vrací text odpovědi Clauda průběžně, jak přichází.
struct ClaudeClient {
    var serverURL = AppConfig.serverURL
    var token = AppConfig.appToken

    /// - Parameters:
    ///   - now: čas začátku odpovědi (ISO 8601) — v navazujícím požadavku musí být stejný.
    ///   - continuation: `{assistant, tool_results}` po provedení nástrojů v telefonu.
    func stream(messages: [[String: Any]], now: String, continuation: [String: Any]? = nil) -> AsyncThrowingStream<StreamItem, Error> {
        AsyncThrowingStream { continuationStream in
            let task = Task {
                do {
                    guard let url = URL(string: serverURL)?.appendingPathComponent("v1/chat"), !token.isEmpty else {
                        throw ClaudeClientError.notConfigured
                    }
                    var body: [String: Any] = ["messages": messages, "client_tools": ["kalendar"], "now": now]
                    if let continuation { body["continuation"] = continuation }
                    var request = URLRequest(url: url)
                    request.httpMethod = "POST"
                    request.timeoutInterval = 90
                    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                    request.httpBody = try JSONSerialization.data(withJSONObject: body)

                    let (bytes, response) = try await URLSession.shared.bytes(for: request)
                    let status = (response as? HTTPURLResponse)?.statusCode ?? 0
                    guard status == 200 else {
                        var data = Data()
                        for try await b in bytes { data.append(b); if data.count > 4000 { break } }
                        let msg = (try? JSONSerialization.jsonObject(with: data) as? [String: Any])?["error"] as? String
                        throw ClaudeClientError.http(status, msg ?? "")
                    }
                    for try await line in bytes.lines {
                        switch SSEParser.parse(line: line) {
                        case .text(let t):
                            continuationStream.yield(.text(t))
                        case .error(let msg):
                            throw ClaudeClientError.server(msg)
                        case .clientTools(let raw):
                            guard let obj = try? JSONSerialization.jsonObject(with: raw) as? [String: Any],
                                  let calls = obj["calls"] as? [[String: Any]],
                                  let pending = obj["pending"] as? [String: Any] else { continue }
                            let parsed = calls.compactMap { c -> ClientToolCall? in
                                guard let id = c["id"] as? String, let name = c["name"] as? String else { return nil }
                                return ClientToolCall(id: id, name: name, input: c["input"] as? [String: Any] ?? [:])
                            }
                            continuationStream.yield(.clientTools(calls: parsed, pending: pending))
                        case .done:
                            continuationStream.finish()
                            return
                        case nil:
                            continue
                        }
                    }
                    continuationStream.finish()
                } catch {
                    continuationStream.finish(throwing: error)
                }
            }
            // Zrušení (přerušení uživatelem) zavře spojení → server zastaví generování.
            continuationStream.onTermination = { _ in task.cancel() }
        }
    }

    static func isoNow() -> String {
        ISO8601DateFormatter().string(from: Date())
    }
}
