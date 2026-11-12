"""Write the Lean runner's inputs (LegalProofs/USCaseLaw/Run.lean) from the graph, court table and events.

    python tools/caselaw/encode.py <graph-dir> <events-dir> <lean-in-dir> [shards]

courts.tsv: one row per court and era (index, system, tier L/A/T/S, circuit); decisions.tsv: id, court index, date;
acts.tsv, reports.tsv from events.py (reports: deciding decision, decision said to be overruled, the overruling
decision named or -1); edges-NN.tsv: the citations, split into shards by citing decision.
"""
import array, os, sys

T = {"last": "L", "appellate": "A", "trial": "T", "special": "S"}


def main(g, ev, out, shards=16):
    shards = int(shards)
    os.makedirs(out, exist_ok=True)
    eras = {}  # cid -> [(lo, hi, idx)]
    rows = []
    for line in open(os.path.join(g, "court_table.tsv"), encoding="utf-8"):
        cid, name, lo, hi, sysid, sysname, tier, circ, rule = line.rstrip("\n").split("\t")
        idx = len(rows)
        rows.append((idx, sysid, T[tier], circ, name, lo, hi, rule))
        eras.setdefault(cid, []).append((int(lo), int(hi), idx))
    # unmapped courts: a trial court of an unknown system (system 999), so no binding relation
    with open(os.path.join(out, "courts.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for idx, sysid, t, circ, *_ in rows:
            f.write(f"{idx}\t{sysid}\t{t}\t{circ}\n")
        unk = len(rows)
        f.write(f"{unk}\t999\tT\t0\n")
    with open(os.path.join(out, "courts_named.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for idx, sysid, t, circ, name, lo, hi, rule in rows:
            f.write(f"{idx}\t{name}\t{lo}\t{hi}\t{sysid}\t{t}\t{circ}\t{rule}\n")
    n = 0
    with open(os.path.join(out, "decisions.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for line in open(os.path.join(g, "nodes.tsv"), encoding="utf-8"):
            p = line.split("\t", 6)
            nid, cid, date = p[0], p[3], int(p[4])
            y = date // 10000
            ci = unk
            for lo, hi, idx in eras.get(cid, []):
                if lo <= y <= hi:
                    ci = idx
                    break
            f.write(f"{nid}\t{ci}\t{date}\n")
            n += 1
    with open(os.path.join(out, "acts.tsv"), "w", encoding="utf-8", newline="\n") as f:
        seen = set()
        for line in open(os.path.join(ev, "acts.tsv"), encoding="utf-8"):
            a = line.split("\t")
            if (a[0], a[1]) not in seen:
                seen.add((a[0], a[1]))
                f.write(f"{a[0]}\t{a[1]}\n")
    with open(os.path.join(out, "reports.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for line in open(os.path.join(ev, "reports.tsv"), encoding="utf-8"):
            a = line.split("\t")
            f.write(f"{a[0]}\t{a[1]}\t{a[2] or -1}\n")
    ed = array.array("I")
    with open(os.path.join(g, "edges.bin"), "rb") as fe:
        ed.frombytes(fe.read())
    fs = [open(os.path.join(out, f"edges-{k:02d}.tsv"), "w", encoding="utf-8", newline="\n") for k in range(shards)]
    for i in range(0, len(ed), 2):
        fs[ed[i] % shards].write(f"{ed[i]}\t{ed[i + 1]}\n")
    for f in fs:
        f.close()
    print("courts", len(rows), "decisions", n, "edges", len(ed) // 2)


if __name__ == "__main__":
    main(*sys.argv[1:])
