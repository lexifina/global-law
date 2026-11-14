import importlib.util
import json
import re
import sys

# usage: python build_answers.py <pack_name e.g. pack_T1f_007> <answers .py file>
PACK_NAME = sys.argv[1]
ANS_FILE = sys.argv[2]
BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACK = BASE + r"\packs\\" + PACK_NAME + ".md"
OUT = BASE + r"\ans_prescreen\ans_" + PACK_NAME + ".jsonl"

FORBIDDEN = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
             "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
             "without overruling", "rather than overrul", "declin", "refus", "would overrule",
             "should be overruled", "should overrule", "to overrule", "contend", "dissent",
             "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]

spec = importlib.util.spec_from_file_location("answers", ANS_FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ANS = mod.ANS


def parse_pack(path):
    txt = open(path, encoding="utf-8").read()
    items = []
    for block in txt.split("### ITEM ")[1:]:
        lines = block.split("\n")
        iid = lines[0].strip()
        stripped = [l.strip() for l in lines]
        assert stripped.count("WINDOW:") == 1, iid
        assert stripped.count("NOTE AT:") == 1, iid
        w = stripped.index("WINDOW:")
        n = stripped.index("NOTE AT:")
        window = "\n".join(lines[w + 1:n]).strip("\n")
        items.append((iid, window))
    return items


items = parse_pack(PACK)
assert len(items) == len(ANS), (len(items), len(ANS))
out = []
problems = []
n_true = 0
for (iid, win), (aid, a) in zip(items, ANS):
    assert iid == aid, (iid, aid)
    rec = {"id": iid, "states": a["states"]}
    if a["states"]:
        n_true += 1
        m = re.search(a["pat"], win, re.S)
        if not m:
            problems.append((iid, "pattern not found in window"))
            rec.update(states=False, reason="notInOneSpan", kind="", scope="", field_limit="",
                       doctrine="", quote="", confidence=a["confidence"])
            out.append(rec)
            continue
        q = m.group(0)
        if len(q) > 400:
            problems.append((iid, "quote too long %d" % len(q)))
        if not re.search(r"overrul|abrogat|disapprov|reced", q, re.I):
            problems.append((iid, "no overruling word"))
        if a["x"] not in q:
            problems.append((iid, "X name missing"))
        if a["y"] not in q:
            problems.append((iid, "Y name missing"))
        low = q.lower()
        for f in FORBIDDEN:
            if f in low:
                problems.append((iid, "forbidden string: " + f))
        if q not in win:
            problems.append((iid, "quote not in window"))
        rec.update(kind=a["kind"], scope=a["scope"], field_limit="", doctrine="", quote=q,
                   confidence=a["confidence"])
    else:
        rec.update(reason=a["reason"], kind="", scope="", field_limit="", doctrine="", quote="",
                   confidence=a["confidence"])
    out.append(rec)

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("items:", len(out), "states true:", n_true)
print("problems:", problems if problems else "none")
