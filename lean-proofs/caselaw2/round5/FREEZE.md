# Round 5 freeze record

Written 13 November 2026, 14:05, before the single run of the sealed half. Nothing listed here was changed afterwards.

Frozen build: variant `final` (`round5/stage/final`, output `round5/out/final`). The frozen build: round-4 data plus the recognised class only (1,459 rows read by Claude readers, 4,685 pattern rows that can only make a case partly negative, and the round-4 witness rows that pass the new check), minus 15 rows the blind audit or the dev diagnosis showed wrong. The operative-words rows are left out: they failed the precision bar in the blind audit.

## Rules and code

| What | Files | SHA-1 |
|---|---|---|
| Lean sources (`LegalProofs/CaseLaw2`) | 28 | `ff7d9de669d829547fa87bfba61f9ef5ad7e2ffe` |
| Cue table and generator (`tools/caselaw2/cues`) | 2 | `60b090f5b303a2303fc4f9fdbfc63e74c94c4706` |
| Python reference (`tools/caselaw2/ref`) | 9 | `25f3f979b2f85b1dc0b45791faf0b370bf96ceff` |
| Recognised reader: brief, certifier, verifier (`round5/recog`) | 379 | `b9432bd7f4238f5905f471a8fbca8c9410dcf111` |
| Operative-words reader (`round5/opwords`; not installed) | 94 | `ed3492586e553e4a9048f7cef50512928766b071` |
| Audit tools (`round5/audit`) | 15 | `1fab4508ce431f4de0f19e869e6a96dc728248e5` |
| Design (`round5/DESIGN5.md`) | 1 | `843cfb48c837a9aba847af0f46c14313c12f37e2` |
| Staging script (`round5/stage.py`) | 1 | `5d00a7e6eb774156b44a37042e4b74bd5780d6a3` |
| Runner script (`run_lean.sh`) | 1 | `613269f9a48081eabd26f1cd8faaffcdb713dfdd` |
| Theorem lock (`audit/statements.lock`) | 1 | `27d61dad067e26becf674df0376de8eae1674acc` |
| Fresh-list scorer (`gold_fresh/score_fresh.py`, not ours) | 1 | `c16db05b9a7cee5d139a531d9439ee316bab3b27` |

## Data of the frozen build (`round5/stage/final`)

| Table | Rows | SHA-1 |
|---|---|---|
| `treatments.tsv` | 41476 | `0cec8e582669ea4cfe11d177cc3f4063e62edb88` |
| `treatment_witness.tsv` | 6290 | `9a796b26e753d361ccc44ef4afb8b2a31ac74145` |
| `treatment_class.tsv` | 6290 | `c457bd020853c5b0db3a58a640d514e35a2c79d7` |
| `cert_text.tsv` | 88916 | `776bb22b203296a816639a4cd6962e70f2893741` |
| `window_sha.tsv` | 345521 | `953dc772f8247befb19c4d73187c4c9701dbbdd1` |
| `cite_index.tsv` | 54562 | `3f439570630f18d829fc602c3c36b4c01dee4f26` |

Every other table is the round-4 table, unchanged (hard links to `data/`).

## Output of the frozen build (`round5/out/final`)

| File | Lines | SHA-1 |
|---|---|---|
| `certs.tsv` | 356766 | `d77a21b9288ddec4fa01cd1ef242d91ce701e088` |
| `classes.tsv` | 33599 | `5e593475cd1856ae28f014104111df694c3d9eb6` |
| `findings.tsv` | 237805 | `98786cb3e4d8a6bc8f101752073697ea7efaa3a8` |
| `horty.tsv` | 44 | `f5ebef436b5a260efcc4e2f1261ec5800ccb56a7` |
| `splits.tsv` | 456 | `91f6da6ab31bad2f6e132d4a6d577e6425eb2c5b` |
| `status.tsv` | 519503 | `58f9bb577e955e97249da63df61445ebb4c40a61` |
| `status_lines.tsv` | 643 | `b4b08b82d4af50868cc782f067a769d2e992865a` |

## What was used to get here

- The open (dev) half of the fresh lists: scored for `it0_claims`, `it1`, `it2` and `final`; its misses were read (`diag2/`). One row was removed and the operative cue lists were extended because of that reading.
- The sealed half: never opened, never scored by this agent before this record.
- The burned lists (SCDB, CRS, Christiansen-Eskridge, Hasen): not used to choose any candidate; the 66 SCDB misses were read for diagnosis only (`diag/`).
- Later-court statements: only speakers with power over the target (the `feed` side of `tests/split`); `check_no_leak.py` exits 0 on this build.
