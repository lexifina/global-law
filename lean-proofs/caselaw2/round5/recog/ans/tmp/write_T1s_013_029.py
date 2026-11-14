import json, re, os, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]
WORDS = ["overrul", "abrogat", "disapprov", "reced"]

# id -> reason (false) or dict (true)
A013 = {
 "s00649": "notOverruling", "s00319": "otherDecision", "s00001": "notOverruling", "s00002": "notOverruling",
 "s00203": "notOverruling", "s00208": "wrongDirection", "s00209": "wrongDirection", "s02130": "notOverruling",
 "s03034": "notOverruling", "s01382": "notOverruling", "s01897": "notOverruling", "s01315": "negation",
 "s02928": "negation",
 "s00019": dict(start="overruled in Louisville, C., & C. R. Co. v. Letson", end="Deveaux", kind="overruled",
                scope="all", names=["Letson", "Deveaux"], conf=0.85),
 "s00040": "notOverruling", "s00023": "notOverruling", "s00124": "notOverruling", "s00003": "notOverruling",
 "s00230": "notOverruling", "s00245": "notOverruling", "s00013": "notOverruling", "s00005": "quotation",
 "s01010": "notOverruling", "s00229": "notOverruling", "s00078": "otherDecision", "s00092": "otherDecision",
 "s00042": "notOverruling", "s00047": "notOverruling", "s00024": "notOverruling", "s02178": "negation",
 "s02911": "negation", "s00945": "notOverruling", "s00264": "notOverruling", "s00464": "notOverruling",
 "s01891": "wrongDirection", "s00008": "notOverruling", "s00014": "notOverruling", "s00114": "negation",
 "s00115": "negation", "s00204": "negation", "s00235": "notOverruling", "s00294": "notOverruling",
 "s01562": "wrongDirection", "s00011": "otherDecision",
 "s00030": dict(start="The Genesee Chief, 12 How. 443, 455", end="10 Wheat. 428, was overruled", kind="overruled",
                scope="all", names=["Genesee Chief", "Thomas Jefferson"], conf=0.9),
 "s00032": "quotation", "s00004": "notOverruling", "s00252": "notOverruling", "s03201": "negation",
 "s00275": "notOverruling",
}
A029 = {
 "s00527": "notOverruling", "s00529": "notOverruling", "s00495": "negation", "s00501": "refusal",
 "s00493": "negation", "s00958": "notOverruling", "s01381": "notOverruling", "s02056": "wrongDirection",
 "s02455": "otherDecision",
 "s03039": dict(start="Thompson v. Utah, 170 U.S. 343 (1898)", end="Collins overruled", kind="overruled",
                scope="all", names=["Thompson v. Utah", "Collins"], conf=0.95),
 "s03070": "otherDecision", "s03645": "notOverruling", "s00569": "negation", "s00594": "negation",
 "s00975": "notOverruling", "s02599": "notOverruling", "s00552": "notOverruling", "s00559": "notOverruling",
 "s00985": "notOverruling", "s00671": "notOverruling", "s00504": "negation", "s00539": "negation",
 "s00540": "negation", "s01545": "refusal", "s01942": "refusal", "s00764": "notOverruling",
 "s00630": "would", "s01306": "would", "s00843": "notOverruling", "s00517": "notOverruling",
 "s00541": "notOverruling", "s00588": "notOverruling", "s00655": "notOverruling", "s00516": "notOverruling",
 "s00542": "notOverruling", "s00553": "notOverruling", "s00591": "notOverruling", "s00538": "negation",
 "s00836": "refusal", "s00837": "refusal", "s01546": "refusal", "s01547": "refusal", "s00600": "notOverruling",
 "s00723": "would", "s01366": "notOverruling", "s00557": "notOverruling", "s00601": "notOverruling",
 "s00545": "notOverruling", "s00842": "notOverruling", "s00973": "notOverruling",
}


def parse(pack):
    text = open(os.path.join(BASE, "packs", pack), encoding="utf-8").read()
    items = []
    for blk in re.split(r"(?m)^### ITEM ", text)[1:]:
        iid = blk.split("\n", 1)[0].strip()
        m = re.search(r"(?ms)^WINDOW:\n(.*?)\nNOTE AT:", blk)
        items.append((iid, m.group(1)))
    return items


def run(pack, ans):
    items = parse(pack)
    ids = [i for i, _ in items]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert set(ids) == set(ans), (set(ids) ^ set(ans))
    lines, ntrue = [], 0
    for iid, win in items:
        a = ans[iid]
        if isinstance(a, str):
            row = {"id": iid, "states": False, "reason": a, "kind": "", "scope": "", "field_limit": "",
                   "doctrine": "", "quote": "", "confidence": 0.9}
        else:
            s = win.index(a["start"])
            e = win.index(a["end"], s) + len(a["end"])
            q = win[s:e]
            assert q in win and len(q) <= 400, (iid, len(q))
            assert any(w in q.lower() for w in WORDS), iid
            for n in a["names"]:
                assert n in q, (iid, n)
            bad = [f for f in FORBID if f in q.lower()]
            assert not bad, (iid, bad)
            row = {"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"], "field_limit": "",
                   "doctrine": "", "quote": q, "confidence": a["conf"]}
            ntrue += 1
        lines.append(json.dumps(row, ensure_ascii=False))
    out = os.path.join(BASE, "ans", "ans_" + pack.replace(".md", ".jsonl"))
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    # re-read and verify
    rows = [json.loads(l) for l in open(out, encoding="utf-8").read().splitlines()]
    assert [r["id"] for r in rows] == ids
    wins = dict(items)
    for r in rows:
        if r["states"]:
            assert r["quote"] in wins[r["id"]] and len(r["quote"]) <= 400
            print("  ", r["id"], len(r["quote"]), repr(r["quote"]))
    print(pack, "items", len(rows), "true", ntrue)


run("pack_T1s_013.md", A013)
run("pack_T1s_029.md", A029)
