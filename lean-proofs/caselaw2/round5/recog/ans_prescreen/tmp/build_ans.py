import json
import os
import sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
pack = sys.argv[1]  # e.g. T1f_037
pack_path = os.path.join(BASE, "packs", "pack_%s.md" % pack)
ans_path = os.path.join(BASE, "ans_prescreen", "ans_pack_%s.jsonl" % pack)
json_path = os.path.join(BASE, "ans_prescreen", "tmp", "answers_%s.json" % pack)

with open(pack_path, encoding="utf-8") as f:
    lines = f.read().split("\n")

items = []
cur = None
mode = None
for ln in lines:
    if ln.startswith("### ITEM "):
        cur = {"id": ln[len("### ITEM "):].strip(), "window": None}
        items.append(cur)
        mode = None
    elif cur is not None:
        if ln.startswith("WINDOW:"):
            mode = "w"
            continue
        if ln.startswith("NOTE AT:"):
            mode = None
            continue
        if mode == "w" and cur["window"] is None:
            cur["window"] = ln

ids = [it["id"] for it in items]
assert len(ids) == len(set(ids)), "duplicate ids in pack"
for it in items:
    assert it["window"] is not None, "no window for %s" % it["id"]

with open(json_path, encoding="utf-8") as f:
    ans = json.load(f)

missing = set(ids) - set(ans)
extra = set(ans) - set(ids)
assert not missing, "missing answers: %s" % sorted(missing)
assert not extra, "extra answers: %s" % sorted(extra)

OVR = ["overrul", "abrogat", "disapprov", "reced"]
BAD = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
       "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
       "without overruling", "rather than overrul", "declin", "refus", "would overrule",
       "should be overruled", "should overrule", "to overrule", "contend", "dissent",
       "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]

errors = []
rows = []
n_true = 0
for it in items:
    iid = it["id"]
    a = ans[iid]
    if a["states"]:
        n_true += 1
        q = a["quote"]
        w = it["window"]
        if len(q) > 400:
            errors.append((iid, "quote longer than 400"))
        if q not in w:
            errors.append((iid, "quote not a substring of window"))
        if not any(o in q.lower() for o in OVR):
            errors.append((iid, "no overruling word in quote"))
        if q.startswith("receded") or q.startswith("Receded"):
            errors.append((iid, "receded first word"))
        for b in BAD:
            if b in q.lower():
                errors.append((iid, "bad string in quote: " + b))
        for key in ("xkey", "ykey"):
            if not a.get(key) or a[key] not in q:
                errors.append((iid, "%s not inside quote" % key))
        rows.append({"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"],
                     "field_limit": a.get("field_limit", ""), "doctrine": a.get("doctrine", ""),
                     "quote": q, "confidence": a["confidence"]})
    else:
        rows.append({"id": iid, "states": False, "reason": a["reason"], "kind": "", "scope": "",
                     "field_limit": "", "doctrine": "", "quote": "", "confidence": a["confidence"]})

if errors:
    for e in errors:
        print("ERROR", e)
    sys.exit(1)

os.makedirs(os.path.dirname(ans_path), exist_ok=True)
with open(ans_path, "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("pack %s: items=%d states_true=%d" % (pack, len(items), n_true))
