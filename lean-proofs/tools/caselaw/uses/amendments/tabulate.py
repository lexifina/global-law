"""Summaries of data/results.tsv -> out/summary.json, out/classes.tsv, and audit samples out/sample_<class>.tsv."""
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

csv.field_size_limit(10 ** 9)
HERE = Path(__file__).resolve().parents[1]
R = list(csv.DictReader(open(HERE / "data/results.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))


def cls(r):
    o = r["outcome"]
    if o == "applied":
        return {"1": "applied_matches", "0": "applied_record_differs"}.get(r["record_shows"], "applied_unchecked")
    return o


for r in R:
    r["cls"] = cls(r)
S = {}
S["operations"] = len(R)
S["laws"] = len({r["law"] for r in R})
S["instructions"] = len({(r["gid"], r["label"], r["path"]) for r in R})
S["by_class"] = Counter(r["cls"] for r in R).most_common()
S["by_class_and_record_status"] = sorted(Counter((r["cls"], r["law_commit"]) for r in R).items())
main = [r for r in R if r["law_commit"] in ("ok", "ok_multi")]
S["main_scope_note"] = "ops whose section has a commit by this law in the record (before and after both exist)"
S["main_by_class"] = Counter(r["cls"] for r in main).most_common()
S["main_by_kind_class"] = sorted(Counter((r["lean_kind"], r["cls"]) for r in main).items())
amb = [r for r in main if r["cls"] == "ambiguous"]
S["ambiguous_record_candidate"] = Counter(r["record_cand"] for r in amb).most_common()
S["ambiguous_candidates_differ"] = Counter(r["cands_differ"] for r in amb).most_common()
g = {}
for r in R:
    if r["group_replay_equal"] != "":
        g[r["gid"]] = (r["group_replay_equal"], r["law_commit"], r["law"])
S["groups"] = len(g)
S["groups_replay_equal_by_status"] = sorted(Counter((v[1], v[0]) for v in g.values()).items())
by_law = defaultdict(Counter)
for r in main:
    by_law[r["law"]][r["cls"]] += 1
S["laws_with_most_failures"] = sorted(((l, c["not_found"] + c["wrong_target"] + c["no_target"], sum(c.values())) for l, c in by_law.items()),
                                      key=lambda x: -x[1])[:15]
by_cong = defaultdict(Counter)
for r in main:
    by_cong[r["law"].split()[-1].split("-")[0]][r["cls"]] += 1
S["main_by_congress"] = {k: dict(v) for k, v in sorted(by_cong.items())}
(HERE / "out").mkdir(exist_ok=True)
json.dump(S, open(HERE / "out/summary.json", "w", encoding="utf-8", newline="\n"), indent=1, default=str)
print(json.dumps({k: S[k] for k in ("operations", "laws", "instructions", "by_class", "main_by_class",
                                    "ambiguous_record_candidate", "ambiguous_candidates_differ",
                                    "groups_replay_equal_by_status")}, indent=1, default=str))
if "--samples" in sys.argv:
    random.seed(20261112)
    cols = ["gid", "oid", "law", "title", "section", "path", "kind", "lean_kind", "law_commit", "label", "cls",
            "places", "record_cand", "args", "wording"]
    for c in ("wrong_target", "not_found", "ambiguous", "applied_record_differs", "no_target", "applied_matches"):
        pool = [r for r in main if r["cls"] == c]
        pick = random.sample(pool, min(20, len(pool)))
        with open(HERE / f"out/sample_{c}.tsv", "w", encoding="utf-8", newline="\n") as f:
            f.write("\t".join(cols) + "\n")
            for r in pick:
                f.write("\t".join(r[k] for k in cols) + "\n")
