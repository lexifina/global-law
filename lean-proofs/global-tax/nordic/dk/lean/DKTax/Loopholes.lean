import DKTax.Household

/-!
# Loopholes and traps as theorems on the full model (`decide`: the kernel evaluates the whole Danish computation)

Every household is København 2025 (2026 where stated), not a church member, full-time ATP. `burden` = state + local
income tax + AM-bidrag + ATP − cash benefits (kroner). FINDINGS F9-F14 explain each.
-/

namespace DKTax.Loopholes
open DKTax

def cph : Opts := { munRate7 := 2350000 }
def cph26 : Opts := { munRate7 := 2339000 }
def w (x : Int) (age : Nat := 40) : PIn := { wages := x, atpOwn := 1188, atpEmployer := 2376, age }
def single (y : Nat) (o : Opts) (x : PIn) : HH := { year := y, persons := [x], o }

/-- F9 (trap, known): marriage pools the spouses' positive nettokapitalindkomst and taxes it in the topskat of the
spouse with the higher personal income (PSL § 7, stk. 8-10). A spouse living on 400.000 kr. of interest married to
a 1.000.000 kr. earner pays 19.159 kr. more than if they were not married. -/
theorem marriage_capital_penalty :
    (HH.mk 2025 true [{ interestIncome := 400000 }, w 1000000] [] cph).burden
      - (HH.mk 2025 false [{ interestIncome := 400000 }, w 1000000] [] cph).burden = 19159 := by decide

/-- F10 (known): an owner-manager with 1.000.000 kr. of company profit keeps 9.863 kr. more by taking 910.000 kr.
of salary and the rest as dividend ((90.000 × 78 % = 70.200 kr., selskabsskat 22 %) than by taking it all as
salary: the first 67.500 kr. of aktieindkomst bear 22 % + 78 % × 27 % = 43,06 % against 54,47 % on pay. -/
theorem owner_manager_dividend_band :
    ((1000000 : Int) - (single 2025 cph (w 1000000)).burden)
      + 9863 = (910000 + 70200) - (single 2025 cph { w 910000 with aktie := 70200 }).burden := by decide

/-- F11 (known design, recreated): 135.000 kr. of dividends in one year instead of 67.500 kr. in each of two
years costs 15 % × 67.500 = 10.125 kr. (PSL § 8 a progressionsgrænse, per year). -/
theorem dividend_bunching :
    (single 2025 cph { w 500000 with aktie := 135000 }).burden + (single 2025 cph (w 500000)).burden
      - 2 * (single 2025 cph { w 500000 with aktie := 67500 }).burden = 10125 := by decide

/-- F12 (timing across the reform): moving 100.000 kr. of pay from 2025 to 2026 saves 6.776 kr. for a København
employee on 750.000 kr. (2025 topskat 15 % from 611.800 kr.; 2026 mellemskat 7,5 % from 641.200 kr.) … -/
theorem defer_bonus_2026 :
    ((single 2025 cph (w 850000)).burden + (single 2026 cph26 (w 750000)).burden)
      - ((single 2025 cph (w 750000)).burden + (single 2026 cph26 (w 850000)).burden) = 6776 := by decide

/-- … but for an employee on 3.000.000 kr. paying it in 2025 saves 4.498 kr. (2026 toptopskat 5 % above
2.592.700 kr. makes 2026 dearer at the top). -/
theorem accelerate_bonus_2025_toptop :
    ((single 2025 cph (w 3000000)).burden + (single 2026 cph26 (w 3100000)).burden)
      - ((single 2025 cph (w 3100000)).burden + (single 2026 cph26 (w 3000000)).burden) = 4498 := by decide

end DKTax.Loopholes
