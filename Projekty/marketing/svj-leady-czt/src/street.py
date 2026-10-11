import json,re,time
from svj import post,kod_obce
rows=json.load(open('eru2026.json'))
out=[];kody={}
for r in rows:
    c=r['cols']
    ends=[v for k,v in c.items() if k in ('domovni PS','sekundarni rozvod','domovni kotelna','blokova kotelna') and v.get('price')]
    if not ends: continue
    p=max(v['price'] for v in ends)
    if p<1100: continue
    m=re.match(r'^(.+?)\s+-\s+(.+?)\s+(\d+)(?:/\d+)?[a-z]?(?:[,;].*)?$',r['name'])
    if not m: continue
    obec,ulice,cp=m.group(1).strip(),m.group(2).strip(),m.group(3)
    obec=re.sub(r'\s+\d+$','',obec)  # "Praha 5" -> Praha
    if obec.startswith('Praha'): obec='Praha'
    if obec not in kody: kody[obec]=kod_obce(obec)
    k=kody[obec]
    if not k: continue
    d=post("/ekonomicke-subjekty/vyhledat",{"pravniForma":["145","205","233"],"sidlo":{"kodObce":k,"textovaAdresa":f"{ulice} {cp}"},"pocet":20})
    for s in d.get("ekonomickeSubjekty",[]) or []:
        if s.get('ico') and str(s['sidlo'].get('cisloDomovni'))==cp:
            out.append({"lok":r['name'],"cena":round(p,2),"subj":s})
    time.sleep(0.15)
json.dump(out,open('street_hits.json','w'),ensure_ascii=False)
print(len(out)); [print(o['lok'],o['cena'],o['subj']['obchodniJmeno']) for o in out]
