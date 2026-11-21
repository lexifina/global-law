import GRTax.Calc

/-! # The contract: canonical household in, one output line out (amounts in cents; `Main` writes euros) -/

namespace GRTax
open TaxKernel Lean

/-- Dependent children (art. 11 par. 1(β)): under 18, or 18-24 in education when `gr_childrenInEducation`. -/
def dependants (c : Canon) : Nat :=
  let edu := (c.bool? "gr_childrenInEducation").getD false
  (c.children.filter fun k => k.age < dependantAgeLimit || (edu && k.age < studentAgeLimit)).length

/-- ΚΦΕ art. 28Α par. 2(α): the annual gross minimum wage (14 payments) raised by 10 % for each three-year period
after the second, compounding. Runs only with `gr_minWageMonthly` and `gr_yearsInBusiness` given. -/
def presumedMinimum (c : Canon) : Int :=
  match c.int? "gr_minWageMonthly", c.int? "gr_yearsInBusiness" with
  | some mw, some yrs =>
    let base := eur (14 * mw)
    let steps : Nat := if yrs ≥ 13 then 3 else if yrs ≥ 10 then 2 else if yrs ≥ 7 then 1 else 0
    (List.range steps).foldl (fun a _ => divR .halfUp (a * 11) 10) base
  | _, _ => 0

/-- Which adult (0 or 1) declares the children when the two adults are not married (default the first;
`gr_childrenWith: 2` for the second). -/
def childrenWith (c : Canon) : Nat := if (c.int? "gr_childrenWith").getD 1 = 2 then 1 else 0

def toPersons (c : Canon) : List Person :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 2 then (if i = 0 then half1 x else half2 x) else x
  let kids := dependants c
  let pm := presumedMinimum c
  c.adults.zipIdx.map fun (a, i) =>
    let sfx := if i = 0 then "1" else "2"
    { wages := eur a.wages, pension := eur a.pension, selfEmp := eur a.selfEmployment, age := a.age,
      kids := if n = 2 && !c.married && i ≠ childrenWith c then 0 else kids,
      interest := share (eur c.interest) i, dividends := share (eur c.dividends) i,
      rent := share (eur c.rentalIncome) i, gains := share (eur c.capitalGains) i,
      substantial := (c.bool? "gr_substantialHolding").getD false,
      art5G := (c.bool? ("gr_art5G" ++ sfx)).getD false,
      cardSpent := (c.int? ("gr_cardSpending" ++ sfx)).map eur,
      presumedMin := if a.selfEmployment ≠ 0 then pm else 0,
      publicSector := (c.bool? ("gr_publicSector" ++ sfx)).getD false }

def sumBy (l : List Int) : Int := l.foldl (· + ·) 0

def out (args : List String) (c : Canon) : Out :=
  let year := if c.year < 2022 then 2025 else c.year
  let ps := toPersons c
  let ks := ps.map (personCalc year · (args.contains "--oecd") (args.contains "--eurostat") (args.contains "--euromod"))
  let pk := ps.zip ks
  let s (f : Calc → Int) := sumBy (ks.map f)
  let kids := dependants c
  -- child benefit family: spouses together; an unmarried couple's children belong to the declaring parent alone
  let (parents, fam) : Nat × Int :=
    if c.isCouple && c.married then (2, sumBy (pk.map fun (p, k) => benefitIncome p k))
    else if c.isCouple then
      (1, match pk[childrenWith c]? with | some (p, k) => benefitIncome p k | none => 0)
    else (1, sumBy (pk.map fun (p, k) => benefitIncome p k))
  let ben := childBenefit parents kids fam
  let detail : List (String × Json) :=
    [Out.d "taxableIncome_cents" (s (·.scaleBase)), Out.d "taxBeforeCredits_cents" (s (·.taxScale)),
     Out.d "art16Reduction_cents" (s (·.creditUsed)), Out.d "art16Full_cents" (s (·.creditFull)),
     Out.d "efka_cents" (s (·.efka)), Out.d "rentTax_cents" (s (·.rentTax)), Out.d "dividendTax_cents" (s (·.divTax)),
     Out.d "interestTax_cents" (s (·.intTax)), Out.d "gainTax_cents" (s (·.gainTax)),
     Out.d "art5GExempt_cents" (s (·.exempt5G)), Out.d "dependants" kids, Out.d "year" year,
     Out.d "benefitIncome_cents" fam, Out.d "benefitParents" parents]
    ++ (ks.zipIdx.map fun (k, i) => Out.d s!"mainTax{i+1}_cents" k.mainTax)
  Out.make c "GR" "EUR" (s Calc.incomeTax) (surtaxes := [("cardSpendingPenalty", s (·.cardPenalty)), ("solidarity43A", s (·.solidarity))])
    (employeeSocial := s (·.efka)) (benefits := ben) (detail := detail)
    (unsupported := ["self-employed EFKA contributions (fixed monthly categories, ν. 4387/2016 art. 39)",
      "presumptive living-expense income (τεκμήρια, arts. 31-34)", "art. 28Α minimum unless gr_minWageMonthly given",
      "deductions and credits needing receipts (art. 18 medical, art. 19 donations)", "ΕΝΦΙΑ and other property taxes",
      "pensioners' health contribution (6 %)", "art. 5Α / 5Β foreign-income regimes (no foreign income in the contract)",
      "employee contribution split by branch (only the 13.37 % total is modelled)"] ++
      (if year = 2022 && args.contains "--euromod" then ["--euromod: EUROMOD 30 June convention, not statute (EFKA 13.87 % for the whole of 2022)"] else []) ++
      (if year = 2022 then ["2022: EFKA 14.12 % on 5.5 of 14 instalments (Jan-May + Easter bonus), 13.87 % on the rest; art. 43Α on pensions and on wages flagged gr_publicSector1/2 only (art. 72 par. 74), on their own scale; the 2022 ceiling of insurable earnings is 6,500 € a month (ν. 4387/2016 art. 38 par. 2 as quoted in e-ΕΦΚΑ Εγκύκλιος 8/2024)"] else []))

def country : Country :=
  { code := "GR", name := "Greece", currency := "EUR", year := "2025", compute := out [], computeWith := out }

end GRTax
