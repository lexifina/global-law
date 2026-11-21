import KrTax.Basic
import KrTax.Social

/-!
# The 종합소득세 of one resident (소득세법), 2025

Order of the statute (ITA §14, §15): 총급여액 → 근로소득공제 (§47) → 근로소득금액; 연금소득 (§47의2); 사업소득금액
(input = net business income, 장부 basis; `Owner.lean` for 경비율); 이자·배당 (§14③6 분리과세 up to 2천만원, above it
종합과세 with Gross-up §17③ and the §62 comparison) → 종합소득금액 → 인적공제 (§50, §51), 연금보험료공제 (§51의3),
특별소득공제 (§52) → 과세표준 → 산출세액 (§55, §62) → 배당세액공제 (§56), 근로소득세액공제 (§59), 자녀세액공제
(§59의2), 연금계좌세액공제 (§59의3), 특별세액공제 (기부금, §59의4④) or 표준세액공제 (§59의4⑨), limited to the 산출세액
(§61) → 결정세액. Amounts are cut to the won (원 미만 절사).
-/

namespace KrTax
open TaxKernel

/-- §47: 근로소득공제 (capped at 2천만원 and at the 총급여액, §47③). -/
def earnedDeduction (w : Int) : Int := min (min (earnedDedSched.tax Rule.unitDown (pos w)) earnedDedCap) (pos w)
/-- §47의2: 연금소득공제 (capped at 900만원 and at the 총연금액). -/
def pensionDeduction (p : Int) : Int := min (min (pensionDedSched.tax Rule.unitDown (pos p)) pensionDedCap) (pos p)
/-- §55① 산출세액 on a 과세표준 (won, cut down). -/
def natTax (x : Int) : Int := natSched.tax Rule.unitDown (pos x)
/-- LTA §92① 개인지방소득세 산출세액. -/
def localTax (x : Int) : Int := localSched.tax Rule.unitDown (pos x)
/-- §59①: 근로소득세액공제 before the limit, on the 근로소득 산출세액. -/
def earnedCreditRaw (t : Int) : Int := earnedCreditSched.tax Rule.unitDown (pos t)
/-- §59: 근로소득세액공제 = min(§59①, §59② limit by 총급여액). -/
def earnedCredit (t w : Int) : Int := if w ≤ 0 then 0 else min (earnedCreditRaw t) (earnedCreditLimit w)

/-- What one resident brings to the computation. -/
structure PersonIn where
  age : Nat := 40
  wages : Int := 0
  biz : Int := 0              -- 사업소득금액 (net)
  pension : Int := 0          -- 총연금액 (public pensions)
  interest : Int := 0
  dividends : Int := 0        -- dividends that bore corporate tax (Gross-up applies)
  pensionContrib : Int := 0   -- 연금계좌 납입액
  charitable : Int := 0       -- 일반기부금
  spouse : Bool := false      -- claims the spouse (기본공제)
  spouseElderly : Bool := false
  kids : List Nat := []       -- ages of the children this person claims (each ≤ 20)
  births : List Nat := []     -- birth order of children born in 2025 that this person claims
  singleParent : Bool := false
  /-- `some true`: 표준세액공제; `some false`: itemise; `none`: the cheaper (the taxpayer's choice, §59의4⑨) -/
  standard : Option Bool := none
  /-- the OECD's social-insurance convention (validation only) -/
  oecdSocial : Bool := false
  /-- tax year (2024 or 2025; tests round 2) -/
  year : Int := 2025
  deriving Repr, Inhabited

structure PersonOut where
  soc : SocialOut
  earnedDed : Int
  earnedInc : Int
  pensionInc : Int
  finSeparate : Int          -- 분리과세 이자·배당 (taxed at 14 % at source)
  grossUp : Int
  finInc : Int               -- 종합과세 이자·배당 incl. Gross-up
  comprehensive : Int        -- 종합소득금액
  personalDed : Int
  pensionPremDed : Int
  specialDed : Int
  taxable : Int              -- 과세표준
  calcTax : Int              -- 산출세액
  dividendCredit : Int
  earnedCr : Int
  childCr : Int
  pensionAcctCr : Int
  donationCr : Int
  stdCr : Int
  determined : Int           -- 결정세액
  sepTax : Int               -- 14 % on 분리과세 이자·배당
  usedStandard : Bool
  deriving Repr

/-- The tax of a resident for one choice of `standard` (§59의4⑨: 표준세액공제 excludes 특별소득공제 and 특별세액공제). -/
def personWith (p : PersonIn) (std : Bool) : PersonOut :=
  let soc0 := if p.oecdSocial ∧ p.wages > 0 then socialOecd p.age p.wages p.year else social p.age p.wages p.biz p.year
  let other := nhiOtherIncome p.biz p.pension (pos p.interest + pos p.dividends)
  -- 직장가입자: premium on other income above 2천만원; 지역가입자: on all of it (property part not modelled)
  let soc := if p.wages > 0 then { soc0 with healthOther := healthOnOther other }
    else { soc0 with health := healthSelf other }
  let employee := p.wages > 0
  let ed := earnedDeduction p.wages
  let ei := pos p.wages - ed
  let pinc := pos p.pension - pensionDeduction p.pension
  let fin := pos p.interest + pos p.dividends
  let comp := decide (fin > finThreshold)
  -- §17③, STAD-style ordering (ITAD §116의2: interest first): Gross-up on dividends above the threshold
  let gu := if comp then mulDiv (min (pos p.dividends) (fin - finThreshold)) grossUpBp 10000 else 0
  let fi := if comp then fin + gu else 0
  let total := ei + pinc + pos p.biz + fi
  -- §50, §51 (인적공제, limited to 종합소득금액 by §51④)
  let nDep : Int := 1 + (if p.spouse then 1 else 0) + p.kids.length
  let extra := (if p.age ≥ 70 then elderlyDed else 0) + (if p.spouseElderly then elderlyDed else 0)
    + (if p.singleParent ∧ p.kids.length > 0 then singleParentDed else 0)
  let personal := min (basicDed * nDep + extra) total
  -- §51의3 연금보험료공제 (employee or 지역 contribution), §52 특별소득공제 (employee insurance), unless standard
  let ppd := soc.pension
  let spd := if std then 0 else min (soc.special employee) ei
  let ded := min (personal + ppd + spd) total
  let taxable := pos (total - ded)
  -- §55, §62
  let (ct, divCr) :=
    if comp then
      let a := (natSchedY p.year).tax Rule.unitDown (pos (taxable - finThreshold)) + mulDiv finThreshold finRateBp 10000
      let b := mulDiv fin finRateBp 10000 + (natSchedY p.year).tax Rule.unitDown (pos (taxable - fi))
      (max a b, if a > b then min gu (a - b) else 0)
    else ((natSchedY p.year).tax Rule.unitDown (pos taxable), 0)
  -- §59: the 근로소득 산출세액 = 산출세액 × 근로소득금액 / 종합소득금액
  let earnedPart := if total > 0 then mulDiv ct ei total else 0
  let ec := if p.wages ≤ 0 then 0 else min (earnedCreditRaw earnedPart) (earnedCreditLimitY p.year p.wages)
  let nKids := (p.kids.filter (fun a => childCreditMinAgeY p.year ≤ a)).length
  let cc := childCreditY2 p.year nKids + (p.births.map birthCredit).foldl (· + ·) 0
  let rate := if total ≤ 45000000 ∨ (p.biz = 0 ∧ p.pension = 0 ∧ fi = 0 ∧ p.wages ≤ 55000000) then 1500 else 1200
  let pac := mulDiv (min (pos p.pensionContrib) pensionAcctCap) rate 10000
  -- §59의4④: 일반기부금, limited to 30 % of 소득금액; 15 % (30 % above 1천만원); not for business-only residents
  let don := min (pos p.charitable) (mulDiv total 30 100)
  let dc := if std ∨ (p.wages ≤ 0 ∧ p.pension ≤ 0 ∧ fi = 0) then 0
    else mulDiv (min don 10000000) 15 100 + mulDiv (pos (don - 10000000)) 30 100
  let sc := if employee then (if std then stdCreditEmployee else 0)
    else if total > 0 then stdCreditOther else 0
  -- §61: credits beyond the 산출세액 are lost
  let det := pos (ct - divCr - ec - cc - pac - dc - sc)
  { soc, earnedDed := ed, earnedInc := ei, pensionInc := pinc,
    finSeparate := if comp then 0 else fin, grossUp := gu, finInc := fi, comprehensive := total,
    personalDed := personal, pensionPremDed := ppd, specialDed := spd, taxable, calcTax := ct,
    dividendCredit := divCr, earnedCr := ec, childCr := cc, pensionAcctCr := pac, donationCr := dc, stdCr := sc,
    determined := det, sepTax := if comp then 0 else mulDiv fin finRateBp 10000, usedStandard := std }

/-- The resident's tax with the cheaper choice of 표준세액공제 (an employee's; others always have it). -/
def person (p : PersonIn) : PersonOut :=
  match p.standard with
  | some s => personWith p s
  | none =>
    let a := personWith p false
    let b := personWith p true
    if p.wages > 0 ∧ b.determined < a.determined then b else a

/-- The child credit a person actually used (for STAD §100의31②): what is left of the 산출세액 after the credits
the statute takes before it is the most that can be used (§61). -/
def childCreditUsed (o : PersonOut) : Int :=
  min o.childCr (pos (o.calcTax - o.dividendCredit - o.earnedCr))

/-- 개인지방소득세 of the resident: 10 % of the 결정세액 (LTA §92① = the national schedule / 10 (`Theorems.local_eq`),
local credits of 지방세특례제한법 assumed equal to 10 % of the national ones; LTA §103의13: 특별징수 "원천징수하는
소득세 … 의 100분의 10"), plus 1.4 % on 분리과세 이자·배당. -/
def localIncomeTax (o : PersonOut) : Int := o.determined / 10 + o.sepTax / 10

end KrTax
