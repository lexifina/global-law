import LegalProofs.USTax.TaxCourt.Basic
import LegalProofs.USTax.TaxCourt.Params
import LegalProofs.USTax.TaxCourt.Schedule
import LegalProofs.USTax.TaxCourt.Dependents
import LegalProofs.USTax.TaxCourt.FilingStatus
import LegalProofs.USTax.TaxCourt.EIC
import LegalProofs.USTax.TaxCourt.CTC
import LegalProofs.USTax.TaxCourt.Income
import LegalProofs.USTax.TaxCourt.EarlyDistribution
import LegalProofs.USTax.TaxCourt.Penalties
import LegalProofs.USTax.TaxCourt.Return
import LegalProofs.USTax.TaxCourt.Case
import LegalProofs.USTax.TaxCourt.Tests
import LegalProofs.USTax.TaxCourt.Theorems
import LegalProofs.USTax.TaxCourt.Axioms

/-!
# Tax Court library: individual income tax, tax years 2012–2024

The rules U.S. Tax Court cases most often turn on, written from the statute as it stood for each year, so that a case
agent can encode a court's findings of fact and recompute its holdings. Namespace `Legal.USTax.TaxCourt`. No `sorry`,
no `native_decide`; axioms only `propext`, `Classical.choice`, `Quot.sound` (`TaxCourt/Axioms.lean`).

    lake build LegalProofs.USTax.TaxCourt
    lake env lean --run LegalProofs/USTax/TaxCourt/Run.lean cases.json outcomes.json
    lake env lean --run tools/taxcourt/CheckTables.lean eic_tables.json tax_tables.json

## Modules

* `Basic` — helpers; dates; "month or fraction thereof".
* `Params` — every year figure with its source; `rateSched_ok`, `eic_max_consistent`, `eic_completed_consistent`.
* `Schedule` — §1 schedules (pre-TCJA and §1(j)), the Tax Table rule, the qualified dividends / capital gain worksheet.
* `Dependents` — §152(c), (d), (b), (e); the §152(c)(4) tie-breaker.
* `FilingStatus` — §7703(a)–(b), §2(a) surviving spouse, §2(b) head of household.
* `EIC` — §32 by year, incl. 2021 §32(n); the EIC Table rule.
* `CTC` — §24 for 2016–17, the TCJA years, and 2021 (§24(i), §24(j) advance-payment reconciliation).
* `Income` — SE tax by year (incl. the 2012 payroll-tax holiday), §86 (the 2025 model's core), the 2020 §85(c) unemployment exclusion.
* `EarlyDistribution` — §72(t) with its exceptions by plan type and year.
* `Penalties` — §6662(a), (b)(1)–(2), (d), §6664(c), §6751(b); §6651(a)(1)–(2), (c)(1), (f).
* `Return` — a simple Form 1040 for any year; `deficiencyOf` (§6211, refundable credits as negative tax).
* `Case` — `Case`, `decideCase`, `Outcome`, JSON reading with defaults; `sfrTax` (§6651(g)). `Run` — the batch runner (not imported here).
* `Tests`, `Theorems`, `Axioms`.

## Findings

1. **The EIC Table rule changed in 2024.** The 2016–2023 Pub. 596 tables phase the credit out from the unrounded
   maximum (credit % × earned income amount: 45% × $13,930 = $6,268.50 in 2016); the 2024 table (and 2025, per the
   2025 model) from the rounded maximum. Example: 2016, three children, $27,350–27,400 prints $4,334; the rounded
   maximum gives $4,335. With that one switch (`Params.eicUnroundedMax`) every correctly extracted cell of the nine
   tables agrees.
2. **2021 childless EIC: the joint threshold is $17,560, not $17,550.** ARPA's §32(n) phase-out amount is $11,610; the
   joint increase is the indexed §32(b)(2)(B) amount, $5,950 (Rev. Proc. 2020-45: $25,470 − $19,520). The printed
   completed phase-out ($27,380 = $17,560 + $9,820) and the 2021 table (the full $1,502 on the joint $17,550–17,600
   line) confirm it. Rev. Proc. 2020-45's pre-ARPA childless gap ($14,820 − $8,880 = $5,940) is easy to carry over.
3. **§6651(a) minimum addition: two revenue procedures were overtaken by statute.** Rev. Proc. 2015-53 §3.43 gives $135
   for 2016, but Pub. L. 114-125 §921 had set $205 for returns due after 2015 (Rev. Proc. 2016-55 §2). Rev. Proc. 2018-57
   ($215) and Rev. Proc. 2019-44 ($330, Taxpayer First Act) were overtaken by Pub. L. 116-94 div. O §402 ($435 for
   returns due after 2019). Rev. Proc. 2023-34 §3.53 says "filed in 2024" for its $510; it means 2025. By tax year:
   $205, $210, $215, $435, $435, $435, $450, $485, $510.
4. **Capital-gain thresholds**: 2018's are statutory (§1(j)(5)(B)), not in Rev. Proc. 2018-18; before 2018 they are
   the tops of the 15% and 35% brackets. (Tax-Calculator's 2023 separate-return 35% top of $578,125 is wrong; the
   Rev. Proc. prints $346,875.)
5. **The printed figures are internally consistent**: all 216 printed bases are the exact tax at the top of the row
   before (`rateSched_ok`); every printed EIC maximum is credit % × earned income amount rounded, and every completed
   phase-out is within $3 of threshold + maximum ÷ phase-out % (`eic_*_consistent`).
6. **Reading choices.**
   * §6662 compares "tax" net of refundable credits (§6211(b)(4)), so an over-claimed EIC can be a substantial
     understatement.
   * §6651(c)(1) is applied month by month and rounded once; the minimum is applied after the (c)(1) reduction.
   * The §24(d) refundable part follows the statute where Schedule 8812 differs (qualifying children and other
     dependents near the phase-out with little tax; the 2025 model's `form_exceeds_statute`).
   * Ties §152(c)(4) leaves open (equal days and equal AGI) go to the first claimant listed.
   * §152(e) releases count for §§151, 24 and §152(d) but not §2(b) or §32.

7. **2012–2015** (Rev. Procs. 2011-52, 2013-15, 2013-35, 2014-61). 2012 has six rates (top 35%, `rates2012`), no
   20% capital-gain rate, no §151(d)(3) phase-out, a 7.5% medical floor, and the payroll-tax holiday: SE OASDI 10.4%
   (employee 4.2%) with the §164(f) deduction replaced by 59.6% of the 10.4% tax plus one-half of the 2.9% tax
   (TRUIRJCA §601(b)(2); Schedule SE (2012) line 13 — the short form's "57.51%, or 50% plus $1,100" approximates it).
   2013–2015: ATRA's 39.6% bracket, 20% capital-gain rate and §151(d)(3) thresholds; 10% medical floor, 7.5% if
   either spouse is 65 (§213(f), through 2016). §6651(a) minimum by tax year: $135, $135, $135, $205 (the 2015 return
   was due after 2015, so Pub. L. 114-125's $205 applies). §68 (2013–2017) stays an input (itemized deductions as
   allowed); AOTC/LLC are inputs (`otherNonrefundableCredits`, `otherRefundableCredits`).
8. **§6651(g) substitute for return** (`Case.sfrTax`): the additions use the SFR's tax as the tax shown, the deficiency
   the tax on the return actually filed (0 for a non-filer). T.C. Memo. 2024-67 then agrees exactly ($4,016 and
   $3,659); without it (a)(1) loses the (c)(1) offset ($4,463) and (a)(2) is 0.

## Table checks (`tools/taxcourt/CheckTables.lean`, Nov 2026)

Every printed row of the nine EIC Tables and nine Tax Tables, extracted with `pdftotext -layout` from the IRS PDFs by
`tools/taxcourt/extract_tables.py` (the JSON is not committed). Rows agreeing exactly — EIC: 2016 1,044/1,060;
2017 1,055/1,067; 2018 1,066/1,081; 2019 1,090/1,105; 2020 1,106/1,122; 2021 1,120/1,134; 2022 1,161/1,168;
2023 1,246/1,253; 2024 1,316/1,323. Tax Table: 2,040–2,042 of 2,057 each year (2020: 1,988 of 2,051). Every other
row was inspected: some of its cells come from a neighbouring line or block of the multi-column page (e.g. 2022 EIC
"$42,900" shows $99 for one child, the model's value for $42,850), or it sits next to the sample-table text. None is
a model error. 2012–2015 (EIC Tables extracted with `pdftotext -raw`, Tax Tables from i1040tt): EIC 2012 999/999,
2013 1,024/1,024, 2014 1,041/1,041, 2015 1,060/1,060; Tax Table 2,012 of 2,036 / 2,038, 2,043 and 2,042 of 2,057, the
rest layout artefacts (an HoH cell from the next block). The 2012–2015 EIC Tables also phase out from the unrounded
maximum.

## Not modelled

AMT, kiddie tax, NIIT, additional Medicare tax, §5000A (pass them in `otherTaxes`); foreign income; the Schedule D
worksheet (28% and §1250 gain); §68 and §199A (pass the amounts); other credits (pass them in); the 2020–2021 Recovery
Rebate Credit (`otherRefundableCredits`); §6651(a)(3), (d), (h); §6654; §6663; §6662(b)(3)–(8); §32(k) beyond a flag;
possessions; community-property allocation.
-/
