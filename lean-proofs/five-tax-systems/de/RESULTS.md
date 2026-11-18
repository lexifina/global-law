# German income tax 2025 in Lean — results (18 November 2026)

Lean model `lean/` (DeTax, exe `detax`): EStG, SolZG 1995 and employee social contributions for VZ 2025. Referees: the
BMF's own publications (PAP 2025 pseudo-code, calculator interface, Datensammlung zur Steuerpolitik 2026) and GETTSIM
1.3.2. Findings S1–S7, P1–P3, G1–G9 and the corrections L1–L4 are in `FINDINGS.md`. Run outputs (`runs/`) are not published.

## Official values (the BMF decides)

| # | Benchmark | Source | Lean |
|---|---|---|---|
| 1 | Marginal and average tax rates 2025 at 10 000 … 150 000 €, single and splitting (44 printed values) | Datensammlung 2026, Tab. 2.6, column T2025 | 44/44 (`Tests.lean`); also 44/44 for T2026 with the 2026 coefficients |
| 2 | First wage bearing Lohnsteuer 2025: 16 836 € (I/0), 21 860 € (II/0,5), 31 586 € (III/0) | Datensammlung 2026, Tab. 2.4.1 | 3/3 (Lean PAP, `Tests.lean`) |
| 3 | Incomes from which the Kinderfreibetrag is "dauerhaft günstiger" 2025: 84 548 / 94 148 € (couples, 1/2 children), 44 644 / 54 244 € (single parents) and their Bruttolöhne 101 455 / 110 889 / 62 175 / 73 280 € | Datensammlung 2026, Tab. 2.8.3 | 4/4 incomes from the 4 wages to the euro; the switch exactly at 101 455 €; the four thresholds are theorems (`kg_permanent_joint`, `kg_permanent_single`, `kg_two_children`) |
| 4 | The 2025 formula and its coefficients | BMF Tarifhistorie (2025-10-14), Datensammlung Tab. 2.5.2, statute | identical (`t2025`, `boundaries`) |
| 5 | PAP 2025 tariff routine UPTAB25 | BMF XML pseudo-code | = § 32a for every whole-euro income (theorem `uptab25_eq_est`); class III = splitting (`pap_class3_is_splitting`) |
| 6 | BMF calculator (external interface, PAP 2025): 44 cases at the tariff and Soli boundaries + random cases (pay periods, Steuerklassen I–VI, children, KRV, Zusatzbeitrag, private insurance, Saxony, PV surcharge/reductions, church, Altersentlastungsbetrag, Freibetrag/Hinzurechnung) | bmf-steuerrechner.de, 61 s apart | **all identical** on LSTLZZ, SOLZLZZ, BK, VFRB, WVFRB (count: `PapBmf.lean`, `runs/bmf_pap/`) |

## Independent model (GETTSIM 1.3.2, 10 000 random households, `runs/g10k*`)

| # | Comparison | Result |
|---|---|---|
| 7 | Statute (Lean default) vs GETTSIM, all nine fields (ESt, zvE, Abgeltungsteuer, Soli, RV, AV, KV, PV, Kindergeld) | identical on all nine for 3 523; total burden within 1 € for 5 283; GETTSIM higher by > 1 € for 4 126 (mean over all households +364 €) |
| 8 | Lean with GETTSIM's readings switched on (`--gettsim-compat`) vs GETTSIM | total burden within 1 € for 9 994/10 000 (max 1,13 €; cent rounding of contributions); ESt equal for 9 986 (14 differ by 1 €); on a second sample of 10 000 (seed 777) within 1 € for all 10 000 |
| 9 | Each GETTSIM reading alone (households changed): tariff 2 906, § 24a 1 948, Vorsorge 2 166, no § 32d (6) 1 243, children together 163, contributions 1 425 | verdicts in FINDINGS G1–G8: the statute (and the BMF where it speaks) side with Lean except G8c, a reading |
| 10 | GETTSIM's tariff on every whole-euro income 0 … 400 000 € (single) / 0 … 800 000 € (joint) | equal on 398 358 / 332 394; GETTSIM 1 € low on 1 643 singles; joint: 1–2 € high on 465 964, 1 € low on 1 643 (G1, G2) |

## OECD Taxing Wages 2026 (year 2025), Germany (SDMX dataflow DSD_TAX_WAGES_COU@DF_TW_COU)

| # | Benchmark | Lean |
|---|---|---|
| 10a | 8 households (single 67/100/167 % AW, single parent, one- and two-earner couples), AW 66 700,04 € | 7/8 identical on contributions (±1 cent), taxable income, income tax + Soli and Kindergeld; the 8th (couple 100 % + 67 %, 2 children) differs by 54 € because the OECD compares all children at once (FINDINGS O1); with that reading Lean reproduces it to the cent |

## Other checks

| # | Check | Result |
|---|---|---|
| 11 | Lean tariff vs exact rational arithmetic (Python Fractions), 0 … 400 000 € | 400 001/400 001 |
| 12 | The formula in IEEE double ("Gleitkommarechnung", BMF Tarifhistorie), 0 … 400 000 € | 400 001/400 001: harmless for whole euros |
| 13 | Lean PAP UPTAB25 vs Lean § 32a, 0 … 300 000 € (evaluated) and all integers (theorem) | equal |
| 14 | `burdenSingle` (the closed form behind `marginal_peak`) vs the full model, wages 24 001 … 140 000 € step 7 | 16 572/16 572 |
| 15 | Speed | 140 001 households in 0,49 s (3,5 µs each, one core) |

## Proofs (`lean/DeTax/Theorems.lean`, 70 theorems with `Basic`/`Params`, no `sorry`, standard axioms)
Tariff: `est_mono`, `est_step` (0 or 1 € per euro, everywhere), `N_step_bounds`/`N_marginal`/`est_marginal` (14–45 %),
`N_step_z2`/`N_step_z3` (linear-progressive), `boundaries`/`boundary_steps` (continuity and the 9,41-cent jump),
`est_eq_zero_iff` (zero up to 12 103 €). Splitting: `splitting_costs_one_euro` (counterexample), `splitting_le_two`
(all incomes, via `step_cmp` and `conv_defect`: convex up to 9,57 cent), `splitting_zone3`,
`splitting_zone4` (at most +1 € within a zone). Soli: `soli_le_rate`, `soli_freigrenze`, `soli_milderung_step`,
`soli_full`, `soli_zone_2025`, `soli_band_rate` (47 %). Kindergeld: `kg_crossover_joint`, `kg_flips`,
`kg_permanent_joint`, `kg_permanent_single`, `kg_two_children`. Combined marginal rate: `marginal_peak` (53,23 %).
PAP: `uptab25_eq_est`, `pap_mlst`, `pap_class3_is_splitting`, `pap_class5_cents`. The peak is the highest for wages
24 001–96 600 €: `marginal_low` (≤ 50,7 %), `marginal_mid` (≤ 53,23 %), with `zvC_rise`, `step_le_42`, `soli_step_le`.

## Final BMF interface result (2026-11-18)
- compared 644: identical on LSTLZZ, SOLZLZZ, BK, VFRB and WVFRB for all 644; no mismatches.
- `lean/DeTax/PapBmf.lean` holds the 644 answers as one `#guard` check, which `lake build` evaluates. (The file as
  first generated stopped Lean at its recursion limit; `set_option maxRecDepth` was added when it was published, and
  the check passes.)
