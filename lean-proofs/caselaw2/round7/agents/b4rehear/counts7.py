"""Counts of admitted rows (certify7 history_delta.tsv) by sub-class, court group and kind.

    python -X utf8 counts7.py CERT_DIR [CERT_DIR ...]      -> stdout, and counts7.json (merged)
"""
import sys

sys.dont_write_bytecode = True
import collections, json, os, re  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "round6", "history")))
import r6lib as L  # noqa: E402


def subclass(src):
    s = src.split(":")
    if s and s[0] == "r7":
        s = s[1:]
    if s[0] == "r7setaside":
        return "setaside/" + s[1]
    if s[1] == "enbanc":
        v = s[2].split("-")[0] + "-" + s[2].split("-")[1]
        return "enbanc-silent" if v == "c-reh" else ("enbanc-order" if v == "c-order" else "enbanc-act")
    return "docket"


def main():
    F = L.Facts()
    out = {}
    for d in sys.argv[1:]:
        cnt = collections.Counter()
        for line in open(os.path.join(d, "history_delta.tsv"), encoding="utf-8"):
            p = line.rstrip("\n").split("\t")
            by, kind, src = int(p[2]), p[4], p[12]
            c = int(F.court[by])
            grp = "federal" if F.system(c) == 0 else "state"
            name = F.court_name(c)
            sc = subclass(src)
            cnt["%s|total" % sc] += 1
            cnt["%s|group|%s" % (sc, grp)] += 1
            cnt["%s|kind|%s" % (sc, kind)] += 1
            cnt["%s|court|%s" % (sc, name)] += 1
            cnt["%s|decade|%ds" % (sc, int(F.date[by]) // 100000 * 10)] += 1
        out[os.path.basename(os.path.normpath(d))] = dict(sorted(cnt.items()))
        for k, v in sorted(cnt.items()):
            if "|court|" in k and v < 5:
                continue
            print(os.path.basename(os.path.normpath(d)), k, v)
    json.dump(out, open(os.path.join(HERE, "counts7.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
