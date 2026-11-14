"""scdb11 rule R3 (round 11; DESIGN7 section 6 scope rule on a remaining SCDB block, `partial`): a bare whole
disposition of a Supreme Court opinion that reviews one decision is a whole-case act.

    python -X utf8 r3scope11.py  -> replace_r3.tsv (13-column history rows, scope unknown -> all), work/r3_rows.tsv

Rule, general over every base (round10/stage/v10d) history row whose acting decision is a Supreme Court opinion
(the round-6 below_sc candidate list of round 10 covers it), kind reversed or vacated, scope unknown, when:
  - the disposition quote is a bare whole disposition with no limiting phrase: "Reversed.", "Judgment reversed.",
    "Decree reversed.", "The judgment is reversed.", "Reversed and remanded.", "Vacated and remanded.",
    "... and the case is remanded for further proceedings ..." (nothing else in the quote);
  - the Supreme Court opinion has review rows (reversed, vacated, affirmed, modified, reviewDismissed) on that one
    target only, and of that one kind only (no affirmed / dismissed row beside it: no several dockets, no partial
    judgment).
Then scope all (DESIGN7 section 6: a whole-case act with no limiting phrase).
No answer-key file is read.
"""
import collections, gzip, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
NL = chr(10)
BASE = os.path.join(C2, "round10", "stage", "v10d")
DIAG = os.path.join(C2, "round10", "agents", "scdb10", "work", "diag10_v5.jsonl.gz")
REVIEW = ("reversed", "vacated", "affirmed", "modified", "reviewDismissed")
BARE = re.compile(r"^\W*(?:(?:the\s+)?(?:judgment|decree)\s+(?:is\s+)?)?(?:reversed|vacated)"
                  r"(?:\s*,?\s*and\s+(?:the\s+)?(?:case|cause)?\s*(?:is\s+)?remanded"
                  r"(?:\s+(?:for\s+further\s+proceedings|to\s+the\s+\w+(?:\s+\w+){0,6}\s+court)[^.;]{0,60})?)?\W*$", re.I)
LIMIT = re.compile(r"in\s+part|insofar|to\s+the\s+extent|as\s+to|so\s+far|in\s+so\s+far", re.I)


def main():
    sc = set()
    with gzip.open(DIAG, "rt", encoding="utf-8") as f:
        for line in f:
            sc.add(json.loads(line)["n"])
    rows = collections.defaultdict(list)
    with open(os.path.join(BASE, "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if int(p[2]) in sc and p[4] in REVIEW:
                rows[int(p[2])].append(p)
    out = []
    st = collections.Counter()
    for by, rs in rows.items():
        for p in rs:
            if p[5] != "unknown" or p[4] not in ("reversed", "vacated"):
                continue
            q = p[9].strip()
            if not BARE.match(q) or LIMIT.search(q):
                continue
            if len({r[1] for r in rs}) > 1:
                st["several_targets"] += 1
                continue
            if len({r[4] for r in rs}) > 1:
                st["several_kinds"] += 1
                continue
            st["ok"] += 1
            np = list(p)
            np[5] = "all"
            out.append(np)
    with open(os.path.join(HERE, "replace_r3.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for p in out:
            f.write("\t".join(p) + NL)
    print(dict(st))


if __name__ == "__main__":
    main()
