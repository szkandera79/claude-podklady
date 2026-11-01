"""Přeznačení technických výkresů nádrží na REO HEATING.

Z PDF výkresů dodavatele (Wok/AKU nádoby výkresy) odstraní všechny texty kromě kót,
čínštinu nahradí češtinou, anglické popisky opraví a zbaví zmínek o výrobci,
do razítka vloží logo REO HEATING a modelové značení z katalogu (REO AN/ZV/KN).

Spuštění z kořene repozitáře Projekty:
    python3 REO/REO-letak-nadrze/vykresy/build_vykresy.py
"""
import glob, os, re, sys
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, 'Wok', 'AKU nádoby výkresy')
OUT = os.path.join(HERE, 'pdf')
LOGO = os.path.join(ROOT, 'REO', 'logo', 'logo-reo-heating.png')
FONT = '/System/Library/Fonts/Supplemental/Arial Narrow.ttf'
FONT_B = '/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf'

# číslo výkresu dodavatele → údaje REO
TANKS = {
    '5189-10311': dict(model='REO AN-100', title='Akumulační nádrž', sub='100 l', D=470, d=370, foams=2),
    '5189-20312': dict(model='REO AN-200', title='Akumulační nádrž', sub='200 l', D=520, d=420, foams=2),
    '5189-30260': dict(model='REO AN-300', title='Akumulační nádrž', sub='300 l', D=560, d=460, foams=3),
    '5186-20136': dict(model='REO ZV-200', title='Zásobník teplé vody', sub='s vlnitým výměníkem · 200 l',
                       D=520, d=420, foams=2, hx=('28', '20', '2,6', '2.6')),
    '5186-30159': dict(model='REO ZV-300', title='Zásobník teplé vody', sub='s vlnitým výměníkem · 300 l',
                       D=560, d=460, foams=3, hx=('28', '40', '5,3', '5.3')),
    '5186-30158': dict(model='REO KN-300', title='Kombinovaná nádrž 2 v 1', sub='300 l (70 + 210 l)',
                       D=560, d=470, foams=3, hx=('28', '20', '2,6', '2.6')),
    '5186-50140': dict(model='REO KN-500', title='Kombinovaná nádrž 2 v 1', sub='500 l (120 + 330 l)',
                       D=700, d=600, foams=3, hx=('25', '30', '4', '4')),
}

def remarks_cs(t):
    r = ['Technické požadavky',
         f'1. Vnější průměr nádrže: Ø{t["D"]} mm.',
         f'2. Vnitřní průměr nádoby: Ø{t["d"]} mm.',
         '3. Izolace: PUR pěna, tloušťka 50 mm.',
         '4. Tolerance výšky pláště ±10 mm, tolerance výšky hrdel ±3 mm.',
         '5. Povrch nádrže hladký a čistý, bez promáčklin a vyboulenin.',
         '6. Tlaková zkouška vnitřní nádoby 0,8–1,0 MPa po dobu 3 minut: bez netěsnosti, poklesu tlaku a deformace.',
         '7. Jímky čidel teploty s bílou kabelovou průchodkou PG7.',
         f'8. Balení: horní, spodní a {t["foams"]} mezilehlé polystyrenové výplně, kartonová krabice s logem REO HEATING.']
    if 'hx' in t:
        dia, ln, a, _ = t['hx']
        r.append(f'9. Výměník: vlnitá nerezová trubka Ø{dia} mm × {ln} m, teplosměnná plocha {a} m².')
    return r

def remarks_en(t):
    r = ['Technical remarks',
         f'1. Outer tank diameter: Ø{t["D"]} mm.',
         f'2. Inner tank diameter: Ø{t["d"]} mm.',
         '3. Insulation: polyurethane foam, 50 mm.',
         '4. Tolerance of cylinder height ±10 mm, tolerance of nozzle heights ±3 mm.',
         '5. Tank surface smooth and clean, without dents or bulges.',
         '6. Inner tank pressure test 0.8–1.0 MPa for 3 minutes: no leakage, no pressure drop, no deformation.',
         '7. White PG7 cable glands on temperature sensor pockets.',
         f'8. Packaging: top, bottom and {t["foams"]} intermediate styrofoam protectors, carton box with REO HEATING logo.']
    if 'hx' in t:
        dia, ln, _, a = t['hx']
        r.append(f'9. Heat exchanger: corrugated stainless pipe Ø{dia} mm × {ln} m, exchange area {a} m².')
    return r

LABELS_CS = ['Značení nádrže', '1. Logo REO HEATING', '2. Štítky hrdel dle výkresu',
             '3. Typový štítek', '4. Označení CE: ano', '5. Čárový kód']
LABELS_EN = ['Labels on the tank:', '1. REO HEATING logo', '2. Nozzle labels according to the drawing',
             '3. Rating plate according to specification', '4. CE marking: yes', '5. Barcode']

# čínské popisky hrdel → čeština (klíč bez mezer a se sjednocenými závorkami)
CS = {
    '排气口(4分内牙)': 'Odvzdušnění (Rp 1/2")',
    '排气口(4分外牙)': 'Odvzdušnění (G 1/2" vnější)',
    'PT阀(6分内牙)': 'Pojistný ventil P/T (Rp 3/4")',
    '热水出口(6分内牙)': 'Výstup teplé vody (Rp 3/4")',
    '镁棒(6分内牙)': 'Hořčíková anoda (Rp 3/4")',
    '保温层': 'Izolace',
    '温控器': 'Termostat',
    '电加热(1寸内牙)': 'El. topné těleso 3 kW (Rp 1")',
    '回水口(6分内牙)': 'Cirkulace TV (Rp 3/4")',
    '冷水进口(6分外牙)': 'Vstup studené vody (G 3/4" vnější)',
    '加单向安全阀(黑色手柄)': '+ pojistný ventil (černá páčka)',
    '排污口(4分外牙)': 'Vypouštění (G 1/2" vnější)',
    '感温口': 'Jímka čidla teploty',
    '盘管循环进口(1寸外牙)': 'Vstup do výměníku (G 1" vnější)',
    '盘管循环出口(1寸外牙)': 'Výstup z výměníku (G 1" vnější)',
    '循环进口(1寸内牙)': 'Vstup topné vody (Rp 1")',
    '循环出口(1寸内牙)': 'Výstup topné vody (Rp 1")',
    '循环进口(1.2寸内牙)': 'Vstup topné vody (Rp 1 1/4")',
    '循环出口(1.2寸内牙)': 'Výstup topné vody (Rp 1 1/4")',
    '循环进口(1.5寸内牙)': 'Vstup topné vody (Rp 1 1/2")',
    '循环出口(1.5寸内牙)': 'Výstup topné vody (Rp 1 1/2")',
    '补水口(1/2-M)': 'Doplňování (G 1/2" vnější)',
    '补水口(4分外牙)': 'Doplňování (G 1/2" vnější)',
    '固定支架': 'Konzola',
    '底脚': 'Nožka',
    '底座': 'Podstavec',
    '20MΦ28波纹管': 'Vlnitý výměník Ø28 × 20 m',
    '30MΦ28波纹管': 'Vlnitý výměník Ø25 × 30 m',   # v podkladu rozpor, poznámka 9 uvádí Ø25
    '40MΦ28波纹管': 'Vlnitý výměník Ø28 × 40 m',
    '版本': 'Verze', '页面': 'Formát', '比例': 'Měřítko', '日期': 'Datum',
}

# opravy anglických popisků (překlepy podkladu)
EN_FIX = {
    'Hot warter outlet(Rp 3/4)': 'Hot water outlet (Rp 3/4)',
    'water ruturn(Rp 3/4)': 'Water return (Rp 3/4)',
    'water return(Rp 3/4)': 'Water return (Rp 3/4)',
    'Add one-way safety valve(Blackhandle)': '+ one-way safety valve (black handle)',
    'Exhaust port(Rp 1/2)': 'Air vent (Rp 1/2)',
    'Exhaust port(1/2-M)': 'Air vent (1/2-M)',
    'Temp Sensor': 'Temp. sensor',
    'thermostat': 'Thermostat',
    'electric heater(Rp 1")': 'Electric heater 3 kW (Rp 1")',
    '30MΦ28 wave pipe': '30MΦ25 wave pipe',
}

KEEP = re.compile(r'[\d\s.,:/φΦØ+\-]*|SUS304|A4')
CJK = re.compile(r'[　-鿿＀-￯]')

def norm(t):
    t = t.replace('（', '(').replace('）', ')').replace(' ', '')
    return t

class Writer:
    def __init__(self, page):
        self.page = page
        self.D = page.derotation_matrix
        self.rot = page.rotation   # rotate pro vodorovný text v zobrazení
        self.f = fitz.Font(fontfile=FONT)
        self.fb = fitz.Font(fontfile=FONT_B)

    def w(self, text, size, bold=False):
        return (self.fb if bold else self.f).text_length(text, size)

    def put(self, x, y, text, size, color=(0, 0, 0), bold=False, maxw=None, align='l', rotate=0):
        if maxw and self.w(text, size, bold) > maxw:
            size = size * maxw / self.w(text, size, bold)
        tw = self.w(text, size, bold)
        if align == 'c': x -= tw / 2
        elif align == 'r': x -= tw
        self.page.insert_text(fitz.Point(x, y) * self.D, text, fontsize=size, color=color,
                              rotate=(self.rot + rotate) % 360,
                              fontname='ANB' if bold else 'AN', fontfile=FONT_B if bold else FONT)
        return size

    def para(self, lines, x, y, size, lead, maxw, first_bold=True, dry=False):
        """Zalomí řádky do šířky maxw, vrátí y za posledním řádkem."""
        for i, ln in enumerate(lines):
            bold = first_bold and i == 0
            words, cur, indent = ln.split(' '), '', ''
            m = re.match(r'(\d+\. )', ln)
            out = []
            for wd in words:
                t = (cur + ' ' + wd).strip() if cur else wd
                if self.w(indent + t, size, bold) > maxw and cur:
                    out.append(indent + cur); cur = wd
                    indent = ' ' * 4 if m else ''
                else:
                    cur = t
            out.append(indent + cur)
            for o in out:
                if dry:
                    y += lead; continue
                self.page.insert_text(fitz.Point(x, y) * self.D, o, fontsize=size, rotate=self.rot,
                                      fontname='ANB' if bold else 'AN',
                                      fontfile=FONT_B if bold else FONT)
                y += lead
        return y


def build(path):
    num = re.search(r'(518\d-\d{5})', os.path.basename(path)).group(1)
    t = TANKS[num]
    drawno = t['model'].replace(' ', '-').replace('REO-', 'REO-') + '-01'
    src = fitz.open(path)
    sp = src[0]
    M = sp.rotation_matrix
    spans = []
    for b in sp.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                if not s['text'].strip():
                    continue
                r = fitz.Rect(s['bbox']) * M
                o = fitz.Point(s['origin']) * M
                spans.append(dict(t=s['text'], r=r, o=o, size=s['size'], color=s['color'], raw=fitz.Rect(s['bbox'])))
    # 1) odstranit všechny texty kromě kót
    repl = [s for s in spans if not KEEP.fullmatch(s['t'].strip())
            or s['t'].strip() == num or re.fullmatch(r'20\d\d/\d+/\d+', s['t'].strip())]
    for s in repl:
        sp.add_redact_annot(s['raw'] + (0.3, 0.3, -0.3, -0.3), fill=None)
    sp.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                        text=fitz.PDF_REDACT_TEXT_REMOVE)
    # 2) psát do původní (otočené) stránky v souřadnicích zobrazení
    pg = sp
    out = src
    W = Writer(pg)

    def find(txt, starts=False):
        for s in spans:
            if (s['t'].strip().startswith(txt) if starts else s['t'].strip() == txt):
                return s
    done = set()

    # razítko
    tb_model = find('Model'); tb_out = find('Out Material'); tb_ins = find('Insulation')
    tb_inn = find('Inner Material'); tb_dno = find('Drawing No.')
    if tb_out is None:  # KN-300: v podkladu omylem „Support foot“ místo „Out Material“
        tb_out = next((x for x in spans if x['t'].strip() == 'Support foot' and x['size'] > 11), None)
    if tb_out is None:  # popis chybí – dopočítat z řádku Insulation
        dy = tb_inn['o'].y - tb_ins['o'].y
        tb_out = dict(t='', r=tb_ins['r'] + (0, -dy, 0, -dy), o=tb_ins['o'] - (0, dy), size=tb_ins['size'])
    firm = find('Foshan', True)
    title = [s for s in spans if s['size'] > 15 and s['r'].x0 > tb_model['r'].x0 - 60 and s['r'].y1 < tb_model['r'].y0]
    title.sort(key=lambda s: s['r'].y0)
    big = [s for s in spans if s['t'].strip() == num and s['size'] > 15][0]
    val_model = [s for s in spans if s['r'].y0 > tb_model['r'].y0 - 3 and s['r'].y1 < tb_model['r'].y1 + 3
                 and s['r'].x0 > tb_model['r'].x1 + 20][0]
    val_dno = [s for s in spans if s['t'].strip() == num and s is not big][0]
    val_out = find('White Paint steel'); val_ins = find('polyurethane')
    date = [s for s in spans if re.fullmatch(r'20\d\d/\d+/\d+', s['t'].strip())][0]
    for s in title + [tb_model, tb_out, tb_ins, tb_inn, tb_dno, firm, big, val_model, val_dno, val_out, val_ins, date]:
        done.add(id(s))

    cellL = tb_out['r'].x0  # levý okraj sloupce popisů
    W.put(tb_out['r'].x0, tb_out['o'].y, 'Plášť', tb_out['size'], maxw=val_out['r'].x0 - cellL - 6)
    W.put(tb_ins['r'].x0, tb_ins['o'].y, 'Izolace', tb_ins['size'])
    W.put(tb_inn['r'].x0, tb_inn['o'].y, 'Vnitřní nádoba', tb_inn['size'], maxw=val_out['r'].x0 - cellL - 6)
    valw = title[0]['r'].x0 - val_out['r'].x0 - 20
    W.put(val_out['r'].x0, val_ins['o'].y - (val_ins['o'].y - val_out['o'].y), 'Bílý lakovaný plech', val_out['size'] * 1.1, maxw=valw)
    W.put(val_ins['r'].x0, val_ins['o'].y, 'PUR pěna 50 mm', val_ins['size'], maxw=valw)
    W.put(tb_model['r'].x0, tb_model['o'].y, 'Model', tb_model['size'])
    mx = tb_model['r'].x1 + 27
    W.put(mx, val_model['o'].y, t['model'], 13, bold=True, maxw=sp.rect.width - 20 - mx)
    W.put(tb_dno['r'].x0, tb_dno['o'].y, 'Č. výkresu', tb_dno['size'])
    dx = val_dno['r'].x0 - 12
    W.put(dx, val_dno['o'].y, drawno, val_dno['size'], maxw=title[0]['r'].x0 - dx - 8)
    W.put(date['r'].x0, date['o'].y, '2026/11/01', date['size'], maxw=date['r'].width + 2)
    # titulek
    tx = title[0]['r'].x0
    y1, y2 = (title[0]['o'].y, title[-1]['o'].y) if len(title) > 1 else (title[0]['o'].y - 11, title[0]['o'].y + 12)
    W.put(tx, y1, t['title'], 19, bold=True, maxw=sp.rect.width - 22 - tx)
    W.put(tx, y2, t['sub'], 15, maxw=sp.rect.width - 22 - tx)
    # logo místo názvu výrobce
    fr = firm['r']
    cell = fitz.Rect(tb_model['r'].x0 - 6, date['r'].y0 - 14, sp.rect.width - 18, date['r'].y1 + 28)
    lh = 30
    lw = lh * 2889 / 1102
    lr = fitz.Rect(cell.x1 - lw - 8, fr.y0 + fr.height / 2 - lh / 2, cell.x1 - 8, fr.y0 + fr.height / 2 + lh / 2)
    pg.insert_image(lr * W.D, filename=LOGO, rotate=W.rot)
    # velké číslo výkresu (vzhůru nohama, jako originál)
    br = big['r']
    sz = big['size'] * 0.9
    ww = W.w(drawno, sz)
    W.put((br.x0 + br.x1) / 2 + ww / 2, br.y0 + sz * 0.25, drawno, sz, rotate=180)

    # technické požadavky
    tr = find('Technical Remark'); cn = find('技术要求')
    en_lines = [s for s in spans if s['r'].y0 >= tr['r'].y0 - 2 and tr['r'].x0 - 3 <= s['r'].x0 < cn['r'].x0 - 5]
    cn_lines = [s for s in spans if s['r'].y0 >= cn['r'].y0 - 2 and cn['r'].x0 - 3 <= s['r'].x0 < cellL - 5
                and s['r'].y0 < tb_model['r'].y1 + 200]
    lead_en = sorted(en_lines, key=lambda s: s['o'].y)
    lead = (lead_en[-1]['o'].y - lead_en[0]['o'].y) / max(1, len(lead_en) - 1)
    for s in en_lines + cn_lines: done.add(id(s))
    sz = tr['size']
    W.para(remarks_en(t), tr['r'].x0, tr['o'].y, sz, lead, cn['r'].x0 - tr['r'].x0 - 12)
    cn_right = max(s['r'].x1 for s in cn_lines)
    bottom = max(s['r'].y1 for s in en_lines) + 2
    k = 1.0
    while W.para(remarks_cs(t), cn['r'].x0, cn['o'].y, sz * k, lead * k, cn_right - cn['r'].x0 + 4, dry=True) - lead * k > bottom and k > 0.7:
        k -= 0.03
    W.para(remarks_cs(t), cn['r'].x0, cn['o'].y, sz * k, lead * k, cn_right - cn['r'].x0 + 4)

    # blok značení
    lb_cn = find('水箱标签'); lb_en = find('Label on the water tank:')
    blk = [s for s in spans if lb_cn['r'].y0 - 3 <= s['r'].y0 <= lb_cn['r'].y0 + 120 and s['r'].x0 >= lb_cn['r'].x0 - 3
           and s['size'] < 10.5]
    for s in blk: done.add(id(s))
    cn_rows = sorted([s for s in blk if s['r'].x0 < lb_en['r'].x0 - 5], key=lambda s: s['o'].y)
    en_rows = sorted([s for s in blk if s['r'].x0 >= lb_en['r'].x0 - 5], key=lambda s: s['o'].y)
    for i, txt in enumerate(LABELS_CS):
        W.put(lb_cn['r'].x0, cn_rows[i]['o'].y, txt, lb_cn['size'], maxw=lb_en['r'].x0 - lb_cn['r'].x0 - 10)
    for i, txt in enumerate(LABELS_EN):
        W.put(lb_en['r'].x0, en_rows[i]['o'].y, txt, lb_en['size'])

    # popisky hrdel
    for s in spans:
        if id(s) in done or KEEP.fullmatch(s['t'].strip()):
            continue
        txt = s['t']
        if CJK.search(txt):
            cs = CS.get(norm(txt))
            if not cs:
                print('  !! bez překladu:', repr(txt)); continue
            # šířka: popisek nad ním (anglický) nebo vlastní
            pair = [e for e in spans if not CJK.search(e['t']) and 0 < s['r'].y0 - e['r'].y0 < 2.2 * s['size']
                    and e['r'].x0 < s['r'].x1 and e['r'].x1 > s['r'].x0]
            maxw = max([s['r'].width] + [e['r'].width for e in pair]) + 24
            size = min(s['size'] * 0.92, max(8.0, s['size'] * 0.92 * maxw / W.w(cs, s['size'] * 0.92)))
            cx = (s['r'].x0 + s['r'].x1) / 2
            W.put(cx, s['o'].y, cs, size, align='c')
        else:
            en = EN_FIX.get(txt.strip(), txt.strip())
            en = re.sub(r'(\w)\(', r'\1 (', en)
            W.put(s['r'].x0, s['o'].y, en, s['size'] * 0.95, maxw=max(s['r'].width + 12, W.w(en, s['size'] * 0.8)))
    name = f"{t['model'].replace(' ', '_')}_technicky_vykres.pdf"
    out.set_metadata({'title': f"{t['model']} – technický výkres", 'author': 'REO HEATING', 'creator': 'REO HEATING',
                      'producer': 'REO HEATING', 'subject': t['title'],
                      'creationDate': fitz.get_pdf_now(), 'modDate': fitz.get_pdf_now()})
    out.del_xml_metadata()
    out.save(os.path.join(OUT, name), garbage=4, deflate=True)
    return name, t


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(SRC, '*.pdf'))):
        print(os.path.basename(f)[:40], '→', build(f)[0])
