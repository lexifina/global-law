import json, sys, re
base = sys.argv[1]
phr = ["we hold","is entitled","is not entitled","is liable","sustain","decision will be entered","we conclude","conceded","not subject","qualified for","deemed"]
for i in sys.argv[2:]:
    t = open(f"{base}/redacted/{i}.txt", encoding="utf-8").read()
    k = json.load(open(f"{base}/keys/{i}.key.json", encoding="utf-8"))
    json.load(open(f"{base}/redacted/{i}.redactions.json", encoding="utf-8"))
    print("==", i)
    for e in k["expected"]:
        v = e.get("value")
        if isinstance(v, int) and v > 0:
            for s in {str(v), f"{v:,}", str(round(v, -1)), f"{v/1000:.1f}"}:
                if s in t: print("  FIGURE", e["item"], s)
    for p in phr:
        for m in re.finditer(p, t, re.I):
            print("  PHRASE", p, "|", t[max(0,m.start()-60):m.end()+40].replace("\n"," "))
