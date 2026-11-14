import json, sys, re
sys.path.insert(0, "~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/recog/ans_prescreen/tmp")
from r5_parse import parse
FORBID = ["not overrul","n't overrul","never overrul","not been overrul","never been overrul","not abrogat","n't abrogat","not been abrogat","not disapprov","whether","without overruling","rather than overrul","declin","refus","would overrule","should be overruled","should overrule","to overrule","contend","dissent","question","doubt","argues","argued","arguing","argument","urges","urged","urging"]
OVR = re.compile(r"overrul|abrogat|disapprov|reced")
def build(pack_path, out_path, rows):
    items = parse(pack_path)
    order = list(items)
    given = [r["id"] for r in rows]
    assert given == order, ("order/coverage mismatch", set(order)-set(given), set(given)-set(order), len(given), len(order))
    out = []
    for r in rows:
        it = items[r["id"]]
        if r["states"]:
            q = r["quote"]
            w = it["window"]
            assert q in w, ("quote not in window", r["id"])
            assert len(q) <= 400, ("too long", r["id"], len(q))
            low = q.lower()
            for f in FORBID:
                assert f not in low, ("forbidden", r["id"], f)
            assert OVR.search(q), ("no overrul word", r["id"])
            assert r["kind"] in ("overruled","abrogated","disapproved","recededFrom")
        else:
            assert r["reason"], r["id"]
            r = dict(r); r.setdefault("quote","")
        out.append(r)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    t = sum(1 for r in out if r["states"])
    print(out_path, "items", len(out), "states true", t)
    for r in out:
        if r["states"]:
            print("  TRUE", r["id"], r["kind"], r["scope"], repr(r["quote"][:120]))
def F(i, reason, conf=0.9):
    return {"id": i, "states": False, "reason": reason, "kind": "", "scope": "", "field_limit": "", "doctrine": "", "quote": "", "confidence": conf}
def T(i, kind, scope, quote, conf=0.8, field_limit="", doctrine=""):
    return {"id": i, "states": True, "kind": kind, "scope": scope, "field_limit": field_limit, "doctrine": doctrine, "quote": quote, "confidence": conf}
