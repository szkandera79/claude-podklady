import json,re,time,urllib.request,zipfile,io,csv,os,sys
A="https://ares.gov.cz/ekonomicke-subjekty-v-be/rest"
def post(path,body,tries=4):
    for i in range(tries):
        try:
            req=urllib.request.Request(A+path,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
            return json.load(urllib.request.urlopen(req,timeout=60))
        except urllib.error.HTTPError as e:
            try: return json.load(e)
            except Exception: time.sleep(2+i*3)
        except Exception: time.sleep(2+i*3)
    return {}
FIX={"Chodov":560383,"Kaplice":545562,"Písek":549240,"Louny":565971,"Mělník":534676,"Nejdek":555380,"Náchod":573868,"Napajedla":585513,"Příbram":539911,"Beroun":531057,"Orlová":599069}
def kod_obce(nazev):
    if nazev in FIX: return FIX[nazev]
    d=post("/standardizovane-adresy/vyhledat",{"textovaAdresa":nazev,"typStandardizaceAdresy":"UPLNA_STANDARDIZACE","pocet":5})
    for a in d.get("standardizovaneAdresy",[]):
        if a.get("nazevObce")==nazev: return a["kodObce"]
    return None
PF=["145","205","233"]
def search(sidlo):
    out=[];start=0
    while True:
        d=post("/ekonomicke-subjekty/vyhledat",{"pravniForma":PF,"sidlo":sidlo,"pocet":100,"start":start})
        if "ekonomickeSubjekty" not in d: return None if "příliš mnoho" in d.get("popis","") else out
        out+=d["ekonomickeSubjekty"]; start+=100
        if start>=d.get("pocetCelkem",0): return out
        time.sleep(0.15)
def psc_list(kod):
    fn=f"adr_{kod}.csv"
    if not os.path.exists(fn):
        u=f"https://vdp.cuzk.gov.cz/vymenny_format/csv/20260831_OB_{kod}_ADR.csv.zip"
        z=zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(u,timeout=120).read()))
        open(fn,"wb").write(z.read(z.namelist()[0]))
    rows=list(csv.reader(io.StringIO(open(fn,encoding="cp1250").read()),delimiter=";"))[1:]
    return sorted({r[15] for r in rows if r[15]}), sorted({(r[7],r[8]) for r in rows})
def obec_all(kod):
    r=search({"kodObce":kod})
    if r is not None: return r
    res={}
    pscs,casti=psc_list(kod)
    for p in pscs:
        x=search({"kodObce":kod,"textovaAdresa":p})
        if x is None:
            for kc,nc in casti:
                y=search({"kodObce":kod,"kodCastiObce":int(kc)}) or []
                for s in y:
                    if s.get("ico"): res[s["ico"]]=s
            break
        for s in x:
            if s.get("ico"): res[s["ico"]]=s
        time.sleep(0.1)
    return list(res.values())
if __name__=="__main__":
    targets=json.load(open("targets.json"))
    db=json.load(open("svj_db.json")) if os.path.exists("svj_db.json") else {}
    for obec,info in targets.items():
        if obec in db: continue
        k=kod_obce(obec)
        if not k: print("NENALEZENO",obec); continue
        subs=obec_all(k)
        db[obec]={"kod":k,"info":info,"subs":subs}
        json.dump(db,open("svj_db.json","w"),ensure_ascii=False)
        print(obec,k,len(subs),flush=True)
