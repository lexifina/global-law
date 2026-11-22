import R4Common.Pkgs

/-! # R4Common: business licence taxes (patente / contribution des patentes / taxe professionnelle / contribution
économique locale) of a company (P7, OECD 5200: permission to carry on a trade).

The usual francophone shape: a fixed duty keyed on last year's turnover (a tariff by turnover tier, or a rate on
turnover with a floor and a cap per tier, or both, plus "so much per step of turnover or fraction" above the last
tier), a proportional duty on the rental value of the business premises (rented / owned rates; often at least a
fraction of the fixed duty), sometimes a duty on value added (SN), and additional centimes on the principal.

Inputs: the company's `turnover`; from the input line's `company` object, `premisesRentalValue` (annual rental value
or rent of the business premises, default 0), `premisesOwned` (default false) and `valueAdded` (default: profit +
payroll). Households (and every 1.x line) get no charge. Rates are in parts per million (ppm). -/

namespace R4
open TaxKernel TaxKernel.Global

/-- A tier of a turnover-keyed duty: inclusive turnover ceiling, rate on turnover (ppm), floor, cap (−1: none). -/
structure LicTier where
  ceil : Int
  ppm : Int := 0
  floor : Int := 0
  cap : Int := -1
  /-- constant added before the floor and cap (e.g. TD: 0,1 % up to 2 bn, then 0,1 % of a tenth of the excess) -/
  add : Int := 0
  deriving Repr, Inhabited, BEq

structure Licence where
  /-- fixed-duty tiers by turnover: the first tier whose ceiling is at least the turnover applies -/
  tiers : List LicTier := []
  /-- the tier above the last ceiling (its `ceil` is ignored) -/
  top : LicTier := { ceil := 0 }
  /-- above the last ceiling: + `stepAmt` per `stepSize` of turnover beyond it, or fraction of it -/
  stepSize : Int := 0
  stepAmt : Int := 0
  /-- below this turnover the lower classes are not modelled: no charge -/
  fromTurnover : Int := 0
  /-- proportional duty on the premises' rental value (ppm): rented or default / owned (−1: the same) -/
  rentPpm : Int := 0
  ownedPpm : Int := -1
  /-- the proportional duty is at least the fixed duty / `propMinDen` (0: no floor) -/
  propMinDen : Int := 0
  /-- duty on value added (ppm), value added capped at `vaCapPpm` of turnover (0: no cap), at least `vaMinPpm` of turnover -/
  vaPpm : Int := 0
  vaCapPpm : Int := 0
  vaMinPpm : Int := 0
  /-- additional centimes on the principal (ppm), or on the fixed duty only when `surchargeFixedOnly` -/
  surchargePpm : Int := 0
  surchargeFixedOnly : Bool := false
  /-- a flat fee per licence (e.g. TD: ONASA 480 F) -/
  flat : Int := 0
  /-- each amount rounded down to a multiple of `step` -/
  step : Int := 1
  deriving Repr, Inhabited

def ppmOf (r x : Int) : Int := divR .down (r * pos x) 1000000

def LicTier.amount (t : LicTier) (x : Int) : Int :=
  let v := max t.floor (t.add + ppmOf t.ppm x)
  if t.cap < 0 then v else min v t.cap

def Licence.fixed (l : Licence) (x : Int) : Int :=
  match l.tiers.find? (fun t => x ≤ t.ceil) with
  | some t => t.amount x
  | none =>
    let last := (l.tiers.getLast?.map (·.ceil)).getD 0
    l.top.amount x + (if l.stepSize > 0 then l.stepAmt * ((pos (x - last) + l.stepSize - 1) / l.stepSize) else 0)

/-- The `company` object of the input line (null when absent). -/
def companyJson (g : CanonGlobal) : Lean.Json :=
  match g.raw.getObjVal? "company" with
  | .ok j => j
  | _ => Lean.Json.null

/-- (event, base, amount) of each component, zero amounts included. -/
def Licence.parts (l : Licence) (turnover rv : Int) (owned : Bool) (va : Int) : List (String × Int × Int) :=
  let rd : Int → Int := fun x => if l.step > 1 then x / l.step * l.step else x
  let fx := rd (l.fixed turnover)
  let rate := if owned && l.ownedPpm ≥ 0 then l.ownedPpm else l.rentPpm
  let pr := if l.rentPpm == 0 && l.ownedPpm ≤ 0 then 0 else
    rd (max (ppmOf rate rv) (if l.propMinDen > 0 then fx / l.propMinDen else 0))
  let vab := if l.vaCapPpm > 0 then min (pos va) (ppmOf l.vaCapPpm turnover) else pos va
  let vd := if l.vaPpm == 0 then 0 else rd (max (ppmOf l.vaPpm vab) (ppmOf l.vaMinPpm turnover))
  let sb := if l.surchargeFixedOnly then fx else fx + pr + vd
  let sc := rd (ppmOf l.surchargePpm sb)
  [("fixed duty", turnover, fx), ("proportional duty (rental value)", rv, pr), ("value-added duty", vab, vd),
   ("additional centimes", sb, sc), ("flat fee", 0, l.flat)]

def licenceFamily (oecd : Oecd) (name : String) (l : Licence) (statute : String) : Family :=
  { name := s!"{oecd.code} {name}", covers := [oecd],
    run := fun _ g _ =>
      if g.entity != .company || g.company.turnover < l.fromTurnover then [] else
      let cj := companyJson g
      let va0 := intField cj "valueAdded" (-1)
      let va := if va0 < 0 then g.company.profit + g.company.payroll else va0
      ((l.parts g.company.turnover (intField cj "premisesRentalValue") (boolField cj "premisesOwned") va).filter
        (·.2.2 != 0)).map fun (ev, b, a) =>
          flatCharge oecd name a (event := ev) (level := .local) (statute := statute) (base := b) }

-- BJ-like: 70 000 up to 1 bn, + 10 000 per bn or fraction; 17 % of rental value, at least a third of the fixed duty
def tLic : Licence where
  tiers := [{ ceil := 1000000000, floor := 70000, cap := 70000 }]
  top := { ceil := 0, floor := 70000, cap := 70000 }
  stepSize := 1000000000
  stepAmt := 10000
  rentPpm := 170000
  propMinDen := 3
#guard tLic.fixed 3000000000 == 90000
#guard tLic.fixed 3000000001 == 100000
#guard (tLic.parts 500000000 100000 false 0).map (·.2.2) == [70000, 23333, 0, 0, 0]
-- TD-like: 0,1 % up to 2 bn, above it 1 800 000 + 0,01 % (a tenth of the excess at 0,1 %); 20 % centimes on it only
def tLic2 : Licence where
  tiers := [{ ceil := 2000000000, ppm := 1000 }]
  top := { ceil := 0, ppm := 100, add := 1800000 }
  rentPpm := 100000
  surchargePpm := 200000
  surchargeFixedOnly := true
  flat := 480
#guard (tLic2.parts 3000000000 60000000 false 0).map (·.2.2) == [2100000, 6000000, 0, 420000, 480]

end R4
