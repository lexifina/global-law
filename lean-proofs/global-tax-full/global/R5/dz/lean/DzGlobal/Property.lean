import TaxKernel.Global
import R5Common

/-!
# Algeria 2025: taxe foncière sur les propriétés bâties (4100)

Code des impôts directs et taxes assimilées (CIDTA), DGI edition 2025 in Arabic (`law/dgi_cidta_2025_ar.pdf`, pp. 72-73
read on the page images) and the 2023 French edition (`law/dgi_cidta_2023_fr.pdf`) for the wording:
* art. 248: annual tax on built properties; art. 254: base = valeur locative fiscale per m² × taxable area; for dwellings
  an abatement of 2 % a year for age, at most 25 %; art. 256: the value is weighted by zone and sub-zone coefficients
  fixed by joint order (not read: coefficient taken as 1).
* art. 257 (as amended by LF 2022 art. 61): valeur locative fiscale: dwellings 520 DA per m², commercial and industrial
  premises 1 038 DA, land forming a dependency of built property 14 DA (urbanised) / 12 DA (to be urbanised).
* art. 261-b (as amended by LF 2022 art. 63 and LF 2025 art. 20): rate 3 % for built properties; 10 % for secondary
  dwellings of natural persons, unoccupied and not let (flag not modelled); dependencies 5 / 7 / 10 % by area.
* art. 252: exemptions (incl. the single dwelling of owners with an annual tax up to 1 400 DA and income limits; new
  buildings for their first years) not applied.
Inputs: `home` (dwelling) and `realEstate` (commercial) assets with `"areaM2"`; age abatement not applied (no age input).
**Grade A** (statute read; zone coefficient and abatement not applied).
-/

namespace DzGlobal
open TaxKernel TaxKernel.Global R5Common

/-- art. 257 × 3 % (art. 261-b), centimes per m²: dwellings 520 DA × 3 % = 15.60 DA; commercial 1 038 DA × 3 % = 31.14 DA. -/
def tfRateC (dwelling : Bool) : Int := if dwelling then 1560 else 3114

def tfTax (dwelling : Bool) (area : Int) : Int := divR .down (pos area * tfRateC dwelling) 100

def tfArea (g : CanonGlobal) (i : Nat) : Int := intField ((arrField g.raw "assets").toList.getD i Lean.Json.null) "areaM2"

def property : Family :=
  { name := "4100 الرسم العقاري على الملكيات المبنية (taxe foncière)", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      (g.assets.zipIdx.filter fun (a, i) => (a.kind == .home || a.kind == .realEstate) && tfArea g i > 0).map fun (a, i) =>
        charge .propertyRecurrent "الرسم العقاري" (tfArea g i) pos (tfTax (a.kind == .home)) (event := s!"property {i + 1}")
          (level := .local) (statute := s!"CIDTA art. 254, 257 ({if a.kind == .home then "520" else "1 038"} DA per m²), 261-b (3 %)") }

def propertyUnsupported (g : CanonGlobal) : List String :=
  if g.assets.any (fun a => a.kind.isRealEstate) then
    ["taxe foncière: needs asset areaM2; zone coefficient taken as 1, age abatement (2 %/year, max 25 %), art. 252 exemptions, the 10 % rate on unoccupied secondary homes, land dependencies and unbuilt land not applied"]
  else []

#guard tfTax true 100 == 1560
#guard tfTax false 100 == 3114

end DzGlobal
