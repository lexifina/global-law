# Poland (PL), tax year 2025: progress

Owner: PL sub-agent of the emerging group. Files: `lean/` (Lake project PlTax + TaxKernel by path, exe `pltax`),
`oecd_map.py` (also `map_pl` for the kernel harness), `results/` (summary.json, oecd_check.*, search/ from the kernel
scanners), `runs/` (scan.py → scan_results.json, sanity.jsonl), `refs/` (official texts fetched 2026-11-19: PIT t.j.
Dz.U. 2025 poz. 163, ryczałt t.j. 2025 poz. 843, health t.j. 2025 poz. 1461, SUS t.j. 2025 poz. 350, Polski Ład Dz.U.
2021 poz. 2105, Dobry start Dz.U. 2018 poz. 1061, M.P. notices 2023/1342, 2023/1456, 2024/1051, 2024/1055, 2024/1084,
2025/84, Dz.U. 2024/1362, ZUS and podatki.gov.pl pages, ERSJ 2025 paper; `*.txt` = pdftotext), FINDINGS.md (F1-F16),
CATALOGUE.md (K1-K19), USEFUL.md, HOWWRITTEN.md.

## Status: done (7/7), 2026-11-19 01:15 UTC

| Step | State |
|---|---|
| 1 Model + exe | done. PL-only optional fields: per adult `plRegime`, `plZus`, `plRyczaltBp`, `plSeRevenue`, `plSex`, `plCommuter`, `plReturning`; per household `plRentalOnePerson`, `plFiling` (doc in `lean/PlTax/Main.lean`, choices in `Household.lean`) |
| 2 Validation | OECD TW 2025: 48/48 mapped lines within 1 PLN; THP 0/8 because the OECD leaves out the subkonto (F1, explained); podatki.gov.pl example 4 224,12 zł exact; 7 official 2025 figures re-derived (F13). No official PIT calculator exists on podatki.gov.pl |
| 3 Proofs | done: Theorems.lean (scale = statute, kwota wolna = 30 000 zł zero band, monotone, marginal 0/12/32, no jump, ≤ 32 %, joint ≤ separate, gain ≤ 27 600 and = 27 600, relief caps), KernelLink.lean (kernel instantiations + bridge `scaleTax = TaxKernel schedule`) |
| 4 Known loopholes | CATALOGUE.md: 19 catalogued, 13 recreated, 5 not modelled, 1 partly |
| 5 New loopholes | F3 one-child notch band, F9 zero-METR payout band, F10 ryczałt outside the one-child test, F16 ceiling bunching (Lean facts in Findings.lean) |
| 6 Gov errors / statute | no government error (F1, F2, F8 conventions/design; F13 all figures correct); statute: F12 112 000 zł unindexed since 2013; F11 85 528 zł checked, deliberate |
| 7 USEFUL.md | done |

## Open (optional depth, in order of value)
1. Partial years: ages that change during 2025 (26th birthday, child turning 18) are taken as whole years (reported in
   `unsupported`); a month field would make K10 timing modellable.
2. Zdrowotna art. 83 cap of the employee health contribution (binds below ~1 250 zł a month) not modelled.
3. Adult children (art. 27f ust. 6, 18-24 in school), mały ZUS plus, IP Box, owner-manager CIT (kernel `company.json`).
4. Full migration of `PlTax.Kernel` to TaxKernel parts (today bridged by `KernelLink.bridge`; numbers unchanged).

## How to resume
`cd ~/cmp20/emerging/pl/lean && export PATH=$HOME/.elan/bin:$PATH && lake build` (needs `~/cmp20/kernel` built);
`python3 ~/cmp20/emerging/oecd/check.py PL`; `python3 ~/cmp20/harness/oecd_check20.py PL --out results`;
`python3 runs/scan.py`; `python3 ~/cmp20/harness/search/run_all.py PL --out results/search`.

## Kernel
API.md v1.0 appeared during the work; the model requires TaxKernel by path and instantiates `ticks_mono_of_progressive`,
`ticks_convex`, `splitting_le_separate`, `ticks_le_maxRate_mul` for the Polish scale; `KernelLink.bridge` proves the
model's scale equals the kernel schedule on every whole-złoty base. Gaps listed in `results/summary.json`.

## Web searches used: 2 of 6
1. OECD Taxing Wages Poland: subkonto treatment (xyz.pl summary of TW 2026).
2. OECD/EU/literature on B2B and the flat regimes (found ERSJ 2025, IBS 2014, EU country report).
