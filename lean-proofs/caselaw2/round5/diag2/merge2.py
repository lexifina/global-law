"""diag2 final step: merge the shard JSONL files into dev_misses.tsv and print the summary counts.

    python merge2.py            reads shard_*.jsonl (+ fixes.jsonl, which overrides by idx), writes dev_misses.tsv

Every quote is re-verified against the cached text (verify.py rules); a line with a failed quote is reported.
`scan_findable`: the later span has one of the scanning forms
   "overrul* / abrogat* [in part] <X>"  (X within 80 characters after the word)   or
   "overruled / abrogated ... by | in <Y>" (Y within 90 characters after the word),
with X / Y a citation or a party-name token.
"""
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify as V  # noqa: E402
import dsearch as D  # noqa: E402

RC = D.RC
COLS = ["pair_id", "outcome", "by_node", "target_node", "names", "own_words", "own_type", "whole", "limiting_words",
        "scope_error", "model_scope", "later_W", "later_W_date", "later_span", "later_weak", "A", "B", "C", "D", "E",
        "primary", "fixable_by", "note",
        # extras
        "S", "scope_reason", "recall_reason", "later_form", "scan_findable", "own_offset", "key_partial",
        "key_implied", "sources", "idx"]


def clean(s):
    return str(s).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def refs(meta_row, extra_name):
    c = "|".join(D.cite_patterns(meta_row[5])) or r"(?!x)x"
    t = sorted(RC.name_tokens(meta_row[6]) | RC.name_tokens(extra_name), key=len, reverse=True)
    n = r"\b(?:%s)\b" % "|".join(re.escape(x) for x in t) if t else r"(?!x)x"
    return re.compile("(?:%s)|(?:%s)" % (c, n))


def scan_findable(span, xr, yr):
    for c in re.finditer(r"overrul\w*|abrogat\w*|over-\s?rul\w*", span, re.I):
        tail = span[c.end():c.end() + 80]
        if xr.search(tail):
            return "1:overruling X"
        m = re.match(r"\W{0,3}(?:in part |in effect |sub silentio )?(?:by|in)\b", span[c.end():c.end() + 30])
        if m and yr.search(span[c.end():c.end() + 90]):
            return "1:overruled by Y"
    return "0"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    with open(os.path.join(HERE, "pairs.tsv"), encoding="utf-8", newline="") as f:
        pairs = {r["idx"]: r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
    meta = D.load_meta()
    files = sorted(glob.glob(os.path.join(HERE, "shard_*.jsonl")))
    bad = sum(V.check(fn) for fn in files)
    got = {}
    for fn in files + ([os.path.join(HERE, "fixes.jsonl")] if os.path.exists(os.path.join(HERE, "fixes.jsonl")) else []):
        for line in open(fn, encoding="utf-8"):
            if line.strip():
                o = json.loads(line)
                got[str(o["idx"])] = o
    if os.path.exists(os.path.join(HERE, "fixes.jsonl")):
        bad += V.check(os.path.join(HERE, "fixes.jsonl"))
    missing = [i for i in pairs if i not in got]
    print("pairs", len(pairs), "answered", len(got), "missing idx", missing, "lines with problems", bad)
    out = []
    for idx in sorted(pairs, key=int):
        if idx not in got:
            continue
        pr, o = pairs[idx], got[idx]
        xr = refs(meta[pr["target_node"]], pr["target_name"])
        yr = refs(meta[pr["by_node"]], pr["label"])
        weak = ""
        if o.get("later_weak_span"):
            weak = "%s|%s|%s" % (o.get("later_weak_W", ""), o.get("later_weak_date", ""), o["later_weak_span"])
        row = {
            "pair_id": pr["pair_id"], "outcome": pr["outcome"], "by_node": pr["by_node"],
            "target_node": pr["target_node"],
            "names": "%s, %s (%s) => %s, %s (%s)" % (pr["label"], pr["by_cite"], pr["by_date"][:4], pr["target_name"],
                                                      pr["target_cite"], pr["target_date"][:4]),
            "own_words": o.get("own_words", ""), "own_type": o.get("own_type", ""), "whole": o.get("whole", ""),
            "limiting_words": o.get("limiting_words", ""), "scope_error": o.get("scope_error", ""),
            "model_scope": o.get("model_scope", ""), "later_W": o.get("later_W", ""),
            "later_W_date": o.get("later_W_date", ""), "later_span": o.get("later_span", ""), "later_weak": weak,
            "A": o.get("A", ""), "B": o.get("B", ""), "C": o.get("C", ""), "D": o.get("D", ""), "E": o.get("E", ""),
            "primary": o.get("primary", ""), "fixable_by": o.get("fixable_by", ""), "note": o.get("note", ""),
            "S": o.get("S", ""), "scope_reason": o.get("scope_reason", ""), "recall_reason": o.get("recall_reason", ""),
            "later_form": o.get("later_form", ""),
            "scan_findable": scan_findable(o["later_span"], xr, yr) if o.get("later_span") else "",
            "own_offset": o.get("own_offset", ""), "key_partial": pr["partial"], "key_implied": pr["implied"],
            "sources": pr["sources"], "idx": idx}
        out.append(row)
    with open(os.path.join(HERE, "dev_misses.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(COLS) + "\n")
        for r in out:
            f.write("\t".join(clean(r[c]) for c in COLS) + "\n")

    def tab(title, key, by="outcome"):
        c = defaultdict(Counter)
        for r in out:
            c[str(r[key])][r[by]] += 1
        print("\n" + title)
        for k in sorted(c, key=lambda k: -sum(c[k].values())):
            print("  %-16s c=%-3d d=%-3d e=%-3d total=%d" % (k or '""', c[k]["c"], c[k]["d"], c[k]["e"],
                                                             sum(c[k].values())))

    tab("fixable_by by outcome", "fixable_by")
    tab("primary by outcome", "primary")
    tab("own_type by outcome", "own_type")
    tab("whole by outcome", "whole")
    print("\nlabels (pairs with the label = 1), by outcome")
    for lab in ("S", "A", "B", "C", "D", "E"):
        c = Counter(r["outcome"] for r in out if r[lab] == 1)
        print("  %s c=%-3d d=%-3d e=%-3d total=%d" % (lab, c["c"], c["d"], c["e"], sum(c.values())))
    cs = [r for r in out if r["outcome"] == "c"]
    print("\nscope_error (outcome c):", dict(Counter(r["scope_error"] for r in cs)))
    print("model_scope kind (outcome c):", dict(Counter((r["model_scope"].split(":")[0] or "none") + "/" + r["scope_error"] for r in cs)))
    for r in cs:
        print("   %s %-9s %-28s | %s" % (r["idx"].rjust(3), r["scope_error"], r["model_scope"][:28], r["scope_reason"][:110]))
    print("\nreader_recall reasons:")
    for r in out:
        if r["fixable_by"] == "reader_recall":
            print("   %s %s | %s" % (r["idx"].rjust(3), r["outcome"], r["recall_reason"][:120]))
    d = [r for r in out if r["later_span"]]
    print("\nlater statement with both names:", len(d), dict(Counter(r["outcome"] for r in d)),
          "scan-findable:", dict(Counter(r["scan_findable"] for r in d)))
    print("later_form:", dict(Counter(r["later_form"] for r in d)))
    print("D by fixable_by:", dict(Counter(r["fixable_by"] for r in d)))
    print("weak only:", sum(1 for r in out if r["later_weak"] and not r["later_span"]))
    print("\ngold_doubtful:")
    for r in out:
        if r["fixable_by"] == "gold_doubtful":
            print("   %s %s %s | %s" % (r["idx"].rjust(3), r["outcome"], r["names"][:90], r["note"][:200]))


if __name__ == "__main__":
    main()
