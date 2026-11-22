import TaxKernel.Global

/-! # Macao SAR: no 1.x PIT model (PLAN.md §2: a new entity). The PIT line is a stub that says so; the SAR's own taxes
(including its tax on salaries) are families of this project. -/

namespace CnmoGlobal
open TaxKernel TaxKernel.Global Lean

def pitLine (_ : List String) (c : Canon) : Json :=
  Json.mkObj [("id", Json.str c.id), ("country", Json.str "CN-MO"), ("currency", Json.str "MOP"),
    ("note", Json.str "no 1.x PIT model for Macao SAR: its taxes are computed by the kernel-2.0 families")]

def base : GlobalModel :=
  { code := "CN-MO", name := "Macao SAR", currency := "MOP", pit := pitLine, pitCharges := fun _ => [] }

def pitOf (_ : List String) (_ : Canon) : Int := 0

end CnmoGlobal
