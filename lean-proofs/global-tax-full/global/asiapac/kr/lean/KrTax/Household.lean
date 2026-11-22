import KrTax.Person
import KrTax.Incentive

/-!
# A household: two separate returns, who claims whom, the 장려금 and 아동수당

Korea taxes each resident separately (no joint filing). The household chooses who claims the children
(§50③ "어느 한 거주자의 종합소득금액에서 공제"); a spouse can be claimed by the other spouse when the spouse's
소득금액 is at most 100만원 (or wages only, 총급여액 ≤ 500만원). Defaults (the OECD's convention): the first adult
claims every child; investment income is split equally between spouses; 연금계좌 and 기부금 are the first adult's.

Korea-only optional input fields (all optional):
* `krClaimant`: 0 or 1, which adult claims the children (default 0); `"best"` tries both.
* `krStandard`: `"auto"` (default; each employee takes the cheaper of itemising and the 13만원 표준세액공제),
  `"itemise"`, `"standard"`.
* `krNoIncentives`: true to leave out 근로·자녀장려금 (a household that does not apply, or fails the asset test).
* `krRegime`, `krSales`, `krExpenseRate`: the self-employment regime (`Owner.lean`).
-/

namespace KrTax
open TaxKernel

/-- 소득금액 of an adult for the spouse test of §50①2 (wages enter through the 총급여액 test). -/
def depIncome (a : Adult) (inv : Int) : Int :=
  (pos a.wages - earnedDeduction a.wages) + pos a.selfEmployment + (pos a.pension - pensionDeduction a.pension)
    + (if inv > finThreshold then inv else 0)

def spouseQualifies (a : Adult) (inv : Int) : Bool :=
  decide (depIncome a inv ≤ depIncomeLimit) ||
    (decide (a.selfEmployment = 0 ∧ a.pension = 0 ∧ inv ≤ finThreshold ∧ a.wages ≤ depWageLimit))

structure HhOut where
  persons : List (PersonIn × PersonOut)
  eitc : Int
  ctc : Int
  kind : Nat
  earnedTotal : Int      -- 총급여액 등
  totalIncome : Int      -- 연간 총소득
  childAllowance : Int
  deriving Repr

def kidAges (c : Canon) : List Nat := (c.children.filter (fun k => k.age ≤ childMaxAge)).map (·.age)

/-- Birth order of children born in the year (age 0), counting the older children first. -/
def birthOrders (c : Canon) : List Nat :=
  let older := (c.children.filter (fun k => k.age > 0)).length
  let born := (c.children.filter (fun k => k.age = 0)).length
  (List.range born).map (fun i => older + i + 1)

/-- Universal cash for children (contract `benefits`): 아동수당 100,000 won a month under 8 (CAA §4①); 부모급여
under 2 (CAA §4⑤ with 아동수당법 시행령 §2① (current text, 대통령령 제36668호; same amounts in 2025): "1세 미만의 아동: 매월 100만원", "1세 이상 2세 미만의 아동: 매월
50만원"; the same words in 제33715호 (2023. 9. 12., `refs/lawgo/아동수당법시행령_33715.txt`), which govern from
2024-01-01 because 아동수당법 부칙 (법률 제18579호) 제6조 as amended by 법률 제19455호 keeps a 고시 amount "2023년 12월 31일까지";
children born from 2022-01-01 only (부칙 제4조), so every child under 2 in 2024–2025; 2022–2023 (고시 amounts, not
located) are listed as unsupported, round 8; read with the child's age at the end of the year, 12 months); with `krHomeCare` (children not at a
어린이집/유치원), 양육수당 (영유아보육법 §34의2) of 100,000 won a month for children aged 2 to 7 (24–85 months; the amount
from the 보건복지부 guidance as reported in OECD TaxBEN Korea 2025 §4.3.2). -/
def childBenefits (c : Canon) : Int :=
  let home := (c.bool? "krHomeCare").getD false
  (c.children.map fun k =>
    (if k.age ≤ childAllowanceMaxAge then childAllowanceMonthly * (if c.year = 2022 ∧ k.age = 7 then 9 else 12) else 0)
    + (if c.year = 2022 ∨ c.year = 2023 then 0 else if k.age = 0 then 1000000 * 12 else if k.age = 1 then 500000 * 12 else 0)
    + (if home ∧ 2 ≤ k.age ∧ k.age ≤ 7 then 100000 * 12 else 0)).foldl (· + ·) 0

def household (c : Canon) (claimant : Nat) (std : Option Bool) (incentives : Bool) : HhOut :=
  let a1 := c.adult1
  let couple := c.isCouple
  let inv1 := if couple then half1 c.interest + half1 c.dividends else c.interest + c.dividends
  let inv2 := half2 c.interest + half2 c.dividends
  let kids := kidAges c
  let bo := birthOrders c
  let mk (a : Adult) (i d : Int) (claims : Bool) (spouseOk : Bool) (spouseOld : Bool) (first : Bool) : PersonIn :=
    { age := a.age, wages := a.wages, biz := a.selfEmployment, pension := a.pension,
      interest := i, dividends := d,
      pensionContrib := if first then c.pensionContributions else 0,
      charitable := if first then c.charitable else 0,
      spouse := spouseOk, spouseElderly := spouseOk && spouseOld,
      kids := if claims then kids else [], births := if claims then bo else [],
      singleParent := claims && !(c.married && couple), standard := std,
      oecdSocial := c.str? "krConvention" == some "oecd", year := (c.year : Int) }
  match c.adult2? with
  | none =>
    let p := mk a1 c.interest c.dividends true false false true
    let o := person p
    let earned := pos a1.wages + pos a1.selfEmployment
    let tot := earned + pos a1.pension + c.interest + c.dividends + c.rentalIncome
    let nChild := (c.children.filter (fun k => k.age ≤ dependentChildMaxAge)).length
    let kind : Nat := if nChild > 0 then 1 else 0
    let e := if incentives then eitc kind earned tot (c.year : Int) else 0
    let k := if incentives then ctc kind nChild earned tot (childCreditUsed o) (c.year : Int) else 0
    { persons := [(p, o)], eitc := e, ctc := k, kind, earnedTotal := earned, totalIncome := tot,
      childAllowance := childBenefits c }
  | some a2 =>
    let m := c.married
    let s2ok := m && spouseQualifies a2 inv2
    let s1ok := m && spouseQualifies a1 inv1
    let p1 := mk a1 (half1 c.interest) (half1 c.dividends) (claimant == 0) s2ok (a2.age ≥ 70) true
    let p2 := mk a2 (half2 c.interest) (half2 c.dividends) (claimant == 1) s1ok (a1.age ≥ 70) false
    let o1 := person p1
    let o2 := person p2
    let e1 := pos a1.wages + pos a1.selfEmployment
    let e2 := pos a2.wages + pos a2.selfEmployment
    let earned := if m then e1 + e2 else (if claimant == 0 then e1 else e2)
    let tot := if m then earned + pos a1.pension + pos a2.pension + c.interest + c.dividends + c.rentalIncome
      else earned + (if claimant == 0 then pos a1.pension + inv1 else pos a2.pension + inv2)
    let nChild := (c.children.filter (fun k => k.age ≤ dependentChildMaxAge)).length
    let kind : Nat :=
      if m then (if e1 ≥ dualEarnerMin ∧ e2 ≥ dualEarnerMin then 2 else 1)
      else (if nChild > 0 then 1 else 0)
    let e := if incentives then eitc kind earned tot (c.year : Int) else 0
    let k := if incentives then ctc kind nChild earned tot (childCreditUsed o1 + childCreditUsed o2) (c.year : Int) else 0
    { persons := [(p1, o1), (p2, o2)], eitc := e, ctc := k, kind, earnedTotal := earned, totalIncome := tot,
      childAllowance := childBenefits c }

/-- National tax of the household (결정세액 + 분리과세 withholding − 장려금). -/
def HhOut.incomeTax (h : HhOut) : Int :=
  (h.persons.map (fun (_, o) => o.determined + o.sepTax)).foldl (· + ·) 0 - h.eitc - h.ctc
def HhOut.localTax (h : HhOut) : Int := (h.persons.map (fun (_, o) => localIncomeTax o)).foldl (· + ·) 0
def HhOut.social (h : HhOut) : Int := (h.persons.map (fun (_, o) => o.soc.total)).foldl (· + ·) 0
def HhOut.net (h : HhOut) (gross : Int) : Int := gross - h.incomeTax - h.localTax - h.social + h.childAllowance

end KrTax
