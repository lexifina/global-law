import json, sys

OUT = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\ans_pack_T1f_019.jsonl"

# (id, states, reason_or_kind, ...) ; false entries: (id, False, reason)
F = [
("s02582","otherDecision"),
("s00955","notOverruling"),
("s00838","notOverruling"),
("s01549","refusal"),
("s01550","refusal"),
("s01217","notOverruling"),
("s00857","negation"),
("s01183","refusal"),
("s01541","negation"),
("s02032","quotation"),
("s00934","wrongDirection"),
("s00974","notOverruling"),
("s00890","notOverruling"),
("s00984","notOverruling"),
("s01160","notOverruling"),
("s01757","argument"),
("s02753","question"),
("s02309","ownAct"),
("s00926","notOverruling"),
("s00947","notOverruling"),
("s00868","notOverruling"),
("s00884","notOverruling"),
("s00918","notOverruling"),
("s00875","notOverruling"),
("s00885","notOverruling"),
("s00879","ownAct"),
("s01043","otherDecision"),
("s01061","otherDecision"),
("s01070","otherDecision"),
("s01501","otherDecision"),
("s01485","negation"),
("s00881","notOverruling"),
("s01063","notOverruling"),
("s01138","notOverruling"),
("s00877","notOverruling"),
("s01004","notOverruling"),
("s01005","notOverruling"),
("s00886","notOverruling"),
("s00882","notOverruling"),
("s00939","notOverruling"),
("s01202","wrongDirection"),
("s02143","wrongDirection"),
("s01768","notOverruling"),
("s01870","notOverruling"),
("s02432","notOverruling"),
("s00903","notOverruling"),
("s02310","notOverruling"),
("s02456","notOverruling"),
("s01006","notOverruling"),
("s01053","otherDecision"),
]

T = []  # true entries: (id, kind, scope, field_limit, doctrine, quote, confidence)

rows = []
for item_id, reason in F:
    rows.append({"id": item_id, "states": False, "reason": reason, "kind": "", "scope": "",
                 "field_limit": "", "doctrine": "", "quote": "", "confidence": 0.9})
for (item_id, kind, scope, fl, doc, quote, conf) in T:
    rows.append({"id": item_id, "states": True, "kind": kind, "scope": scope, "field_limit": fl,
                 "doctrine": doc, "quote": quote, "confidence": conf})

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(rows), sum(1 for r in rows if r["states"]))
