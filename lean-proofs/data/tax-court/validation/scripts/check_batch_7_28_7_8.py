import json, re, sys
base = r"~\Documents\tax-formalization-data\taxcourt\validation\holdout"
ids = ["tcsumm-2022-7","tcsumm-2019-28","tcsumm-2021-7","tcsumm-2025-8"]
def norm(s): return re.sub(r"\s+"," ",s.replace("\u2019","'").replace("\u201c",'"').replace("\u201d",'"')).strip()
phr = ["we hold","is entitled","is not entitled","not entitled","is liable","liable","sustain","conclude","Decision will be entered","Rule 155","we find","qualif"]
for i in ids:
    raw = open(base+"/raw/"+i+".txt",encoding="utf-8").read()
    red = open(base+"/redacted/"+i+".txt",encoding="utf-8").read()
    json.load(open(base+"/redacted/"+i+".redactions.json",encoding="utf-8"))
    k = json.load(open(base+"/keys/"+i+".key.json",encoding="utf-8"))
    rawn = norm(raw)
    print("==",i)
    for e in k["expected"]:
        s = e["snippet"]
        ok = norm(s) in rawn
        pg = re.split(r"=== \[page (\d+)\] ===", raw)
        pages = {int(pg[j]):norm(pg[j+1]) for j in range(1,len(pg),2)}
        onpage = norm(s) in pages.get(e["page"],"") or (norm(s) in norm(pages.get(e["page"],"")+" "+pages.get(e["page"]+1,"")))
        print(" ", e["item"], "verbatim" if ok else "NOT-VERBATIM", "page-ok" if onpage else "PAGE?", len(s.split()),"words")
        if "value" in e:
            v = e["value"]
            if v:
                for f in {str(v), f"{v:,}"}:
                    for m in re.finditer(re.escape(f), red):
                        print("   LEAK", f, red[max(0,m.start()-40):m.end()+20].replace("\n"," "))
    for p in phr:
        for m in re.finditer(p, red, re.I):
            print("   phrase", p, "|", red[max(0,m.start()-50):m.end()+30].replace("\n"," "))
    for f in ["15,786","15786","3,157","3157","3,090","3090","618","494","5,348","5348","1,070","1070","5,124","5124","906","16,140","16140","13,960","13960"]:
        if f in red: print("   NUM", f)
