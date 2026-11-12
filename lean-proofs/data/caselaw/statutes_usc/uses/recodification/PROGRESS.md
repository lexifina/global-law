# (8) Recodification checks: PROGRESS

Status 2026-11-12: done. Draft in BLOG.md, figure results/recodification.svg, table results/per_title.tsv.

## Pipeline (run from this directory)
1. `cache/`: govinfo US Code HTML (fetched ~1/1.5 s): first edition after each restatement (holds the disposition
   table: 1998 t36, 2002 t40, 2006 t46, 2011 t51, 2011 t41, 2014 t54), 2024 editions of the six titles (drift notes),
   PLAW-113publ287.htm. govinfo has no 46 App. package.
2. `python tools/parse_tables.py` -> data/dispo_rows.tsv (5,136 table rows).
   `python tools/parse_transfers.py` -> data/transfers.tsv (28 49->51 renumberings from title 51 credits).
3. `python tools/analyze.py` -> data/old_provisions.tsv, pairs.tsv, app_rows.tsv, vanished_unrelated.tsv,
   summary.json, data/lean/<T>.tsv (restatement day), <T>.ed.tsv (first edition after), 40A/46A.tsv.
4. Lean: model `LegalProofs/USCaseLaw/Recodification.lean`, runner `RunRecodification.lean` (global-law-lean repo,
   not committed). The model olean is compiled into `lean-build/` (no lake build):
   `lake env lean LegalProofs/USCaseLaw/Recodification.lean -o <here>/lean-build/LegalProofs/USCaseLaw/Recodification.olean`
   then run with LEAN_PATH=<here>/lean-build;<lake LEAN_PATH>:
   `lean --run LegalProofs/USCaseLaw/RunRecodification.lean data/lean/36.tsv results/lean_36.tsv [explained]`.
   Output: results/lean_run.txt, results/lean_*.tsv (U = unaccounted, I = image not in force).
5. `tools/crosscheck_notes.py` (title 54/51 repeal placeholders vs table), `tools/drift_notes.py` (2024 notes),
   `tools/drift.py` (record law commits on emptied paths: only number reuse, filter for collisions is rough),
   `tools/cites_old.py` (bonus), `tools/results.py`, `tools/figure.py`, `tools/make_audit.py`,
   `tools/trace_unaccounted.py` (git grep of an unaccounted section's phrases at the next edition).

## Results
- Old provisions (record, in force day before, placeholders excluded): 36: 1370, 40: 586, 51: 273, 41: 198,
  54: 294; title 46's own 404 (396 kept at number, 8 explained only by Code notes); 46 App. 867 named in table.
- Unaccounted by tables: 1 (40 U.S.C. 207b-2 -> found at 2 U.S.C. 1927).
- Images not in force on the day: 36: 47, 40: 145, 41: 9, 54: 1; at first edition: 40: 3, 54: 1 (16 U.S.C. 458a ->
  104908, should be 104905 per the Code's repeal note). 46 App.: 83 (cumulative table rows from 1983/1988).
- 54 placeholders: 224 of 236 agree exactly with the table.
- Content: 2,478 pairs, 197 lose amount/percent/date; audit 24: 19 intended, 4 false flags, 1 silent loss
  (16 U.S.C. 1a-2(g) Glacier Bay fee rules, repealed by 113-287 §7, not restated).
- Drift: 52 notes / 51 sections in 2024 editions (46: 38 "directed the amendment of former ..." repealed by 110-181).
- Cites: 847 later citations of old numbers (618 decisions) translatable; 46 App. cites not extracted.

## Audit
audit/totality_sample.tsv (36 rows, checked by hand against raw rows: 36/36 right),
audit/content_packet.txt + audit/content_verdicts.tsv (agent-read, 24 cases).
