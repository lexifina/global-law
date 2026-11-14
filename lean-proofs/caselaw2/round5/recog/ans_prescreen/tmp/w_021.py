import json

OUT = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\ans_pack_T1f_021.jsonl"

PACK_ORDER = [
"s00983","s01173","s01047","s01056","s01274","s01364","s00967","s01557","s01720","s02057",
"s01657","s01517","s01377","s01015","s01140","s01159","s02088","s00996","s02600","s01028",
"s01448","s01514","s01712","s01013","s03343","s02366","s01174","s01177","s01203","s01288",
"s01161","s01472","s01012","s01017","s01038","s01116","s01135","s02165","s02352","s03300",
"s01025","s01067","s02495","s01224","s01265","s01612","s01379","s02121","s01881","s02468",
]

F = {
"s00983": "notOverruling",
"s01173": "notOverruling",
"s01047": "would",
"s01056": "would",
"s01274": "quotation",
"s01364": "notOverruling",
"s00967": "notOverruling",
"s01557": "notOverruling",
"s01720": "notOverruling",
"s02057": "notMajority",
"s01657": "notOverruling",
"s01517": "quotation",
"s01377": "notOverruling",
"s01015": "notOverruling",
"s01140": "notOverruling",
"s01159": "notOverruling",
"s02088": "negation",
"s00996": "wrongDirection",
"s02600": "notOverruling",
"s01028": "otherDecision",
"s01448": "otherDecision",
"s01514": "argument",
"s01013": "would",
"s03343": "would",
"s02366": "notOverruling",
"s01174": "ownAct",
"s01177": "ownAct",
"s01203": "otherDecision",
"s01288": "otherDecision",
"s01161": "notOverruling",
"s01472": "notOverruling",
"s01012": "otherDecision",
"s01017": "ownAct",
"s01038": "ownAct",
"s01116": "notOverruling",
"s01135": "otherDecision",
"s02165": "notOverruling",
"s02352": "notOverruling",
"s03300": "quotation",
"s01025": "notOverruling",
"s01067": "negation",
"s02495": "notOverruling",
"s01224": "notOverruling",
"s01265": "wrongDirection",
"s01612": "notOverruling",
"s01379": "notOverruling",
"s02121": "notOverruling",
"s01881": "notOverruling",
"s02468": "notOverruling",
}

# (id, kind, scope, field_limit, doctrine, quote, confidence)
T = [
("s01712", "disapproved", "otherGrounds", "", "",
 "United States v. Murdock, 284 U. S. 141 (1931) (Murdock I), disapproved on other grounds, Murphy v. Waterfront Comm’n, 378 U. S. 52 (1964)", 0.75),
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
