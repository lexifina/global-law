import json, os

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen"
OUT = os.path.join(BASE, "ans_pack_T1f_031.jsonl")


def f(i, reason, conf=0.9):
    return {"id": i, "states": False, "reason": reason, "kind": "", "scope": "",
            "field_limit": "", "doctrine": "", "quote": "", "confidence": conf}


def t(i, kind, scope, field_limit, doctrine, quote, conf):
    return {"id": i, "states": True, "kind": kind, "scope": scope,
            "field_limit": field_limit, "doctrine": doctrine, "quote": quote,
            "confidence": conf}


rows = [
    f("s03100", "otherDecision"),
    f("s01838", "notOverruling"),
    f("s02127", "notOverruling"),
    f("s01724", "notOverruling"),
    f("s01631", "wrongDirection"),
    f("s02659", "argument"),
    f("s03515", "argument"),
    f("s01744", "notInOneSpan"),
    f("s02044", "otherDecision"),
    f("s03161", "otherDecision"),
    f("s02092", "cannotTell"),
    f("s01890", "otherDecision"),
    f("s01966", "ownAct"),
    f("s02844", "otherDecision"),
    f("s03422", "notMajority"),
    f("s02064", "otherDecision"),
    f("s02068", "wrongDirection"),
    f("s02645", "notOverruling"),
    f("s01671", "ownAct"),
    f("s02916", "ownAct"),
    f("s01874", "notOverruling"),
    f("s01663", "notOverruling"),
    f("s01936", "notOverruling"),
    f("s02109", "notOverruling"),
    f("s02030", "cannotTell"),
    f("s02239", "ownAct"),
    f("s01665", "notOverruling"),
    f("s01705", "notOverruling"),
    f("s01802", "notOverruling"),
    f("s01961", "notOverruling"),
    f("s02071", "notOverruling"),
    f("s02505", "wrongDirection"),
    f("s03497", "notOverruling"),
    f("s01809", "notOverruling"),
    f("s01837", "notOverruling"),
    f("s02240", "notOverruling"),
    f("s02678", "otherDecision"),
    f("s02323", "notOverruling"),
    f("s02028", "notOverruling"),
    f("s02010", "argument"),
    f("s02591", "notOverruling"),
    f("s02629", "notOverruling"),
    f("s01975", "would"),
    f("s02049", "would"),
    f("s03633", "otherDecision"),
    f("s02917", "ownAct"),
    f("s02914", "notOverruling"),
    f("s01816", "quotation"),
    f("s02514", "quotation"),
    f("s01995", "notOverruling"),
]

os.makedirs(os.path.join(BASE, "tmp"), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print("wrote", len(rows), "rows to", OUT)
