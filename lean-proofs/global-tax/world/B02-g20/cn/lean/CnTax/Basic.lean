import TaxKernel.World

/-!
# China: 个人所得税 of a resident individual, 2025

Statutes (国家法律法规数据库 flk.npc.gov.cn, the NPC's official database; files in `cn/law/`):
* 中华人民共和国个人所得税法 (7th amendment 2018-08-31, in force 2019-01-01; no later amendment in the database),
  docx sha256 903cc8d5…: art. 2 (综合所得 = wages + three labour-type incomes, annual), art. 3 (综合所得 3-45 %, 经营所得
  5-35 %, interest/dividends/rent/transfers "比例税率，税率为百分之二十"), art. 4 (7) basic pensions exempt, art. 6
  ("减除费用六万元以及专项扣除、专项附加扣除和依法确定的其他扣除"; rent "每次收入不超过四千元的，减除费用八百元；
  四千元以上的，减除百分之二十的费用"; donations up to "应纳税所得额百分之三十"), 税率表一 and 税率表二.
* 中华人民共和国个人所得税法实施条例 (2018-12-18), docx sha256 428d08b5…: art. 14 (rent "以一个月内取得的收入为
  一次"), art. 15 (business income of a person without 综合所得: "应当减除费用6万元"), art. 13 (deductions limited to
  the taxable income, no carry-forward), art. 19 (donation base before the donation).
* 专项附加扣除 for children (W5 review, 2026-11-20; texts in `cn/law/w5/`): 个人所得税专项附加扣除暂行办法
  (国发〔2018〕41号, gov.cn content_5351181, sha256 328e8a38…) 第五条 (子女教育 "按照每个子女每月1000元的标准定额扣除";
  "年满3岁至小学入学前处于学前教育阶段的子女，按本条第一款规定执行"), 第六条 ("父母可以选择由其中一方按扣除标准的100%扣除，
  也可以选择由双方分别按扣除标准的50%扣除"); 国发〔2022〕8号 (content_5682013, sha256 e37186ad…) 一、二 (3岁以下婴幼儿照护,
  same election); 国发〔2023〕13号 (content_6901206, sha256 e357548e…) 一、二 (both "由每个...每月1000元提高到2000元",
  "自2023年1月1日起实施"), no later change found.
Not reached (flagged): elderly support and the other 专项附加扣除 (no inputs), and the social insurance / housing fund
专项扣除 (rates by State Council decisions, bases by city notices). Preferential notices (listed
dividends held > 1 year, 10 % residential rent, the suspension of deposit-interest tax under art. 18) are not applied.
Unit: individual.
-/

namespace CnTax
open TaxKernel

/-- 税率表一 (综合所得): 3 % to 36 000, 10 % to 144 000, 20 % to 300 000, 25 % to 420 000, 30 % to 660 000, 35 % to
960 000, 45 % above. -/
def sched : Schedule :=
  Schedule.ofList [(0, 300), (36000, 1000), (144000, 2000), (300000, 2500), (420000, 3000), (660000, 3500), (960000, 4500)]
/-- 税率表二 (经营所得): 5 % to 30 000, 10 % to 90 000, 20 % to 300 000, 30 % to 500 000, 35 % above. -/
def schedBiz : Schedule := Schedule.ofList [(0, 500), (30000, 1000), (90000, 2000), (300000, 3000), (500000, 3500)]
def basicDeduction : Int := 60000
def flatRate : Int := 2000
def donationPct : Int := 3000

def taxOn (s : Schedule) (x : Int) : Int := s.tax Rule.unitHalfUp (pos x)

/-- Rent of one month (art. 6 (4); 实施条例 art. 14): taxable part. -/
def rentTaxable (r : Int) : Int := if r ≤ 0 then 0 else if r ≤ 4000 then pos (r - 800) else r - divR .down (2000 * r) BP

/-- Art. 6 (1) and its second paragraph: "专项扣除，包括居民个人按照国家规定的范围和标准缴纳的基本养老保险、基本医疗保险、
失业保险等社会保险费和住房公积金等", deducted from the 综合所得 with the 60,000. The rates and the contribution base limits
are set locally (city notices; e.g. Beijing's 京人社发〔2026〕7号 sets the base limits only from July 2026: 36,348 / 7,270 a
month; the 2025 notice was not reached), so they are optional inputs: `cnSocialRate` (employee basic pension + medical +
unemployment, basis points of the base), `cnHousingFundRate` (basis points), `cnBaseCapMonthly`, `cnBaseFloorMonthly`
(yuan a month). Without them nothing is deducted (as before). Wages are paid evenly over 12 months. -/
structure Special where
  siRate : Int := 0
  hfRate : Int := 0
  cap : Option Int := none
  floor : Option Int := none

def contribBase (sp : Special) (m : Int) : Int :=
  let m1 := match sp.cap with | some c => min m c | none => m
  match sp.floor with | some f => max m1 f | none => m1

/-- Annual employee 专项扣除 (social insurance + housing fund) on wages `w`. -/
def special (sp : Special) (w : Int) : Int :=
  if w ≤ 0 then 0 else
  perPeriod 12 (fun m => divR .down (sp.siRate * contribBase sp m) BP + divR .down (sp.hfRate * contribBase sp m) BP) w

#guard special {} 240000 = 0
#guard special { siRate := 1050, hfRate := 1200, cap := some 36348, floor := some 7270 } 1200000 =
  12 * (divR .down (1050 * 36348) BP + divR .down (1200 * 36348) BP)

/-- 子女教育 / 3岁以下婴幼儿照护 (国发〔2023〕13号 一、二): 2,000 yuan a month for each child, i.e. 24,000 a year. A child
under 3 takes the infant-care deduction, a child of 3 or more the education deduction (第五条: from 3, pre-school then
全日制学历教育; the grid's children, 0-17, are taken to be in education); the same amount either way. The age is the
household's (one age for the year: the months around a third birthday or a birth are not split). -/
def childMonthly : Int := 2000
/-- The deductions are claimed: 暂行办法 第二十五条 "纳税人首次享受专项附加扣除，应当将专项附加扣除相关信息提交扣缴义务人或者税务机关"; `cnChildDeduction` = false
models a household that claims none (default true: claimed). -/
def childAnnual (c : Canon) : Int :=
  if (c.bool? "cnChildDeduction").getD true then 12 * childMonthly * c.children.length else 0

#guard 12 * childMonthly = 24000

/-- One person: (综合所得 tax, 经营所得 tax, 20 % taxes, comprehensive taxable income). `extra` = the person's
专项附加扣除 for the year; a person with no 综合所得 deducts it from 经营所得 (实施条例 art. 15: "应当减除费用6万元、专项扣除、
专项附加扣除以及依法确定的其他扣除"). -/
def person (sp : Special) (a : Adult) (div gains rent donations : Int) (extra : Int := 0) : Int × Int × Int × Int :=
  let comp := a.wages
  let hasComp := comp > 0
  let ti0 := pos (comp - basicDeduction - special sp comp - extra)
  let don := min donations (divR .down (donationPct * ti0) BP)
  let ti := pos (ti0 - don)
  let bizTI := if hasComp then pos a.selfEmployment else pos (a.selfEmployment - basicDeduction - extra)
  let rentTax := 12 * divR .down (flatRate * rentTaxable (divR .down rent 12)) BP
  let flat := divR .down (flatRate * (pos div + pos gains)) BP + rentTax
  (taxOn sched ti, taxOn schedBiz bizTI, flat, ti)

def out (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let sp : Special := { siRate := (c.int? "cnSocialRate").getD 0, hfRate := (c.int? "cnHousingFundRate").getD 0,
                        cap := c.int? "cnBaseCapMonthly", floor := c.int? "cnBaseFloorMonthly" }
  let kids := childAnnual c
  /- 第六条 election per household: all to the first adult, all to the second, or 50 % each (a married couple); the
  household takes the allocation with the least total tax (ties: the first listed). `cnChildAlloc` (0 = first adult,
  1 = second, 2 = halves) fixes it instead. -/
  let alloc (k : Nat) (i : Nat) : Int :=
    if n = 1 then kids else if k = 2 then (if i = 0 then half1 kids else half2 kids) else if k = i then kids else 0
  let run (k : Nat) := (c.adults.zip (List.range n)).map fun (a, i) =>
    person sp a (share c.dividends i) (share c.capitalGains i) (share c.rentalIncome i) (share c.charitable i) (alloc k i)
  let total (rs : List (Int × Int × Int × Int)) : Int := sumInts (rs.map fun r => r.1 + r.2.1 + r.2.2.1)
  let opts : List Nat := if n = 1 ∨ kids = 0 then [0] else if c.married then [0, 1, 2] else [0, 1]
  let rs := match c.int? "cnChildAlloc" with
    | some k => run k.toNat
    | none => (opts.map run).foldl (fun b r => if total r < total b then r else b) (run (opts.headD 0))
  let comp := sumInts (rs.map (·.1))
  let biz := sumInts (rs.map (·.2.1))
  let flat := sumInts (rs.map (·.2.2.1))
  Out.make c "CN" "CNY" (comp + biz + flat)
    (employeeSocial := sumInts (c.adults.map fun a => special sp a.wages))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.2.2.2))), Out.d "comprehensiveTax" comp,
      Out.d "businessTax" biz, Out.d "flatRateTax" flat])
    (unsupported := ["专项附加扣除: children (education / infant care, 2,000 a month each) applied with the household's least-tax 第六条 allocation (inputs cnChildAlloc, cnChildDeduction); elderly support, housing, continuing education and serious illness not applied (no inputs)",
      "专项扣除 (employee social insurance and housing fund, art. 6 (1)): city rates and bases not read; deducted only when cnSocialRate / cnHousingFundRate (and cnBaseCapMonthly / cnBaseFloorMonthly) are given",
      "interest ignored (deposit-interest tax under art. 18 suspended by the State Council; not read)",
      "preferential notices (listed dividends, residential rent at 10 %, listed-share gains) not applied"])

def country : Country := { code := "CN", name := "China (个人所得税, resident)", currency := "CNY", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- 速算扣除数 published with the monthly-converted table are not in the Act; the annual band sums at the thresholds: -/
/- W5 review: a single earner of 300,000 with two children: 300,000 - 60,000 - 48,000 = 192,000 taxable; tax
3 % x 36,000 + 10 % x 108,000 + 20 % x 48,000 = 1,080 + 10,800 + 9,600 = 21,480. -/
#guard (person {} { wages := 300000 } 0 0 0 0 48000).1 = 21480
#guard (person {} { wages := 300000 } 0 0 0 0).1 = 31080
#guard sched.ticks 36000 = 1080 * BP ∧ sched.ticks 144000 = 11880 * BP ∧ sched.ticks 960000 = 250080 * BP

end CnTax
