import TaxKernel.Global

/-! # Hong Kong SAR: no 1.x PIT model (PLAN.md §2: a new entity). The PIT line is a stub that says so; the SAR's own taxes
(including its tax on salaries) are families of this project. -/

namespace CnhkGlobal
open TaxKernel TaxKernel.Global Lean

def pitLine (_ : List String) (c : Canon) : Json :=
  Json.mkObj [("id", Json.str c.id), ("country", Json.str "CN-HK"), ("currency", Json.str "HKD"),
    ("note", Json.str "no 1.x PIT model for Hong Kong SAR: its taxes are computed by the kernel-2.0 families")]

def base : GlobalModel :=
  { code := "CN-HK", name := "Hong Kong SAR", currency := "HKD", pit := pitLine, pitCharges := fun _ => [] }

def pitOf (_ : List String) (_ : Canon) : Int := 0

end CnhkGlobal
