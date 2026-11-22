import TaxKernel.Global
import R5Common
import SaGlobal.Corporate

/-!
# Saudi Arabia 2025: zakat on companies (booked under 1200, by its base)

Zakat Collection Law (Royal Decree 17/2/28/8634, 1370H), laws.boe.gov.sa as archived on 2025-07-10
(`law/zakat_2025.html`): art. 2: "تستوفى من الأفراد والشركات الذين يحملون الرعوية السعودية الزكاة الشرعية وفقا لأحكام
الشريعة الإسلامية". The Law prints neither the rate nor the base: the Implementing Regulations (Ministerial
Resolution 2216, 1440H) were not read. Applied: the Sharia rate of a quarter of a tenth (2,5 %) on the input
`zakatBase` (the zakat base of the Regulations) or, without it, the taxable profit, times the Saudi/GCC share
`zakatShareBp` (P2 taxes the rest). Grade B.
-/

namespace SaGlobal
open TaxKernel TaxKernel.Global R5Common

def zakatBase (g : CanonGlobal) : Int :=
  let b := intField g.raw "zakatBase"
  if b ≠ 0 then b else (incomeTax g.company).taxableProfit g.company

def zakat : Family :=
  { name := "1200 الزكاة", covers := [],
    run := fun _ g _ =>
      if g.entity != .company || zakatShareBp g = 0 then [] else
      [zakatOnBase .cit "الزكاة" (divR .down (zakatShareBp g * pos (zakatBase g)) BP) 250
        "Zakat Collection Law art. 2 (Sharia zakat); 2,5 % and the base per the Implementing Regulations (not read)"] }

def zakatUnsupported (g : CanonGlobal) : List String :=
  (if g.entity == .company && zakatShareBp g ≠ 0 && intField g.raw "zakatBase" = 0 then
    ["zakat base of the Implementing Regulations not given: taxable profit used"] else [])
  ++ (if g.entity != .company then ["zakat of Saudi individuals (business assets) not modelled"] else [])

end SaGlobal
