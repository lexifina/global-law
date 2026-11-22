import TaxKernel.World

/-!
# Saint Vincent and the Grenadines: no accessible statute (access tier C)

Stub required by CONTRACTWORLD for tier C: every household gets `unsupported: ["no accessible statute"]` and no tax
amounts. What was tried and what would unlock a model: `vc/PROGRESS.md` and `vc/FINDINGS.md`.
-/

namespace VcTax
open TaxKernel

def out (c : Canon) : Out :=
  Out.make c "VC" "XCD" 0 (detail := [Out.dStr "status" "unsupported: no accessible statute (tier C)"])
    (unsupported := ["no accessible statute"])

def country : Country := { code := "VC", name := "Saint Vincent and the Grenadines (no accessible statute)", currency := "XCD", year := "2025", compute := out }

end VcTax
