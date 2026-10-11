// pdf2txt <vstup.pdf> — vypíše text PDF (PDFKit, součást macOS). Stránky oddělí řádkem „--- strana N ---“.
import Foundation
import PDFKit

guard CommandLine.arguments.count == 2, let doc = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1])) else {
    FileHandle.standardError.write("Nelze otevřít PDF\n".data(using: .utf8)!)
    exit(1)
}
var out = ""
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i), let text = page.string else { continue }
    let t = text.trimmingCharacters(in: .whitespacesAndNewlines)
    if t.isEmpty { continue }
    out += "--- strana \(i + 1) ---\n\(t)\n"
}
print(out, terminator: "")
