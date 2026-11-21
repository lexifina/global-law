# ES (Spain, state + Comunidad de Madrid, ejercicio 2025): progress

Updated 2026-11-19. Owner: ES worker (continental family). Contract: `~/cmp20/CONTRACT20.md`.

## Status: done (7/7 steps at first depth); open items below
| Step | State |
|---|---|
| 1 Model `lean/ESTax`, exe `estax` | done. LIRPF arts. 17-20, 46-52, 56-58, 61, 63, 66, 67, 69, 74, 76, 77, 81, 81 bis, 82, 84, 96, DA 61.ª (Ley 5/2025); Madrid DLeg 1/2010 arts. 1, 2, 2 bis, 4, 14, 18.1; SS Orden PJC/178/2025 incl. solidaridad; Ley 49/2002 art. 19; joint vs separate chosen automatically (`--joint`/`--separate` force) |
| 1 OECD | state lines 32/32 within 0,76 EUR; SLT differs (OECD weighted regions, F1) |
| 2 Referees | AEAT withholding algorithm implemented (`ESTax/Withholding.lean`, output detail `withholding`); AEAT 2025 guide parameter check; no official numeric worked example found |
| 3 Proofs | `ESTax/Theorems.lean`: 31 theorems, no sorry (scales progressive/monotone/convex via kernel; printed cuota columns = rounded band sums; mínimo = bottom-rate credit; art. 20/DA 61 continuity; withholding scale = 2x state except top band; 7 concrete household theorems for F2-F8) |
| 4 Known loopholes | `CATALOGUE.md`: 16 catalogued, 10 recreated, 6 not modelled |
| 5 New | `NOVEL.md`: 4 new (F3, F4, F6, F7) |
| 6 Gov/statute errors | F2 (RIRPF art. 81 not updated for the 2025 SMI; AEAT text outdated), F5 (6.500 EUR not indexed), F10 (art. 20 endpoint); conventions F1, F11 |
| 7 Useful | `USEFUL.md` |

## Files
`FINDINGS.md`, `CATALOGUE.md`, `NOVEL.md`, `USEFUL.md`, `results/summary.json`, `results/oecd_check.{json,md}`,
`oecd_map.py`, `law/` (statute excerpts + URLs), `refs/` (AEAT algorithm 2026, AEAT bulletin Ley 5/2025, OECD
country note 2026), `harness/` (es.py, scan_metr.py, scan_withholding.py, recreate.py), `runs/` (outputs).

## How to resume
- Build: `cd ~/cmp20/continental/es/lean && export PATH=$HOME/.elan/bin:$PATH && lake build` (requires TaxKernel at
  ../../../kernel; the lake build may replay kernel files).
- OECD: `python3 ~/cmp20/continental/harness/oecd_check.py ES`; scans: `python3 harness/scan_metr.py` etc.

## Open items (next, in order of value)
1. Official worked examples: the AEAT Manual práctico Renta 2025 chapter pages (capítulos 3, 14, 16) were not
   reached (index page truncated); fetch individual example pages and add them to `Tests`.
2. OECD regional weights: if the Taxing Wages 2026 Spain chapter becomes readable (oecd.org refused automated fetch),
   add a region "oecd" reproducing its regional schedule, and re-run the check.
3. DA 61.ª limit formula and joint-return treatment: confirm against the AEAT Manual (model uses a stated reading).
4. Not modelled: art. 93 impatriados, art. 7 p), loss netting (arts. 48-49), disability mínimos, other Madrid
   deductions (art. 3 list), RETA contributions, art. 81.2 guardería.

## Kernel / family-lib gaps
- Kernel `Out`/`countryMain` write whole units; Spain needs cents (own JSON writer in `ESTax/Main.lean`).
- Kernel `Canon` rounds inputs to whole euros (cents read from the raw JSON).
- Statutory tables with a printed cuota column (`Row`, `tableTax`; consistency proved per table).
- The "mínimo at the bottom of the scale" construction (`cuotaMinusMin`); all-or-nothing income-limited deductions.
- No generic kernel theorem failed for Spain (nothing sent to `~/cmp20/kernel/INBOX.md`).

Web searches used: 5 of 7.
