import AuTax.Household
import AuTax.Schedule1

/-! `ausched`: Schedule 1 scale 2 (tax-free threshold claimed, no offsets, no Medicare adjustment) x 52 against the
year's liability on 52 x weekly earnings for a single resident with wages only (ITRA Sch 7 tax - LITO + Medicare
levy, 2024-25 or 2025-26). Output CSV: weekly, annual, withheld_annual, liability, diff (withheld - liability). -/

open AuTax

def liabilityCents (p : Params) (annual : Int) : Int :=
  let ti := aud annual
  pos (basicTaxC p ti - litoC p ti) + levyS7C p ti

def main (args : List String) : IO Unit := do
  let year := if args.contains "2026" then 2026 else 2025
  let p := paramsFor year
  IO.println "weekly,annual,withheld,liability,diff"
  for w in List.range 4001 do
    let x : Int := w
    let wh := 52 * aud (withhold scale2 x)
    let li := liabilityCents p (52 * x)
    IO.println s!"{x},{52 * x},{wh},{li},{wh - li}"
