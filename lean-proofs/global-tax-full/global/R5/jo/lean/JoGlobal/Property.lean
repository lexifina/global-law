import TaxKernel.Global
import R5Common

/-!
# Jordan 2025: buildings and land tax within municipal areas (ضريبة الأبنية والأراضي, 4100)

Law No. 11 of 1954 on the buildings and land tax within the areas of municipalities and local councils, Jordanian
consolidated text as reprinted by jordanianlaw.com ("تشريعات الأردن"; `law/jo_lawcom_11_1954.{html,txt}`).
**Unofficial reprint** (lob.gov.jo sits behind a reCAPTCHA: not bypassed): flagged, grade B.
* art. 5: rate (أ) a building with its yard, other than one used for a machine-driven industrial project, **8 %** of
  the annual rent; (ب) a machine-driven industrial building 10 %; (ج) land without buildings **8 %** of the annual rent;
* art. 9(1)-(2): the annual rent is the rent the building is let at, or the committee's estimate; art. 9(3): the annual
  rent of land without permanent buildings is **6 %** of the price it would sell at;
* art. 13(1): the tax is collected **from the owner**; art. 14(2)(ب): owner-occupied dwellings with an annual rent
  under two dinars are exempt.
Model: `home`/`realEstate` with `annualValue`: 8 % of it; `land`: 8 % of 6 % of its value. **Grade B** (unofficial
reprint; amendments after the reprint's date not checked).
-/

namespace JoGlobal
open TaxKernel TaxKernel.Global R5Common

/-- art. 5(أ): 8 % of the annual rent. -/
def buildingTax (rent : Int) : Int := divR .down (pos rent * 800) BP

/-- art. 9(3) + 5(ج): 8 % of an annual rent of 6 % of the sale value. -/
def landTax (value : Int) : Int := divR .down (divR .down (pos value * 600) BP * 800) BP

def propertyPre3q : Family :=
  { name := "4100 ضريبة الأبنية والأراضي", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      g.assets.zipIdx.filterMap fun (a, i) =>
        if (a.kind == .home || a.kind == .realEstate) && a.annualValue ≥ 0 then
          some (charge .propertyRecurrent "ضريبة الأبنية" a.annualValue pos buildingTax (event := s!"property {i + 1}")
            (level := .local) (statute := "Law 11/1954 art. 5(أ) (8 % of the annual rent), 9(1)-(2), 13(1) (owner) [unofficial reprint]"))
        else if a.kind == .land then
          some (charge .propertyRecurrent "ضريبة الأراضي" a.value pos landTax (event := s!"property {i + 1}")
            (level := .local) (statute := "Law 11/1954 art. 5(ج), 9(3) (8 % of an annual rent of 6 % of the sale value), 13(1) [unofficial reprint]"))
        else none }

def propertyUnsupportedPre3q (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => (a.kind == .home || a.kind == .realEstate) && a.annualValue < 0) then
    ["4100 buildings tax: a building without `annualValue` (annual rent) is not computed (grade C)"] else [])
  ++ (if g.assets.any (fun a => a.kind.isRealEstate) then
    ["4100 buildings and land tax: property taken as inside a municipal area; machine-driven industrial buildings (10 %) and art. 14 exemptions not distinguished"] else [])

#guard buildingTax 3000 == 240
#guard landTax 100000 == 480


/-- Pass 3q year-in-force audit: grade C. 4100 buildings and land tax grade C (year-in-force audit, pass 3q): Law 11/1954 in an unofficial reprint without amendment notes is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`propertyPre3q`) for a later re-cite;
it is not in the model. -/
def propertyUnsupported (g : CanonGlobal) : List String :=
  (if (propertyPre3q.run [] g []).isEmpty then [] else ["4100 buildings and land tax grade C (year-in-force audit, pass 3q): Law 11/1954 in an unofficial reprint without amendment notes is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ propertyUnsupportedPre3q g

end JoGlobal
