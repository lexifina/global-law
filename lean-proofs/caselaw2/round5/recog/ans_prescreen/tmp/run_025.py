import sys
sys.path.insert(0, r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\tmp")
from common import write_pack, parse

R = [
    ("s01293", "cannotTell"), ("s01308", "notOverruling"), ("s01316", "notOverruling"),
    ("s02368", "negation"), ("s01554", "otherDecision"), ("s01566", "cannotTell"),
    ("s01773", "argument"), ("s03356", "cannotTell"), ("s01393", "notOverruling"),
    ("s01397", "wrongDirection"), ("s01440", "quotation"), ("s01503", "notOverruling"),
    ("s02333", "cannotTell"), ("s03011", "wrongDirection"), ("s03095", "notOverruling"),
    ("s03664", "wrongDirection"), ("s01526", "cannotTell"), ("s01406", "notOverruling"),
    ("s01423", "wrongDirection"), ("s01479", "notOverruling"), ("s01742", "notOverruling"),
    ("s02530", "refusal"), ("s02657", "notOverruling"), ("s03018", "wrongDirection"),
    ("s03096", "notOverruling"), ("s03097", "notOverruling"), ("s01358", "otherDecision"),
    ("s01685", "wrongDirection"), ("s01565", "otherDecision"), ("s01317", "notOverruling"),
    ("s01682", "notOverruling"), ("s01600", "wrongDirection"), ("s01774", "notOverruling"),
    ("s01581", "notOverruling"), ("s01504", "otherDecision"), ("s01353", "ownAct"),
    ("s03487", "negation"), ("s01319", "argument"), ("s01320", "argument"),
    ("s01535", "wrongDirection"), ("s01857", "notOverruling"), ("s02568", "notOverruling"),
    ("s02966", "notOverruling"), ("s01331", "notOverruling"), ("s01431", "quotation"),
    ("s01375", "notOverruling"), ("s01875", "cannotTell"), ("s01876", "wrongDirection"),
    ("s02077", "cannotTell"), ("s02232", "notOverruling"),
]
answers = [{"id": i, "states": False, "reason": r, "confidence": 0.9} for i, r in R]
PK = "pack_T1f_025"
byid = {a["id"]: a for a in answers}
ordered = [byid[i] for i in parse(PK)[1]]
write_pack(PK, ordered)
