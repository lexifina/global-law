import LiTax.Params

/-!
# Liechtenstein 2025: Landessteuer on the Erwerb (SteG Art. 14-19), Gemeindezuschlag, AHV/IV/ALV

Unit: spouses are assessed jointly with tariff c (Art. 18 Abs. 3, Art. 19 Bst. c); a single adult with children uses
tariff b (single parent: reading of "Alleinerziehende im Sinne des Familienzulagengesetzes"); others tariff a.
Erwerb: wages less own AHV/IV/ALV contributions (Art. 16 Abs. 3 Bst. c) and 1 600 CHF (Abs. 2 Bst. c) per earner;
self-employment as given; AHV/IV pensions at 30 % (Abs. 2 Bst. d); less 12 700 CHF per child (Abs. 3 Bst. a); rounded
down to 10 CHF (Art. 18 Abs. 1). Interest, rent and other wealth income are not Erwerb (Art. 15 Abs. 1 Bst. a: taxed
through the Sollertrag on wealth, which the household line does not carry: unsupported); dividends (Abs. 2 Bst. n) and
private capital gains (Bst. m, o) are not taxed. Tax: the Art. 19 row "rate · x − subtract", not below 0, in Rappen,
rounded half-up to the franc at the end (reading). Gemeindezuschlag: % of the Landessteuer (Art. 75).
-/

namespace LiTax
open TaxKernel

/-- Art. 19 tax in Rappen for an Erwerb `x` (CHF). -/
def tariffRp (rows : List Row) (x : Int) : Int :=
  let r := (rows.filter (·.lo ≤ x)).getLast?.getD ⟨0, 0, 0⟩
  pos (x * r.rate / 100 - r.sub * 100)

def contrib (w : Int) : Int :=
  if w ≤ 0 then 0 else
  divR .halfUp (w * (ahv + iv)) TBP + divR .halfUp (min w alvCeiling * alv) TBP

def erwerbOf (w se pen : Int) : Int :=
  (if w > 0 then pos (w - contrib w - employmentExpenses) else 0) + se +
    (pos pen - divR .halfUp (pos pen * pensionDeductionRate) BP)

def out (c : Canon) : Out :=
  let as := c.adults
  let kids : Int := c.childrenUnder 18
  let joint := c.married && as.length == 2
  let rows := if joint then tariffC else if as.length == 1 && kids > 0 then tariffB else tariffA
  let units : List (List Adult) := if joint || as.length == 1 then [as] else as.map fun a => [a]
  let unitTax := fun (us : List Adult) (withKids : Bool) =>
    let e := sumInts (us.map fun a => erwerbOf a.wages a.selfEmployment a.pension)
    let e := pos (e - (if withKids then kids * childDeduction else 0))
    let e := e / 10 * 10
    (e, tariffRp rows e)
  let res := (units.zipIdx).map fun (u, i) => unitTax u (i == 0)
  let landRp := sumInts (res.map (·.2))
  let gzRp := divR .halfUp (landRp * gemeindeZuschlagMin) BP
  let unsup :=
    ["Gemeindezuschlag: default municipality Vaduz; its 2025 rate (set yearly by the Gemeinderat, Art. 75 Abs. 3) was not reached; the statutory minimum 150 % is used"] ++
    ["wealth tax (Sollertrag on net wealth, Art. 14 Abs. 2 Bst. l; rate set by the Finanzgesetz) not modelled: the household line carries no wealth"] ++
    (if c.interest != 0 || c.rentalIncome != 0 then ["interest/rentalIncome: not Erwerb (Art. 15 Abs. 1 Bst. a), taxed only through the Sollertrag on the underlying wealth (not modelled)"] else []) ++
    (if as.any (·.selfEmployment != 0) then ["selfEmployment: taken as net Erwerb (Art. 16 Abs. 2 Bst. b); AHV of the self-employed (8.25 %) not modelled"] else []) ++
    (if c.charitable != 0 || c.pensionContributions != 0 then ["charitable/pensionContributions: Art. 16 Abs. 3 Bst. e, h not modelled"] else []) ++
    ["insurance premiums (Art. 16 Abs. 3 Bst. d, up to 3 700 / 7 400 CHF + 2 200 per child) need the premiums paid: not deducted"]
  Out.make c "LI" "CHF" (divR .halfUp landRp 100) (localIncomeTax := divR .halfUp gzRp 100)
    (employeeSocial := sumInts (as.map fun a => contrib a.wages))
    (detail := [Out.d "taxableIncome" (sumInts (res.map (·.1))), Out.d "dividendsExempt" (pos c.dividends),
                Out.dStr "note" "SteG 2025 (Fassung 01.01.2025): Art. 19 tariff a/b/c on the Erwerb after AHV/IV/ALV, 1 600 CHF and 12 700 per child; Gemeindezuschlag at the 150 % minimum (Vaduz rate not cited)"])
    (unsupported := unsup)

def country : Country :=
  { code := "LI", name := "Liechtenstein (Landessteuer, Gemeindezuschlag, AHV/IV/ALV)", currency := "CHF", year := "2025",
    compute := out }

end LiTax
