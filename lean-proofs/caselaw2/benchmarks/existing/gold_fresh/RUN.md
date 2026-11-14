# Fresh overruling lists (round 5 key) — folded results

Dataset `gold_fresh`; tests `overruling`; court `supreme` (both sides of every pair are Supreme Court decisions:
the key resolves only against `gold/work/scotus_nodes.tsv`). Key and scorer: `round5/gold_fresh/` (`GOLD_FRESH.md`).

Primary `recall` = lenient (overruled X is `neg:*` or `unknown:*` in status.tsv: outcomes a, a_date, a_kind, b, c).
`recall_strict` = outcome a (neg:overruled/abrogated by the listed Y from Y's date). Breakdowns `recall_[strict_]
{express,implied,full,partial,inCRS,notInCRS}`. `precision` = of the model's Supreme-Court-on-Supreme-Court
overrulings in this half, the share on a fresh list (`listed`; "unlisted" is not "wrong", so a lower bound).
`link_rate` 100% by construction (pairs are scoreable pairs).

## Files

| split | label | file | how |
|---|---|---|---|
| dev | round4 | `results/round4.dev.json` | **re-run** here |
| dev | round6 | `results/round6.dev.json` | **re-run** here |
| sealed | round4 | `results/round4.sealed.json` | **reused**: `round5/gold_fresh/sealed/results/baseline-round4.json` (sha1 642dfb581d3f2d0c29789fa291591fd699d34b00) |
| sealed | round5 | `results/round5.sealed.json` | **reused**: `round5/gold_fresh/sealed/results/final-frozen.json` (sha1 aa25836698209fe92b6df144136da287aed1c6af), the round-5 frozen build `round5/out/final` |

**No sealed run exists on round6 `final2`.** The sealed half was scored once (on round 5) and is not re-run here;
`TEST_RUNS.log` was not touched. Only the two sealed result JSONs above were read; no sealed key row.

## Dev re-runs

`score_fresh.py` hard-codes its output to `round5/gold_fresh/dev/results/`, so a copy is run:
`scorer/score_fresh_copy.py` (sha1 9ebcffae7f1f0db5aecac2c7c7e338e7f41ddf6f; original c16db05b9a7cee5d139a531d9439ee316bab3b27).
Diff against the original: paths only — `HERE` points at the original `round5/gold_fresh` (key and meta read there),
output goes to `--results-dir`, and `--split test` is refused. Scoring logic unchanged.

```
python -I benchmarks/existing/gold_fresh/scorer/score_fresh_copy.py --split dev --status <R>/out/status.tsv --treatments <R>/data/treatments.tsv --label round4 --results-dir <R>/benchmarks/existing/gold_fresh/runs/round4
python -I benchmarks/existing/gold_fresh/scorer/score_fresh_copy.py --split dev --status <R>/round6/history/out/final2/status.tsv --treatments <R>/round6/history/stage/final2/treatments.tsv --label round6 --results-dir <R>/benchmarks/existing/gold_fresh/runs/round6
```

(`--findings` defaults to findings.tsv beside `--status`.) Input sha1 (`runs/*/inputs.json`):

| file | round4 | round6 |
|---|---|---|
| out/status.tsv | ece2365efc536dfcb39425e8c95efe842c57e3a6 | 96888c8b4381d3230e83d90c5d6f2fa45dfeeb8e |
| out/findings.tsv | 67a8b8a8e4a8358bca347c70ac65bad1907f3b95 | f007ad4c0c499fc248caf44fc19552027f29ca9f |
| data/treatments.tsv | 4254db70505653eb847be5b0c54fbf20694f532a | 0cec8e582669ea4cfe11d177cc3f4063e62edb88 |
| dev/dev.tsv | fc068b3a4987f3f1bd67fd3157d0c4cdcbb69ec0 | same |
| work/scotus_meta.tsv | b6e585177e2854100e95e90bd7538f5683f0e949 | same |

**Agreement with earlier logs.** round4 dev: recall tables and precision side identical to
`round5/gold_fresh/dev/results/baseline-round4.json` (same status sha1). round6 dev: outcome counts identical to the
round-5 `final.json` dev result (a 50, a_date 30, b 5, c 23, e 57; precision 80 listed / 1 other overruler / 12
unlisted) — round 6 changed same-case history only.

## Blind flag

Sealed files and `round4.dev`: blind. `round6.dev`: **not blind** — the dev half was open to the round-5 builders
(scored at every iteration: `dev/results/it0_claims…final`, ROUND5.md), and round 6 contains round 5.

## Headline (Wilson 95%)

| | recall (lenient) | recall_strict | precision (listed) |
|---|---|---|---|
| round4 dev | 86/165 = 52.1% (44.5–59.6) | 50/165 = 30.3% (23.8–37.7) | 50/53 = 94.3% (84.6–98.1) |
| round6 dev | 108/165 = 65.5% (57.9–72.3) | 50/165 = 30.3% (23.8–37.7) | 80/93 = 86.0% (77.5–91.6) |
| round4 sealed | 59/127 = 46.5% (38.0–55.1) | 32/127 = 25.2% (18.5–33.4) | 32/43 = 74.4% (59.8–85.1) |
| round5 sealed | 77/127 = 60.6% (51.9–68.7) | 32/127 = 25.2% (18.5–33.4) | 57/76 = 75.0% (64.2–83.4) |

Rounding only: the strict sealed lower bound is 0.18451 (benchlib and the scorer agree); GOLD_FRESH.md / ROUND5.md
print it as 18.4, the table above as 18.5.
