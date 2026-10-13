# Bezpečnostní pravidla — Reo Heating IOT CZ

Tato pravidla jsou **závazná** pro každou verzi a každou změnu kódu. Porušení = chyba,
která blokuje vydání.

## 1. Read-only
Rozšíření **nesmí**:
1. Měnit nastavení tepelných čerpadel ani hodnoty formulářů IOT.
2. Odesílat ovládací příkazy (žádné `fetch`/`XMLHttpRequest` na IOT, žádné simulované kliky
   na tlačítka typu Save/Set/Send/Apply/Reset).
3. Procházet databázi zařízení (žádné automatické vyhledávání, stránkování, otevírání seznamů).
4. Získávat, číst ani ukládat přihlašovací údaje (pole hesla se ignorují, cookies se nečtou).
5. Automaticky shromažďovat data jakýchkoli zařízení — vlastních ani cizích distributorů.
6. Odesílat zákaznická ani provozní data externím službám (ve verzích 1–4 **žádná síťová komunikace**).

Rozšíření **smí**: číst text aktuálně zobrazené stránky v prohlížeči uživatele, měnit
jeho *zobrazení* (překlad, ikony, tooltipy) a zobrazovat lokální data v postranním panelu.

## 2. Minimální oprávnění (manifest)
- `host_permissions` / `content_scripts.matches`: **jen adresa IOT** `http://162.62.225.58/*`
  (IOT běží na holé IP adrese přes nešifrované HTTP — při změně adresy se upraví manifest).
- `permissions`: pouze `storage` (nastavení přepínačů) a `sidePanel`.
- Zakázáno bez schválení: `<all_urls>`, `tabs`, `cookies`, `webRequest`, `scripting`
  na jiné domény, `history`, `downloads`, `identity`, `externally_connectable`.
- Content Security Policy: žádný vzdálený kód, žádné `eval`, žádné CDN — vše přibaleno.

## 3. Ochrana dat
- `chrome.storage` obsahuje jen nastavení (překlad zap/vyp, jazyk) a lokální seznam
  nepřeložených textů. **Nikdy** jména zákazníků, Virtual ID, adresy, provozní hodnoty.
- Diagnostický formulář pracuje jen v paměti panelu; po zavření se nic neukládá
  (pokud uživatel výslovně neuloží anonymizovaný případ).
- Hodnoty převzaté ze stránky musí uživatel **výslovně vybrat**; jméno zařízení a Virtual ID
  se nikdy nepřebírají.

## 4. Git a repozitář
Do gitu **nikdy**:
- přihlašovací údaje, API klíče, tokeny (`.env*` je v `.gitignore`);
- snímky obrazovky a HTML stránek IOT, které nejsou anonymizované;
- PDF manuály Power World a index z nich vytvořený (neveřejné materiály) — `podklady/`
  a `extension/data/dokumentace-index.json` jsou v `.gitignore`;
- jména zákazníků, adresy, Virtual ID, sériová čísla konkrétních instalací.

Anonymizované testovací vzorky (`tests/vzorky/`) se před uložením zkontrolují
(viz `TESTOVANI.md`, kontrola „anonymizace“). Repo `Projekty` se automaticky
synchronizuje — proto platí pravidlo „mimo git už při uložení“, ne až před commitem.

## 5. Anonymizace snímků obrazovky (pro uživatele)
Před předáním snímku zakryj (macOS Náhled → Nástroje → Anotace → obdélník s výplní):
- název zařízení / jméno zákazníka, Virtual ID, sériové číslo, MAC, IP;
- adresu, telefon, e-mail, GPS/mapu;
- své přihlašovací jméno a vše v adresním řádku za doménou, pokud obsahuje ID.
Technické názvy parametrů, nabídky, jednotky a hodnoty ponech — ty potřebujeme.

## 6. Kontrola před každým vydáním
- [ ] `manifest.json` — oprávnění odpovídají bodu 2.
- [ ] V kódu není žádné síťové volání (`fetch`, `XMLHttpRequest`, `WebSocket`, `sendBeacon`).
- [ ] Žádný zápis do `value` formulářových prvků (automatický test).
- [ ] Žádné citlivé soubory v gitu (`git ls-files` + kontrola vzorků).
- [ ] Ruční test: s vypnutým rozšířením a se zapnutým funguje IOT stejně.

## 7. Etapa 5 (budoucí)
Jakékoli automatické čtení dat nebo napojení na IOT jen po **písemném souhlasu Power World**,
přes oficiální API/oprávnění, výhradně pro zařízení Reo Heating, s oddělenou analýzou
GDPR (zpracovatelská smlouva se zákazníky). Do té doby se nic z toho neprogramuje.
