import NLTax.Years

/-!
# NLTax.Tax: the Wet IB 2001, the Wfsv premies and the kortingen, provision by provision

All amounts in cents. Exact intermediate values ("ticks") are kept in cents × bp (or cents × pcm) and rounded down
to the cent once, where an amount is final; the statute itself writes no rounding for these amounts (see
`Params.lean`).
-/

namespace NLTax
open TaxKernel

/-- `max 0 x` (local copy so that proofs can unfold it). -/
@[reducible] def p0 (x : Int) : Int := max 0 x

/-! ## Box 1 tariff -/

/-- The statute's table (art. 2.10 lid 1), in cents × bp: kolom III plus kolom IV % of the excess over kolom I. The
row is chosen by "van meer dan [I] maar niet meer dan [II]". -/
def Table3.ticks (t : Table3) (x : Int) : Int :=
  if x ≤ t.b1 then t.r1 * p0 x
  else if x ≤ t.b2 then t.c2 * 10000 + t.r2 * (x - t.b1)
  else t.c3 * 10000 + t.r3 * (x - t.b2)

/-- The same three rates as a kernel `Schedule` (the exact sum over bands). This is what the OECD computes; it
differs from the statute's table because kolom III is rounded down to whole euros (`Theorems.lean`). -/
def Table3.bands (t : Table3) : Schedule := Schedule.ofList [(0, t.r1), (t.b1, t.r2), (t.b2, t.r3)]

/-- Box-1 tax part (cents): statute table, or the band sum when `bandSum` (OECD method). -/
def box1Tax (t : Table3) (bandSum : Bool) (x : Int) : Int :=
  if bandSum then (t.bands.ticks x) / 10000 else (t.ticks x) / 10000

/-- Art. 2.10 lid 2: the extra 12,02 % on grondslagverminderende posten that fall in the top band (cents). -/
def grondslagExtra (x posten : Int) (y : YP := y2025) : Int :=
  y.grondslagRate * min (p0 posten) (p0 (x + p0 posten - y.t210.b2)) / 10000

/-! ## Box 2 (art. 2.12) -/

def box2Ticks (x : Int) (y : YP := y2025) : Int :=
  if x ≤ y.box2B1 then y.box2R1 * p0 x else y.box2C2 * 10000 + y.box2R2 * (x - y.box2B1)

def box2BandTicks (x : Int) (y : YP := y2025) : Int := (Schedule.ofList [(0, y.box2R1), (y.box2B1, y.box2R2)]).ticks x

/-! ## Premies volksverzekeringen (Wfsv art. 8 lid 3, 10, 11) -/

/-- Premie-inkomen capped at "het als eerste vermelde bedrag in kolom II van de tarieftabel in artikel 2.10"
(2.10a for those born before 1946). -/
def premieBase (pre1946 : Bool) (x : Int) (y : YP := y2025) : Int := min (p0 x) (if pre1946 then y.t210a.b1 else y.t210.b1)

/-- Premie (cents) at the summed rate; the AOW premie is not due from the AOW age (Wfsv art. 10 lid 2). -/
def premie (aowAged pre1946 : Bool) (x : Int) (y : YP := y2025) : Int :=
  ((if aowAged then 0 else pAOW) + pAnw + pWlz) * premieBase pre1946 x y / 10000

/-! ## Heffingskortingen (art. 8.10, 8.11, 8.14a, 8.17, 8.18), in cents × pcm -/

/-- Art. 8.10 lid 2. -/
def ahkNum (vi : Int) (y : YP := y2025) : Int := p0 (y.ahkMax * 100000 - y.ahkRate * p0 (vi - y.ahkStart))

/-- Art. 8.11 lid 2 a-d. -/
def akNum (ai : Int) (y : YP := y2025) : Int :=
  p0 (min (min (min (y.akRateA * ai) (y.akCapA * 100000) + y.akRateB * p0 (ai - y.akStartB)) (y.akCapB * 100000)
      + y.akRateC * p0 (ai - y.akStartC)) (y.akCapC * 100000)
    - y.akRateD * p0 (ai - y.akStartD))

/-- Art. 8.14a lid 2 (the conditions of lid 1 are checked by the caller). -/
def iackNum (ai : Int) (y : YP := y2025) : Int := min (y.iackRate * p0 (ai - y.iackStart)) (y.iackMax * 100000)

/-- Art. 8.17 lid 2. -/
def okNum (vi : Int) (y : YP := y2025) : Int := p0 (y.okMax * 100000 - y.okRate * p0 (vi - y.okStart))

/-- Cents from a pcm-scaled amount, rounded down. -/
def ofPcm (n : Int) : Int := n / 100000

/-! ## The split of the standaardheffingskorting (art. 8.3-8.7) -/

/-- The parts of one person's kortingen: income tax, and premies volksverzekeringen (AOW, Anw, Wlz), in cents.
`main` = AHK + AK + IACK (+ jonggehandicaptenkorting, not modelled); `old` = ouderenkorting + alleenstaande
ouderenkorting (+ groene beleggingen, not modelled), which art. 8.7 splits without the AOW percentage. -/
structure Split where
  ib : Int
  aow : Int
  anw : Int
  wlz : Int
  deriving Repr

def Split.prem (s : Split) : Int := s.aow + s.anw + s.wlz
def Split.total (s : Split) : Int := s.ib + s.prem

/-- Art. 8.3: the IB part is "het deel ... dat tot de standaardheffingskorting in dezelfde verhouding staat als het
belastingtarief eerste schijf staat tot het gecombineerde heffingspercentage" (8,17/35,82); art. 8.4-8.6 the premium
parts; art. 8.7 for `old`: the percentage is reduced by the AOW premium and the AOW part is nil. Wfsv art. 12 lid 1:
the AOW part only "indien betrokkene premieplichtig is voor de algemene ouderdomsverzekering". Each part rounded
down to the cent; for an insured person the Wlz part takes the remainder so that the parts add up to the korting. -/
def split (main old : Int) (aowInsured : Bool) (y : YP := y2025) : Split :=
  let g := y.t210.r1 + pAOW + pAnw + pWlz
  let g7 := y.t210.r1 + pAnw + pWlz
  let ib := y.t210.r1 * main / g + y.t210.r1 * old / g7
  let aow := if aowInsured then pAOW * main / g else 0
  let anw := pAnw * main / g + pAnw * old / g7
  let wlz := if aowInsured then main + old - ib - aow - anw else pWlz * main / g + pWlz * old / g7
  { ib, aow, anw, wlz }

/-- Art. 2.7 lid 1 and 3, Wfsv art. 9, art. 8.8: the IB and premium kortingen are set off against the tax and the
premie; the part one cannot absorb is set off against the other; the total never exceeds the total levy. Returns
(income tax due, premie due), both ≥ 0. -/
def setOff (tax prem kIb kPrem : Int) : Int × Int :=
  let t := tax - kIb
  let p := prem - kPrem
  if t < 0 then (0, p0 (p + t)) else if p < 0 then (p0 (t + p), 0) else (t, p)

/-! ## Box 3 (art. 5.2, 5.3, 5.5) for one fiscal unit (a person, or partners together, art. 5.2 lid 5) -/

structure Box3 where
  /-- rendementsgrondslag (cents) -/
  rg : Int
  /-- forfaitair rendement (cents × bp) -/
  rendTicks : Int
  /-- grondslag sparen en beleggen (cents) -/
  grondslag : Int
  /-- voordeel uit sparen en beleggen (cents), before allocation -/
  voordeel : Int
  /-- 2022 (round 10): the Wet rechtsherstel box 3 voordeel before allocation, and whether the 2022 rendementsklassen
  regime applies (then partners compare per allocated share, `box3Shares`). -/
  rhVoordeel : Int := 0
  klassen : Bool := false
  deriving Repr

/-- `bank`, `other`, `debts` at 1 January (cents); `n` = 1 or 2 persons (heffingvrij vermogen and debt threshold
counted once per person). -/
def box3New (bank other debts : Int) (n : Int) (y : YP := y2025) : Box3 :=
  let d := p0 (debts - n * y.debtThreshold)
  let rg := bank + other - d
  let rend := p0 (y.box3Bank * bank + y.box3Other * other - y.box3Debt * d)
  let gr := p0 (rg - n * y.hvv)
  -- art. 5.2 lid 1-2: voordeel = (rendement / rendementsgrondslag) × grondslag
  let v := if rg ≤ 0 then 0 else rend * gr / (rg * 10000)
  { rg, rendTicks := rend, grondslag := gr, voordeel := v }

/-- Wet IB 2022 art. 5.2 lid 1 (rendementsklassen) on a grondslag `gr` (cents) for `n` persons: cents x bp. -/
def klassenTicks (gr n : Int) : Int :=
  let b1 := n * eur 50650
  let b2 := n * eur 962350
  let t1 := min gr b1
  let t2 := min (p0 (gr - b1)) (b2 - b1)
  let t3 := p0 (gr - b2)
  let k1 := (67 * t1 + 21 * t2) / 100
  let k2 := gr - k1
  553 * k2 - 1 * k1

/-- Box 3 for the year: 2022 the lower of the 2022 statutory voordeel and the Wet rechtsherstel box 3 one (art. 1
lid 4); other years `box3New`'s method with the year's percentages. -/
def box3 (bank other debts : Int) (n : Int) (y : YP := y2025) : Box3 :=
  let r := box3New bank other debts n y
  if !y.box3Klassen then r else
  let vOld := p0 (klassenTicks r.grondslag n) / 10000
  let r := { r with rhVoordeel := r.voordeel, klassen := true }
  if vOld < r.voordeel then { r with voordeel := vOld } else r

/-! ## Kinderbijslag and kindgebonden budget -/

/-- AKW art. 12 lid 3: two quarters at the January amounts and two at the July amounts (age constant over the year). -/
def kinderbijslag (ages : List Nat) (y : YP := y2025) : Int := ages.foldl (fun a k => a + 2 * y.kbQ1 k + 2 * y.kbQ3 k) 0

/-- Wet op het kindgebonden budget art. 2 lid 2-8 (cents). `toets` = (gezamenlijk) toetsingsinkomen (cents). -/
def kgb (ages : List Nat) (partner : Bool) (toets wealth : Int) (y : YP := y2025) : Int :=
  let kids := ages.filter (· < 18)
  let n : Int := kids.length
  if n = 0 then 0
  else if wealth > (if partner then y.kgbWealthPartners else y.kgbWealthSingle) then 0
  else
    let base := y.kgbBase n + kids.foldl (fun a k => a + (if k ≥ 16 then y.kgb16 else if k ≥ 12 then y.kgb12 else 0)) 0
    let amt := base + (if partner then 0 else y.kgbAlo)
    -- reduction in tenths of a cent × pcm: 7,10 % of (toets − drempel)
    let dr := y.kgbDrempelMilli + (if partner then 10 * y.kgbPartnerExtra else 0)
    let red := y.kgbRate * p0 (10 * toets - dr)
    p0 (amt * 1000000 - red) / 1000000

/-- Partners' box-3 voordeel for an allocation of `s` % to the first partner (Wet IB art. 2.17). 2022 (round 10): Wet IB
2022 art. 5.2 lid 2 applies the rendementsklassen table to each partner's allocated part of the joint grondslag, and the
Wet rechtsherstel box 3 (art. 3 lid 4) gives each partner the allocated part of the joint rechtsherstel voordeel; art. 1
lid 4 keeps, per assessment, the lower of the two. Other years: the joint voordeel split by `s`. -/
def box3Shares (b : Box3) (s : Int) : Int × Int :=
  if b.klassen then
    let gp := b.grondslag * s / 100
    let gq := b.grondslag - gp
    let rp := b.rhVoordeel * s / 100
    let rq := b.rhVoordeel - rp
    (min rp (p0 (klassenTicks gp 1) / 10000), min rq (p0 (klassenTicks gq 1) / 10000))
  else
    let vp := b.voordeel * s / 100
    (vp, b.voordeel - vp)

end NLTax
