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

/// Klient serverového prostředníka. Vrací text odpovědi Clauda průběžně, jak přichází.
struct ClaudeClient {
    var serverURL = AppConfig.serverURL
    var token = AppConfig.appToken

    func stream(messages: [[String: String]]) -> AsyncThrowingStream<String, Error> {
        AsyncThrowingStream { continuation in
            let task = Task {
                do {
                    guard let url = URL(string: serverURL)?.appendingPathComponent("v1/chat"), !token.isEmpty else {
                        throw ClaudeClientError.notConfigured
                    }
                    var request = URLRequest(url: url)
                    request.httpMethod = "POST"
                    request.timeoutInterval = 60
                    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                    request.httpBody = try JSONSerialization.data(withJSONObject: ["messages": messages])

                    let (bytes, response) = try await URLSession.shared.bytes(for: request)
                    let status = (response as? HTTPURLResponse)?.statusCode ?? 0
                    guard status == 200 else {
                        var body = Data()
                        for try await b in bytes { body.append(b); if body.count > 4000 { break } }
                        let msg = (try? JSONSerialization.jsonObject(with: body) as? [String: Any])?["error"] as? String
                        throw ClaudeClientError.http(status, msg ?? "")
                    }
                    for try await line in bytes.lines {
                        switch SSEParser.parse(line: line) {
                        case .text(let t): continuation.yield(t)
                        case .error(let msg): throw ClaudeClientError.server(msg)
                        case .done: continuation.finish(); return
                        case nil: continue
                        }
                    }
                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
            // Zrušení (přerušení uživatelem) zavře spojení → server zastaví generování.
            continuation.onTermination = { _ in task.cancel() }
        }
    }
}
