import FrTax.Liquidation

/-!
# Statute-faithful additions for the loophole catalogue (`~/cmp/loop/fr`)

Not in the base model (`~/fr/lean/FrTax`, copied here unchanged). Each addition is a reduction or a computation
rule entered per return, applied on top of `FrTax.compute`:
- investment reductions in the global cap: Pinel/Denormandie (art. 199 novovicies, entered as the reduction of the
  year), IR-PME (art. 199 terdecies-0 A, 18 % of the subscriptions, at most 50 000 € / 100 000 € for a couple),
  Girardin industriel (art. 199 undecies B, entered as the reduction of the year);
- reductions outside the cap: Malraux (art. 199 tervicies, 30 % of at most 400 000 €; excluded from the cap from
  income 2013, BOI-IR-LIQ-20-20-10-10 § 90-95), prestation compensatoire in capital (art. 199 octodecies, 25 % of at
  most 30 500 €; listed as excluded in the same BOFiP);
- the global cap (art. 200-0 A, 1): 10 000 €, raised to 18 000 € with the outre-mer reductions, the Girardin
  industriel reduction (with retrocession at 56 %) counting for 44 % (BOI-IR-LIQ-20-20-10-30);
- the quotient for exceptional income (art. 163-0 A, I, "en ajoutant le quart du revenu exceptionnel net à son
  revenu net global imposable et en multipliant par quatre la cotisation supplémentaire ainsi obtenue"), the RFR,
  CEHR taking the income in full (art. 223 sexies, I, 1, "sans qu'il soit fait application des règles de quotient";
  its smoothing of II needs earlier years and is not applied); for the CDHR the exceptional income, and the income
  tax and CEHR on it computed without the quotient, count for a quarter (art. 224, II, ninth paragraph; IV, A, 1°;
  IV, B, 3°);
- the CDHR adds back to its income tax the Girardin industriel reduction (art. 224, IV, A, 2°) and, for
  investments made up to 31 December 2025, the outre-mer, PME, Malraux and Pinel reductions (loi n° 2025-127,
  art. 10, II; BOI-IR-CDHR-10 § 250-270), so those keep their value for a CDHR payer; the prestation compensatoire
  (not listed) does not.
Simplifications: the cap is taken from the investments only (the home-help and childcare credits computed by the
model are kept whole and only reduce the room); reductions are capped before imputation (no carry-forward).
-/

namespace FrLoop
open FrTax

structure Extra where
  pinel : Int := 0
  pme : Int := 0
  girardin : Int := 0
  malraux : Int := 0
  pcCapital : Int := 0
  exc : Int := 0
  deriving Repr

def pmeRed (d : Decl) (e : Extra) : Int := pct 1800 (min (pos e.pme) (if d.couple then 100000 else 50000))
def malrauxRed (e : Extra) : Int := pct 3000 (min (pos e.malraux) 400000)
def pcRed (e : Extra) : Int := pct 2500 (min (pos e.pcCapital) 30500)

/-- art. 200-0 A, 1: the allowed (Pinel, PME, Girardin) reductions. -/
def capNiches (p : Params) (d : Decl) (e : Extra) : Int × Int × Int :=
  let cr := homeHelpCredit d + childcareCredit p d
  let room := pos (10000 - cr)
  let pin := min (pos e.pinel) room
  let pm := min (pmeRed d e) (room - pin)
  let gRoom := pos (18000 - min 10000 (cr + pin + pm))
  let gir := min (pos e.girardin) ((gRoom * 100) / 44)
  (pin, pm, gir)

def computeX (p : Params) (d : Decl) (e : Extra) : Result :=
  let r := compute p d
  let (pin, pm, gir) := capNiches p d e
  let listed := pin + pm + gir + malrauxRed e
  let vl := flatLevyIncome d
  let ex := if vl = 0 then pos e.exc else 0
  let tax := r.capped.tax + (if ex > 0 then 4 * ((capped p d (r.rni + ex / 4)).tax - r.capped.tax) else 0)
  let dcote := decote p d tax
  let afterDec := tax - dcote
  let redu := min afterDec (reductions p d (r.rni + ex) + listed + pcRed e)
  let before := afterDec - redu + r.flat
  let ab := foreignCredit d before
  let cr := r.credits
  let rf := r.rfr + ex
  let ce := cehr d rf
  let net := if ab + cr ≥ before then before - ab - cr else if before + ce < 61 then 0 else before - ab - cr
  let listedUsed := min listed redu
  let cap' : Capped := { r.capped with tax := tax }
  -- art. 224, II, ninth paragraph and IV: for the CDHR the exceptional income and the tax and CEHR on it (without
  -- the quotient) count for a quarter
  let ordEx := (capped p d (r.rni + ex)).tax - r.capped.tax
  let taxC := before - (tax - r.capped.tax) + ordEx / 4
  let ceC := cehr d r.rfr + (ce - cehr d r.rfr) / 4
  let cd := cdhr d (r.rfr + ex / 4) (taxC - (cr - d.get "2CK") + flatLevyPaid d + pct 1900 (d.get "3VZ") + listedUsed) ceC
  Result.mk r.quarters r.rng (r.rni + ex) cap' dcote redu cr r.flat ab (before - ab) net rf r.social ce cd

end FrLoop
