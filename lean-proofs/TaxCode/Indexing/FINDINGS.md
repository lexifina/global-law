# Check the IRS's own arithmetic — findings (2026-11-16)

Summary also in the header of `Findings.lean`; item table in `ITEMS.tsv`. `lake build TaxCode.Indexing.All` builds clean (~1 min),
axioms: propext, Classical.choice, Quot.sound only.

## Counts

| Group | Checked | Match | Rounding only | Match only with 1-year lag | Mismatch |
|---|---|---|---|---|---|
| Rev. Proc. 2024-40 (TY2025) | 181 | 142 | 4 | 27 | 8 |
| Rev. Proc. 2025-32 (TY2026) | 194 | 123 | 4 | 57 | 10 |
| Rev. Proc. 2023-34 (subset) | 73 | 64 | 0 | 7 | 2 |
| Rev. Proc. 2022-38 (subset) | 73 | 63 | 0 | 7 | 3 |
| Structural checks | 46 | 43 | – | – | 3 |

Social Security base and COLAs: 4/4 match. Retirement and HSA limits: 50/50 match. Index vintage matters: with today's
revised C-CPI-U, 231 items would come out differently; every published match uses the first-published values the
statute requires.

## Findings, most certain first

- **F1 (high) — the IRS rounds the adjusted amount where the statute rounds the increase.** Proved: the published figures
  cannot come out of the statutory rounding for any index values.
  - Head-of-household standard deduction 2026: published $24,150, statute $24,175.
  - §6334(d) wage-levy exemption and §642(b) disability-trust exemption 2023–2026: published $4,700 / $5,000 / $5,100 /
    $5,300; statute $4,750 / $5,050 / $5,150 / $5,250.
  - §7702B(d) long-term-care per diem: published $420 / $430; statute $425 / $435.
  - §213(d)(10) $375 premium tier: published $900 / $930; statute $905 / $935.
- **F2 (medium) — penalty amounts lag the statute's index year by one year.** All 98 published penalty figures match only
  with the prior year's index. Read literally the statute gives higher amounts, e.g. 2026 §6721(a)(1) cap $4,191,500, not
  $4,098,500.
- **F3 (medium-high)** — 2026 first bracket for estates and trusts published $3,300; amended §1(j)(3)(B)(i) gives $3,250.
- **F4** — long-term-care index: the statute's literal formula gives much lower limits than published; all 12 published
  figures are reproduced by an index the IRS does not state.
- **F5 (medium)** — MFS 15% capital-gains breakpoint is $25 below half the joint amount in 2023, 2024 and 2025.
- **F6 (medium-high)** — 2023 qualifying-relative income limit published $4,700; the IRS's own method for 2024–2026 gives
  $4,800 ($4,700 is the §6334/§642 figure).
- **F7 — text errors:** Rev. Proc. 2023-34 "filed in 2024" (should be 2025); Rev. Proc. 2025-32 "August 1, 2026" (should be
  2027); Rev. Proc. 2023-34 "excess over $191,150" (should be $191,950); a §59(j) limit still published though switched off
  since 2017.
- **F9** — BLS never published the October 2025 index, so the 2026 C-CPI-U average needed for every 2027 adjustment cannot
  be formed.
- **F10 (low)** — §36B 2026 table not checkable: HHS's own growth figure gives a top rate of 9.56%, not the published
  9.96%; the IRS does not publish its inputs.

Publication check: F1 (head of household) and F6 searched once each, nothing published found; others not searched.

## Pub. 15-T (2025, 2026)

- Standard percentage-method tables = exactly the §1(j) tax on (wages − standard deduction), proved for every wage.
- 2025 tables use the pre-2025-Act standard deduction: over-withholding at most $277.50 single / $555 joint. Unreported
  tips, overtime or senior deductions cause over-withholding of 10–37% of the deduction.
- Step 2 checkbox: two equal jobs withhold exactly the joint tax; unequal jobs never under-withhold.
- Each wage-bracket entry = percentage-method amount at the row midpoint, rounded to the dollar; within $2 weekly,
  $4.50 biweekly, $5 semimonthly, $9 monthly of the percentage method.

## Gaps

Item 6 covers about 73 items per older Rev. Proc., not all. Daily wage-bracket tables not examined. Regulatory amounts
(§148, Rev. Procs 90-12, 98-19) left out. Web: 13 of 20 used; SSA pages refused, Federal Register notices used instead.
