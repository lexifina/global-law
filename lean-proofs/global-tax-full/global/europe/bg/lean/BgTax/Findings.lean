import BgTax.Theorems

/-!
# The findings of `FINDINGS.md`, each proved on concrete households (`native_decide` evaluates the model)

Amounts in stotinki. `hh` builds a canonical household; `burden` = income tax + employee contributions − benefits.
-/

namespace BgTax.Findings
open TaxKernel BgTax

def hh (ws : List Int) (kids : List Nat := []) (se : Int := 0) (married := true) : Canon :=
  { id := "f", adults := ws.map fun w => { wages := w, selfEmployment := se }, married := married && ws.length == 2,
    children := kids.map fun a => { age := a } }

def burden (c : Canon) : Int := let o := out c; o.incomeTax + o.employeeSocial - o.benefits

/-- F5 (notch): single parent, two children: 10 лв. more gross wage at 30 960 лв. costs 784.29 лв. of net income
(the whole 80 % allowance for April-December, 9 × 88 лв., less the 10 лв.'s own taxes). -/
theorem F5_single_parent_notch :
    (30970 * LEV - burden (hh [30970] [6, 11])) - (30960 * LEV - burden (hh [30960] [6, 11])) = -78429 := by
  native_decide

/-- F6 (ceiling): above 48 420 лв. a year, 1 000 лв. more wage costs exactly 100 лв. (10 %); below, 223.98 лв. (13.78 % + 10 % of the rest, per-month rounding) -/
theorem F6_above_ceiling : burden (hh [61000]) - burden (hh [60000]) = 100 * LEV := by native_decide
theorem F6_below_ceiling : burden (hh [21000]) - burden (hh [20000]) = 22398 := by native_decide

/-- F8 (anti-splitting): a couple with 120 000 лв. of wages pays 6 005.02 лв. less when one spouse earns it all
than when each earns 60 000 лв. (each has its own contribution ceiling; the 10 % tax is indifferent). -/
theorem F8_concentrate : burden (hh [60000, 60000]) - burden (hh [120000, 0]) = 600502 := by native_decide

/-- F9 (second income above the ceiling): 12 000 лв. more as a civil contract / free profession (25 % statutory
expenses, no contribution room left) costs 900 лв.; as employment 1 200 лв. -/
theorem F9_civil : burden (hh [60000] (se := 12000)) - burden (hh [60000]) = 900 * LEV := by native_decide
theorem F9_employment : burden (hh [72000]) - burden (hh [60000]) = 1200 * LEV := by native_decide

/-- F11 (self-insured minimum): the first lev of registered free-profession income costs 3 472.78 лв. of
contributions (27.8 % of the 12 492 лв. annual minimum base). -/
theorem F11_first_lev : (out (hh [0] (se := 1))).employeeSocial = 347278 := by native_decide

/-- F12 (family test by address): unmarried parents earning 22 500 лв. each with two children: registered at one
current address the allowance is the school grant only (300 лв.); the parent at a separate address with the
children receives the full allowance (1 320 лв.) and the grant. -/
theorem F12_separate_address :
    (out (hh [22500] [8, 12])).benefits - (out (hh [22500, 22500] [8, 12] (married := false))).benefits
      = 1320 * LEV := by native_decide

/-- F3 (statute): the codified child relief is a thirtieth of the amount actually granted for 2025. -/
theorem F3_relief : childRelief 2 = 30 * childReliefCodified 2 := childRelief_30x 2

end BgTax.Findings
