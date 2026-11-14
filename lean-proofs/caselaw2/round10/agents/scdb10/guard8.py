# scdb8 copy (via round-7 b4sc) of round6/history/rules/guard/vx_guard.py (paths only)
"""Apply the KEPT guard (guard.rules_of, gaudit.groups_of, kept.py; unchanged) to the round-6 v1 delta rows.

    python -X utf8 gfeat.py --base ../../snap/cert_v1/history_delta.tsv --tag v1_
    python -X utf8 v1_guard.py
Writes v1_flags.tsv, v1_drop_ids.txt, V1_GUARD.md.
"""
import collections, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "round6", "history", "rules", "guard")
sys.path.insert(0, os.path.dirname(os.path.dirname(GD)))
sys.path.insert(0, GD)
import guard as G  # noqa: E402
import gaudit  # noqa: E402
import r6lib as L  # noqa: E402
from kept import KEPT_GROUPS, KEPT_GROUPS_AFF  # noqa: E402

NL = chr(10)
TAG = sys.argv[1] if len(sys.argv) > 1 else "v1"
DELTA = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "..", "snap", "cert_v1", "history_delta.tsv")


def main():
    src = {}
    kinds = collections.Counter()
    for l in open(DELTA, encoding="utf-8"):
        p = l.rstrip(NL).split("\t")
        src[p[0]] = p[12]
        kinds[(p[12], p[4])] += 1
    F = G.facts()
    rows = [json.loads(l) for l in gzip.open(os.path.join(HERE, "work", "guard", TAG + "_features.jsonl.gz"), "rt", encoding="utf-8")]
    cnt = collections.Counter()
    feat = collections.Counter()
    drop = []
    with open(os.path.join(HERE, "work", "guard", TAG + "_flags.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("id\tsrc\trule\tgroups\tkept_groups\tkind\tsystem\tevidence\toffset\n")
        for r in rows:
            s = src[r["id"]]
            fed = "federal" if F.system(r["cD"]) == 0 else "state"
            rs = G.rules_of(r)
            groups = set(gaudit.groups_of(r, {x[0] for x in rs}))
            kept = groups & (KEPT_GROUPS_AFF if r["kind"] == "affirmed" else KEPT_GROUPS)
            feat[(s, "T cited in D" if r["tocc"] else "T not cited (name evidence)")] += 1
            for rid, ev, off in rs:
                f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%d\n" % (r["id"], s, rid, ",".join(sorted(groups)),
                        ",".join(sorted(kept)), r["kind"], fed, L.norm(ev), off))
            if kept:
                drop.append(r["id"])
                cnt[(s, r["kind"], "REMOVED")] += 1
                for g in kept:
                    cnt[(s, r["kind"], g)] += 1
    with open(os.path.join(HERE, "work", "guard", TAG + "_drop_ids.txt"), "w", encoding="utf-8", newline=NL) as f:
        f.write(NL.join(drop) + (NL if drop else ""))
    groups = sorted({k[2] for k in cnt if k[2] != "REMOVED"})
    out = ["# Guard over the round-6 v1 rows (`snap/cert_v1/history_delta.tsv`)", "",
           "Rules unchanged (`guard.rules_of`, `gaudit.groups_of`, `kept.py`), run by `v1_guard.py` on features from "
           "`gfeat.py --base ../../snap/cert_v1/history_delta.tsv --tag v1_`. Guarded kinds only (reversed, vacated, "
           "affirmed); the delta has no withdrawn / en banc rows; certDenied, reviewDismissed, modified are not guarded.",
           "", "Rows with features: %d; removed by a kept group: **%d** (`v1_drop_ids.txt`). `v1_flags.tsv` lists every "
           "rule that fires (also the not-kept ones) with groups and kept groups." % (len(rows), len(drop)), "",
           "## Removed rows by src rule x kind x kept group (a row can count in several groups)", "",
           "| src | kind | rows | removed | " + " | ".join(groups) + " |",
           "|---|---|---|---|" + "---|" * len(groups)]
    for (s, k), n in sorted(kinds.items()):
        if k not in ("reversed", "vacated", "affirmed"):
            continue
        out.append("| %s | %s | %d | %d | %s |" % (s, k, n, cnt[(s, k, "REMOVED")],
                                                   " | ".join(str(cnt[(s, k, g)]) for g in groups)))
    out += ["", "## Feature check: is the target cited in the acting decision's text?", "",
            "| src | T cited in D | T not cited (name evidence) |", "|---|---|---|"]
    for s in sorted({k[0] for k in feat}):
        out.append("| %s | %d | %d |" % (s, feat[(s, "T cited in D")], feat[(s, "T not cited (name evidence)")]))
    out += ["", "Where T is not cited in D (memo orders linked by caption), the wording rules (b-earlier, f-other-signal) "
            "cannot fire; d-own, d-peer, d-gap5 use only courts and dates; a-same-later / a-own-denied use D's other "
            "citations. The audit precision of the kept groups was measured on base rows (RULES.md), not on these."]
    with open(os.path.join(HERE, "work", "guard", TAG.upper() + "_GUARD.md"), "w", encoding="utf-8", newline=NL) as f:
        f.write(NL.join(out) + NL)
    print(NL.join(out))


if __name__ == "__main__":
    main()
