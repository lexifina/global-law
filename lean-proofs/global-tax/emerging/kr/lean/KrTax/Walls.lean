import KrTax.Out

/-!
# Walls: kernel-checked facts about named households (FINDINGS F9–F14)

Each fact evaluates the whole model (`household`) on a concrete household; `decide` makes the kernel compute it.
`netOf` is the contract's net income (gross − taxes − social + benefits).
-/

namespace KrTax
open TaxKernel

set_option maxRecDepth 200000

def mkCanon (w1 : Int) (w2 : Option Int) (married : Bool) (kids : List Nat) (div : Int := 0) : Canon :=
  { id := "w", adults := [{ wages := w1 }] ++ (match w2 with | some w => [{ wages := w }] | none => []),
    married, children := kids.map fun a => { age := a }, dividends := div }

def netOf (c : Canon) : Int := (household c 0 none true).net c.gross

/-- F9: a one-earner couple with children 6 and 11 and 56,749,797 won of dividends: one more won of wages at
13,250,202 takes 연간 총소득 to 7천만원 (STA §100의28①2) while the 자녀장려금 is set by earnings alone (§100의29①):
1,750,000 won of 자녀장려금 is lost (1,749,999 net). -/
theorem wall_ctc_dividends :
    netOf (mkCanon 13250202 (some 0) true [6, 11] 56749797)
      - netOf (mkCanon 13250203 (some 0) true [6, 11] 56749797) = 1749999 := by decide

/-- F4 in money: the 자녀장려금 ends 10 won before the statute's 7천만원 (no table row from 69,999,990). -/
theorem wall_ctc_gap :
    netOf (mkCanon 69999989 (some 0) true [6, 11]) - netOf (mkCanon 69999990 (some 0) true [6, 11]) = 761999 := by
  decide

/-- F11: 근로장려금 starts at 100,000 won: a single person earning 40,000 won (the table's first row, 29,000 won,
raised to 10만원 by STA §100의7③) gets 99,999 won more net (100,000 less one won of social insurance) than one earning 39,999. -/
theorem wall_eitc_start :
    netOf (mkCanon 40000 none false []) - netOf (mkCanon 39999 none false []) = 99999 := by decide

/-- F11: and it ends with a 30,000-won cliff (단독가구 at 21,881,900 won: the table's "-" row; the row before is raised
from 26,000 to 3만원 by §100의7③). -/
theorem wall_eitc_end :
    netOf (mkCanon 21881899 none false []) - netOf (mkCanon 21881900 none false []) = 29999 := by decide

/-- The spouse's 500만원 wage test (ITA §50①2): one won more of the spouse's wages costs the couple 247,499 won. -/
theorem wall_spouse_test :
    netOf (mkCanon 56749797 (some 5000000) true []) - netOf (mkCanon 56749797 (some 5000001) true []) = 247499 := by
  decide

end KrTax
