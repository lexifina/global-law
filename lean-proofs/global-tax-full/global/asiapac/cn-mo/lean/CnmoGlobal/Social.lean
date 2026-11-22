import CnmoGlobal.Pit

/-!
# Macau SAR 2025: Social Security Fund contribution, employer part (2200)
Secondary-source sweep, grade B (guide facts; Lei n.º 4/2010 not read): PwC Worldwide Tax Summaries, Macau SAR, Individual - Other taxes, last reviewed 9 June 2025 (Wayback capture 2025-12-15, asiapac/cn-mo/law/pwc_mo_indother_wb20251215.txt): a fixed MOP 90 a month is paid for
each resident employee, two thirds (MOP 60) by the employer and one third by the employee. Modelled as MOP 60 x 12 = MOP 720 a
year from the employer for each adult with wages. Non-resident workers (a different fixed levy) and part-time rates are not
distinguished: every wage earner is taken as a full-time resident employee (flagged).
-/

namespace CnmoGlobal.Social
open TaxKernel TaxKernel.Global

/-- Macau SAR Social Security Fund: MOP 60 a month (employer two thirds of MOP 90) per resident employee, MOP 720 a year. -/
def ssfF : Family :=
  { name := "2200 Social Security Fund contribution (employer MOP 60 a month)", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (_, k) =>
        charge .sscEmployer "Social Security Fund contribution (employer, MOP 60 a month)" 720 id id
          (event := s!"adult {k + 1}") (level := .social) (bearer := .employer)
          (statute := "Lei n.º 4/2010 (not read); MOP 90 a month per resident employee, employer two thirds, from PwC WWTS Macau SAR, Individual - Other taxes (reviewed 9 June 2025)") }

def families : List Family := [ssfF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => a.wages > 0) then ["2200 Macau SAR Social Security Fund: each wage earner taken as a full-time resident employee (part-time and non-resident workers' amounts not modelled)"] else [])

#guard (ssfF.run [] { id := "t", household := { id := "t", adults := [{ age := 40, wages := 300000 }] } } []).map (·.due) == [720]
#guard (ssfF.run [] { id := "t", household := { id := "t", adults := [{ age := 40, wages := 0 }] } } []).map (·.due) == []

end CnmoGlobal.Social
