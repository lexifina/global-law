# Round 5 progress (lead: one agent; started 13 Nov 2026 11:35)

Contract: `DESIGN5.md`. Iteration log: `LOG.md`. Backups of everything edited: `pre/` (Lean tree `pre/lean`, tools
`pre/tools`, cue table, lock, run_lean.sh); data tables get `data/*.pre_round5.tsv` before any install.

## How to resume
1. Read `DESIGN5.md`, this file, `LOG.md`.
2. WSL: keep `wsl.exe -d Ubuntu -- sleep N` attached; build with `./run_lean_wsl.sh build`; audit with
   `./run_lean_wsl.sh audit check`.
3. Sub-agent outputs are under `round5/<name>/` (each has its own NOTES.md): `diag/`, `recog/`, `opwords/`, `ref/`.

**12:40 the session crashed; every sub-agent and the WSL keep-alive stopped. 13:42 resumed from the files on disk; unfinished reading, the reference rulings and the audits were restarted.**

## State (final, 14:20)
| item | state |
|---|---|
| Design (`DESIGN5.md`) | final; rulings in section 9 |
| Lean | 175 theorems locked and checked (0 problems), 34 mutants killed, no sorry / new axiom / native_decide; round-4 output reproduced byte for byte |
| Python reference | round-5 rules implemented from the design alone; regression set 0 disagreements; new universes: status 0 of 55,055 keys |
| Recognised class | read (2,902 passages by the main model, 2,347 pre-screened), certified, blind-audited (94-97% right), **installed in the frozen build** |
| Operative-words class | read (2,179 passages), certified (665 rows), blind-audited at 79% (part) and 27% (whole): **not installed** |
| Frozen build | `round5/stage/final` + `round5/out/final`; `FREEZE.md` written 14:05 |
| Sealed test | run once, 14:06: lenient 46.5% -> 60.6%; strict 25.2% unchanged |
| Round report | `ROUND5.md`; page `~/Documents/html-reports/overturned.html` |
| Not done | fuzzer extension; scope and reader-recall fixes from the dev diagnosis; decoys in the audits; install over `data/`; fix of the date-0 power lookup |

## How to rebuild a variant
`python round5/stage.py <name> --delta ... ` -> `wsl/r5_run.sh <name> [ref]` (inside WSL) -> `bash round5/score_all.sh <name>`
-> `python round5/report/make_overturned.py`. The frozen build's command line is in `round5/stage/final/MANIFEST.txt`.
