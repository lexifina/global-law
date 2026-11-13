# Round 3 resume: agent bench (bulk court-size pass)

Start 23:03 (12 Nov 2026). Time box 30 minutes.

## State found (23:05)

- `work/round3/bench/bench3r.tsv`: 2,433,434 rows, complete (scan.log: 2,198,264 tier L unknown, 235,170 tier A panel in small or full-court years; 0 missing blobs).
- `features.tsv`: 2,433,434 rows, last line whole. Complete; not rebuilt.
- `decide.py` writes features only; the rule step that writes the candidates was not in it. `t_decide.py` is the same script on a 300,000-row sample (`t/`).
- `ref_before/`: baseline reference run, 151,685 findings, 71,848 status rows.
- Nothing installed: `data/decisions2.tsv` dated 22:26, no `decisions2.pre_round3.tsv`, no lock.

## Stopped (23:12)

The coordinator dropped this item for this round. State at stop:

- Scan done and features complete (above). `decide.py` is unchanged: it builds `features.tsv` and has no rule step. No `cand.tsv` or `bench_delta.tsv` for the full set exists (`t/cand.tsv` is an old 300,000-row sample output).
- Added only `work/round3/bench/explore.py` (read-only count of rows passing the round-2 size rule in `features.tsv`).
- No reviewers launched. No reference run. No lock, no `.tmp`, no `decisions2.pre_round3.tsv`. `data/decisions2.tsv` not touched.

## Next round

1. Rule step: tier L unknown and tier A panel (size <= 3 or full year), sitting >= 2, sitting + out equal to size, support >= 5, no non-regular names, court key not a unit, DIVISION_UNITS excluded. Write `bench_delta.tsv` (node, old, new, reason).
2. Blind review of at least 40 relabels (`make_sheets.py`, `score.py`), exclude failing courts.
3. Install column 5 only by node id under the lock (`install.py` also rewrites the src column: change it first).
4. One reference run against `ref_before/` (151,685 findings).
