import fitz, json, re
d=fitz.open('eru2026.pdf')
COLS=["vyroba>10MW","vyroba<10MW","TV na zdroji","primarni rozvod","CVS","TV na CVS","blokova kotelna","sekundarni rozvod","domovni PS","domovni kotelna"]
rows=[]
for p in d:
    ws=[w for w in p.get_text('words') if w[1]>62]
    krajw=[w for w in ws if 176<=w[0]<=190 and re.fullmatch(r'[A-Z]',w[4])]
    ys=sorted(set(round((w[1]+w[3])/2,1) for w in krajw))
    R={y:{'name':[], 'kraj':None,'bins':{}} for y in ys}
    for w in ws:
        yc=(w[1]+w[3])/2
        if not ys: break
        y=min(ys,key=lambda v:abs(v-yc))
        r=R[y]
        if w[0]<175: r['name'].append((w[1],w[0],w[4]))
        elif w[0]<=190: r['kraj']=w[4]
        elif w[0]>=320:
            b=int((w[0]-322)//25.35)
            r['bins'].setdefault(b,[]).append((w[0],w[4]))
    for y in ys:
        r=R[y]
        name=' '.join(t for _,_,t in sorted(r['name']))
        cols={}
        for b,toks in r['bins'].items():
            v=''.join(t for _,t in sorted(toks)).replace(',','.')
            try: v=float(v)
            except: continue
            ci=b//2
            if ci>=10: continue
            cols.setdefault(COLS[ci],{})['price' if b%2==0 else 'qty']=v
        rows.append(dict(name=name,kraj=r['kraj'],cols=cols))
json.dump(rows,open('eru2026.json','w'),ensure_ascii=False)
print(len(rows))
for r in rows[:12]: print(r)
