import VcGlobal.Pit

/-!
# Saint Vincent and the Grenadines 2025: property tax (4100); stamp and transfer duties grade C

Source: Inland Revenue Department page "Property Tax Rates" (ird.gov.vc, Wayback capture 25 Apr 2025,
`vc/law/ird_property_tax_rates_wb20250425.html`, ARCHIVE_INDEX.tsv; facts paraphrased): the yearly rate is 0.08 % for land and for buildings in
urban districts and for property in purely commercial use, 0.04 % for property in purely agricultural use, for hotels,
guest houses and tourism developments and for manufacturing factories, and a flat $10 a year both for vacant rural land
of under six acres and for property valued at $50,000 or less. A national tax
(Property Tax Act, administered by the IRD). Grade B (official rate page; the Act and the valuation basis were not read:
the asset's statutory value is taken as the value on the roll).
Modelled: 0.08 % of the value of a home, other real estate or land; $10 a year when the value is $50,000 or less. The
0.04 % agricultural, hotel and factory rates need the use of the property (not an input). Stamp duty and the transfer
taxes on real property were not read (C row).
-/

namespace VcGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon VcGlobal

/-- IRD rates: 0.08 % (8 bp) of the value; $10 a year at a value of $50,000 or less. -/
def propTax (v : Int) : Int := if pos v ≤ 50000 then 10 else divR .down (8 * pos v) BP

def propF : Family :=
  { name := "4100 property tax", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      (g.assets.zipIdx.filter fun (a, _) => a.kind.isRealEstate).map fun (a, i) =>
        charge .propertyRecurrent "Property tax" a.statutoryValue id propTax (event := s!"asset {i + 1}") (level := .central)
          (statute := "Property Tax Act (IRD 'Property Tax Rates' page 2025): 0.08 % of the value; $10 p.a. for values of $50,000 or less") }

def families : List Family := [propF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.assets.any (·.kind.isRealEstate)) "property tax at the 0.08 % urban/commercial rate (0.04 % for agricultural, hotel and factory use needs the property's use); value on the roll taken as the asset's statutory value"
  ++ when (!g.purchases.isEmpty) "stamp duty and transfer taxes on real property not modelled"

#guard propTax 50000 == 10
#guard propTax 1000000 == 800

end VcGlobal.Transfers
