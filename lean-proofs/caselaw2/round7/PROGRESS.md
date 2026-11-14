# Round 7 progress

Lead: one agent; started 13 Nov 2026 22:37. Contract: `DESIGN7.md`. Log: `LOG.md`.
Base: `round6/history/stage/final2` + `round6/history/out/final2`. Backups of anything changed outside `round7/`:
`round7/pre/`.

## How to resume
1. Read `DESIGN7.md`, this file, `LOG.md`.
2. Keep `wsl.exe -d Ubuntu -- sleep N` attached.
3. Each agent has a folder with `NOTES.md`: `round7/agents/<name>/` (lean, ref, infra, orderhead, antecedent,
   doctrine, opwords, queue, b3), `round7/audit/`, `round7/heldout/`. A dead agent is resumed from its NOTES.md
   (a new agent with the same brief + "resume from NOTES.md").
4. Build a variant: certify (certify7 / certify_recog / certify_opwords) → `python -X utf8 round7/stage7.py <name>
   --delta …` → `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r7_run.sh <name> [ref]'`
   → `bash round7/score7.sh <name>` → `python round5/report/make_overturned.py`.
5. Lean builds only when `round7/LEAN_READY` exists (written by agent `lean`).

## Agents (state)
| agent | track | started | state |
|---|---|---|---|
| lean | A1 Lean: joined certificate, doctrine, orderHead, setAside | 22:42 | done |
| ref | A1 Python reference + differential + fuzzer | 22:42 | done 23:18 (Lean differential pending LEAN_READY) |
| infra | certify7, stage7, r7_run, score7; A1(iii) orderHead rows; B4(f) count | 22:43 | done 23:18 |
| antecedent | A1(i) two-sentence overrulings (+ B2 anaphora recall) | 22:43 | done |
| doctrine | A1(ii) doctrine targets | 22:43 | done |
| opwords | A2 failure analysis, sharper brief, packs (readers: lead, opus) | 22:44 | done; 103 packs read; 936 rows; part installed |
| audit | blind-audit tooling with decoys | 22:44 | done 23:10 |
| queue | B1 prep: inventory of unread packs, new packs, shards | 22:44 | done 23:02; P1 read; 317 rows |
| b3 | B3 scorer, two date views | 22:44 | done 23:00 |
| heldout | new clean held-out key (time split 2021+, 256 pairs) | 22:45 | done 23:16 |

## Variants
| name | contents | dev scored | notes |
|---|---|---|---|
| base | final2, no delta | yes | reproduces round-6 output byte for byte |
| v1 | + operative words part (906, audit 79/80) + B1 recognised (317, audit 80/80) | 23:27 | fresh lenient 109/165; holdout alsoInFeed 1,027/2,640, holdoutOnly 499/6,734 |
| v1rcg | ablation: + B1 recognised only | holdout only | 1,019 / 431 |

| b4sc | B4 (a) SC opinions not linked, (e) re-pointing | 23:08 | done |
| b4rehear | B4 (b) en banc / docket rehearing, (d) set aside | 23:19 | done |
| scope | B2 scope rule | 23:19 | done |

Readers: see READING_QUEUE.md. Audits: round7/audit/r7a01 (opw part 79/80), r7a02 (opw whole 10/30, not installed), r7a03 (recognised 80/80).

## State (00:11): DONE
All agents finished. Frozen variant `v3` (FREEZE.md 00:08); sealed runs once each (SEALED_LOG.md); report ROUND7.md.
Audits r7a01-r7a21 in round7/audit/. Variants: base, v1, v1rcg, v2 (staged, not run), v3 (frozen).
