"""syl10: corpus-wide count of reader / linker rows (every history_delta.tsv / treatments_delta.tsv under round5..round9,
plus the v9c stage) whose quotes for a (by, target, kind) all lie outside the court zones of the text owner (head
matter / syllabus / straddle) -- rows the round-9 zone check refuses now or would refuse in a future build.
Zones: v9c part_zone.tsv; nodes it lacks get calpart9 partzone.zones (same map).

    python -X utf8 count_future.py --out work/future
No answer-key file is read.
"""
import argparse
import collections
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round9", "agents", "calpart9"))
import partzone as PZ  # noqa: E402

L = PZ.L
NL, TAB = "\n", "\t"
STAGE = os.path.join(C2, "round9", "stage", "v9c")
COURT = ("majority", "plurality", "perCuriam")


def delta_files():
    out = []
    for r in ("round5", "round6", "round7", "round8", "round9"):
        base = os.path.join(C2, r)
        for dp, dn, fn in os.walk(base):
            if dp[len(base):].count(os.sep) >= 4:
                dn[:] = []
            if os.path.basename(dp) in ("cache", "stage", "out", "results"):
                dn[:] = []
                continue
            for f in fn:
                if f in ("history_delta.tsv", "treatments_delta.tsv"):
                    out.append(os.path.join(dp, f))
    return sorted(out)


def parse(p):
    if len(p) == 13 and p[0][:1] == "h":
        by = int(p[2]) if p[2].lstrip("-").isdigit() else -1
        own = by if by >= 0 else int(p[1])
        return ("history", own, int(p[1]), p[4], int(p[7]), int(p[8]), p[11])
    if len(p) == 16 and p[0][:1] == "t":
        return ("treatments", int(p[1]), int(p[2]), p[4], int(p[9]), int(p[10]), p[13])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = {}
    src = collections.Counter()
    for f in [os.path.join(STAGE, "history.tsv"), os.path.join(STAGE, "treatments.tsv")] + delta_files():
        staged = os.path.dirname(f) == STAGE
        for ln in open(f, encoding="utf-8"):
            p = ln.rstrip(NL).split(TAB)
            try:
                r = parse(p)
            except ValueError:
                r = None
            if r is None:
                continue
            key = (r[0], r[1], r[4], r[5], r[2], r[3])
            if key not in rows:
                rows[key] = (p[0], staged)
                src["staged" if staged else "unstaged"] += 1
    nodes = set(k[1] for k in rows)
    zones = collections.defaultdict(list)
    for ln in open(os.path.join(STAGE, "part_zone.tsv"), encoding="utf-8"):
        p = ln.rstrip(NL).split(TAB)
        n = int(p[0])
        if n in nodes:
            zones[n].append((int(p[1]), int(p[2]), p[3]))
    missing = sorted(nodes - set(zones))
    for i in range(0, len(missing), 2000):
        tx = L.fetch_texts(missing[i:i + 2000])
        for n, (_sha, t) in tx.items():
            zones[n] = PZ.zones(t)[0]
    st = collections.Counter(src)
    st["nodes"] = len(nodes)
    st["nodes_zoned_here"] = len(missing)
    verdict = {}
    for ln in open(os.path.join(C2, "round9", "out", "v9c", "certs.tsv"), encoding="utf-8"):
        p = ln.rstrip(NL).split(TAB)
        if len(p) >= 3:
            verdict[p[1]] = p[2]
    by_key = collections.defaultdict(list)
    for (tab, own, s, e, tg, kind), (rid, staged) in rows.items():
        zs = zones.get(own, [])
        z = next((zz for zz in zs if zz[0] <= s and e <= zz[1]), None)
        if not zs:
            where = "noZones"
        elif z is None:
            parts = sorted(set(zz[2] for zz in zs if zz[0] < e and s < zz[1]))
            where = "straddle:" + "+".join(parts)
        else:
            where = z[2]
        by_key[(tab, own, tg, kind)].append((rid, staged, where))
    fo = open(os.path.join(a.out, "outside_only.tsv"), "w", encoding="utf-8", newline=NL)
    for k, lst in by_key.items():
        if any(w in COURT or w in ("concurrence", "dissent", "noZones") for _, _, w in lst):
            continue
        cls = "headmatter" if all(w == "headmatter" for _, _, w in lst) else (
            "straddle" if all(w.startswith("straddle") for _, _, w in lst) else "mixedOutside")
        stg = "staged" if any(s for _, s, _ in lst) else "unstaged"
        if stg == "staged":
            vs = sorted(set(verdict.get(r, "?") for r, s, _ in lst if s))
            adm = any(v.startswith("ok") or v.startswith("witness") for v in vs)
            stg += ":admitted" if adm else ":" + "|".join(vs)[:40]
        st["keys_outside_only:%s:%s:%s" % (k[0], stg, cls)] += 1
        fo.write(TAB.join([k[0], str(k[1]), str(k[2]), k[3], stg, cls, ";".join(r for r, _, _ in lst)]) + NL)
    fo.close()
    st["keys"] = len(by_key)
    json.dump(dict(sorted(st.items())), open(os.path.join(a.out, "stats.json"), "w"), indent=1)
    print(json.dumps(dict(sorted(st.items())), indent=1))


if __name__ == "__main__":
    main()
