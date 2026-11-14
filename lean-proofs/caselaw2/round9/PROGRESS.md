# Round 9 progress

Lead: one agent; started 14 Nov 2026 02:04. Contract: `DESIGN9.md`. Log: `LOG.md`.
Base: `round8/stage/v8e` + `round8/out/v8e`. Backups of anything changed outside `round9/`: `round9/pre/`.

## How to resume
1. Read `DESIGN9.md`, this file, `LOG.md`.
2. Keep `wsl.exe -d Ubuntu -- sleep N` attached.
3. Each agent has a folder with `BRIEF.md` + `NOTES.md`: `round9/agents/<name>/`. A dead agent is resumed by a new
   agent with the same brief + "resume from NOTES.md".
4. Build a variant: certify (`round9/certify9.py`) → `python -X utf8 round9/stage9.py <name> --delta …` →
   `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r9_run.sh <name> [ref]'`
   → `bash round9/score9.sh <name>` → `python -X utf8 round5/report/make_overturned.py`.
5. Lean builds only when `round9/LEAN_READY` exists (agent `lean9`). Lean requests to lean9/ref9 go through
   `round9/agents/{lean9,ref9}/INBOX.md` + a DESIGN9 section.

## Agents (state)
| agent | track | started | state |
|---|---|---|---|
| infra9 | stage9 / r9_run / score9 / freeze9 / sealed9 / audit / live page | 02:10 | done 02:32 (INFRA_READY); --table option requested |
| fjc9 | move 1: FJC no-court-phrase + guard exception | 02:10 | done 02:52: W install, J install with §8, G/G2 not |
| scdb9 | move 2: SCDB judgment lines, D1/D3/D5, anchors | 02:10 | done 02:52: 4 rows install; readings 0.867 not (D9-11) |
| calpart9 | move 3: part map fix + part_zone table | 02:10 | done 02:57: zones + PJT/PJR/recut install; PJH not |
| shadow9 | move 4: post-2013 GVRs, data gap | 02:10 | done 02:44: cert_remandtext_v2 335 rows, r9k01 79/80, INSTALL |
| state9 | move 5: at-risk implicit class, far joins, doctrine own-tie | 02:10 | done 03:02: A (72, at-risk) + B (52, §5) install; C withdrawn |
| nj9 | move 6: NJ successor-court rule (research) | 02:10 | done 02:32: option A data rows (D9-6) |
| lean9 | Lean: DESIGN9 §4 part zones (+ later sections) | 02:10 | done 03:32: LEAN_READY §4-§8, 272 theorems, 74 mutants |
| ref9 | Python reference + differential | 02:10 | done 03:45: real data 0 (v9a/b/c); synthetic only known W rows |
| bench_bh | NEW fresh key: Brace & Hall (benchmarks/brace_hall_state) | 02:10 | done 02:28 READY |
| bench_songer | NEW fresh key: Songer TREAT (benchmarks/songer_treat) | 02:10 | done 02:27 READY |

## Variants
| name | contents | notes |
|---|---|---|
| v9c | v9b with state9 B/cert_far2 (gap windows) (args round9/lead/v9c.args) | FROZEN 03:36 (FREEZE.md re-written 03:37); sealed once 03:37 |
| v9b | v9a + fjc9 delta_J + state9 B/cert_far + A/cert2_claim | 48 B rows joinedFarWindow (no gap window); superseded, deleted |
| v9a_s4 | v9a with the §4 binary + reference | 0 disagreements; zone check 72; superseded, deleted |
| v9a | v8e + shadow9 v2 + fjc9 W + scdb9 a9/r4w/wfix (+remove) + calpart9 PJT/PJR/recut (+remove, relabels) + state9 A plain + zones (all rows, round9/lead/zone_delta_all) + NJ tables (args: round9/lead/v9a.args) | frozen-binary run 03:03 (zones ignored); round-9 binary run after LEAN_READY |

## State (03:40): DONE
Frozen v9c (FREEZE.md); sealed run once (SEALED_LOG.md); report ROUND9.md; live page section 97 + Round 9 row Done.
