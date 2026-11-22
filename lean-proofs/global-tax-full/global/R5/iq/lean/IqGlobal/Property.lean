import TaxKernel.Global
import R5Common

/-!
# Iraq 2025: real estate tax (ضريبة العقار, 4100)

Real Estate Tax Law No. 162 of 1959 with its amendments, consolidated text of the General Commission for Taxes
(`tax.mof.gov.iq/قانون-ضريبة-العقار-رقم-162-لسنة-1959-وتعديلا/`, Wayback 2023-09-25; `law/iq_rett162.{html,txt}`):
* art. 1(6)-(8): the taxpayer is the owner of the property (المالك أو واضع اليد أو متولي الوقف); (7) revenue = the
  actual or estimated annual rent;
* art. 2(1): **10 %** of the annual revenue of all real property; art. 2(2): **10 %** of the annual revenue is deducted
  for maintenance and wear before the tax is computed;
* art. 4(1): the dwelling house or flat (occupied by its owner) is exempt; art. 3(11): property used for the owner's
  own business subject to income tax is exempt; art. 32 bis: the rate may be changed by the annual budget law.
Model: `realEstate` with `annualValue` (let property): 10 % × 90 % of `annualValue`; `home` (the owner's dwelling):
exempt, no charge. Vacant land is taxed under the separate land (العرصات) tax law, not read: grade-C note.
**Grade A** (statute text read; budget-law changes of the rate after 2023 not checked).
-/

namespace IqGlobal
open TaxKernel TaxKernel.Global R5Common

/-- art. 2(2): revenue less 10 % for maintenance and wear. -/
def netRevenue (v : Int) : Int := divR .down (pos v * 9000) BP

/-- art. 2(1): 10 %. -/
def realEstateTax (n : Int) : Int := divR .down (pos n * 1000) BP

def property : Family :=
  { name := "4100 ضريبة العقار", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      g.assets.zipIdx.filterMap fun (a, i) =>
        if a.kind == .realEstate && a.annualValue ≥ 0 then
          some (charge .propertyRecurrent "ضريبة العقار" a.annualValue netRevenue realEstateTax
            (event := s!"property {i + 1}") (level := .central)
            (statute := "Real Estate Tax Law 162/1959 art. 1(6)-(7) (owner; annual rent), art. 2(1) (10 %), 2(2) (10 % deducted for maintenance and wear)"))
        else none }

def propertyUnsupported (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .realEstate && a.annualValue < 0) then
    ["4100 real estate tax: a let property without `annualValue` (annual rent) is not computed (grade C)"] else [])
  ++ (if g.assets.any (fun a => a.kind == .land) then
    ["4100 vacant land (العرصات) tax: separate law, not read (grade C)"] else [])
  ++ (if g.assets.any (fun a => a.kind == .home) then
    ["4100 real estate tax: `home` taken as the owner's dwelling, exempt (Law 162/1959 art. 4(1))"] else [])

#guard realEstateTax (netRevenue 12000000) == 1080000

end IqGlobal
