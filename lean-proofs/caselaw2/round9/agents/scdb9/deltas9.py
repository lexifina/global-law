"""scdb8: delta folders from certify8 output with the round-6 guard's drops applied (as round 7's deltas.py), split by
class, and the R4 remove list restricted to replacements that survive.

    python -X utf8 deltas8.py <cert dir> <guard drop ids> <out prefix> [--classes disp,r4,r5]
        -> <out prefix>_<cls>/ delta folders (one per class) + <out prefix>_all/, and <out prefix>_remove_r4.txt
Class of a row = its rule id: below:sc9_<cls>_... (disp | r4 | r4rep -> r4 | r5).
"""
import collections, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = ["history_delta.tsv", "history_anchor_delta.tsv", "history_claim_delta.tsv", "cert_text_delta.tsv",
          "window_sha_delta.tsv", "cite_index_delta.tsv", "treatments_delta.tsv", "treatment_class_delta.tsv",
          "joined_delta.tsv"]
NL = "\n"


def lines(p):
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline=NL) as f:
        return [l for l in f.read().split(NL) if l]


def cls_of(src):
    s = src.split("below:sc9_", 1)[1]
    c = s.split("_", 1)[0]
    return "r4w" if c.startswith("r4w") else c


def main():
    cert, dropf, pre = sys.argv[1], sys.argv[2], sys.argv[3]
    drop = set(lines(dropf))
    hist = [l for l in lines(os.path.join(cert, "history_delta.tsv")) if l.split("\t")[0] not in drop]
    by_cls = collections.defaultdict(set)
    for l in hist:
        p = l.split("\t")
        by_cls[cls_of(p[12])].add(p[0])
    by_cls["all"] = {l.split("\t")[0] for l in hist}
    counts = {}
    for c, ids in by_cls.items():
        out = pre + "_" + c
        os.makedirs(out, exist_ok=True)
        cc = {}
        for t in TABLES:
            acc = lines(os.path.join(cert, t))
            if t.startswith("history"):
                acc = [l for l in acc if l.split("\t")[0] in ids]
            with open(os.path.join(out, t), "w", encoding="utf-8", newline=NL) as f:
                for l in acc:
                    f.write(l + NL)
            cc[t] = len(acc)
        counts[c] = cc["history_delta.tsv"]
    print("history rows by class:", counts, "| guard drops:", len(drop & {l.split("\t")[0] for l in lines(os.path.join(cert, "history_delta.tsv"))}))


if __name__ == "__main__":
    main()
