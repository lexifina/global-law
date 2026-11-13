# caselaw-lean-2: the 13 numbered limits of the first pass, and where each is recorded

The first pass listed 13 quick limits. Limits 1-4 and the commission opinions are in `LEAN.md` "Five limits" (that
table numbers the commission opinions 5; in the original list they are limit 12, and limit 5 is the glue fuzzing).
Limits 8, 9, 10, 11 and 13 are in `data/courts_validation.md` §5. This file records the rest, so that every number
has an entry. `report/make_report.py` reads the table below; a row here replaces a row with the same number from
the other two files.

| # | Limit | Where | Now | What was done | Recorded |
|---|---|---|---|---|---|
| 5 | The file-reading glue was tested only on fixtures | Lean glue | Fixed | The TSV parser, text normalisation and offsets were fuzzed against a SCHEMA oracle and the reference (300 cases with Lean, 5,000 against the reference). Nine bugs were found and fixed. | FUZZ.md, FUZZ_BUGS.md |
| 6 | The Horty consistency check had never run: there was no `factors.tsv` | Data and Lean | Fixed | Factors were produced for the Supreme Court holdings (`data/factors.tsv`, `factor_cases.tsv`, `factor_vocab.tsv`), a fixture was added, and the runner's check ran on the real factors: 44 binding bases, 43 consistent, 1 inconsistent (express pre-emption). `horty_py.py` recomputes it independently and agrees on all 51 sub-family bases. | data/FACTORS.md, FACTORS_NEEDS.md, DIFFTEST.md §8.4 |
| 7 | Windows Application Control blocks the Windows Lean toolchain and the compiled runner | Machine policy | The user's to set | Not a defect of the model. It needs a standing allow rule on this machine, which only the user can set. Until then the build, the audit and every run are made under Linux Lean 4.35.0 in WSL Ubuntu (`run_lean_wsl.sh`), from the unchanged Windows sources. | TRUST.md headline, LEAN.md "Running under WSL" |
| 12 | Commission opinions (Texas, Missouri) were not distinguished, though `commission.tsv` existed | Lean | Fixed | The notation is wired into force: `Notation`, the adoption filters `opinionAdopted`, `holdingApproved`, `judgmentAdopted` and `noNotation`, and `Decision.commission`; `Run.lean` loads `commission.tsv`. The reference does the same. | LEAN.md "Five limits" (row 5), DEVIATIONS 63 |
