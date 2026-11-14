import json
import re
import sys
sys.path.insert(0, r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\tmp")
from build_T1f_023 import parse, FORBIDDEN

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACK = BASE + r"\packs\pack_T1f_028.md"
OUT = BASE + r"\ans_prescreen\ans_pack_T1f_028.jsonl"

F = {
    "s01715": ("notOverruling", 0.9),
    "s01490": ("cannotTell", 0.9),
    "s01567": ("notMajority", 0.9),
    "s02344": ("otherDecision", 0.9),
    "s02433": ("notOverruling", 0.95),
    "s02639": ("notOverruling", 0.95),
    "s01805": ("notOverruling", 0.95),
    "s01806": ("notOverruling", 0.9),
    "s01815": ("notOverruling", 0.95),
    "s02230": ("notOverruling", 0.95),
    "s02486": ("notOverruling", 0.95),
    "s02548": ("notOverruling", 0.95),
    "s02689": ("cannotTell", 0.9),
    "s03573": ("notOverruling", 0.95),
    "s02129": ("notOverruling", 0.95),
    "s02011": ("notOverruling", 0.95),
    "s01970": ("quotation", 0.9),
    "s02363": ("notOverruling", 0.95),
    "s01493": ("notOverruling", 0.9),
    "s01938": ("notOverruling", 0.9),
    "s01617": ("notOverruling", 0.7),
    "s01735": ("otherDecision", 0.9),
    "s02861": ("notOverruling", 0.9),
    "s01640": ("wrongDirection", 0.9),
    "s01654": ("notInOneSpan", 0.8),
    "s01795": ("cannotTell", 0.9),
    "s02111": ("cannotTell", 0.9),
    "s02146": ("cannotTell", 0.9),
    "s02209": ("cannotTell", 0.9),
    "s03148": ("notOverruling", 0.9),
    "s01508": ("question", 0.9),
    "s01509": ("question", 0.9),
    "s01510": ("ownAct", 0.9),
    "s01488": ("argument", 0.9),
    "s01512": ("notOverruling", 0.9),
    "s02601": ("notOverruling", 0.9),
    "s01506": ("notOverruling", 0.9),
    "s01542": ("notOverruling", 0.9),
    "s01721": ("notOverruling", 0.9),
    "s01978": ("ownAct", 0.9),
    "s02157": ("otherDecision", 0.9),
    "s02841": ("ownAct", 0.9),
    "s02843": ("ownAct", 0.9),
    "s01519": ("notOverruling", 0.95),
    "s01576": ("notOverruling", 0.95),
}

T = {
    "s01846": {
        "kind": "overruled",
        "scope": "all",
        "field_limit": "",
        "doctrine": "",
        "quote": "Marchetti v. United States, 390 U. S. 39, 53 (1968). Marchetti, which overruled earlier decisions of this Court in United States v. Kahriger, 345 U. S. 22",
        "confidence": 0.85,
    },
    "s01711": {
        "kind": "overruled",
        "scope": "otherGrounds",
        "field_limit": "",
        "doctrine": "",
        "quote": "Stein v. New York, 346 U. S. 156,178 (1953) (\u201cOur own Rules of Criminal Procedure make no provision for anything but a general verdict.\u201d), overruled on other grounds, Jackson v. Denno, 378 U. S. 368",
        "confidence": 0.85,
    },
    "s01710": {
        "kind": "overruled",
        "scope": "all",
        "field_limit": "",
        "doctrine": "",
        "quote": "overruled Stein v. New York, 346 U. S. 156 (1953), which had approved the New York practice. Whether- a guilty plea was entered before or after Jackson v. Denno",
        "confidence": 0.6,
    },
    "s02932": {
        "kind": "overruled",
        "scope": "otherGrounds",
        "field_limit": "",
        "doctrine": "",
        "quote": "Wilko v. Swan, 346 U. S. 427, 436-437 (1953) (parties bound by arbitrator\u2019s decision not in \u201cmanifest disregard\u201d of the law), overruled on other grounds, Rodriguez de Quijas v. Shearson/American Express, Inc., 490 U. S. 477",
        "confidence": 0.9,
    },
    "s02934": {
        "kind": "overruled",
        "scope": "all",
        "field_limit": "",
        "doctrine": "",
        "quote": "The Court subsequently overruled Wilko and, in so doing, characterized the decision as \u201cpervaded by . . . \u2018the old judicial hostility to arbitration.\u2019\u201d Rodriguez de Quijas v. Shearson/American Express, Inc., 490 U. S. 477",
        "confidence": 0.85,
    },
}


def span_report(window, x_names, y_names, word="overrul"):
    # minimal span length that holds an overrul word, an X name and a Y name
    best = None
    for xn in x_names:
        for yn in y_names:
            for m in re.finditer(re.escape(xn), window):
                pass
    occ = []
    for xn in x_names:
        occ += [(m.start(), m.end(), "X") for m in re.finditer(re.escape(xn), window)]
    for yn in y_names:
        occ += [(m.start(), m.end(), "Y") for m in re.finditer(re.escape(yn), window)]
    ovs = [(m.start(), m.end(), "W") for m in re.finditer(word, window)]
    for ow in ovs:
        for xo in [o for o in occ if o[2] == "X"]:
            for yo in [o for o in occ if o[2] == "Y"]:
                s = min(ow[0], xo[0], yo[0])
                e = max(ow[1], xo[1], yo[1])
                L = e - s
                if best is None or L < best:
                    best = L
    return best


def main():
    items = parse(PACK)
    ids = [it["id"] for it in items]
    assert len(ids) == len(set(ids)) == 50, (len(ids), len(set(ids)))
    decided = set(F) | set(T)
    assert decided == set(ids), ("mismatch", sorted(set(ids) - decided), sorted(decided - set(ids)))
    assert not (set(F) & set(T))
    # diagnostics for span lengths
    it654 = next(x for x in items if x["id"] == "s01654")
    print("s01654 min span:", span_report(it654["window"], ["Brown v. Allen", "344 U. S. 443"], ["Fay v. Noia", "372 U. S. 391"]))
    it934 = next(x for x in items if x["id"] == "s02934")
    print("s02934 quote len:", len(T["s02934"]["quote"]))
    out = []
    problems = []
    for it in items:
        i = it["id"]
        if i in T:
            t = T[i]
            q = t["quote"]
            win = it["window"]
            if q not in win:
                problems.append((i, "quote not in window"))
            if len(q) > 400:
                problems.append((i, "quote too long"))
            low = q.lower()
            for f in FORBIDDEN:
                if f in low:
                    problems.append((i, "forbidden " + f))
            if not any(w in q for w in ["overrul", "abrogat", "disapprov", "reced"]):
                problems.append((i, "no overruling word"))
            out.append({"id": i, "states": True, "kind": t["kind"], "scope": t["scope"],
                        "field_limit": t["field_limit"], "doctrine": t["doctrine"], "quote": q,
                        "confidence": t["confidence"]})
        else:
            reason, conf = F[i]
            out.append({"id": i, "states": False, "reason": reason, "kind": "", "scope": "",
                        "field_limit": "", "doctrine": "", "quote": "", "confidence": conf})
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    print("items", len(items), "written", len(out), "true", sum(1 for o in out if o["states"]))
    print("problems", problems)
    assert [o["id"] for o in out] == ids
    back = [json.loads(l) for l in open(OUT, encoding="utf-8")]
    assert len(back) == 50 and [b["id"] for b in back] == ids
    for b in back:
        if b["states"]:
            it = next(x for x in items if x["id"] == b["id"])
            assert b["quote"] in it["window"] and len(b["quote"]) <= 400
    print("verified")


if __name__ == "__main__":
    main()
