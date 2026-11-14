import json, re, sys
base = "~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/recog"
banned = ["not overrul","n't overrul","never overrul","not been overrul","never been overrul","not abrogat","n't abrogat","not been abrogat","not disapprov","whether","without overruling","rather than overrul","declin","refus","would overrule","should be overruled","should overrule","to overrule","contend","dissent","question","doubt","argues","argued","arguing","argument","urges","urged","urging"]
for pack in ["T1f_046", "T1f_047"]:
    text = open(f"{base}/packs/pack_{pack}.md", encoding="utf-8").read()
    ids = re.findall(r"^### ITEM (\S+)", text, re.M)
    windows = {}
    blocks = re.split(r"^### ITEM ", text, flags=re.M)[1:]
    for b in blocks:
        iid = b.split("\n", 1)[0].strip()
        m = re.search(r"^WINDOW:\n(.*?)\n^NOTE AT:", b, re.M | re.S)
        windows[iid] = m.group(1) if m else ""
    rows = [json.loads(l) for l in open(f"{base}/ans_prescreen/ans_pack_{pack}.jsonl", encoding="utf-8")]
    ok_order = [r["id"] for r in rows] == ids
    n_true = 0
    problems = []
    for r in rows:
        if r["states"] is True:
            n_true += 1
            q = r["quote"]
            w = windows[r["id"]]
            if q not in w: problems.append((r["id"], "not substring"))
            if len(q) > 400: problems.append((r["id"], "too long", len(q)))
            low = q.lower()
            for bs in banned:
                if bs in low: problems.append((r["id"], "banned", bs))
            if not re.search(r"overrul|abrogat|disapprov|reced", q): problems.append((r["id"], "no overruling word"))
    print(pack, "items", len(ids), "answers", len(rows), "order_ok", ok_order, "true", n_true, "problems", problems)
