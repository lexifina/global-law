"""Live check of detectors/dead_fine.py on the real corpora, without a full run: only the acts named below are read.

python bench/dead_fine_bench.py          -> prints a table, writes bench/out/dead_fine_bench.json

POSITIVES: penalty provisions confirmed against official sources whose trigger points at a repealed or deleted provision.
NEGATIVES: provisions an earlier detector flagged wrongly (another act's section with the same number); must stay silent.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ingest")); sys.path.insert(0, str(ROOT / "detectors"))
from common import CORPUS, pins  # noqa: E402
from dead_fine import scan_corpus  # noqa: E402

# (case, repo, act folder, citing path regex, reference key)
POSITIVES = [
    ("DE AWaffV § 34 no. 11 → § 12 (weggefallen)", "germany-law", "awaffv", r"^awaffv/0034\.md$", "12"),
    ("DE EIGV § 41(2) no. 5 → § 38 (weggefallen)", "germany-law", "eigv", r"^eigv/0041\.md$", "38"),
    ("DE SchSiHafV § 42 no. 33 → § 27 (weggefallen)", "germany-law", "schsihafv", r"^schsihafv/0042\.md$", "27"),
    ("DE SchSiHafV § 42 no. 34 → § 29 (weggefallen)", "germany-law", "schsihafv", r"^schsihafv/0042\.md$", "29"),
    ("DE SchSiHafV § 42 no. 35 → § 30 (weggefallen)", "germany-law", "schsihafv", r"^schsihafv/0042\.md$", "30"),
    ("DE FuttMV § 40(1) no. 1 → § 4 (weggefallen)", "germany-law", "futtmv_1981", r"^futtmv_1981/0040\.md$", "4"),
    ("DE EnergieStV § 111(1) no. 17 → § 101 (weggefallen)", "germany-law", "energiestv", r"^energiestv/0111\.md$", "101"),
    ("MT Cap. 10 art. 319 → art. 190 (repealed)", "malta-law", "cap/10", r"^cap/10/319\.md$", "190"),
    ("FJ VAT Act s 71 → s 63 (repealed)", "fiji-law", "acts/value-added-tax-act-1991", r"/S71\.md$", "63"),
]
NEGATIVES = [  # (case, repo, act folder, citing path regex, reference key that must not be flagged)
    ("DE AromenV § 7 → § 60 LFGB (other act)", "germany-law", "aromendv", r"^aromendv/0007\.md$", "60"),
    ("DE KaffeeV § 5 → § 60 LFGB (other act)", "germany-law", "kaffeev_2001", r"^kaffeev_2001/0005\.md$", "60"),
    ("DE ChemG § 27 → §§ 328, 330 StGB (other act)", "germany-law", "chemg", r"^chemg/0027\.md$", "328"),
    ("DE AntarktUmwSchProtAG § 37 → § 324 StGB (other act)", "germany-law", "antarktumwschprotag", r"^antarktumwschprotag/0037\.md$", "324"),
    ("DE KVLG 1989 § 57 → § 202 SGB V (other act)", "germany-law", "kvlg_1989", r"^kvlg_1989/0057\.md$", "202"),
    ("DE AWG § 18 → § 46 AWV (other act)", "germany-law", "awg_2013", r"^awg_2013/0018\.md$", "46"),
]


def main():
    by_repo: dict[str, set[str]] = {}
    for _, repo, act, *_ in POSITIVES + NEGATIVES:
        by_repo.setdefault(repo, set()).add(act)
    corp = {c["repo"]: c for c in pins()["corpora"]}
    flags = []
    for repo, acts in by_repo.items():
        if repo in corp and (CORPUS / f"{repo}.git").exists():
            flags += scan_corpus(corp[repo], acts)
    res = []
    for kind, cases in (("positive", POSITIVES), ("negative", NEGATIVES)):
        for name, repo, _, prx, ref in cases:
            hit = any(f["repo"] == repo and re.search(prx, f["path"]) and f["ref"] == ref for f in flags)
            res.append({"case": name, "kind": kind, "flagged": hit, "ok": hit if kind == "positive" else not hit})
    w = max(len(r["case"]) for r in res)
    for r in res:
        print(f"{'✔' if r['ok'] else '✘'} {r['kind']:<8} {r['case']:<{w}}")
    pos = [r for r in res if r["kind"] == "positive"]; neg = [r for r in res if r["kind"] == "negative"]
    print(f"\nrecall on confirmed dead fines: {sum(r['ok'] for r in pos)}/{len(pos)}; "
          f"known false positives avoided: {sum(r['ok'] for r in neg)}/{len(neg)}; flags in these acts: {len(flags)}")
    out = ROOT / "bench" / "out"; out.mkdir(parents=True, exist_ok=True)
    (out / "dead_fine_bench.json").write_text(json.dumps({"cases": res, "flags": flags}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if all(r["ok"] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
