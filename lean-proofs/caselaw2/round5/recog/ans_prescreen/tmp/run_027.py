import sys
sys.path.insert(0, r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\tmp")
from common import write_pack, parse

PK = "pack_T1f_027"

R = [
    ("s01507", "wrongDirection"), ("s01747", "notOverruling"), ("s03661", "notOverruling"),
    ("s01575", "negation"), ("s01759", "notOverruling"), ("s01444", "wrongDirection"),
    ("s01465", "notOverruling"), ("s01889", "negation"), ("s01998", "notOverruling"),
    ("s02053", "otherDecision"), ("s02893", "otherDecision"), ("s02183", "otherDecision"),
    ("s02278", "notOverruling"), ("s02317", "otherDecision"), ("s01659", "notOverruling"),
    ("s02107", "otherDecision"), ("s02496", "notOverruling"), ("s01589", "notOverruling"),
    ("s01418", "notOverruling"), ("s01426", "notOverruling"), ("s01427", "notOverruling"),
    ("s02249", "quotation"), ("s02607", "quotation"), ("s01572", "notOverruling"),
    ("s01687", "notOverruling"), ("s02279", "notOverruling"), ("s02609", "notOverruling"),
    ("s02713", "notOverruling"), ("s02959", "notOverruling"), ("s03098", "argument"),
    ("s03217", "notOverruling"), ("s01463", "notOverruling"),
    ("s01647", "otherDecision"), ("s01699", "otherDecision"),
    ("s01515", "otherDecision"), ("s02819", "otherDecision"),
    ("s01836", "otherDecision"), ("s01481", "question"), ("s01734", "argument"),
    ("s01598", "notOverruling"), ("s03063", "notMajority"), ("s03512", "notMajority"),
    ("s01456", "notOverruling"), ("s01489", "notOverruling"), ("s02212", "notOverruling"),
    ("s02499", "notOverruling"),
]
byid = {i: {"id": i, "states": False, "reason": r, "conf": 0.9} for i, r in R}

byid["s01616"] = {
    "id": "s01616", "states": True, "kind": "overruled", "scope": "partialUnknown",
    "field_limit": "to the extent that it failed to apply the exclusionary rule to the States",
    "doctrine": "",
    "quote": "Mapp v. Ohio, 367 U. S. 643 (1961), we held that the exclusion of evidence seized in violation of the search and seizure provisions of the Fourth Amendment was required of the States by the Due Process Clause of the Fourteenth Amendment. In so doing we overruled Wolf v. Colorado, 338 U. S. 25 (1949), to the extent that it failed to apply the exclusionary rule to the States.",
    "conf": 0.85, "xkeys": ["Wolf v. Colorado"], "ykeys": ["Mapp v. Ohio"],
}
byid["s02401"] = {
    "id": "s02401", "states": True, "kind": "overruled", "scope": "all", "field_limit": "",
    "doctrine": "",
    "quote": "In Burks we held that once a defendant obtained an unreversed appellate ruling that the Government had failed to introduce sufficient evidence to convict him at trial, a second trial was barred by the Double Jeopardy Clause. Id., at 18. We overruled prior decisions such as Bryan v. United States, 338 U. S. 552 (1950)",
    "conf": 0.75, "xkeys": ["Bryan v. United States"], "ykeys": ["Burks"],
}
byid["s01653"] = {
    "id": "s01653", "states": True, "kind": "overruled", "scope": "all", "field_limit": "",
    "doctrine": "",
    "quote": "Darr v. Burford, 339 U. S. 200, 204-206 (1950), and the case which overruled it, Fay v. Noia, 372 U. S. 391, 417-420 (1963)",
    "conf": 0.8, "xkeys": ["Darr v. Burford"], "ykeys": ["Fay v. Noia"],
}
byid["s02108"] = {
    "id": "s02108", "states": True, "kind": "overruled", "scope": "partialUnknown", "field_limit": "",
    "doctrine": "the statutory predicate to Eisentrager's holding",
    "quote": "Because Braden overruled the statutory predicate to Ei-sentrager’s holding, Eisentrager plainly does not preclude",
    "conf": 0.5, "xkeys": ["Eisentrager"], "ykeys": ["Braden"],
}

ordered = [byid[i] for i in parse(PK)[1]]
write_pack(PK, ordered)
