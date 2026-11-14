"""Blind audit: print a wider passage of the speaking decision's text for one item, and nothing else.

    python round5/audit/more_text.py <item id> [chars | all] [--name <audit name>]

`chars` = extra characters on each side of the pack's passage (default 3000; `all` = the whole opinion text).
The pack's passage stands between `>>>` and `<<<`. Line breaks are turned into spaces, as in the packs. The front
matter of the decision file is never printed. `--name` is only needed if two audits share an item id.
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_common as AC  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("item")
    ap.add_argument("chars", nargs="?", default="3000")
    ap.add_argument("--name")
    a = ap.parse_args()
    AC.utf8_stdout()
    hits = []
    for d in sorted(os.listdir(AC.HERE)):
        if a.name and d != a.name:
            continue
        ip = os.path.join(AC.HERE, d, "store", "index.tsv")
        if os.path.exists(ip):
            for p in AC.read_rows(ip, 5):
                if p[0] == a.item:
                    hits.append((d, p))
    if not hits:
        sys.exit("unknown item id " + a.item)
    if len(hits) > 1:
        sys.exit("item id %s exists in several audits: give --name <audit name>" % a.item)
    d, (_, sha, body0, pa, pb) = hits[0]
    body0, pa, pb = int(body0), int(pa), int(pb)
    with open(os.path.join(AC.HERE, d, "store", "text", sha + ".txt"), encoding="utf-8", newline="") as f:
        ct = AC.clean(f.read())
    if a.chars.lower() == "all":
        lo, hi = body0, len(ct)
    else:
        try:
            n = max(0, int(a.chars))
        except ValueError:
            sys.exit("chars: a number, or all")
        lo, hi = max(body0, pa - n), min(len(ct), pb + n)
        for _ in range(40):
            if lo <= body0 or ct[lo - 1] == " ":
                break
            lo -= 1
        for _ in range(40):
            if hi >= len(ct) or ct[hi] == " ":
                break
            hi += 1
    print("ITEM %s: text of the speaking decision, characters %d-%d of %d (the pack's passage is between >>> and <<<)"
          % (a.item, lo - body0, hi - body0, len(ct) - body0))
    print(("… " if lo > body0 else "[start of the text] ") + ct[lo:pa] + ">>> " + ct[pa:pb] + " <<<" + ct[pb:hi]
          + (" …" if hi < len(ct) else " [end of the text]"))


if __name__ == "__main__":
    main()
