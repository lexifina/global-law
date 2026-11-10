# Group C findings: the tax (§1(j), §3 Tax Table, §1(h), §§55–56), tax year 2025

Files: `Schedule.lean`, `Table.lean`, `CapitalGains.lean`, `AMT.lean`, `All.lean` (axiom check).

- 57 theorems.
- 26 `#guard` checks covering about 100 printed IRS figures.
- No `sorry`, no `native_decide`; the main theorems use only `propext`, `Classical.choice` and `Quot.sound`.

## Findings

1. **No 2025 bracket changed.**
   - Pub. L. 119-21 §70101(c) applies its §1(j) changes only to years after 2025, although the OLRC text already shows
     the new wording.
   - All 24 base amounts in Rev. Proc. 2024-40 Tables 1–4 check out (`sched_ok`).
   - All 20 subtraction amounts in the 2025 Tax Computation Worksheet match the schedule to the cent at every income
     from $100,000 (`tcw_eq_schedule`).
2. **The schedule's marginal rate is always between 10% and 37%, and 37% is reached.**
   - This holds for every filing status (`scheduleCents_marginal`, `scheduleTax_step`, `scheduleTax_mono`,
     `scheduleCents_top`).
   - Below $100,000 the rate is at most 22%.
   - Married filing separately is exactly half of joint at every income (`mfs_half_mfj`).
   - There is no marriage penalty up to $375,800 each (`no_marriage_penalty`). At $700,000 each, filing jointly costs
     $10,022 more.
3. **The Tax Table differs from the schedule by −$5 to +$6.**
   - `table_within_6` proves the ±$6 bound for every status and every income under $100,000.
   - +$6 occurs: single $48,500 is $5,590 in the Table against $5,584 on the schedule.
   - −$6 never occurs; the worst case is −$5 (`table_ge_minus5`).
   - The Table never decreases, and one more dollar costs at most $11 (`line16Tax_step`).
   - §3 says nothing about midpoints, and it limits the Table to people who do not itemize. The IRS uses it for
     everyone under $100,000, relying on §3(a)(3).
4. **The §1(h) sum can exceed the ordinary tax.**
   - The 0% ceilings ($48,350, $96,700, $64,750) sit just below the top of the 12% bracket ($48,475, $96,950,
     $64,850).
   - Gain in that strip is charged 15% instead of 12%. The proved maximum excess is $3.75 single and separate, $7.50
     joint and $3.00 head of household, each reached (`capGainSum_excess_max`).
   - The statute's "shall not exceed" and worksheet line 25 cap the tax at the ordinary amount (`regularTax_le`).
5. **Moving wages into qualified dividends can raise the tax by 3¢ per dollar.**
   - Single, $60,000 of taxable income, dividends going from $11,600 to $11,601 (`more_dividends_more_tax`).
   - This is a worked example only; no general bound is proved.
6. **§1(h)(1)(A)(ii)(I) still says "taxed at a rate below 25 percent".** There has been no 25% rate since 2018. This
   matters only for 28%-rate and §1250 gain, which are not modelled.
7. **The 15% ceiling for married filing separately is $300,000, not half of $600,050 ($300,025).** That ceiling is
   halved before indexing (with $50 round-down), while the 0% ceiling is halved after indexing.
8. **The 2025 AMT phase-out is 25%, not 50%.**
   - The OLRC text shows the 50% rate and re-indexed threshold, but §70107(d) starts them after 2025. Rev. Proc.
     2024-40 and the 2025 Form 6251 use 25% (`zero_points`).
   - Open for 2026: the 50% substitution applies to "paragraph (2)", which contains "25 percent" twice. Read
     literally, the separate-filer add-back also becomes 50%.
9. **The tentative minimum tax's marginal rates are exactly 0, 26, 28 or 35%** for all incomes and statuses
   (`tmt_marginal`).
   - 32.5% never occurs, because the 26% band ends before the phase-out starts.
   - 35% is the maximum and is reached.
   - For separate filers, the add-back carries 35% on to $1,174,350.
10. **With only SALT, the standard deduction and the senior deduction added back, the AMT stays zero** while the
    add-backs total at most $45,411 single, $46,614 joint, $38,723 head of household and $23,307 separate
    (`amt_unreachable`, for every taxable income).
    - These limits are tight to within rounding (`safe_tight`).
    - Standard-deduction filers never owe AMT.
    - Itemizers at the $40,000 SALT cap never owe it if single, joint or separate.
    - A head of household can owe it: $332 at $197,300 with $40,000 of SALT (`hoh_salt_amt`).
    - A single itemizer aged 65+ is a narrow corner case (`single_senior_corner`).
11. **Gains inside the AMT keep the 0/15/20% rates, but the bands come from regular taxable income**
    (`tmt_capgain_le`).
    - In the phase-out, gain taxed at 20% has a marginal tentative-minimum-tax rate of 27%
      (`gain_rate_in_phaseout`).
    - The literal "excess (if any)" is modelled where gains exceed taxable income. This was not compared with Form 6251
      Part III, because only the 1040-NR line text could be fetched.
12. **The senior deduction is added back on Form 6251 line 1b.**
    - §56(b)(1)(D) denies "the deduction for personal exemptions under section 151".
    - The senior deduction sits in §151(d)(5)(C) but is not an exemption, so the IRS reading is plausible rather than
      explicit. The model follows the form.
13. **The worksheet's amounts on lines 5, 9, 17 and 20 equal the statute's** (`worksheet_lines_eq`). The worksheet
    result is within $7 of the exact statutory tax (`regularTax_near`); random sampling found at most $6.

## Interface

- `scheduleCents` / `scheduleTax (f) (ti)`: exact cents, and whole dollars rounded half up.
- `tableTax` and `line16Tax`: the Table below $100,000, the schedule from $100,000.
- `regularTax (f) (ti qualDivAndLtcg)`: the worksheet result. `regularCents` is the exact statutory amount.
- `amt (f) (taxableIncome saltDeducted stdDeduction seniorDeduction qualDivAndLtcg regularTax)`, plus `amtForReturn`.
- Gap: `Return` lacks the SALT amount actually deducted and the senior deduction, so both are passed in.

## Tests and sources

- **Rev. Proc. 2024-40 §2.01:** 24 base amounts and 6 row checks.
- **2025 Form 1040 instructions:**
  - Tax Computation Worksheet, p. 80: 20 subtraction amounts.
  - Tax Table, pp. 68–79: 20 checks covering 70+ printed entries, including the $25,300 joint worked example
    ($2,562).
  - Qualified Dividends and Capital Gain Tax Worksheet, p. 37: the line 6 and line 13 thresholds.
- **Rev. Proc. 2024-40 §2.11:** the complete phase-out amounts.
- **2025 Form 6251 instructions:** the separate-filer example and the $68,500 cap; the line 7 shortcut (28% minus
  $4,782, or $2,391 separate), proved for every amount.

## Not modelled

- §1(g) kiddie tax.
- 28%-rate gain, §1250 gain, and the Schedule D Tax Worksheet.
- Foreign earned income, Schedule J, and estates and trusts.
- AMT items other than SALT, the standard deduction and the senior deduction; the AMT foreign tax credit; the §53
  credit.
- 2026 figures and the 50% phase-out.

## Independent review (step 4)

The reviewer had not written this group.
- **Fixed an error in `AMT.lean` (`tmtCapGainQ`).** The §55(b)(3)(B) 0% band uses the excess described in §1(h)(1)(B),
  floored at zero as in the regular tax and on Form 6251 line 20. The AMT code used the unfloored figure, so when gain
  exceeded taxable income all of it sat at 0%. New theorem `tmt_gain_over_ti` covers this case.
- **Finding 10 downgraded.** `amt_unreachable` holds only with no net capital gain. Large gains make the AMT reachable
  even with no add-backs (`gains_amt_reachable`: $197,300 of ordinary income plus $1,000,000 of gain owes $15,194). The
  claims "standard-deduction filers never owe AMT" and "itemizers at the SALT cap never owe it" need the qualifier "with
  no net capital gain and no other preferences".
- **Finding 6 reworded.** "Below 25 percent" still reaches the top of the 24% bracket. The point is only that
  §1(j)(5)(A) did not rewrite (A)(ii)(I); it has no effect without 28%-rate or §1250 gain.
- **Finding 12 upgraded to explicit.** The 2025 Form 6251 instructions say the senior deduction "is treated as a
  personal exemption that is added back". Those instructions cite "§56(b)(5)(D)", which looks like a typo for
  §56(b)(1)(D).
- **Test provenance corrected.** `exemption_worksheet_example` is the authors' own example, not one printed in the
  Form 6251 instructions.
- **Weak theorems.** `regularTax_le`, `regularCents_le` and `tmt_capgain_le` hold only because the result is a `min`.
  `worksheet_lines_eq`, `regularTax_near` and the fixed tests are what pin the computation down.
- **Verified against the source:** every 2025 figure in Rev. Proc. 2024-40 §§2.01, 2.03 and 2.11, the 27 Tax Table rows
  cited, and the Form 6251 worksheet figures.
