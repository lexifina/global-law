import json, os, re, sys

pack, decf, outf = sys.argv[1], sys.argv[2], sys.argv[3]
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "contend", "dissent",
          "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]

text = open(pack, encoding="utf-8", newline="").read().replace("\r\n", "\n")
dec = json.load(open(decf, encoding="utf-8"))

order, windows = [], {}
for block in text.split("### ITEM ")[1:]:
    lines = block.split("\n")
    iid = lines[0].strip()
    wi = [i for i, l in enumerate(lines) if l.strip() == "WINDOW:"][0]
    order.append(iid)
    windows[iid] = lines[wi + 1]

missing = set(order) - set(dec)
extra = set(dec) - set(order)
assert not missing, ("missing decisions", sorted(missing))
assert not extra, ("extra decisions", sorted(extra))
assert len(order) == len(set(order)), "duplicate ids in pack"

out_lines = []
n_true = 0
for iid in order:
    d = dec[iid]
    if d["states"] is True:
        w = windows[iid]
        s = w.find(d["start"])
        assert s >= 0, (iid, "start not found")
        e = w.find(d["end"], s)
        assert e >= 0, (iid, "end not found")
        q = w[s:e + len(d["end"])]
        assert len(q) <= 400, (iid, "too long", len(q))
        assert q in w, (iid, "not substring")
        ql = q.lower()
        bad = [b for b in FORBID if b in ql]
        assert not bad, (iid, "forbidden", bad)
        assert re.search(r"overrul|abrogat|disapprov|reced", q, re.I), (iid, "no overruling word")
        assert d["xmark"] in q, (iid, "X marker not in quote")
        assert d["ymark"] in q, (iid, "Y marker not in quote")
        obj = {"id": iid, "states": True, "kind": d["kind"], "scope": d["scope"],
               "field_limit": d.get("field_limit", ""), "doctrine": d.get("doctrine", ""),
               "quote": q, "confidence": d["confidence"]}
        n_true += 1
    else:
        obj = {"id": iid, "states": False, "reason": d["reason"], "kind": "", "scope": "",
               "field_limit": "", "doctrine": "", "quote": "", "confidence": d.get("confidence", 0.9)}
    out_lines.append(json.dumps(obj, ensure_ascii=False))

os.makedirs(os.path.dirname(outf), exist_ok=True)
with open(outf, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out_lines) + "\n")

# re-verify written file
rows = [json.loads(l) for l in open(outf, encoding="utf-8")]
assert [r["id"] for r in rows] == order, "order/coverage mismatch"
for r in rows:
    if r["states"]:
        assert r["quote"] in windows[r["id"]] and len(r["quote"]) <= 400
print(os.path.basename(pack), "items:", len(order), "states_true:", n_true, "written:", len(rows))
