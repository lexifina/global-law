# IT: progress (Italy, periodo d'imposta 2025, Roma Capitale / Lazio)

Updated: 2026-11-19. Status: DONE (all 7 steps; open items below).

| Step | Status |
|---|---|
| 1 Model (`lean/`, exe `ittax`, TaxKernel by path) | DONE: IRPEF artt. 10-13, 16-ter; L. 207/2024 cc. 2-6; trattamento integrativo; addizionali Lazio + Roma; INPS; assegno unico + ISEE; cedolare / sostitutiva |
| 2 Referees | OECD TW 2025: 56 lines, 42 within 1 EUR, 49 within 1 % (all misses = Lazio reliefs the OECD omits, F1); circ. AdE 4/E 2025 examples 3/3; OECD component lines 5/5 |
| 3 Proofs | DONE: 37 theorems, 0 sorry (Theorems.lean, Tests.lean, Loopholes.lean) |
| 4 Known loopholes | DONE: CATALOGUE.md, 18 catalogued, 10 recreated, 8 not modelled |
| 5 New loopholes | DONE: NOVEL.md, 4 new (F4-F7), scanner harness/metr_scan.py |
| 6 Government / statute errors | DONE: 4 gov (F1, F2, F3, F13), 3 statute (F9, F10, F11), 1 reading (F12) |
| 7 USEFUL.md | DONE |

## Files
FINDINGS.md, CATALOGUE.md, NOVEL.md, USEFUL.md, results/summary.json, results/oecd_check.{json,md},
results/search/METR.md (+ metr_*.json), oecd_map.py, harness/{fetch_law.py, metr_scan.py}, law/ (statute texts),
refs/ (raw pages: normattiva, MEF Roma register, Lazio 2026 table, circ. 4/E 2025 (copy from dirittobancario.it of
the AdE circular), GU 19/2014 extract).

## How to resume / rerun
- Build: `cd ~/cmp20/continental/it/lean && export PATH=$HOME/.elan/bin:$PATH && lake build` (needs ~/cmp20/kernel).
- Exe: `ittax [--euro] [--rent=cedolare|irpef] < households.jsonl` (money in euros with cents; --euro whole euros).
- OECD: `python3 ~/cmp20/continental/harness/oecd_check.py IT`. Scanner: `python3 harness/metr_scan.py`.
- Law: TUIR (DPR 917/1986) is NOT in Global law's italy corpus (only the 2026 testo unico); fetched from normattiva
  by `harness/fetch_law.py NAME URN ART DATE`. Lazio from Global law italy/lazio/acts; Roma from the MEF register.
- Web searches used: 8 of 8 (Lazio, Roma x2, INPS, assegno unico, cuneo novelty, forfettario coefficients, ...).

## Open items
- AUU: residuals 0,35 / 0,09 EUR vs OECD unexplained; INPS circ. 33/2025 amounts (rounded) not read.
- Self-employed INPS, forfettario in the default output, fringe-benefit notch (K7), owner-manager (K11) not modelled.
- Kernel harness scanners (~/cmp20/harness/search) did not exist yet; rerun them when they do.
- INPS 0,30 % employee share assumed (industry; the OECD's 9,49 %); sector-dependent.

## Family-lib / kernel gaps (also in ~/cmp20/kernel/INBOX.md)
- Kernel Out is whole units; Italy outputs cents (own writer); ITTax.country rounds to euros for tax20.
- No kernel part for a four-decimal ratio, a whole-income percentage chosen by band (L. 207/2024 c. 4), a local
  surtax due only when the central net tax is positive, or an ISEE equivalence-scale benefit. ContCommon not used.
