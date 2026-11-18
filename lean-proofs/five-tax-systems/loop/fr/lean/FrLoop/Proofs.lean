import FrLoop.Extra

/-!
# Headline results of the French loophole catalogue (income 2025), as whole-return statements

As in `FrTax/Loopholes.lean`, whole returns go through `native_decide` (a `Decl` keeps its boxes in a hash map
whose `String.hash` the kernel cannot evaluate). `burden` = net income tax + CEHR + CDHR + levies on the return.
-/

namespace FrLoop
open FrTax

def mk (l : List (String × Int)) : Decl := { year := 2025, boxes := l.foldl (fun m kv => m.insert kv.1 kv.2) {} }
def burdenX (l : List (String × Int)) (e : Extra := {}) : Int :=
  let r := computeX p2025 (mk l) e
  r.net + r.cehr + r.cdhr + r.social

/-- A single CDHR payer above the smoothing band: salary 150 000 €, dividends 800 000 € (levies withheld). -/
def cd2 : List (String × Int) := [("0AC", 1), ("0DA", 1975), ("1AJ", 150000), ("2DC", 800000), ("2BH", 800000)]
/-- A single person in the CDHR smoothing band: salary 30 000 €, dividends 290 000 €. -/
def band : List (String × Int) := [("0AC", 1), ("0DA", 1975), ("1AJ", 30000), ("2DC", 290000), ("2BH", 290000)]

/-- **Novel.** Home help makes a CDHR payer who subscribes to SMEs pay 5 000 € more: the 6 000 € credit is taken
back by the CDHR (art. 224, IV, A, 2° does not list art. 199 sexdecies) but still fills 6 000 € of the 10 000 €
global cap (art. 200-0 A), so the IR-PME reduction (listed, art. 10, II of loi n° 2025-127) falls from 9 000 € to
4 000 €. -/
theorem homehelp_costs_cdhr_payer_2025 :
    burdenX (cd2 ++ [("7DB", 12000)]) { pme := 50000 } = burdenX cd2 { pme := 50000 } + 5000 := by native_decide

/-- Without the CDHR the same home help is worth its 6 000 € credit less the 5 000 € of PME reduction it crowds
out: 1 000 €. -/
theorem homehelp_no_cdhr_2025 :
    burdenX [("0AC", 1), ("0DA", 1975), ("1AJ", 150000), ("7DB", 12000)] { pme := 50000 }
      = burdenX [("0AC", 1), ("0DA", 1975), ("1AJ", 150000)] { pme := 50000 } - 1000 := by native_decide

/-- **Variant.** In the CDHR smoothing band (art. 224, V) a deduction that lowers the RFR is worth 82.5 %: a
10 700 € property deficit (art. 156, I, 3°) saves 8 827 €, an alimony of 6 855 € to an adult child 5 655 €;
a PER contribution (added back to the RFR, art. 1417, IV, 1°) saves nothing. -/
theorem band_deficit_2025 : burdenX band - burdenX (band ++ [("4BC", 10700)]) = 8827 := by native_decide
theorem band_alimony_2025 : burdenX band - burdenX (band ++ [("6EL", 6855)]) = 5655 := by native_decide
theorem band_per_2025 : burdenX (band ++ [("APS", 10000)]) = burdenX (band ++ [("APS", 10000), ("6NS", 10000)]) := by
  native_decide

/-- **Novel (small).** Above the band the CDHR reverses the adult-child choice: attaching saves 1 500 € (the CDHR's
amount per dependant, art. 224, III, 2°), the 6 855 € alimony 1 371 € (20 % of the RFR it removes); without the
CDHR the alimony wins (LOOPHOLES finding 1). -/
theorem cdhr_prefers_attachment_2025 :
    burdenX (cd2 ++ [("0DJ", 1)]) + 129 = burdenX (cd2 ++ [("6EL", 6855)]) := by native_decide

/-- **Known.** Girardin industriel: the 18 000 € cap counts the reduction for 44 % (BOI-IR-LIQ-20-20-10-30), so a
household can take 40 909 € of reduction in one year. -/
theorem girardin_40909_2025 :
    (computeX p2025 (mk [("0AC", 1), ("0DA", 1980), ("1AJ", 300000)]) { girardin := 50000 }).reductions = 40909 := by
  native_decide

/-- **Known.** Year of death (art. 6, 8; art. 196 ter): two returns on the couple's parts instead of one. Salaries
60 000 € and 20 000 €, death on 30 June: 7 808 € on one return, 562 € on the two. -/
theorem death_year_2025 :
    burdenX [("0AM", 1), ("0DA", 1980), ("0DB", 1982), ("1AJ", 60000), ("1BJ", 20000)] = 7808 ∧
    burdenX [("0AM", 1), ("0DA", 1980), ("0DB", 1982), ("1AJ", 30000), ("1BJ", 10000)]
      + burdenX [("0AM", 1), ("0DA", 1980), ("0DB", 1982), ("1AJ", 30000)] = 562 := by native_decide

/-- **Known.** Quotient (art. 163-0 A): 200 000 € of exceptional income on a couple with two children and 60 000 €
of salary costs 48 840 € instead of 68 127 €. -/
theorem quotient_2025 :
    burdenX [("0AM", 1), ("0DA", 1980), ("0DB", 1982), ("0CF", 2), ("1AJ", 60000)] { exc := 200000 } = 48840 ∧
    burdenX [("0AM", 1), ("0DA", 1980), ("0DB", 1982), ("0CF", 2), ("1AJ", 60000), ("5QC", 200000)] = 68127 := by
  native_decide

end FrLoop
