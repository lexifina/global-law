# Round 12 progress

Lead: one agent; started 14 Nov 2026 07:00. Contract: `DESIGN12.md`. Log: `LOG.md`.
Base: `round11/stage/v11d` + `round11/out/v11d` (binary s51 a1cc4296). Backups of anything changed outside `round12/`: `round12/pre/`.

## How to resume
1. Read `DESIGN12.md`, this file, `LOG.md`.
2. Keep `wsl.exe -d Ubuntu -- sleep N` attached. `df -h /c` before every stage / Lean run (stop under 8 GB).
3. Each agent has `round12/agents/<name>/BRIEF.md` + `NOTES.md`. A dead agent is resumed by a new agent with the same
   brief + "resume from NOTES.md" (own folder `<name>b`).
4. Variant: certify12 -> stage12 -> `wsl/r12_run.sh` (NOBUILD) -> score12 -> make_overturned -> clean12 <old>.

## Agents (state)
| agent | track | started | state |
|---|---|---|---|
| infra12 | tools on v11d, audit exclusion, node plumbing, freeze/sealed/live | 07:04 | done 07:29 (INFRA 07:23, NODES 07:27, Part C) |
| orders12 | Journal terms OT2010-13/15/17-18, ligature, 2005 long lists | 07:04 | done 07:20 (1,871 nodes: 57 repaired, 826 longlist) |
| shadow12 | Shadow: 87 unlinked nodes, several-candidate pick, 2005, new nodes | 07:04 | done 07:38: C8 67 + newnodes 321 + recert 14 installed |
| enbanc12 | en banc vacatur of own panel | 07:04 | done 07:36: none installed (v5 0.812; v6 fresh 26/27 -> user; OP12 5/6) |
| fedcir12 | Fed Cir district targets + other-target opinions | 07:04 | done 07:38: none installed (M+L 0.510; L split 9/10 post hoc) |
| stlink12 | Brace & Hall third tie | 07:04 | done 07:32: u2t 402 rows installed (0.950 / 0.938) |
| bench12 | NEW fresh key (isolated) | 07:04 | done 07:17 (READY) |

## Variants
| name | contents | notes |
|---|---|---|
| v12a | v11d + u2t3 + c8 + newnodes + recert (--drop 14), 1,871 nodes (lead/v12a.args) | scored 07:42; FROZEN 07:43; sealed once 07:43; reference 0 disagreements |

## State
DONE 07:46: frozen v12a (FREEZE.md), sealed once (SEALED_LOG.md), report ROUND12.md, live page Done.
