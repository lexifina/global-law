import json, re, sys
base = r"C:\Users\alany\Documents\tax-formalization-data\taxcourt\validation\holdout"
ids = sys.argv[1:]
def norm(s):
    s = s.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s).strip()
for i in ids:
    raw = open(f"{base}/raw/{i}.txt", encoding="utf-8").read()
    # page-attributed text
    pages = re.split(r"=== \[page (\d+)\] ===", raw)
    pg = {}
    for k in range(1, len(pages), 2):
        pg[int(pages[k])] = pages[k+1]
    full = norm(re.sub(r"=== \[page \d+\] ===", " ", raw))
    full2 = norm(re.sub(r"(=== \[page \d+\] ===)|(-\s*\d+\s*-)|(\[\*\d+\])", " ", raw))
    key = json.load(open(f"{base}//keys/{i}.key.json", encoding="utf-8"))
    red = open(f"{base}/redacted/{i}.txt", encoding="utf-8").read()
    json.load(open(f"{base}/redacted/{i}.redactions.json", encoding="utf-8"))
    print("==", i)
    for e in key["expected"]:
        sn = norm(e["snippet"])
        n = len(sn.split())
        ok = sn in full or sn in full2
        onpage = sn[:40] in norm(pg.get(e["page"], ""))
        if n > 25 or not ok or not onpage:
            print("  SNIPPET", e["item"], e.get("year"), "words", n, "found", ok, "onpage", onpage)
        if "value" in e:
            v = e["value"]
            if v:
                for form in {str(v), f"{v:,}"}:
                    if form in red: print("  LEAK value", form)
    for ph in ["we hold","is entitled","is not entitled","is liable","not liable","sustain","Decision will be entered","Held","qualifying child of","not a qualifying"]:
        for m in re.finditer(re.escape(ph), red, re.I):
            print("  PHRASE", ph, "::", red[max(0,m.start()-60):m.end()+40].replace("\n"," "))
