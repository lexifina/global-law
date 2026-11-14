import json
import sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACK = BASE + r"\packs\pack_T1f_023.md"
OUT = BASE + r"\ans_prescreen\ans_pack_T1f_023.jsonl"

# F = states false (reason), T = states true (kind, scope, field_limit, doctrine, quote)
F = {
    "s01240": ("otherDecision", 0.9),
    "s01187": ("otherDecision", 0.9),
    "s01120": ("question", 0.85),
    "s03092": ("notOverruling", 0.95),
    "s03261": ("notOverruling", 0.95),
    "s03713": ("cannotTell", 0.95),
    "s01087": ("negation", 0.95),
    "s01272": ("otherDecision", 0.9),
    "s01292": ("cannotTell", 0.95),
    "s01318": ("quotation", 0.85),
    "s01733": ("notOverruling", 0.95),
    "s01930": ("notOverruling", 0.95),
    "s01102": ("ownAct", 0.9),
    "s01207": ("notOverruling", 0.95),
    "s01136": ("notOverruling", 0.9),
    "s01219": ("notOverruling", 0.95),
    "s01458": ("notOverruling", 0.95),
    "s01502": ("notOverruling", 0.95),
    "s03159": ("notOverruling", 0.9),
    "s01124": ("notOverruling", 0.9),
    "s01220": ("notOverruling", 0.95),
    "s01227": ("notOverruling", 0.95),
    "s01103": ("notOverruling", 0.9),
    "s01357": ("otherDecision", 0.9),
    "s01494": ("otherDecision", 0.9),
    "s02312": ("ownAct", 0.9),
    "s02414": ("otherDecision", 0.9),
    "s01196": ("notOverruling", 0.95),
    "s01197": ("notOverruling", 0.95),
    "s01247": ("notOverruling", 0.95),
    "s01248": ("notOverruling", 0.95),
    "s01100": ("notOverruling", 0.95),
    "s01642": ("otherDecision", 0.9),
    "s01943": ("otherDecision", 0.9),
    "s02014": ("otherDecision", 0.9),
    "s01451": ("wrongDirection", 0.9),
    "s02203": ("notOverruling", 0.95),
    "s02301": ("notOverruling", 0.95),
    "s01189": ("negation", 0.9),
    "s01387": ("cannotTell", 0.9),
    "s01126": ("notOverruling", 0.9),
    "s01156": ("notOverruling", 0.9),
    "s01168": ("notOverruling", 0.9),
    "s02891": ("notOverruling", 0.9),
    "s02089": ("notOverruling", 0.9),
    "s01169": ("notOverruling", 0.9),
    "s01255": ("notOverruling", 0.95),
    "s01275": ("notOverruling", 0.95),
}

T = {
    "s01084": {
        "kind": "overruled",
        "scope": "partialUnknown",
        "field_limit": "as to power to enact minimum wage laws",
        "doctrine": "",
        "quote": "West Coast Hotel Co. v. Parrish, 300 U. S. 379, overruled Adkins v. Children\u2019s Hospital, 261 U. S. 525, and Morehead v. Tipaldo, 298 U. S. 587",
        "confidence": 0.8,
    },
    "s01957": {
        "kind": "overruled",
        "scope": "all",
        "field_limit": "",
        "doctrine": "",
        "quote": "Benton v. Maryland, 395 U. S. 784 (1969), this Court declared the double jeopardy provisions of the Fifth Amendment applicable to the States, overruling Palko v. Connecticut, 302 U. S. 319",
        "confidence": 0.9,
    },
}

FORBIDDEN = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
             "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
             "without overruling", "rather than overrul", "declin", "refus", "would overrule",
             "should be overruled", "should overrule", "to overrule", "contend", "dissent",
             "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]


def parse(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    items = []
    cur = None
    mode = None
    for ln in lines:
        if ln.startswith("### ITEM "):
            cur = {"id": ln[len("### ITEM "):].strip(), "window": []}
            items.append(cur)
            mode = None
            continue
        if cur is None:
            continue
        if ln.startswith("WINDOW:"):
            mode = "w"
            continue
        if ln.startswith("NOTE AT:"):
            mode = None
            continue
        if ln.startswith("W (") or ln.startswith("X (") or ln.startswith("Y (") or ln.startswith("INTRO"):
            mode = None
            continue
        if mode == "w":
            cur["window"].append(ln)
    for it in items:
        it["window"] = "\n".join(it["window"]).rstrip("\n")
    return items


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
    # check order equals pack order
    assert [o["id"] for o in out] == ids
    # re-read and verify
    back = [json.loads(l) for l in open(OUT, encoding="utf-8")]
    assert len(back) == 50 and [b["id"] for b in back] == ids
    for b in back:
        if b["states"]:
            it = next(x for x in items if x["id"] == b["id"])
            assert b["quote"] in it["window"] and len(b["quote"]) <= 400
    print("verified")


if __name__ == "__main__":
    main()
