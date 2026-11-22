import MmGlobal.Pit

/-!
# Myanmar 2025: employer social security contribution (2200)
Secondary-source sweep, grade B (guide facts, the Social Security Law 2012 and its notifications not read):
PwC Worldwide Tax Summaries, Myanmar, Individual - Other taxes, last reviewed 3 June 2025 (Wayback capture 2025-11-08, asiapac/mm/law/pwc_mm_indother_wb20251108.txt), section on social security: the employer pays 3 % and the employee 2 % of wages; since 1 April 2014 the
employer's part is at most MMK 9,000 a month, i.e. 3 % of a MMK 300,000 monthly wage (MMK 3,600,000 a year).
The scheme covers employers with more than five workers: the input does not give the employer's headcount, so every wage
earner is charged (flagged).
-/

namespace MmGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Social security contribution (employer 3 %, wage base capped at MMK 300,000 a month)" a.wages (fun w => min (pos w) 3600000) (fun b => divR .down (300 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Social Security Law 2012 (not read); rate and MMK 9,000 monthly maximum from PwC Worldwide Tax Summaries, Myanmar, Individual - Other taxes, last reviewed 3 June 2025 (Wayback capture 2025-11-08, asiapac/mm/law/pwc_mm_indother_wb20251108.txt)")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => a.wages > 0) then ["2200 Myanmar social security: applies to employers with more than five workers; the employer's size is not an input, so every wage is charged (B, PwC 2025)"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ age := 40, wages := 2400000 }] } } []).map (·.due) == [72000]
#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ age := 40, wages := 6000000 }] } } []).map (·.due) == [108000]

end MmGlobal.Social
