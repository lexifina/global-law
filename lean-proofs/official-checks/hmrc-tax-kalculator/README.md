# HMRC tax-kalculator vs the statute and HMRC's PAYE routines

Checked: [hmrc/tax-kalculator](https://github.com/hmrc/tax-kalculator) tag 2.16.1
(`26190cf52c4e93031486d228c15f057137c35e08`), the engine behind GOV.UK's take-home pay estimator. Upstream's Gradle
build needs a private package registry, so `kalc-build/` is a minimal JVM-only build of the same sources (copied
unchanged from the tag) with a driver, `kalc-build/src/jvmMain`, that calls the public `Calculator(...).run()`.
Upstream's own 810 tests pass in it.

Compared with the Lean UK model (`../uk-model`) on 20,490 statute cases, and with a Lean copy of HMRC's PAYE tax-table
routine (`paye/`, which reproduces HMRC's 2025-26 PAYE test data to within 1p) on 1,755 cases over 27 tax codes.

Findings:

1. **T-suffix and K-prefix codes do not get the £9 that L codes get**: for 1257T the result's `taxFree` is £12,561
   and the tax is higher than for 1257L, though HMRC's PAYE specification says the suffix plays no part.
   `lean/03-kalculator-t-and-k-codes.lean`.
2. **The £100,000 taper is not applied to the default tax code of a year whose default is not the current one**
   (today only 2020-21). `lean/04-kalculator-default-code-year.lean`.

Every other difference is a documented convention; see `../uk-report.md`. `results/kalc_summary.txt` has the counts,
`results/kalc_rows.jsonl.gz` every case.
