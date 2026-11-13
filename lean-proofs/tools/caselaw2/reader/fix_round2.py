"""Round 2 repairs of existing treatment rows that the checker rejected for a reason the row itself can cure.

    python -X utf8 fix_round2.py --in treatments.tsv --cert-text cert_text.tsv --out treatments.fixed.tsv --log changes.tsv

Only rows the checker does not admit today are touched (round2/recall.md, class c); admitted rows stay as they are.

A  name evidence in the checker's form. The checker compares whole words of letters and digits, so `name:Meraz-Valeta`
   or `name:O'Brien` never matched ("meraz", "valeta"). The evidence becomes `name:Meraz Valeta` (every word of 3+
   characters must be in the quote or window), when those words are in the window.
B  "X will no longer be followed" / "we will no longer follow X" / "we no longer adhere to X" labelled
   declinedToFollow: the v1 prompt defines this as `overruled` "when X is this court's own precedent or one it has
   power over". The label is changed to overruled when the treating court is the target's own court or a higher court
   of the same system (court table of the graph); otherwise the row stays declinedToFollow.
C  a disqualifier phrase inside the quote of a genuine act ("the law as stated in Wells ... and Moody must be
   overruled", "implicitly overruled by Mears and are now explicitly overruled"): the quote is cut to the clause that
   holds the act, when that clause alone is act-shaped (rules.act_shaped / rules2.shapes) and has no disqualifier.
"""
import argparse, collections, os, re, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, WORK  # noqa: E402
import rules, rules2  # noqa: E402
from certify2 import checker_name  # noqa: E402

STATUS = {"overruled", "disapproved", "recededFrom", "abrogated", "supersededByEnactment"}
FAM = {"overruled": ["overrule", "repudiate"], "disapproved": ["disapprove"], "recededFrom": ["recede"],
       "abrogated": ["abrogate"]}
NOLONGER = re.compile(r"no\s+longer\s+(?:be\s+)?follow|no\s+longer\s+adhere", re.I)
TIER_RANK = {"L": 3, "A": 2, "B": 2, "D": 2, "T": 1, "S": 1}
CLAUSE = re.compile(r"[;,:]\s+|\s+and\s+|\s+but\s+|\.\s+(?=[A-Z])")


def words(s):
    return set(re.findall(r"[0-9a-z]+", s.lower()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--cert-text", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    rows = [l.rstrip("\n").split("\t") for l in open(a.inp, encoding="utf-8", newline="\n")]
    need = {r[8] for r in rows}
    wins = collections.defaultdict(list)
    with open(a.cert_text, "rb") as f:
        for line in f:
            p = line.rstrip(b"\n").decode("utf-8").split("\t", 3)
            if len(p) == 4 and p[0] in need:
                wins[p[0]].append((int(p[1]), int(p[2]), p[3]))
    court = np.load(os.path.join(WORK, "node_court.npy"))
    cname, tier, system = {}, {}, {}
    for line in open(os.path.join(W, "graph", "courts.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        cname[int(f[0])] = f[1]
    by_name = {}
    for line in open(os.path.join(W, "lean-in-v3", "courts_named.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        by_name[f[1]] = (f[5], int(f[4]))
    for cid, nm in cname.items():
        tier[cid], system[cid] = by_name.get(nm, ("T", -1))
    have = {(r[1], r[2], r[4]) for r in rows}
    st = collections.Counter()
    log = open(a.log, "w", encoding="utf-8", newline="\n")
    for r in rows:
        tid, by, target, kind = r[0], int(r[1]), int(r[2]), r[4]
        start, end, quote, ev = int(r[9]), int(r[10]), r[11], r[12]
        ctx = quote + " " + " ".join(w for s0, e0, w in wins.get(r[8], ()) if s0 <= start and end <= e0)
        cw = words(ctx)
        # A
        if ev.startswith("name:"):
            toks = [re.sub(r"[^0-9a-z]", "", x) for x in ev[5:].lower().split(" ")]
            toks = [x for x in toks if len(x) >= 3]
            if not toks or not all(x in cw for x in toks):
                ne = checker_name(ev[5:])
                if ne and all(x.lower() in cw for x in ne[5:].split()):
                    log.write(f"{tid}\tA\tevidence\t{ev}\t{ne}\n")
                    r[12] = ne
                    st["A_evidence"] += 1
                else:
                    st["A_not_curable"] += 1
        # B
        if kind == "declinedToFollow" and NOLONGER.search(quote) and not any(
                c in quote.lower() for c in ("declin", "not follow", "refuse to follow", "disagree", "reject",
                                             "not persuaded")):   # the checker's cues today: such a row is admitted
            bc, xc = int(court[by]), int(court[target])
            own = bc == xc or (system.get(bc, -1) == system.get(xc, -2) and system.get(bc, -1) >= 0 and
                               TIER_RANK.get(tier.get(bc, "T"), 1) > TIER_RANK.get(tier.get(xc, "T"), 1))
            if own and (r[1], r[2], "overruled") not in have:
                log.write(f"{tid}\tB\tkind\tdeclinedToFollow\toverruled\n")
                r[4] = "overruled"
                have.add((r[1], r[2], "overruled"))
                st["B_relabel"] += 1
            else:
                st["B_kept_declinedToFollow"] += 1
        # C
        ql = quote.lower()
        if kind in STATUS and any(x in ql for x in rules2.DISQUAL2):
            done = False
            cuts = [0] + [m.end() for m in CLAUSE.finditer(quote)] + [len(quote)]
            spans = sorted({(cuts[i], cuts[j]) for i in range(len(cuts)) for j in range(i + 1, len(cuts))},
                           key=lambda ab: -(ab[1] - ab[0]))
            for s0, s1 in spans:
                sub = quote[s0:s1]
                strip = len(sub) - len(sub.rstrip(" ,;:"))
                sub = sub.rstrip(" ,;:")
                if len(sub) < 12 or any(x in sub.lower() for x in rules2.DISQUAL2) or not rules2.cue_ok2(kind, sub):
                    continue
                if kind == "overruled" and "overrul" not in sub.lower() and not any(
                        c in sub.lower() for c in rules2.CUES2["overruled"]):
                    continue
                shaped = any(rules.act_shaped(sub, f) for f in FAM.get(kind, [])) or bool(rules2.shapes(sub))
                if not shaped:
                    continue
                log.write(f"{tid}\tC\tquote\t{start}-{end}\t{start + s0}-{start + s1 - strip}\n")
                r[9], r[10], r[11] = str(start + s0), str(start + s1 - strip), sub
                st["C_recut"] += 1
                done = True
                break
            if not done:
                st["C_not_curable"] += 1
    log.close()
    with open(a.out, "w", encoding="utf-8", newline="\n") as fo:
        for r in rows:
            fo.write("\t".join(r) + "\n")
    print(dict(st))


if __name__ == "__main__":
    main()
