"""Independent check of the holdings certificates against git HEAD, as Lean will check them.

    python check_certs.py
For every holdings.tsv row: sha1(file bytes) == text_sha; normalised text[start:end] == quote; and holdings_cert_text.tsv
has a row (text_sha, start0, end0, window) with start0 = max(0, start-400), end0 = min(len, end+400),
window == normalised text[start0:end0], and window[start-start0 : end-start0] == quote.
Prints counts of each failure (all should be 0).
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text

DATA = os.environ.get("HOLD_DATA") or os.path.join(text.WORK, "caselaw-lean-2", "data")
_W = None


def _load():
    global _W, _H
    if _W is None:
        _W = {}
        for l in open(os.path.join(DATA, "holdings_cert_text.tsv"), encoding="utf-8"):
            f = l.rstrip("\n").split("\t", 3)
            _W[(f[0], int(f[1]), int(f[2]))] = f[3]
        _H = collections.defaultdict(list)
        for l in open(os.path.join(DATA, "holdings.tsv"), encoding="utf-8"):
            f = l.rstrip("\n").split("\t")
            _H[int(f[1])].append((f[6], int(f[7]), int(f[8]), f[9]))


def work(nid, raw):
    _load()
    t = text.norm_text(raw)
    sha = text.text_sha(raw)
    c = collections.Counter()
    for s, a, z, q in _H[nid]:
        c["rows"] += 1
        if s != sha:
            c["sha_mismatch"] += 1
            continue
        if text.quote_of(t, a, z) != q:
            c["quote_mismatch"] += 1
        w0, w1 = max(0, a - 400), min(len(t), z + 400)
        w = _W.get((s, w0, w1))
        if w is None:
            c["window_missing"] += 1
        elif w != text.quote_of(t, w0, w1) or w[a - w0:z - w0] != q:
            c["window_mismatch"] += 1
    return dict(c)


def main():
    _load()
    tot = collections.Counter()
    for r in text.map_nodes(sorted(_H), work, procs=6, chunk=3000):
        if isinstance(r, tuple):
            tot["errors"] += 1
            continue
        tot.update(r)
    tot["cert_text_rows"] = len(_W)
    print(json.dumps(dict(tot), indent=1))
    json.dump(dict(tot), open(os.path.join(DATA, "holdings_work", "check_certs.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
