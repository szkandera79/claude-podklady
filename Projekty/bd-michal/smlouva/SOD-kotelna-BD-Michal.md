# Smlouva o dílo – technologická kotelna s tepelnými čerpadly, BD Michal

**Pracovní návrh k vyjednávání, verze 2.0 (finální znění po zátěžovém testu), 23. 9. 2026**

Dokument má sedm částí:

- **A.** Úvodní poznámky, předpoklady a body k doplnění
- **B.** Finální znění smlouvy o dílo (v2.0)
- **C.** Seznam příloh a osnova klíčových příloh
- **D.** Riziková analýza z pohledu zhotovitele
- **E.** Zátěžový test z pozice právníka objednatele: slabá místa verze 1.0 a jejich opravy
- **F.** Modelové situace a jak je smlouva řeší
- **G.** Vyjednávací prostor a doporučení

> Návrh připravil Claude jako podklad pro jednání a pro srovnání s vaší verzí. Není to
> stanovisko advokáta. Před podpisem ho má zkontrolovat advokát, hlavně části označené [DOPLNIT]
> a volby označené [VOLBA].

---

## A. Úvodní poznámky, předpoklady a body k doplnění

### A.1 Z čeho návrh vychází

| Položka | Hodnota v návrhu | Zdroj |
|---|---|---|
| Zhotovitel | Riva Trade, s.r.o., Korunní 2569/108, 101 00 Praha, IČ 08864811, DIČ CZ08864811 | zadání |
| Objednatel | [DOPLNIT] | doplní objednatel |
| Stavba | Bytový dům Michal, novostavba, k. ú. Michálkovice, Ostrava; 27 b. j. | PENB č. 530077.2, DPS |
| Tepelná ztráta | 53 kW při −15 °C | PENB (TRIPLAN, 12/2023) |
| Zdroj | 3× TČ vzduch/voda REO Heating X50 (monoblok, chladivo R290) | zadání, TV-BDM-04 |
| Výkon X50 | A−15/W55 cca 24,8 kW; A7/W35 cca 49,3 kW | datový list výrobce |
| Akumulace | ÚT 2× 1 000 l; TUV 3× 1 000 l, nabíjení přes deskový výměník | zadání, TV-BDM-04 |
| Provozní filozofie | TČ1 ÚT, TČ2 ÚT + TUV, TČ3 záloha (režimy A–D) | TV-BDM-04, TV-BDM-05 |
| Bivalence | uvažovaná, konfigurace není finální → řešeno **opcí** | zadání |
| FVE | 46 kWp + baterie 40,8 kWh (mimo dílo, rozhraní Modbus TCP) | DPS FVE |
| Termín | neurčitý, podle stavební připravenosti; nezávazný cíl: předání před topnou sezónou 2027/2028 | zadání |
| Platby | 100 % ceny hlavních komponent záloha po podpisu, zbytek po předání | zadání |

### A.2 Technická skutečnost, na které stojí smlouva

Při −15 °C a teplotě otopné vody 55 °C dávají **dvě** jednotky X50 podle datového listu
zhruba **2 × 24,8 = 49,6 kW**. Tepelná ztráta domu je **53 kW** a k tomu přichází ohřev TUV.
V nejchladnějších dnech tedy dvě TČ „v běžném provozu" nestačí a TČ3 poběží jako třetí stupeň,
ne jen jako záloha. Pokud jedna jednotka mezitím vypadne a bivalentní zdroj není osazen,
kotelna nepokryje celou potřebu.

Tohle je **největší právní riziko zhotovitele**. Objednatel by takový stav reklamoval jako
„nedostatečný výkon" a smlouva, která o něm mlčí, by se vykládala proti zhotoviteli.
Proto návrh:

1. popisuje provozní filozofii přesně a výslovně připouští zapojení TČ3 při výkonovém deficitu (čl. 4.1),
2. uvádí výkonové limity se zdrojem dat, aby je objednatel vzal na vědomí (čl. 4.2),
3. dává jeden jasný a ověřitelný výkonový závazek zhotovitele: pokrytí ztráty všemi třemi TČ (čl. 4.3),
4. řeší bivalenci opcí s pevnou lhůtou a cenou (čl. 3.5). Pokud ji objednatel neuplatní, nese riziko sám.

### A.3 Co je nutné doplnit před podpisem

1. Identifikace objednatele. Pokud je objednatel **fyzická osoba, která nejedná v rámci podnikání**,
   je spotřebitelem. Pak je třeba smlouvu přepracovat: odstupné, limitace odpovědnosti, fikce převzetí
   a smluvní pokuty podléhají kontrole zneužívajících klauzulí (§ 1813 a násl. OZ). Při uzavření mimo
   obchodní prostory má navíc spotřebitel právo odstoupit do 14 dnů (§ 1829 OZ). Návrh počítá
   s objednatelem-podnikatelem (developer / SPV).
2. Spisová značka zhotovitele v obchodním rejstříku, statutární orgán, bankovní spojení.
3. Parcelní čísla, číslo stavebního povolení / povolení záměru.
4. Ceny v Příloze 2 (část A: hlavní komponenty, část B: ostatní dodávky a práce, opce).
5. Teplotní spád otopné soustavy (návrhová teplota přívodu) a rezervovaný příkon. Na obojím závisí čl. 4.3.
6. Rozhodnutí voda / glykol v primárním okruhu (TV-BDM-04, bod 5). Mění sestavu i cenu.
7. Umístění venkovních jednotek (terén / střecha). Mění statiku, jeřáb, hluk a ochranná pásma R290.

---

## B. SMLOUVA O DÍLO č. [RT-BDM-2026-01]

**Technologická kotelna s tepelnými čerpadly – Bytový dům Michal, Ostrava-Michálkovice**

uzavřená podle § 2586 a násl. zákona č. 89/2012 Sb., občanský zákoník, ve znění pozdějších předpisů („**OZ**")

### Smluvní strany

**Zhotovitel:**
**Riva Trade, s.r.o.**
sídlo: Korunní 2569/108, 101 00 Praha
IČO: 08864811, DIČ: CZ08864811
zapsaná v obchodním rejstříku vedeném Městským soudem v Praze, oddíl C, vložka [DOPLNIT]
zastoupená: [DOPLNIT – jméno, funkce]
bankovní spojení: [DOPLNIT]
(dále jen „**zhotovitel**")

**Objednatel:**
[DOPLNIT – obchodní firma / jméno]
sídlo: [DOPLNIT]
IČO: [DOPLNIT], DIČ: [DOPLNIT]
zapsaný v [DOPLNIT]
zastoupený: [DOPLNIT]
bankovní spojení: [DOPLNIT]
(dále jen „**objednatel**")

(zhotovitel a objednatel společně „**strany**")

---

### Článek 1 – Úvodní ustanovení a účel smlouvy

1.1 Objednatel je stavebníkem bytového domu „Michal" na pozemku parc. č. [DOPLNIT] v k. ú. Michálkovice,
obec Ostrava („**stavba**" nebo „**dům**"). Stavba se provádí podle [povolení stavby / povolení záměru]
č. j. [DOPLNIT].

1.2 Účelem smlouvy je dodat a zprovoznit centrální zdroj tepla pro vytápění a přípravu teplé vody
domu s tepelnými čerpadly („**kotelna**") a rozdělit mezi strany rizika a odpovědnosti tak, aby odpovídala
tomu, kdo je může ovlivnit.

1.3 Objednatel prohlašuje, že uzavírá smlouvu v rámci své podnikatelské činnosti. Strany prohlašují,
že obsah smlouvy vyjednaly jednotlivě a každá z nich mohla obsah ovlivnit.

1.4 Zhotovitel prohlašuje, že se s odbornou péčí seznámil se vstupními podklady uvedenými v Příloze 3.
Na nedostatky, které zjistil, upozornil v Příloze 3, oddíl „Výhrady zhotovitele". Za správnost
a úplnost vstupních podkladů odpovídá objednatel. Zhotovitel odpovídá za důsledky vad podkladů,
které mohl při odborné péči zjistit a na které neupozornil (§ 2594 OZ).

### Článek 2 – Vymezení pojmů

Pojmy s velkým počátečním písmenem nebo tučně vyznačené mají v této smlouvě tento význam:

2.1 **Hlavní technologické komponenty („HTK")**: 3× tepelné čerpadlo REO Heating X50 včetně příslušenství
dodávaného výrobcem, 2× akumulační nádrž 1 000 l, 3× zásobník TUV 1 000 l, deskový výměník pro
nabíjení TUV, řídicí systém (PLC/kaskádový regulátor a HMI). Přesná specifikace a cena každé položky
je v Příloze 2, část A.

2.2 **Stavební připravenost**: stav stavby, ve kterém jsou splněny všechny podmínky podle Přílohy 5
a který strany potvrdily protokolem podle čl. 6.2 („**Protokol o stavební připravenosti**").
**Datum stavební připravenosti** je den uvedený v tomto protokolu.

2.3 **Realizační lhůta**: [10] týdnů od Data stavební připravenosti. Je to lhůta k dokončení a předání
díla podle čl. 12. Prodlužuje se podle čl. 6.4.

2.4 **Cílový termín**: předání kotelny do 30. 9. 2027. Je to společný plánovací cíl stran, nikoli smluvní
lhůta (čl. 6.3).

2.5 **Provozní filozofie**: způsob provozu kotelny podle čl. 4.1 a Přílohy 4.

2.6 **Předaná a funkční kotelna**: stav podle čl. 12.2.

2.7 **Vada**: odchylka díla od této smlouvy a jejích příloh, u níž se nejedná o odchylku podle čl. 4.4.
- **Drobná vada** nebo **nedodělek**: vada, která sama o sobě ani ve spojení s jinými nebrání užívání
  kotelny funkčně ani esteticky a užívání podstatně neomezuje (§ 2628 OZ). Nikdy se za ni nepovažují
  vady uvedené v čl. 12.4 písm. b).
- **Havarijní vada**: vada, kvůli které kotelna nedodává teplo do otopné soustavy nebo neohřívá TUV
  ani v záložním režimu, nebo vada, která bezprostředně ohrožuje zdraví či majetek (únik vody,
  elektrická závada, únik chladiva).
- **Provozní vada**: vada, která omezuje provoz, ale kotelna díky záloze dodává teplo a TUV
  (např. porucha jednoho TČ).

2.8 **Změna**: jakákoli změna rozsahu, technického řešení, jakosti, termínu nebo podmínek provádění
díla oproti smlouvě. Změna se sjednává **Změnovým listem** podle čl. 9 a Přílohy 9.

2.9 **Okolnost vylučující odpovědnost**: mimořádná, nepředvídatelná a nepřekonatelná překážka
vzniklá nezávisle na vůli strany (§ 2913 odst. 2 OZ). Patří sem zejména živelní události, válka,
epidemie s úředními omezeními, embargo a celoplošná nedostupnost HTK u výrobce, kterou zhotovitel
doloží písemným vyjádřením výrobce. Nepatří sem finanční potíže strany ani prodlení jejích
poddodavatelů, pokud nejsou způsobena touto okolností.

2.10 **Opce bivalence**: právo objednatele objednat bivalentní zdroj podle čl. 3.5.

### Článek 3 – Předmět díla

3.1 Zhotovitel se zavazuje na svůj náklad a na své nebezpečí provést pro objednatele dílo podle
této smlouvy. Objednatel se zavazuje dílo převzít a zaplatit cenu.

3.2 Dílo tvoří (podrobně Příloha 1 a Příloha 2):

a) **dodavatelská dokumentace kotelny** navazující na projektovou dokumentaci stavby: hydraulické
   schéma, schéma MaR, dispozice, dimenzování primárního potrubí, výpočet expanze, specifikace
   a podklady pro stavební připravenost (zatížení, prostupy, napojovací body),
b) **dodávka HTK** a ostatního materiálu,
c) **montáž** TČ na připravené základy nebo konzoly, hydraulické propojení, sběrač a rozdělovač,
   oběhová a nabíjecí čerpadla, armatury, zpětné klapky, expanzní a pojistná zařízení, úprava topné vody,
   izolace, odvod kondenzátu a pojistných ventilů k napojovacím bodům podle Přílohy 8,
d) **elektroinstalace a MaR** kotelny od svorek rozvaděče kotelny („**RK**") včetně RK,
e) **řídicí systém** s kaskádovým řízením, provozními režimy podle Přílohy 4, ekvitermní regulací,
   přípravou TUV, termickou dezinfekcí, alarmy a rozhraním Modbus TCP pro nadřazené systémy,
f) **napuštění, proplach, tlakové zkoušky, uvedení do provozu, komplexní zkoušku a zaregulování
   primárního okruhu kotelny**,
g) **doklady** podle Přílohy 6 a **zaškolení obsluhy** podle čl. 12.1 písm. g).

3.3 Hydraulika kotelny se provede s připravenými napojovacími body (odbočky s uzávěry, návarky
nebo jímky) pro pozdější připojení bivalentního zdroje v obou variantách podle Přílohy 2, část C.
Tato příprava je v ceně díla.

3.4 Předmětem díla **není** (podrobně Příloha 8): stavební práce a statika, rozvody ÚT a TUV
mimo kotelnu, otopná tělesa a hydraulické vyvážení otopné soustavy domu, cirkulace TUV mimo kotelnu,
přívod elektřiny do RK včetně předřazeného jištění, FVE, baterie a jejich řízení, bivalentní zdroj
(pokud nebyla uplatněna opce), měření tepla pro rozúčtování nákladů, povolení veřejnoprávních orgánů,
hluková studie, požárně bezpečnostní řešení stavby a internetová konektivita.

3.5 **Opce bivalence.** Objednatel může **do 31. 3. 2027** nebo do [8] týdnů před oznámeným Datem
stavební připravenosti (podle toho, co nastane dříve) písemně objednat bivalentní zdroj v některé
z variant podle Přílohy 2, část C, za ceny tam uvedené. Realizační lhůta se neprodlužuje, ledaže
výrobce bivalentního zdroje doloží delší dodací lhůtu. Pozdější objednávka je Změnou podle čl. 9.
Dokud objednatel opci neuplatní, platí čl. 4.2 poslední věta.

### Článek 4 – Provozní filozofie, výkonové parametry a co zhotovitel negarantuje

4.1 **Provozní filozofie.** Kotelna je navržena takto: TČ1 vytápí, TČ2 vytápí a nabíjí TUV, TČ3 je
záloha. Řídicí systém připojí TČ3 k vytápění nebo k TUV při poruše TČ1 nebo TČ2 **a také při
výkonovém deficitu**, tj. když TČ1 a TČ2 nepokryjí okamžitou potřebu (režimy A–D podle Přílohy 4).
Pořadí, střídání rolí jednotek a spínací prahy jsou provozní parametry. Na žádost objednatele je lze
změnit bez Změny a jejich změna není vadou díla, pokud neodporuje čl. 4.3.

4.2 **Výkonové limity.** Objednatel bere na vědomí, že:
- podle datového listu výrobce (Příloha 7) dodává jedna jednotka X50 při venkovní teplotě −15 °C
  a výstupní teplotě 55 °C tepelný výkon přibližně 24,8 kW,
- tepelná ztráta domu podle PENB č. 530077.2 je 53 kW při −15 °C,
- při venkovních teplotách blízkých výpočtové teplotě a při současném nabíjení TUV proto dvě TČ
  nepokryjí celou potřebu a kotelna počítá s TČ3 jako třetím výkonovým stupněm,
- pokud v takových podmínkách jedna z jednotek nepracuje (porucha, servis, odmrazování) a bivalentní
  zdroj není osazen, **nemusí kotelna pokrýt celou potřebu tepla.** Takový stav sám o sobě není vadou
  díla. Zhotovitel odpovídá jen za příčinu nefunkčnosti jednotky, je-li vadou díla.

4.3 **Výkonový závazek zhotovitele.** Zhotovitel odpovídá za to, že:

a) HTK odpovídají typu a parametrům uvedeným v Příloze 1 a v datových listech výrobce (Příloha 7).
   Parametry jednotek se posuzují za podmínek normy ČSN EN 14511, pro kterou je výrobce udává,
b) kotelna je navržena, provedena a nastavena tak, že **při provozu všech tří TČ** pokryje tepelnou
   ztrátu domu podle Přílohy 3 při výpočtové venkovní teplotě −15 °C a teplotě přívodu otopné vody
   [DOPLNIT, např. 55 °C] a zároveň připraví TUV na teplotu na výstupu ze zásobníků podle Přílohy 4
   (nejméně [55] °C). Kotelna také umožní termickou dezinfekci zásobníků podle Přílohy 4.
   Splnění se prokazuje výpočtem v dodavatelské dokumentaci z datových listů výrobce a funkčními
   zkouškami podle čl. 12. Výkonová zkouška při výpočtové venkovní teplotě se neprovádí,
c) kotelna je provedena v souladu s právními předpisy, s normami ČSN uvedenými v Příloze 1,
   s dodavatelskou dokumentací a s pokyny výrobců HTK.

4.4 **Co zhotovitel negarantuje.** Zhotovitel negarantuje roční spotřebu elektrické energie, sezónní
ani okamžitý topný faktor (SCOP/COP) v provozu, provozní náklady, úspory, návratnost investice ani
podíl pokrytí spotřeby z FVE. Tyto hodnoty závisí zejména na počasí, na způsobu užívání domu, na odběru
TUV, na stavu a vyvážení otopné soustavy, na teplotě zpátečky, na nastavení zvoleném objednatelem
a na cenách energií. Výpočty, simulace a kalkulace, které zhotovitel poskytl před uzavřením smlouvy
nebo později, jsou orientační a nejsou závazkem zhotovitele.
**Tím není dotčena odpovědnost zhotovitele za vady díla.** Pokud je vyšší spotřeba nebo nižší topný
faktor způsoben vadou díla (např. vadným komponentem, chybným zapojením, chybným nastavením
provedeným zhotovitelem nebo odchylkou od čl. 4.3), jde o vadu podle čl. 13.

4.5 **Teplota TUV u odběrných míst** závisí na rozvodech a cirkulaci mimo kotelnu. Ty nejsou
předmětem díla. Zhotovitel odpovídá za teplotu na výstupu ze zásobníků a za funkci termické dezinfekce
podle čl. 4.3 písm. b). Za splnění hygienických požadavků na teplotu teplé vody v místě odběru podle
vyhlášky č. 252/2004 Sb. odpovídá objednatel. Zhotovitel tímto upozorňuje, že kvůli nízkoteplotnímu
zdroji je třeba navrhnout rozvody a cirkulaci s co nejnižšími tepelnými ztrátami a cirkulaci vyvážit.

4.6 **Hluk.** Zhotovitel odpovídá za to, že TČ jsou osazena podle pokynů výrobce včetně
antivibračních prvků a že jejich akustické parametry odpovídají datovému listu. Posouzení hluku
v chráněném venkovním i vnitřním prostoru (nařízení vlády č. 272/2011 Sb.) a případná protihluková
opatření zajišťuje objednatel v rámci projektu stavby. Zhotovitel dodá akustické podklady do
10 pracovních dnů od vyžádání.

4.7 **Chladivo R290.** Jednotky obsahují hořlavé chladivo. Umístění jednotek včetně ochranných pásem
podle pokynů výrobce musí být v souladu s požárně bezpečnostním řešením stavby, které zajišťuje
objednatel. Zhotovitel dodá požadavky výrobce na ochranná pásma nejpozději s dodavatelskou
dokumentací a odpovídá za montáž v souladu s nimi.

### Článek 5 – Rozhraní dodávek a odpovědností

5.1 Rozhraní je závazně vymezeno maticí v Příloze 8. V základu platí:

a) **ÚT:** hranicí jsou výstupní uzavírací armatury rozdělovače a sběrače pro jednotlivé topné větve.
   Tyto armatury dodává zhotovitel, vše za nimi objednatel,
b) **TUV:** hranicí jsou hrdla studené vody na vstupu do kotelny (za vodoměrem objednatele) a hrdla
   výstupu TUV a cirkulace na zásobnících nebo na směšovací sestavě,
c) **elektro:** hranicí jsou vstupní svorky RK. Přívodní kabel, předřazené jištění, hlavní vypínač
   a zajištění rezervovaného příkonu podle Přílohy 3 dodává objednatel. Ochranné pospojování
   se napojí na hlavní ochrannou přípojnici objednatele,
d) **stavba:** základy nebo konzoly venkovních jednotek podle zatížení a výkresů zhotovitele, prostupy
   a jejich utěsnění včetně požárních ucpávek, podlahy, odvětrání a osvětlení kotelny, napojovací
   body kanalizace pro kondenzát a pojistné ventily a přístupové cesty dodává objednatel,
e) **data:** zhotovitel zpřístupní datové body řídicího systému přes Modbus TCP podle seznamu
   v Příloze 4. Připojení k internetu a integraci s řízením FVE a baterie zajišťuje objednatel,
   pokud strany nesjednají jinak Změnou,
f) **povolení:** veřejnoprávní povolení a stanoviska zajišťuje objednatel. Zhotovitel k nim dodá
   technické podklady do 10 pracovních dnů od vyžádání.

5.2 Pokud zhotovitel zjistí, že podklad, pokyn nebo věc předaná objednatelem je nevhodná, upozorní
na to objednatele bez zbytečného odkladu písemně a v nezbytném rozsahu přeruší dotčené práce
(§ 2594 OZ). Pokud objednatel na pokynu přesto písemně trvá, zhotovitel za vady takto vzniklé
neodpovídá. Pokud by provedení podle pokynu vedlo k porušení právních předpisů nebo k ohrožení
zdraví, může zhotovitel od smlouvy odstoupit (§ 2595 OZ).

### Článek 6 – Stavební připravenost a termíny

6.1 **Postup:**

a) **Objednání HTK:** zhotovitel objedná HTK u výrobce do 10 pracovních dnů od připsání zálohy
   podle čl. 8.1 a objednávku potvrzenou výrobcem předá objednateli v kopii,
b) **Dodavatelská dokumentace:** zhotovitel ji předá do [6] týdnů od podpisu smlouvy. Objednatel se
   k ní vyjádří do 10 pracovních dnů. Pokud se nevyjádří, zhotovitel ho písemně upozorní. Pokud se
   objednatel nevyjádří ani do 5 pracovních dnů od upozornění, platí dokumentace za schválenou,
c) **Dodání HTK na stavbu:** HTK se dodávají podle Stavební připravenosti. Do té doby je zhotovitel
   skladuje za podmínek čl. 8.3 a 6.5,
d) **Montáž a předání:** zhotovitel dokončí a předá dílo v Realizační lhůtě („**termín dokončení**").

6.2 **Stavební připravenost.** Objednatel oznámí zhotoviteli předpokládané Datum stavební připravenosti
písemně nejméně [15] pracovních dnů předem. Zhotovitel do 5 pracovních dnů od tohoto data připravenost
prověří na místě a podepíše Protokol o stavební připravenosti, nebo písemně uvede konkrétní neplněné
podmínky podle Přílohy 5. Pokud zhotovitel tuto lhůtu zmešká bez uvedení neplněných podmínek, platí
připravenost za potvrzenou k oznámenému datu. Strany mohou potvrdit **dílčí připravenost**
(vnitřní část kotelny / venkovní jednotky). Realizační lhůta ale běží až od potvrzení úplné
připravenosti. Trvalé napájení kotelny v plném rezervovaném příkonu je podmínkou uvedení do provozu.
Staveništní přípojka ho nenahrazuje.

6.3 **Cílový termín.** Strany mají zájem, aby kotelna byla předána do 30. 9. 2027. Objednatel bere
na vědomí, že to vyžaduje Datum stavební připravenosti nejpozději [22. 7. 2027]. Zhotovitel:
- vyvine přiměřené úsilí k dosažení Cílového termínu i při pozdější připravenosti. Zrychlení nad rámec
  běžného nasazení provede jen na základě Změny,
- bez zbytečného odkladu písemně upozorní objednatele na každou skutečnost, která Cílový termín
  ohrožuje, a navrhne opatření.

Nedosažení Cílového termínu nezakládá sankce. Sankcionována je pouze Realizační lhůta.

6.4 **Prodloužení Realizační lhůty.** Realizační lhůta se prodlouží o dobu, po kterou zhotovitel
nemohl plnit kvůli:
- prodlení objednatele se součinností nebo s platbou,
- Změně (podle Změnového listu),
- Okolnosti vylučující odpovědnost,
- přerušení podle čl. 16,
- venkovním podmínkám, které znemožňují venkovní práce nebo napouštění podle technologických
  předpisů (zejm. teplota pod −5 °C nebo trvalé srážky).

Prodloužení odpovídá skutečnému dopadu na postup prací a zhotovitel je musí uplatnit písemně
do 10 pracovních dnů od okamžiku, kdy se o příčině dozvěděl. Jinak nárok na prodloužení zaniká,
pokud objednatel o příčině a jejím dopadu prokazatelně nevěděl.

6.5 **Dlouhodobá nepřipravenost.** Pokud Datum stavební připravenosti nenastane do **31. 12. 2027**:

a) zhotovitel skladuje HTK dál. Od 1. 1. 2028 má nárok na skladné [DOPLNIT, např. 4 500 Kč bez DPH]
   za každý započatý měsíc a na náklady pojištění skladovaných HTK. Na žádost objednatele je místo
   toho kdykoli dodá na místo určené objednatelem v Ostravě. Tím na objednatele přechází nebezpečí
   škody na HTK a skladné přestane běžet,
b) cena části B se upraví podle čl. 7.6,
c) záruční doba HTK se řídí čl. 13.1 poslední větou,
d) pokud Datum stavební připravenosti nenastane ani do **30. 6. 2028**, může kterákoli strana od
   smlouvy odstoupit. Vypořádání se řídí čl. 17.2 písm. b), přičemž odstupné podle čl. 17.1 písm. c)
   bod iv. se nehradí.

### Článek 7 – Cena díla

7.1 Cena díla (podrobně Příloha 2):

| Část | Obsah | Cena bez DPH |
|---|---|---|
| A | Hlavní technologické komponenty (HTK) | [DOPLNIT] Kč |
| B | Ostatní dodávky, doprava, montáž, dokumentace, zkoušky, uvedení do provozu | [DOPLNIT] Kč |
| **A+B** | **Cena díla** | **[DOPLNIT] Kč** |
| C | Opce bivalence (není v ceně díla, podle čl. 3.5) | varianty podle Přílohy 2 |

7.2 Cena je sjednána jako **pevná** pro rozsah podle Příloh 1, 2, 3 a 8 a pro stav podkladů ke dni
podpisu. Zahrnuje zejména dopravu, zdvihací techniku pro osazení venkovních jednotek na místa podle
Přílohy 1 (za předpokladu přístupu podle Přílohy 5), odvoz a likvidaci odpadu, zkoušky, revize,
dokumentaci a zaškolení. Zhotovitel prohlašuje, že rozsah prací a dodávek potřebných pro funkční
kotelnu podle čl. 4.3 v Příloze 2 zohlednil. Položky, které tam chybějí a jsou pro takovou funkci
nezbytné, provede bez nároku na zvýšení ceny, ledaže vyplývají ze skutečností podle čl. 9.5.

7.3 Cena nezahrnuje: elektřinu a vodu pro zkoušky a uvedení do provozu (poskytuje objednatel
bezúplatně), provoz kotelny před předáním mimo zkoušky (čl. 11.8), pravidelný servis po předání
a plnění vyloučená podle čl. 3.4.

7.4 **DPH** se připočte v zákonné výši ke dni uskutečnění zdanitelného plnění. Pokud jsou splněny
podmínky, použije se režim přenesení daňové povinnosti podle § 92e zákona č. 235/2004 Sb.
Objednatel předá zhotoviteli nejpozději s úhradou zálohy písemné prohlášení o účelu užití stavby
pro účely určení sazby DPH (Příloha 15) a odpovídá za jeho pravdivost. Doměrek DPH způsobený
nepravdivým prohlášením nese objednatel.

7.5 Cenu lze změnit jen:
- Změnou podle čl. 9,
- v případech podle čl. 9.5 (nepředvídatelné skutečnosti),
- při změně sazby DPH,
- indexací podle čl. 7.6.

Mimo tyto případy přebírají obě strany nebezpečí změny okolností podle § 1765 odst. 2 OZ
a § 2620 odst. 2 OZ se nepoužije.

7.6 **Indexace části B.** Pokud Datum stavební připravenosti nastane po 30. 9. 2027, upraví se cena
dosud neprovedených prací a dodávek části B podle změny indexu cen stavebních děl ČSÚ (skupina
„ostatní inženýrská díla a technologie", případně celkový index) mezi měsícem podpisu smlouvy a měsícem
Data stavební připravenosti. Úprava se použije jen v rozsahu, v jakém změna indexu **přesáhne 3 %**,
a platí oběma směry. Část A se neindexuje.

### Článek 8 – Platební podmínky a zajištění

8.1 **Záloha na HTK.** Objednatel uhradí zálohu ve výši **100 % ceny části A** do [7] dnů od podpisu
smlouvy na základě výzvy k platbě (zálohové faktury). Zhotovitel vystaví daňový doklad o přijaté
platbě podle zákona o DPH. Před připsáním zálohy není zhotovitel povinen HTK objednat a lhůty podle
čl. 6.1 písm. a) a b) běží až od připsání. Záloha není smluvní pokutou ani odstupným. Vypořádá se
v konečné faktuře nebo podle čl. 17.

8.2 **Doplatek.** Zbytek ceny díla, tj. cenu části B, uplatněné Změny a indexaci (po odečtení
pozastávky podle čl. 8.4), vyfakturuje zhotovitel po předání a převzetí díla (čl. 12). Právo
vystavit fakturu vzniká dnem podpisu předávacího protokolu nebo dnem převzetí podle čl. 12.5.
Pokud však dílo nelze předat nebo dokončit zkoušky z důvodů na straně objednatele (čl. 12.6), smí
zhotovitel vyfakturovat 90 % ceny části B po mechanickém dokončení a provedení všech zkoušek, které
bylo možné provést. Zbytek vyfakturuje po odložených zkouškách.

8.3 **Zajištění zálohy objednatele.**

a) **Vlastnické právo** k HTK přechází na objednatele dnem, kdy je splněno obojí: záloha je plně
   uhrazena a HTK jsou u zhotovitele nebo v jím určeném skladu individuálně určeny výrobními čísly
   ve **Skladovém listu**. Zhotovitel ho zašle objednateli do 5 pracovních dnů od převzetí HTK od
   výrobce. Zhotovitel HTK fyzicky označí jako majetek objednatele, uloží je odděleně od jiného zboží
   a umožní objednateli jejich prohlídku po předchozím ohlášení,
b) **Nebezpečí škody** na HTK nese do převzetí díla zhotovitel, ledaže škodu způsobil objednatel
   nebo osoby, které se na stavbě podílejí na jeho straně (čl. 11.6). Zhotovitel HTK po dobu
   skladování pojistí nejméně na jejich cenu,
c) [VOLBA] Na žádost objednatele vystaví zhotovitel do 10 pracovních dnů od podpisu **bankovní záruku
   za vrácení zálohy** ve výši ceny části A s platností do dodání HTK na stavbu. Náklady záruky nese
   [objednatel / zhotovitel / každá strana polovinu]. Pokud objednatel záruku požaduje, splatnost
   zálohy běží až od jejího doručení.

8.4 **Pozastávka.** Z konečné faktury se zadrží **5 % ceny díla bez DPH**. Zhotovitel ji vyfakturuje
po odstranění všech vad a nedodělků uvedených v předávacím protokolu, nejpozději však uplynutím
[6] měsíců od převzetí, pokud objednatel do té doby písemně neuvede konkrétní neodstraněnou vadu
z protokolu. Zhotovitel může pozastávku kdykoli nahradit bankovní zárukou ve stejné výši.

8.5 **Splatnost** faktur je 14 dnů od doručení. Faktura musí mít náležitosti daňového dokladu.
Fakturu bez nich může objednatel do 5 pracovních dnů vrátit s uvedením vady. Splatnost pak běží
od doručení opravené faktury.

8.6 **Prodlení s platbou:** zákonný úrok z prodlení (§ 1970 OZ, nařízení vlády č. 351/2013 Sb.)
a smluvní pokuta podle čl. 14.3.

8.7 Objednatel smí proti pohledávkám zhotovitele započíst jen pohledávky, které zhotovitel písemně
uznal nebo které byly pravomocně přiznány, a pohledávky ze smluvních pokut uplatněné podle čl. 14.

### Článek 9 – Změny díla, vícepráce a méněpráce

9.1 Změna je závazná jen tehdy, pokud ji podepsaly oprávněné osoby ve věcech smluvních (Příloha 13)
na Změnovém listu (Příloha 9). Změnový list určí popis Změny, dopad na cenu, dopad na Realizační lhůtu
a případně na čl. 4.3.

9.2 Na žádost objednatele o Změnu předloží zhotovitel do 10 pracovních dnů nabídku. Změny se oceňují:
- jednotkovými cenami z Přílohy 2,
- pokud tam položka není, hodinovou sazbou [DOPLNIT] Kč/h a cenou materiálu podle doložené nákupní
  ceny s přirážkou [10] %.

9.3 **Méněpráce** se odečtou podle Přílohy 2. Odečíst nelze prokazatelně již objednaný nevratný materiál
a HTK. Ty se předají objednateli.

9.4 **Práce bez Změnového listu.** Na zaplacení prací nad rozsah díla provedených bez Změnového listu
nemá zhotovitel nárok, ledaže:
a) šlo o neodkladné práce k odvrácení škody nebo ohrožení (havárie) a zhotovitel o nich objednatele
   informoval bez zbytečného odkladu, nejpozději do 24 hodin, nebo
b) objednatel jejich provedení vyžádal nebo odsouhlasil písemně (i e-mailem nebo zápisem ve stavebním
   deníku) prostřednictvím oprávněné osoby a Změnový list nebyl uzavřen z důvodů na straně objednatele.

V těchto případech se práce ocení podle čl. 9.2.

9.5 **Nepředvídatelné skutečnosti.** Pokud se ukáže, že fyzické podmínky stavby nebo napojovacích bodů
se odchylují od vstupních podkladů (Příloha 3) nebo od Přílohy 5 a zhotovitel to nemohl zjistit
s odbornou péčí z podkladů ani z prohlídky místa, zhotovitel:
- to objednateli bez zbytečného odkladu písemně oznámí,
- v nezbytném rozsahu přeruší dotčené práce,
- navrhne řešení.

Pokud objednatel řešení odsouhlasí nebo jinak určí postup, má zhotovitel nárok na úpravu ceny
a Realizační lhůty podle čl. 9.2. Důsledky odchylek, které zhotovitel mohl s odbornou péčí zjistit,
nese zhotovitel.

9.6 **Neshoda o ceně Změny.** Pokud se strany neshodnou na ceně Změny a objednatel písemně trvá na jejím
provedení, zhotovitel ji provede, je-li technicky proveditelná a nevyžaduje-li oprávnění, které nemá.
Zatím se fakturuje podle čl. 9.2 a spor o výši ceny se řeší podle čl. 19. Nesouhlas s cenou není
důvodem k přerušení prací na zbytku díla.

9.7 Změna právních předpisů nebo závazných norem po podpisu smlouvy, která mění požadavky na dílo,
je Změnou.

9.8 **Náhrada výrobku.** Pokud výrobce přestane dodávat některou HTK nebo jiný komponent nebo změní
jeho provedení, může zhotovitel se souhlasem objednatele dodat rovnocenný výrobek s parametry
ne horšími. Objednatel souhlas bezdůvodně neodepře. Cena díla se tím nezvyšuje.

### Článek 10 – Součinnost objednatele

10.1 Objednatel zejména:
a) předá podklady podle Přílohy 3 a bez zbytečného odkladu jejich změny,
b) zajistí Stavební připravenost podle Přílohy 5 a přístup na staveniště v pracovní dny od 7 do 18 hodin,
c) bezúplatně poskytne elektřinu a vodu pro montáž, zkoušky a uvedení do provozu, uzamykatelný sklad
   nebo plochu a sociální zázemí,
d) koordinuje ostatní zhotovitele stavby a zajistí koordinátora BOZP, pokud to vyžaduje zákon
   č. 309/2006 Sb.,
e) svolává kontrolní dny nejméně jednou za 14 dnů v době montáže,
f) vyjadřuje se k dokumentaci a dotazům zhotovitele v lhůtách podle smlouvy, jinak do 10 pracovních dnů,
g) zajistí smlouvu s distributorem elektřiny s rezervovaným příkonem podle Přílohy 3, internetovou
   konektivitu a veřejnoprávní povolení,
h) převezme dílo podle čl. 12 a určí osobu odpovědnou za provoz kotelny po předání.

10.2 Při prodlení objednatele se součinností se Realizační lhůta prodlouží podle čl. 6.4 a objednatel
nahradí zhotoviteli účelně vynaložené a doložené náklady prostojů a opakovaných výjezdů. Pokud
prodlení trvá déle než 30 dnů od písemné výzvy, může zhotovitel přerušit práce podle čl. 16.
Pokud trvá déle než 90 dnů, může zhotovitel od smlouvy odstoupit podle čl. 17.2.

### Článek 11 – Provádění díla

11.1 Zhotovitel provádí dílo s odbornou péčí, v souladu s právními předpisy, s normami ČSN uvedenými
v Příloze 1 (zejména ČSN EN 12828, ČSN 06 0310, ČSN 06 0320, ČSN 06 0830, ČSN EN 378 a souboru
ČSN 33 2000), s dodavatelskou dokumentací a s pokyny výrobců.

11.2 Zhotovitel vede montážní deník nebo zapisuje do stavebního deníku objednatele, pokud je veden
podle stavebního zákona. Záznamy podepsané oprávněnými osobami jsou dokladem o skutečnostech,
nemění však smlouvu (kromě čl. 9.4 písm. b)).

11.3 Zhotovitel vyzve objednatele ke kontrole prací, které budou zakryty nebo se stanou nepřístupnými,
nejméně 3 pracovní dny předem. Pokud se objednatel nedostaví, může zhotovitel pokračovat. Pokud
objednatel později požádá o odkrytí, nese náklady ten, v jehož neprospěch kontrola vyzněla.

11.4 Zhotovitel smí použít poddodavatele. Odpovídá za ně, jako by plnil sám. Uvedení TČ do provozu
provede technik autorizovaný výrobcem.

11.5 Zhotovitel dodržuje předpisy BOZP a požární ochrany, udržuje pořádek na svém pracovišti a jako
původce odpadů je likviduje podle zákona č. 541/2020 Sb.

11.6 **Nebezpečí škody na díle** nese zhotovitel do převzetí díla. Neodpovídá však za škody, které
způsobil objednatel, jeho ostatní zhotovitelé nebo jiné osoby, jimž objednatel umožnil přístup
na stavbu. Pokud škodu zjistí, zapíše ji bez zbytečného odkladu do deníku.

11.7 **Pojištění.** Zhotovitel má po celou dobu plnění a do konce záruční doby podle čl. 13.1 pojištění
odpovědnosti za škodu s limitem nejméně [10 000 000] Kč. Na vyžádání předloží pojistný certifikát.
Pokud objednatel sjedná stavebně-montážní pojištění stavby, zahrne do něj zhotovitele jako
spolupojištěného.

11.8 **Předčasné užívání.** Kotelnu lze před převzetím užívat (vysoušení stavby, temperování, vytápění
částečně obydleného domu) jen na základě písemného **protokolu o předčasném užívání**. Ten zaznamená
stav, motohodiny, odečty a nastavení. Od podpisu protokolu:
- nese objednatel náklady energií a provozní odpovědnost,
- nese objednatel nebezpečí škody způsobené provozem nebo zásahy jiných osob,
- zhotovitel nadále odpovídá za vady díla,
- zhotovitel má nárok na preventivní servisní prohlídku před předáním na náklady objednatele,
  pokud předčasné užívání trvalo déle než [60] dnů. Prohlídka spočívá ve výměně filtrů a kontrole
  kvality topné vody.

Předčasné užívání není převzetím díla (srov. čl. 12.5).

### Článek 12 – Dokončení, zkoušky a předání: „předaná a funkční kotelna"

12.1 **Dílo je dokončeno**, jsou-li splněny všechny tyto podmínky:

a) **Mechanické dokončení:** všechny položky podle Přílohy 1 jsou namontovány, propojeny, izolovány
   a označeny,
b) **zkoušky podle Přílohy 10 s kladným výsledkem:** tlakové zkoušky, proplach, napuštění vodou
   upravenou podle ČSN 07 7401 (hodnoty v protokolu), výchozí revize elektrické instalace RK
   a navazujících obvodů, doklady k tlakovým zařízením podle předpisů,
c) **uvedení všech tří TČ do provozu** autorizovaným technikem výrobce, doložené protokolem,
   který je podmínkou záruky výrobce,
d) **funkční zkoušky řízení:**
   - každá TČ samostatně,
   - kaskáda,
   - všechny režimy A–D podle Přílohy 4 včetně simulace poruchy TČ1 a TČ2 s automatickým připojením TČ3,
   - ekvitermní regulace,
   - nabití TUV na nastavenou teplotu,
   - úplný cyklus termické dezinfekce,
   - výpadek napájení a automatický restart,
   - protizámrazová ochrana,
   - bezpečnostní vypnutí,
   - doručení alarmu určenému příjemci,
   - čitelnost datových bodů přes Modbus TCP,
e) **komplexní zkouška:** 72 hodin nepřetržitého automatického provozu bez poruchy, která by bránila
   provozu. Provede se při skutečném odběru tepla domu. Pokud skutečný odběr není k dispozici,
   provede se se simulovaným odběrem v rozsahu, který podmínky dovolují, a s protokolem. Výkonová
   zkouška při výpočtové venkovní teplotě se neprovádí,
f) **doklady podle Přílohy 6** jsou předány. Dokumentaci skutečného provedení lze předat nejpozději
   do 15 dnů po převzetí jako nedodělek. Návody, revizní zprávy, protokoly o zkouškách, protokoly
   o uvedení do provozu a provozní řád kotelny musí být předány nejpozději při převzetí,
g) **zaškolení** nejméně [3] osob určených objednatelem v rozsahu [4] hodin, s prezenční listinou.

12.2 **Předaná a funkční kotelna** je dílo dokončené podle čl. 12.1 a převzaté předávacím protokolem
nebo podle čl. 12.5. Taková kotelna:
- dodává v automatickém režimu bez zásahu obsluhy teplo do otopné soustavy podle ekvitermní křivky,
- připravuje TUV v rozsahu čl. 4.3 písm. b),
- má funkční zálohu (TČ3) a funkční termickou dezinfekci,
- nemá aktivní poruchová hlášení, která by bránila provozu.

12.3 **Předávací řízení.** Zhotovitel vyzve objednatele k převzetí nejméně 5 pracovních dnů předem.
Předávací protokol obsahuje:
- zjištěný stav,
- soupis vad a nedodělků s termíny odstranění (nestanoví-li se jinak, 30 dnů),
- odečty elektroměru a případných měřičů tepla,
- motohodiny TČ,
- seznam předaných dokladů,
- výsledek převzetí.

12.4 **Drobné vady a odmítnutí převzetí.**

a) Objednatel nesmí odmítnout převzetí pro drobné vady a nedodělky (čl. 2.7, § 2628 OZ). Ty se
   zapíší do protokolu s termínem odstranění,
b) za drobné se **nikdy** nepovažují:
   - nefunkční TČ,
   - nefunkční záloha TČ3 nebo přepínání režimů,
   - nefunkční ohřev TUV nebo termická dezinfekce,
   - nefunkční bezpečnostní a ochranné prvky,
   - chybějící výchozí revize elektro,
   - chybějící protokoly o uvedení TČ do provozu,
   - únik média,
c) pokud objednatel převzetí odmítne, písemně a konkrétně uvede vady, pro které převzetí odmítá.
   Po jejich odstranění se předávací řízení opakuje jen v rozsahu těchto vad.

12.5 **Fikce převzetí.** Dílo se považuje za převzaté:

a) pokud objednatel nezahájí předávací řízení nebo nepodepíše protokol a ani neuvede konkrétní vady
   podle čl. 12.4 písm. c) do 10 pracovních dnů od výzvy k převzetí a nenapraví to ani v dodatečné
   lhůtě 5 pracovních dnů od další písemné výzvy, která na tento následek výslovně upozorní.
   Dílo je pak převzato posledním dnem dodatečné lhůty, nebo
b) pokud objednatel začne kotelnu užívat k vytápění nebo přípravě TUV pro uživatele bytů a do
   14 dnů od začátku takového užívání zhotoviteli písemně nesdělí konkrétní vady podle čl. 12.4
   písm. b). To neplatí pro předčasné užívání podle čl. 11.8 a pro užívání nezbytné k odvrácení škody
   (např. mrazem), o kterém objednatel zhotovitele písemně informuje.

12.6 **Zkoušky zmařené na straně objednatele.** Pokud nelze některou zkoušku podle čl. 12.1 provést
z důvodu na straně objednatele, provede zhotovitel zkoušky v rozsahu, v jakém je to možné. Takovým
důvodem je zejména chybějící trvalé napájení, chybějící otopná soustava nebo nenapuštěná otopná soustava
domu. Zbývající zkoušky („**odložené zkoušky**") provede do 30 dnů od písemného oznámení, že překážka
odpadla. Do té doby platí čl. 8.2 poslední věta. Záruční doba běží od převzetí, nejpozději však
od uplynutí 6 měsíců od mechanického dokončení.

12.7 Převzetím díla přechází na objednatele nebezpečí škody. Vlastnické právo k dílu, které se stalo
součástí stavby, nabývá objednatel zabudováním. K HTK platí čl. 8.3 písm. a).

### Článek 13 – Odpovědnost za vady a záruka za jakost

13.1 **Záruka za jakost.** Zhotovitel poskytuje záruku za jakost:

| Část díla | Záruční doba |
|---|---|
| Hydraulické a montážní práce (spoje, těsnost, izolace, uložení potrubí) | [36] měsíců |
| Elektroinstalace, MaR a řídicí systém včetně software | 24 měsíců |
| HTK | 24 měsíců, případně delší záruka výrobce podle Přílohy 7 |
| Ostatní dodávky | 24 měsíců |

Záruka běží od převzetí díla. Pokud výrobce poskytuje na některou HTK delší záruku, uplatňuje objednatel
práva i po 24 měsících **vždy u zhotovitele**. Zhotovitel je vyřídí za podmínek záruky výrobce. Pokud
dodání HTK a převzetí díla dělí z důvodů na straně objednatele více než 9 měsíců, končí záruka na HTK
nejpozději uplynutím 36 měsíců od jejich dodání zhotoviteli, vždy však nejdříve 12 měsíců po převzetí díla.

13.2 **Podmínky záruky.** Kotelna se provozuje podle návodů a provozního řádu. Nejméně jednou ročně
projde servisní prohlídkou osobou autorizovanou výrobcem. Kvalita topné vody se udržuje podle Přílohy 6.
Záruka se nevztahuje na vady **způsobené nebo zhoršené** porušením těchto podmínek. Pokud servisní
prohlídka neproběhla vůbec, má se za to, že vada komponentu, kterého se prohlídka týká, byla způsobena
jejím neprovedením. Objednatel může prokázat opak. Záruka **není podmíněna** uzavřením servisní smlouvy
se zhotovitelem.

13.3 **Výluky ze záruky:**
- běžné opotřebení spotřebních dílů (filtry, těsnění, pojistky),
- poškození vnějšími vlivy mimo kontrolu zhotovitele (přepětí z distribuční soustavy nad rámec ochran
  podle projektu, úder blesku, povodeň),
- zásahy nebo změny nastavení provedené neoprávněnou osobou,
- nesprávná obsluha,
- vady podkladů nebo pokynů objednatele, na něž zhotovitel upozornil podle čl. 5.2.

Zhotovitel prokazuje, že vada spadá pod výluku.

13.4 **Reklamace a reakční doby.** Reklamace se uplatňuje písemně nebo e-mailem na adresu podle Přílohy 13
s popisem projevu vady. Havarijní vady se hlásí také telefonicky na servisní linku.

| Kategorie | Zahájení odstraňování | Obnovení provozu / odstranění |
|---|---|---|
| Havarijní vada | vzdálená diagnostika do 4 h, nástup na místo do 24 h (i o víkendech a svátcích v topném období 1. 9.–31. 5.) | provizorní obnovení dodávky tepla/TUV do 48 h od nahlášení, odstranění bez zbytečného odkladu |
| Provozní vada | do 3 pracovních dnů | do 15 dnů |
| Ostatní vady | do 10 pracovních dnů | v dohodnuté přiměřené lhůtě, jinak do 30 dnů |

Pokud odstranění vady závisí na dodání náhradního dílu výrobcem, prodlužuje se lhůta k odstranění
o dodací lhůtu dílu. Zhotovitel musí prokázat, že díl objednal bez zbytečného odkladu. Prodloužení
je nejvýše 30 dnů. Pokud v topném období provozní vada podle kategorie trvá déle než 10 dnů
a zbývající zdroje prokazatelně nepokrývají potřebu tepla, zajistí zhotovitel na své náklady
provizorní zdroj tepla (např. mobilní elektrokotel) až do odstranění vady.

13.5 **Neoprávněná reklamace.** Pokud se ukáže, že vada nespadá pod záruku a objednatel to mohl při
běžné péči zjistit, uhradí náklady výjezdu a práce podle ceníku v Příloze 11. Příklady: vypnutý jistič,
výpadek distribuční sítě, zavřená armatura za rozhraním. Pro havarijní hlášení v dobré víře se to
nepoužije.

13.6 **Práva z vad.** Objednatel má právo na:
- odstranění vady opravou nebo výměnou,
- přiměřenou slevu, pokud vada není odstraněna ani v dodatečné přiměřené lhůtě (nejméně 10 dnů),
- odstoupení jen pro podstatnou vadu, kterou zhotovitel neodstranil ani v dodatečné lhůtě.

Pokud zhotovitel vadu v dodatečné lhůtě neodstraní, může ji objednatel odstranit sám nebo prostřednictvím
třetí osoby (u HTK osoby autorizované výrobcem) na účelně vynaložené náklady zhotovitele. Záruka na
ostatní části díla tím není dotčena.

13.7 **Postoupení práv ze záruky.** Objednatel smí bez souhlasu zhotovitele postoupit práva z vad a ze
záruky na společenství vlastníků jednotek domu nebo na nabyvatele domu. Postoupení zhotoviteli oznámí.
Objednatel předá postupníkovi podmínky záruky podle čl. 13.2 a Přílohy 6 a písemně ho s nimi seznámí.
Jinak objednatel odpovídá za důsledky jejich nedodržení způsobené neznalostí. Postoupení smlouvy jako
celku před převzetím díla vyžaduje souhlas zhotovitele, který ho bezdůvodně neodepře.

13.8 Zhotovitel nabídne pozáruční a záruční servis za podmínek Přílohy 11. Servisní smlouva je
samostatná a není podmínkou záruky.

### Článek 14 – Smluvní pokuty

14.1 **Prodlení s dokončením.** Při prodlení zhotovitele s dokončením a předáním díla v termínu
dokončení (čl. 6.1 písm. d) a 6.4) zaplatí zhotovitel smluvní pokutu **0,05 % z ceny díla bez DPH**
za každý den prodlení. Celkem nejvýše **10 % ceny díla bez DPH**.

14.2 **Prodlení s vadami.** Při prodlení zhotovitele:
a) s nástupem na havarijní vadu: [5 000] Kč za každý započatý den,
b) s obnovením provozu nebo odstraněním havarijní vady: [3 000] Kč za každý den,
c) s odstraněním jiné vady nebo nedodělku: [500] Kč za každou vadu a den.

Celkem nejvýše **5 % ceny díla bez DPH**.

14.3 **Prodlení objednatele** s úhradou peněžitého dluhu: smluvní pokuta **0,05 % z dlužné částky** za
každý den prodlení. Celkem nejvýše 10 % dlužné částky. Úrok z prodlení tím není dotčen.

14.4 **Vztah k náhradě škody.** Smluvní pokuta podle čl. 14.1 je jediným peněžitým nárokem objednatele
z prodlení s dokončením. Nárok na odstoupení podle čl. 17.3 tím není dotčen. Vedle ostatních pokut lze
požadovat náhradu škody v rozsahu, v jakém je převyšuje, v limitu čl. 15.

14.5 Souhrn všech smluvních pokut zhotovitele nepřesáhne **15 % ceny díla bez DPH**. Pokuta je splatná
do 30 dnů od doručení písemného vyúčtování, které uvede důvod a výpočet.

### Článek 15 – Náhrada škody a limitace

15.1 Strany odpovídají za škodu podle OZ, s omezeními podle tohoto článku.

15.2 Náhrada ušlého zisku a nepřímých škod je vyloučena. Nepřímou škodou se rozumí zejména nároky
nájemců nebo kupujících bytů, ztráty z prodeje jednotek, sankce vůči třetím osobám a vyšší náklady
na energie.

15.3 Celková odpovědnost zhotovitele za škodu a smluvní pokuty je omezena na **100 % ceny díla bez DPH**.
Pokud je škoda kryta pojištěním podle čl. 11.7, je limitem vyšší z částek: cena díla, nebo skutečné
pojistné plnění.

15.4 Omezení podle čl. 15.2 a 15.3 se nepoužijí:
- na škodu způsobenou úmyslně nebo z hrubé nedbalosti,
- na újmu na zdraví a jiných přirozených právech člověka (§ 2898 OZ),
- na povinnost vrátit zálohu nebo vydat HTK podle čl. 17.

15.5 **Okolnost vylučující odpovědnost.** Strana, které taková okolnost brání v plnění, to druhé straně
oznámí bez zbytečného odkladu. Lhůty se prodlužují o dobu jejího trvání. Pokud trvá déle než 90 dnů,
může kterákoli strana od smlouvy odstoupit s vypořádáním podle čl. 17.2 písm. b), bez odstupného.

### Článek 16 – Přerušení prací

16.1 Zhotovitel může přerušit práce po předchozím písemném oznámení s lhůtou 5 pracovních dnů:
- je-li objednatel v prodlení s platbou déle než 15 dnů,
- je-li objednatel v prodlení se součinností, bez níž nelze pokračovat,
- při bezprostředním ohrožení bezpečnosti.

Lhůty se prodlouží o dobu přerušení a o přiměřenou dobu ke znovuzahájení. Doložené náklady přerušení
hradí objednatel. **Zhotovitel nesmí jako prostředek nátlaku omezit, zablokovat ani vzdáleně vypnout
provoz předané nebo předčasně užívané kotelny.**

16.2 Objednatel může práce přerušit ze svého rozhodnutí na celkem nejvýše [60] dnů. Doložené náklady
přerušení nahradí. Delší přerušení opravňuje zhotovitele odstoupit podle čl. 17.2.

### Článek 17 – Ukončení smlouvy; ochrana zhotovitele po objednání technologií

17.1 **Odstoupení objednatele za odstupné (§ 1992 OZ).** Objednatel může od smlouvy odstoupit bez
udání důvodu kdykoli před převzetím díla. Vypořádá se takto:

a) **před potvrzením objednávky HTK výrobcem:** objednatel zaplatí náklady na dokumentaci podle
   Přílohy 2 v rozsahu, v jakém byla provedena, a odstupné [2] % z ceny díla bez DPH. Zbytek zálohy
   zhotovitel vrátí do 30 dnů,
b) **po potvrzení objednávky HTK výrobcem:** zhotovitel se bez zbytečného odkladu pokusí objednávku
   stornovat, jinak HTK prodat třetí osobě za přiměřenou cenu. Objednatel si může zvolit, že HTK
   převezme. V tom případě se čl. 17.1 písm. b) bod ii. nepoužije,
c) objednatel zaplatí:
   - i. doložené storno poplatky výrobce a dodavatelů, nebo, pokud storno nebylo možné,
   - ii. rozdíl mezi cenou HTK podle Přílohy 2 a výtěžkem prodeje HTK sníženým o doložené náklady
     prodeje. Pokud HTK nebudou prodány do 90 dnů, převezme je objednatel za cenu části A,
   - iii. cenu již provedených prací a dodávek části B podle Přílohy 2,
   - iv. odstupné **5 % z ceny dosud neprovedené části B** jako paušální náhradu za rezervaci kapacit
     a ušlý zisk,
d) úhrady podle písm. c) se započtou na zálohu. Přeplatek zhotovitel vrátí do 30 dnů od vyúčtování,
   nedoplatek je splatný do 14 dnů,
e) HTK, které objednatel uhradil a které nebyly stornovány ani prodány, zhotovitel vydá objednateli
   v místě skladu.

17.2 **Odstoupení zhotovitele.** Zhotovitel může odstoupit:
a) je-li objednatel v prodlení s úhradou zálohy déle než 30 dnů nebo s jinou platbou déle než 30 dnů
   od písemné upomínky; je-li v prodlení se součinností podle čl. 10.2; v případě čl. 6.5 písm. d)
   a 16.2; nebo bylo-li na majetek objednatele vydáno rozhodnutí o úpadku,
b) vypořádání: objednatel zaplatí částky podle čl. 17.1 písm. c) body i. až iv. a náhradu škody
   v limitu čl. 15. V případech čl. 6.5 písm. d) a 15.5 se odstupné podle bodu iv. neplatí.

17.3 **Odstoupení objednatele pro porušení zhotovitelem.** Objednatel může odstoupit:
- je-li zhotovitel v prodlení s objednáním HTK déle než 30 dnů,
- je-li zhotovitel v prodlení s termínem dokončení déle než [60] dnů a nesjedná nápravu ani v dodatečné
  lhůtě 15 dnů,
- neodstraní-li zhotovitel podstatnou vadu podle čl. 13.6,
- bylo-li na majetek zhotovitele vydáno rozhodnutí o úpadku.

Vypořádání:
- zhotovitel bez zbytečného odkladu vydá objednateli HTK (čl. 8.3 písm. a)) a veškerou dokumentaci
  vytvořenou pro dílo,
- objednatel zaplatí jen cenu provedené a použitelné části díla podle Přílohy 2,
- zhotovitel nahradí objednateli účelně vynaložené přiměřené vícenáklady na dokončení díla jiným
  zhotovitelem v limitu čl. 15,
- na provedenou část díla se vztahuje záruka podle čl. 13.

17.4 Odstoupení nemá vliv na:
- vlastnické právo k HTK podle čl. 8.3,
- nároky na smluvní pokuty vzniklé před odstoupením,
- nároky na náhradu škody,
- práva z vad provedené části,
- ustanovení o vypořádání a řešení sporů.

17.5 Do 10 pracovních dnů od odstoupení sepíší strany protokol o stavu rozpracovanosti a soupis HTK
a materiálu. Vyúčtování předloží zhotovitel do 30 dnů.

### Článek 18 – Oprávněné osoby, komunikace a forma

18.1 Oprávněné osoby ve věcech smluvních a technických jsou uvedeny v Příloze 13. Změnové listy
a dodatky podepisují jen osoby oprávněné ve věcech smluvních.

18.2 Smlouvu lze měnit jen písemnými číslovanými dodatky nebo Změnovými listy. Za písemnou formu se
nepovažuje výměna e-mailů bez elektronického podpisu, s výjimkou čl. 6.1 písm. b), 9.4 písm. b)
a reklamací.

18.3 Oznámení se doručují na adresy podle Přílohy 13. Doručení odstoupení a výzvy podle čl. 12.5
vyžaduje doporučený dopis, datovou schránku nebo e-mail podepsaný kvalifikovaným elektronickým podpisem.

### Článek 19 – Řešení sporů

19.1 Spory řeší nejprve statutární zástupci stran jednáním, které se uskuteční do 15 dnů od výzvy.

19.2 Technické spory (existence a příčina vady, soulad s čl. 4.3, ocenění Změny) mohou strany předložit
znalci nebo znaleckému ústavu vybranému dohodou, případně prvnímu ze tří navržených objednatelem,
kterého zhotovitel neodmítne. Posudek není pro strany závazný, strany ale prohlašují, že jej použijí
jako podklad v případném řízení. Náklady posudku nese strana, jejíž stanovisko posudek nepotvrdil,
jinak každá polovinu.

19.3 Nedojde-li k dohodě, rozhodují soudy České republiky. Místně příslušným soudem prvního stupně je
[VOLBA: Okresní soud v Ostravě / Krajský soud v Ostravě / soud podle sídla žalovaného] (§ 89a o. s. ř.).

### Článek 20 – Závěrečná ustanovení

20.1 Smlouva se řídí právem České republiky, zejména OZ.

20.2 Smlouva obsahuje úplné ujednání o předmětu smlouvy a nahrazuje předchozí ujednání, nabídky
a korespondenci. Obchodní zvyklosti nemají přednost před ustanoveními zákona, jež nemají donucující
účinky (§ 558 odst. 2 OZ se nepoužije). Použití § 1740 odst. 3 OZ se vylučuje.

20.3 **Pořadí dokumentů při rozporu:**
1. Změnové listy (pozdější před dřívějším),
2. text smlouvy,
3. Příloha 4,
4. Příloha 1,
5. Příloha 8,
6. Příloha 5,
7. Příloha 2,
8. ostatní přílohy.

Rozpor mezi přílohami, který zhotovitel s odbornou péčí mohl zjistit, je povinen oznámit bez
zbytečného odkladu.

20.4 Neplatnost nebo neúčinnost některého ustanovení nemá vliv na ostatní. Strany jej nahradí
ustanovením, které se jeho účelu nejvíce blíží.

20.5 Smlouva nabývá platnosti a účinnosti podpisem obou stran. Je podepsána elektronicky nebo ve dvou
listinných vyhotoveních, z nichž každá strana obdrží jedno.

20.6 Nedílnou součástí smlouvy jsou Přílohy 1 až 15.

V ______________ dne ___________    V ______________ dne ___________

__________________________    __________________________
za zhotovitele: Riva Trade, s.r.o.    za objednatele: [DOPLNIT]

---

## C. Seznam příloh a osnova klíčových příloh

### C.1 Seznam příloh

| Č. | Příloha | Kdo připraví | Kritičnost |
|---|---|---|---|
| 1 | Technická specifikace a rozsah díla (vč. výkresů TV-BDM-04, TV-BDM-05, seznamu norem) | zhotovitel | vysoká |
| 2 | Položkový rozpočet: část A (HTK po položkách), část B, část C (varianty bivalence), jednotkové ceny, hodinová sazba, cena dokumentace | zhotovitel | vysoká |
| 3 | Vstupní podklady a jejich status (PENB, DPS D102–D105, TZ elektro, FVE, koncepce vytápění 07/2026; hodnoty: ztráta 53 kW, návrhové teploty, odběr TUV, rezervovaný příkon, HDO) + Výhrady zhotovitele | objednatel + zhotovitel | vysoká |
| 4 | Provozní filozofie a funkční specifikace řízení (režimy A–D, kaskáda, prahy deficitu, střídání rolí, TUV a termická dezinfekce, alarmy, seznam datových bodů Modbus TCP) | zhotovitel | vysoká |
| 5 | Podmínky stavební připravenosti a vzor protokolu | zhotovitel | vysoká |
| 6 | Seznam dokladů k předání + požadavky na kvalitu topné vody | zhotovitel | střední |
| 7 | Datové listy HTK (výkonové tabulky X50, nádrže, výměník) a záruční podmínky výrobce | zhotovitel | vysoká |
| 8 | Matice rozhraní dodávek a odpovědností | obě strany | vysoká |
| 9 | Vzor Změnového listu | zhotovitel | střední |
| 10 | Program zkoušek a vzor předávacího protokolu | zhotovitel | vysoká |
| 11 | Servisní podmínky, reakční doby, ceník pozáručního servisu a výjezdů | zhotovitel | střední |
| 12 | Rámcový harmonogram (relativně k Datu stavební připravenosti) | zhotovitel | střední |
| 13 | Oprávněné osoby, kontakty, servisní linka, adresy pro doručování | obě strany | střední |
| 14 | Vzor Skladového listu HTK; (volitelně) vzor bankovní záruky za zálohu | zhotovitel | střední |
| 15 | Prohlášení objednatele k DPH (účel užití stavby, § 92e) | objednatel | nízká |

### C.2 Osnova Přílohy 5 – podmínky stavební připravenosti

1. Kotelna: dokončené stavební konstrukce, omítky/nátěry, podlaha s povrchovou úpravou, uzamykatelné
   dveře, osvětlení, větrání, podlahová vpusť nebo napojovací bod kanalizace, protokol o zkoušce
   nosnosti nebo statické posouzení pro nádrže (2× 1 000 l + 3× 1 000 l v provozu, cca [7,5] t).
2. Venkovní jednotky: základy/konzoly podle výkresů zhotovitele (zatížení cca 370 kg na jednotku
   plus sníh a vítr), zpevněná příjezdová plocha pro jeřáb/manipulaci, prostupy pro potrubí a kabely,
   odvod kondenzátu (nezamrzající trasa), splnění ochranných pásem R290 podle PBŘ.
3. Elektro: přívod do místa RK dimenzovaný na rezervovaný příkon podle Přílohy 3, předřazené jištění,
   hlavní ochranná přípojnice, trvalé napájení nejpozději k zahájení uvedení do provozu.
4. Voda a kanalizace: přívod studené vody s vodoměrem a uzávěrem, tlak [min. 3 bar], napojovací body.
5. Otopná soustava domu: rozvody napojené k hranici rozhraní, tlakově odzkoušené, propláchnuté,
   schopné odběru tepla (pro komplexní zkoušku).
6. TUV: rozvody a cirkulace k hranici rozhraní, tlakově odzkoušené.
7. Přístup, sklad, zázemí, internetová konektivita v kotelně (pro dálkový dohled).

### C.3 Osnova Přílohy 8 – matice rozhraní (výřez)

| Položka | Dodá | Namontuje | Odpovídá za funkci | Pozn. |
|---|---|---|---|---|
| Základy/konzoly venkovních jednotek | O | O | O (statika) | podle výkresu Z |
| Antivibrační prvky TČ | Z | Z | Z | |
| Prostupy a požární ucpávky | O | O | O | Z dodá polohy a DN |
| Primární potrubí TČ–kotelna vč. izolace | Z | Z | Z | |
| Rozdělovač/sběrač + uzávěry větví | Z | Z | Z | hranice ÚT |
| Rozvody ÚT za uzávěry, otopná tělesa, vyvážení | O | O | O | |
| Deskový výměník, nabíjecí čerpadlo, zásobníky TUV | Z | Z | Z | |
| Cirkulace TUV mimo kotelnu, vyvážení cirkulace | O | O | O | vliv na teplotu u výtoků (čl. 4.5) |
| RK, kabeláž kotelny, MaR | Z | Z | Z | |
| Přívod do RK, jištění, rezervovaný příkon | O | O | O | |
| FVE, baterie, energetický manažer | O | O | O | Z: datové body Modbus |
| Integrace řízení FVE → kotelna | – | – | – | jen Změnou |
| Hluková studie, protihluková opatření | O | O | O | Z: akustická data |
| Bivalentní zdroj | Z* | Z* | Z* | *jen při uplatnění opce |
| Měřiče tepla pro rozúčtování | O | O | O | volitelně Změnou |

(Z = zhotovitel, O = objednatel nebo jeho zhotovitelé)

### C.4 Osnova Přílohy 10 – program zkoušek

1. Tlaková zkouška primáru a okruhů kotelny (ČSN EN 14336 přiměřeně), protokol.
2. Proplach, napuštění, rozbor/měření upravené vody (vodivost, pH, tvrdost), protokol.
3. Výchozí revize elektro RK a obvodů kotelny.
4. Uvedení TČ1–TČ3 do provozu autorizovaným technikem, protokoly výrobce.
5. Funkční zkoušky podle čl. 12.1 písm. d) – kontrolní list s položkami A–D, simulace poruch.
6. Nabití TUV na setpoint a úplný cyklus termické dezinfekce, záznam teplot.
7. Výpadek napájení a restart, protizámrazová funkce, alarmové zprávy.
8. Ověření datových bodů Modbus TCP (výpis hodnot).
9. Komplexní zkouška 72 h – trend záznam z řídicího systému.
10. Předávací protokol – vzor s oddíly podle čl. 12.3.

---

## D. Riziková analýza z pohledu zhotovitele

Pravděpodobnost (P) a dopad (D): N = nízká, S = střední, V = vysoká.

| # | Riziko | P | D | Jak ho řeší smlouva | Zbytkové riziko a doporučení |
|---|---|---|---|---|---|
| 1 | **Reklamace „nedostatečného výkonu"** v mrazech (2 TČ ≈ 49,6 kW proti 53 kW + TUV) | V | V | čl. 4.1–4.3 (TČ3 jako třetí stupeň je součást filozofie, výkonový závazek jen při 3 TČ), opce bivalence čl. 3.5 | Nechte si **písemně potvrdit**, že objednatel bivalenci odmítá (e-mail nebo zápis). Ověřte ztrátu výpočtem podle ČSN EN 12831. Hodnota z PENB může být jiná. |
| 2 | Dlouhé zpoždění stavby, HTK leží ve skladu | V | S | čl. 6.5 (skladné, dodání na stavbu, long-stop 30. 6. 2028), čl. 7.6 indexace, čl. 13.1 omezení záruky HTK | Ověřte u výrobce, **od kdy běží jeho záruka** (dodání × uvedení do provozu). Pokud od dodání, drží zhotovitel riziko rozdílu. Vyjednejte s výrobcem registraci od uvedení do provozu. |
| 3 | Objednatel odstoupí po objednání HTK | S | V | čl. 17.1 (storno, prodej, převzetí HTK, odstupné 5 % z neprovedené části B), záloha 100 % na HTK | Nízké, protože záloha kryje HTK. Riziko zůstává u kurzových rozdílů při prodeji. |
| 4 | Objednatel neuhradí doplatek, ale kotelnu užívá | S | V | čl. 12.5 písm. b) fikce převzetí užíváním, čl. 8.4 pozastávka jen 5 %, čl. 14.3 pokuta, úrok | Záměrně **bez** vzdáleného vypnutí (čl. 16.1). Bylo by protiprávní vůči obyvatelům. Proti insolvenci objednatele chrání jen rychlé vymáhání. Zvažte ručení mateřské společnosti / SPV. |
| 5 | Insolvence objednatele (developer SPV) | N–S | V | záloha na HTK, čl. 17.2 | Část B se předfinancuje až do předání. Zvažte **dílčí fakturaci** části B (viz G.2). |
| 6 | Teplota TUV u výtoků pod 50 °C, hygienická stížnost | S | S | čl. 4.5 (odpovědnost za výstup ze zásobníků; výtoky a cirkulace jsou objednatele), upozornění podle § 2594 | Doporučte objednateli výpočet cirkulace. Udržujte záznamy termické dezinfekce. |
| 7 | Hluk TČ, stížnosti sousedů nebo KHS | S | S | čl. 4.6 (hluková studie je objednatele), odpovědnost jen za montáž a data | Dodejte akustická data včas a písemně. Jinak hrozí výtka nedostatečné součinnosti. |
| 8 | Zamrznutí primáru při výpadku proudu | S | V | čl. 12.1 písm. d) zkouška protizámrazové ochrany, čl. 13.3 výluky | **Rozhodnutí voda/glykol** musí být v Příloze 1. Pokud voda, uveďte protizámrazové ventily a nutnost záložního napájení čerpadel (kdo ho dodá). |
| 9 | Nelze dokončit komplexní zkoušku (dům bez odběru tepla, bez trvalého napájení) | V | S | čl. 12.6 odložené zkoušky, čl. 8.2 fakturace 90 % části B | Novostavba – toto je velmi pravděpodobné. Dodržujte formální výzvy. |
| 10 | Předčasné užívání k vysoušení stavby opotřebí TČ | S | S | čl. 11.8 protokol, preventivní servis, přechod nebezpečí | Bez protokolu nepouštět. Vysoušení zatěžuje filtry a kvalitu vody. |
| 11 | Poškození TČ jinými profesemi | S | S | čl. 11.6 (nebezpečí na objednateli za škody jeho zhotovitelů) | Fotodokumentace a deníkové zápisy ihned. |
| 12 | Vícepráce na ústní pokyn stavbyvedoucího | V | S | čl. 9.4 písm. b) (e-mail/deník postačí) | Disciplína: každý pokyn nad rámec potvrdit e-mailem oprávněné osoby ještě týž den. |
| 13 | Neúplný rozpočet – chybějící položky nutné k funkci | S | S | čl. 7.2 (riziko nese zhotovitel), čl. 9.5 (jen nezjistitelné skutečnosti) | Toto je férová cena za pevnou cenu. Důkladně zkontrolujte Přílohu 2 proti TV-BDM-04. |
| 14 | Sankce za prodlení a náhrady škody (kupující bytů) | S | V | čl. 14.1 strop 10 %, čl. 14.4 pokuta jako jediný nárok, čl. 15.2 vyloučení nepřímých škod, čl. 15.3 limit | Zbytkově: hrubá nedbalost limit prolomí. |
| 15 | Záruka výrobce kratší nebo s jinými podmínkami než záruka zhotovitele | S | S | čl. 13.1 (HTK 24 měsíců a delší „back-to-back"), čl. 13.2 podmínky | Sladit záruční podmínky výrobce s Přílohou 7 **před podpisem**. |
| 16 | Náhrada výrobku (výrobce změní model) | N | S | čl. 9.8 | HTK se objednávají ihned po záloze, takže riziko je malé. |
| 17 | Chybně určená sazba DPH | N | S | čl. 7.4 prohlášení objednatele | Konzultovat s daňovým poradcem u bytového domu (sociální bydlení). |
| 18 | Objednatel je spotřebitel | N | V | čl. 1.3 prohlášení | Pokud ano, smlouvu přepracovat (A.3 bod 1). |
| 19 | Zdražení montáže mezi podpisem a realizací 2027/2028 | S | S | čl. 7.6 indexace nad 3 % (jen při připravenosti po 30. 9. 2027) | Do 30. 9. 2027 nese riziko zhotovitel. Počítejte s tím v kalkulaci. |
| 20 | Hořlavé chladivo R290 – ochranná pásma nesplněna na stavbě | S | V | čl. 4.7, Příloha 5 bod 2 | Nemontovat do nevyhovujícího umístění. Zapsat výhradu a postupovat podle čl. 5.2. |

---

## E. Zátěžový test: slabá místa verze 1.0 a jejich opravy

Postup: nejdřív vznikla verze 1.0 psaná primárně z pohledu zhotovitele. Pak jsem ji četl jako advokát
objednatele s úkolem najít ustanovení, která jsou neplatná, nejasná, zneužitelná nebo nepřijatelná,
a postup opravy. U každého bodu je uvedeno původní znění verze 1.0, útok objednatele, oprava a místo
ve finálním znění (v2.0).

### E.1 Ustanovení napadnutelná pro neplatnost nebo neúčinnost

**1. Výhrada vlastnictví ke HTK až do úplného zaplacení ceny díla**
- *v1.0:* „Vlastnické právo k dodaným komponentům přechází na objednatele až úplným zaplacením ceny díla."
- *Útok:* Po zabudování se komponenty stávají součástí stavby (§ 506, 507 OZ) a výhrada je neúčinná.
  Před zabudováním je naopak nepřijatelná: objednatel zaplatil 100 % zálohy a při insolvenci zhotovitele
  by HTK spadly do majetkové podstaty zhotovitele. Objednatel by byl jen nezajištěným věřitelem.
- *Oprava:* Vlastnictví přechází zaplacením a individuálním určením ve Skladovém listu. Následuje
  oddělené skladování, označení, pojištění a volitelná bankovní záruka.
- *v2.0:* čl. 8.3, 12.7, 17.3.

**2. Limitace odpovědnosti bez výjimek**
- *v1.0:* „Odpovědnost zhotovitele za škodu je omezena na 50 % ceny díla."
- *Útok:* Předem nelze vyloučit ani omezit odpovědnost za újmu na přirozených právech ani za škodu
  způsobenou úmyslně nebo z hrubé nedbalosti (§ 2898 OZ). Ustanovení by bylo v tomto rozsahu neplatné.
  Limit 50 % je navíc nižší než pojistné krytí zhotovitele, což je neobhajitelné.
- *Oprava:* Výjimky podle § 2898 OZ. Limit 100 % ceny, případně pojistné plnění, je-li vyšší.
- *v2.0:* čl. 15.3–15.4.

**3. Odstupné ve výši celé zálohy „bez ohledu na okolnosti"**
- *v1.0:* „Při odstoupení objednatele po podpisu propadá záloha na HTK ve prospěch zhotovitele jako odstupné."
- *Útok:* Zhotovitel by zbohatl dvakrát: ponechal by si 100 % ceny HTK a HTK by mu zůstaly k dalšímu
  prodeji. Ujednání je zjevně nepřiměřené, je v rozporu s dobrými mravy a lze ho napadnout podle § 580
  a § 1 odst. 2 OZ. Jeho skutečná funkce je sankční, takže hrozí i posouzení jako smluvní pokuty
  s moderací (§ 2051 OZ).
- *Oprava:* Odstupné je navázané na skutečnou škodu: storno poplatky, rozdíl při prodeji nebo převzetí
  HTK objednatelem, provedené práce a paušál 5 % jen z neprovedené části B. Zhotovitel má povinnost
  zmírnit škodu.
- *v2.0:* čl. 17.1.

**4. Fikce převzetí prostým uplynutím lhůty**
- *v1.0:* „Nepřevezme-li objednatel dílo do 5 dnů od výzvy, považuje se za převzaté."
- *Útok:* Objednatel by přišel o právo odmítnout dílo s podstatnou vadou jen proto, že zmešká krátkou
  lhůtu (dovolená, nemoc). Soud by takovou fikci vykládal restriktivně nebo ji posoudil jako obcházení
  § 2605 a § 2628 OZ. Zhotovitel by se na ni nemohl spolehnout.
- *Oprava:* Dvoustupňová výzva s výslovným upozorněním na následky. Objednateli stačí konkrétně
  uvést podstatné vady. Fikce užíváním platí až po 14 dnech a nevztahuje se na předčasné a nouzové užívání.
- *v2.0:* čl. 12.5.

**5. Záruka podmíněná servisní smlouvou se zhotovitelem**
- *v1.0:* „Záruka platí jen při uzavření servisní smlouvy se zhotovitelem a pravidelném servisu."
- *Útok:* Jde o vázání plnění. Ruší záruku i pro vady, které se servisem nesouvisejí, např. netěsný
  spoj potrubí. Mezi podnikateli to není automaticky neplatné, ale soud by to vyložil proti zhotoviteli
  jako navrhovateli (§ 557 OZ). Pro objednatele je to obchodně nepřijatelné.
- *Oprava:* Servis provádí kdokoli autorizovaný výrobcem. Záruka se vylučuje jen pro vady servisem
  způsobené. Pokud servis vůbec neproběhl, platí vyvratitelná domněnka.
- *v2.0:* čl. 13.2, 13.8.

**6. Smluvní pokuta objednatele bez stropu, zhotovitele se stropem 5 %**
- *v1.0:* objednatel 0,1 % denně bez stropu, zhotovitel 0,02 % denně se stropem 5 %.
- *Útok:* Zjevná asymetrie. Neomezená pokuta 0,1 % denně (36,5 % ročně) vedle zákonného úroku je
  kandidátem na moderaci (§ 2051 OZ). Sankce zhotovitele je naopak tak nízká, že nemotivuje.
- *Oprava:* Symetrická sazba 0,05 % denně se stropy 10 %.
- *v2.0:* čl. 14.1, 14.3.

**7. Obecné vyloučení § 2594 OZ (povinnost upozornit na nevhodné pokyny)**
- *v1.0:* „Zhotovitel neodpovídá za vady způsobené podklady objednatele."
- *Útok:* Zhotovitel je odborník a má kontrolovat podklady s odbornou péčí. Plošné zproštění by
  soud nepřijal pro vady, které byly pro odborníka zjevné. Navíc je v rozporu s tím, že zhotovitel
  sám dělá dodavatelskou dokumentaci.
- *Oprava:* Zhotovitel odpovídá za vady podkladů, které mohl s odbornou péčí zjistit a neupozornil
  na ně. Výhrady jsou v Příloze 3.
- *v2.0:* čl. 1.4, 5.2, 9.5.

### E.2 Nejasnosti, které by se vykládaly proti zhotoviteli

**8. „Funkční kotelna" bez výkonového měřítka**
- *v1.0:* „Kotelna je funkční, pokud jsou TČ v provozu a regulace pracuje."
- *Útok:* Definice nic neříká o tom, k čemu kotelna slouží. Objednatel by tvrdil, že „funkční"
  znamená „vytopí dům", a opřel by se o účel smlouvy (§ 556 OZ). Protože definice nic neříká, vyhraje ten
  výklad, který odpovídá účelu smlouvy, tedy vytápění domu v zimě. To je pro zhotovitele horší než
  jasný výkonový závazek.
- *Oprava:* Jasný a ověřitelný výkonový závazek při provozu 3 TČ (čl. 4.3 písm. b)), přesná definice
  předané a funkční kotelny (čl. 12.2) a výčet zkoušek (čl. 12.1).
- *v2.0:* čl. 4.3, 12.1, 12.2.

**9. Negarance COP a spotřeby bez výhrady vad**
- *v1.0:* „Zhotovitel neodpovídá za spotřebu energie ani COP."
- *Útok:* Takto široce by to vyloučilo odpovědnost i za vadně zapojený výměník nebo chybně nastavenou
  křivku, které spotřebu zvyšují. To je v rozporu s podstatou díla a hrozí posouzení jako vyloučení
  odpovědnosti za vady.
- *Oprava:* Negarance zůstává, ale výslovně nevylučuje odpovědnost za vady, které spotřebu zvyšují.
- *v2.0:* čl. 4.4 poslední věta.

**10. Termín „dle stavební připravenosti" bez mechanismu**
- *v1.0:* „Dílo bude dokončeno v přiměřené lhůtě po zajištění stavební připravenosti."
- *Útok:* „Přiměřená lhůta" je nevymahatelná a neumožňuje sankci ani odstoupení. Chybí definice
  připravenosti a chybí, kdo a jak ji potvrzuje. Zhotovitel by mohl připravenost odmítat donekonečna.
- *Oprava:* Checklist připravenosti (Příloha 5), protokol, fikce potvrzení při nečinnosti zhotovitele,
  pevná Realizační lhůta 10 týdnů, nesankcionovaný Cílový termín s povinností včas varovat.
- *v2.0:* čl. 2.2–2.4, 6.1–6.3.

**11. Prodloužení termínu „při jakékoli překážce"**
- *v1.0:* „Termín se prodlužuje o dobu trvání překážek, které zhotovitel nezpůsobil."
- *Útok:* Do této kategorie by spadalo i prodlení poddodavatelů zhotovitele. Chybí lhůta k uplatnění,
  takže by zhotovitel mohl důvody prodloužení „sbírat" až při vyúčtování pokuty.
- *Oprava:* Uzavřený výčet důvodů, prodloužení jen o skutečný dopad, oznámení do 10 pracovních dnů
  pod sankcí zániku nároku.
- *v2.0:* čl. 6.4, 2.9.

**12. Tichý souhlas s dokumentací**
- *v1.0:* „Nevyjádří-li se objednatel do 5 dnů, platí dokumentace za schválenou."
- *Útok:* Lhůta je krátká a obejde se bez upozornění. Mohla by „schválit" dokumentaci, kterou nikdo
  nečetl. Navíc by tím zhotovitel mohl přenést odpovědnost za vlastní chyby na objednatele.
- *Oprava:* 10 pracovních dnů a poté upozornění s další lhůtou 5 dnů. Schválení nesnímá odpovědnost
  zhotovitele za vady (vyplývá z čl. 4.3 písm. c) a 1.4).
- *v2.0:* čl. 6.1 písm. b).

**13. Chybějící hierarchie dokumentů**
- *v1.0:* bez ustanovení.
- *Útok:* Nabídka zhotovitele, výkresy TV-BDM a rozpočet si mohou odporovat (např. v počtu čerpadel).
  Bez pořadí se rozpor vykládá proti tomu, kdo text navrhl (§ 557 OZ), tedy proti zhotoviteli.
- *Oprava:* Pořadí dokumentů a povinnost oznámit zjištěný rozpor.
- *v2.0:* čl. 20.3.

### E.3 Ustanovení platná, ale pro objednatele obchodně nepřijatelná (riziko, že smlouvu nepodepíše)

**14. Žádné zajištění 100% zálohy**
- *Útok:* Objednatel platí statisíce až miliony předem bez jakékoli jistoty.
- *Oprava:* Vlastnictví HTK, Skladový list, pojištění, volitelná bankovní záruka a lhůta k objednání
  HTK s kopií potvrzení výrobce.
- *v2.0:* čl. 6.1 písm. a), 8.3.

**15. Žádná pozastávka**
- *Útok:* Po zaplacení doplatku zmizí motivace odstraňovat nedodělky z protokolu.
- *Oprava:* Pozastávka 5 %, vázaná jen na nedodělky z protokolu (ne na celou záruku), s automatickým
  uvolněním po 6 měsících a možností nahradit ji bankovní zárukou.
- *v2.0:* čl. 8.4.

**16. Reakční doby „bez zbytečného odkladu"**
- *Útok:* V lednu s nefunkčním topením pro 27 bytů je to nevymahatelné.
- *Oprava:* Tabulka reakčních dob, víkendový nástup v topném období, provizorní zdroj při dlouhé
  poruše a strop prodloužení kvůli náhradním dílům.
- *v2.0:* čl. 13.4.

**17. Prodlení zhotovitele bez práva odstoupit**
- *Útok:* Pokuta má strop 10 % a objednatel pak nemá žádný nástroj. Zhotovitel by mohl „dojet
  strop" a dál stát.
- *Oprava:* Odstoupení při prodlení nad 60 dnů plus dodatečné lhůtě. Vydání HTK a dokumentace.
  Vícenáklady na náhradního zhotovitele v limitu.
- *v2.0:* čl. 14.4, 17.3.

**18. Nepřevoditelnost záruky**
- *v1.0:* „Práva ze smlouvy nelze postoupit bez souhlasu zhotovitele."
- *Útok:* Developer prodá byty a správu převezme SVJ. Záruka by zůstala „viset" u developera, který
  už s domem nemá nic společného.
- *Oprava:* Volné postoupení práv ze záruky na SVJ a nabyvatele s povinností předat záruční podmínky.
- *v2.0:* čl. 13.7.

**19. Bivalence jen jako „možnost dle dohody"**
- *Útok:* Objednatel neví, kolik bude bivalence stát a do kdy se musí rozhodnout. Zhotovitel ji
  později může nacenit libovolně. Hydraulika také nemusí být na dodatečné připojení připravena.
- *Oprava:* Opce s pevnými cenami, pevnou lhůtou a připravenými napojovacími body v ceně.
- *v2.0:* čl. 3.3, 3.5.

**20. Blokace provozu jako zajištění platby**
- *v1.0:* „Při prodlení s platbou může zhotovitel omezit funkce řídicího systému."
- *Útok:* Vzdálené vypnutí vytápění obydleného domu ohrožuje zdraví a majetek. Může založit
  odpovědnost za škodu, odpovědnost za přestupek nebo i trestní odpovědnost a je v rozporu s dobrými
  mravy. Pro zhotovitele je to past.
- *Oprava:* Výslovný zákaz. Zajištění platby řeší pozastávka, pokuta, úrok a fikce převzetí užíváním.
- *v2.0:* čl. 16.1 poslední věta.

**21. Předčasné užívání neřešeno**
- *Útok z obou stran:* Objednatel tvrdí, že užíváním k vysoušení kotelnu nepřevzal. Zhotovitel pak
  nese opotřebení a škody způsobené cizími osobami.
- *Oprava:* Protokol o předčasném užívání a přechod provozních rizik. Záruka za vady zůstává zachována.
- *v2.0:* čl. 11.8.

**22. Skladné od prvního dne a bez stropu**
- *v1.0:* skladné 1 % z ceny HTK měsíčně od podpisu.
- *Útok:* Objednatel už HTK zaplatil a přitom platí skladování i za dobu, kterou potřebuje zhotovitel
  sám (dodací lhůty). 12 % ročně z ceny HTK je nepřiměřené.
- *Oprava:* Skladné až od 1. 1. 2028 jako pevná měsíční částka a možnost převzít HTK kdykoli do vlastního
  skladu.
- *v2.0:* čl. 6.5 písm. a).

**23. Indexace celé ceny bez franšízy**
- *Útok:* Indexovala by se i zaplacená část A a každá drobná změna indexu.
- *Oprava:* Indexace jen neprovedené části B, jen při připravenosti po 30. 9. 2027, s franšízou 3 %,
  oběma směry.
- *v2.0:* čl. 7.6.

### E.4 Body, které jsem v zátěžovém testu zvažoval a **vědomě ponechal** ve prospěch zhotovitele

| Bod | Proč zůstává |
|---|---|
| Záloha 100 % na HTK | Požadavek zadání. Ekonomicky odůvodněné (§ 2611 OZ – zvýšené náklady). Zajištěno čl. 8.3. |
| Doplatek až po předání, ale 90 % části B při zmařených zkouškách | Chrání zhotovitele u novostavby bez odběru tepla. Objednatel má kontrolu přes odložené zkoušky. |
| Pokuta za prodlení jako jediný nárok (čl. 14.4) | Bez tohoto stropu by developer přenášel na zhotovitele sankce vůči kupujícím bytů. Pojistitelnost. |
| Vyloučení nepřímých škod | Standard B2B. Neplatí pro úmysl a hrubou nedbalost. |
| Žádný výkonový závazek při 2 TČ | Technicky nesplnitelný (A.2). Vyrovnává to opce bivalence a transparentnost čl. 4.2. |
| Zákaz zápočtu nesporných pohledávek | Mezi podnikateli přípustné (§ 1987 OZ). Omezeno jen na pohledávky neuznané a nepřiznané. |

---

## F. Modelové situace a jak je smlouva řeší

**1. Stavba se zpozdí o rok; stavební připravenost v listopadu 2027**
Cílový termín se nesplní bez sankce (čl. 6.3). Zhotovitel skladuje HTK. Skladné začne běžet
od 1. 1. 2028 (čl. 6.5), pokud objednatel HTK nepřevezme. Cena montáže se indexuje nad 3 %
(čl. 7.6). Záruka HTK je omezena podle čl. 13.1. Realizační lhůta 10 týdnů začne běžet až
od protokolu. Při zimní montáži se lhůta prodlužuje o dny s mrazy pod −5 °C (čl. 6.4).

**2. Investor po objednání TČ projekt zruší (změna financování)**
Postupuje se podle čl. 17.1 písm. b)–e). Zhotovitel se pokusí stornovat objednávku. Pokud to nejde,
prodá HTK nebo je převezme objednatel. Objednatel hradí storno nebo rozdíl, provedené práce
a 5 % z neprovedené části B. Zbytek zálohy se vrátí do 30 dnů. Zhotovitel neztratí nic, objednatel
nepřeplatí.

**3. Leden, −17 °C, byty mají 19 °C, investor reklamuje výkon**
Nejdřív se zjišťuje, zda běží všechny tři TČ a zda je odběr v mezích PENB. Pokud ano a kotelna
nedosahuje výkonu podle čl. 4.3 písm. b), jde o vadu. Zhotovitel ji odstraní (čl. 13).
Pokud jedna TČ stojí kvůli poruše, jde o provozní vadu s reakční dobou 3 pracovní dny. Nedostatek
výkonu sám o sobě vadou není (čl. 4.2 poslední bod). Pokud porucha trvá déle než 10 dnů a výkon
nestačí, zhotovitel zajistí provizorní zdroj (čl. 13.4). Pokud byla odmítnuta opce bivalence,
nese objednatel riziko extrémních teplot (čl. 3.5, 4.2). Příčinu může posoudit znalec (čl. 19.2).

**4. Po první zimě: „spotřebovali jsme o 30 % víc elektřiny, než jste slibovali"**
Spotřeba ani COP nejsou garantovány a kalkulace byly orientační (čl. 4.4, 20.2). Pokud objednatel
prokáže vadu (např. chybně zapojený výměník nebo nevhodně nastavenou křivku), jde o vadu díla
a zhotovitel ji odstraní. Náhradu vyšších nákladů na energii za minulé období ale vylučuje čl. 15.2,
ledaže jde o hrubou nedbalost.

**5. Kupující si stěžuje, že z kohoutku teče voda 45 °C**
Zhotovitel doloží teplotu na výstupu ze zásobníků a záznamy termické dezinfekce (čl. 4.3 písm. b)).
Teplota u výtoků závisí na rozvodech a cirkulaci objednatele (čl. 4.5, Příloha 8). Pokud je teplota
na výstupu ze zásobníků nižší než podle Přílohy 4, jde o vadu zhotovitele.

**6. KHS nařídí měření hluku po stížnosti sousedů**
Hlukovou studii a protihluková opatření zajišťuje objednatel (čl. 4.6). Zhotovitel odpovídá, jen
pokud je příčinou vadná montáž (chybějící antivibrační prvky) nebo pokud jednotka neodpovídá
akustickým datům.

**7. Porucha TČ2 v prosinci, na víkend**
Jde o provozní vadu, protože TČ3 převezme TUV (režim D). Nástup do 3 pracovních dnů. Pokud by
vypadly dvě TČ, jde o havarijní vadu: vzdálená diagnostika do 4 h, nástup do 24 h i o víkendu,
provizorní obnovení do 48 h (čl. 13.4). Při prodlení hrozí pokuty podle čl. 14.2.

**8. Investor přestane platit, ale v domě už bydlí lidé**
Užívání bez výhrad po 14 dnech znamená převzetí (čl. 12.5 písm. b)). Zhotovitel vyfakturuje doplatek.
Následují úrok, pokuta 0,05 % denně se stropem a soudní vymáhání. Zhotovitel **nesmí** kotelnu
vzdáleně vypnout (čl. 16.1). Pozastávka je jen 5 %, takže expozice je omezená.

**9. Investor odmítá převzetí kvůli chybějícím štítkům a jedné nedotažené izolaci**
Jde o drobné vady (čl. 2.7, 12.4 písm. a), § 2628 OZ). Převzetí nelze odmítnout. Vady se zapíší
do protokolu s lhůtou 30 dnů. Odmítnutí by bylo neoprávněné a po výzvě by nastala fikce převzetí
(čl. 12.5 písm. a)).

**10. Stavbyvedoucí ústně nařídí přeložit rozdělovač o 2 metry**
Bez Změnového listu nárok nevzniká (čl. 9.4). Pokud zhotovitel získá e-mailové potvrzení oprávněné
osoby nebo zápis v deníku, má nárok podle jednotkových cen (čl. 9.4 písm. b)). Doporučení: nic
nedělat bez e-mailu.

**11. Zhotovitel se dostane do úpadku po zaplacení zálohy**
Pokud byl vystaven Skladový list, HTK jsou ve vlastnictví objednatele (čl. 8.3 písm. a)).
Objednatel je vyloučí z majetkové podstaty a nechá dílo dokončit jiným zhotovitelem (čl. 17.3).
Pokud byla vystavena bankovní záruka, objednatel ji čerpá.

**12. Developerská SPV se dostane do úpadku před předáním**
Zhotovitel má uhrazenu část A. Riziko je v předfinancované části B, kterou zhotovitel přihlásí
do insolvence. Proto doporučení G.2 (dílčí fakturace nebo ručení).

**13. Výrobce ukončí výrobu X50 před dodáním**
Použije se náhrada rovnocenným výrobkem se souhlasem objednatele bez navýšení ceny (čl. 9.8).
Pokud jde o celoplošnou nedostupnost doloženou výrobcem, jde o Okolnost vylučující odpovědnost
(čl. 2.9).

**14. Elektrikář objednatele poškodí venkovní jednotku při montáži FVE**
Nebezpečí škody nese objednatel (čl. 11.6). Oprava se provede jako Změna. Zhotovitel musí škodu
ihned zapsat do deníku.

**15. Kotelna běží od října 2027 na vysoušení stavby, předání v březnu 2028**
Na základě protokolu o předčasném užívání (čl. 11.8) nese objednatel energie a provozní riziko.
Po 60 dnech má zhotovitel nárok na placenou preventivní prohlídku. Záruka běží až od převzetí.
Předčasné užívání není převzetím.

**16. Developer prodá dům a správu převezme SVJ**
Práva ze záruky lze postoupit na SVJ bez souhlasu zhotovitele (čl. 13.7). Developer musí SVJ předat
záruční podmínky, jinak odpovídá za jejich porušení z neznalosti.

**17. Investor chce v listopadu 2027 dodatečně bivalentní elektrokotel**
Lhůta opce uplynula, jde o Změnu (čl. 3.5, 9). Napojovací body jsou připraveny v ceně (čl. 3.3),
takže změna je levná a rychlá.

**18. Dům bez odběru tepla v době dokončení (nejsou otopná tělesa)**
Komplexní zkouška proběhne se simulovaným odběrem nebo jako odložená zkouška (čl. 12.6).
Zhotovitel fakturuje 90 % části B. Záruka běží nejpozději 6 měsíců od mechanického dokončení.

**19. Zamrznutí venkovní části primáru při výpadku distribuční sítě**
Pokud protizámrazová ochrana podle dodavatelské dokumentace funguje a výpadek trval déle, než na
co je dimenzována, jde o výluku ze záruky (čl. 13.3). Pokud ochrana nefungovala, jde o vadu
zhotovitele. Zkouška protizámrazové ochrany je součástí předání (čl. 12.1 písm. d)).

**20. Spor o to, zda je výměník poddimenzovaný**
Nezávislý znalec (čl. 19.2) posoudí soulad s čl. 4.3 z výpočtu a datových listů. Náklady nese
ten, jehož stanovisko posudek nepotvrdil.

---

## G. Vyjednávací prostor a doporučení

### G.1 Co můžete v jednání bez velké škody pustit

- Záruční dobu hydrauliky 36 → **60 měsíců**. Montážní práce jsou vaše a riziko je nízké.
- Náklady bankovní záruky za zálohu (čl. 8.3 písm. c)) převzít na sebe.
- Pokutu za prodlení 0,05 % → 0,1 % denně, pokud strop zůstane 10 %.
- Nástup na havarijní vadu do 12 h místo 24 h, pokud máte technika v Ostravě.

### G.2 Co byste neměli pustit

- **čl. 4.2 a 4.3** (výkonové limity a závazek jen při 3 TČ). Bez nich nesete riziko nedostatečného výkonu.
- **čl. 14.4 a 15.2** (pokuta jako jediný nárok, vyloučení nepřímých škod). Jinak přebíráte riziko
  sankcí vůči kupujícím bytů.
- **čl. 12.6** (odložené zkoušky a fakturace 90 %). U novostavby je to vaše hlavní ochrana cash flow.
- **Opce bivalence s pevnou lhůtou.** Nerozhodnutí objednatele nesmí jít k vaší tíži.

### G.3 Doporučení nad rámec smlouvy

1. **Dílčí fakturace části B:** zvažte fakturaci 50 % části B po mechanickém dokončení. Zadání říká
   „zbytek po předání", ale u developerské SPV je to riziko úpadku (F.12). Alternativou je
   ručení mateřské společnosti.
2. **Záruka výrobce:** písemně ověřte u výrobce, od kdy běží záruka a jaké jsou servisní podmínky.
   Přílohu 7 sladit s čl. 13 **před** podpisem.
3. **Ztráta objektu:** 53 kW z PENB není výpočet podle ČSN EN 12831. Než podepíšete čl. 4.3 písm. b),
   nechte ztrátu ověřit, nebo do Přílohy 3 zapište výhradu.
4. **Glykol / voda:** rozhodnout před podpisem (TV-BDM-04, bod 5). Mění cenu i odpovědnost za zamrznutí.
5. **Dokumentace komunikace:** e-mail po každém kontrolním dni se shrnutím pokynů. To je nejlepší
   ochrana nároků podle čl. 9.4.

### G.4 Otevřené body k doplnění (souhrn)

- objednatel, parcelní čísla, povolení,
- ceny části A, B a C, hodinová sazba, skladné,
- teplotní spád otopné soustavy a teplota TUV na výstupu,
- rezervovaný příkon,
- volba soudu,
- volba nákladů bankovní záruky,
- rozhodnutí o glykolu,
- umístění venkovních jednotek.
