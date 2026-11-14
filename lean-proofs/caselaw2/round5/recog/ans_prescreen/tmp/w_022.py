import json

OUT = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\ans_pack_T1f_022.jsonl"

PACK_ORDER = [
"s01345","s01018","s01033","s03344","s01141","s01040","s01034","s01964","s01713","s01530",
"s01882","s01883","s01884","s02469","s02566","s01190","s01210","s02329","s02669","s01127",
"s01844","s01048","s01321","s01330","s01268","s01182","s01334","s01602","s01327","s01374",
"s01062","s01337","s01767","s02574","s01218","s01235","s01299","s01303","s01758","s03001",
"s01516","s02210","s02311","s01119","s02330","s02584","s01057","s02144","s01185","s01188",
]

F = {
"s01345": "quotation",
"s01018": "notOverruling",
"s01033": "notOverruling",
"s03344": "would",
"s01141": "notOverruling",
"s01040": "notOverruling",
"s01034": "notOverruling",
"s01964": "notOverruling",
"s01713": "notOverruling",
"s01530": "notOverruling",
"s01882": "notOverruling",
"s01883": "notOverruling",
"s01884": "notOverruling",
"s02469": "notOverruling",
"s02566": "notOverruling",
"s01190": "notOverruling",
"s01210": "notOverruling",
"s02329": "notOverruling",
"s02669": "notOverruling",
"s01127": "ownAct",
"s01844": "ownAct",
"s01048": "notOverruling",
"s01321": "notOverruling",
"s01330": "notOverruling",
"s01268": "ownAct",
"s01182": "notOverruling",
"s01334": "wrongDirection",
"s01602": "notOverruling",
"s01327": "notOverruling",
"s01374": "notOverruling",
"s01062": "notOverruling",
"s01337": "notOverruling",
"s01767": "notOverruling",
"s02574": "notOverruling",
"s01218": "otherDecision",
"s01235": "otherDecision",
"s01303": "ownAct",
"s01758": "otherDecision",
"s03001": "notOverruling",
"s01516": "argument",
"s02210": "argument",
"s02311": "argument",
"s01119": "notOverruling",
"s02330": "notOverruling",
"s02584": "notOverruling",
"s01057": "would",
"s02144": "wrongDirection",
"s01185": "notOverruling",
}

# (id, kind, scope, field_limit, doctrine, quote, confidence)
T = [
("s01299", "overruled", "all", "", "",
 "Grovey was overruled and the Court decided that the resolution adopted by the party’s state convention constituted state action violative of the Fifteenth Amendment even though it was not expressly authorized by statute. Smith v. Allwright, 321 U. S. 649 (1944).", 0.7),
("s01188", "overruled", "all", "", "",
 "These cases were expressly overruled by Helvering v. Hallock. Helvering v. Hallock was decided in 1940. Three separate trusts were considered in the Hallock case. These three trusts as those considered in the St. Louis Trust and Becker cases", 0.7),
]

rows = {}
for i in PACK_ORDER:
    if i in F:
        rows[i] = {"id": i, "states": False, "reason": F[i], "kind": "", "scope": "",
                   "field_limit": "", "doctrine": "", "quote": "", "confidence": 0.9}
for (i, kind, scope, fl, doc, quote, conf) in T:
    rows[i] = {"id": i, "states": True, "kind": kind, "scope": scope, "field_limit": fl,
               "doctrine": doc, "quote": quote, "confidence": conf}

assert len(rows) == 50 == len(PACK_ORDER) == len(set(PACK_ORDER)), (len(rows), len(PACK_ORDER))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for i in PACK_ORDER:
        f.write(json.dumps(rows[i], ensure_ascii=False) + "\n")
print(len(rows), sum(1 for r in rows.values() if r["states"]))
