import json
import sys
sys.path.insert(0, r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\tmp")
from build_T1f_023 import parse, FORBIDDEN

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACK = BASE + r"\packs\pack_T1f_024.md"
OUT = BASE + r"\ans_prescreen\ans_pack_T1f_024.jsonl"

F = {
    "s01281": ("notOverruling", 0.9),
    "s01670": ("notOverruling", 0.95),
    "s02022": ("notOverruling", 0.95),
    "s02245": ("notOverruling", 0.95),
    "s01477": ("cannotTell", 0.9),
    "s01157": ("notOverruling", 0.9),
    "s01170": ("notOverruling", 0.9),
    "s01771": ("notOverruling", 0.9),
    "s02771": ("notOverruling", 0.9),
    "s01208": ("notOverruling", 0.95),
    "s01249": ("notOverruling", 0.9),
    "s01396": ("notOverruling", 0.9),
    "s01179": ("notOverruling", 0.95),
    "s02141": ("otherDecision", 0.9),
    "s01195": ("notOverruling", 0.9),
    "s01635": ("notOverruling", 0.95),
    "s01241": ("notOverruling", 0.9),
    "s01253": ("notOverruling", 0.95),
    "s01336": ("wrongDirection", 0.95),
    "s01355": ("notOverruling", 0.9),
    "s01603": ("notOverruling", 0.9),
    "s01388": ("cannotTell", 0.9),
    "s01486": ("notOverruling", 0.9),
    "s03094": ("notOverruling", 0.9),
    "s03160": ("notOverruling", 0.9),
    "s01211": ("notOverruling", 0.9),
    "s01286": ("notOverruling", 0.9),
    "s01279": ("argument", 0.9),
    "s03533": ("notOverruling", 0.9),
    "s03653": ("notOverruling", 0.9),
    "s01772": ("otherDecision", 0.9),
    "s01425": ("notOverruling", 0.9),
    "s02126": ("notOverruling", 0.9),
    "s01339": ("otherDecision", 0.9),
    "s01373": ("otherDecision", 0.9),
    "s01623": ("otherDecision", 0.9),
    "s01664": ("otherDecision", 0.9),
    "s01696": ("otherDecision", 0.9),
    "s01800": ("otherDecision", 0.9),
    "s02070": ("otherDecision", 0.85),
    "s01726": ("notOverruling", 0.9),
    "s01329": ("wrongDirection", 0.9),
    "s01414": ("notOverruling", 0.9),
    "s01392": ("notOverruling", 0.9),
    "s01990": ("notOverruling", 0.9),
    "s01627": ("negation", 0.9),
    "s01309": ("notOverruling", 0.95),
    "s01580": ("notOverruling", 0.95),
}

T = {
    "s01830": {
        "kind": "overruled",
        "scope": "all",
        "field_limit": "",
        "doctrine": "",
        "quote": "Katz v. United States, 389 U. S. 347 (1967), overruled Olmstead v. United States, 277 U. S. 438 (1928), and Gold man v. United States, 316 U. S. 129",
        "confidence": 0.9,
    },
    "s01643": {
        "kind": "overruled",
        "scope": "all",
        "field_limit": "",
        "doctrine": "",
        "quote": "Betts v. Brady, 316 U. S. 455 (1942), and accordingly relied on various \u201cspecial circumstances\u201d to make the right to counsel applicable. In Gideon v. Wainwright, 372 U. S. 335 (1963), however, Betts was overruled",
        "confidence": 0.85,
    },
}


def main():
    items = parse(PACK)
    ids = [it["id"] for it in items]
    assert len(ids) == len(set(ids)) == 50, (len(ids), len(set(ids)))
    decided = set(F) | set(T)
    assert decided == set(ids), ("mismatch", sorted(set(ids) - decided), sorted(decided - set(ids)))
    assert not (set(F) & set(T))
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
