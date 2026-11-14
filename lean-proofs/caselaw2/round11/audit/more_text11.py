"""Round-11 blind audit (port of round7/audit/more_text7.py): print more text for one item, and nothing else.

    python -X utf8 round11/audit/more_text11.py <item id> [chars | all] [--target] [--run <run>]

Without --target: the text shown in the item (the speaking / acting decision's text, or the target's own text when
the item says so), `chars` more characters on each side of the pack's passages (default 3000; `all` = the whole
text); the passages stand between `>>>` and `<<<`. With --target: the opening of the target decision's own text
(`chars` characters, default 3000; `all` = the whole text). The file's front matter is never printed. `--run` is
only needed if two runs share an item id.
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit11lib as A  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("item")
    ap.add_argument("chars", nargs="?", default="3000")
    ap.add_argument("--target", action="store_true")
    ap.add_argument("--run")
    a = ap.parse_args()
    A.utf8_stdout()
    hits = []
    import glob
    for ip in sorted(glob.glob(os.path.join(A.HERE, "**", "store", "index.tsv"), recursive=True)):
        d = os.path.dirname(os.path.dirname(ip))
        if a.run and a.run.strip("/") not in (os.path.basename(d),
                                               os.path.relpath(d, A.HERE).replace("\\", "/")):
            continue
        if True:
            for p in A.read_tsv(ip, 6):
                if p[0] == a.item:
                    hits.append((d, p))
    if not hits:
        sys.exit("unknown item id " + a.item)
    if len(hits) > 1:
        sys.exit("item id %s exists in several runs: give --run <run>" % a.item)
    d, (_i, sha, b0, wins, tsha, tb0) = hits[0]
    every = a.chars.strip().lower() == "all"
    if not every:
        try:
            n = max(0, int(a.chars))
        except ValueError:
            sys.exit("chars: a number, or all")
    if a.target:
        with open(os.path.join(A.HERE, d, "store", "text", tsha + ".txt"), encoding="utf-8", newline="") as f:
            t = f.read()
        tb0 = int(tb0)
        hi = len(t) if every else min(len(t), A._word_right(t, tb0 + n))
        print("ITEM %s: the target decision's own text, characters 0-%d of %d" % (a.item, hi - tb0, len(t) - tb0))
        print(t[tb0:hi] + ("" if hi >= len(t) else " [...]") + ("" if hi < len(t) else A.NL + "[end of the text]"))
        return
    with open(os.path.join(A.HERE, d, "store", "text", sha + ".txt"), encoding="utf-8", newline="") as f:
        t = f.read()
    b0 = int(b0)
    ws = [tuple(int(x) for x in w.split("-")) for w in wins.split(";") if w]
    lo = b0 if every else A._word_left(t, max(b0, ws[0][0] - n), b0)
    hi = len(t) if every else A._word_right(t, min(len(t), ws[-1][1] + n))
    out = ["[start of the text] " if lo <= b0 else "[...] "]
    cur = lo
    for pa, pb in ws:
        if pb <= lo or pa >= hi:
            continue
        out.append(t[cur:pa])
        out.append(">>> " + t[pa:pb] + " <<<")
        cur = pb
    out.append(t[cur:hi])
    out.append(" [end of the text]" if hi >= len(t) else " [...]")
    print("ITEM %s: the text shown in the item, characters %d-%d of %d (the pack's passages are between >>> and <<<)"
          % (a.item, lo - b0, hi - b0, len(t) - b0))
    print("".join(out))


if __name__ == "__main__":
    main()
