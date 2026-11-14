"""Audit packs: blind review sheets for treatment rows, rejected candidates and history rows.

    python -X utf8 audit_pack.py treat  <treatments.tsv> <treatments_items.tsv> <out.jsonl> [n] [seed]
    python -X utf8 audit_pack.py reject <ids.tsv (id, ...)> <out.jsonl>
    python -X utf8 audit_pack.py hist   <history.tsv> <out.jsonl> [n] [seed]

Each record carries what a reviewer needs and nothing of the reader's verdict beyond the claim under test: the
deciding decision (name, court, date, repo, path, so the full text can be read with `git -C <repo> show HEAD:<path>`),
the opinion part, the text window, the focus sentence and the claimed target (or, for rejected candidates, the first
resolved candidate).
"""
import collections, glob, gzip, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, WORK, REPOS  # noqa: E402


def node_info(ids):
    out = {}
    courts = {}
    for line in open(os.path.join(W, "graph", "courts.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        courts[f[0]] = f[1]
    for line in open(os.path.join(W, "graph", "nodes.tsv"), encoding="utf-8"):
        f = line.split("\t", 7)
        n = int(f[0])
        if n in ids:
            out[n] = {"node": n, "repo": f[1], "path": f[2], "court": courts.get(f[3], "?"), "date": int(f[4]),
                      "cite": f[5].split("|")[0], "name": f[6]}
    return out


def items_for(ids):
    need = set(ids)
    out = {}
    for f in glob.glob(os.path.join(WORK, "res", "*.items.jsonl.gz")):
        for line in gzip.open(f, "rt", encoding="utf-8"):
            if not need:
                break
            i = line[8:line.index('"', 8)]
            if i in need:
                it = json.loads(line)
                out[it["id"]] = it
                need.discard(it["id"])
    return out


def window(it, pad=600):
    a = max(it["w0"], it["s0"] - pad)
    b = min(it["w1"], it["s1"] + pad)
    return it["w"][a - it["w0"]:b - it["w0"]]


def main():
    mode = sys.argv[1]
    if mode == "treat":
        rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[2], encoding="utf-8")]
        imap = {l.split("\t")[0]: l.rstrip("\n").split("\t")[1] for l in open(sys.argv[3], encoding="utf-8")}
        out = sys.argv[4]
        n = int(sys.argv[5]) if len(sys.argv) > 5 else len(rows)
        rnd = random.Random(int(sys.argv[6]) if len(sys.argv) > 6 else 1)
        # stratify by kind
        byk = collections.defaultdict(list)
        for r in rows:
            byk[r[4]].append(r)
        pick = []
        for k, xs in sorted(byk.items()):
            rnd.shuffle(xs)
            pick += xs[:max(8, n // max(1, len(byk)))]
        rest = [r for k, xs in byk.items() for r in xs if r not in pick]
        rnd.shuffle(rest)
        pick = (pick + rest)[:max(n, 0)] if n < len(rows) else rows
        its = items_for({imap[r[0]] for r in pick})
        ni = node_info({int(r[1]) for r in pick} | {int(r[2]) for r in pick})
        with open(out, "w", encoding="utf-8", newline="\n") as fo:
            for r in pick:
                it = its[imap[r[0]]]
                by, tg = ni[int(r[1])], ni[int(r[2])]
                fo.write(json.dumps({"audit_id": r[0], "type": "treatment", "deciding": by, "part": r[13],
                                     "focus": it["w"][it["s0"] - it["w0"]:it["s1"] - it["w0"]], "window": window(it),
                                     "quote": r[11], "claimed_target": tg,
                                     "claim": {"kind": r[4], "scope": r[5], "temporal": r[6]}},
                                    ensure_ascii=False) + "\n")
    elif mode == "reject":
        ids = [l.split("\t")[0].strip() for l in open(sys.argv[2], encoding="utf-8") if l.strip()]
        its = items_for(ids)
        ni = node_info({its[i]["n"] for i in ids if i in its})
        with open(sys.argv[3], "w", encoding="utf-8", newline="\n") as fo:
            for i in ids:
                it = its.get(i)
                if it is None:
                    continue
                t = it["targets"][0] if it["targets"] else None
                fo.write(json.dumps({"audit_id": i, "type": "candidate", "deciding": ni[it["n"]],
                                     "part": it["part"].rstrip("~"),
                                     "focus": it["w"][it["s0"] - it["w0"]:it["s1"] - it["w0"]], "window": window(it),
                                     "candidate_targets": [{k: x[k] for k in ("name", "court", "year", "cite", "node")}
                                                           for x in it["targets"]]},
                                    ensure_ascii=False) + "\n")
    elif mode == "hist":
        rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[2], encoding="utf-8")]
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 50
        rnd = random.Random(int(sys.argv[5]) if len(sys.argv) > 5 else 1)
        byk = collections.defaultdict(list)
        for r in rows:
            byk[r[4]].append(r)
        pick = []
        for k, xs in sorted(byk.items()):
            rnd.shuffle(xs)
            pick += xs[:max(3, n // max(1, len(byk)))]
        rest = [r for k, xs in byk.items() for r in xs if r not in pick]
        rnd.shuffle(rest)
        pick = (pick + rest)[:n]
        ni = node_info({int(r[1]) for r in pick} | {int(r[2]) for r in pick})
        certs = {}
        want = {(r[6], int(r[7]), int(r[8])) for r in pick}
        cdir = os.path.dirname(sys.argv[2])
        for line in open(os.path.join(cdir, "cert_text.tsv"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            certs.setdefault(f[0], []).append((int(f[1]), int(f[2]), f[3]))
        with open(sys.argv[3], "w", encoding="utf-8", newline="\n") as fo:
            for r in pick:
                win = next((w for a, b, w in certs.get(r[6], []) if a <= int(r[7]) and int(r[8]) <= b), "")
                fo.write(json.dumps({"audit_id": r[0], "type": "history", "deciding": ni[int(r[2])],
                                     "claimed_target": ni[int(r[1])], "quote": r[9], "window": win,
                                     "claim": {"kind": r[4], "scope": r[5]}}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
