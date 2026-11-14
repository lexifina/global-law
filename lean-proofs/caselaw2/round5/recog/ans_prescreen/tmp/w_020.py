import json

OUT = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\ans_pack_T1f_020.jsonl"

F = [
("s01193","otherDecision"),
("s00921","negation"),
("s00929","notOverruling"),
("s01200","would"),
("s01679","quotation"),
("s01338","otherDecision"),
("s00994","ownAct"),
("s01113","ownAct"),
("s01172","ownAct"),
("s01176","ownAct"),
("s03629","negation"),
("s01083","otherDecision"),
("s02224","notOverruling"),
("s02376","notOverruling"),
("s00998","notOverruling"),
("s01024","notOverruling"),
("s01639","otherDecision"),
("s01825","otherDecision"),
("s00957","notOverruling"),
("s01206","notOverruling"),
("s01250","notOverruling"),
("s01380","notOverruling"),
("s00995","otherDecision"),
("s01114","otherDecision"),
("s00940","notOverruling"),
("s01497","quotation"),
("s00999","notOverruling"),
("s01066","notOverruling"),
("s01093","otherDecision"),
("s01762","otherDecision"),
("s02131","otherDecision"),
("s01258","otherDecision"),
("s01259","otherDecision"),
("s01770","otherDecision"),
("s01819","otherDecision"),
("s02482","quotation"),
("s01391","ownAct"),
("s01394","negation"),
("s01658","ownAct"),
("s01919","otherDecision"),
("s02164","otherDecision"),
("s01284","argument"),
("s01532","argument"),
("s03045","otherDecision"),
("s03452","otherDecision"),
("s02769","notOverruling"),
("s00960","notOverruling"),
]

# (id, kind, scope, field_limit, doctrine, quote, confidence)
T = [
("s01167", "overruled", "partialUnknown", "", "",
 "Although the case was after-wards overruled on this point, O’Malley v. Woodrough, 307 U. S. 277, 283, what is of continuing interest is the Court’s reliance in Miles", 0.8),
("s01046", "disapproved", "partialUnknown", "", "",
 "Humphrey’s Executor v. United States, 295 U. S. 602, narrowly confined the scope of the Myers decision to include only “all purely executive officers.” 295 U. S., at 628. The Court explicitly “disapproved” the expressions in Myers", 0.6),
("s01233", "overruled", "all", "", "",
 "The Court’s decision in Ribnik v. McBride was overruled unanimously in Olsen v. Nebraska, 313 U. S. 236.", 0.85),
]

rows = []
for item_id, reason in F:
    rows.append({"id": item_id, "states": False, "reason": reason, "kind": "", "scope": "",
                 "field_limit": "", "doctrine": "", "quote": "", "confidence": 0.9})
for (item_id, kind, scope, fl, doc, quote, conf) in T:
    rows.append({"id": item_id, "states": True, "kind": kind, "scope": scope, "field_limit": fl,
                 "doctrine": doc, "quote": quote, "confidence": conf})

# keep pack order
PACK_ORDER = [
"s01167","s01193","s00921","s00929","s01200","s01679","s01338","s01046","s00994","s01113",
"s01172","s01176","s03629","s01083","s02224","s02376","s00998","s01024","s01639","s01825",
"s00957","s01206","s01250","s01380","s00995","s01114","s00940","s01497","s00999","s01066",
"s01093","s01233","s01762","s02131","s01258","s01259","s01770","s01819","s02482","s01391",
"s01394","s01658","s01919","s02164","s01284","s01532","s03045","s03452","s02769","s00960",
]
byid = {r["id"]: r for r in rows}
assert len(byid) == len(rows) == 50, (len(byid), len(rows))
assert set(byid) == set(PACK_ORDER)
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for i in PACK_ORDER:
        f.write(json.dumps(byid[i], ensure_ascii=False) + "\n")
print(len(rows), sum(1 for r in rows if r["states"]))
