import TaxKernel.Global
import R5Common

/-!
# Oman 2025: fee on registering lease contracts, Muscat (رسوم تسجيل عقود الإيجار, 4100)

Model governorate **Muscat**. Muscat Municipality Decision No. 20/2016 fixing the fees for registering lease contracts
(Official Gazette 1133 of 31/01/2016, in force 01/02/2016; issued under Royal Decree 6/89 on landlords and tenants and
the Muscat Municipality Law RD 38/2015; qanoon.om `p/2016/mm20160020/`, `law/om_mm20160020.{html,txt}`), art. 1: **the
lessor** of any property or part of it (or the tenant where agreed that he registers) pays a fee of **5 %** of the total
value of the contract for its term. The municipality cut the fee **from 5 % to 3 %** (Oman Daily, 2021, reporting the
municipality: "تم تخفيض رسوم عقود الإيجار من 5% إلى 3%"; `law/om_daily4308.{html,txt}`); the amending decision was not
found (Muscat fee decision 1/2018 and its amendment 96/2019 read: no lease fee in them).
Model: a let `realEstate` with `annualValue` (the annual rent): **3 %** of it, on the owner (lessor), local level.
**Grade B** (decision text read; the 3 % rate from a reliable secondary source; other municipalities not modelled).
**2025 (pass 3r re-cite).** Muscat Municipality page "عقود الايجار – كيفية حساب رسوم الخدمة" (mm.gov.om/ar/
Ca_RentContractNew.aspx, Wayback 18/04/2025; `law/om_mm_rentcontract_2025.html`): "رسوم تسجيل العقد ... (قيمة الإيجار
الشهري × مدة العقد ) × 3%" with the example "(100 * 12 شهرا ) * 0.03 =36": the 3 % applied in 2025 (official
municipal guide; late registration triples the fee, not modelled). Grade B (the amending decision still not read).
-/

namespace OmGlobal
open TaxKernel TaxKernel.Global R5Common

/-- 3 % of the rent (Decision 20/2016 art. 1 as reduced). -/
def leaseFee (rent : Int) : Int := divR .down (pos rent * 300) BP

def property : Family :=
  { name := "4100 رسوم تسجيل عقود الإيجار (بلدية مسقط)", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      g.assets.zipIdx.filterMap fun (a, i) =>
        if a.kind == .realEstate && a.annualValue ≥ 0 then
          some (charge .propertyRecurrent "رسوم تسجيل عقد الإيجار (المؤجر)" a.annualValue pos leaseFee
            (event := s!"property {i + 1}") (level := .local)
            (statute := "Muscat Municipality Decision 20/2016 art. 1 (lessor; 5 % of the contract value), reduced to 3 % (Oman Daily 2021; amending decision not found)"))
        else none }

def propertyUnsupported (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .realEstate && a.annualValue < 0) then
    ["4100 lease registration fee: a let property without `annualValue` (annual rent) is not computed (grade C)"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate) then
    ["4100 lease registration fee: Muscat taken as the model governorate; `realEstate` with `annualValue` taken as let; the 3 % reduction's decision not found"] else [])

#guard leaseFee 6000 == 180



end OmGlobal
