import TaxKernel.Global
import R5Common

/-!
# Georgia 2025: property tax of natural persons on buildings (4100)

Tax Code of Georgia, official English consolidation on matsne.gov.ge (document 1043717, publication 99), read from the
Wayback capture of 21/12/2025 (`law/matsne_1043717_en_art200-206.txt`):
* art. 201(1)(c.a): a natural person pays property tax on any real estate (incl. unfinished construction, buildings or
  their parts), yachts, helicopters and airplanes owned.
* art. 202(5): "The annual tax rate on taxable property of a natural person shall be differentiated according to income
  earned by the taxpayer's family during the tax year": (a) family income up to GEL 100 000: at least 0.05 % but not
  more than 0.2 % of the market value at the end of the tax year; (b) GEL 100 000 and more: at least 0.8 % but not more
  than 1 %. (6)-(7): family income = all income incl. gross salary, economic activity, other income.
* art. 206(1)(a): exempt "a natural person's taxable property (except land) if the person's family income received during
  the year preceding the tax year does not exceed GEL 40 000".
The rate inside each band is set by the municipality (local council decision): the statutory maximum (0.2 % / 1 %) is
used, the municipal decisions are not read. Family income is the household's income of the year (the exemption looks at
the preceding year: taken equal). Assets: `home` and `realEstate` at market value; land (art. 203-204, per-hectare and
per-m² rates) and enterprises' property (art. 202(1): up to 1 % of average net book value) are not computed.
**Grade B** (statute read; municipal rate and prior-year income assumptions).

Pass 3h: land tax (property tax on land), art. 203 (payer: the possessor of land on 1 April), art. 204(2): non-agricultural
land "the basic tax rate shall be fixed at GEL 0.24 per m2 of land per year", multiplied by a territorial coefficient set
by the local council, "not exceed 1.5": taken at the maximum, GEL 0.36 per m². The art. 206(1)(a) income exemption
excludes land ("except land"). Agricultural land (art. 204(1): GEL per ha by municipality and land category) is not
computed. Input: land asset `"areaM2"`. Same Wayback capture (`law/matsne_1043717_en_art200-206.txt`).
-/

namespace GeGlobal
open TaxKernel TaxKernel.Global R5Common

def familyIncome (g : CanonGlobal) : Int :=
  let h := g.household
  isum (h.adults.map fun a => a.wages + a.selfEmployment + a.pension)
    + h.interest + h.dividends + h.rentalIncome + h.capitalGains + isum (g.incomes.map (·.amount))

/-- art. 202(5) band maximum (bp) by family income; 0 when exempt under art. 206(1)(a). -/
def propRateBp (income : Int) : Int :=
  if income ≤ 40000 then 0 else if income < 100000 then 20 else 100

def propTax (income value : Int) : Int := divR .down (pos value * propRateBp income) BP

/-- art. 204(2): GEL 0.24 per m² × coefficient 1.5 (maximum), in tetri then down to GEL. -/
def landTaxM2 (area : Int) : Int := divR .down (pos area * 36) 100

def landAreaOf (g : CanonGlobal) (i : Nat) : Int := intField ((arrField g.raw "assets").toList.getD i Lean.Json.null) "areaM2"

def landCharges (g : CanonGlobal) : List Charge :=
  (g.assets.zipIdx.filter fun (a, i) => a.kind == .land && landAreaOf g i > 0).map fun (a, i) =>
    charge .propertyRecurrent "ქონების გადასახადი მიწაზე (land tax)" (landAreaOf g i) pos landTaxM2 (event := s!"land {i + 1}")
      (level := .local) (statute := "Tax Code art. 203, 204(2) (GEL 0.24 per m² × territorial coefficient, maximum 1.5)")

def property : Family :=
  { name := "4100 ქონების გადასახადი (property tax)", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      let y := familyIncome g
      ((g.assets.zipIdx.filter fun (a, _) => a.kind == .home || a.kind == .realEstate).map fun (a, i) =>
        charge .propertyRecurrent "ქონების გადასახადი" a.value pos (propTax y) (event := s!"property {i + 1}")
          (statute := s!"Tax Code art. 201(1)(c.a), 202(5) (maximum {propRateBp y} bp), 206(1)(a) (exempt to GEL 40 000)"))
      ++ landCharges g }

def propertyUnsupported (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["enterprise property tax (art. 202(1): up to 1 % of average net book value) not computed"] else [])
  ++ (if g.assets.any (fun a => a.kind == .home || a.kind == .realEstate) then
    ["property tax: municipal rate taken at the art. 202(5) maximum (0.2 % / 1 %); the exemption test uses this year's family income"] else [])
  ++ (if g.assets.any (·.kind == .land) then ["land tax: non-agricultural land at the maximum coefficient (GEL 0.36 per m²) when areaM2 is given; agricultural land (art. 204(1)) not computed"] else [])

#guard propTax 40000 800000 == 0
#guard propTax 60000 800000 == 1600
#guard propTax 120000 800000 == 8000

#guard landTaxM2 600 == 216

end GeGlobal
