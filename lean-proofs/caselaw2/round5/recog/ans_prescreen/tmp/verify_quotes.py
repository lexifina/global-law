import json, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
pack = sys.argv[1]  # e.g. T1f_042
PACK = BASE + r"\packs\pack_" + pack + ".md"
ANS = BASE + r"\ans_prescreen\ans_pack_" + pack + ".jsonl"

BANNED = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "contend",
          "dissent", "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]

text = open(PACK, encoding="utf-8").read()
blocks = re.split(r"^### ITEM ", text, flags=re.M)[1:]
windows = {}
for b in blocks:
    iid = b.split("\n", 1)[0].strip()
    m = re.search(r"^WINDOW:\n(.*?)\n^NOTE AT:", b, flags=re.M | re.S)
    windows[iid] = m.group(1) if m else None
    # names X and Y
    xm = re.search(r"^X \(the earlier decision\): (.*)$", b, flags=re.M)
    ym = re.search(r"^Y \(the decision said to have done it\): (.*)$", b, flags=re.M)
    windows[iid + "#X"] = xm.group(1) if xm else ""
    windows[iid + "#Y"] = ym.group(1) if ym else ""

rows = [json.loads(l) for l in open(ANS, encoding="utf-8")]
ids = re.findall(r"^### ITEM (\S+)", text, flags=re.M)
assert [r["id"] for r in rows] == ids, "order/coverage mismatch"
assert len(rows) == len(set(r["id"] for r in rows))
problems = 0
ntrue = 0
for r in rows:
    if not r["states"]:
        continue
    ntrue += 1
    q = r["quote"]
    w = windows[r["id"]]
    issues = []
    if w is None:
        issues.append("no window")
    else:
        if q not in w:
            issues.append("quote not substring of window")
        if len(q) > 400:
            issues.append("quote too long %d" % len(q))
        if not re.search(r"overrul|abrogat|disapprov|reced", q):
            issues.append("no overruling word")
        for label in ("#X", "#Y"):
            name = windows[r["id"] + label]
            # distinctive first party name
            first = re.split(r",| v\. ", name)[0].strip()
            if first and first.split(" ")[-1] not in q and first not in q:
                # check citation fallback
                cit = re.search(r"(\d+ (U\. ?S\.|U\.S\.|F\.\s?\d*d|S\. ?Ct\.)[^;]*)", name)
                if not (cit and cit.group(1).split(" (")[0] in q):
                    issues.append("name %s (%s) not in quote" % (label, first))
        for bad in BANNED:
            if bad in q:
                issues.append("banned: " + bad)
    if issues:
        problems += 1
        print(r["id"], issues)
print("rows", len(rows), "true", ntrue, "problem rows", problems)
