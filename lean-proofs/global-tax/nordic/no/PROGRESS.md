# Norway (Oslo), income year 2025: PROGRESS

Owner: NORWAY agent (delegated by the Nordic lead). Contract: ~/cmp20/CONTRACT20.md. Kernel: ~/cmp20/kernel (API v1.0).

## Status (2026-11-19, milestone 8: done)
| # | Step | Status |
|---|---|---|
| 0 | read contracts, kernel API, DE style | done |
| 1a | parameters 2025 with citations (refs/PARAMS.md, P1-P26) | done |
| 1b | Lean model lean/NOTax on TaxKernel (by path), exe `notax` | done: 637 lines, 88 definitions, 39 theorems, 0 sorry |
| 2 | validation | done: OECD TW 2025 48/48 lines within 1 % (max 6.3 NOK, rounding); kernel oecd_check20.py 40/40; worked examples 11/11; trekkrutine port 909 996/909 996 published rows; tables vs statute 2 001 bases (F1) |
| 3 | proofs | done (lean/NOTax/Theorems.lean) |
| 4 | known loopholes | done: CATALOGUE.md, 18 catalogued, 10 recreated, 8 not modelled |
| 5 | new loopholes | done: F10 (sole-trader 47 % band, Lean `soleTrader_band`), F18 (gift minimum, minor) |
| 6 | gov errors / statute faults | done: gov-error F1-F4, F8; statute-fault F5-F7, F9; draft issue drafts/ISSUE_trekktabell_2025.md (not filed) |
| 7 | USEFUL.md, FAMILY_NOTES.md, results/summary.json | done |

Done 8/8.

## Open issues / possible next steps
- Prop. 1 LS (2025–2026) point 3.2.6 (why the 2025 § 17-1 limits were raised in Dec 2025, F9) not read:
  regjeringen.no is behind bot protection.
- Tables 6300/6350/7300/7350/7500/7550/7700 in the published 2025 file are not in the open code; not checked (F2).
- Not modelled: wealth tax, housing, IPS payouts, aksjesparekonto, holding companies (rate theorem only), § 17-2
  joint skattebegrensning, fagforening/reise deductions, kontantstøtte.
- Rounding: each tax rounded down separately (reading of skattebetalingsforskriften § 10-4-4, F19).

## How to rerun
- Build: `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build` (exe .lake/build/bin/notax).
- `cd harness && python3 oecd_check.py --json ../runs/oecd_check.json; python3 worked_examples.py;
  python3 table_vs_statute.py; python3 scan_metr.py; python3 scan_owner.py; python3 scan_couples.py;
  python3 xref_check.py`.
- Sources: refs/web (Lovdata STV/LTI, Innst. 3 S, Skatteetaten satser, NAV), refs/lovdata (Lovdata public data
  skatteloven/folketrygdloven XML), refs/src/trekktabell2025 (worktree at commit aeaaf08),
  refs/web/tabeller2025 (published 2025 tables).
Web searches used: 5 / 10.
