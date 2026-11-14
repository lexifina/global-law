"""b4sc: final delta folders (certify7 outputs merged, the round-6 guard's drops applied).

    python -X utf8 deltas.py   -> delta_a/ (B4 a: cert_a), delta_e/ (B4 e: cert_e + cert_e_other)
Rows whose id is in work/guard/*_drop_ids.txt (round 6's kept guard groups, unchanged, run by gfeat7.py/guard7.py)
are left out of history_delta.tsv and history_anchor_delta.tsv; windows, hashes and index lines are merged (sorted,
unique). A stage7 `--delta` takes each folder as is.
"""
import os

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
    drop = set()
    gd = os.path.join(HERE, "work", "guard")
    for f in os.listdir(gd):
        if f.endswith("_drop_ids.txt"):
            drop |= set(lines(os.path.join(gd, f)))
    for name, srcs in (("delta_a", ["cert_a"]), ("delta_e", ["cert_e", "cert_e_other"])):
        out = os.path.join(HERE, name)
        os.makedirs(out, exist_ok=True)
        counts = {}
        for t in TABLES:
            acc = []
            seen = set()
            for s in srcs:
                for l in lines(os.path.join(HERE, s, t)):
                    if t.startswith("history") and l.split("\t")[0] in drop:
                        continue
                    if l in seen:
                        continue
                    seen.add(l)
                    acc.append(l)
            with open(os.path.join(out, t), "w", encoding="utf-8", newline="\n") as f:
                for l in acc:
                    f.write(l + "\n")
            counts[t] = len(acc)
        print(name, counts)


if __name__ == "__main__":
    main()
