import json, re, sys
base = r"~\Documents\tax-formalization-data\taxcourt\validation\holdout"
ids = ["tcmemo-2026-25", "tcsumm-2023-11", "tcsumm-2022-19", "tcsumm-2021-13"]
extra = {
    "tcmemo-2026-25": ["5,454", "22,782", "85%"],
    "tcsumm-2023-11": ["6,874", "7,104", "1,420", "113,721", "81,680", "20,420", "6,875"],
    "tcsumm-2022-19": ["17,652", "17,288", "636", "119,82", "121,917", "94,970", "4,311", "1,001", "11,885", "2,097", "80,640"],
    "tcsumm-2021-13": ["1,275", "327", "1,602", "37,538", "20,192", "7,620", "887.59", "1,428", "316", "303.12", "9.69", "11,880"],
}
phrases = ["we hold", "court holds", "is entitled", "is not entitled", "not entitled", "is liable", "sustain", "decision will be entered",
           "ineligible", "not eligible", "does not qualify", "must repay", "owes"]
for i in ids:
    txt = open(f"{base}\\redacted\\{i}.txt", encoding="utf-8").read()
    key = json.load(open(f"{base}\\keys\\{i}.key.json", encoding="utf-8"))
    json.load(open(f"{base}\\redacted\\{i}.redactions.json", encoding="utf-8"))
    pats = list(extra[i])
    for e in key["expected"]:
        if "value" in e and e["value"] not in (0,):
            v = e["value"]
            pats += [f"{v:,}", str(v)]
    low = txt.lower()
    for p in pats:
        if p in txt or p.replace(",", "") in txt:
            print(i, "FIGURE", p)
    for p in phrases:
        if p in low:
            for m in re.finditer(re.escape(p), low):
                print(i, "PHRASE", p, "::", txt[max(0, m.start()-60):m.end()+40].replace("\n", " "))
    # snippet check against raw
    raw = open(f"{base}\\raw\\{i}.txt", encoding="utf-8").read()
    norm = lambda s: re.sub(r"\s+", " ", s.replace("\u2019", "'").replace("\u2014", "-"))
    rn = norm(raw)
    for e in key["expected"]:
        s = norm(e["snippet"])
        if s not in rn:
            print(i, "SNIPPET-NOT-FOUND", e["item"], s[:60])
        if len(e["snippet"].split()) > 25:
            print(i, "SNIPPET-LONG", e["item"])
print("done")
