"""Zdrojová data ceníku nabíjení → frontend/public/data/ceniky.json (spouští se ručně po ověření nových cen).

Každý údaj má zdroj (URL) a datum ověření. Ceny bez DPH v Kč (u PRE jsou bez DPH závazné, s DPH jen orientační).
Denní kontrolu, zda se zdroj nezměnil, dělá update_prices.py (hash cenových údajů zdroje).
Spuštění: python3 backend/tools/ceniky_zdroj.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "frontend/public/data/ceniky.json"
VERIFIED = "2026-10-31"

SOURCES = {
    "pre-point": {"name": "PRE – Ceník dobíjení v síti PRE POINT (platný od 1. 12. 2025)",
                  "url": "https://www.pre.cz/Files/emobilita/cenik/cenik-dobijeni-v-siti-pre-point-aktualne-platny/", "kind": "pdf"},
    "pre-roaming": {"name": "PRE – Ceník dobíjení na stanicích ostatních provozovatelů (platný od 1. 7. 2026)",
                    "url": "https://www.pre.cz/Files/emobilita/cenik/cenik-dobijeni-na-stanicich-ostatnich-provozovatelu-aktualne-platny/",
                    "kind": "pdf"},
    "pre-adhoc": {"name": "PRE – Jednorázové dobíjení (web)",
                  "url": "https://www.pre.cz/cs/domacnosti/emobilita/verejne-dobijeni/chci-dobijet-jednorazove/", "kind": "html"},
    "eon-clanek": {"name": "EV Magazín – E.ON Drive mění ceník od dubna 2026 (článek, ne oficiální ceník)",
                   "url": "https://www.evmagazin.cz/eon-drive-meni-cenik-nabijeni-od-dubna-2026-950-kckwh-na-70-site-nocni-tarif-jeste-levnejsi",
                   "kind": "html"},
}


def tier(kind, from_kw, price, per_min=0.0, after=None, to_kw=None):
    return {"kind": kind, "from_kw": from_kw, "to_kw": to_kw, "price": price, "price_min": per_min, "after_min": after}


def acdc(ac, dc, ufc, ufc_from=150):
    """(cena, Kč/min, po min) pro AC / DC / UFC(HPC) dle PRE; None = nenabízí."""
    out = []
    if ac: out.append(tier("AC", 0, *ac, to_kw=49))
    if dc: out.append(tier("DC", 50, *dc, to_kw=ufc_from - 1))
    if ufc: out.append(tier("HPC", ufc_from, *ufc))
    return out


def e(id, operator, country, payment, plan, tiers, source, *, membership=False, fee_month=0.0, region="",
      verified=VERIFIED, status="ověřeno", note=""):
    return {"id": id, "operator": operator, "country": country, "region": region, "payment": payment, "plan": plan,
            "membership": membership, "fee_month": fee_month, "currency": "CZK", "vat_included": False,
            "tiers": tiers, "source": source, "verified": verified, "status": status, "note": note}


R = "čip PRE – roaming"
ENTRIES = [
    # --- PRE POINT (vlastní síť), čip PRE
    e("pre-start", "PRE", "CZ", "čip PRE", "PRE CHARGE START (bez poplatku)", acdc((7.44, 0.83, 180), (9.91, 1.65, 60), (11.57, 1.65, 30)),
      "pre-point", membership=True, note="váš tarif"),
    e("pre-silver", "PRE", "CZ", "čip PRE", "PRE CHARGE SILVER", acdc((6.61, 0.41, 180), (9.09, 0.83, 60), (10.74, 1.65, 30)),
      "pre-point", membership=True, fee_month=123.97),
    e("pre-gold", "PRE", "CZ", "čip PRE", "PRE CHARGE GOLD (jen zákazníci energií PRE)", acdc((5.79, 0.41, 180), (8.26, 0.83, 60), (9.92, 1.65, 30)),
      "pre-point", membership=True, fee_month=123.97),
    e("pre-adhoc", "PRE", "CZ", "platba kartou (QR)", "jednorázově bez registrace", acdc((8.26, 0.83, 180), (10.74, 1.65, 60), (12.40, 1.65, 30)),
      "pre-adhoc"),
    # --- E.ON vlastní síť
    e("eon-drive", "E.ON", "CZ", "aplikace / karta E.ON Drive", "registrovaný (denní sazba 8–20 h)",
      [tier("DC", 0, 9.5, to_kw=100), tier("HPC", 101, 13, 2, 60, to_kw=200), tier("HPC", 201, 16.9, 2, 30)], "eon-clanek",
      membership=True, status="neověřeno",
      note="z článku, ne z oficiálního ceníku; není jisté, zda jsou ceny s DPH; noc 20–8 h: 8 / 10 / 12 Kč"),
    # --- roaming čipem PRE (ceník PRE od 1. 7. 2026)
    e("pr-eon", "E.ON", "CZ", R, "roaming", acdc((10.74, 1.65, 360), (14.87, 2.48, 60), (17.36, 3.31, 45)), "pre-roaming"),
    e("pr-cez", "ČEZ", "CZ", R, "roaming", acdc((9.92, 1.65, 180), (15.70, 1.65, 60), (21.49, 1.65, 60)), "pre-roaming"),
    e("pr-ionity", "IONITY", "EU", R, "roaming", acdc(None, (20.66, 2.48, 60), (20.66, 2.48, 60)), "pre-roaming",
      note="platí v ČR i v Evropě"),
    e("pr-lidl", "Lidl", "CZ", R, "roaming", acdc((8.43, 0, None), (10.91, 0.83, 60), None), "pre-roaming"),
    e("pr-teplarny", "Teplárny Brno", "CZ", R, "roaming (síť Chargee)", acdc((9.50, 0.83, 240), (14.05, 0.83, 60), (14.87, 0.83, 60)),
      "pre-roaming", region="Brno"),
    e("pr-shell", "Shell", "CZ", R, "roaming", acdc(None, (14.05, 1.65, 45), (14.05, 1.65, 45)), "pre-roaming"),
    e("pr-chargee", "Chargee", "CZ", R, "roaming", acdc((16.53, 1.65, 480), (20.66, 1.65, 90), (22.31, 1.65, 60)), "pre-roaming"),
    e("pr-innogy", "innogy", "CZ", R, "roaming", acdc((9.09, 1.65, 480), (14.87, 1.65, 90), (14.87, 1.65, 30)), "pre-roaming"),
    e("pr-orlen", "Orlen", "CZ", R, "roaming", acdc((10.74, 0, None), (10.74, 0, None), (14.87, 0, None)), "pre-roaming",
      note="UFC v ceníku PRE nejednoznačné (13 Kč s DPH × 14,87 bez DPH) — uvedena vyšší"),
    e("pr-prcm", "P+R Černý Most", "CZ", R, "roaming", acdc((6.61, 0.41, 720), None, None), "pre-roaming", region="Praha"),
    e("pr-enbw", "EnBW", "DE", R, "roaming", acdc((11.16, 2.07, 120), (15.29, 4.13, 30), (15.29, 4.13, 30)), "pre-roaming"),
    e("pr-smatrics", "Smatrics", "AT", R, "roaming", acdc((8.60, 0, None), (10.74, 0, None), (12.80, 0, None)), "pre-roaming"),
    e("pr-greenway", "Greenway", "SK", R, "roaming (SK, PL, HR)", acdc((13.22, 2.48, 240), (20.80, 2.48, 60), (20.66, 2.48, 60)),
      "pre-roaming", note="platí i v Polsku a Chorvatsku"),
    e("pr-zse", "ZSE", "SK", R, "roaming", acdc((7.44, 0, None), (12.40, 0, None), (12.40, 0, None)), "pre-roaming",
      note="UFC v ceníku PRE nejednoznačné (15 Kč s DPH × 10,74 bez DPH) — uvedena vyšší"),
    e("pr-enelx", "Enel X", "IT", R, "roaming", acdc((16.45, 2.07, 60), (16.45, 4.13, 60), None), "pre-roaming"),
    e("pr-hep", "HEP", "HR", R, "roaming", acdc((12.64, 0, None), (17.60, 0, None), (23.88, 0, None)), "pre-roaming"),
    e("pr-petrol", "Petrol", "SI", R, "roaming (HR, SI)", acdc((10.10, 0, None), (22.70, 0, None), (25.61, 0, None)), "pre-roaming",
      note="platí i v Chorvatsku"),
    e("pr-chargepoint", "ChargePoint", "EU", R, "roaming", acdc((14.46, 0.83, 60), (14.46, 0.83, 60), (14.46, 0.83, 60)), "pre-roaming"),
    e("pr-lidl-hr", "Lidl", "HR", R, "roaming", acdc((8.68, 0, None), (11.15, 0, None), None), "pre-roaming"),
    e("pr-kaufland-hr", "Kaufland", "HR", R, "roaming", acdc((8.68, 0, None), (11.15, 0, None), None), "pre-roaming"),
    e("pr-eon-eu", "E.ON", "DE", R, "roaming (D, A, PL, IT, H, NL, DK, RO, SE)",
      acdc((14.79, 2.48, 240), (17.27, 4.13, 45), (19.75, 4.13, 45)), "pre-roaming", note="E.ON Drive Infrastructure v 9 zemích"),
    e("pr-shell-eu", "Shell", "DE", R, "roaming (D, PL, SK, H, FR, NL, GB)",
      acdc((19.01, 1.65, 45), (19.01, 1.65, 45), (19.01, 1.65, 45)), "pre-roaming"),
    # --- bez ověřeného veřejného ceníku (zobrazit jako neověřené, planner bere ruční tarif)
    e("tesla", "Tesla", "EU", "aplikace Tesla", "Supercharger pro jiné vozy", [tier("HPC", 0, 12.0)], "",
      status="neověřeno", verified="", note="cena se liší podle stanice a času; jen v aplikaci Tesla — dle vaší zkušenosti 10–12 Kč bez DPH"),
    e("cez-app", "ČEZ", "CZ", "aplikace ČEZ", "vlastní síť ČEZ", [], "", status="neověřeno", verified="",
      note="oficiální ceník ČEZ zatím neověřen — doplňte ručně, nebo použijte čip PRE (roaming)"),
]


def main():
    data = {"generated": VERIFIED, "stale_after_days": 30, "currency_note": "ceny bez DPH v Kč; u cizích měn přepočet orientační",
            "sources": {k: {**v, "checked": VERIFIED, "changed": None, "fingerprint": None} for k, v in SOURCES.items()},
            "entries": ENTRIES}
    latest = Path.home() / ".local/share/voyah-route-planner/ceniky-latest.json"
    prev = latest if latest.exists() else OUT
    if prev.exists():                              # zachovat otisky zdrojů z denní kontroly
        old = json.loads(prev.read_text())
        for k, s in old.get("sources", {}).items():
            if k in data["sources"]:
                data["sources"][k]["fingerprint"] = s.get("new_fingerprint") or s.get("fingerprint")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{len(ENTRIES)} položek → {OUT}")


if __name__ == "__main__":
    main()
