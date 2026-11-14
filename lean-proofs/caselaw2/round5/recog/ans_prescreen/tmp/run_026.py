import sys
sys.path.insert(0, r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\tmp")
from common import check_and_write

R = [
    ("s01346", "cannotTell"), ("s02253", "wrongDirection"), ("s02699", "notOverruling"),
    ("s03147", "notOverruling"), ("s01662", "negation"), ("s01522", "otherDecision"),
    ("s01523", "otherDecision"), ("s01524", "otherDecision"), ("s02339", "otherDecision"),
    ("s02461", "otherDecision"), ("s02462", "otherDecision"), ("s01810", "notOverruling"),
    ("s01400", "notOverruling"), ("s02489", "notOverruling"), ("s01646", "otherDecision"),
    ("s01365", "ownAct"), ("s02369", "negation"), ("s01452", "notOverruling"),
    ("s01453", "wrongDirection"), ("s01454", "otherDecision"), ("s02313", "notOverruling"),
    ("s03506", "notOverruling"), ("s01495", "otherDecision"), ("s02315", "ownAct"),
    ("s01383", "wrongDirection"), ("s01436", "otherDecision"), ("s01437", "otherDecision"),
    ("s02528", "notOverruling"), ("s02737", "notOverruling"), ("s01578", "quotation"),
    ("s01607", "refusal"), ("s01796", "refusal"), ("s01363", "notOverruling"),
    ("s01971", "negation"), ("s02943", "notOverruling"), ("s01441", "argument"),
    ("s01442", "argument"), ("s01676", "otherDecision"), ("s01864", "quotation"),
    ("s01822", "notOverruling"), ("s01823", "notOverruling"), ("s01920", "notOverruling"),
    ("s01921", "notOverruling"), ("s01899", "notOverruling"), ("s02547", "negation"),
    ("s02676", "negation"), ("s02073", "negation"), ("s01476", "notOverruling"),
]
answers = [{"id": i, "states": False, "reason": r, "confidence": 0.9} for i, r in R]

# s01697: Malloy (Y) overruled Adamson (X) in the court's own voice.
# s01947: Chimel (Y) overruled Harris (X), stated in the court's citation parenthetical.
answers = [a for a in answers if a["id"] not in ("s01697", "s01947")]
answers.append({
    "id": "s01697", "states": True, "kind": "overruled", "scope": "all", "field_limit": "",
    "doctrine": "",
    "quote": "The Malloy case overruled Twining v. New Jersey, 211 U. S. 78, and Adamson v. California, 332 U. S. 46",
    "confidence": 0.9, "names": ["Malloy", "Adamson v. California"],
})
answers.append({
    "id": "s01947", "states": True, "kind": "overruled", "scope": "all", "field_limit": "",
    "doctrine": "",
    "quote": "Chimel v. California, 395 U. S. 752 (1969), which overruled United States v. Rabinowitz, 339 U. S. 56 (1950), and Harris v. United States, 331 U. S. 145 (1947)",
    "confidence": 0.65, "names": ["Chimel", "Harris v. United States"],
})
check_and_write("pack_T1f_026.md", answers)
