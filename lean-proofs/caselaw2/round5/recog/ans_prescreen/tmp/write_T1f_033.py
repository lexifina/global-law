import json, os, re

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACK = os.path.join(BASE, "packs", "pack_T1f_033.md")
OUT = os.path.join(BASE, "ans_prescreen", "ans_pack_T1f_033.jsonl")


def windows(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    out = {}
    cur = None
    for i, ln in enumerate(lines):
        if ln.startswith("### ITEM "):
            cur = ln[len("### ITEM "):].strip()
        elif ln.startswith("WINDOW:") and cur:
            out[cur] = lines[i + 1]
    return out


WIN = windows(PACK)


def sl(iid, start, end):
    w = WIN[iid]
    i = w.index(start)
    j = w.index(end, i) + len(end)
    return w[i:j]


def f(i, reason, conf=0.9):
    return {"id": i, "states": False, "reason": reason, "kind": "", "scope": "",
            "field_limit": "", "doctrine": "", "quote": "", "confidence": conf}


def t(i, kind, scope, field_limit, doctrine, quote, conf):
    return {"id": i, "states": True, "kind": kind, "scope": scope,
            "field_limit": field_limit, "doctrine": doctrine, "quote": quote,
            "confidence": conf}


rows = [
    f("s02179", "notOverruling"),
    f("s02199", "notOverruling"),
    f("s02250", "notOverruling"),
    f("s02492", "quotation"),
    f("s02772", "notMajority"),
    f("s02971", "negation"),
    f("s03221", "otherDecision"),
    f("s03331", "refusal"),
    f("s03363", "quotation"),
    f("s03398", "notOverruling"),
    f("s03399", "otherDecision"),
    f("s02307", "notOverruling"),
    f("s02308", "quotation"),
    f("s02123", "notOverruling"),
    f("s02124", "notOverruling"),
    f("s01812", "cannotTell"),
    f("s02289", "notOverruling"),
    f("s02383", "notOverruling"),
    f("s01821", "notOverruling"),
    f("s01803", "notOverruling"),
    f("s02661", "notMajority"),
    f("s02764", "notOverruling"),
    f("s03190", "notOverruling"),
    f("s03551", "notOverruling"),
    f("s02001", "argument"),
    f("s02231", "notOverruling"),
    f("s02410", "notOverruling"),
    f("s02549", "notOverruling"),
    f("s02112", "cannotTell"),
    f("s02321", "ownAct"),
    t("s03151", "overruled", "partialUnknown", "the due process holding", "",
      sl("s03151", "Bellas Hess linked due process", "due process holding"),
      0.8),
    f("s01963", "notOverruling"),
    f("s02605", "notOverruling"),
    f("s03071", "notOverruling"),
    f("s02006", "quotation"),
    f("s02515", "quotation"),
    f("s02096", "notOverruling"),
    f("s01913", "ownAct"),
    f("s01914", "notOverruling"),
    t("s02831", "overruled", "partialUnknown", "", "criminal retroactivity cases",
      sl("s02831", "criminal retroactivity cases overruled by Griffith", "Stovall v. Denno"),
      0.6),
    f("s01929", "otherDecision"),
    f("s02265", "otherDecision"),
    f("s01922", "quotation"),
    f("s01965", "notOverruling"),
    f("s01911", "notOverruling"),
    f("s01916", "argument"),
    f("s01924", "notOverruling"),
    f("s02887", "otherDecision"),
    f("s01940", "notOverruling"),
    f("s02004", "notOverruling"),
]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print("wrote", len(rows), "rows to", OUT)
