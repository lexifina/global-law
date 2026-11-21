# GR Greece: PROGRESS

Updated 2026-11-19 (milestone 4: model, validation, proofs, scans, findings written)
Status: done (first pass). Done 7/7. Web searches used: 2/3.

## What exists (all under ~/cmp20/southeast/gr)
- `lean/` (lib GRTax, exe grtax; euros with cents writer copied from PT): Params (every figure cited), Calc (person,
  child benefit), Country (contract), Theorems (kernel one-liners + statute properties), Loopholes (findings as
  theorems, `native_decide` on concrete households). 595 lines, 52 defs, 30 theorems, 0 sorry. Years 2023-2026
  (`year` field): 2023 credit table, 2024 credit table, 2025 EFKA 13.37 %, 2026 scales of ν. 5246/2025 (tax only).
- `law/`: statute extracts; `law/src/kfe_codif.{pdf,txt}` = official ΚΦΕ codification ΑΔΑ Ε7ΔΠΗ-Φ32 with dated
  footnotes (the 2025 wordings); `fek_a5_2018.*` (ν. 4512/2018, art. 214 child benefit); `e40.*` (e-ΕΦΚΑ Εγκ. 40/2024,
  health contribution cut); `efka_3_2025.txt` (Εγκ. 3/2025, ceiling 7,572.62); `opeka_a21.txt` (OPEKA amounts).
- `oecd_map.py`; `~/cmp20/southeast/oecd/check_gr.py` (OECD check at the OECD's own gross, years 2023-2025).
- `results/`: oecd_check.{json,md} (shared checker), oecd_check_gross_{2023,2024,2025}.{json,md}, oecd20/ (kernel
  checker), search/ (generic scanners, SUMMARY.md), summary.json.
- `FINDINGS.md` (F1-F12, M1-M4), `CATALOGUE.md` (12 known routes), `USEFUL.md`, `elections.json` (gr_childrenWith).

## Validation
- OECD TW 2025 at the OECD's own gross: 56/56 lines exact (|diff| ≤ 1 €; largest 0.47 € from whole-euro wages);
  2023: 56/56; 2024: 56/56. Shared check.py / harness oecd_check20.py (single wage fed to married types): 36/56,
  the 20 misses are exactly the married types' 10 % marriage allowance in the OECD gross (FINDINGS M1).
- No official AADE worked example or calculator compared yet (open).

## Company side for the owner-manager scan (proposed entry; INBOX line appended)
CIT 22 % (ΚΦΕ art. 58 par. 1(α): "Για τα εισοδήματα του φορολογικού έτους 2021 και εφεξής ... είκοσι δύο τοις εκατό
(22%)"); dividend 5 % (art. 40 par. 1); employer EFKA 21.79 % in 2025 (22.29 % in 2024 per OECD ERCSSC/GEBT, less 0.50
health in kind, e-ΕΦΚΑ Εγκ. 40/2024 on ν. 5162/2024 art. 12), ceiling 14 × 7,572.62 = 106,016.68 € a year (Εγκ. 3/2025).
The harness entry (OECD-derived 21.79 %, no ceiling) is right below the ceiling.

## Open / next
1. AADE worked examples (ΠΟΛ/Ε. circulars on art. 16) and an official withholding calculator, if usable without login.
2. Verify the employee 13.37 % split by branch (main pension, ΕΤΕΑΕΠ, ΔΥΠΑ) from a primary text; 2023-2024 ceilings.
3. Verify the 2025 minimum wage (art. 28Α base) from the ministerial decision; art. 28Α reductions/exemptions not modelled.
4. F5 (unmarried parents and A21): confirm how OPEKA treats cohabiting unmarried parents.
5. Self-employed EFKA categories (fixed amounts) not modelled; pensioners' 6 % health contribution not modelled.
