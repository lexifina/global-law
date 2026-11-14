"""Self-test of round7/certify7.py on real rows: base rows of round6/history/stage/final2 turned back into linker rows,
certified with --no-base-skip, and compared with the round-6 Lean verdict of the same row
(round6/history/out/final2/certs.tsv). Lean ok / okUnverifiedBy / noAuthority <-> admitted; any other Lean verdict
<-> the same reason. certify7 may be stricter than Lean (one window per quote) but never looser.

    python -X utf8 round7/agents/infra/selftest7.py [--n 3000] [--seed 7] [--procs 12]
Writes round7/agents/infra/selftest/ (rows.jsonl, cert/, SELFTEST.txt). Reads no answer key.
"""
import argparse
import collections
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R7 = os.path.dirname(os.path.dirname(HERE))
C2 = os.path.dirname(R7)
sys.path.insert(0, R7)
import certify7 as C7  # noqa: E402

BASE = C7.BASE
OUT6 = os.path.join(C2, "round6", "history", "out", "final2", "certs.tsv")
ADMIT = ("ok", "okUnverifiedBy", "noAuthority")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--procs", type=int, default=12)
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    work = os.path.join(HERE, "selftest")
    os.makedirs(work, exist_ok=True)
    lean = {}
    with open(OUT6, encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3 and p[0] in ("treatment", "history"):
                lean[(p[0], p[1])] = p[2]
    wit = {p[0] for p in C7.C6.read_tsv(os.path.join(BASE, "treatment_witness.tsv"))}
    cls = {p[0] for p in C7.C6.read_tsv(os.path.join(BASE, "treatment_class.tsv"))}
    trows = [p for p in C7.C6.read_tsv(os.path.join(BASE, "treatments.tsv"))
             if len(p) == 16 and p[0] not in wit and p[0] not in cls and p[7] == "1"]
    hrows = [p for p in C7.C6.read_tsv(os.path.join(BASE, "history.tsv")) if len(p) == 13]
    anc = {p[0]: p for p in C7.C6.read_tsv(os.path.join(BASE, "history_anchor.tsv")) if len(p) == 6}

    def pick(rows, table):
        fail = [p for p in rows if lean.get((table, p[0]), "ok") not in ADMIT]
        okr = [p for p in rows if lean.get((table, p[0]), "ok") in ADMIT]
        by_reason = collections.defaultdict(list)
        for p in fail:
            by_reason[lean[(table, p[0])]].append(p)
        s = rnd.sample(okr, min(a.n, len(okr)))
        for r, ps in by_reason.items():
            s += rnd.sample(ps, min(60, len(ps)))
        return s

    ts, hs = pick(trows, "treatment"), pick(hrows, "history")
    want = {int(p[1]) for p in hs} | {int(p[2]) for p in hs if int(p[2]) >= 0}
    dec = C7.read_decisions(os.path.join(BASE, "decisions2.tsv"), want)
    ref = {}
    with open(os.path.join(work, "rows.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        k = 0
        for p in ts:
            k += 1
            ref[k] = ("treatment", p[0])
            sc = p[5] if p[5] in C7.T_SCOPES else "all"
            f.write(json.dumps({"rule": "selftest:t", "table": "treatments", "by": int(p[1]), "target": int(p[2]),
                                "kind": p[4], "scope": sc, "main": [int(p[9]), int(p[10])], "part": p[13],
                                "ev": p[12], "claim": "-"}) + "\n")
        for p in hs:
            by, tg = int(p[2]), int(p[1])
            text = "target" if tg in dec and dec[tg][2] == p[6] else "by"
            an = anc.get(p[0])
            ev = p[10]
            if text == "target" and an is None and not (ev.startswith("cite:") or ev.startswith("name:")):
                ev = ""
            k += 1
            ref[k] = ("history", p[0])
            f.write(json.dumps({"rule": "selftest:h", "table": "history", "by": by, "target": tg, "kind": p[4],
                                "scope": p[5] if p[5] in ("all", "unknown") else "all",
                                "main": [int(p[7]), int(p[8])], "part": p[11], "ev": ev, "text": text,
                                "anchor": [int(an[1]), int(an[2])] if an else None,
                                "anchor_part": an[4] if an else "", "claim": "-"}) + "\n")
    cert = os.path.join(work, "cert")
    r = subprocess.run([sys.executable, "-X", "utf8", os.path.join(R7, "certify7.py"), "--rows",
                        os.path.join(work, "rows.jsonl"), "--out", cert, "--procs", str(a.procs), "--no-base-skip"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:])
        return 1
    mine = {}
    for p in C7.C6.read_tsv(os.path.join(cert, "rejects.tsv")):
        mine[int(p[0].rsplit(":", 1)[1])] = p[1]
    agree = collections.Counter()
    dis = collections.Counter()
    looser = []
    stricter = []
    for k, (table, i) in ref.items():
        lv = lean.get((table, i))
        cv = mine.get(k, "admitted")
        if cv in ("duplicate", "conflict"):
            agree[(table, "post-check " + cv)] += 1
            continue
        lv2 = "admitted" if lv in ADMIT else lv
        if lv2 == cv:
            agree[(table, cv)] += 1
        else:
            dis[(table, lv, cv)] += 1
            (looser if cv == "admitted" else stricter).append((table, i, lv, cv))
    lines = ["certify7 self-test on base rows of final2 (seed %d, n %d per table + up to 60 per Lean failure "
             "reason)" % (a.seed, a.n), ""]
    for (t, v), c in sorted(agree.items()):
        lines.append("agree\t%s\t%s\t%d" % (t, v, c))
    for (t, lv, cv), c in sorted(dis.items()):
        lines.append("DISAGREE\t%s\tLean %s\tcertify7 %s\t%d" % (t, lv, cv, c))
    lines.append("")
    lines.append("rows %d; agree %d; certify7 looser than Lean %d; certify7 stricter %d" % (
        len(ref), sum(agree.values()), len(looser), len(stricter)))
    for x in (looser + stricter)[:40]:
        lines.append("  %s %s Lean %s certify7 %s" % x)
    open(os.path.join(work, "SELFTEST.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 1 if looser else 0


if __name__ == "__main__":
    sys.exit(main())
