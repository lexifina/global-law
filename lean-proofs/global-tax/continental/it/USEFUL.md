# Italy 2025: what this work is useful for

Evidence: `FINDINGS.md` (F-numbers), Lean statements in `lean/ITTax/`, scanner output `results/search/METR.md`.

## For a taxpayer (an employee or pensioner resident in Rome)
1. Near 8.500 of income (about 9.390 gross pay), a small raise can cost you about 300 euro a year: the 2025 cuneo sum
   drops from 7,1 % to 5,3 % of your whole income and the regional surtax becomes due at the same point (F4,
   `cliff_8500`). Check where you are before accepting a few extra hours.
2. If you are just above a surtax threshold (IRPEF netta barely positive; Lazio's 28.000; Rome's 14.000 of taxable
   income), paying a little into a pension fund can save more tax than you pay in, and the money stays yours: 99
   euro saved 171 euro in our example (F5).
3. A spouse who earns more than 2.840,51 in a year stops being "a carico": the earning spouse loses about 690-710
   euro of detrazione (F8, `spouse_limit`). The limit has not changed since 1995 (F9).
4. Rent: the cedolare secca (21 %) is far cheaper for a landlord in the 35 % or 43 % band; for a low-income
   landlord IRPEF on 95 % of the rent can be cheaper. The model chooses for you (`--rent=`; K3).

## For an adviser
1. Thresholds are tested on different incomes: the detrazioni, trattamento integrativo and cuneo on the reddito
   complessivo (before oneri deducibili), the addizionali and their "dovuta" test on the imponibile (after). Planning
   with deductions works on the second set only (F5).
2. Above about 18.400 of income, a one-earner family with a dependent spouse and a child aged 21-29 pays the
   addizionali, stops paying them at 20.000 (the new 1.000 detrazione), and pays them again from about 21.450 (F7).
3. The regime forfettario's exit at 100.000 of fees is immediate and on the whole year (L. 190/2014 c. 71):
   11.700 of tax at 100.000 against about 29.240 just above it (78 % coefficient; `forfettario_exit_cliff`).
4. Circolare 4/E 2025 (note 60) on which relatives count for art. 51 was overtaken for 2025 itself by D.Lgs.
   192/2025 (art. 12 c. 4-ter): re-check 2025 welfare and fringe benefits for cohabiting parents (F13).

## For the Italian government (and the OECD)
1. Make the addizionali taper in instead of switching on with the first cent of IRPEF netta, or test them on the
   same income as the detrazioni: today one euro can cost 300 (F4) or 565 (F7), and a 99-euro deduction can save
   171 (F5).
2. The L. 207/2024 c. 4 cuneo sum applies one percentage to the whole income, so it falls by 153 euro at 8.500 and
   75 at 15.000 (`cuneo_cliff_8500`, `cuneo_cliff_15000`). A banded (marginal) formula would remove both cliffs
   at no cost to the rates.
3. Update the frozen amounts: the 2.840,51 dependants' limit (1995) and a dozen lire amounts still in TUIR artt. 10,
   15 and 51 (F9); clean the references to repealed commi in art. 13 (F10) when the 2026 testo unico takes over.
4. The OECD's Taxing Wages for Italy 2025 omits Lazio's two 2025 reliefs (L.R. 22/2024 art. 2 cc. 2-3), overstating
   the regional surtax by 60-175 euro for the published households (F1; draft note in FINDINGS). It also ignores
   the four-decimal rule of art. 13 c. 6 (cents; F2).
