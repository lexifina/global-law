import BtGlobal.Pit

/-!
# Bhutan 2025: land tax and building tax (4100)
Source: Property Tax Act of Bhutan 2022, read in lexifina/bhutan-law `act/2022/property-tax-act-of-bhutan` (official source oag.gov.bt/wp-content/uploads/2026/08/Property-Tax-Act-of-Bhutan-2022.pdf). In force 1 January 2023 (s. 2); one version, no amending act in the repository.
* **s. 8**: "Land tax is payable each year on all land at the rate of 0.1% on the taxable land value"; s. 59 (11): the value
  from the compensation rate published by the PAVA (Property Assessment and Valuation Agency) as at the payment deadline.
* **s. 11**: "Building tax is payable each year on all buildings at the rate of 0.1% on the taxable building value";
  s. 59 (10) and Schedule 1: the assessed capital value, 12.5 × the annual rental value for freehold (10 or 8 for leasehold).
* s. 5: the revenue goes to the Government Revenue Account (central); s. 6: no other tax on immovable property.
* Not modelled: the vacant land tax (s. 16: 15 % of the land tax, Schedule 2 towns, undeveloped serviced land), the
  concessions (ss. 19-23: Chhuzhing 90 %, Kamzhing 50 %, highland 90 %, traditional houses up to 50 % / 70 %).
Both taxes are 0.1 %, so the charge is 0.1 % of the asset's `assessed` value, taken as its taxable land value plus taxable
building value. An asset without `assessed` is listed (grade C): the market value is not the statute's value.
-/

namespace BtGlobal.Property
open TaxKernel TaxKernel.Global

/-- Property Tax Act of Bhutan 2022 ss. 8, 11: 0.1 % of the taxable land value plus 0.1 % of the taxable building value. -/
def propF : Family :=
  { name := "4100 land tax and building tax (Property Tax Act 2022)", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      (g.assets.zipIdx.filter fun (a, _) => [AssetKind.home, .realEstate, .land].contains a.kind && a.assessed ≥ 0).map fun (a, k) =>
        charge .propertyRecurrent "Land tax and building tax (0.1 % each)" a.assessed id (fun b => divR .down (10 * b) BP)
          (event := s!"asset {k + 1}") (level := .central)
          (statute := "Property Tax Act of Bhutan 2022 ss. 8, 11, 59 (10)-(11), Schedule 1") }

def families : List Family := [propF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => [AssetKind.home, .realEstate, .land].contains a.kind && a.assessed < 0) then ["4100 land tax and building tax (Property Tax Act 2022 ss. 8, 11: 0.1 % of the PAVA land value and of the Schedule 1 building value): an immovable asset without its taxable value (the assessed field): not booked (grade C)"] else [])
  ++ (if g.assets.any (fun a => a.kind == .land) then ["4100 vacant land tax (s. 16: 15 % of the land tax on undeveloped serviced land in the Schedule 2 towns) and the concessions (ss. 19-23) not modelled"] else [])

#guard (propF.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .land, value := 5000000, assessed := 2000000 }] } []).map (·.due) == [2000]
#guard (propF.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 9000000, assessed := 8000000 }] } []).map (·.due) == [8000]
#guard (propF.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 9000000, assessed := -1 }] } []).map (·.due) == []

end BtGlobal.Property
