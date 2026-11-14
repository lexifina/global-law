import json, os, re

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
OVER = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
BANNED = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "argu", "contend", "urge",
          "dissent", "question", "doubt"]

# id -> (reason, confidence) for states:false ; id -> dict for states:true
A045 = [
    ("s01969", "notOverruling", 0.95), ("s02719", "notOverruling", 0.95),
    ("s02990", "notOverruling", 0.97), ("s03122", "notOverruling", 0.97),
    ("s01378", "notOverruling", 0.97), ("s02291", "notOverruling", 0.95),
    ("s02612", "notOverruling", 0.95), ("s02332", "otherDecision", 0.95),
    ("s01209", "notOverruling", 0.97), ("s01251", "notOverruling", 0.97),
    ("s03150", "wrongDirection", 0.95), ("s01282", "notOverruling", 0.97),
    ("s01716", "would", 0.95), ("s03526", "refusal", 0.95),
    ("s03531", "refusal", 0.95), ("s01222", "notOverruling", 0.95),
    ("s01231", "notOverruling", 0.95), ("s02251", "wrongDirection", 0.95),
    ("s01313", "notOverruling", 0.97), ("s01738", "notOverruling", 0.95),
    ("s01511", "wrongDirection", 0.93), ("s02452", "notOverruling", 0.95),
    ("s01273", "question", 0.93), ("s02090", "question", 0.93),
    ("s01429", "question", 0.93), ("s01480", "question", 0.93),
    ("s01594", "ownAct", 0.93), ("s01977", "otherDecision", 0.95),
    ("s02034", "question", 0.95), ("s01254", "notOverruling", 0.93),
    ("s01871", "notOverruling", 0.93), ("s02020", "notOverruling", 0.95),
    ("s02378", "notOverruling", 0.9), ("s01304", "refusal", 0.93),
    ("s01305", "refusal", 0.93), ("s01597", "wrongDirection", 0.95),
    ("s02147", "argument", 0.95), ("s01974", "notOverruling", 0.95),
    ("s01621", "wrongDirection", 0.93), ("s01741", "notOverruling", 0.93),
    ("s01256", "notOverruling", 0.97), ("s01473", "notOverruling", 0.97),
    ("s01885", "notOverruling", 0.97), ("s02470", "notOverruling", 0.97),
    ("s01276", "notOverruling", 0.97), ("s02102", "otherDecision", 0.93),
    ("s02371", "otherDecision", 0.93), ("s01294", "refusal", 0.93),
    ("s01474", "notOverruling", 0.97), ("s02252", "otherDecision", 0.95),
]

A061 = [
    ("s02213", "otherDecision", 0.93), ("s02508", "notOverruling", 0.97),
    ("s02372", "notOverruling", 0.95), ("s02120", "notOverruling", 0.93),
    ("s02266", "notOverruling", 0.95), ("s02269", "notOverruling", 0.95),
    ("s02894", "notOverruling", 0.95), ("s03522", "cannotTell", 0.97),
    ("s03046", "wrongDirection", 0.95), ("s03453", "notOverruling", 0.95),
    ("s02281", "notOverruling", 0.97), ("s03057", "notOverruling", 0.97),
    ("s03264", "notOverruling", 0.97), ("s02172", "notOverruling", 0.97),
    ("s02173", "notOverruling", 0.97), ("s02174", "notOverruling", 0.97),
    ("s02282", "notOverruling", 0.97), ("s02411", "notOverruling", 0.97),
    ("s02448", "notOverruling", 0.97), ("s02578", "cannotTell", 0.97),
    ("s03352", "cannotTell", 0.97), ("s03622", "notOverruling", 0.6),
    ("s02177", "wrongDirection", 0.95), ("s02923", "notOverruling", 0.95),
    ("s02128", "notOverruling", 0.93), ("s02262", "notOverruling", 0.93),
    ("s02292", "wrongDirection", 0.93), ("s02263", "notOverruling", 0.93),
    ("s02493", "wrongDirection", 0.93), ("s02939", "otherDecision", 0.93),
    ("s02287", "notOverruling", 0.97), ("s02602", "would", 0.95),
    ("s02936", "notOverruling", 0.93), ("s02973", "would", 0.95),
    ("s02663", "notOverruling", 0.97), ("s02216", "notOverruling", 0.95),
    ("s02283", "notOverruling", 0.97), ("s02358", "notOverruling", 0.95),
    ("s02397", "notOverruling", 0.93), ("s02412", "notOverruling", 0.97),
    ("s02434", "notOverruling", 0.97), ("s02435", "notOverruling", 0.97),
    ("s02449", "notOverruling", 0.97), ("s02520", "would", 0.95),
    ("s02695", "notOverruling", 0.97), ("s02244", "notOverruling", 0.97),
    ("s02194", "notOverruling", 0.97),
    ("s02925", {"kind": "overruled", "scope": "otherGrounds", "field_limit": "", "doctrine": "",
                "start": "Procunier v. Martinez, 416 U. S. 396",
                "end": "Thornburgh v. Abbott, 490 U. S. 401",
                "x": ["Procunier", "416 U. S. 396"], "y": ["Thornburgh", "490 U. S. 401"],
                "confidence": 0.95}),
    ("s02946", "otherDecision", 0.95), ("s02570", "argument", 0.95),
]


def parse_pack(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    items = []
    for block in re.split(r"(?m)^### ITEM ", text)[1:]:
        iid = block.split("\n", 1)[0].strip()
        m = re.search(r"\nWINDOW:\n(.*?)\nNOTE AT:\n", block, re.S)
        items.append((iid, m.group(1) if m else ""))
    return items


def run(pack, answers):
    items = parse_pack(os.path.join(BASE, "packs", pack + ".md"))
    ids = [i for i, _ in items]
    assert ids == [a[0] for a in answers], (pack, "order/ids mismatch",
                                            [x for x in zip(ids, [a[0] for a in answers]) if x[0] != x[1]])
    win = dict(items)
    rows, n_true = [], 0
    for a in answers:
        iid = a[0]
        if isinstance(a[1], dict):
            d = a[1]
            w = win[iid]
            s = w.index(d["start"])
            e = w.index(d["end"], s) + len(d["end"])
            q = w[s:e]
            assert q in w and len(q) <= 400, (iid, len(q))
            assert OVER.search(q), iid
            assert any(n in q for n in d["x"]), iid
            assert any(n in q for n in d["y"]), iid
            low = q.lower()
            hit = [b for b in BANNED if b in low]
            assert not hit, (iid, hit)
            rows.append({"id": iid, "states": True, "kind": d["kind"], "scope": d["scope"],
                         "field_limit": d["field_limit"], "doctrine": d["doctrine"],
                         "quote": q, "confidence": d["confidence"]})
            n_true += 1
        else:
            rows.append({"id": iid, "states": False, "reason": a[1], "kind": "", "scope": "",
                         "field_limit": "", "doctrine": "", "quote": "", "confidence": a[2]})
    out = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # re-read and verify
    with open(out, encoding="utf-8") as f:
        back = [json.loads(line) for line in f if line.strip()]
    assert [r["id"] for r in back] == ids and len(set(ids)) == len(ids)
    for r in back:
        if r["states"]:
            assert r["quote"] in win[r["id"]] and len(r["quote"]) <= 400
    print(pack, "items", len(back), "true", n_true)
    for r in back:
        if r["states"]:
            print("  ", r["id"], len(r["quote"]), r["quote"])


run("pack_T1s_045", A045)
run("pack_T1s_061", A061)
