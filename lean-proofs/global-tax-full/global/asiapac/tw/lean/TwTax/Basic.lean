import TaxKernel.World

/-!
# Taiwan (Republic of China): 綜合所得稅 for income year 2025 (民國114年度)

Statute: 所得稅法 (Income Tax Act), read through Global law (`taiwan/national/acts/law/1943/G0340003`, text as in
force 2025-12-31; official text lis.ly.gov.tw / law.moj.gov.tw): art. 5 (exemption and brackets, indexed by CPI and
announced by the Ministry of Finance before each year, art. 5 (4)), art. 5-1, art. 14 (categories of income), art. 15
(joint return and the three ways of computing it), art. 17 (exemptions and deductions), art. 71.

The 2025 amounts are the Ministry's art. 5 (4) announcement of 2024-11-28 (賦稅署 新聞稿 "公告114年度綜合所得稅及所得
基本稅額相關免稅額、扣除額、課稅級距…", attachment 114年度…金額一覽表.pdf, sha256 3d9e68ae…; 速算公式.pdf sha256
70c63d73…): "114年度適用之平均消費者物價指數與113年度適用之指數相較，上漲2.29%，未達應調整標準，爰免予調整". The basic
living expense (基本生活所需之費用, 納稅者權利保護法 art. 4) is the Ministry's announcement of 2025-11-27: "114年度每人
基本生活所需之費用金額為新臺幣21.3萬元". The 2025 filing briefing (114年度所得稅結算申報記者座談會資料, 2026-04-23,
sha256 d0bab3d9…) restates every amount used here. Files: `cmp20/world/B02-g20/tw/law/`.

Not modelled (flagged in `unsupported`): employee labour/health/employment insurance (rates and insured-salary grades
are set by administrative notices under 勞工保險條例 art. 13-15, 全民健康保險法 art. 18-19, 27 and 就業保險法 art. 8,
not by the Act; the notices were not reached), itemized deductions other than donations, disability, tuition,
long-term-care and rent deductions (no input), the alternative minimum tax (所得基本稅額條例), 房地合一 property gains.

W5 pattern A (2026-11-20): employee labour, employment and national health insurance premiums (input `"w5Contrib":
false` drops them and restores the earlier outputs). Texts in `tw/law/w5/` (law.moj.gov.tw, bli.gov.tw, nhi.gov.tw).
* 勞工保險條例 (as amended to 2026-01-21) art. 13 (2): ordinary-accident rate 7.5 % when the 2008 amendment took effect
  (2009), +0.5 in the third year, then +0.5 a year to 10 %, then +0.5 every two years to 13 %: 12.5 % for 2025;
  就業保險法 art. 41 (2): for its insured the LI rate is reduced by 1 % ("按被保險人當月之月投保薪資百分之一調降之"),
  so 11.5 %; art. 8: EI rate 1-2 % as approved by the Executive Yuan, 1 % in force. LI art. 15 (1): employee 20 %;
  EI art. 40 applies LI's burden rules. LI art. 6 / EI art. 5: employees aged 15 to 65. BLI share table for 114年 (ods,
  "勞工保險普通事故保險費率自114年1月1日起由12%調整為12.5%，…依該法41條第2項規定調降1%，…11.5%，就業保險費率1%，
  按被保險人負擔20%") confirms the rates (official secondary). Insured salary: LI art. 14 grading table
  (勞動部 2024-11-15 勞動保2字第1130087589號令, from 2025-01-01): grade 1 28,590 to grade 12 45,800; its note's
  part-time grades 11,100 / 12,540 and the trainee grades 13,500-27,600 are applied to a monthly wage below 28,590
  (reading: a wage below the minimum wage is part-time pay). Each premium rounded half up per month (as the BLI table).
* 全民健康保險法 (2023-06-28) art. 18: premium = insured amount x rate (cap 6 %), dependants' premiums paid by the
  insured, "超過三口者，以三口計"; art. 27 (1) (二): private employee and dependants pay 30 %; art. 2 (二): dependants =
  spouse without occupation, minor children without occupation (parents not modelled). Rate 5.17 % (from 2021-01-01) and
  the 59-grade 投保金額分級表 from 2025-01-01 (28,590 to 313,000), NHIA tables (official secondary); art. 19 (2) floor
  = minimum wage, applied to any positive wage. Dependants are attached to the first adult with wages (else the second).
  The supplementary premium (二代健保補充保費) on interest, dividends and rent is not modelled.
* 所得稅法 art. 17 (1) 2 (二) 2: NHI premiums deductible without limit, labour (and employment) insurance premiums up to
  24,000 a person (text before the 2025-12-26 amendment; the current text drops the cap for labour insurance; the cap
  never binds here); as itemized deductions, so only when they and donations beat the standard deduction.
-/

namespace TwTax
open TaxKernel

/-- 所得稅法 art. 5 (2) brackets as announced for 114年度 (速算公式: "0~590,000 ×5％－0 … 4,980,001 以上×40％－911,700"). -/
def sched : Schedule := Schedule.ofList [(0, 500), (590000, 1200), (1330000, 2000), (2660000, 3000), (4980000, 4000)]

/-- art. 5 (1), 17 (1) 1: 免稅額 "一般 97,000" for 114年度 (one-page table). -/
def exemption : Int := 97000
/-- art. 17 (1) 1: "年滿七十歲者，免稅額增加百分之五十": 145,500 for 114年度. -/
def exemption70 : Int := 145500
/-- art. 17 (1) 2 (一) 標準扣除額: "單身 131,000 / 有配偶者 262,000" (114年度). -/
def stdSingle : Int := 131000
def stdMarried : Int := 262000
/-- art. 17 (1) 2 (三) 2 薪資所得特別扣除額 "218,000" (114年度); art. 14 第三類 一: salary less this, not below 0. -/
def salaryDed : Int := 218000
/-- art. 17 (1) 2 (三) 3 儲蓄投資特別扣除: "合計全年扣除數額以二十七萬元為限" (not indexed). -/
def savingsCap : Int := 270000
/-- art. 17 (1) 2 (三) 6 幼兒學前特別扣除: "六歲以下之子女，第一名子女每年扣除十五萬元，第二名及以上子女每人每年扣除二十二萬五千元". -/
def preschool1 : Int := 150000
def preschoolN : Int := 225000
/-- 基本生活所需之費用 per person, 114年度 (MOF announcement 2025-11-27): 213,000. -/
def basicLiving : Int := 213000
/-- art. 14 第九類 二 分期領取退職所得 減除金額, 114年度: 859,000. -/
def pensionDed : Int := 859000
/-- art. 15 (4): dividends "按百分之八點五計算可抵減稅額 … 每一申報戶每年抵減金額以八萬元為限". -/
def divCreditRate : Int := 850
def divCreditCap : Int := 80000
/-- art. 15 (5): "按百分之二十八之稅率分開計算應納稅額". -/
def divSepRate : Int := 2800
/-- art. 17 (1) 2 (二) 1: donations "最高不超過綜合所得總額百分之二十". -/
def donationPct : Int := 2000
/-- art. 14 第三類 五: voluntary labour-pension contributions "合計在每月工資百分之六範圍內，不計入…薪資收入". -/
def volPensionPct : Int := 600
/-- Rental income: art. 14 第五類 一 (收入 less necessary costs); the Ministry's standard for 114年度 is 43 % of the
rent (briefing 三(十二)2: "114年度財產租賃必要損耗及費用標準均維持113年度之標準43%"). -/
def rentalCostPct : Int := 4300

/-! ### W5 pattern A: employee social insurance -/

/-- 勞工保險投保薪資分級表 from 2025-01-01: part-time 11,100 / 12,540, trainee 13,500-27,600, then grades 1-12. -/
def liGrades : List Int := [11100, 12540, 13500, 15840, 16500, 17280, 17880, 19047, 20008, 21009, 22000, 23100, 24000,
  25250, 26400, 27600, 28590, 28800, 30300, 31800, 33300, 34800, 36300, 38200, 40100, 42000, 43900, 45800]
/-- 全民健康保險投保金額分級表 from 2025-01-01, grades 1-59. -/
def nhiGrades : List Int := [28590, 28800, 30300, 31800, 33300, 34800, 36300, 38200, 40100, 42000, 43900, 45800, 48200,
  50600, 53000, 55400, 57800, 60800, 63800, 66800, 69800, 72800, 76500, 80200, 83900, 87600, 92100, 96600, 101100,
  105600, 110100, 115500, 120900, 126300, 131700, 137100, 142500, 147900, 150000, 156400, 162800, 169200, 175600,
  182000, 189500, 197000, 204500, 212000, 219500, 228200, 236900, 245600, 254300, 263000, 273000, 283000, 293000,
  303000, 313000]

/-- The grade for a monthly wage: the first grade at or above it, the top grade above the table. -/
def gradeOf (gs : List Int) (m : Int) : Int := (gs.find? (fun g => m ≤ g)).getD (gs.getLastD 0)

/-- Employee LI (11.5 % x 20 % = 2.3 %) + EI (1 % x 20 % = 0.2 %) a month, each rounded half up. -/
def liEiMonthly (g : Int) : Int := divR .halfUp (g * 23) 1000 + divR .halfUp (g * 2) 1000
/-- Employee NHI a month for one insured person: 5.17 % x 30 %, rounded half up. -/
def nhiMonthly (g : Int) : Int := divR .halfUp (g * 517 * 30) 1000000

/-- Annual employee premiums of one adult: (LI + EI, NHI for self and `deps` dependants). -/
def premiums (a : Adult) (deps : Nat) : Int × Int :=
  if a.wages ≤ 0 then (0, 0) else
  let m := a.wages / 12
  let li := if 15 ≤ a.age ∧ a.age ≤ 65 then 12 * liEiMonthly (gradeOf liGrades m) else 0
  (li, 12 * nhiMonthly (gradeOf nhiGrades m) * (1 + (min deps 3 : Nat)))

#guard gradeOf liGrades 30000 = 30300 ∧ gradeOf liGrades 50000 = 45800 ∧ gradeOf liGrades 28000 = 28590
#guard liEiMonthly 45800 = 1145 ∧ liEiMonthly 28590 = 715
#guard nhiMonthly 28590 = 443 ∧ nhiMonthly 150000 = 2327 ∧ nhiMonthly 313000 = 4855
#guard liGrades.length = 28 ∧ nhiGrades.length = 59

/-- Tax on 綜合所得淨額 (whole dollars; the Act prints no rounding rule: down to the dollar). -/
def taxOn (ni : Int) : Int := sched.tax Rule.unitDown (pos ni)

def pctOf (bp x : Int) : Int := divR .down (bp * x) BP

/-- One person of the return: salary, other personal income (business + pension after its deduction) and
the exemption that person brings. -/
structure Person where
  salary : Int
  other : Int
  exempt : Int
  deriving Repr

/-- Salary income of a person (art. 14 第三類 一): salary less the special deduction, not below 0. -/
def salaryIncome (w : Int) : Int := pos (w - min (pos w) salaryDed)

def personOf (a : Adult) (volPension : Int) : Person :=
  let w := pos (a.wages - volPension)
  { salary := w, other := a.selfEmployment + pos (a.pension - pensionDed),
    exempt := if a.age ≥ 70 then exemption70 else exemption }

/-- Preschool deduction for `n` children aged six or less (art. 17 (1) 2 (三) 6). -/
def preschool (n : Nat) : Int := if n = 0 then 0 else preschool1 + preschoolN * ((n : Int) - 1)

/-- The household-level inputs of one return. -/
structure Ret where
  people : List Person      -- taxpayer, then spouse (if any)
  deps : Nat                -- dependants (children)
  under7 : Nat
  interest : Int
  dividends : Int
  rentalNet : Int
  donations : Int
  married : Bool
  premiums : Int := 0        -- W5: insurance premiums deductible under art. 17 (1) 2 (二) 2
  deriving Repr

def Ret.sumSalaryIncome (r : Ret) : Int := sumInts (r.people.map fun p => salaryIncome p.salary)
def Ret.sumOther (r : Ret) : Int := sumInts (r.people.map (·.other))
def Ret.exemptAll (r : Ret) : Int := sumInts (r.people.map (·.exempt)) + exemption * (r.deps : Int)
def Ret.std (r : Ret) : Int := if r.married then stdMarried else stdSingle
def Ret.persons (r : Ret) : Int := (r.people.length : Int) + r.deps

/-- 基本生活費差額 (納稅者權利保護法 art. 4 as announced): persons × 213,000 less the comparison items (exemptions,
standard or itemized deduction, savings, preschool), if positive; deducted from 綜合所得總額. -/
def basicDiff (persons exempt general savings pre : Int) : Int :=
  pos (basicLiving * persons - (exempt + general + savings + pre))

/-- Tax of a return under art. 15 (2), method `m`: 1 = all combined; (2, i) = person i's salary separately;
(3, i) = all of person i's income separately. `divSep` = dividends taxed at 28 % apart (art. 15 (5)).
Returns (tax before the dividend credit, dividend credit). -/
def methodTax (r : Ret) (m : Nat) (i : Nat) (divSep : Bool) : Int × Int :=
  let divIn := if divSep then 0 else r.dividends
  let grossInv := r.interest + r.rentalNet + divIn
  let savings := min r.interest savingsCap
  let pre := preschool r.under7
  let grossAll := r.sumSalaryIncome + r.sumOther + grossInv
  let itemized := min r.donations (pctOf donationPct grossAll) + r.premiums
  let general := max r.std itemized
  let bd := basicDiff r.persons r.exemptAll general savings pre
  let sepPart : Int × Int × Int :=   -- (separate tax, income removed from the combined part, exemption removed)
    match r.people[i]? with
    | none => (0, 0, 0)
    | some p =>
      if m = 2 then (taxOn (salaryIncome p.salary - p.exempt), salaryIncome p.salary, p.exempt)
      else if m = 3 then (taxOn (salaryIncome p.salary + p.other - p.exempt), salaryIncome p.salary + p.other, p.exempt)
      else (0, 0, 0)
  let (sepTax, removed, exRemoved) := sepPart
  let combinedNet := grossAll - removed - bd - (r.exemptAll - exRemoved) - general - savings - pre
  let t := sepTax + taxOn combinedNet + (if divSep then pctOf divSepRate r.dividends else 0)
  let credit := if divSep then 0 else min divCreditCap (pctOf divCreditRate r.dividends)
  (t, credit)

/-- All the computations art. 15 (2) and (4)-(5) let the taxpayer choose from; the cheapest net of the credit. -/
def options (r : Ret) : List (String × Int × Int) :=
  let idx := List.range r.people.length
  let ms : List (String × Nat × Nat) :=
    [("combined", 1, 0)] ++ (if r.people.length ≥ 2 then
      idx.map (fun i => (s!"salarySeparate{i+1}", 2, i)) ++ idx.map (fun i => (s!"allSeparate{i+1}", 3, i)) else [])
  ms.foldr (fun (nm, m, i) acc =>
    let a := methodTax r m i false
    let b := methodTax r m i true
    (nm ++ "+dividendCredit", a.1, a.2) :: (nm ++ "+dividend28", b.1, b.2) :: acc) []

def best (r : Ret) : String × Int × Int :=
  (options r).foldl (fun acc o => if o.2.1 - o.2.2 < acc.2.1 - acc.2.2 then o else acc)
    (options r).head!

def out (c : Canon) : Out :=
  let couple := c.isCouple && c.married
  let volP := c.pensionContributions
  let wagesTot := sumInts (c.adults.map (·.wages))
  let volCap := pctOf volPensionPct wagesTot
  let volUsed := min (pos volP) volCap
  -- voluntary pension contributions attributed to the first adult (contract: household total)
  let adults := c.adults
  let p1 := personOf c.adult1 volUsed
  let rentalNet := c.rentalIncome - pctOf rentalCostPct c.rentalIncome
  -- W5 pattern A: employee LI / EI / NHI premiums; NHI dependants (art. 2 (二), cap 3 in art. 18 (2)) with the first
  -- adult who has wages (else the second): a spouse without occupation and the minor children.
  let w5 := (c.bool? "w5Contrib").getD true
  let holder : Nat := if c.adult1.wages > 0 then 0 else 1
  let spouseDep : Nat := match adults[1 - holder]? with
    | some s => if couple ∧ s.wages ≤ 0 ∧ s.selfEmployment ≤ 0 then 1 else 0
    | none => 0
  let prem (i : Nat) : Int × Int := match adults[i]? with
    | some a => if w5 then premiums a (if i = holder then spouseDep + c.nChildren else 0) else (0, 0)
    | none => (0, 0)
  let liTot := (prem 0).1 + (prem 1).1
  let nhiTot := (prem 0).2 + (prem 1).2
  let dedOf (i : Nat) : Int := (prem i).2 + min (prem i).1 24000
  let mk (ps : List Person) (deps under7 : Nat) (inv : Int × Int × Int) (don : Int) (m : Bool) (pr : Int) : Ret :=
    { people := ps, deps, under7, interest := inv.1, dividends := inv.2.1, rentalNet := inv.2.2, donations := don,
      married := m, premiums := pr }
  let rets : List Ret :=
    if couple then
      [mk [p1, personOf (adults[1]!) 0] c.nChildren (c.children.filter (·.age ≤ 6)).length
        (c.interest, c.dividends, rentalNet) c.charitable true (dedOf 0 + dedOf 1)]
    else match c.adult2? with
      | none => [mk [p1] c.nChildren (c.children.filter (·.age ≤ 6)).length (c.interest, c.dividends, rentalNet)
                  c.charitable false (dedOf 0)]
      | some a2 =>
        [mk [p1] c.nChildren (c.children.filter (·.age ≤ 6)).length
            (half1 c.interest, half1 c.dividends, half1 rentalNet) (half1 c.charitable) false (dedOf 0),
         mk [personOf a2 0] 0 0 (half2 c.interest, half2 c.dividends, half2 rentalNet) (half2 c.charitable) false
            (dedOf 1)]
  let res := rets.map best
  let tax := sumInts (res.map fun o => o.2.1)
  let credit := sumInts (res.map fun o => o.2.2)
  let it := tax - credit
  Out.make c "TW" "TWD" it (employeeSocial := liTot + nhiTot)
    (detail := [Out.d "taxBeforeCredits" tax, Out.d "dividendCredit" credit,
      Out.d "labourEmploymentInsurance" liTot, Out.d "nationalHealthInsurance" nhiTot,
      Out.dStr "method" (String.intercalate "; " (res.map (·.1))),
      Out.d "returns" (rets.length : Int),
      Out.dStr "note" "all art. 15 (2) computations and both dividend options evaluated; the cheapest is taken (the taxpayer's election); 8.5% dividend credit is refundable (art. 15 (4), art. 71 (3))"])
    (unsupported := (if w5 then ["NHI: dependent parents and the supplementary premium (補充保費) on interest, dividends and rent not modelled; part-time LI grades applied to any monthly wage below 28,590"]
      else ["employee social insurance (labour, employment and national health insurance): rates and insured-salary grades are administrative notices not reached"]) ++ [
      "capital gains: securities transaction income is not taxed under art. 4-1 (not modelled; capitalGains ignored)",
      "alternative minimum tax (所得基本稅額條例) not modelled",
      "children counted as dependants regardless of age (adult children qualify only if in school, disabled or unable to work: art. 17 (1) 1 (二))"])

def country : Country := { code := "TW", name := "Taiwan (綜合所得稅)", currency := "TWD", year := "2025", compute := out }

/-! ## Checks on the statute's own printed tables -/

/-- The 速算公式 (rate × net − 累進差額) equals the bracket sum at every printed threshold. -/
def quick (x : Int) : Int :=
  if x ≤ 590000 then x * 5 / 100 else if x ≤ 1330000 then x * 12 / 100 - 41300
  else if x ≤ 2660000 then x * 20 / 100 - 147700 else if x ≤ 4980000 then x * 30 / 100 - 413700
  else x * 40 / 100 - 911700
#guard [0, 590000, 1330000, 2660000, 4980000, 10000000].all fun x => taxOn x = quick x
#guard taxOn 1000000 = 78700

theorem sched_progressive : sched.progressive = true := by decide

end TwTax
