import json
import os

base = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen"
out = os.path.join(base, "ans_pack_T1f_047.jsonl")
os.makedirs(base, exist_ok=True)

F = "false"
# (item id, reason) for states: false, in pack order
rows = [
    ("s03467", "notOverruling"),
    ("s03468", "notOverruling"),
    ("s03469", "notOverruling"),
    ("s03639", "notMajority"),
    ("s03648", "notOverruling"),
    ("s03680", "notOverruling"),
    ("s03686", "notOverruling"),
    ("s03628", "argument"),
    ("s03519", "notOverruling"),
    ("s03640", "notMajority"),
    ("s03626", "notOverruling"),
    ("s03724", "notOverruling"),
    ("s03611", "notOverruling"),
    ("s03668", "argument"),
    ("s03470", "notOverruling"),
    ("s03598", "otherDecision"),
    # s03612 is the one true item, handled below
    ("s03530", "question"),
    ("s03511", "notOverruling"),
    ("s03541", "notOverruling"),
    ("s03542", "notOverruling"),
    ("s03545", "notOverruling"),
    ("s03588", "notOverruling"),
    ("s03603", "notOverruling"),
    ("s03527", "notOverruling"),
    ("s03655", "notOverruling"),
    ("s03656", "cannotTell"),
    ("s03630", "ownAct"),
    ("s03672", "notOverruling"),
    ("s03613", "notOverruling"),
    ("s03614", "notOverruling"),
    ("s03669", "notOverruling"),
    ("s03651", "cannotTell"),
    ("s03670", "notOverruling"),
    ("s03718", "notOverruling"),
    ("s03725", "notOverruling"),
    ("s03675", "negation"),
    ("s03681", "notOverruling"),
    ("s03687", "notOverruling"),
    ("s03674", "notOverruling"),
    ("s03699", "notOverruling"),
    ("s03714", "notOverruling"),
    ("s03698", "notOverruling"),
    ("s03702", "notOverruling"),
    ("s03710", "notOverruling"),
    ("s03703", "notOverruling"),
    ("s03715", "notOverruling"),
]

TRUE_ITEM = "s03612"
TRUE_QUOTE = ("Citizens United v. Federal Election Comm’n, 558 U. S. 310 (2010) (right to engage in "
              "campaign-related speech), overruling Austin v. Michigan Chamber of Commerce, 494 U. S. 652 "
              "(1990), and partially overruling McConnell v. Federal Election Comm’n, 540 U. S. 93 (2003)")

# Insert the true item at its pack position (after s03598, before s03530).
ordered = []
for item_id, reason in rows:
    ordered.append((item_id, reason))
    if item_id == "s03598":
        ordered.append((TRUE_ITEM, None))

with open(out, "w", encoding="utf-8", newline="\n") as f:
    for item_id, reason in ordered:
        if reason is None:
            obj = {
                "id": item_id,
                "states": True,
                "kind": "overruled",
                "scope": "partialUnknown",
                "field_limit": "",
                "doctrine": "",
                "quote": TRUE_QUOTE,
                "confidence": 0.85,
            }
        else:
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

print("rows", len(ordered), "true", sum(1 for _, r in ordered if r is None))
