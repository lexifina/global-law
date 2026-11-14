import json, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACK = BASE + r"\packs\pack_T1f_042.md"
OUT = BASE + r"\ans_prescreen\ans_pack_T1f_042.jsonl"

F = lambda reason: {"states": False, "reason": reason, "kind": "", "scope": "", "field_limit": "", "doctrine": "", "quote": "", "confidence": 0.9}

ANS = {
    "s02768": F("argument"),
    "s02816": F("would"),
    "s02825": F("cannotTell"),
    "s02826": F("cannotTell"),
    "s02876": F("notOverruling"),
    "s02877": F("otherDecision"),
    "s02980": F("notOverruling"),
    "s02981": F("notOverruling"),
    "s02982": F("notOverruling"),
    "s03003": F("notOverruling"),
    "s03062": F("notOverruling"),
    "s03080": F("notOverruling"),
    "s03085": F("notOverruling"),
    "s03086": F("notOverruling"),
    "s03136": F("notOverruling"),
    "s03371": F("notOverruling"),
    "s03029": F("notOverruling"),
    "s03107": F("ownAct"),
    "s03311": {
        "states": True, "reason": "", "kind": "overruled", "scope": "all", "field_limit": "", "doctrine": "",
        "quote": "Agostini v. Felton, 521 U. S. 203 (1997) (approving a program that provided public employees to teach remedial classes at religious and other private schools), overruling Aguilar v. Felton, 473 U. S. 402 (1985) (barring public school teachers from going to parochial schools to provide remedial education to disadvantaged children), and School Dist. of Grand Rapids v. Ball, 473 U. S. 373 (1985)",
        "confidence": 0.55,
    },
    "s03696": F("otherDecision"),
    "s03108": F("ownAct"),
    "s03199": F("argument"),
    "s02878": F("notOverruling"),
    "s02776": F("notOverruling"),
    "s02848": F("notOverruling"),
    "s02898": F("notOverruling"),
    "s02950": F("notOverruling"),
    "s02804": F("notOverruling"),
    "s03200": F("notOverruling"),
    "s02910": F("would"),
    "s03109": F("question"),
    "s03501": F("otherDecision"),
    "s03592": F("notMajority"),
    "s02812": F("notOverruling"),
    "s02813": F("notOverruling"),
    "s02814": F("notOverruling"),
    "s02849": F("notOverruling"),
    "s02867": F("notOverruling"),
    "s02951": F("notOverruling"),
    "s03074": F("negation"),
    "s03157": F("negation"),
    "s03241": F("notMajority"),
    "s03456": F("notMajority"),
    "s03566": F("notOverruling"),
    "s03705": F("notMajority"),
    "s03517": F("argument"),
    "s03471": F("notMajority"),
    "s03615": F("notOverruling"),
    "s03133": F("notOverruling"),
    "s03361": F("notOverruling"),
}

text = open(PACK, encoding="utf-8").read()
ids = re.findall(r"^### ITEM (\S+)", text, flags=re.M)
assert len(ids) == len(set(ids)) == 50, len(ids)
assert set(ids) == set(ANS), (set(ids) ^ set(ANS))

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for i in ids:
        obj = {"id": i}
        obj.update(ANS[i])
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
print("wrote", len(ids), "lines to", OUT)
