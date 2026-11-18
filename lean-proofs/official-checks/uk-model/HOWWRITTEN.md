# How the UK writes its income tax (evidence from formalising 2025-26)

**An algorithm in the Act, the numbers elsewhere.** ITA 2007 (a Tax Law Rewrite consolidation) states the liability
as a procedure: s. 23 "To find the liability of a person ... take the following steps. Step 1 ... Step 7". Income
tax is an annual tax: the Act has no rates of its own ("the rates determined as such by Parliament for the tax year",
s. 6(2)), and each Finance Act re-imposes it ("Income tax is charged for the tax year 2025-26", FA 2025 s. 1) and sets
the rates (ss. 2–3). Thresholds are written into the Act (s. 10(5) £37,700; s. 35(1) £12,570), indexed to CPI by
default (s. 21, s. 57) and frozen by later Acts (FA 2021 s. 5: to 2027-28); the higher rate limit is a formula
(s. 10(5A): 2 × allowance + £100,000, which makes the additional rate begin exactly where the taper ends — theorem
`hrl_is_taper_end`). The 45 numbers the model needs (rest of the UK) live in 15 instruments: ITA 2007, ITEPA 2003, TCGA 1992,
SSCBA 1992, FA 2004, FA 2021, FA 2022, FA 2023, F(No. 2)A 2024, FA 2025, and the statutory instruments 2001/1004
(NI thresholds), 2006/965 and 2025/292 (child benefit), 2025/53 (blind person's and married couple's allowances),
2025/288 (Class 2); Scotland adds the Scottish rate resolution (10 more).

**How often.** Rates every year (FA 2025 ss. 2–3); thresholds frozen since 2021-22, the starting rate limit frozen
year by year (FA 2025 s. 4); the savings allowance unchanged since 2016; dividend rates changed in 2016, 2022 and 2026;
CGT rates changed mid-year (30 October 2024, FA 2025 s. 7); the employee NI rate three times in 2023-24 (12 % → 10 % on
6 January 2024 → 8 % on 6 April 2024). legislation.gov.uk's point-in-time text lagged once: child benefit on 6 April
2025 still shows 2024-25 rates (the new ones start on the first Monday, 7 April).

**Official code or specification.** None for the liability. legislation.gov.uk publishes the text as XML with an open
API (used for every provision here), not logic. HMRC publishes payroll specifications and test data for withholding:
PAYE tax table routines (.odt) and 2025-26 test data (.xlsx) for PAYE and NICs. All 448 NIC rows are reproduced in
Lean (`hmrc_ni_test_data`); the PAYE routine, written from the specification, gives 159 of 168 PAYE payments exactly
and all within HMRC's own £0.01 tolerance (`hmrc_paye_test_data`). HMRC's Self Assessment calculation is not
published; the only executable model is the unofficial PolicyEngine-UK, which agrees with Lean on 99.97 % of 15,500
households once five named conventions of its own are adopted, and on 85 % under the statute.

**Devolution.** The Scottish Parliament sets rates and bands for the non-savings income of Scottish taxpayers
(Scotland Act 1998 s. 80C; ITA 2007 s. 11A), but savings and dividends stay on UK rates and UK bands "as if" not a
Scottish taxpayer (s. 11D(6), s. 13(5)), and capital gains tax assumes the same (TCGA s. 1J(6)): one person's income is
charged under two schedules at once. The UK-wide NI threshold no longer lines up with the Scottish higher rate, so
Scots pay 50 % (42 % + 8 %) between £43,663 and £50,270, and 69.5 % in the taper band (theorem
`scot_vs_ruk_marginal`).

**What was hard or ambiguous.** (1) s. 25(2) delegates an optimisation: reliefs and allowances go "in the way which
will result in the greatest reduction" — Lean searches every break point (HMRC's own example sets the allowance
against dividends). (2) Positional stacking (s. 16) with 0 % bands that still use up the band (ss. 12, 12A, 13A).
(3) Conditions written as lists of rate names that drifted when new rates were created: the savings allowance's
"higher-rate income" omits the savings higher rate (s. 12B(8), F1); pension band extension needs tax "at the higher
rate" (FA 2004 s. 192(4), F2) — on its words a cliff and non-monotone. (4) Elections with tests "not liable to tax at a
rate other than [list]" (s. 55B(2)(b)), with a dividend proviso but none for savings. (5) Rounding: only s. 35(3),
s. 55B(5) and ITEPA s. 681C(3) round; NI rounding lives in guidance, and HMRC's guide and test data disagree (F8).
(6) The household: no joint return, so who holds income and who elects are modelling choices.

**What I would change in the drafting.** Define the rate groups once ("a higher rate": higher, savings higher, default
higher, dividend upper) and refer to the group — F1 and F2(a) would not exist. State the rounding of the liability.
Make the pension band extension unconditional, as HMRC's manual already describes it. Publish an executable reference
calculation with test vectors for Self Assessment, as HMRC already does for PAYE and NICs.

| Count | |
|---|---|
| Provisions modelled | about 80 (ITA 2007: 42 sections; ITEPA 2003: 4; FA 2004: 7; TCGA 1992: 4; SSCBA 1992: 6; S.I. 2001/1004: 5 regulations; S.I. 2006/965: 1; Finance Acts: 9; the Scottish rate resolution), plus HMRC's PAYE tax-table specification |
| Lines of Lean | 2,320 written + 603 generated (HMRC NI and PAYE test data) |
| Numeric parameters | 45 for the rest of the UK + 10 for Scotland (plus one formula, the higher rate limit) |
| Theorems | 94: 50 for all inputs, 44 on named figures (incl. HMRC's 448 NIC rows and 168 PAYE payments); + 31 `#guard` checks of official examples |
