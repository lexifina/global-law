import TaxKernel.World

/-!
# Jordan: Income Tax Law No. 34 of 2014 as amended (Law No. 38 of 2018), tax year 2025

Statute text: the Income and Sales Tax Department's consolidated text of the Income Tax Law
(`https://istd.gov.jo/AR/List/قانون_ضريبة_الدخل`, nine pages served by postback, fetched 2026-11-20 into
`jo/law/itl_p1.html` … `itl_p6.html`, sha256 of page 1 087138529bea…, page 2 eb3dbb380f23…). The text names its years
("لسنة (2020) وما يليها"), so its amounts govern 2025.
* Art. 9 (أ) (1): "تسعة آلاف دينار لسنة (2020) وما يليها" personal exemption 9,000 for 2020 onwards;
  (2): 9,000 "عن المعالين مهما كان عددهم" for dependants whatever their number; (3): 1,000 each for the taxpayer, the
  spouse and each child (max 3,000) against medical, education, rent and housing-loan expenses (invoices: not in the
  canonical household, so not claimed here; flagged); (ب) (1): spouses together at most 23,000; (ج) either spouse may
  use the other's unused difference, the total never above 23,000.
* Art. 2: "المعال: زوج المكلف أو أولاده أو أصوله أو أقاربه حتى الدرجة الثانية الذين يتولى المكلف الإنفاق عليهم".
* Art. 11 (أ): 5 % on the first 5,000, 10 % on the next 5,000, 15 % on the next 5,000, 20 % on the next 5,000,
  "(25%) … مما تلاها ولغاية مليون دينار", "(30%) … من الدخل الخاضع للضريبة للمكلف الذي يزيد على (1000000)"
  (read here as 30 % on the part above 1,000,000; see FINDINGS F2). The consolidated text numbers the items
  1, 2, 4, 5, 6, 7 (no item 3: FINDINGS F3).
* Art. 11 (هـ): taxable income and tax "يخفض المبلغ الناتج لأقرب دينار" (rounded down to the dinar).
* Art. 11 (و) (1) (و): national contribution "1% من الدخل الخاضع للضريبة مما يزيد عن (200000) … للشخص الطبيعي".
* Art. 4 (أ) (5) capital gains exempt (assets outside depreciation), (8) dividends of resident companies exempt,
  (14) "أول (2500) دينار من اجمالي الراتب التقاعدي الشهري" exempt.
* Art. 12 (أ) (2): bank interest 5 % withheld, final ("ضريبة قطعية") for a natural person; (ج) such income is not part
  of gross income.
Social security: Social Security Law No. 1 of 2014 as amended to 16 April 2023 (SSC copy
`ssc.gov.jo/wp-content/uploads/2024/01/قانون-الضمان-الاجتماعي-رقم-١-لسنة-٢٠١٤-…pdf`, sha256 7bd6415d26a1…, scanned;
read as page images): art. 59 (أ) (2) old age, disability and death "(6,5%) من أجور المؤمن عليهم" deducted by the
employer; art. 48 (ب) unemployment "(واحد بالمائة)"; the ceiling "الحد الأعلى للأجر الذي تحتسب الاشتراكات على
أساسه ثلاثة آلاف دينار" (art. 20 (أ); contributions are monthly, art. 59), indexed to inflation each January (art. 20 (ب)) (the indexed 2025 amount is not in the law:
the statutory 3,000 was used and flagged until W5). W5 pattern A (2026-11-20): the SSC's press release on the 2026
ceiling (ssc.gov.jo, fetched 2026-11-20, `jo/law/w5/`): "الحد الأعلى للأجر الذي تُحتسب اشتراكات الضمان على أساسه
للعام الحالي 2026 أصبح (3733) ديناراً، في حين كان العام الماضي (3668) ديناراً": the art. 20 (ب) indexed ceiling for 2025
is 3,668 JOD a month (official secondary: the SSC's own statement of the indexation it applies). Input
`"w5Contrib": false` restores the statutory 3,000.
Unit: individual (each spouse a taxpayer; art. 9 (ب) caps the couple's exemptions).
-/

namespace JoTax
open TaxKernel

/-- Art. 11 (أ): the natural-person bands (bp). -/
def sched : Schedule :=
  Schedule.ofList [(0, 500), (5000, 1000), (10000, 1500), (15000, 2000), (20000, 2500), (1000000, 3000)]

def personal : Int := 9000      -- art. 9 (أ) (1)
def dependants : Int := 9000    -- art. 9 (أ) (2)
def coupleCap : Int := 23000    -- art. 9 (ب) (1), (ج)
def pensionMonthlyExempt : Int := 2500   -- art. 4 (أ) (14)

/-- Tax on taxable income (art. 11 (أ), (هـ): whole dinars, rounded down). -/
def taxOn (ti : Int) : Int := sched.tax Rule.unitDown (pos ti)

/-- National contribution, art. 11 (و) (1) (و): 1 % of taxable income above 200,000. -/
def nationalContribution (ti : Int) : Int := (pos (ti - 200000)) / 100

/-- Employee social security (arts. 59 (أ) (2), 48 (ب)): 7.5 % of wages up to 12 × 3,000. -/
def ssc : Contribution := Contribution.flatCapped "SSC old age + unemployment" 750 36000
/-- The same with the 2025 indexed ceiling 3,668 a month (SSC statement, art. 20 (ب)). -/
def ssc2025 : Contribution := Contribution.flatCapped "SSC old age + unemployment" 750 (12 * 3668)

#guard ssc2025.amount 100000 = 3301 ∧ ssc.amount 100000 = 2700   -- 7.5 % x 44,016 = 3,301.20

/-- Net income of one adult before exemptions: wages, business income, pension above the art. 4 exemption, own share
of rent (art. 3 (أ) (6)); dividends and capital gains exempt (art. 4 (أ) (5), (8)); interest taxed apart (art. 12). -/
def grossOf (a : Adult) (rent : Int) : Int :=
  a.wages + a.selfEmployment + pos (a.pension - 12 * pensionMonthlyExempt) + rent

/-- Exemptions (art. 9): (exemption of adult 1, exemption of adult 2). The dependants' 9,000 goes to the first
adult when a spouse without income or a child is maintained; for two earners with children it goes to the higher
income; the couple's total never exceeds 23,000 (art. 9 (ب), (ج)). -/
def exemptions (c : Canon) (g1 g2 : Int) : Int × Int :=
  match c.adult2? with
  | none => (personal + (if c.nChildren > 0 then dependants else 0), 0)
  | some _ =>
    let both := g1 > 0 && g2 > 0
    if !both then
      -- one earner: own 9,000 + dependants 9,000 (the spouse is a dependant, art. 2)
      let e := personal + dependants
      if g1 ≥ g2 then (e, 0) else (0, e)
    else
      let dep := if c.nChildren > 0 then dependants else 0
      let total := min coupleCap (2 * personal + dep)
      let extra := total - 2 * personal
      if g1 ≥ g2 then (personal + extra, personal) else (personal, personal + extra)

def out (c : Canon) : Out :=
  let rent := c.rentalIncome
  let g1 := grossOf c.adult1 (half1 rent)
  let g2 := match c.adult2? with | some a => grossOf a (half2 rent) | none => 0
  let (e1, e2) := exemptions c g1 g2
  -- art. 9 (ج): an unused exemption of one spouse passes to the other (total within 23,000)
  let u1 := pos (e1 - g1)
  let u2 := pos (e2 - g2)
  let ti1 := pos (g1 - e1 - (if c.isCouple then u2 else 0))
  let ti2 := if c.isCouple then pos (g2 - e2 - u1) else 0
  let tax := taxOn ti1 + taxOn ti2
  let nc := nationalContribution ti1 + nationalContribution ti2
  let intTax := pos c.interest * 5 / 100
  let w5 := (c.bool? "w5Contrib").getD true
  let ss := sumInts (c.adults.map fun a => (if w5 then ssc2025 else ssc).amount a.wages)
  Out.make c "JO" "JOD" (tax + intTax) (surtaxes := [("nationalContribution", nc)]) (employeeSocial := ss)
    (detail := [Out.d "taxableIncome" (ti1 + ti2), Out.d "taxOnTaxable" tax, Out.d "interestFinalWHT" intTax,
      Out.d "exemptions" (e1 + e2)])
    (unsupported := ["art. 9 (أ) (3) expense exemptions (up to 1,000 + 1,000 + 3,000 against invoices) not claimed",
      "SSC wage ceiling: 2025 indexed 3,668 JOD/month (SSC statement); members insured before 15/10/2009 have their own indexed ceiling (art. 20 (ج)): not modelled",
      "rental income taken gross (expenses not modelled); dividends of excepted sectors (banks, telecoms …) not separated",
      "self-employed social security (voluntary/optional schemes) not modelled"])

def country : Country :=
  { code := "JO", name := "Jordan (Income Tax Law 34/2014 as amended)", currency := "JOD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Art. 11 (أ) checked on its own band ends: 5,000 → 250; 10,000 → 750; 15,000 → 1,500; 20,000 → 2,500;
   1,000,000 → 2,500 + 25 % × 980,000 = 247,500. -/
#guard taxOn 5000 = 250 ∧ taxOn 10000 = 750 ∧ taxOn 15000 = 1500 ∧ taxOn 20000 = 2500
#guard taxOn 1000000 = 247500 ∧ taxOn 1000100 = 247530
#guard nationalContribution 200000 = 0 ∧ nationalContribution 300000 = 1000

end JoTax
