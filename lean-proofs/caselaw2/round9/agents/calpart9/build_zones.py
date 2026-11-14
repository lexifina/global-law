"""calpart9: part_zone table (DESIGN9 section 4) for every acting text node of the rows of a stage folder (+ deltas),
and the check of every row against it.

    python -X utf8 build_zones.py --stage round8/stage/v8e [--delta DIR ...] --out work/v8e [--procs 8]

The text node of a row: treatments -> `by`; history -> `by` when its text_sha (base decisions2.tsv) equals the row's
text_sha, else `target` (round-6 "text": "target" rows). Joined lines (joined.tsv / joined_delta.tsv) are checked in
their row's text. Anchors and bridges are not zone-checked (DESIGN9 section 4) and get no zones of their own.

Output (in --out):
  part_zone.tsv     node, z_start, z_end, part, src       (src = pm1|pm2 [+PJ]: part_map / part_map2, rule PJ fired)
  rowcheck.tsv      id, table (treatments|treatments_w = witness text|history), quote kind (main|joined), node,
                    start, end, row part, zone part (new map), zone part (old map, no PJ), quote_ok, sha_ok,
                    parts overlapped by a straddling quote (else -), court2, date
                    (zone part "straddle" = no single zone contains the quote)
  pj.tsv            node, section start, mark offset, old part, new part, form, mark line
  stats.json
Progress lines on stdout. No answer-key file is read.
"""
import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import partzone as PZ  # noqa: E402

L = PZ.L
NL, TAB = "\n", "\t"
C2 = PZ.C2


def read_tsv(p):
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline=NL) as f:
        return [ln.rstrip(NL).split(TAB) for ln in f if ln.strip()]


def load_rows(folders):
    """[(id, table, kind, by, target, sha, start, end, quote, part)] incl. joined lines (kind 'joined')."""
    rows = []
    byid = {}
    for d in folders:
        sfx = "" if os.path.exists(os.path.join(d, "treatments.tsv")) else "_delta"
        for p in read_tsv(os.path.join(d, "treatments%s.tsv" % sfx)):
            r = (p[0], "treatments", "main", int(p[1]), int(p[2]), p[8], int(p[9]), int(p[10]), p[11], p[13])
            rows.append(r)
            byid[p[0]] = r
        for p in read_tsv(os.path.join(d, "history%s.tsv" % sfx)):
            by = int(p[2]) if p[2].lstrip("-").isdigit() else -1
            r = (p[0], "history", "main", by, int(p[1]), p[6], int(p[7]), int(p[8]), p[9], p[11])
            rows.append(r)
            byid[p[0]] = r
    wit = {}
    for d in folders:
        sfx = "" if os.path.exists(os.path.join(d, "treatment_witness.tsv")) else "_delta"
        for p in read_tsv(os.path.join(d, "treatment_witness%s.tsv" % sfx)):
            wit[p[0]] = int(p[1])
    for i, r in enumerate(rows):
        if r[0] in wit:  # witness row: the quote is from the witness node's text
            rows[i] = r = (r[0], "treatments_w", r[2], wit[r[0]], r[4], r[5], r[6], r[7], r[8], r[9])
            byid[r[0]] = r
    for d in folders:
        sfx = "" if os.path.exists(os.path.join(d, "joined.tsv")) else "_delta"
        for p in read_tsv(os.path.join(d, "joined%s.tsv" % sfx)):
            base = byid.get(p[0])
            if base is None:
                continue
            rows.append((p[0], base[1], "joined", base[3], base[4], base[5], int(p[3]), int(p[4]), p[5], p[6]))
    return rows


def node_shas(want):
    """{node: text_sha} from the base decisions2.tsv (line k = node k)."""
    out = {}
    mx = max(want) if want else -1
    with open(os.path.join(C2, "round8", "stage", "v8e", "decisions2.tsv"), encoding="utf-8", newline=NL) as f:
        for k, ln in enumerate(f):
            if k > mx:
                break
            if k in want:
                out[k] = ln.split(TAB, 8)[7]
    return out


def work(job):
    repo, items = job  # items: [(node, path, [row tuples])]
    rd = os.path.join(L.REPOS, repo)
    p = subprocess.Popen(["git", "-C", rd, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         creationflags=L.NOWIN)

    def feed():
        for _n, path, _r in items:
            p.stdin.write(("HEAD:%s\n" % path).encode("utf-8"))
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    zl, rl, pl = [], [], []
    st = collections.Counter()
    for n, path, rows in items:
        header = p.stdout.readline().split()
        if len(header) < 3 or header[1] != b"blob":
            st["missing_text"] += 1
            continue
        size = int(header[2])
        data = p.stdout.read(size)
        p.stdout.read(1)
        sha = hashlib.sha1(data).hexdigest()
        text = data.decode("utf-8", "replace").replace("\r\n", NL)
        try:
            zs, info = PZ.zones(text)
        except Exception as ex:  # count, keep going
            st["zone_err"] += 1
            sys.stderr.write("%s %d: %r\n" % (repo, n, ex))
            continue
        old = PZ.to_zones(info["pm_old"], len(text))
        src = PZ.MODE["pm"] + ("hw" if info["hw"] else "") + ("+PJ" if info["pj"] else "")
        st["nodes"] += 1
        st["nodes_pj"] += bool(info["pj"])
        for a, b, zp in zs:
            zl.append("%d\t%d\t%d\t%s\t%s" % (n, a, b, zp, src))
        for c in info["pj"]:
            pl.append("%d\t%d\t%d\t%s\t%s\t%s\t%s" % (n, c[0], c[1], c[3], c[4], c[5], L.norm(c[2])))
        for r in rows:
            rid, table, qk, by, tg, rsha, s, e, quote, part = r
            qok = int(0 <= s < e <= len(text) and L.norm(text[s:e]) == quote)
            z = PZ.zone_at(zs, s, e)
            zo = PZ.zone_at(old, s, e)
            ov = "+".join(sorted(set(zp for a, b, zp in zs if a < e and s < b))) if not z else "-"
            rl.append(TAB.join([rid, table, qk, str(n), str(s), str(e), part, z[2] if z else "straddle",
                                zo[2] if zo else "straddle", str(qok), str(int(rsha == sha)), ov]))
    p.wait()
    return zl, rl, pl, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default=os.path.join(C2, "round8", "stage", "v8e"))
    ap.add_argument("--delta", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--chunk", type=int, default=1500)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    rows = load_rows([a.stage] + a.delta)
    print("rows", len(rows), flush=True)
    want = set()
    for r in rows:
        want.add(r[3])
        want.add(r[4])
    want.discard(-1)
    shas = node_shas(want)
    print("shas", len(shas), round(time.time() - t0), flush=True)
    per_node = collections.defaultdict(list)
    st = collections.Counter()
    for r in rows:
        if r[1] in ("treatments", "treatments_w"):
            n = r[3]
        else:
            n = r[3] if (r[3] >= 0 and shas.get(r[3]) == r[5]) else r[4]
            st["hist_text_target"] += n == r[4]
        per_node[n].append(r)
    print("nodes", len(per_node), flush=True)
    by_repo = collections.defaultdict(list)
    for n in sorted(per_node):
        nr = L.node_row(n)
        by_repo[nr[1]].append((n, nr[2], per_node[n]))
    jobs = []
    for repo, items in by_repo.items():
        for k in range(0, len(items), a.chunk):
            jobs.append((repo, items[k:k + a.chunk]))
    jobs.sort(key=lambda j: -len(j[1]))
    print("jobs", len(jobs), flush=True)
    F = L.Facts()
    zf = open(os.path.join(a.out, "part_zone.tsv"), "w", encoding="utf-8", newline=NL)
    rf = open(os.path.join(a.out, "rowcheck.tsv"), "w", encoding="utf-8", newline=NL)
    pf = open(os.path.join(a.out, "pj.tsv"), "w", encoding="utf-8", newline=NL)
    done = 0
    for zl, rl, pl, s2 in L.pmap(work, jobs, procs=a.procs):
        for x in zl:
            zf.write(x + NL)
        for x in rl:
            n = int(x.split(TAB)[3])
            rf.write(x + TAB + str(int(F.court[n])) + TAB + str(int(F.date[n])) + NL)
        for x in pl:
            pf.write(x + NL)
        st.update(s2)
        done += 1
        if done % 10 == 0 or done == len(jobs):
            print("jobs %d/%d nodes %d %ds" % (done, len(jobs), st["nodes"], time.time() - t0), flush=True)
    zf.close()
    rf.close()
    pf.close()
    st["sec"] = round(time.time() - t0)
    json.dump(dict(st), open(os.path.join(a.out, "stats.json"), "w"), indent=1)
    print("DONE", json.dumps(dict(st)), flush=True)


if __name__ == "__main__":
    main()
