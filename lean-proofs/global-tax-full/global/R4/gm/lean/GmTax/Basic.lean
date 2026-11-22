import TaxKernel.World

/-!
# The Gambia: no accessible statute (access tier C)

Stub required by CONTRACTWORLD for tier C: every household gets `unsupported: ["no accessible statute"]` and no tax
amounts. What was tried and what would unlock a model: `gm/PROGRESS.md` and `gm/FINDINGS.md`.
-/

namespace GmTax
open TaxKernel

def out (c : Canon) : Out :=
  Out.make c "GM" "GMD" 0 (detail := [Out.dStr "status" "unsupported: no accessible statute (tier C)"])
    (unsupported := ["no accessible statute"])

def country : Country := { code := "GM", name := "The Gambia (no accessible statute)", currency := "GMD", year := "2025", compute := out }

end GmTax
