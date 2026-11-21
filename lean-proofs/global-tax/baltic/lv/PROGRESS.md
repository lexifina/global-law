# Latvia (LV), tax year 2025 (calendar): progress

Owner: Nordic + Baltic family, LV worker. Contracts: ~/cmp20/CONTRACT38.md + CONTRACT20.md. Folder: ~/cmp20/baltic/lv.
Status: **done** (steps 1-7), 2026-11-19. Resume from here; everything below is reproducible.

| step | status | where |
|---|---|---|
| 1 model | done | `lean/` (lib LvTax, exe lvtax; Params, Basic, Theorems, Tests, Findings, Main); `lake build` clean, 0 sorry |
| 2 validation | done | OECD TW 2025 country table 56/56 exact (`results/oecd_check_LV.md`); OECD decomposition 2025, 804 households × 4 lines: 3 200 exact, 3 216 within 1 % (`results/oecd_decomp.md`, `tools/oecd_decomp.py`); VID "Algas nodoklis 2025" 8 examples (13 values) + "Attaisnotie izdevumi" 2 examples, kernel-checked (`LvTax/Tests.lean`); withholding vs annual (`runs/lv_scan.md` §5) |
| 3 proofs | done | `LvTax/Theorems.lean` (kernel Schedule/Unit/lowBand/Contribution/Surcharge theorems + Latvia's closed forms), `LvTax/Findings.lean` |
| 4 known loopholes | done | `CATALOGUE.md`: 20 catalogued, 14 recreated (6 blind), 6 not modelled |
| 5 new loopholes | done | generic scanners `results/search/SUMMARY.md`; targeted `tools/lv_scan.py` → `runs/lv_scan.md`; FINDINGS F1-F3 |
| 6 gov / statute errors | done | FINDINGS F8, F13 (VID, readings), F10-F12 (statute) |
| 7 USEFUL.md | done | `USEFUL.md`; `FAMILY_NOTES.md` |

## Commands
```
export PATH=$HOME/.elan/bin:$PATH; cd ~/cmp20/baltic/lv/lean && lake build
python3 ~/cmp20/baltic/harness/b38.py oecd LV --out ~/cmp20/baltic/lv/results
python3 ~/cmp20/baltic/lv/tools/oecd_decomp.py
python3 ~/cmp20/baltic/harness/b38.py scan LV --out ~/cmp20/baltic/lv/results/search
python3 ~/cmp20/baltic/lv/tools/lv_scan.py
```

## Sources (saved under refs/)
likumi.lv: IIN likums id 56880 redakcijas 01.01.2024, 01.01.2025, 16.05.2025 (the one used), current 2026;
VSAOI likums id 45466 (01.01.2025); Solidaritātes nodokļa likums id 278636; UIN likums id 292700 (01.01.2024-31.12.2025;
2026); MUN likums id 215302 (01.01.2025; 2026); Valsts sociālo pabalstu likums id 68483 (01.01.2025). VID media
27931, 27996, 33101 (+ 9 other VID materials fetched, refs/vid/). LV portāls 35368, 37184, 37449. OECD ES Latvia 2017
(em.gov.lv media 2173). OECD TW data from ~/cmp20/baltic/oecd (family lead). OECD 2024/2026 survey pages: HTTP 403.
Web searches used: 3 of 3 (VID self-employed VSAOI 2025; VID 33 % worked examples; OECD survey micro/royalty/dividends).

## Model choices (also in the exe's `unsupported`)
Amounts in cents, output rounded to whole euro; dividends exempt (paid from CIT-taxed profit); self-employment
spread evenly over 12 months (option lvSeMonths), lowest permitted VSAOI object, no minimum quarterly contributions;
children 16-19 at school / 18-23 in education by default (childrenInEducation); a person with pension income is a
pensioner (minimum 12 000, VSAOI 9,25 %); rent at 10 % of receipts; micro income outside the 3 % base (VID reading,
F13); options lvSeRegime = general | micro | royalty. Not modelled: izdienas pensija rate, disability reliefs,
medical/education costs (no contract field), loans to shareholders, retained profit, investment account.

## Open issues
- F3 depends on the reading of "nestrādājošs laulātais"; F2 on when self-employed income arises.
- The self-employed minimum contributions of VSAOI 20.4(3.1) (10 % of the shortfall below 12 minimum wages) are
  assumed avoided by the planned-income declaration of 20.4(3.2); if not, low self-employed incomes pay more.
- No official IIN calculator usable without login was found (VID publishes worked examples instead; used).
- The owner scan used the kernel's LV company entry (OECD data, same 20 % / 23,59 %); `company.json` here has the
  statute-cited version (adds the employer's net 14,5 % solidarity share above 105 300).
