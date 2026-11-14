# Round 8 progress

Lead: one agent; started 14 Nov 2026 00:11. Contract: `DESIGN8.md`. Log: `LOG.md`.
Base: `round7/stage/v3` + `round7/out/v3`. Backups of anything changed outside `round8/`: `round8/pre/`.

## How to resume
1. Read `DESIGN8.md`, this file, `LOG.md`.
2. Keep `wsl.exe -d Ubuntu -- sleep N` attached.
3. Each agent has a folder with `NOTES.md`: `round8/agents/<name>/`. A dead agent is resumed from its NOTES.md (a new
   agent with the same brief, `round8/agents/<name>/BRIEF.md`, + "resume from NOTES.md").
4. Build a variant: certify → `python -X utf8 round8/stage8.py <name> --delta …` →
   `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r8_run.sh <name> [ref]'`
   → `bash round8/score8.sh <name>` → `python round5/report/make_overturned.py`.
5. Lean builds only when `round8/LEAN_READY` exists (written by agent `lean8`).

## Agents (state)
| agent | track | started | state |
|---|---|---|---|
| base | v3, no delta | 00:37 | byte-identical to round7/out/v3 |
| v8b | v8a + state8 + orderdock_d | 01:23 | Shadow h0 403/1,059 (Booker reinstatements, D8-6) |
| v8c | v8b + multicase + fjc8 F1 (no claims) | 01:30 | FJC h0 54.2%; fresh dev 52/112 |
| v8d | v8c + scdb8 delta_ins (remove 12) | 01:34 | SCDB h0 74.0%; Shadow 38.2%; state 17/132; Shep dev 143/254 |
| v8e | v8d + fjc8 oldCircuit claims + scdb8 W (anchorWide) + notarget; round-8 Lean + ref | 01:42 | FROZEN 01:59; sealed once (SEALED_LOG.md) |
| v8a | rehear8 G+N, ownact | 01:04 | Shep dev 141/254; holdout Y-named strict 775; h0 see results/v8a/bench_h0.txt |
| infra | stage8 / r8_run / score8, h0 benchmark shadow, base reproduction, v3 h0 baseline | 00:15 | done 00:37 |
| ownact | move 1: port + read the round-3 own-act queue | 00:15 | done: 591 rows, r8o02 77/80, installed |
| orderdock | move 2: head-matter SC orders by docket; Shadow Docket h0 diagnosis | 00:15 | done: orderdock_d installed; Shadow h0 156 → 426 |
| rehear8 | move 3: rehearing grant orders → panel; 589 no-date docket rows | 00:15 | done 00:50: G 76/80, N 72/80, installed |
| multicase | move 4: multi-case overruling sentences | 00:15 | done: 706 rows, r8m01 76/80, installed |
| state8 | move 5: state-court gaps (state tables h0) | 00:15 | done: R8S 151 rows, r8s01 77/80, installed |
| contradict | move 6: base rows contradicted by newer two-quote rows | 00:15 | done 00:31: audit 27/40, not installed |
| fjc8 | FJC appeals h0 diagnosis: courts of appeals reversing district decisions | 00:15 | done: F1 2,081 rows, r8f05 73/80, installed |
| scdb8 | SCDB disposition h0 diagnosis: Supreme Court merits dispositions | 00:15 | done: delta_ins 512 + W 110 (after Lean), installed |
| audit8 | blind-audit tooling (port of round7/audit) | 00:15 | done 00:27 (READY) |
| doctrine8 | move 7: doctrine dominance (analysis first) | 00:15 | done 00:22: ≤15 rows, not built |
| lean8 | Lean: DESIGN8 §4 bridge evidence (+ later requests) | 00:52 | done 01:38 LEAN_READY |
| ref8 | Python reference for DESIGN8 §4, differential | 00:52 | done 01:45 |
| calpart | old-California header part map (state8 finding) | 01:06 | stopped; no output after 01:11; not staged |
| notarget | own-act sentences with unresolved targets (state8's 41,889) | 01:24 | done: 51 rows, r8n01 38/39, installed |

## Variants
| name | contents | dev scored | notes |
|---|---|---|---|

## State (02:01): DONE
Frozen v8e (FREEZE.md 01:59); sealed run once (SEALED_LOG.md); report ROUND8.md. calpart produced nothing staged.
