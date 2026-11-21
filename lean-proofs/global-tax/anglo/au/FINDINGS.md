# Australia: findings (income year 2024-25; 2025-26 where stated)

Model: `lean/` (AuTax, exe `autax`, built on TaxKernel 1.0: `Schedule`, `Surcharge`, `Credit`, `Taper`). "Burden"
below = income tax after offsets + Medicare levy + MLS + Div 293 + the fund's 15 % contributions tax + HELP
repayment - FTB (- PP(S) when claimed). Runs in `runs/` (oecd_2025*.json, metr_scan.json, loopholes.json,
generic_scan.json, sched1_vs_statute_*.csv); kernel scanners in `results/search/SUMMARY.md`. Sources:
`refs/SOURCES.md`. Lean names refer to `lean/AuTax/*.lean` (all proved, no `sorry`; 12 use `native_decide`).

### F1 Validation: OECD Taxing Wages 2025 reproduced line for line
kind: model-fix (validation). Households: the 8 OECD family types at AW $108,674. With the OECD's two assumptions
switched on (`autax --oecd`: grandfathered energy supplement; the sole parent claims Parenting Payment (Single))
all 40 lines (IT, ML, CGITFP, CTGG, THP) agree within $1; the residual cents come from the OECD's fractional gross
(the statute taxes whole dollars). On the model's statutory defaults (a new claimant, no income support): 36/40;
SP67 CTGG -$1,848.11 and M100_0 -$124.10, fully explained by F2 and F3. Kernel harness `oecd_check20.py AU`
(defaults): CGITFP 8/8, EECSSC 8/8, CTGG 6/8, THP 7/8 within 1 %. Status: done.

### F2 The OECD assumes the energy supplement, closed to new FTB claimants since 2016-17
kind: gov-error (classification: convention, disclosed). OECD chapter: "The calculations assume families and
individuals are eligible for the energy supplement as a significant proportion of FTB(A) and FTB(B) recipients were
eligible". FA Act Sch 1 cll 6A, 25C, 29AA keep it only for those continuously eligible since 19 September 2016
(DSS guide 3.6.1 Table 4: "From 20 March 2017, ES ceased for new FTB claimants"). Effect on the OECD's CTGG:
+$124.10 for M100_0 (ES A base 2 x $36.50 + ES B $51.10), +$233.60 for SP67. A family forming today receives less
than the OECD shows, and the share of families who still get it shrinks every year. Status: documented.

### F3 The income-support passport: a few dollars of Parenting Payment switch off the FTB A income test
kind: loophole-new (notch; lead). FA Act Sch 1 cl 38L: if the individual "is receiving a social security pension, a
social security benefit ... the individual's income excess is nil". A sole parent with two children at the OECD's
67 % AW ($72,811.58) still has a residual PP(S) entitlement (OECD annualised parameters: maximum $26,104.20 +
pharmaceutical allowance $176.80 + ES $312, reduced by 40 % above $5,735.60 + $639.60 for the second child), so
(i) the full PA $176.80 and the telephone allowance $146.71 are paid (OECD CTHF $323.51 = 176.80 + 146.71 exactly)
and (ii) FTB A is paid at the maximum rate with no 20 % income test ($1,524.52 more). When the residual runs out
(annualised: at $72,078 of earnings) the family loses $1,701.63 for one more dollar.
Lean: `notch_income_support_passport` (Notches.lean). The OECD's SP67 CTGG ($17,850.81) is reproduced exactly only
with this rule (F1), so the OECD applies it. Caveat: PP(S) is assessed fortnightly; the annual notch is the OECD's
annualisation. Novelty: the cliff was not found in 1 web search (17 results, incl. Services Australia and DSS rate
lists); not claimed new.

### F4 FTB A supplement: a $916.15-per-child notch at $80,000 that is never indexed
kind: statute-fault (thresholds not updated together) + loophole-known (notch). Sch 1 cl 38A(1A): the supplement "is
nil if the individual's adjusted taxable income is more than $80,000". Sch 4 cl 2 indexes the supplement itself
(item 8A: $600 base, $916.15 in 2024-25, $938.05 in 2025-26), the lower and higher income free areas (items 13, 11)
and the FTB B limit (item 17AA), but not the $80,000. One dollar over costs $1,832.82 (2 children, 2024-25;
`notch_ftb_supplement`) and $1,876.62 in 2025-26 (scan). The limit has fallen from 1.54 x the lower income free
area (2016-17: $51,903, DSS 3.6.1 Table 1) to 1.23 x (2024-25: $65,189) and 1.20 x (2025-26: $66,722), so every year
more families inside the 20 % taper also meet the notch. The kernel scanners found it blind (edges, METR).
Suggested fix: add cl 38A(1A) to Sch 4 cl 2, and withdraw the supplement on a taper instead of all at once.

### F5 FTB B primary-earner limit: $3,883.60 lost for one dollar, and splitting crosses it
kind: loophole-known (notch). Sch 1 cl 28B(1) ($100,000, indexed to $117,194 for 2024-25): a one-earner couple or
sole parent going from $117,194 to $117,195 pays $3,884.22 more (`notch_ftb_b_primary_limit`); $3,979.12 at
$120,008 in 2025-26. The limit is tested on the higher earner's ATI alone (Sch 3 cl 3), so moving investment income
to the other spouse crosses it: moving $5,000 of interest at $100,000 + $20,000 saves $5,483.60, more than the
amount moved (`split_crosses_ftb_b`; generic lever L1 found it blind).

### F6 Medicare levy surcharge: a notch by design (kernel `exempt_notch`)
kind: loophole-known. MLA s. 8B: 1 % of all taxable income once income for surcharge purposes exceeds the singles
tier 1 threshold ($97,000 in 2024-25, ATO table; PHI Act s. 22-35, indexed): +$970.33 for $1 (`notch_mls_single`;
the kernel theorem `Surcharge.exempt_notch` instantiated as `mls_notch`). Tiers 2 and 3 add notches of $282.83 and
$377.90; families with two children at $195,501 (+$1,955). The Medicare levy itself has a glide zone and no notch
(`levy_no_notch`, kernel `glide_no_notch`).

### F7 HELP repayments: 18 notches in 2024-25, none in 2025-26
kind: loophole-known. 2024-25: one rate on all repayment income, 1 % from $54,435 up to 10 % from $159,664 (ATO
table 2): +$544.68 at $54,435 (`cliff_help_2425`) and 18 notches up to $628.85. 2025-26 (HESA s. 154-10, $67,000;
marginal 15 % / 17 %, then 10 % of all from $179,286): no notch on the scan grid (`no_cliff_help_2526`); the step at
$179,286 is $0.15 (10 % x 179,286 = 17,928.60 against 8,700 + 17 % x 54,285 = 17,928.45). The reform removed every
notch.

### F8 PAYG Schedule 1 still uses the 2023-24 Medicare levy parameters in 2024-25 and 2025-26
kind: gov-error (stale table; classification: error of updating, small amounts). Schedule 1 of F2024L00664 (1 July
2024), F2025L00647 (1 July 2025) and F2025L01016 (24 September 2025) all say "last updated on 1 July 2024" and use a
$500/$625 weekly shade-in ($26,000 / $32,500) and a family threshold of $43,846 + $4,027 a child: the 2023-24 figures
of MLA ss. 3 and 8. The Act moved to $27,222 / $34,027 / $45,907 + $4,216 for 2024-25 (TLA (More Cost of Living
Relief) Act 2025, assented 27 March 2025) and $28,011 / $35,013 / $47,238 + $4,338 for 2025-26 (Act No. 58 of 2026,
assented 30 June 2026). The coefficient tables of the three instruments are identical (extracted text in `refs/`).
Over-collection of levy through withholding: up to $122 (single, at $32,500) and $244 (one-earner couple, 2
children) in 2024-25; $201 and $401 in 2025-26; refunded on assessment. The 2024-25 thresholds were law two months
before F2025L00647 was made (30 May 2025) and were not used. Draft note to the ATO (not filed): "Schedule 1 of
F2025L00647 / F2025L01016 uses Medicare levy parameters (scale 2 and 6 thresholds 500 / 625 and 843 / 1,053; family
threshold 43,846; additional child 4,027) that are the 2023-24 values of the Medicare Levy Act 1986 ss. 3 and 8;
the 2024-25 values ($27,222, $45,907, $4,216) were enacted on 27 March 2025."

### F9 Schedule 1 scale 2 leaves the low income tax offset to the return: up to $765 over-withheld
kind: gov-error (classification: convention; the schedule accepts approximation). For a single resident with wages
only, 52 x the weekly scale 2 amount is never below the year's liability (ITRA Sch 7 - LITO + levy) on $0-$4,000 a
week (`sched1_never_under`, 2024-25 and 2025-26), and exceeds it by up to $765.00 at $535 a week ($27,820 a year:
liability $899, withholding $1,664; `sched1_max_over_2025`), and by $843.90 at $585 a week in 2025-26. At $500 a
week the withholding ($1,144) is $104 under the liability without LITO ($1,248) and $596 over the liability with it
($548): the $700 offset is almost entirely left out (`sched1_lito_left_out`). Scale 2's zero band ends at $361 a
week ($18,772), not at $434 ($22,575) where tax net of LITO starts. Above $1,282 a week the excess is $20-$80 (the
"+99 cents" convention and rounding). The schedule never mentions LITO. All 240 published sample amounts (48
weekly rows x 5 scales) are reproduced exactly (`sched1_sample_all`), so this is the schedule, not the model.

### F10 ATO worked example arithmetic (HELP page)
kind: gov-error (trivial). ATO "Study and training loan repayment thresholds and rates", example 4: "$99,736 x 5.5% =
$5,485.52"; 5.5 % x 99,736 = $5,485.48 (`Checks.lean`). Example 3 rounds to the dollar ("$23,854"; exactly
$23,853.70) where examples 1, 2 and 4 show cents; typo "Branon's". Draft note (not filed): "Example 4: 99,736 x
5.5 % = 5,485.48, not 5,485.52."

### F11 The Family Assistance Act prints amounts that never apply
kind: statute-fault (transparency; classification: convention). The consolidated Act shows Sch 4 base amounts: higher
income free area $98,988 (cl 2), FTB B nil above $100,000 (cl 28B), income free areas $4,000 (cl 33) and $40,000
(cl 38N), supplement $600 (cl 38A(3)), child rate $4,292.40 (cl 7). The 2024-25 amounts ($115,997, $117,194,
$6,789, $65,189, $916.15, $5,788.90) are in no legislation, only in the DSS guide. The PHI Act likewise shows the MLS
tier 1 threshold as "$90,000 for the 2021-22 and 2022-23 financial year" (s. 22-35); 2024-25's $97,000 is on the
ATO site only. A reader of the law cannot find the law's numbers.

### F12 Consistency checks that passed (versioned law)
kind: statute-fault (none found). (a) Medicare levy: every phase-in limit is the threshold x 5/4 rounded down, in
2023-24, 2024-25, 2025-26 and for SAPTO (`phase_in_is_five_quarters`), and the separately written phase-in limit
adds nothing (`levy_kernel_eq`). (b) MLA s. 8D(3)(c) repeats the s. 3 threshold as a literal ($26,000 -> $27,222 ->
$28,011) and was amended by the same Act both times (compare_dates 2025-01-01..2026-06-30 and ..today). (c) LITO's
$66,667 ceiling (s. 61-110(1)(b)) is the zero of item 3 to the cent (`lito_ceiling_is_zero_crossing`): no notch.
(d) ITRA's "second resident personal tax rate" (s. 3; used in s. 15 and Sch 7 Pt II) points at "item 2 of the table
... applicable to the year of income", which survives the 2025 insertion of the 2026-27 and 2027-28 tables. (e) The
2024-25 and 2025-26 rate tables are identical (`au_2026_same`).

### F13 Medicare thresholds are legislated after the year has started
kind: statute-fault (process; classification: convention). The low-income thresholds for 2024-25 were enacted on 27
March 2025 (in force 28 March 2025, for the whole year) and those for 2025-26 on 30 June 2026, the last day of that
year (Global law change dates). Withholding cannot follow (F8).

### F14 Bunching income into alternate years pays families up to 12 % of AW
kind: loophole-new (lead; kernel timing scanner). FTB A/B are annual and tested on ATI, so a sole parent or one-earner
couple with two children averaging $128,453 gains $13,424 over two years by earning $191,701 then $65,204 instead of
$128,453 twice (`results/search/timing.md`): FTB A at the maximum and FTB B under the primary-earner limit in the low
year. Not searched for in the literature; a lead (employees have little control over timing).

### F15 Integrity rules that work: sacrifice and negative gearing do not buy family payments or HELP relief
kind: model-fix (positive finding). Reportable super contributions and net investment losses are added back to ATI
(FA Act Sch 3 cl 2), to income for surcharge purposes and to HELP repayment income (HESA s. 154-5(1)(b), (e)):
$3,000 of salary sacrifice at $82,000 saves only $510 (32 % - 15 %), not the $1,832 supplement
(`sacrifice_blocked_ftb`); a $5,000 rental loss at $100,000 without cover saves tax but not the surcharge tier. Only
deductions that are not added back (gifts, work expenses) move a family across a notch (generic lever L3: a $5,000
gift at $120,000 nets $1,684 by restoring FTB B).

### F16 Known techniques recreated (CATALOGUE.md)
kind: loophole-known. 24 catalogued, 15 recreated on the model (7 by the generic scanners without being told), 9
not modelled. Sizes (2024-25): $60,000 of interest held by a non-earning spouse instead of a $180,000 earner saves
$17,512; owner-manager dividends split between spouses instead of salary + SG saves $8,811 on $200,000 of profit;
negative gearing $20,000 at $150,000 saves $7,450 a year, and the 50 % discount saves $3,900 on a $20,000 gain;
salary sacrifice of $20,000 at $150,000 saves $4,450; franking credits refund $9,355 to a holder of $40,000 of
dividends with no other income.

### F17 Filing unit: marrying changes nothing (de facto partners are spouses)
kind: model-fix (positive check). ITAA 1997 s. 995-1 "spouse" includes a person who "lives with the individual on a
genuine domestic basis in a relationship as a couple"; the Medicare levy and surcharge use it (MLA s. 3(4), ITAA 1936
s. 6(1)) and family assistance's "member of a couple" covers de facto relationships (FA Act s. 3(1), Social Security
Act 1991 s. 4). `autax` reads `married || cohabiting` as a couple; the kernel unit scanner then finds no marriage
penalty or bonus anywhere on its grid (`results/search/SUMMARY.md`). The couple rule itself is large: two
cohabiting earners on $70,000 + $50,000 with two children get $2,514.80 of FTB; the same two as unrelated
housemates (children with the first) would get $16,331.50, which is why the law does not let a couple choose.

### W5S-1 personal-finance-planner (yintheair, wronglaw grid): flat Medicare levy, no LITO (W5 review pass 2, 2026-11-20)
- kind: software-error
- `au_open_personal_finance_planner_yintheair_grid`: the page charges 2 % of income with no low-income threshold or shade-in (Medicare Levy Act 1986 ss. 7-8) and gives no low income tax offset (ITAA 1997 s. 61-110): at 30,421 it charges 2,564 against the model's 1,496; exact above about $85,000.
- status: recorded (world/IMPROVE_W5.md pass 2, wronglaw table)
