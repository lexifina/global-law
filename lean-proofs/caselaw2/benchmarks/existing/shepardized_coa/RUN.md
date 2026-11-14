# Shepardized Courts of Appeals Database (same-case history) — folded results

Dataset name `shepardized_coa`; tests `same-case`; court `federal`. Scorer `round6/shepardized/compare.py`
(mapping `round6/shepardized/MAPPING.md`, unchanged since first scoring). As-of 2010-11-19.

Primary metric `recall` = Shepardized `NEG` (Supreme Court reversed/vacated, panel opinion withdrawn, different
result en banc) shown `NEG_HIST` by the model (strict). `precision` = of model `NEG_HIST`, Shepardized `NEG`
(strict, `AMBIG` left out). Also `recall_lenient` (NEG_HIST or UNK_HIST), `recall_part`, `clean`, `mod_kept`,
`agreement`, `recall_sub_*`, and every dev/sealed-log figure again as `*_setaside` (the documented database errors of
`round6/history/shep_errors.tsv` left out of numerator and denominator). `link_rate` = cases linked to one corpus decision.

## Files

| split | label | file | how |
|---|---|---|---|
| dev | round4 | `results/round4.dev.json` | **re-run** here |
| dev | round6 | `results/round6.dev.json` | **re-run** here |
| sealed | round4 | `results/round4.sealed.json` | **derived from logs** (arithmetic: all cases minus dev; not a sealed run) |
| sealed | round6 | `results/round6.sealed.json` | **reused from log** `round6/history/SEALED_LOG.md` line 5 |

## Dev re-runs (exact commands; run by `../run_existing.py --only shep`)

```
python -I round6/shepardized/compare.py --split dev --out <R>/out --data <R>/data --results <R>/benchmarks/existing/shepardized_coa/runs/round4_dev
python -I round6/shepardized/compare.py --split dev --out <R>/round6/history/out/final2 --data <R>/round6/history/stage/final2 --results <R>/benchmarks/existing/shepardized_coa/runs/round6_dev
```

Python 3.12.10 (Windows). Outputs: `runs/<label>_dev/{headline.tsv,tables.tsv,cases_dev.tsv,compare.log,inputs.json}`.

Input sha1 (also in `runs/*/inputs.json`):

| file | round4 | round6 (final2) |
|---|---|---|
| compare.py | 3dd792c9c8e82c4e6a85583529943213f83ed44e | same |
| out/status.tsv | ece2365efc536dfcb39425e8c95efe842c57e3a6 | 96888c8b4381d3230e83d90c5d6f2fa45dfeeb8e |
| out/certs.tsv | 0c9ef2f1676456bb11d94a4ec915fd6dd4ac3941 | 68f6fb621957748f9defe2235716ed9e1baa8146 |
| data/history.tsv | d96f654ec1581207e60b809fa759a03770068322 | 7b9a3ada46b6b3dd32ec95958b301056db1bfb56 |
| work/shepardized.tsv | b14ca4c039193dfbd7f85063e1215517251c1780 | same |
| results/links.tsv | 66e91eef84892eb8e5f32b9c9cfca85d6c8e7ecf | same |
| history/split/dev.tsv | 327d276d1802f92469b547be775483159ff53dac | same |
| history/shep_errors.tsv | 58111b4cd2cd45cbb2e6485d8fa47b96fb7192ab | same |

The round-6 status/certs/history sha1s are the ones recorded in the sealed log line, so the dev re-run and the
sealed run are on the same build.

**Agreement with earlier logs.** `round6/history/results/baseline/headline.tsv` (round 4) and
`round6/history/results/final2/headline.tsv`: every raw figure identical. For final2 the set-aside columns are
identical too. For the round-4 baseline the set-aside columns differ only because `shep_errors.tsv` listed 4 errors
when the baseline was written and 11 now (agreement set-aside 9723/9984 then, 9717/9977 now; recall set-aside
6/253 both times).

## Sealed (NOT run here)

- **round6** (`final2`): parsed from the single line of `round6/history/SEALED_LOG.md` (sha1
  a00d613f1a9267c11c73f96ce312d137001fdc80), `compare.py --split sealed` of 2026-11-13T18:23:37, run once by the
  round-6 lead after `FREEZE.md`. k/n raw and bracketed set-aside; Wilson recomputed with `benchlib.metric`. The log
  has no sub-class split.
- **round4**: there is no sealed run on round 4. Values = round-4 aggregate over all cases
  (`round6/shepardized/results/asof20101119/tables.tsv`, sha1 78ce6bbb1805c02de800ee304245e52852cfb2ca, aggregate
  lines only; its header names the round-4 `out/`) minus the round-4 dev re-run above. This is the "sealed before"
  column of `round6/history/ROUND6.md` (sha1 987200fd7720507c0a03f8f79bf44866e5ded275): "the round-4 figure over all
  cases minus the dev half (arithmetic, not a second sealed run)". `fold_logged.py` checks each ROUND6.md cell
  (recall 8/252, sub-classes 5/132, 3/61, 0/25, 0/33, part 1/16, precision 8/9, clean 9,586/9,586, modified 13/13)
  equals the subtraction, and stops otherwise. No set-aside variant exists for it.
- Sealed `link_rate` (9,897 / 10,105) is the counts table of `round6/history/split/SPLIT.md`.

## Blind flag

`round4.dev`, both sealed files: `blind: true`. `round6.dev`: **`blind: false`** — the dev half was open to the
round-6 builders, who read its misses and false positives case by case (`DESIGN6.md` 1, `results/*/dev_misses.tsv`).
The sealed half is the blind figure for round 6.

## Headline (Wilson 95%)

| | round4 dev | round6 dev | round4 sealed (derived) | round6 sealed (log) |
|---|---|---|---|---|
| recall (NEG strict) | 6/254 = 2.4% (1.1–5.1) | 105/254 = 41.3% (35.5–47.5) | 8/252 = 3.2% (1.6–6.1) | 104/252 = 41.3% (35.4–47.4) |
| precision (strict) | 6/9 = 66.7% (35.4–87.9) | 105/111 = 94.6% (88.7–97.5) | 8/9 = 88.9% (56.5–98.0) | 104/113 = 92.0% (85.6–95.8) |
| clean | 9,701/9,704 = 99.97% | 9,698/9,704 = 99.94% | 9,586/9,586 = 100% | 9,579/9,586 = 99.93% |
| link rate | 10,019/10,249 | 10,019/10,249 | 9,897/10,105 | 9,897/10,105 |

One discrepancy in the earlier write-up, not in any scorer output: `ROUND6.md` gives dev `final2` precision with
errors set aside as 105/108 = 97.2%; the re-run and the logged `final2/headline.tsv` both give 105/110 (95.5%).
