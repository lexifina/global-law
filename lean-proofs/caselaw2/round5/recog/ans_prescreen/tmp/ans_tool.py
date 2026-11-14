import json, re, sys, os

# usage: python -I ans_tool.py <pack_path> <decisions_json> <out_jsonl>
# decisions json: {"<id>": {"s": true/false, "r": reason, "kind":..., "scope":..., "field_limit":..., "doctrine":..., "quote":..., "confidence":...}}
pack_path, dec_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(pack_path, encoding="utf-8").read()
items = {}
order = []
for block in text.split("### ITEM ")[1:]:
    iid = block.split("\n", 1)[0].strip()
    m = re.search(r"WINDOW:\n(.*?)\nNOTE AT:", block, re.S)
    window = m.group(1) if m else ""
    items[iid] = window
    order.append(iid)

dec = json.load(open(dec_path, encoding="utf-8"))
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "contend", "dissent",
          "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]
errors = []
out = []
trues = 0
if set(dec) != set(order):
    errors.append("id mismatch: missing=%s extra=%s" % (sorted(set(order)-set(dec)), sorted(set(dec)-set(order))))
for iid in order:
    d = dec.get(iid)
    if d is None:
        continue
    if d["s"]:
        trues += 1
        q = d["quote"]
        w = items[iid]
        if q not in w:
            errors.append("%s quote not in window" % iid)
        if len(q) > 400:
            errors.append("%s quote too long" % iid)
        for f in FORBID:
            if f in q.lower():
                errors.append("%s quote contains forbidden %r" % (iid, f))
        if not re.search(r"overrul|abrogat|disapprov|reced", q):
            errors.append("%s quote lacks overruling word" % iid)
        rec = {"id": iid, "states": True, "kind": d["kind"], "scope": d["scope"],
               "field_limit": d.get("field_limit", ""), "doctrine": d.get("doctrine", ""),
               "quote": q, "confidence": d["confidence"]}
    else:
        rec = {"id": iid, "states": False, "reason": d["r"], "kind": "", "scope": "",
               "field_limit": "", "doctrine": "", "quote": "", "confidence": d.get("confidence", 0.9)}
    out.append(json.dumps(rec, ensure_ascii=False))
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
print("items=%d answered=%d states_true=%d" % (len(order), len(out), trues))
for e in errors:
    print("ERROR", e)
