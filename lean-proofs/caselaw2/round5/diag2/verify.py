"""diag2: check a shard JSONL. Every quote must be a substring of the cached text (newlines / tabs as spaces).

    python verify.py shard_1.jsonl [...]

Checks: one object per line with the required keys; idx / nodes match pairs.tsv; own_words in text/<Y>.md;
later_span in text/<later_W>.md, <= 400 characters, later_W_date after Y; later_weak_span in text/<later_weak_W>.md;
enumerated values.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = ["idx", "pair_id", "by_node", "target_node", "own_words", "own_offset", "own_type", "whole", "limiting_words",
        "scope_error", "scope_reason", "model_scope", "later_W", "later_W_date", "later_span", "later_form",
        "later_weak_W", "later_weak_date", "later_weak_span", "S", "A", "B", "C", "D", "E", "primary", "fixable_by",
        "recall_reason", "note"]
ENUM = {"own_type": {"overrule", "operative", "contrary", "doctrine", "none"},
        "whole": {"true", "false", "unclear"},
        "scope_error": {"yes", "no", "arguable", ""},
        "primary": {"S", "A", "B", "C", "D", "E"},
        "fixable_by": {"scope_fix", "reader_recall", "recognised", "operative", "doctrine_field", "none",
                       "gold_doubtful"}}
_T = {}


def norm(s):
    return s.replace("\r\n", "\n").replace("\n", " ").replace("\t", " ").replace("\x0c", " ")


def text(node):
    node = str(node)
    if node not in _T:
        p = os.path.join(HERE, "text", node + ".md")
        _T[node] = norm(open(p, encoding="utf-8", newline="").read()) if os.path.exists(p) else None
    return _T[node]


def check(fn):
    with open(os.path.join(HERE, "pairs.tsv"), encoding="utf-8", newline="") as f:
        pairs = {r["idx"]: r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
    bad = 0
    n = 0
    seen = set()
    for ln, line in enumerate(open(fn, encoding="utf-8"), 1):
        if not line.strip():
            continue
        n += 1
        try:
            o = json.loads(line)
        except Exception as e:  # noqa: BLE001
            print("%s:%d not JSON: %s" % (fn, ln, e))
            bad += 1
            continue
        errs = []
        miss = [k for k in KEYS if k not in o]
        if miss:
            errs.append("missing keys %s" % miss)
        idx = str(o.get("idx"))
        pr = pairs.get(idx)
        if not pr:
            errs.append("unknown idx")
        else:
            if idx in seen:
                errs.append("duplicate idx")
            seen.add(idx)
            if str(o.get("by_node")) != pr["by_node"] or str(o.get("target_node")) != pr["target_node"]:
                errs.append("nodes differ from pairs.tsv")
            if pr["outcome"] == "c" and o.get("scope_error", "") == "":
                errs.append("outcome c needs scope_error")
        for k, vals in ENUM.items():
            if k in o and str(o[k]).lower() not in {v.lower() for v in vals}:
                errs.append("%s=%r not allowed" % (k, o[k]))
        for k in ("S", "A", "B", "C", "D", "E"):
            if k in o and o[k] not in (0, 1):
                errs.append("%s must be 0/1" % k)
        ow = o.get("own_words", "")
        if ow:
            t = text(o.get("by_node"))
            if t is None:
                errs.append("no cached text for Y")
            elif norm(ow) not in t:
                errs.append("own_words NOT in Y text")
        elif o.get("own_type") not in ("none", None):
            errs.append("own_type %s without own_words" % o.get("own_type"))
        ls = o.get("later_span", "")
        if ls:
            t = text(o.get("later_W"))
            if t is None:
                errs.append("no cached text for later_W %s" % o.get("later_W"))
            elif norm(ls) not in t:
                errs.append("later_span NOT in W text")
            if len(ls) > 400:
                errs.append("later_span %d chars > 400" % len(ls))
            if pr and str(o.get("later_W_date", "")) <= pr["by_date"]:
                errs.append("later_W_date not after Y")
            if o.get("D") != 1:
                errs.append("later_span given but D != 1")
        elif o.get("D") == 1:
            errs.append("D = 1 without later_span")
        lw = o.get("later_weak_span", "")
        if lw:
            t = text(o.get("later_weak_W"))
            if t is None:
                errs.append("no cached text for later_weak_W %s" % o.get("later_weak_W"))
            elif norm(lw) not in t:
                errs.append("later_weak_span NOT in W text")
        if errs:
            bad += 1
            print("%s:%d idx %s: %s" % (fn, ln, idx, "; ".join(errs)))
    print("%s: %d lines, %d with problems" % (fn, n, bad))
    return bad


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    tot = sum(check(a) for a in sys.argv[1:])
    sys.exit(1 if tot else 0)
