# Round 11 progress

Lead: one agent; started 14 Nov 2026 05:06. Contract: `DESIGN11.md`. Log: `LOG.md`.
Base: `round10/stage/v10d` + `round10/out/v10d` (binary e7e32592). Backups of anything changed outside `round11/`: `round11/pre/`.

## How to resume
1. Read `DESIGN11.md`, this file, `LOG.md`.
2. Keep `wsl.exe -d Ubuntu -- sleep N` attached. `df -h /c` before every stage / Lean run (stop under 8 GB).
3. Each agent has `round11/agents/<name>/BRIEF.md` + `NOTES.md`. A dead agent is resumed by a new agent with the same
   brief + "resume from NOTES.md" (own folder `<name>b`).
4. Variant: certify11 -> stage11 -> `wsl/r11_run.sh` (NOBUILD) -> score11 -> make_overturned -> clean11 <old>.

## Agents (state)
| agent | track | started | state |
|---|---|---|---|
| infra11 | stage11 / certify11 / r11_run / score11 / clean11 / audit / §4 node overlay / freeze11 / sealed11 / live page | 05:14 | done ~05:50 (INFRA_READY 05:29, NODES_READY ~05:46, Part C) |
| stlink11 | move 1: state review of uncited decisions below (U2) | 05:14 | done 06:07: U2 + u2w installed (0.963 each); u2n, u2e, u2q not; §5.2 lines 139 |
| fedcir11 | move 2: Federal Circuit linker | 05:14 | done 06:16: tribunal class installed (0.912); lean-cue 0.841, rule R 0.883 not |
| orders11 | move 3: order lists 2006-09, 2020-25 as staged data | 05:14 | silent 05:16; replaced by orders11b; ended |
| orders11b | move 3 resume: parse Journal texts into order nodes | 05:38 | done 05:55: 980 nodes (DATA_READY) |
| shadow11 | move 3 rows on order nodes + move 6 narrower C2/C9 | 05:14 | done 06:28: olist 431 + olist2 28 installed; C11 0.850 not |
| fjc11 | move 4: FJC caption + docket/judge/date ties | 05:14 | done 05:55: X2b 0.850, FU2 0.673 — nothing installed |
| scdb11 | move 5: SCDB rehearing / en banc targets | 05:14 | done 05:50: R1 installed; R2v3 0.898, R3 0.500 not |
| bench11 | NEW fresh key (isolated) | 05:14 | done 05:22 (READY; scored only after FREEZE) |
| lean11 | Lean §5.1 anchorTribunal + §5.2 identity | 05:23 | done 06:55: s51 a1cc4296 (frozen), s52 ea2e1d7e; 305 theorems, 89 mutants |
| ref11 | Python reference §5.1 + differential | 05:23 | done 06:56: 0 disagreements on v11d |

## Variants
| name | contents | notes |
|---|---|---|
| v11a | v10d + stlink11 delta_u2c + scdb11 cert_r1 (--remove remove_r1) (args lead\/v11a.args) | scored 05:56 (SCDB 1,837); superseded |
| v11b | v11a + u2w + R4 + shadow11 cert_olist with --nodes (args lead/v11b.args) | scored 06:09: Shadow 684, SCDB 1,838; cleaned |
| v11c | v11b + cert_olist2 + delta_b_trib + delta_u2c_ident, 1,045 order nodes (args lead/v11c.args) | interim s51 06:31 (Shadow 688, SCDB 1,838); cleaned |
| v11d | v11c minus delta_u2c_ident (args lead/v11d.args); binary s51 a1cc4296 | FROZEN 06:53; sealed once 06:53; reference 0 disagreements |

## State (06:56): DONE
Frozen v11d (FREEZE.md); sealed run once (SEALED_LOG.md); report ROUND11.md; live page section 99 + Round 11 row Done.
