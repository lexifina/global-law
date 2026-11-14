import json
import os

base = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen"
out = os.path.join(base, "ans_pack_T1f_046.jsonl")
os.makedirs(base, exist_ok=True)

# (item id, reason) in pack order; every item is states: false (no statement of X overruled by Y)
rows = [
    ("s03525", "notOverruling"),
    ("s03464", "notOverruling"),
    ("s03282", "cannotTell"),
    ("s03322", "quotation"),
    ("s03286", "negation"),
    ("s03555", "negation"),
    ("s03290", "notOverruling"),
    ("s03318", "notOverruling"),
    ("s03327", "notOverruling"),
    ("s03351", "notOverruling"),
    ("s03372", "notOverruling"),
    ("s03377", "notOverruling"),
    ("s03389", "notOverruling"),
    ("s03390", "notOverruling"),
    ("s03417", "notOverruling"),
    ("s03534", "notOverruling"),
    ("s03708", "notOverruling"),
    ("s03717", "notOverruling"),
    ("s03297", "notOverruling"),
    ("s03485", "notOverruling"),
    ("s03556", "negation"),
    ("s03654", "argument"),
    ("s03544", "notOverruling"),
    ("s03355", "notOverruling"),
    ("s03465", "notOverruling"),
    ("s03697", "notOverruling"),
    ("s03341", "notOverruling"),
    ("s03582", "notOverruling"),
    ("s03403", "notOverruling"),
    ("s03428", "quotation"),
    ("s03677", "notMajority"),
    ("s03437", "notOverruling"),
    ("s03426", "notOverruling"),
    ("s03353", "refusal"),
    ("s03557", "negation"),
    ("s03430", "quotation"),
    ("s03392", "negation"),
    ("s03391", "notOverruling"),
    ("s03393", "negation"),
    ("s03478", "notOverruling"),
    ("s03394", "notOverruling"),
    ("s03418", "notOverruling"),
    ("s03479", "notOverruling"),
    ("s03625", "notOverruling"),
    ("s03635", "notOverruling"),
    ("s03636", "notOverruling"),
    ("s03709", "notOverruling"),
    ("s03723", "notOverruling"),
    ("s03466", "notOverruling"),
    ("s03451", "wrongDirection"),
]

with open(out, "w", encoding="utf-8", newline="\n") as f:
    for item_id, reason in rows:
        obj = {
            "id": item_id,
            "states": False,
            "reason": reason,
            "kind": "",
            "scope": "",
            "field_limit": "",
            "doctrine": "",
            "quote": "",
            "confidence": 0.9,
        }
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

print("rows", len(rows), "true", 0)
