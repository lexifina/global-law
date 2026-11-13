"""Sample rejected candidates for the blind audit: half rejected by the model or the certificate check, half by the
cheap filters (only sentences with a status verb: overrule, disapprove, recede, abrogate, supersede).

    python -X utf8 reject_sample.py <reader_rejects.tsv> <out pack.jsonl> <n> <seed>
"""
import glob, gzip, json, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK  # noqa: E402
from audit_pack import node_info  # noqa: E402

STRONG = re.compile(r"overrul|disapprov|reced\w*\s+from|abrogat|supersed", re.I)


def main():
    rej_path, out, n, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    rnd = random.Random(seed)
    model_rej = [l.rstrip("\n").split("\t") for l in open(rej_path, encoding="utf-8")]
    rnd.shuffle(model_rej)
    want_model = {r[0]: r[2] for r in model_rej[: n // 2]}
    # cheap rejects: reservoir over every repo's rejects, excluding procedural noise that never names a decision
    cheap = []
    k = 0
    for f in sorted(glob.glob(os.path.join(WORK, "res", "*.rejects.tsv.gz"))):
        repo = os.path.basename(f)[:-len(".rejects.tsv.gz")]
        for line in gzip.open(f, "rt", encoding="utf-8"):
            i, why, fam = line.rstrip("\n").split("\t")
            if not re.search(r"overrule|disapprove|recede|abrogate|supersede", fam):
                continue
            k += 1
            if len(cheap) < 4000:
                cheap.append((i, why, repo))
            else:
                j = rnd.randrange(k)
                if j < 4000:
                    cheap[j] = (i, why, repo)
    rnd.shuffle(cheap)
    recs = []
    # model rejects come from items
    items = {}
    for f in glob.glob(os.path.join(WORK, "res", "*.items.jsonl.gz")):
        for line in gzip.open(f, "rt", encoding="utf-8"):
            i = line[8:line.index('"', 8)]
            if i in want_model:
                items[i] = json.loads(line)
    for i, why in want_model.items():
        it = items.get(i)
        if it is None:
            continue
        a, b = max(it["w0"], it["s0"] - 600), min(it["w1"], it["s1"] + 600)
        recs.append({"audit_id": i, "type": "candidate", "n": it["n"], "part": it["part"].rstrip("~"),
                     "focus": it["w"][it["s0"] - it["w0"]:it["s1"] - it["w0"]], "window": it["w"][a - it["w0"]:b - it["w0"]],
                     "candidate_targets": [{x: t[x] for x in ("name", "court", "year", "cite", "node")} for t in it["targets"]],
                     "_stage": "model:" + why})
    # cheap rejects come from the candidate files
    need = {}
    for i, why, repo in cheap[: 3 * (n - n // 2)]:
        need.setdefault(repo, {})[i] = why
    got = []
    for repo, ids in need.items():
        for line in gzip.open(os.path.join(WORK, "cand", repo + ".jsonl.gz"), "rt", encoding="utf-8"):
            r = json.loads(line)
            if r["t"] != "c":
                continue
            i = f"{r['n']}:{r['s0']}"
            if i in ids:
                sent = r["w"][r["s0"] - r["w0"]:r["s1"] - r["w0"]]
                if not STRONG.search(sent):
                    continue
                a, b = max(r["w0"], r["s0"] - 600), min(r["w1"], r["s1"] + 600)
                got.append({"audit_id": i, "type": "candidate", "n": r["n"], "part": r["part"].rstrip("~"),
                            "focus": sent, "window": r["w"][a - r["w0"]:b - r["w0"]], "candidate_targets": [],
                            "_stage": "cheap:" + ids[i]})
    rnd.shuffle(got)
    recs += got[: n - len(recs)]
    ni = node_info({r["n"] for r in recs})
    with open(out, "w", encoding="utf-8", newline="\n") as fo:
        for r in recs:
            r["deciding"] = ni[r.pop("n")]
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(recs), "rejected candidates sampled")


if __name__ == "__main__":
    main()
