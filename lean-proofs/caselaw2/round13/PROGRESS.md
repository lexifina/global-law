# Round 13 progress

Lead: one agent; started 14 Nov 2026 11:30. Contract: `DESIGN13.md`. Log: `LOG.md`.
Base: `round12/stage/v12a` + `round12/out/v12a` (binary s51 a1cc4296, NOBUILD). Rule work: `agents/shadow13/`.

## How to resume
1. Read `DESIGN13.md`, this file, `LOG.md`, `agents/shadow13/NOTES.md`.
2. `df -h /c` before every stage / Lean run (stop under 8 GB). One staged variant at a time; `bash round13/clean13.sh <name>` after scoring.
3. Variant: certify13 -> stage13 -> `wsl/r13_run.sh` (NOBUILD) -> score13 -> clean13.

## State
| item | state |
|---|---|
| tools (mk_round13) | done 11:35; v12a_check reproduces round12/out/v12a byte for byte (11:56) |
| rule D (second docket) | 16 rows; r13k01 14/15 = 0.933 -> installed |
| rule S (officer successor) | 11 rows; r13k02 9/9 (+2 read right in r11k01) -> installed |
| rule A (agency acronym) | 8 rows; r13k03 8/8 -> installed |
| rule N (2005 / name form) | dev 9/13 = 0.69 -> not built |
| held classes (user decision) | T4 245, R2 v3 76 (12 overlap rows dropped), EB12 v6 101 -> installed (below bar) |
| Lean build check | OK 11:45 (305 theorems, audit check clean) |
| v13h | scored 11:59 (held classes alone), cleaned |
| v13a | staged 12:03, NOBUILD + reference 0 disagreements, scored, FROZEN 12:04, sealed once 12:04 |
| fold + graph | done 12:06 (run_existing, views, fold_round, make_graph) |

DONE 12:10: ROUND13.md written.
