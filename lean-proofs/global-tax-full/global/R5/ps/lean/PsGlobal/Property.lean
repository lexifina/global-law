import TaxKernel.Global
import R5Common

/-!
# Palestine 2025: buildings and land tax within municipalities (4100)

Law No 11 of 1954 on the buildings and land tax within the areas of municipalities and local councils (قانون ضريبة
الأبنية والأراضي داخل مناطق البلديات والمجالس المحلية), with its amendments (Decree-Law 12/2018 art. 2-3: art. 13 bis
added, art. 14 amended), Maqam consolidated text (maqam.najah.edu/legislation/2082/, "ساري النفاذ في الضفة الغربية
وغزة"; DL 12/2018 "ساري النفاذ في الضفة الغربية"; `law/ps_maqam_buildings_land_tax_1954.txt`):
* art. 7(1): net annual rental value of a building = annual rent less one fifth (wear and use); 7(3): for land without
  permanent buildings, net annual value = 6 % of the price it would sell at.
* art. 13: rate: buildings (with their yard) 10 % of the net annual rental value; land that is not a building yard 5 %.
* art. 12(1): exemptions for state, municipal, religious, charitable bodies, …; (ل) owner-occupied dwellings with a net
  annual rental value under two dinars.
Asset inputs: `home`/`realEstate` need `annualValue` (the annual rent the building would fetch); `land` uses its value.
Only properties inside municipal and local-council areas are taxed (taken as given). **Grade B** (statute read; art. 13
bis of DL 12/2018 not read; whether Israeli military orders changed the rates in the West Bank not checked).
-/

namespace PsGlobal
open TaxKernel TaxKernel.Global R5Common

/-- art. 7(1) + 13(1): 10 % of four fifths of the annual rent. -/
def buildingTax (annualRent : Int) : Int := divR .down (divR .down (pos annualRent * 4) 5 * 1000) BP

/-- art. 7(3) + 13(2): 5 % of a net annual value of 6 % of the sale value. -/
def landTax (value : Int) : Int := divR .down (divR .down (pos value * 600) BP * 500) BP

def property : Family :=
  { name := "4100 ضريبة الأبنية والأراضي", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      (g.assets.zipIdx.filterMap fun (a, i) =>
        if (a.kind == .home || a.kind == .realEstate) && a.annualValue ≥ 0 then
          some (charge .propertyRecurrent "ضريبة الأبنية" a.annualValue pos buildingTax (event := s!"property {i + 1}")
            (level := .local) (statute := "Law 11/1954 art. 7(1), 13(1) (10 % of the net annual rental value = rent less 1/5)"))
        else if a.kind == .land then
          some (charge .propertyRecurrent "ضريبة الأراضي" a.value pos landTax (event := s!"property {i + 1}")
            (level := .local) (statute := "Law 11/1954 art. 7(3), 13(2) (5 % of a net annual value of 6 % of the sale value)"))
        else none) }

def propertyUnsupported (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => (a.kind == .home || a.kind == .realEstate) && a.annualValue < 0) then
    ["buildings tax: a building without `annualValue` (annual rental value) is not computed"] else [])
  ++ (if g.assets.any (fun a => a.kind.isRealEstate) then
    ["buildings and land tax: property taken as inside a municipal area; art. 12 exemptions and art. 13 bis not applied"] else [])

#guard buildingTax 10000 == 800
#guard landTax 1000000 == 3000

end PsGlobal
