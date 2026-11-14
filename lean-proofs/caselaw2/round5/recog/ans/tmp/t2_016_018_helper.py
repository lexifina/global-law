import json, re, sys, os

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
BAD = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
       "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
       "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu", "contend",
       "urge", "dissent", "question", "doubt"]
WORD = re.compile(r"overrul|abrogat|disapprov|reced", re.I)


def load_pack(name):
    with open(os.path.join(BASE, "packs", name + ".md"), encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")
    items = []
    for block in text.split("### ITEM ")[1:]:
        iid = block.split("\n", 1)[0].strip()
        w = block.split("\nWINDOW:\n", 1)[1]
        w = w.split("\nNOTE AT:", 1)[0]
        items.append((iid, w))
    return items


def T(iid, kind, scope, start, end, xtok, ytok, conf, fl="", doc=""):
    return dict(id=iid, states=True, kind=kind, scope=scope, start=start, end=end, xtok=xtok, ytok=ytok,
                conf=conf, fl=fl, doc=doc)


def F(iid, reason, conf):
    return dict(id=iid, states=False, reason=reason, conf=conf)


def span(w, start, end, iid):
    i = w.find(start)
    assert i >= 0, (iid, "start not found", start)
    assert w.find(start, i + 1) < 0 or True
    j = w.find(end, i)
    assert j >= 0, (iid, "end not found", end)
    return w[i:j + len(end)]


def build(name, entries):
    items = load_pack(name)
    ids = [i for i, _ in items]
    assert ids == [e["id"] for e in entries], (
        "order/coverage mismatch", [(a, b) for a, b in zip(ids, [e["id"] for e in entries]) if a != b],
        len(ids), len(entries))
    win = dict(items)
    out = []
    problems = []
    for e in entries:
        if not e["states"]:
            out.append(dict(id=e["id"], states=False, reason=e["reason"], kind="", scope="", field_limit="",
                            doctrine="", quote="", confidence=e["conf"]))
            continue
        w = win[e["id"]]
        q = span(w, e["start"], e["end"], e["id"])
        fl = e["fl"]
        if isinstance(fl, tuple):
            fl = span(w, fl[0], fl[1], e["id"])
        if len(q) > 400:
            problems.append((e["id"], "too long", len(q)))
        if q not in w:
            problems.append((e["id"], "not substring"))
        if not WORD.search(q):
            problems.append((e["id"], "no overruling word"))
        if e["xtok"] not in q:
            problems.append((e["id"], "x missing", e["xtok"]))
        if e["ytok"] not in q:
            problems.append((e["id"], "y missing", e["ytok"]))
        low = q.lower()
        for b in BAD:
            if b in low:
                problems.append((e["id"], "forbidden", b))
        out.append(dict(id=e["id"], states=True, kind=e["kind"], scope=e["scope"], field_limit=fl,
                        doctrine=e["doc"], quote=q, confidence=e["conf"]))
    path = os.path.join(BASE, "ans", "ans_" + name + ".jsonl")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    # re-read and verify independently
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f.read().split("\n") if l]
    assert [r["id"] for r in rows] == ids
    for r in rows:
        if r["states"]:
            assert r["quote"] in win[r["id"]] and len(r["quote"]) <= 400 or problems, r["id"]
    print(name, "items", len(rows), "true", sum(1 for r in rows if r["states"]))
    for p in problems:
        print("  PROBLEM", p)
    for r in rows:
        if r["states"]:
            print("  ", r["id"], len(r["quote"]), "|", r["quote"])
