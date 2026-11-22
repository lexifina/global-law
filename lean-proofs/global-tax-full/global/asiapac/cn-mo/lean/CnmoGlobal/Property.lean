import CnmoGlobal.Pit

/-!
# Macau SAR 2025: urban property tax (Contribuição Predial Urbana, 4100)
Secondary-source sweep, grade B (guide facts; Lei n.º 19/78/M and the 2025 Budget Law not read): PwC Worldwide Tax Summaries, Macau SAR, Corporate - Other taxes, property tax section, last reviewed 9 June 2025 (Wayback capture 2025-10-11, asiapac/cn-mo/law/pwc_mo_corpother_wb20251011.txt):
* a building used by its owner: 6 % of the official ratable value fixed by the Finance Services committee, after an automatic
  10 % allowance for repairs (so 5.4 % of that value);
* a let building: 10 % of the actual rent, cut to 8 % for tax year 2025 by the 2025 Budget (a 10 % repairs allowance is
  given only on application: not applied);
* the 2025 Budget reduces each 2025 assessment by MOP 3,500 (not for companies or non-residents).
Model: a home's `annualValue` is read as its official ratable value; a `realEstate` asset's `annualValue` as the rent it earns
in the year. Charge per asset, reduced by MOP 3,500 and floored at 0; companies are not given the reduction. An asset
without `annualValue`: no charge, listed (grade C). The exemption periods for new buildings (by location) are not modelled.
-/

namespace CnmoGlobal.Property
open TaxKernel TaxKernel.Global

def moReduction (g : CanonGlobal) : Int := if g.entity == .company then 0 else 3500
/-- Contribuição Predial Urbana 2025: self-use 6 % of 90 % of the ratable value; let 8 % of the rent; less MOP 3,500 per assessment. -/
def cpuF : Family :=
  { name := "4100 Contribuição Predial Urbana (2025)", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      (g.assets.zipIdx.filter fun (x, _) => (x.kind == .home || x.kind == .realEstate) && x.annualValue ≥ 0).map fun (x, k) =>
        let gross := if x.kind == .home then divR .down (6 * (x.annualValue - divR .down x.annualValue 10)) 100
                     else divR .down (8 * x.annualValue) 100
        charge .propertyRecurrent (if x.kind == .home then "Urban property tax, own use (6 % of 90 % of the ratable value, less MOP 3,500)" else "Urban property tax, let (8 % of the rent in 2025, less MOP 3,500)")
          gross id (fun b => max 0 (b - moReduction g))
          (event := s!"asset {k + 1}") (level := .central)
          (statute := "Lei n.º 19/78/M (Regulamento da Contribuição Predial Urbana) and Budget Law 2025 (not read); rates, allowance and MOP 3,500 reduction from PwC WWTS Macau SAR, Corporate - Other taxes (reviewed 9 June 2025)") }

def families : List Family := [cpuF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun x => (x.kind == .home || x.kind == .realEstate) && x.annualValue < 0) then ["4100 Macau SAR urban property tax: a building without annualValue (ratable value or rent) is not charged (grade C)"] else [])
  ++ (if g.assets.any (fun x => x.kind == .home || x.kind == .realEstate) then ["4100 Macau SAR urban property tax: exemption periods for new buildings, the repairs allowance on let property (on application) and the non-resident exclusion from the MOP 3,500 reduction not modelled"] else [])

#guard (cpuF.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 5000000, annualValue := 200000 }] } []).map (·.due) == [7300]
#guard (cpuF.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .realEstate, value := 5000000, annualValue := 240000 }] } []).map (·.due) == [15700]
#guard (cpuF.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 5000000, annualValue := 50000 }] } []).map (·.due) == [0]

end CnmoGlobal.Property
