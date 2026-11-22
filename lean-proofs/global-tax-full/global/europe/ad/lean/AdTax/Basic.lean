import AdTax.Params

/-!
# Andorra 2025: IRPF (10 % with a 24 000 € personal minimum and a 50 % bonus up to 40 000 €), CASS contributions

Unit: the individual (each obligat tributari); a spouse with no income lets the other use up to 40 000 € (art. 35.1;
when the spouse has some income, the unused part of the spouse's 24 000 € passes to the other up to 16 000 €: reading
of the third paragraph of art. 35.1). Child reductions shared equally between parents with income (art. 35.3).
Work income: gross pay less the employee's CASS contributions and 3 % other expenses (max 2 500 €) (art. 13).
Savings income (interest, dividends, capital gains) forms the savings base, less 3 000 € (art. 39), at 10 %; the
household's savings income is split equally between two adults (reading).
Tax: 10 % of each base (art. 41-42), less the bonus of art. 46 on the general base, not below 0 (art. 47).
-/

namespace AdTax
open TaxKernel

/-- Employee CASS: general branch (art. 100.1 as replaced by Llei 2/2016 DF 6a: 3 %; `old`: Llei 18/2014's 2 %) +
retirement branch 3,5 %. -/
def cass (old : Bool) (w : Int) : Int :=
  if w ≤ 0 then 0 else divR .halfUp (w * ((if old then cassGeneral2014 else cassGeneral) + cassRetirement)) BP

#guard cass false 40000 = 2600 ∧ cass true 40000 = 2200

def workNet (old : Bool) (w : Int) : Int :=
  if w ≤ 0 then 0 else pos (w - cass old w - min otherExpCap (divR .halfUp (w * otherExpRate) BP))

def tenPct (x : Int) : Int := divR .halfUp (pos x * rate) BP

structure Person where
  general : Int
  reductions : Int
  quota : Int
  bonus : Int
  savingsTax : Int
  tax : Int

/-- Quota, bonus and savings tax are computed in cents (the euro amounts of arts. 41-47 carry cents; no rounding rule
in the law) and the household's tax is rounded half-up to the euro once, at the end (round 2 fix of FINDINGS F4). -/
def tenPctC (x : Int) : Int := divR .halfUp (pos x * 100 * rate) BP

def person (general reductions savings : Int) : Person :=
  let quotaC := tenPctC (general - reductions)
  let bonusC := min (bonusCap * 100) (divR .halfUp (pos (general - personalMin) * 100 * rate * bonusShare) (BP * BP))
  let stC := tenPctC (savings - savingsMin)
  { general, reductions, quota := divR .halfUp quotaC 100, bonus := divR .halfUp bonusC 100,
    savingsTax := divR .halfUp stC 100, tax := pos (quotaC - bonusC) + stC }

def out (c : Canon) : Out :=
  let as := c.adults
  let old := (c.bool? "adCassGeneral2014").getD false
  let gens := as.map fun a => workNet old a.wages + pos a.selfEmployment
  let n := as.length
  let kids : Int := c.childrenUnder childAge
  let earners := (gens.filter (· > 0)).length
  let savings := pos c.interest + pos c.dividends + pos c.capitalGains
  let red := fun (i : Nat) =>
    let own := gens.getD i 0
    let other := gens.getD (1 - i) 0
    let transfer := if c.married && n == 2 && own > 0 then min (couplePersonalMin - personalMin) (pos (personalMin - other)) else 0
    let kidRed := if own ≤ 0 then 0 else if earners == 2 then (if i == 0 then half1 (kids * childReduction) else half2 (kids * childReduction)) else kids * childReduction
    personalMin + transfer + kidRed
  let ps := (gens.zipIdx).map fun (g, i) =>
    person g (red i) (if n == 2 then (if i == 0 then half1 savings else half2 savings) else savings)
  let tax := divR .halfUp (sumInts (ps.map (·.tax))) 100
  let unsup :=
    (if c.rentalIncome != 0 then ["rentalIncome: capital immobiliari (arts. 20-21, art. 21.2 replaced by Llei 5/2023 and Llei 5/2025) not modelled"] else []) ++
    (if c.dividends != 0 then ["dividends: put in the savings base; the exemptions of art. 5 for some dividends were not checked"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taken as net income of an activity (arts. 14-17); CASS for the self-employed not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: treatment of pensions (art. 12.2) not modelled"] else []) ++
    (if c.charitable != 0 || c.pensionContributions != 0 then ["charitable/pensionContributions: reductions of arts. 38-39 not modelled"] else [])
  Out.make c "AD" "EUR" tax (employeeSocial := sumInts (as.map fun a => cass old a.wages))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map fun p => pos (p.general - p.reductions))),
                Out.d "quotaGeneral" (sumInts (ps.map (·.quota))), Out.d "bonusArt46" (sumInts (ps.map (·.bonus))),
                Out.d "savingsTax" (sumInts (ps.map (·.savingsTax))),
                Out.dStr "note" "IRPF Llei 5/2014: 10 % above 24 000 € (40 000 € with a spouse without income), 50 % bonus up to 800 €; CASS 3 % + 3,5 % (Llei 17/2008 arts. 100, 103 as replaced by Llei 2/2016 DF 6a and Llei 18/2014 art. 29)"])
    (unsupported := unsup)

def country : Country :=
  { code := "AD", name := "Andorra (IRPF, CASS)", currency := "EUR", year := "2025", compute := out }

end AdTax
