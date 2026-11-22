import TaxKernel.Global2
import R5Common

/-!
# United Arab Emirates 2025: Dubai municipality housing fee (4100), model emirate Dubai

Secondary-source sweep (2026-11-22), grade B (guide facts; the Dubai Local Order on the fee was not read):
PwC Worldwide Tax Summaries, United Arab Emirates, Individual - Other taxes, section on municipal or property tax, last
reviewed 26 August 2025 (Wayback capture 2025-10-21, `law/pwc_ae_indother_wb20251021.txt`): most emirates charge a municipal
fee by reference to the annual rental value, generally on the tenant; in Dubai it is 5 % of the annual rental value for
residential property (the housing fee, paid by the tenant, or by the owner where there is no tenant) and 5 % for commercial
property (market fees, paid by the owner). Deloitte UAE Highlights 2025 (updated June 2025, `law/deloitte_ae_2025.txt`)
confirms a municipality fee on rentals in certain emirates, varying by emirate (no rate).
Model (Dubai, as the 4400 entry): a tenant household pays 5 % of its rent (basket line `rent`, taken as the rent paid,
the fee outside it); an owner-occupied home pays 5 % of its annual rental value (kernel 2.8 `LocalTax`, base
`.annualValue [.home]`, default Dubai 5 % with the guide as source; another emirate's home needs its own declared rate
under `localRates.propertyTax`, else grade C). Let property (`realEstate`): the tenant pays if residential and the owner
if commercial; the use is not an input: listed, not charged. Other emirates' fees (Abu Dhabi, Sharjah, ...) not modelled.
-/

namespace AeGlobal
open TaxKernel TaxKernel.Global R5Common

def aePwc : String := "PwC WWTS United Arab Emirates, Individual - Other taxes (reviewed 26 August 2025): Dubai housing fee 5 % of the annual rental value"

def housingFeeOwner : LocalTax :=
  { key := "propertyTax", name := "Dubai Municipality housing fee (owner-occupied home, 5 % of annual rental value)",
    base := .annualValue [.home], unit := .percent,
    default := some { municipality := "Dubai", num := 5, den := 1, source := aePwc, date := "2025-08-26" },
    statute := "Dubai Municipality housing fee (Local Order not read); " ++ aePwc }

/-- 5 % of each `rent` basket line (the tenant's housing fee, Dubai). -/
def housingFeeTenant (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.consumption.zipIdx.filter fun (s, _) => s.good == .rent).map fun (s, k) =>
    charge .propertyRecurrent "Dubai Municipality housing fee (tenant, 5 % of rent)" s.amount pos (fun b => divR .down (5 * b) 100)
      (event := s!"line {k + 1}") (level := .local) (statute := "Dubai Municipality housing fee (Local Order not read); " ++ aePwc)

def property : Family :=
  { name := "4100 Dubai housing fee", covers := [.propertyRecurrent],
    run := fun a g c => housingFeeOwner.family.run a g c ++ housingFeeTenant g }

def propertyUnsupported (g : CanonGlobal) : List String :=
  housingFeeOwner.unknown g ++
  (if g.assets.any (·.kind == .realEstate) then
    ["4100 Dubai municipal fees on let property: residential (tenant pays) or commercial (owner pays 5 %): the use is not an input, not charged (grade C part)"] else []) ++
  (if g.assets.any (·.kind == .home) || g.consumption.any (·.good == .rent) then
    ["4100 municipal fees of emirates other than Dubai not modelled (model emirate Dubai; a home in another emirate needs a declared localRates.propertyTax)"] else [])

#guard taxAt .percent 120000 5 1 == 6000

end AeGlobal
