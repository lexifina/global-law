import importlib.util
import json
import os
import re
import sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACKS = os.path.join(BASE, "packs")
OUT = os.path.join(BASE, "ans_prescreen")
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "contend", "dissent",
          "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]
VALID_REASONS = {"notMajority", "quotation", "argument", "negation", "question", "refusal", "would",
                 "ownAct", "wrongDirection", "otherDecision", "notOverruling", "cannotTell", "notInOneSpan"}


def parse_pack(path):
    text = open(path, encoding="utf-8").read()
    chunks = text.split("### ITEM ")[1:]
    items = []
    for ch in chunks:
        lines = ch.split("\n")
        iid = lines[0].strip()
        m = re.search(r"WINDOW:\n(.*?)\nNOTE AT:", ch, re.S)
        window = m.group(1) if m else None
        items.append((iid, window))
    return items


def main(pn):
    spec = importlib.util.spec_from_file_location("ans_mod", os.path.join(OUT, "tmp", "answers_%s.py" % pn))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    A = mod.A
    items = parse_pack(os.path.join(PACKS, mod.P + ".md"))
    ids = [i for i, _ in items]
    assert len(ids) == len(set(ids)), "dup ids in pack"
    missing = [i for i in ids if i not in A]
    extra = [k for k in A if k not in ids]
    assert not missing, ("missing", missing)
    assert not extra, ("extra", extra)
    errors = []
    lines = []
    n_true = 0
    for iid, window in items:
        a = A[iid]
        if a["states"]:
            n_true += 1
            q = a["quote"]
            if window is None:
                errors.append((iid, "no window"))
            if q not in window:
                errors.append((iid, "quote not in window"))
            if len(q) > 400:
                errors.append((iid, "quote too long"))
            if not re.search(r"overrul|abrogat|disapprov|reced", q, re.I):
                errors.append((iid, "no overruling word"))
            if re.match(r"receded", q):
                errors.append((iid, "receded first"))
            for f in FORBID:
                if f in q.lower():
                    errors.append((iid, "forbidden " + f))
            if a["x"] not in q:
                errors.append((iid, "x not in quote"))
            if a["y"] not in q:
                errors.append((iid, "y not in quote"))
            obj = dict(id=iid, states=True, kind=a["kind"], scope=a["scope"], field_limit=a["field_limit"],
                       doctrine=a["doctrine"], quote=q, confidence=a["confidence"])
        else:
            assert a["reason"] in VALID_REASONS, (iid, a["reason"])
            obj = dict(id=iid, states=False, reason=a["reason"], kind="", scope="", field_limit="",
                       doctrine="", quote="", confidence=0.9)
        lines.append(json.dumps(obj, ensure_ascii=False))
    if errors:
        print("ERRORS:")
        for e in errors:
            print(" ", e)
        sys.exit(1)
    out = os.path.join(OUT, "ans_pack_%s.jsonl" % pn)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(pn, "items", len(items), "states_true", n_true, "written", out)


if __name__ == "__main__":
    main(sys.argv[1])
