import ITTax.Irpef

/-!
# Addizionali: regionale (D.Lgs. 446/1997 art. 50, Lazio 2025) and comunale (D.Lgs. 360/1998 art. 1, Roma 2025)

Both are a rate on the IRPEF base ("al reddito complessivo ... al netto degli oneri deducibili"), and both are due
only "se per lo stesso anno l'imposta sul reddito delle persone fisiche, al netto delle detrazioni ... risulta
dovuta" (art. 50 c. 2; art. 1 c. 4): a taxpayer whose detrazioni cover the imposta lorda pays neither. The
trattamento integrativo and the cuneo sum are not detrazioni, so they do not change that test.
-/

namespace ITTax
open TaxKernel

/-- Lazio 2025, before the "dovuta" test. -/
def lazio (base : Int) : Int :=
  if base ≤ 0 then 0 else
  let gross := if base ≤ lazioNoMagg then lazioLow.tax Rule.unitHalfUp base else lazioHigh.tax Rule.unitHalfUp base
  let d := if lazioDetrLo ≤ base ∧ base ≤ lazioDetrHi then lazioDetr else 0
  pos (gross - d)

/-- Roma Capitale 2025: an exemption threshold ("esenzione per redditi imponibili fino a"), not an allowance. -/
def romaSurcharge : Surcharge := { rate := romaRate, exempt := romaExempt, round := Rule.unitHalfUp }
def roma (base : Int) : Int := romaSurcharge.amount base

/-- Roma Capitale by year (`Params.romaExemptY`). -/
def romaY (y : Nat) (base : Int) : Int :=
  ({ rate := romaRate, exempt := romaExemptY y, round := Rule.unitHalfUp } : Surcharge).amount base

/-- Lazio by year (`Params.lazio2022Exempt`): 2022 1,73 % to 35.000 (else 1,73/3,33 less 300 up to 40.000);
2023 1,73/3,33; 2024 1,73 % to 28.000, else 1,73/3,33 less 60 up to 35.000 (not cumulable); 2025 `lazio`.
`oecd`: the OECD's model leaves out Lazio's 2024 and 2025 reliefs (FINDINGS F1): plain 1,73/3,33. -/
def lazioY (y : Nat) (oecd : Bool) (base : Int) : Int :=
  if base ≤ 0 then 0
  else if y ≤ 2022 then
    (if base ≤ lazio2022Exempt then lazioLow.tax Rule.unitHalfUp base
     else pos (lazioHigh.tax Rule.unitHalfUp base - (if base ≤ lazio2022DetrHi then lazio2022Detr else 0)))
  else if y = 2023 ∨ oecd then lazioHigh.tax Rule.unitHalfUp base
  else if y = 2024 then
    (if base ≤ lazioNoMagg then lazioLow.tax Rule.unitHalfUp base
     else pos (lazioHigh.tax Rule.unitHalfUp base - (if base ≤ lazioDetrHi then lazioDetr else 0)))
  else lazio base

theorem lazioY_2025 (base : Int) : lazioY 2025 false base = lazio base := by
  unfold lazioY lazio; split <;> simp_all

def Irpef.dovuta (t : Irpef) : Bool := decide (t.netta > 0)
def Irpef.regionale (t : Irpef) (y : Nat := 2025) (oecd : Bool := false) : Int :=
  if t.dovuta then lazioY y oecd t.imponibile else 0
def Irpef.comunale (t : Irpef) (y : Nat := 2025) : Int := if t.dovuta then romaY y t.imponibile else 0

end ITTax
