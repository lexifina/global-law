import json, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACK = BASE + r"\packs\pack_T1f_045.md"
OUT = BASE + r"\ans_prescreen\ans_pack_T1f_045.jsonl"

def F(reason):
    return {"states": False, "reason": reason, "kind": "", "scope": "", "field_limit": "", "doctrine": "", "quote": "", "confidence": 0.9}

def T(kind, scope, quote, conf):
    return {"states": True, "reason": "", "kind": kind, "scope": scope, "field_limit": "", "doctrine": "", "quote": quote, "confidence": conf}

ANS = {
    "s03449": F("otherDecision"),
    "s03460": T("overruled", "otherGrounds",
                "Walton v. Arizona, 497 U. S. 639, 653 (1990), overruled on other grounds, Ring v. Arizona, 536 U. S. 584 (2002)", 0.9),
    "s03461": T("overruled", "all",
                "In Ring, we applied this principle to a death sentence imposed under the Arizona sentencing scheme at issue here. We concluded that, because Arizona law authorized the death penalty only if an aggravating factor was present, Apprendi required the existence of such a factor to be proved to a jury rather than to a judge. 536 U. S., at 603-609. We specifically overruled our earlier decision in Walton", 0.85),
    "s03462": T("overruled", "otherGrounds",
                "Walton, supra, overruled on other grounds, Ring v. Arizona, 536 U. S. 584 (2002)", 0.8),
    "s03504": F("notOverruling"),
    "s03068": F("ownAct"),
    "s03278": F("notOverruling"),
    "s03320": F("notOverruling"),
    "s03239": F("cannotTell"),
    "s03644": F("notOverruling"),
    "s03256": F("negation"),
    "s03587": F("notOverruling"),
    "s03158": F("negation"),
    "s03189": F("notOverruling"),
    "s03192": F("notOverruling"),
    "s03139": F("notOverruling"),
    "s03624": F("notOverruling"),
    "s03177": F("notOverruling"),
    "s03279": F("notOverruling"),
    "s03280": F("notOverruling"),
    "s03316": F("notOverruling"),
    "s03317": F("notOverruling"),
    "s03693": F("notMajority"),
    "s03700": F("notMajority"),
    "s03184": F("negation"),
    "s03492": F("cannotTell"),
    "s03178": F("notOverruling"),
    "s03225": F("notOverruling"),
    "s03368": F("negation"),
    "s03387": F("notOverruling"),
    "s03634": F("notOverruling"),
    "s03285": F("notOverruling"),
    "s03484": F("argument"),
    "s03667": F("argument"),
    "s03206": F("notOverruling"),
    "s03226": F("notOverruling"),
    "s03324": F("notOverruling"),
    "s03552": F("negation"),
    "s03553": F("negation"),
    "s03671": F("negation"),
    "s03436": F("argument"),
    "s03369": F("notOverruling"),
    "s03216": F("notOverruling"),
    "s03227": F("notOverruling"),
    "s03342": F("would"),
    "s03676": F("would"),
    "s03281": F("notOverruling"),
    "s03716": F("notOverruling"),
    "s03547": F("would"),
    "s03685": F("notOverruling"),
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
