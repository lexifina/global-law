"""Draw a stratified sample of model items (by family/why), for the development or the held-out audit.

    python -X utf8 sample_ids.py <out.tsv> <n> <seed> [--exclude ids.tsv ...] [--repos r1,r2]
"""
import collections, glob, gzip, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK  # noqa: E402


def main():
    out, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    excl = set()
    repos = None
    a = sys.argv[4:]
    while a:
        if a[0] == "--exclude":
            excl |= {l.split("\t")[0].strip() for l in open(a[1], encoding="utf-8") if l.strip()}
            a = a[2:]
        elif a[0] == "--repos":
            repos = set(a[1].split(","))
            a = a[2:]
        else:
            raise SystemExit("bad arg " + a[0])
    by = collections.defaultdict(list)
    for f in glob.glob(os.path.join(WORK, "res", "*.items.jsonl.gz")):
        repo = os.path.basename(f)[:-len(".items.jsonl.gz")]
        if repos and repo not in repos:
            continue
        for line in gzip.open(f, "rt", encoding="utf-8"):
            it = json.loads(line)
            if it["id"] in excl:
                continue
            by[it["why"].split(":")[0]].append((it["id"], repo, it["why"]))
    rnd = random.Random(seed)
    k = max(1, n // len(by))
    pick = []
    for fam, xs in sorted(by.items()):
        rnd.shuffle(xs)
        pick += xs[:k]
    rest = [x for fam, xs in by.items() for x in xs[k:]]
    rnd.shuffle(rest)
    pick += rest[:max(0, n - len(pick))]
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for i, r, w in pick:
            f.write(f"{i}\t{r}\t{w}\n")
    print(len(pick), {f: len(x) for f, x in by.items()})


if __name__ == "__main__":
    main()
