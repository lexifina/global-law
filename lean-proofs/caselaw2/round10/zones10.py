"""Round 10 (agent infra10): part-zone lines (DESIGN9 section 4) for the acting text nodes of staged rows that have none.

v9c's part_zone.tsv was built by round9/agents/calpart9/build_zones.py over every round-9 row (round9/lead/zones_all).
A round-10 row whose text node has no zone line would be refused by the Lean zone check (zone_missing), so
round10/stage10.py calls missing_zone_lines() after its deltas: the same per-node builder (build_zones.work ->
partzone.zones, part_map2 + rule PJ, PZ_PM=pm2), the same text-node rule and the same line format
(node, z_start, z_end, part, src). Lines come out sorted by node (each node's zones in text order), so a stage is
reproducible. Nothing under round9/ is written (no bytecode).

Text node of a row (= build_zones.py): treatments -> `by`, or the witness node when the row has a treatment_witness
line; history -> `by` when decisions2.tsv's text_sha of `by` equals the row's text_sha, else `target`. Joined lines
live in their row's text (same node). Anchors and bridges are not zone-checked.

    python -X utf8 round10/zones10.py --check-stage round10/stage/<name>      nodes of the stage's rows without zones
    python -X utf8 round10/zones10.py --selftest [--sample K | --all] [--procs 8]
        rebuild the zone lines of K random (seed 10) or all nodes of round9/stage/v9c/part_zone.tsv with this builder
        and compare them byte for byte (per node, in order) with v9c's lines.
No answer-key file is read.
"""
import argparse
import collections
import os
import random
import sys
import time

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"  # spawned workers import round-9 modules: write no bytecode there
os.environ["PZ_PM"] = "pm2"  # the v9c zone table's mode (src pm2...)
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
CALPART = os.path.join(C2, "round9", "agents", "calpart9")
V9C = os.path.join(C2, "round9", "stage", "v9c")
sys.path.insert(0, CALPART)
import build_zones as BZ  # noqa: E402
import partzone as PZ  # noqa: E402

L = PZ.L
TAB = b"\t"


def read_lines(p):
    if not os.path.exists(p):
        return []
    with open(p, "rb") as f:
        return [x for x in f.read().split(b"\n") if x]


def zone_nodes(lines):
    out = set()
    for x in lines:
        h = x.split(TAB, 1)[0]
        if h.isdigit():
            out.add(int(h))
    return out


def node_shas(want, d2):
    """{node: text_sha bytes} from decisions2.tsv (line k = node k, column 7)."""
    out = {}
    if not want:
        return out
    mx = max(want)
    with open(d2, "rb") as f:
        for k, ln in enumerate(f):
            if k > mx:
                break
            if k in want:
                out[k] = ln.split(TAB, 8)[7]
    return out


def needed_nodes(tabs, d2):
    """Text nodes of the staged rows that have no part_zone line, and counts."""
    zn = zone_nodes(tabs.get("part_zone", []))
    wit = {}
    for x in tabs.get("treatment_witness", []):
        p = x.split(TAB, 2)
        if len(p) >= 2 and p[1].lstrip(b"-").isdigit():
            wit[p[0]] = int(p[1])
    need = collections.Counter()  # node -> rows
    for x in tabs.get("treatments", []):
        p = x.split(TAB, 3)
        n = wit.get(p[0], int(p[1]))
        if n not in zn:
            need[n] += 1
    cand = []
    for x in tabs.get("history", []):
        p = x.split(TAB, 7)
        target = int(p[1])
        by = int(p[2]) if p[2].lstrip(b"-").isdigit() else -1
        if (by < 0 or by in zn) and target in zn:
            continue
        cand.append((by, target, p[6]))
    shas = node_shas({c[0] for c in cand if c[0] >= 0}, d2)
    for by, target, sha in cand:
        n = by if (by >= 0 and shas.get(by) == sha) else target
        if n not in zn:
            need[n] += 1
    return need, len(zn)


def build(nodes, procs=8, chunk=1500):
    """{node: [zone line bytes]} by build_zones.work (one git cat-file per repo chunk); and its counters."""
    by_repo = collections.defaultdict(list)
    for n in sorted(nodes):
        nr = L.node_row(n)
        by_repo[nr[1]].append((n, nr[2], []))
    jobs = []
    for repo, items in by_repo.items():
        for k in range(0, len(items), chunk):
            jobs.append((repo, items[k:k + chunk]))
    jobs.sort(key=lambda j: -len(j[1]))
    per = collections.defaultdict(list)
    st = collections.Counter()
    if not jobs:
        return per, st
    it = map(BZ.work, jobs) if procs <= 1 or len(jobs) == 1 else L.pmap(BZ.work, jobs, procs=min(procs, len(jobs)))
    for zl, _rl, _pl, s2 in it:
        for z in zl:
            per[int(z.split("\t", 1)[0])].append(z.encode("utf-8"))
        st.update(s2)
    return per, st


def missing_zone_lines(tabs, d2, procs=8):
    """(lines to append to part_zone, one-line report) for a stage10 Stage's tables."""
    t0 = time.time()
    need, nz = needed_nodes(tabs, d2)
    if not need:
        return [], "every staged row's text node has zone lines (%d zoned nodes); none added" % nz
    per, st = build(set(need), procs=procs)
    lines = []
    for n in sorted(per):
        lines.extend(per[n])
    nomiss = sorted(n for n in need if n not in per)
    info = ("%d text nodes of %d staged rows had no zone line; built %d zone lines for %d nodes "
            "(calpart9 build_zones.work, pm2+PJ; missing text %d, zone errors %d%s), %ds" % (
                len(need), sum(need.values()), len(lines), len(per), st["missing_text"], st["zone_err"],
                ("; still without zones: %s" % " ".join(map(str, nomiss[:20])) + (" ..." if len(nomiss) > 20 else ""))
                if nomiss else "", time.time() - t0))
    return lines, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-stage")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sample", type=int, default=3000)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    if a.check_stage:
        tabs = {t: read_lines(os.path.join(a.check_stage, t + ".tsv"))
                for t in ("treatments", "treatment_witness", "history", "part_zone")}
        need, nz = needed_nodes(tabs, os.path.join(V9C, "decisions2.tsv"))
        print("stage %s: %d zoned nodes; %d text nodes of %d rows without zones%s" % (
            a.check_stage, nz, len(need), sum(need.values()),
            (": " + " ".join(map(str, sorted(need)[:30]))) if need else ""))
        return
    if a.selftest:
        t0 = time.time()
        base = collections.defaultdict(list)
        for x in read_lines(os.path.join(V9C, "part_zone.tsv")):
            base[int(x.split(TAB, 1)[0])].append(x)
        nodes = sorted(base)
        if not a.all:
            nodes = sorted(random.Random(10).sample(nodes, min(a.sample, len(nodes))))
        per, st = build(set(nodes), procs=a.procs)
        same = sum(1 for n in nodes if per.get(n) == base[n])
        diff = [n for n in nodes if per.get(n) != base[n]]
        print("zones10 selftest: %d v9c nodes rebuilt, %d byte-identical, %d differ%s; lines %d vs %d; "
              "missing text %d, zone errors %d; %ds" % (
                  len(nodes), same, len(diff), (" (e.g. %s)" % " ".join(map(str, diff[:10]))) if diff else "",
                  sum(len(per.get(n, [])) for n in nodes), sum(len(base[n]) for n in nodes),
                  st["missing_text"], st["zone_err"], time.time() - t0))
        sys.exit(1 if diff else 0)
    ap.print_help()


if __name__ == "__main__":
    main()
