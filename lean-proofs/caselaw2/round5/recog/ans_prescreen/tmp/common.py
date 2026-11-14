import json
import os
import re

REC = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACKS = os.path.join(REC, "packs")
OUT = os.path.join(REC, "ans_prescreen")
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
BAD = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
       "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
       "without overruling", "rather than overrul", "declin", "refus", "would overrule",
       "should be overruled", "should overrule", "to overrule", "contend", "dissent",
       "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]


def parse(pack_name):
    path = os.path.join(PACKS, pack_name + ".md")
    text = open(path, encoding="utf-8").read()
    items = {}
    order = []
    for p in re.split(r"^### ITEM ", text, flags=re.M)[1:]:
        lines = p.split("\n")
        iid = lines[0].strip()
        wi = lines.index("WINDOW:")
        ni = lines.index("NOTE AT:")
        items[iid] = {
            "id": iid,
            "head": "\n".join(lines[:wi]),
            "window": "\n".join(lines[wi + 1:ni]),
        }
        order.append(iid)
    return items, order


def feasible(window, xkeys, ykeys, limit=400):
    """True if some span of <= limit chars holds an overruling word, an X key and a Y key."""
    o = [(m.start(), m.end()) for m in OVR.finditer(window)]
    xs = [(window.find(k, s), window.find(k, s) + len(k))
          for k in xkeys for s in [0] for _ in [0]]
    xs = []
    ys = []
    for k in xkeys:
        for m in re.finditer(re.escape(k), window):
            xs.append((m.start(), m.end()))
    for k in ykeys:
        for m in re.finditer(re.escape(k), window):
            ys.append((m.start(), m.end()))
    for a in o:
        for b in xs:
            for c in ys:
                lo = min(a[0], b[0], c[0])
                hi = max(a[1], b[1], c[1])
                if hi - lo <= limit:
                    return True
    return False


def write_pack(pack_name, answers):
    """answers: list of dicts in pack order. True rows need quote, kind, scope, field_limit,
    doctrine, conf, xkeys, ykeys. False rows need reason (xkeys/ykeys optional, checked for
    notInOneSpan)."""
    items, order = parse(pack_name)
    errors = []
    ids = [a["id"] for a in answers]
    if ids != order:
        missing = [i for i in order if i not in ids]
        extra = [i for i in ids if i not in order]
        dup = sorted({i for i in ids if ids.count(i) > 1})
        errors.append("id mismatch missing=%s extra=%s dup=%s order_equal=%s"
                      % (missing, extra, dup, ids == order))
    lines = []
    ntrue = 0
    for a in answers:
        it = items.get(a["id"])
        if it is None:
            continue
        w = it["window"]
        if a.get("states"):
            ntrue += 1
            q = a["quote"]
            if q not in w:
                errors.append("%s quote not in window" % a["id"])
            if len(q) > 400:
                errors.append("%s quote too long %d" % (a["id"], len(q)))
            if not OVR.search(q):
                errors.append("%s no overrul word in quote" % a["id"])
            for k in a["xkeys"]:
                if k not in q:
                    errors.append("%s X key %r not in quote" % (a["id"], k))
            for k in a["ykeys"]:
                if k not in q:
                    errors.append("%s Y key %r not in quote" % (a["id"], k))
            low = q.lower()
            for b in BAD:
                if b in low:
                    errors.append("%s bad string %r in quote" % (a["id"], b))
            row = {"id": a["id"], "states": True, "kind": a["kind"], "scope": a["scope"],
                   "field_limit": a.get("field_limit", ""), "doctrine": a.get("doctrine", ""),
                   "quote": q, "confidence": a["conf"]}
        else:
            if a.get("reason") == "notInOneSpan" and a.get("xkeys") and a.get("ykeys"):
                if feasible(w, a["xkeys"], a["ykeys"]):
                    errors.append("%s notInOneSpan but a feasible span exists" % a["id"])
            row = {"id": a["id"], "states": False, "reason": a["reason"], "kind": "", "scope": "",
                   "field_limit": "", "doctrine": "", "quote": "", "confidence": a.get("conf", 0.9)}
        lines.append(json.dumps(row, ensure_ascii=False))
    if not errors:
        outp = os.path.join(OUT, "ans_" + pack_name + ".jsonl")
        with open(outp, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        print("WROTE", outp)
    print("items", len(answers), "true", ntrue)
    for e in errors:
        print("ERR", e)
    return not errors
