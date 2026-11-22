import LtGlobal.Pit

/-!
# LT 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (no real-estate transfer tax (notary fees): absence not yet cited): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Nekilnojamojo turto mokesčio įstatymas (Vilnius)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4400 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Lithuania, Corporate - Other taxes, accessed 2025-05-25 (Wayback capture; `law/pwc_corpother_wb2025.txt`): stamp duty: none; state-service fees only (notary, registers) (PwC WWTS Corporate - Other taxes, 2025-05-25 (Wayback capture))
-/

namespace LtGlobal.Property
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .transactions, why := "stamp duty: none; state-service fees only (notary, registers)" }]

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])


end LtGlobal.Property
