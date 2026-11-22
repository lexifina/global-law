import TaxKernel.World

/-!
# Iraq (federal): Income Tax Law No. 113 of 1982 as amended (CPA Order 49 of 2004 and later), 2025

Authority modelled: the federal General Commission for Taxes (الهيئة العامة للضرائب, Baghdad); the Kurdistan Region
taxes salaries under its own rules (not modelled). Source: the GCT's consolidated text "قانون ضريبة الدخل رقم 113
لسنة 1982 وتعديلاته" on `tax.mof.gov.iq` (the live site refuses the build server and a second machine; archived official copy
`web.archive.org/web/20230926053900id_/https://tax.mof.gov.iq/قانون-ضريبة-الدخل-رقم-113-لسنة-1982-وتعديلاته/`,
sha256 in FINDINGS). Art. 13 مكررة (4) lets the minister propose changes of the allowances (art. 12) and the scale
(art. 13) in the annual budget law; the budget law for 2023-2025 could not be read, so access B.
* Art. 12 (1) (أ): "مبلغ مليونين وخمسمائة ألف دينار" (2,500,000) for the taxpayer (or an unmarried woman taxpayer, or
  when the wife's income is not added to the husband's) and "مبلغ مليوني دينار" (2,000,000) for the wife "اذا كانت
  الزوجة ربة بيت لا دخل لها"; (ب) 200,000 per child "بغض النظر عن عددهم"; (ج) 3,200,000 for a widow or divorcee and
  200,000 per child in her care; (5) a further 300,000 above age 63.
* Art. 13 (1) (أ): resident individual, after the art. 12 allowances, 3 % up to 250,000; 5 % to 500,000; 10 % to
  1,000,000; 15 % above.
* The wife is a taxpayer in her own right (the page's paragraph on "تعتبر الزوجة مكلفة بذاتها").
Not modelled: employee social security (Law 18/2023 not read), the many salary allowances exempted by other laws,
investment income, Kurdistan Region. Unit: individual.
-/

namespace IqTax
open TaxKernel

/-- Art. 13 (1) (أ) (bp). -/
def sched : Schedule := Schedule.ofList [(0, 300), (250000, 500), (500000, 1000), (1000000, 1500)]

def taxOn (ti : Int) : Int := sched.tax Rule.unitDown (pos ti)

def ageExtra (a : Adult) : Int := if a.age > 63 then 300000 else 0

def out (c : Canon) : Out :=
  let kids := c.childrenUnder 18
  let a1 := c.adult1
  let i1 := a1.wages + a1.selfEmployment + a1.pension
  let (al1, al2, i2) := match c.adult2? with
    | some a2 =>
      let i2 := a2.wages + a2.selfEmployment + a2.pension
      -- a housewife without income: 2,000,000 to the husband; an earning wife: her own 2,500,000
      if i2 > 0 then (2500000 + 200000 * kids + ageExtra a1, 2500000 + ageExtra a2, i2)
      else (2500000 + 2000000 + 200000 * kids + ageExtra a1, 0, 0)
    | none =>
      -- single parent: the widow/divorcee allowance (art. 12 (1) (ج)) when children are in her care
      ((if kids > 0 then 3200000 else 2500000) + 200000 * kids + ageExtra a1, 0, 0)
  let sep := taxOn (i1 - al1) + taxOn (i2 - al2)
  -- art. 12 (1) (أ): "أو في حالة اضافة دخلها الى دخله": the wife's income may be added to the husband's, keeping the
  -- 2,000,000 wife allowance; the cheaper of the two is taken (election)
  let joint := if c.married && i2 > 0 then taxOn (i1 + i2 - (2500000 + 2000000 + 200000 * kids + ageExtra a1)) else sep
  let t1 := min sep joint
  let t2 := 0
  Out.make c "IQ" "IQD" (t1 + t2)
    (detail := [Out.d "taxableIncome" (pos (i1 - al1) + pos (i2 - al2)), Out.d "allowances" (al1 + al2)])
    (unsupported := ["employee social security contributions not modelled",
      "budget-law changes to arts. 12-13 for 2023-2025 not verified (art. 13 مكررة (4))",
      "exempt salary allowances, investment and rental income not modelled; Kurdistan Region not modelled",
      "art. 12 (1) (ج) names the widow or divorcee: given here to any single parent with children (reading)"])

def country : Country :=
  { code := "IQ", name := "Iraq (federal, Income Tax Law 113/1982)", currency := "IQD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard taxOn 250000 = 7500 ∧ taxOn 500000 = 20000 ∧ taxOn 1000000 = 70000 ∧ taxOn 2000000 = 220000

end IqTax
