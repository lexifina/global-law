# Round 10 progress

Lead: one agent; started 14 Nov 2026 03:42. Contract: `DESIGN10.md`. Log: `LOG.md`.
Base: `round9/stage/v9c` + `round9/out/v9c` (binary 22bab5cd). Backups of anything changed outside `round10/`: `round10/pre/`.

## How to resume
1. Read `DESIGN10.md`, this file, `LOG.md`.
2. Keep `wsl.exe -d Ubuntu -- sleep N` attached. `df -h /c` before every stage / Lean run (stop under 8 GB).
3. Each agent has a folder with `BRIEF.md` + `NOTES.md`: `round10/agents/<name>/`. A dead agent is resumed by a new
   agent with the same brief + "resume from NOTES.md".
4. Build a variant (after INFRA_READY): certify (`round10/certify10.py`) → `python -X utf8 round10/stage10.py <name> --delta …` →
   `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r10_run.sh <name> [ref]'`
   → `bash round10/score10.sh <name>` → `python -X utf8 round5/report/make_overturned.py` → `bash round10/clean10.sh <old>`.
5. Lean builds only when `round10/LEAN_READY` exists (agent `lean10`). Requests to lean10/ref10 go through
   `round10/agents/{lean10,ref10}/INBOX.md` + a DESIGN10 section.

## Agents (state)
| agent | track | started | state |
|---|---|---|---|
| infra10 | stage10 / certify10 / r10_run / score10 / clean10 / audit / freeze10 / sealed10 / live page | 03:48 | done 04:09 (INFRA_READY); 7-8 done |
| syl10 | move 1: syllabus / head-matter quotes re-cut | 03:48 | done 04:18: RO treat 3 installed; history RO not |
| stlink10 | move 2: state-court review linker (FJC analogue) | 03:48 | done 04:55: s1, g2, D installed; T4, U not |
| fjc10 | move 3: FJC named-other-case, one-side captions, ruling under review | 03:48 | silent 03:54, stopped 04:44 (coordinator) |
| scdb10 | move 4: SCDB cited without accepted anchor | 03:48 | done 04:50: a10, s10 installed; a10t, a10n not |
| shadow10 | move 5: remand-bridge table (§4) + post-2013 orders without remand decision | 03:48 | done 04:58: C6 + remand table installed; C2, C9 not |
| lean10 | Lean: DESIGN10 §4 (+ later sections) | 03:48 | done 04:54 LEAN_READY (e7e32592, 292 theorems, 83 mutants) |
| ref10 | Python reference + differential | 03:48 | done: 0 disagreements real data (v10b/c/d) |
| fjc10b | move 3 resume (from fjc10 files) | 04:42 | done 04:57: N/h+P installed; h w/o P, x+s not |
| bench10 | NEW fresh key (isolated) | 03:48 | done 03:57: benchmarks/fedcir_dataset READY |

## Variants
| name | contents | notes |
|---|---|---|
| v10d | v10c + fjc10b n2h (args round10/lead/v10d.args); binary e7e32592 + reference 0 disagreements | FROZEN 05:02; sealed once 05:02 |
| v10c | v10b + scdb10 s10 replace + stlink10 d2 | built binary + reference 0 disagreements; deleted |
| v10b | v10a + shadow10 cert_remand (§4 table, 316 lines); args round10/lead/v10b.args | §4 binary 43efb994 + reference: 0 disagreements; status = v10a; deleted |
| v10a | v9c + syl10 RO treat + scdb10 a10 + shadow10 C6 + stlink10 s1 + g2 (frozen binary) | scored; superseded by v10b, deleted |

## State (05:05): DONE
Frozen v10d (FREEZE.md); sealed run once (SEALED_LOG.md); report ROUND10.md; live page section 98 + Round 10 row Done.
