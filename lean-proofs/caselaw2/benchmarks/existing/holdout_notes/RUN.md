# Held-out later-court notes (round 5 Test 1) — folded results

Scorer `round5/tests/score_holdout.py`, docs `round5/tests/TESTS.md`. **Not a run-once test**: TESTS.md says it is
re-run with one command on each new output (the split and the testable pool are frozen; neither is rebuilt). So it
was re-run on round4 and round6. Statements by courts with **no power** over X ("X, overruled by Y", "rev'd, Y" ...)
never feed the model (`check_no_leak.py` passes: 0 leaks on both builds, 16 power-unknown warnings), so `blind: true`.
Caveat recorded in the notes: round-5 builders saw these aggregate scores at each iteration (`results/holdout_it*`).

Two datasets (pair level, Y named; one (X, Y) counted once, on its first holdout statement's date):

| file | dataset | tests | what |
|---|---|---|---|
| `results/<label>.all.json` | `holdout_notes` | overruling | precedent family (overruled, abrogated, disapproved, receded from), 12,354 pairs |
| `results/holdout_notes_history.<label>.all.json` | `holdout_notes_history` | same-case | history family (reversed, vacated), 20,843 pairs |

court `mixed` (federal and state targets). Primary `recall` = negOrPartly (X negative or partly negative, any actor,
on that date); `recall_strict` = whole-decision negative by Y; `recall_byAnyone`; `any_signal` (+ at-risk finding);
`precision` = reverse direction (of the model's whole-decision negative (X, actor) rows whose X a holdout note names
with a Y, the note names the model's actor). Precedent also: `pool_{all,alsoInFeed,holdoutOnly}_recall[_strict]`
(frozen testable pool, 9,374 pairs) and `recall_explicit` / `recall_notExplicit`.

## Commands (run by `../run_existing.py --only holdout`)

Copies in `../_r5tests/` (`common.py`, `score_holdout.py`, `check_no_leak.py`, `behaviour.py`). Only `common.py`
differs from the original (sha1 0d8ca215… vs 4f4df670…): its cache dir is `_r5tests/cache` instead of
`round5/tests/cache` (the round-6 data dir needed a new 100 MB decisions cache, which would otherwise have been
written into round5/tests); `split/` and the frozen pool are still read from round5/tests. The two existing caches
(round-4 decisions, edges) are hard links of the originals, not copies. `score_holdout.py` is byte-identical
(028904791961598205c47085f0eb872fb039596f).

```
python benchmarks/existing/_r5tests/check_no_leak.py <DATA>/treatments.tsv <DATA>/treatment_witness.tsv --certs <OUT>/certs.tsv --data <DATA>
python benchmarks/existing/_r5tests/score_holdout.py --status <OUT>/status.tsv --label <label> --data <DATA> --pool <R>/round5/tests/results/testable_pool_baseline-round4.tsv --out <R>/benchmarks/existing/holdout_notes/runs/<label>
```

`--pool` is passed explicitly because the scorer's default looks for the pool inside `--out`. `check_no_leak.py` is
given `--data` (TESTS.md omits it, so the original always used the live `data/` court tables).

| file | round4 | round6 |
|---|---|---|
| out/status.tsv | ece2365efc536dfcb39425e8c95efe842c57e3a6 | 96888c8b4381d3230e83d90c5d6f2fa45dfeeb8e |
| out/findings.tsv | 67a8b8a8e4a8358bca347c70ac65bad1907f3b95 | f007ad4c0c499fc248caf44fc19552027f29ca9f |
| out/certs.tsv | 0c9ef2f1676456bb11d94a4ec915fd6dd4ac3941 | 68f6fb621957748f9defe2235716ed9e1baa8146 |
| data/treatments.tsv | 4254db70505653eb847be5b0c54fbf20694f532a | 0cec8e582669ea4cfe11d177cc3f4063e62edb88 |
| data/decisions2.tsv | fd54596734f12a9fd3a739c55a82102f3c49213c | same file |
| split/holdout_ids.tsv | 6d444f307eb8ebfcee0a555a538809b810df274b | same |
| split/manifest.json | 16d8e1fbfd1b0dbd4a4c52a6e02cbe8045a2acbe | same |
| testable_pool_baseline-round4.tsv | ea5c4a9672190e1970845a8e7978c1c35ec4c22f | same |

**Agreement with earlier logs.** round4: `tables` and `reverse` identical to
`round5/tests/results/holdout_baseline-round4.json`; leak check 204 rows / 0 leaks / 16 warnings as in TESTS.md.
round6: leak check 6,315 rows resting on a speaker, 0 leaks, 16 warnings.

## Headline (Wilson 95%)

| | precedent recall (negOrPartly) | strict (neg by Y) | precision (reverse) | pool alsoInFeed / holdoutOnly |
|---|---|---|---|---|
| round4 | 3,264/12,354 = 26.4% (25.7–27.2) | 620/12,354 = 5.0% (4.6–5.4) | 598/641 = 93.3% (91.1–95.0) | 36/2,640 = 1.4% / 257/6,734 = 3.8% |
| round6 | 4,295/12,354 = 34.8% (33.9–35.6) | 745/12,354 = 6.0% (5.6–6.5) | 766/820 = 93.4% (91.5–94.9) | 940/2,640 = 35.6% / 425/6,734 = 6.3% |

| | history recall (negOrPartly) | strict | precision (reverse) |
|---|---|---|---|
| round4 | 2,379/20,843 = 11.4% (11.0–11.9) | 1,650/20,843 = 7.9% (7.6–8.3) | 1,623/1,726 = 94.0% (92.8–95.1) |
| round6 | 6,659/20,843 = 31.9% (31.3–32.6) | 4,367/20,843 = 21.0% (20.4–21.5) | 4,375/5,089 = 86.0% (85.0–86.9) |

Note: `check_no_leak.py` audits treatment/witness rows only, not `history.tsv`. Round 6's new same-case rows come
from the reviewing decision's own text (round6/history ROUND6.md), not from later-court notes, but the history
figures are not covered by the leak check.
