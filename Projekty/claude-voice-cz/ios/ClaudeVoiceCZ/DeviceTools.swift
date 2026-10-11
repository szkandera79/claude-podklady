import EventKit
import Foundation

/// Kalendář a připomínky v iPhonu — nástroje, které Claude volá přes server a provádí je telefon.
final class DeviceTools {
    private let store = EKEventStore()

    private static let isoParser: ISO8601DateFormatter = {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime]
        return f
    }()

    private static let spoken: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "cs_CZ")
        f.timeZone = TimeZone(identifier: "Europe/Prague")
        f.dateFormat = "EEEE d. M. yyyy H:mm"
        return f
    }()

    private static let dayOnly: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "cs_CZ")
        f.timeZone = TimeZone(identifier: "Europe/Prague")
        f.dateFormat = "EEEE d. M. yyyy"
        return f
    }()

    static func parseDate(_ value: Any?) -> Date? {
        guard let s = value as? String else { return nil }
        if let d = isoParser.date(from: s) { return d }
        // Tolerance: bez časového posunu → Europe/Prague
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Europe/Prague")
        for fmt in ["yyyy-MM-dd'T'HH:mm:ss", "yyyy-MM-dd'T'HH:mm", "yyyy-MM-dd"] {
            f.dateFormat = fmt
            if let d = f.date(from: s) { return d }
        }
        return nil
    }

    /// Provede nástroj; chyby vrací jako text pro Clauda.
    func run(_ call: ClientToolCall) async -> (content: String, isError: Bool) {
        do {
            switch call.name {
            case "kalendar_udalosti": return (try await events(call.input), false)
            case "kalendar_vytvor": return (try await createEvent(call.input), false)
            case "pripominky": return (try await reminders(), false)
            case "pripominka_vytvor": return (try await createReminder(call.input), false)
            default: return ("Neznámý nástroj \(call.name).", true)
            }
        } catch {
            return (error.localizedDescription, true)
        }
    }

    // MARK: Oprávnění

    private func requireCalendar() async throws {
        if EKEventStore.authorizationStatus(for: .event) == .fullAccess { return }
        guard try await store.requestFullAccessToEvents() else {
            throw toolError("Aplikace nemá přístup ke kalendáři. Uživatel ho může povolit v Nastavení iPhonu → Claude Voice → Kalendáře.")
        }
    }

    private func requireReminders() async throws {
        if EKEventStore.authorizationStatus(for: .reminder) == .fullAccess { return }
        guard try await store.requestFullAccessToReminders() else {
            throw toolError("Aplikace nemá přístup k připomínkám. Uživatel ho může povolit v Nastavení iPhonu → Claude Voice → Připomínky.")
        }
    }

    private func toolError(_ message: String) -> NSError {
        NSError(domain: "DeviceTools", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
    }

    // MARK: Kalendář

    private func events(_ input: [String: Any]) async throws -> String {
        try await requireCalendar()
        guard let from = Self.parseDate(input["od"]), let to = Self.parseDate(input["do"]), to > from else {
            throw toolError("Neplatné období (od/do).")
        }
        let predicate = store.predicateForEvents(withStart: from, end: to, calendars: nil)
        let found = store.events(matching: predicate).sorted { $0.startDate < $1.startDate }
        if found.isEmpty { return "V tomto období nejsou v kalendáři žádné události." }
        return found.prefix(50).map { e in
            var line = e.isAllDay ? "\(Self.dayOnly.string(from: e.startDate)) (celý den)" :
                "\(Self.spoken.string(from: e.startDate))–\(Self.hourMinute(e.endDate))"
            line += ": \(e.title ?? "(bez názvu)")"
            if let loc = e.location, !loc.isEmpty { line += ", místo: \(loc)" }
            if let cal = e.calendar?.title { line += " [\(cal)]" }
            return line
        }.joined(separator: "\n")
    }

    private static func hourMinute(_ d: Date) -> String {
        let f = DateFormatter()
        f.timeZone = TimeZone(identifier: "Europe/Prague")
        f.dateFormat = "H:mm"
        return f.string(from: d)
    }

    private func createEvent(_ input: [String: Any]) async throws -> String {
        try await requireCalendar()
        guard let title = (input["nazev"] as? String)?.trimmingCharacters(in: .whitespaces), !title.isEmpty else {
            throw toolError("Chybí název události.")
        }
        guard let start = Self.parseDate(input["zacatek"]) else { throw toolError("Neplatný začátek události.") }
        let allDay = input["celodenni"] as? Bool ?? false
        let end = Self.parseDate(input["konec"]) ?? start.addingTimeInterval(allDay ? 86_400 : 3_600)
        guard let calendar = store.defaultCalendarForNewEvents else { throw toolError("V iPhonu není výchozí kalendář.") }
        let event = EKEvent(eventStore: store)
        event.title = title
        event.startDate = start
        event.endDate = max(end, start.addingTimeInterval(60))
        event.isAllDay = allDay
        event.calendar = calendar
        if let loc = input["misto"] as? String, !loc.isEmpty { event.location = loc }
        if let note = input["poznamka"] as? String, !note.isEmpty { event.notes = note }
        try store.save(event, span: .thisEvent, commit: true)
        let when = allDay ? Self.dayOnly.string(from: start) : Self.spoken.string(from: start)
        return "Událost „\(title)“ vytvořena: \(when) v kalendáři \(calendar.title)."
    }

    // MARK: Připomínky

    private func reminders() async throws -> String {
        try await requireReminders()
        let predicate = store.predicateForIncompleteReminders(withDueDateStarting: nil, ending: nil, calendars: nil)
        let items: [EKReminder] = await withCheckedContinuation { cont in
            store.fetchReminders(matching: predicate) { cont.resume(returning: $0 ?? []) }
        }
        if items.isEmpty { return "Nejsou žádné nesplněné připomínky." }
        let sorted = items.sorted {
            ($0.dueDateComponents?.date ?? .distantFuture) < ($1.dueDateComponents?.date ?? .distantFuture)
        }
        return sorted.prefix(50).map { r in
            var line = r.title ?? "(bez názvu)"
            if let due = r.dueDateComponents?.date { line += " — termín \(Self.spoken.string(from: due))" }
            return line
        }.joined(separator: "\n")
    }

    private func createReminder(_ input: [String: Any]) async throws -> String {
        try await requireReminders()
        guard let title = (input["nazev"] as? String)?.trimmingCharacters(in: .whitespaces), !title.isEmpty else {
            throw toolError("Chybí název připomínky.")
        }
        guard let list = store.defaultCalendarForNewReminders() else { throw toolError("V iPhonu není výchozí seznam připomínek.") }
        let reminder = EKReminder(eventStore: store)
        reminder.title = title
        reminder.calendar = list
        if let note = input["poznamka"] as? String, !note.isEmpty { reminder.notes = note }
        var whenText = "bez termínu"
        if let due = Self.parseDate(input["termin"]) {
            var comps = Calendar.current.dateComponents(in: TimeZone(identifier: "Europe/Prague")!, from: due)
            comps.nanosecond = nil
            reminder.dueDateComponents = comps
            reminder.addAlarm(EKAlarm(absoluteDate: due))
            whenText = "s upozorněním \(Self.spoken.string(from: due))"
        }
        try store.save(reminder, commit: true)
        return "Připomínka „\(title)“ vytvořena \(whenText) v seznamu \(list.title)."
    }
}
