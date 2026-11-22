import TaxKernel.Rounding

/-!
# TaxKernel.Surcharge: a rate on a base with an exemption limit, a deduction and a glide zone

One object covers the surcharges and levies of the 20 systems:
* % of tax: Germany's Solidaritätszuschlag (SolZG § 3, § 4: 5.5 % of income tax, nothing up to the Freigrenze,
  then at most 11.9 % of the excess: `{ rate := 550, exempt := 19950, glide := 1190 }`), Japan's 復興特別所得税
  (2.1 % of income tax), municipal surcharges set as % of state tax;
* % of income: Australia's Medicare levy (2 %, nothing up to a threshold, shade-in at 10 % of the excess),
  France's CEHR (3 %/4 % above thresholds: a `Schedule` is better there), US Additional Medicare / NIIT
  (`deduct` = the threshold: only the excess is charged).

    ticks base = 0                                           if base ≤ exempt
               = min (rate · (base − deduct)⁺) (glide · (base − exempt))   if glide > 0
               = rate · (base − deduct)⁺                      otherwise

Generic theorems (`TaxKernel.Theorems.Surcharge`): `ticks_mono` (for `0 ≤ rate`, `0 ≤ glide`, `deduct ≤ exempt`
or `glide = 0` with `exempt ≤ deduct`: monotone in the base, so tax + surcharge(tax) stays monotone, `withSurcharge_mono`);
`ticks_le_rate` (never more than `rate` of the base above `deduct`); and the notch theorem `exempt_notch`: with no
glide zone and `deduct < exempt`, one more unit of base above `exempt` costs `rate · (exempt + 1 − deduct)`, a
jump (a cliff the scanners look for).
-/

namespace TaxKernel

structure Surcharge where
  /-- bp of the base -/
  rate : Int
  /-- base at or below this: nothing (Freigrenze, exemption limit) -/
  exempt : Int := 0
  /-- only the base above this is charged (Freibetrag; US NIIT threshold) -/
  deduct : Int := 0
  /-- glide zone rate, bp (0: none): the surcharge is at most `glide` × (base − exempt) -/
  glide : Int := 0
  /-- rounding of the result -/
  round : Rule := {}
  deriving Repr, DecidableEq, Inhabited

namespace Surcharge

def ticks (s : Surcharge) (base : Int) : Int :=
  if base ≤ s.exempt then 0
  else if 0 < s.glide then min (s.rate * pos (base - s.deduct)) (s.glide * (base - s.exempt))
  else s.rate * pos (base - s.deduct)

def amount (s : Surcharge) (base : Int) : Int := s.round.ofTicks (s.ticks base)

/-- Germany's Soli shape: `rate` of tax above the exemption limit, glide zone `glide` (SolZG § 4). -/
def withGlide (rate exempt glide : Int) : Surcharge := { rate, exempt, glide }

/-- A flat % of the whole base (JP 復興特別所得税: 210 bp). -/
def flatPct (rate : Int) : Surcharge := { rate }

/-- A % of the base above a threshold (US NIIT, Additional Medicare). -/
def above (rate threshold : Int) : Surcharge := { rate, exempt := threshold, deduct := threshold }

end Surcharge
end TaxKernel
