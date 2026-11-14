"""fjc8: delta folder = certify8 output minus the round-6 guard's drops (as round7 b4sc deltas.py).

    python -X utf8 deltas.py OUT CERT_DIR [CERT_DIR ...] --drop work/guard/x_drop_ids.txt [--drop ...]
                             [--only-rule REGEX] [--skip-kind kind,kind]
"""
import argparse, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = ["history_delta.tsv", "history_anchor_delta.tsv", "history_claim_delta.tsv", "cert_text_delta.tsv",
          "window_sha_delta.tsv", "cite_index_delta.tsv", "treatments_delta.tsv", "treatment_class_delta.tsv",
          "joined_delta.tsv"]


def lines(p):
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="\n") as f:
        return [l for l in f.read().split("\n") if l]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("certs", nargs="+")
    ap.add_argument("--drop", action="append", default=[])
    ap.add_argument("--only-rule")
    ap.add_argument("--skip-kind", default="")
    a = ap.parse_args()
    drop = set()
    for f in a.drop:
        drop |= set(lines(f))
    skip_kind = set(k for k in a.skip_kind.split(",") if k)
    keep_ids = None
    if a.only_rule or skip_kind:
        keep_ids = set()
        rx = re.compile(a.only_rule) if a.only_rule else None
        for s in a.certs:
            for l in lines(os.path.join(s, "history_delta.tsv")):
                p = l.split("\t")
                if (rx is None or rx.search(p[12])) and p[4] not in skip_kind:
                    keep_ids.add(p[0])
    os.makedirs(a.out, exist_ok=True)
    counts = {}
    for t in TABLES:
        acc, seen = [], set()
        for s in a.certs:
            for l in lines(os.path.join(s, t)):
                if t.startswith("history"):
                    i = l.split("\t")[0]
                    if i in drop or (keep_ids is not None and i not in keep_ids):
                        continue
                if l in seen:
                    continue
                seen.add(l)
                acc.append(l)
        with open(os.path.join(a.out, t), "w", encoding="utf-8", newline="\n") as f:
            for l in acc:
                f.write(l + "\n")
        counts[t] = len(acc)
    print(a.out, counts)


if __name__ == "__main__":
    main()
