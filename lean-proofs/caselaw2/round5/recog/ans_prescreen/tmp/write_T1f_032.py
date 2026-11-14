import json, os

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen"
OUT = os.path.join(BASE, "ans_pack_T1f_032.jsonl")


def f(i, reason, conf=0.9):
    return {"id": i, "states": False, "reason": reason, "kind": "", "scope": "",
            "field_limit": "", "doctrine": "", "quote": "", "confidence": conf}


def t(i, kind, scope, field_limit, doctrine, quote, conf):
    return {"id": i, "states": True, "kind": kind, "scope": scope,
            "field_limit": field_limit, "doctrine": doctrine, "quote": quote,
            "confidence": conf}


rows = [
    f("s02117", "notOverruling"),
    f("s02169", "notOverruling"),
    f("s02738", "otherDecision"),
    f("s02815", "ownAct"),
    f("s02892", "otherDecision"),
    f("s02961", "otherDecision"),
    f("s02978", "notOverruling"),
    f("s03056", "notOverruling"),
    t("s03263", "overruled", "all", "", "",
      "Parden v. Terminal R. Co. of Ala. Docks Dept., 377 U. S. 184, 190-194 (1964); Pennsylvania v. Union Gas Co., 491 U. S. 1, 13-23 (1989) (plurality opinion), they have since been overruled, see Seminole Tribe",
      0.5),
    f("s03326", "otherDecision"),
    t("s03370", "overruled", "partialUnknown", "", "constructive waiver rule",
      "College Savings Bank, we rested our decision to overrule the constructive waiver rule of Parden v. Terminal R. Co. of Ala. Docks Dept.",
      0.5),
    f("s01731", "notOverruling"),
    f("s02058", "notOverruling"),
    f("s01904", "would"),
    f("s01905", "otherDecision"),
    f("s02023", "notOverruling"),
    f("s02415", "otherDecision"),
    f("s02640", "otherDecision"),
    f("s03128", "wrongDirection"),
    f("s02970", "refusal"),
    f("s01996", "notOverruling"),
    f("s01737", "otherDecision"),
    f("s02628", "otherDecision"),
    f("s02809", "otherDecision"),
    f("s02810", "otherDecision"),
    f("s02863", "otherDecision"),
    f("s03704", "otherDecision"),
    f("s01755", "notOverruling"),
    f("s01931", "notOverruling"),
    f("s01756", "cannotTell"),
    f("s01779", "notOverruling"),
    f("s01782", "notOverruling"),
    f("s01847", "notMajority"),
    f("s01852", "notMajority"),
    f("s01896", "notOverruling"),
    f("s02799", "notOverruling"),
    f("s01791", "cannotTell"),
    f("s02531", "refusal"),
    f("s02132", "notOverruling"),
    f("s02261", "notInOneSpan"),
    f("s01794", "notOverruling"),
    f("s01820", "notOverruling"),
    f("s02575", "quotation"),
    f("s03041", "otherDecision"),
    f("s01872", "notOverruling"),
    f("s01783", "notOverruling"),
    f("s01785", "notOverruling"),
    f("s01867", "notOverruling"),
    f("s01967", "otherDecision"),
    f("s02059", "notOverruling"),
]

os.makedirs(os.path.join(BASE, "tmp"), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print("wrote", len(rows), "rows to", OUT)
