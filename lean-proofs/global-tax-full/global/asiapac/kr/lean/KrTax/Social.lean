import KrTax.Basic

/-!
# Employee social insurance, 2025 (사업장가입자 / 직장가입자, employee share)

Annual amounts from annual wages at the statutory rates (the OECD's convention); simplifications, stated:
* 국민연금 (NPA §88③: 4.5 %) on the 기준소득월액 = monthly wage cut to the 1,000 won (국민연금법 시행령 §5①)
  within the floor and ceiling of each July–June period (2025: 6 months of each). Members aged 60+ do not
  contribute (국민연금법 §8: 18세 이상 60세 미만). Not modelled: mid-year revaluation, 10-won truncation of monthly bills.
* 건강보험 3.545 % (half of 7.09 %, NHID §44①), 장기요양 0.4591 % (half of 0.9182 %, LTCD §4), 고용보험 0.9 % (half of
  1.8 %, EIPD §12①2). Not modelled: the health premium's upper limit (보수월액보험료 상한, binding only above about
  127 million won a month), monthly 10-won truncation.
* 지역가입자 (self-employed, no wages): 국민연금 9 % (NPA §88④) of business income within the ceilings; 건강보험 7.09 %
  + 장기요양 0.9182 % of business income (the property part of the 지역 premium is not modelled).
-/

namespace KrTax
open TaxKernel

/-- 기준소득월액 for one period: the monthly wage cut to the 1,000 won, within `[lo, hi]`. -/
def pensionBase (lo hi monthly : Int) : Int := clamp lo hi (floorTo 1000 monthly)

/-- Employee 국민연금 for the year: six months at each period's base. -/
def pensionEmployee (age : Nat) (wages : Int) (y : Int := 2025) : Int :=
  if wages ≤ 0 ∨ age ≥ 60 ∨ age < 18 then 0
  else
    let m := wages / 12
    let ((f1, c1), (f2, c2)) := pensionLimitsY y
    6 * mulDiv (pensionBase f1 c1 m) pensionRatePermille 1000
      + 6 * mulDiv (pensionBase f2 c2 m) pensionRatePermille 1000

def healthEmployee (wages : Int) : Int := mulDiv (pos wages) healthRateTotal 20000
def ltcEmployee (wages : Int) : Int := mulDiv (pos wages) ltcRatePpm 2000000
def employmentEmployee (wages : Int) : Int := mulDiv (pos wages) empRatePermille 2000

/-- Tax years 2022–2023 (tests round 5). 국민건강보험법 시행령 §44①: "1만분의 699" in the version in force from
2022-01-01 (대통령령 제32190호, `refs/lawgo/국민건강보험법시행령_32190_ef20220101.txt`) and "1만분의 709" from 2023-01-01
(제33128호; also the display of 제32293호). 노인장기요양보험법 시행령 §4: 2022 "장기요양보험료율은 1만분의 1,227" — then a
rate on the 건강보험료 (제32236호, efYd 2022-01-01) — and 2023 "100만분의 9,082" of the 보수 (제33100호, efYd 2023-01-01). 고용보험료
징수법 시행령 §12①2 "1천분의 18" from 2022-07-01 (대통령령 제32302호 부칙 제1조 단서, "2022년 7월 1일부터 시행"); "1천분의 16"
before: the same decree (제32302호, 2021. 12. 31.) as in force on 2022-01-01 (lsiSeq 238669, efYd 20220101, round 8;
`refs/lawgo/고용보험_및_산업재해보상보험의_보험료징수_등에_관한_법률_시행령_32302.txt`): §12①2 "실업급여의 보험료율: 1천분의
16"; 부칙 제2조 applies the new rate from the monthly premium of July 2022. -/
def healthEmployeeY (y : Int) (wages : Int) : Int :=
  if y = 2022 then mulDiv (pos wages) 699 20000 else healthEmployee wages
def ltcEmployeeY (y : Int) (wages : Int) : Int :=
  if y = 2022 then mulDiv (healthEmployeeY 2022 wages) 1227 10000 else if y = 2023 then mulDiv (pos wages) 9082 2000000
  else ltcEmployee wages
def employmentEmployeeY (y : Int) (wages : Int) : Int :=
  if y = 2022 then mulDiv (pos wages) 16 4000 + mulDiv (pos wages) 18 4000 else employmentEmployee wages

/-- Self-employed (지역가입자) 국민연금: 9 % of business income within the year's ceilings. -/
def pensionSelf (age : Nat) (biz : Int) : Int :=
  if biz ≤ 0 ∨ age ≥ 60 ∨ age < 18 then 0
  else
    let m := biz / 12
    6 * mulDiv (pensionBase pensionFloorH1 pensionCeilH1 m) (2 * pensionRatePermille) 1000
      + 6 * mulDiv (pensionBase pensionFloorH2 pensionCeilH2 m) (2 * pensionRatePermille) 1000

def healthSelf (biz : Int) : Int := mulDiv (pos biz) healthRateTotal 10000 + mulDiv (pos biz) ltcRatePpm 1000000

structure SocialOut where
  pension : Int
  health : Int
  ltc : Int
  employment : Int
  /-- 직장가입자 보수 외 소득월액보험료 (국민건강보험법 §71①, 시행령 §41④: other income above 연간 2천만원, at the
  full 7.09 % + 장기요양 0.9182 %; charged later from the tax records, counted here in the year earned) -/
  healthOther : Int := 0
  deriving Repr

def SocialOut.total (s : SocialOut) : Int := s.pension + s.health + s.ltc + s.employment + s.healthOther

/-- The income NHI counts besides wages (국민건강보험법 시행규칙 §44 (current text): 이자·배당 only when their total
exceeds 1천만원, then in full; 사업소득 in full; 연금 at 100분의 50 (§44②2)). -/
def nhiOtherIncome (biz pension fin : Int) : Int :=
  pos biz + pos pension / 2 + (if fin > 10000000 then fin else 0)

/-- 보수 외 소득월액보험료 of an employee on other income `x` above 연간 2천만원 (국민건강보험법 §71①, 시행령 §41④). -/
def healthOnOther (x : Int) : Int := mulDiv (pos (x - 20000000)) (healthRateTotal * 100 + ltcRatePpm) 1000000
/-- The premiums deductible under ITA §52① (건강·장기요양·고용, employee share only). -/
def SocialOut.special (s : SocialOut) (employee : Bool) : Int := if employee then s.health + s.ltc + s.employment else 0

def social (age : Nat) (wages biz : Int) (y : Int := 2025) : SocialOut :=
  if wages > 0 then
    { pension := pensionEmployee age wages y, health := healthEmployeeY y wages, ltc := ltcEmployeeY y wages,
      employment := employmentEmployeeY y wages }
  else
    { pension := pensionSelf age biz, health := healthSelf biz, ltc := 0, employment := 0 }

/-- The OECD Taxing Wages convention for Korea (`krConvention = "oecd"`, for validation only): annual wages × rates
with no 1,000-won truncation of the 기준소득월액, the 장기요양 premium at 12.95 % of the health premium (the published
ratio; the statute's is 0.9182/7.09 = 12.9506… %, 노인장기요양보험법 §9①), each premium rounded half up. -/
def socialOecd (age : Nat) (wages : Int) (y : Int := 2025) : SocialOut :=
  let w := pos wages
  let hu (n d : Int) : Int := (2 * n + d) / (2 * d)
  { pension := if wages ≤ 0 ∨ age ≥ 60 ∨ age < 18 then 0
      else hu (45 * (min w (12 * (pensionLimitsY y).1.2) + min w (12 * (pensionLimitsY y).2.2))) 2000,
    -- 2022–2023 (round 5): the same arithmetic with that year's statutory rates (health 3.495 % / 3.545 %; LTC 12.27 % of
    -- health in 2022, 0.4541 % of wages in 2023; employment 0.85 % on average in 2022) — the rule, not a fit
    health := hu (w * (if y = 2022 then 3495 else 3545)) 100000,
    ltc := (if y = 2022 then hu (w * 3495 * 1227) 1000000000 else if y = 2023 then hu (w * 4541) 1000000 else hu (w * 4590775) 1000000000),
    employment := (if y = 2022 then hu (w * 17) 2000 else hu (w * 9) 1000) }

end KrTax
