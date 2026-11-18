# GOV.UK Child Benefit tax calculator vs ITEPA 2003 s. 681C

Checked: `lib/smart_answer/calculators/child_benefit_tax_calculator.rb` in
[alphagov/smart-answers](https://github.com/alphagov/smart-answers) at `be649a544cf720a708c29e0bbfc07510e5af0796`,
run unmodified in Ruby 4.0.8 (`scripts/hicbc_run.rb`), against
[ITEPA 2003 s. 681C](https://www.legislation.gov.uk/ukpga/2003/1/section/681C) and the Lean UK model (`../uk-model`).

Cases: whole-pound adjusted net incomes from £59,000 to £81,000 with one to four children, 2025-26 (88,004 cases).

Two differences, both in the rounding of s. 681C(3):

1. **The percentage is 1 % too low at exactly £65,800, £71,400 and £71,600**, because `5800.0 / 20000 * 100` is
   28.999999999999996 in binary floating point and `.floor` gives 28. With two children at £65,800 the calculator
   shows £630; the statute gives £652. `lean/01-hicbc-float-percentage.lean`.
2. **The total child benefit is not rounded down to whole pounds before the percentage is applied**, so the estimate
   is £1 higher in 23,197 of the 88,004 cases and never lower. `lean/02-hicbc-total-rounding.lean`.

`results/hicbc_summary.txt` has the counts, `results/hicbc_rows.jsonl.gz` every case.
