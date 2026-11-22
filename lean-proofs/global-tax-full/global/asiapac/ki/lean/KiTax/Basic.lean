import TaxKernel.World

/-!
# Kiribati: no accessible statute for 2025 (access tier C)

Stub required by CONTRACTWORLD for tier C: every household gets `unsupported: ["no accessible statute"]` and no tax
amounts. What was tried and what would unlock a model: `ki/PROGRESS.md` and `ki/FINDINGS.md`.
-/

namespace KiTax
open TaxKernel

def out (c : Canon) : Out :=
  Out.make c "KI" "AUD" 0 (detail := [Out.dStr "status" "unsupported: no accessible statute for 2025 (tier C)"])
    (unsupported := ["no accessible statute"])

def country : Country := { code := "KI", name := "Kiribati (no accessible statute for 2025)", currency := "AUD", year := "2025", compute := out }

end KiTax
