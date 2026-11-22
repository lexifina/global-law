import SETax.Reductions

/-!
# Fees on the income-tax return: allmän pensionsavgift, public service-avgift, begravningsavgift; egenavgifter

* Lag (1994:1744) om allmän pensionsavgift, 2-4 §§ (see `Params.pensionFee`). Income of employment and of other
  gainful work "var för sig avrundas till närmast lägre hundratal kronor" (3 §).
* Lag (2018:1893) om finansiering av radio och tv i allmänhetens tjänst (in force 2019-2025, repealed 2026-01-01):
  3 § payable by those who "vid beskattningsårets ingång har fyllt 18 år"; 4 § underlag = beskattningsbar
  förvärvsinkomst, "högst ... 1,55 gånger det inkomstbasbelopp" (Lag 2024:1251, 2025 wording); 5 § "1 procent".
* Begravningslagen (1990:1144) 9 kap. 1-3 §§: payable by everyone folkbokförd, "beräknas på grundval av den
  avgiftsskyldiges till kommunal inkomstskatt beskattningsbara förvärvsinkomst"; rate set by the huvudman
  (Stockholm: the municipality, 0,07 % in 2025).
* Socialavgiftslagen (2000:980) 3 kap.: egenavgifter on income from self-employment (28,97 % in 2025). Modelled in
  the steady state: the deduction for egenavgifter (IL 16 kap. 29 §) equals the year's egenavgifter, so with profit
  `P` before the deduction, `A = r·(P − A)`, i.e. `A = r·P/(1 + r)`. The 7,5 % nedsättning (3 kap. 15-16 §§) and
  the schablonavdrag/återföring timing are not modelled.

Rounding of the fees in kronor: öretal dropped (SKV 433 avsnitt 7.6 "Öretal bortfaller efter uträkningen").
-/

namespace SETax
open TaxKernel

/-- Allmän pensionsavgift on wages `w` and income of other gainful work `n` (each rounded down to hundreds). -/
def pensionFeeOn (p : Params) (w n : Int) : Int :=
  (pensionFee p).amount (toMultiple .down 100 (pos w) + toMultiple .down 100 (pos n))

/-- Public service-avgift (lag 2018:1893, 4-5 §§). -/
def publicService (p : Params) (adult : Bool) (b : Int) : Int :=
  if adult then p.psRate * min (pos b) (p.psCapIbbMilli * p.ibb / 1000) / BP else 0

/-- Begravningsavgift (begravningslagen 9 kap. 3 §). -/
def begravningsavgift (p : Params) (b : Int) : Int :=
  match p.begravning100k with
  | some r => r * pos b / 100000
  | none => p.begravning * pos b / BP

/-- Egenavgifter in the steady state, `r·P/(1+r)`, öretal dropped. -/
def egenavgifter (age : Nat) (profit : Int) : Int :=
  let r := egenavgiftRate age
  r * pos profit / (BP + r)

end SETax
