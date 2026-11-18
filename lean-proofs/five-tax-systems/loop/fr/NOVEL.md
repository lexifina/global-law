# France: bounded novel search (income 2025), 18 November 2026

Extends [`FrTax/reports/LOOPHOLES.md`](../../../FrTax/reports/LOOPHOLES.md) step 2 (marginal-rate rays, choice pairs, CDHR × credits, 61 € / 157 bis / 197 C
interactions). New dimensions searched here: the value of every lever across the three CDHR zones, the global cap
with the CDHR, the interplay of four options decided jointly, family benefits with tax and contributions, and the
quotient for exceptional income. Script `harness/novel.py` (N1–N6), results `runs/novel_n*.json`; about 0.4 M Lean
returns, a few CPU-minutes. Proofs `lean/FrLoop/Proofs.lean` (`native_decide`, checked: a false statement is
rejected). Production simulator: 8 requests, sequential, 1.2 s apart
(`runs/sim.jsonl`; production's "Impôt sur le revenu net" includes CEHR and CDHR).

Status: **novel** = not found in the sources checked (BOFiP corpus, the earlier report's sources, 2 web searches);
**variant** = known rule, new combination or size; **known**; **artefact** = model or rounding.

## Results

| # | Finding | Size | Cause | Status | Checks |
|---|---|---|---|---|---|
| N1 | **Home help makes a CDHR payer pay more tax.** Single CDHR payer (salary 150 k€, dividends 800 k€) subscribing 50 000 € to SMEs: adding 12 000 € of home help raises the burden by 5 000 € | +5 000 € (plus the spending) | the 6 000 € credit is taken back by the CDHR (art. 199 sexdecies is not listed in art. 224, IV, A, 2°) but still counts against the 10 000 € global cap (art. 200-0 A), crowding out 5 000 € of the IR-PME reduction, which the CDHR does not take back (loi 2025-127, art. 10, II) | **novel** (not found; one web source says the two "apply in parallel") | Lean `homehelp_costs_cdhr_payer_2025`; production confirms the CDHR line 20 438 → 26 438 € with home help; box 7CF was not taken as an IR-PME subscription by the simulator (no reduction applied), so the PME half is unconfirmed in production |
| N2 | **In the CDHR smoothing band, deductions are worth 82.5 % and reductions at most the scale tax.** Single, salary 30 k€ + dividends 290 k€: a 10 700 € property deficit saves 8 827 €, a 6 855 € alimony 5 655 €; PER, exempt overtime, gifts and home help 0 €; Pinel, PME and Girardin only 1 564 € (couple: 3 388 €), the whole scale tax | 82.5 % of the deduction | inside 224, V the CDHR + income tax + CEHR equals 82.5 % × (R − 250 k€): anything that lowers R saves 82.5 %; reductions come off the scale tax only, not the 12.8 % flat tax (art. 197, I, 5; what production does), and the dividend-heavy band households have little scale tax | variant of LOOPHOLES finding 3 | Lean `band_deficit_2025`, `band_alimony_2025`, `band_per_2025`; production 55 275 → 46 447 € (Lean 46 448: 1 € rounding in the CDHR) |
| N3 | **Retiring director's 500 000 € allowance also lifts the CDHR.** Gain 700 000 €, pension 30 000 €: 145 400 € without the allowance, 43 744 € with it | 101 656 € (64 000 € flat tax + 37 656 € CDHR) | art. 224, II, 1° removes the a bis allowances other than 150-0 D 1 ter / 1 quater from the CDHR base; the RFR (CEHR) keeps them. The household falls under the 250 000 € threshold | variant (statutory; the size and the CDHR effect not found described) | production: 43 744 € and 145 400 €, equal to Lean (emulated with 2EE; CDHR rerun on the base without it) |
| N4 | **The CDHR reverses attach vs alimony.** Above the band, attaching an adult child saves 1 500 €, the 6 855 € alimony 1 371 €; without the CDHR the alimony wins (2 811 € vs 1 807 € at salary 120 k€) | 129 € | the QF half part is taken back by the CDHR, the 1 500 € per dependant (224, III, 2°) is not; the alimony is worth 20 % of the RFR it removes. In the band the alimony wins again (5 655 € vs 1 500 €) | **novel** (small) | Lean `cdhr_prefers_attachment_2025` |
| N5 | Exceptional income with the CDHR: 300 000 € with 150 000 € of dividends costs 87 616 € under the quotient vs 136 724 € as ordinary income | 49 108 € | 224, II, ninth paragraph counts exceptional income for a quarter in the CDHR base (whether or not 163-0 A is chosen), IV, A, 1° and B, 3° the tax and CEHR on it for a quarter; plus the quotient itself | variant (statutory; which gains qualify as exceptional is in BOI-IR-CDHR-20 § 160–190, not checked) | Lean (frloop) only |
| N6 | Options interact: deciding 2OP, attach/alimony, actual expenses and micro-foncier/réel each on its own (vs the default) misses the joint optimum for 1 296 of 20 000 random households (6.5 %), median 170 €, max 1 593 €; trying them one by one in a fixed order still misses for 459 (max 1 465 €) | ≤ 1 593 € | each option's value depends on whether the household pays scale tax: e.g. a single parent of 3 with 83 k€ of dividends gains nothing from actual expenses under the PFU (scale tax 0), but 2OP brings dividends into the scale and then actual expenses are worth 1 593 € | known in principle (the simulator is meant to be run on each combination); the size is new | `runs/novel_n2.json` |
| N7 | Family benefits × tax × contributions: effective marginal rates on gross pay of 118–119 % over 1 200–5 000 € bands at both allocations familiales ceilings (couple 2 children: gross 101.0–102.2 k€ and 134.3–135.0 k€; 4 children 117.7–122.6 k€ at 107 %); 145–147 % for one 100 € step where two earners both cross the PASS | 1.18 € per 1 € | the complément dégressif (CSS D521-1, II) withdraws the allocation one for one above each ceiling; income tax, CSG and contributions come on top; the CET (0.14 %) starts with a jump at the PASS | known mechanism (the 100 % withdrawal is by design); the combined rate is a variant. Caveat: the allocations use the resources of year N−2 (CSS R532-3), so the rate falls on two different years | `runs/novel_n3.json` (Python port of `Compare/Fr.lean`, matches its #guard values) |
| N8 | 2OP chosen only because it lowers the allocations familiales resources: 17 grid points (couple 2 children, gross 95–97 k€, dividends 4–7 k€), up to 894 € | ≤ 894 € | the comparison adapter counts dividends under 2OP after the 40 % allowance (net categorial income) and under the PFU in full | **unverified**: rests on the adapter's reading of CSS R532-3 (resources = net categorial income + income under the flat levy); the text was not obtained (Légifrance blocks bots), so possibly an adapter artefact | `runs/novel_n3.json` |
| N9 | Quotient never materially worse than ordinary taxation: worse in 571 of 8 820 pairs, by at most 3 € | ≤ 3 € | rounding of the ×4 step | artefact | `runs/novel_n5.json` |
| N10 | Exempt overtime, PPV and PER worth (almost) 0 to CDHR payers (85 € and 73 € for overtime above the band, the 10 % allowance share) | — | kept in the RFR (1417, IV) and so in the CDHR base | variant of LOOPHOLES finding 2 | N1 table `runs/novel_n1.json` |

## Lever × CDHR zone (N1, savings in €; `runs/novel_n1.json`)

| Lever | single, no CDHR (120 k€) | single, band | single, above band | couple, band | couple, above band |
|---|---|---|---|---|---|
| attach adult child | 1 807 | 1 500 | 1 500 | 1 500 | 1 500 |
| alimony 6 855 € | 2 811 | 5 655 | 1 371 | 5 655 | 1 371 |
| PER 10 000 € | 4 100 | 0 | 0 | 0 | 0 |
| property deficit 10 700 € | 4 387 | 8 827 | 2 140 | 8 827 | 2 140 |
| overtime 7 500 € exempt | 2 768 | 0 | 85 | 0 | 73 |
| gifts 10 000 € | 6 600 | 0 | 0 | 0 | 0 |
| home help 12 000 € | 6 000 | 0 | 0 | 0 | 0 |
| Pinel 5 000 € | 5 000 | 1 564 | 5 000 | 3 388 | 5 000 |
| IR-PME 50 000 € (9 000 €) | 9 000 | 1 564 | 9 000 | 3 388 | 9 000 |
| Girardin 20 000 € | 20 000 | 1 564 | 20 000 | 3 388 | 20 000 |
| prestation compensatoire 30 500 € | 7 625 | 0 | 0 | 0 | 0 |

## Searched, nothing new
- Contribution thresholds: only the CET jump at the PASS (+65.94 € for 1 €, known from the comparison) and the
  61 € notches already in LOOPHOLES.
- Quotient × décote × QF cap: no case where the quotient costs more than ±3 € of rounding.

## Not verified / limits
- The IR-PME, Pinel, Girardin and Malraux reductions, the global cap and the quotient are additions in
  `FrLoop/Extra.lean` (statute and BOFiP cited there); production checks could not be made for the reductions
  (simulator box codes for 2025 not established; 7CF was ignored).
- The cap is taken from the investment reductions only; reductions are capped before imputation; no
  carry-forward.
- Family benefits: same-year resources as in the comparison adapter (law: N−2).
