"""Cross-check our classes against OLRC's notes ("could not be executed", "probable intent").

For each (title, section, law) OLRC flags, what did the Lean run say about that law's operations on that section? And
of our failures, how many does OLRC flag? Laws up to the 118th Congress (the 2024 edition's notes stop there)."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

csv.field_size_limit(10 ** 9)
HERE = Path(__file__).resolve().parents[1]
notes = defaultdict(set)
note_text = {}
for r in csv.DictReader(open(HERE / "data/olrc_notes.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
    k = (r["title"], r["section"], r["law"])
    notes[k].add(r["kind"])
    note_text[(k, r["kind"])] = r["note"]
R = list(csv.DictReader(open(HERE / "data/results.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
FAIL = {"not_found", "wrong_target", "ambiguous", "no_target"}


def cls(r):
    o = r["outcome"]
    if o == "applied":
        return {"1": "applied_matches", "0": "applied_record_differs"}.get(r["record_shows"], "applied_unchecked")
    return o


groups = defaultdict(list)
for r in R:
    c = int(r["law"].split()[-1].split("-")[0])
    if c <= 118 and r["law_commit"] in ("ok", "ok_multi", "no_law_commit"):
        groups[(r["title"], r["section"], r["law"])].append(cls(r))
out = {}
for kind in ("not_executed", "probable_intent"):
    flagged = [k for k, v in notes.items() if kind in v and k in groups]
    hit = [k for k in flagged if any(c in FAIL or c == "applied_record_differs" for c in groups[k])]
    out[kind] = {"olrc_flagged_groups_in_our_run": len(flagged),
                 "we_flag_some_op_in_group": len(hit),
                 "our_classes_in_those_groups": Counter(c for k in flagged for c in groups[k]).most_common()}
ours = [k for k, v in groups.items() if any(c in FAIL for c in v)]
out["our_failure_groups"] = len(ours)
out["of_which_olrc_noted"] = sum(1 for k in ours if k in notes)
out["groups_total"] = len(groups)
out["groups_olrc_noted_any"] = sum(1 for k in groups if k in notes)
json.dump(out, open(HERE / "out/olrc_xcheck.json", "w", encoding="utf-8", newline="\n"), indent=1)
print(json.dumps(out, indent=1))
# examples where OLRC says not executed and we agree
with open(HERE / "out/olrc_agree_examples.tsv", "w", encoding="utf-8", newline="\n") as f:
    for k, v in groups.items():
        if "not_executed" in notes.get(k, ()) and any(c in ("not_found", "wrong_target", "no_target") for c in v):
            f.write("\t".join(k) + "\t" + ",".join(v) + "\t" + note_text[(k, "not_executed")] + "\n")
