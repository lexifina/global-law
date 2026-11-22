import TaxKernel.World

/-!
# Eritrea: no accessible statute (access tier C)

Stub required by CONTRACTWORLD for tier C: every household gets `unsupported: ["no accessible statute"]` and no tax
amounts. What was tried and what would unlock a model: `er/PROGRESS.md` and `er/FINDINGS.md`.
-/

namespace ErTax
open TaxKernel

def out (c : Canon) : Out :=
  Out.make c "ER" "ERN" 0 (detail := [Out.dStr "status" "unsupported: no accessible statute (tier C)"])
    (unsupported := ["no accessible statute"])

def country : Country := { code := "ER", name := "Eritrea (no accessible statute)", currency := "ERN", year := "2025", compute := out }

end ErTax
