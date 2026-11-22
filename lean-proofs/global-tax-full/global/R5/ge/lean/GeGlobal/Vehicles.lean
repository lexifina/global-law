import TaxKernel.Global2
import R5Common
import GeGlobal.Property

/-!
# Georgia 2025: property tax of natural persons on motor cars (Code 8703), shown under 5200

Tax Code of Georgia, official English consolidation on matsne.gov.ge (document 1043717), Wayback capture of 21/12/2025
(`law/matsne_1043717_en_full_cap20251221.txt`; art. 201 last amended by Law 6817 of 14/07/2020, art. 202 by Law 6817 of
14/07/2020: the text in force throughout 2025):
* art. 201(1)(c.a): a natural person pays property tax "on a real estate …, yachts (cutters), helicopters, airplanes,
  and motor cars specified under Code 8703 of the National Commodity Nomenclature of Foreign Economic Activities that
  are owned by him/her" (the owner is liable);
* art. 202(5): rate by the family's income of the tax year: up to GEL 100 000 at least 0.05 % and not more than 0.2 %,
  GEL 100 000 and more at least 0.8 % and not more than 1 %, "of the market value of the taxable property at the end of
  the tax year"; (6)-(7) family income;
* art. 202(9): "calculated in proportion to the time he/she owned the property during the tax period";
* art. 206(1)(a): exempt "a natural person's taxable property (except land) if the person's family income received
  during the year preceding the tax year does not exceed GEL 40 000".
Same rate assumptions as the 4100 module (`GeGlobal.Property`): the municipal rate taken at the band maximum, this
year's family income for the exemption. Input: a vehicle asset of `vehicleKind` "car" (Code 8703: passenger cars),
`value` = market value at the end of 2025, `months` held. Motorcycles (8711), goods vehicles (8704) are not taxable
objects of art. 201(1)(c.a) (cited zero: no charge). Enterprises' cars are within their fixed assets (art. 202(1)),
not computed. **Grade B** (statute read; municipal rate and prior-year income assumptions).
-/

namespace GeGlobal
open TaxKernel TaxKernel.Global R5Common

/-- art. 202(5) band maximum on the value, × months owned / 12 (art. 202(9)). -/
def carPropTax (income : Int) (months : Nat) (value : Int) : Int :=
  divR .down (propTax income value * (months : Int)) 12

def vehicles : Family :=
  { name := "5200 ქონების გადასახადი ავტომობილზე (property tax on motor cars)", covers := [.useOfGoods],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      let y := familyIncome g
      (g.vehicles.zipIdx.filter fun (v, _) => v.kind == "car" && v.value ≥ 0).map fun (v, k) =>
        charge .useOfGoods "ქონების გადასახადი (motor car, Code 8703)" v.value pos (carPropTax y v.months)
          (event := s!"vehicle {k + 1} ({v.source})")
          (statute := s!"Tax Code art. 201(1)(c.a), 202(5) (maximum {propRateBp y} bp), 202(9) ({v.months}/12), 206(1)(a) (exempt to GEL 40 000)") }

def vehiclesUnsupported (g : CanonGlobal) : List String :=
  (if g.entity == .company && !g.vehicles.isEmpty then ["company cars: enterprise property tax on fixed assets (art. 202(1)) not computed"] else [])
  ++ ((g.vehicles.zipIdx.filter fun (v, _) => g.entity != .company && v.kind == "car" && v.value < 0).map fun (_, k) =>
      s!"5200 property tax on motor cars: vehicle {k + 1}: value not given (grade C)")
  ++ (if g.entity != .company && g.vehicles.any (·.kind == "car") then
      ["property tax on motor cars: municipal rate taken at the art. 202(5) maximum (0.2 % / 1 %); the exemption test uses this year's family income"] else [])

#guard carPropTax 120000 12 50000 == 500
#guard carPropTax 120000 6 30000 == 150
#guard carPropTax 60000 12 50000 == 100
#guard carPropTax 40000 12 50000 == 0

end GeGlobal
