import TaxKernel.World

/-!
# Egypt: tax on the income of natural persons (Income Tax Law 91/2005), 2025

Statute: Law No. 7 of 2024 amending arts. 8 and 13 (1) of the Income Tax Law 91/2005 (Official Gazette No. 7 bis (a),
21 February 2024), the Egyptian Tax Authority's copy `eta.gov.eg/sites/default/files/2024-03/law_no.7-2024.pdf`
(sha256 2aaec2ec…; the served file has an HTML page appended after `%%EOF`, stripped before reading). Article 2: in
force for salaries "من أول الشهر التالي لتاريخ نشره" (1 March 2024), so all of 2025.
* Art. 8: a table of rates whose bands depend on the size of the whole net income (columns): up to 600,000: 0 % to
  40,000, 10 % to 55,000, 15 % to 70,000, 20 % to 200,000, 22.5 % to 400,000, 25 % above; above 600,000 to 700,000 the
  first band is "من 1 جنيه إلى 55,000" at 10 %; above 700,000 to 800,000 "من 1 جنيه إلى 70,000" at 15 %; above 800,000
  to 900,000 "من 1 جنيه إلى 200,000" at 20 %; above 900,000 to 1,200,000 "من 1 جنيه إلى 400,000" at 22.5 %; above
  1,200,000: 25 % "من 1 جنيه إلى 1,200,000" and 27.5 % "ما زاد على 1,200,000". "ويتم تقريب مجموع صافي الدخل السنوى عند
  حساب الضريبة لأقرب عشرة جنيهات أقل" (net income rounded down to 10 pounds).
* Art. 13 (1): "مبلغ 20000 جنيه إعفاء شخصيا سنويا للممول" (20,000 personal exemption).
Not read (flagged): rental income rules, dividends and interest. Unit: individual.
W5 pattern A (2026-11-20), social insurance (`eg/law/w5/`):
* Social Insurance and Pensions Law No. 148 of 2019 (NOSI's copy "كتاب القانون الجديد", nosi.gov.eg library): art. 19
  (1) (b) old-age, disability and death "الحصة التي يلتزم بها المؤمن عليه بواقع (9٪) من أجره شهريًا"; art. 36 (1) the
  end-of-service reward scheme "حصة يلتزم بها المؤمن عليه بواقع (1٪) من أجر الاشتراك شهريًا" (unemployment, art. 86,
  and injury are employer-only): employee 10 % of the monthly contribution wage. Art. 1 (definition of the contribution
  wage): the executive regulation sets "الحد الأدنى والأقصى لأجر الاشتراك", raised yearly; for 2025 NOSI's news item of
  30/11/2025 (facts restated, not quoted): from 1 January 2026 the monthly contribution wage has a floor of EGP 2,700
  (up from 2,300) and a ceiling of EGP 16,700 (up from 14,500), i.e. 2,300-14,500 a month in 2025 (official secondary for the limits;
  the regulation's table was not read). The 1 % health contribution of the Universal Health Insurance Law 2/2018 is a
  different law, not reached (unsupported).
* Income Tax Law 91/2005 art. 13 (ETA's circular 1/2005 printing the deductions): "حصة الموظف أو العامل فى التأمين
  الإجتماعى" is deducted from salary income (no cap; the 15 % cap of the same article covers items 3-4 only).
Input `"w5Contrib": false` drops the contribution and its deduction.
-/

namespace EgTax
open TaxKernel

/-- Column 1 of the art. 8 table (net income up to 600,000), used for the kernel theorems. -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (40000, 1000), (55000, 1500), (70000, 2000), (200000, 2250), (400000, 2500)]

/-- The schedule that art. 8 applies to a net income `ni` (the column is chosen by the size of the whole income). -/
def column (ni : Int) : Schedule :=
  if ni ≤ 600000 then sched
  else if ni ≤ 700000 then Schedule.ofList [(0, 1000), (55000, 1500), (70000, 2000), (200000, 2250), (400000, 2500)]
  else if ni ≤ 800000 then Schedule.ofList [(0, 1500), (70000, 2000), (200000, 2250), (400000, 2500)]
  else if ni ≤ 900000 then Schedule.ofList [(0, 2000), (200000, 2250), (400000, 2500)]
  else if ni ≤ 1200000 then Schedule.ofList [(0, 2250), (400000, 2500)]
  else Schedule.ofList [(0, 2500), (1200000, 2750)]

def exemption : Int := 20000

/-- Tax on net income (art. 8): rounded down to 10 pounds, the column's bands, whole pounds (piastres dropped). -/
def taxOn (ni : Int) : Int :=
  let x := toMultiple .down 10 (pos ni)
  rateSchedTax x
where rateSchedTax (x : Int) : Int := (column x).tax Rule.unitDown x

/- The notches the table creates: passing 600,000 / 700,000 / 800,000 / 900,000 / 1,200,000 by 10 pounds. -/
#guard taxOn 600000 = 124750 ∧ taxOn 600010 = 128752
#guard taxOn 1200000 = 290000 ∧ taxOn 1200010 = 300002

/-- Law 148/2019 arts. 19 (1) (b) and 36 (1): employee 9 % + 1 % of the monthly contribution wage, kept between the
2025 limits 2,300 and 14,500 (a positive wage below the minimum is insured at the minimum). -/
def siMonth (m : Int) : Int := if m ≤ 0 then 0 else divR .halfUp (1000 * clamp 2300 14500 m) BP

def socialInsurance (wages : Int) : Int := perPeriod 12 siMonth (pos wages)

#guard siMonth 10000 = 1000 ∧ siMonth 20000 = 1450 ∧ siMonth 1000 = 230
#guard socialInsurance 120000 = 12000 ∧ socialInsurance 600000 = 17400

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let rs := c.adults.map fun a =>
    let si := if w5 then socialInsurance a.wages else 0
    let ni := pos (a.wages - si - exemption) + a.selfEmployment
    (taxOn ni, ni, si)
  Out.make c "EG" "EGP" (sumInts (rs.map (·.1))) (employeeSocial := sumInts (rs.map (·.2.2)))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.2.1))), Out.d "socialInsurance" (sumInts (rs.map (·.2.2)))])
    (unsupported := ["Universal Health Insurance Law 2/2018 employee contribution not reached",
      "rental income, dividends, interest and capital gains not modelled; excluded",
      "pensions not modelled"])

def country : Country := { code := "EG", name := "Egypt (Income Tax Law 91/2005 as amended by Law 7/2024)", currency := "EGP", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end EgTax
