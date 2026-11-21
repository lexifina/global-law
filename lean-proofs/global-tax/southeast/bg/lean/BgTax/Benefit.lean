import BgTax.Tax

/-!
# Monthly child allowance (ЗСПД чл. 7, чл. 4а; ЗДБРБ 2025 чл. 64) and the school grants (чл. 10а, 10б)

ЗСПД чл. 4а, ал. 1: the right exists for families "със средномесечен доход на член от семейството за предходните 12
месеца, по-нисък или равен на дохода, определен за целта в закона за държавния бюджет"; ал. 2: two limits, full and
80 %. § 1, т. 2 ДР: "Доход" = "всички брутни доходи на семейството, които са облагаеми по Закона за данъците върху
доходите на физическите лица, както и получаваните пенсии, обезщетения, помощи и стипендии" (except the allowances
themselves). The family is the parents and their children (§ 1, т. 1 ДР).

Static household: the 12 months before each month are taken to have the year's income (steady state). The test is
an **all-or-nothing notch** at each limit: one stotinka of income per member above 860 лв. removes the whole
allowance (ЗДБРБ 2025 чл. 64, ал. 2-5); there is no taper.

Children: the canonical `age` is read as the age on 1 January 2025. Allowance: children under 18 (ЗСПД чл. 7, ал. 1
pays "до завършване на средно образование, но не повече от 20-годишна възраст"; pupils of 18-19 are not modelled).
School grants: grades 1-4 are the children who turn 7-10 in 2025 (age 6-9 on 1 January; ЗПУО чл. 12: first grade in
the year the child turns 7), grade 8 the children who turn 14 (age 13).
-/

namespace BgTax
open TaxKernel

/-- Monthly allowance of month `m` for `n` children and a family income per member per month `pm` (stotinki). -/
def allowanceMonth (n : Nat) (pm : Int) (m : Nat) : Int :=
  if pm ≤ allowanceFullLimit m then allowanceFull n
  else if pm ≤ allowancePartLimit m then stRound.ofTicks (allowancePartRate * allowanceFull n)
  else 0

/-- The year's allowance for annual family income `inc` (stotinki), `members` members and `n` children. The test
`inc / 12 / members ≤ limit` is evaluated exactly as `inc ≤ 12 · members · limit`. -/
def allowanceYear (n members : Nat) (inc : Int) : Int :=
  if n = 0 || members = 0 then 0 else
  months.foldl (fun a m =>
    let full := allowanceFullLimit m * 12 * (members : Int)
    let part := allowancePartLimit m * 12 * (members : Int)
    a + (if inc ≤ full then allowanceFull n
         else if inc ≤ part then stRound.ofTicks (allowancePartRate * allowanceFull n) else 0)) 0

/-- Children who turn 7-10 or 14 in 2025 (school grants of ЗСПД чл. 10а, 10б). -/
def schoolGrantChildren (ages : List Nat) : Nat :=
  (ages.filter fun a => (6 ≤ a && a ≤ 9) || a == 13).length

/-- `allowanceYear` for tax year `y` (limits and amounts of that year's budget act; 2025 and later: `allowanceYear`). -/
def allowanceYearY (y n members : Nat) (inc : Int) : Int :=
  if y ≥ 2025 then allowanceYear n members inc else
  if n = 0 || members = 0 then 0 else
  months.foldl (fun a m =>
    let full := allowanceFullLimitY y m * 12 * (members : Int)
    let part := allowancePartLimitY y m * 12 * (members : Int)
    a + (if inc ≤ full then allowanceFullY y m n
         else if inc ≤ part then stRound.ofTicks (allowancePartRate * allowanceFullY y m n) else 0)) 0

/-- EUROMOD convention (`--euromod`, round 15; 30 June rule, see `Social.lean`): the limits and amounts in force in
June (month index 5) for all twelve months (2022: 510 / 610 лв. and 50 / 110 / 165 / 175 лв. from 1 April; 2025:
760 / 860 лв. from 1 April). -/
def allowanceYearJ (y n members : Nat) (inc : Int) : Int :=
  if n = 0 || members = 0 then 0 else
  let full := (if y ≥ 2025 then allowanceFullLimit 5 else allowanceFullLimitY y 5) * 12 * (members : Int)
  let part := (if y ≥ 2025 then allowancePartLimit 5 else allowancePartLimitY y 5) * 12 * (members : Int)
  let amt := if y ≥ 2025 then allowanceFull n else allowanceFullY y 5 n
  12 * (if inc ≤ full then amt else if inc ≤ part then stRound.ofTicks (allowancePartRate * amt) else 0)

/-- School grants of year `y`: in 2022 (ЗСПД чл. 10а before ДВ 102/2022) first grade only (age 6 on 1 January,
turning 7) and grade 8; from 2023 grades 1-4 and grade 8. -/
def schoolGrantChildrenY (y : Nat) (ages : List Nat) : Nat :=
  if y ≤ 2022 then (ages.filter fun a => a == 6 || a == 13).length else schoolGrantChildren ages

/-- Eurostat convention (`--eurostat`, NOT statute; ESMS 3.4: family allowances for children "aged between 6 and 11
years ... If the amounts vary within this age range, the most generous are used"): a child aged 6-11 receives the
grade 1-4 school grant, the most generous annual amount for any age in 6-11 (the monthly allowance does not vary with
age); children of other ages as in statute mode. -/
def schoolGrantChildrenE (y : Nat) (ages : List Nat) : Nat :=
  (ages.filter fun a => 6 ≤ a && a ≤ 11).length +
    schoolGrantChildrenY y (ages.filter fun a => !(6 ≤ a && a ≤ 11))

end BgTax
