import FrTax.Income

/-!
# Contributions on high incomes

* **CEHR**, CGI art. 223 sexies: 3 % of the revenu fiscal de référence between 250 000 € and 500 000 € (couples:
  500 000 € and 1 000 000 €), 4 % above. The smoothing of II (exceptional income against the two previous
  years) needs earlier years' RFR and is not modelled.
* **CDHR**, CGI art. 224 (income 2025 only, as created by loi n° 2025-127, art. 10; NOTA: "applicables à
  l'imposition des revenus de l'année 2025"): 20 % of the revenu of II, less the income tax, the CEHR, 12 500 €
  for a couple and 1 500 € per dependant (III, 2°). The version of IV, A, 2° that also adds back the reduction
  for gifts of art. 200 was inserted by loi n° 2026-103, art. 2, and applies only "à compter de l'imposition des
  revenus de l'année 2026" (NOTA): for income 2025 the gifts are not added back.
-/

namespace FrTax

def cehr (d : Decl) (rfr : Int) : Int :=
  let (t1, t2) : Int × Int := if d.couple then (500000, 1000000) else (250000, 500000)
  pct 300 (pos (min rfr t2 - t1)) + pct 400 (pos (rfr - t2))

/-- The revenu of art. 224, II: the RFR less the allowances of 1417, IV, 1°, a bis other than 150-0 D (here
the 40 % allowance on dividends taxed at the scale, art. 158, 3, 2°). -/
def cdhrBase (d : Decl) (rfr : Int) : Int :=
  rfr - (if scaleOption d then pct 4000 (d.get "2DC") else 0)

/-- Dependants "au sens des articles 196 à 196 B": children in charge, in shared residence, attached, and
disabled people under the roof (0CF, 0CH, 0DJ, 0DN, 0CR); a child in shared residence counts in full (what M
does). -/
def dependants (d : Decl) : Int := d.sum ["0CF", "0CH", "0DJ", "0DN", "0CR"]

/-- `tax`: the income tax after reductions and the tax credits (other than the prepayments 2CK and the
conventions credit 2AB, which IV, A, 2° adds back), with the income tax at 19 % on property gains (art. 200 B,
box 3VZ) and the flat levies of art. 151-0 (prélèvements libératoires listed in 1417, IV, 1°, c). -/
def cdhr (d : Decl) (rfr tax cehrAmt : Int) : Int :=
  if d.year ≠ 2025 then 0 else
  let r := cdhrBase d rfr
  let thr : Int := if d.couple then 500000 else 250000
  if r ≤ thr then 0 else
  let a := pct 2000 r
  let a := if r ≤ (if d.couple then 660000 else 330000) then min a (pct 8250 (r - thr)) else a
  pos (a - (tax + cehrAmt + (if d.couple then 12500 else 0) + 1500 * dependants d))

end FrTax
