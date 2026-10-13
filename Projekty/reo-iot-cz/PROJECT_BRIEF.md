# Reo Heating – IOT CZ | Inteligentní servisní a diagnostický asistent

> Úplné zadání projektu (uloženo 2026-10-13). Toto je závazný výchozí dokument —
> paměť Claude není náhradou za projektovou dokumentaci. Změny zadání zapisuj sem
> (s datem) nebo do `README.md` → „Rozhodnutí“.

Jsi zkušený softwarový architekt, vývojář webových aplikací a specialista na systémy vzdáleného monitoringu tepelných čerpadel.
Tvým úkolem je navrhnout a postupně naprogramovat profesionální českou servisní nadstavbu nad webovou platformou IOT společnosti Power World.

## 1. Výchozí situace
Provozuji společnost Real Heating, která prodává a instaluje tepelná čerpadla vyráběná společností Power World.
Tato tepelná čerpadla prodáváme pod vlastní obchodní značkou Reo Heating.
K jejich vzdálenému monitoringu a diagnostice používám webovou platformu IOT.
V IOT vyhledávám jednotlivá tepelná čerpadla podle unikátního identifikátoru Virtual ID nebo podle názvu zařízení, často odpovídajícího jménu zákazníka.
Po vyhledání zařízení vidím jeho stav online/offline. Pokud je dostupné, mohu zobrazovat provozní parametry a využívat servisní funkce.
Současné rozhraní je v angličtině, obsahuje množství odborných technických údajů a není dostatečně přehledné pro každodenní diagnostiku.
Mám servisní přístup, který technicky umožňuje zobrazovat také zařízení jiných distributorů. Projekt však smí pracovat výhradně v rozsahu mých oprávnění. Nesmí automaticky procházet, sbírat, ukládat ani ovládat zařízení jiných distributorů.
Používám Mac, Google Chrome, Claude Code a GitHub.

## 2. Hlavní cíl projektu
Vytvoř rozšíření pro Google Chrome, které nad existujícím rozhraním IOT poskytne čtyři základní funkce:

1. Profesionální překlad rozhraní do češtiny.
2. Interaktivní odbornou encyklopedii provozních parametrů.
3. Databázi chybových kódů a doporučených servisních postupů.
4. Inteligentního diagnostického asistenta využívajícího technickou dokumentaci Power World.

Projekt musí být navržen modulárně, aby bylo možné jednotlivé funkce postupně rozvíjet.

## 3. Česká lokalizace
Vytvoř překladový systém s odborným slovníkem terminologie tepelných čerpadel.
Překládej:

* Hlavní nabídky a ovládací prvky.
* Názvy provozních parametrů.
* Servisní nastavení.
* Chybová a informační hlášení.
* Dynamicky načítané části rozhraní.

Zachovávej původní číselné hodnoty, jednotky, identifikátory a technické kódy.
U každého přeloženého parametru umožni zobrazit původní anglický název, například po najetí kurzorem.
Překladový slovník musí být snadno upravitelný.

## 4. Odborná encyklopedie parametrů
Vedle jednotlivých technických parametrů zobraz informační ikonu.
Po kliknutí otevři odbornou nápovědu obsahující:

* Český a anglický název parametru.
* Jeho fyzikální význam.
* Funkci v tepelném čerpadle.
* Jednotku měření.
* Faktory ovlivňující jeho hodnotu.
* Vztahy k ostatním provozním parametrům.
* Typické příznaky nestandardního provozu.
* Doporučené diagnostické kontroly.

Informace musí vycházet z technických znalostí a pokud možno z dokumentace konkrétního modelu Power World.
Nevymýšlej univerzální přípustné hodnoty. Limity se mohou lišit podle modelu, chladiva, režimu a provozních podmínek.
Pokud dokumentace konkrétní hodnotu nepotvrzuje, musí to systém jednoznačně uvést.

## 5. Databáze chybových kódů
Vytvoř strukturovanou databázi servisních chyb.
U každé chyby eviduj:

* Kód chyby.
* Originální anglický popis.
* Odborný český překlad.
* Význam chyby.
* Pravděpodobné příčiny.
* Doporučený diagnostický postup.
* Možnosti odstranění závady.
* Příslušný model tepelného čerpadla.
* Zdroj informací v servisním manuálu.

Umožni vyhledávání podle chybového kódu i podle příznaků závady.
Počítej s tím, že stejné označení chyby může mít u různých řídicích jednotek odlišný význam.

## 6. Import technické dokumentace
Navrhni systém, do kterého budu moci postupně přidávat:

* Uživatelské manuály Power World.
* Servisní manuály.
* Seznamy chybových kódů.
* Technické katalogy.
* Elektrická schémata.
* Dokumentaci regulátorů.
* Vlastní servisní poznatky Reo Heating.

Dokumentace bude převážně ve formátu PDF.
Navrhni vhodné zpracování dokumentů, jejich indexaci a vyhledávání.
Každá odborná odpověď diagnostického asistenta by měla pokud možno obsahovat odkaz na konkrétní dokument a stránku.
Rozlišuj mezi potvrzenými informacemi výrobce, obecnými technickými znalostmi a hypotézami diagnostického asistenta.

## 7. Inteligentní diagnostický asistent
Navrhni asistenta, který dokáže vyhodnocovat vzájemné souvislosti provozních parametrů.
Například při zvýšené výtlačné teplotě kompresoru by měl upozornit na další relevantní veličiny, které je potřeba zkontrolovat.
Diagnostika musí respektovat:

* Konkrétní model tepelného čerpadla.
* Typ chladiva.
* Provozní režim.
* Venkovní teplotu.
* Požadovanou teplotu topné vody.
* Frekvenci kompresoru.
* Další dostupné provozní údaje.

Výstupem nemá být automaticky definitivní diagnóza, ale odborně zdůvodněné možné příčiny, jejich pravděpodobnost pouze tam, kde je podložená, a doporučený postup ověřování.
První verze asistenta musí fungovat s ručně zadanými nebo uživatelem výslovně vybranými anonymizovanými údaji.
Automatické čtení a přenos zákaznických provozních dat do externí AI služby není povolen.

## 8. Prověření AI systému Power World
Zjisti z veřejně dostupné dokumentace, zda Power World již nabízí vlastní AI systém pro servisní diagnostiku.
Prověř zejména:

* Zda je integrován do IOT.
* Jaké diagnostické funkce nabízí.
* Zda existuje dokumentace nebo API.
* Zda lze systém legálně integrovat s naší nadstavbou.

Nepředpokládej, že takový systém existuje, dokud jeho existenci nepotvrdíš.
Pokud nebude dostupný, navrhni vlastní nezávislé řešení.

## 9. Bezpečnostní požadavky
První verze musí být striktně read-only.
Rozšíření nesmí:

* Měnit nastavení tepelných čerpadel.
* Automaticky odesílat ovládací příkazy.
* Procházet databázi zařízení.
* Získávat nebo ukládat přihlašovací údaje.
* Automaticky shromažďovat data cizích zařízení.
* Odesílat zákaznické údaje externím službám.

Použij princip minimálních oprávnění a omez rozšíření na konkrétní doménu IOT.
Při práci s rozhraním nesmí docházet k narušení jeho původních funkcí.
Překlad ani informační prvky nesmějí měnit hodnoty formulářů, které by mohly být následně odeslány do IOT.

## 10. Uživatelské rozhraní
Navrhni přehledný profesionální design odpovídající značce Real Heating.
Preferuji jednoduché ovládání.
Uživatel musí mít možnost:

* Zapnout nebo vypnout překlad.
* Zobrazit odborné vysvětlení parametru.
* Vyhledat chybový kód.
* Otevřít diagnostického asistenta.
* Zobrazit použitou technickou dokumentaci.
* Přepnout mezi češtinou a angličtinou.

Diagnostického asistenta můžeš navrhnout jako postranní panel v Chrome.

## 11. Technická architektura
Použij Chrome Extension Manifest V3.
Navrhni samostatné moduly pro:

* Lokalizaci.
* Odborný slovník.
* Databázi chyb.
* Zpracování dokumentace.
* Diagnostického asistenta.
* Uživatelské rozhraní.

Odděl statickou odbornou databázi od případných budoucích AI funkcí.
Zajisti možnost aktualizovat překlady a odborné informace bez nutnosti přeprogramovat celé rozšíření.
Projekt připrav pro verzování na GitHubu.
Do repozitáře nesmějí být ukládány přihlašovací údaje, zákaznická data ani neveřejné materiály bez odpovídajícího oprávnění.

## 12. Postup realizace
Pracuj po etapách.

- **Etapa 1:** Analýza IOT a vytvoření české lokalizace.
- **Etapa 2:** Interaktivní odborná encyklopedie parametrů.
- **Etapa 3:** Import servisních manuálů a databáze chybových kódů.
- **Etapa 4:** Diagnostický asistent pracující s dokumentací a ručně poskytnutými údaji.
- **Etapa 5:** Posouzení možnosti autorizovaného propojení s IOT a případného automatizovaného monitoringu vlastních zařízení Reo Heating.

Před zahájením programování nejprve připrav architekturu, strukturu projektu, bezpečnostní pravidla a plán testování.
Následně mě požádej o anonymizované snímky obrazovky IOT a příslušnou dokumentaci Power World.
Nevymýšlej strukturu IOT ani jeho API.
Vysvětluj mi jednotlivé kroky srozumitelně. Nejsem profesionální programátor, ale mám funkční Claude Code a používám GitHub.
Cílem je vytvořit dlouhodobě rozšiřitelný profesionální servisní nástroj Real Heating, nikoliv pouze jednoduchý překladač.

---

## Pracovní dohoda (z úvodní konzultace)
- Začínáme v Chromu na Macu, Claude Code programuje, GitHub slouží k verzování.
- Uživatel pomáhá s technickou koncepcí, zadáním, odbornou terminologií a kontrolou výsledků.
- Navázání v další relaci: „Pokračujeme v projektu IOT CZ.“

> Poznámka k přepisu: v původním textu se objevovalo i „IROT“ — jde o tutéž platformu IOT
> (sjednoceno). Adresa platformy IOT (Power World): `http://162.62.225.58/` (login `/#/login`).
