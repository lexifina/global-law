# SCDB precedentAlteration and Constitution Annotated (CRS) overruled table — folded results

Scorer `~\gl-pub\lean-proofs\tools\caselaw2\eval\score.py` (sha1 fae0261ded223113e68926cafa92285c55fb9ea0;
byte-identical to the `global-law-lean` copy that `round5/score_all.sh` calls). Keys `gold/scdb.tsv`
(7ddf2d7ac2123f064ce90c403a0ee65e2b1e1f63), `gold/crs_overruled.tsv` (87216e8c061086aa1893755706bc51c6303b22a6).
Both **not blind** (`blind: false`): rounds 1–4 were evaluated and tuned against them (`eval/score_round*.txt`).
tests `overruling`, court `supreme`, split `all`.

| file | dataset | primary |
|---|---|---|
| `results/scdb_precedent_alteration.<label>.all.json` | `scdb_precedent_alteration` | recall = SCDB-flagged decisions with an admitted overruling of a Supreme Court decision; precision = of Supreme Court decisions the model has overruling one, SCDB flags it |
| `results/conan_overruled.<label>.all.json` | `conan_overruled` | recall = current CRS table pairs admitted (`recall_2016_express`, `recall_2016_all` also); precision = admitted SC-on-SC pairs in any CRS edition; link_rate = resolved pairs |

## Commands (run by `../run_existing.py --only scdb`; the scorer takes `--results`, so the original is run)

```
python <gl-pub>/lean-proofs/tools/caselaw2/eval/score.py --out <R>/out --data <R>/data --results <R>/benchmarks/existing/scdb_conan/runs/round4
python <gl-pub>/lean-proofs/tools/caselaw2/eval/score.py --out <R>/round6/history/out/final2 --data <R>/round6/history/stage/final2 --results <R>/benchmarks/existing/scdb_conan/runs/round6
```

| file | round4 | round6 |
|---|---|---|
| out/status.tsv | ece2365efc536dfcb39425e8c95efe842c57e3a6 | 96888c8b4381d3230e83d90c5d6f2fa45dfeeb8e |
| out/certs.tsv | 0c9ef2f1676456bb11d94a4ec915fd6dd4ac3941 | 68f6fb621957748f9defe2235716ed9e1baa8146 |
| data/treatments.tsv | 4254db70505653eb847be5b0c54fbf20694f532a | 0cec8e582669ea4cfe11d177cc3f4063e62edb88 |
| data/history.tsv | d96f654ec1581207e60b809fa759a03770068322 | 7b9a3ada46b6b3dd32ec95958b301056db1bfb56 |
| data/decisions2.tsv | fd54596734f12a9fd3a739c55a82102f3c49213c | same file |

**Agreement with earlier logs.** round4: `scdb` and `crs` sections identical to `caselaw-lean-2/eval/results.json`
(= `eval/score_final.txt`, 2026-11-12 23:29), same input counts (25,035 admitted).

## Headline (Wilson 95%) — identical on both builds

| | round4 | round6 |
|---|---|---|
| SCDB recall | 141/278 = 50.7% (44.9–56.5) | 141/278 = 50.7% (44.9–56.5) |
| SCDB precision | 141/152 = 92.8% (87.5–95.9) | same |
| CRS current recall | 162/292 = 55.5% (49.7–61.1) | same |
| CRS 2016 express | 135/243 = 55.6% (49.3–61.7) | same |
| CRS precision (any edition) | 163/187 = 87.2% (81.6–91.2) | same |

Why unchanged: this scorer counts only admitted explicit treatment rows, and round 6 has the same 25,035 admitted
rows as round 4 (treatments rows grew 35,365 → 41,476, but none of the added rows passes this scorer's filter:
certificate ok, explicit = 1, a status-changing kind, not the implicit tier). Round 5's gains are "recognised"
status rows, which this scorer does not read. ROUND5.md (line 48–49) reports 175/278 SCDB and 195/292
CRS "with recognised rows" from another scorer; those are not reproduced by this one and are not folded here.
