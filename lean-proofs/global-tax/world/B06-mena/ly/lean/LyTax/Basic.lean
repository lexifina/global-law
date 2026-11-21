import TaxKernel.World

/-!
# Libya: Income Tax Law No. 7 of 2010 (tax on income from work), 2025

Authority and source: the Tax Authority (مصلحة الضرائب, Tripoli; `tax.gov.ly`) publishes the "Encyclopaedia of
modern tax legislation" (موسوعة التشريعات الضريبية الحديثة, 2016, `tax.gov.ly/assets/m2016.pdf`, 227 scanned pages,
sha256 in FINDINGS), "النافذة والحديثة الإلغاء". Law 7/2010 predates the 2014 division of authority and is applied
by both; no amendment of the articles below after 2016 was found, but the post-2016 record could not be read
(access B). Text read by Arabic OCR (tools/ocrx.sh) and checked on the page images.
* Art. 35 (د): a schedular tax on "الدخل الناتج عن العمل وما في حكمه".
* Art. 36: exempt "(1800) … إذا كان أعزب أو (2400) … إذا كان متزوجاً وليس له أطفال يعولهم فضلا عن تمتعه بإعفاء
  قدره (300) … عن كل طفل أو طفلة من أطفاله القصر"; widowed or divorced with children as married; "يستنزل مبلغ
  الإعفاء من وعاء الضريبة". Art. 57: tax on what exceeds the exemption.
* Art. 55 (exclusions) 1: "ما يساهم به الممول في نظام التقاعد".
* Art. 58: "(12000) دينار الأولى من الدخل (5%) ؛ ما زاد على ذلك من الدخل (10%)" (page image checked).
* Art. 61-62: interest on bank deposits 5 %.
* Jihad tax, Law 44/1970 art. 2 أولاً (in the encyclopaedia's list without "ملغي"): on salaries and pensions 1 % if
  the income is ≤ 50 a month, 2 % "من كامل الدخل" if above 50 and ≤ 100, 3 % "من كامل الدخل" above 100 (pounds; the
  dinar replaced the Libyan pound at par in 1971).
* Social Solidarity Fund, Law 20/1428 art. 3 as replaced by Law 10/1430: "اشتراك بنسبة 1% يستقطع من إجمالى دخول
  العاملين كافة".
* Social security: the encyclopaedia's table (p. 208) under Law 1/1991 and decision 182/1991: total 15 % of pay,
  the insured national employee's share 25 % of it, "3.75% من المرتب" (employees of foreign employers also 3.75 %).
Unit: individual.
-/

namespace LyTax
open TaxKernel

/-- Art. 58 (bp), on income above the art. 36 exemption. -/
def sched : Schedule := Schedule.ofList [(0, 500), (12000, 1000)]

def exemption (married : Bool) (kids : Nat) : Int :=
  (if married || kids > 0 then 2400 else 1800) + 300 * kids

def ssEmployee (w : Int) : Int := pos w * 375 / 10000      -- 3.75 % (decision 182/1991 table)
def solidarity (w : Int) : Int := pos w / 100              -- 1 % (Law 20/1428 art. 3)

/-- Law 44/1970 art. 2 أولاً: the rate applies to the whole monthly income. -/
def jihadMonthly (m : Int) : Int :=
  if m ≤ 0 then 0 else if m ≤ 50 then m / 100 else if m ≤ 100 then m * 2 / 100 else m * 3 / 100

/-- On 12 equal months, at the rate the monthly pay falls in, computed on the year in whole dinars (the Libyan unit
    has 1,000 dirhams; flooring each month to a whole dinar made 12-dinar steps). -/
def jihad (annual : Int) : Int :=
  let m := pos annual / 12
  if m ≤ 0 then 0 else if m ≤ 50 then pos annual / 100 else if m ≤ 100 then pos annual * 2 / 100 else pos annual * 3 / 100

def workTax (w : Int) (ex : Int) : Int := sched.tax Rule.unitDown (pos (w - ssEmployee w - ex))

def out (c : Canon) : Out :=
  let kids := c.childrenUnder 18
  let a1 := c.adult1
  let t1 := workTax a1.wages (exemption c.married kids)
  let t2 := match c.adult2? with | some a => workTax a.wages (exemption c.married 0) | none => 0
  let jh := sumInts (c.adults.map fun a => jihad a.wages + jihad a.pension)
  let intTax := pos c.interest * 5 / 100
  let ss := sumInts (c.adults.map fun a => ssEmployee a.wages + solidarity a.wages)
  Out.make c "LY" "LYD" (t1 + t2 + intTax) (surtaxes := [("jihadTax", jh)]) (employeeSocial := ss)
    (detail := [Out.d "workIncomeTax" (t1 + t2), Out.d "interestTax" intTax])
    (unsupported := ["trade, craft and professional income (art. 35 أ-ج) not modelled; rents and dividends not modelled",
      "post-2016 amendments not verified (source: the Tax Authority's 2016 encyclopaedia)",
      "jihad tax 2025 status: listed without repeal in 2016; modelled as in force",
      "pensions: income-tax treatment not read (jihad tax applied)"])

def country : Country :=
  { code := "LY", name := "Libya (Income Tax Law 7/2010)", currency := "LYD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard workTax 14200 1800 = 0 + (pos (14200 - 532 - 1800)) * 5 / 100   -- 11,868 at 5 %
#guard sched.tax Rule.unitDown 12000 = 600 ∧ sched.tax Rule.unitDown 22000 = 1600
/- Jihad tax notches: 100 a month → 2; 101 → 3.03 (whole-income rates). -/
#guard jihadMonthly 100 = 2 ∧ jihadMonthly 101 = 3 ∧ jihadMonthly 50 = 0 ∧ jihadMonthly 51 = 1

end LyTax
