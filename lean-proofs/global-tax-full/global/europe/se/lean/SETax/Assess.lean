import SETax.Fees

/-!
# One person, one household: the assessment (slutlig skatt) for inkomstår 2025

Sweden taxes individuals; there is no joint assessment or splitting. For each adult:

1. Inkomst av tjänst = wages + pension; näringsverksamhet = self-employment profit less egenavgifter (`Fees`).
   No allmänna avdrag are modelled (private pension saving is deductible only for those without pension rights in
   employment, IL 59 kap. 3 §; listed in `unsupported` when given).
2. Fastställd förvärvsinkomst (1 kap. 5 §), grundavdrag (63 kap.), beskattningsbar förvärvsinkomst (BFI).
3. Kommunal inkomstskatt = BFI × (kommunalskatt + regionskatt) (65 kap. 3 §), statlig inkomstskatt 20 % of BFI
   above the skiktgräns (65 kap. 5 §), statlig skatt på kapital 30 % of the capital surplus (65 kap. 7 §); taxes in
   whole kronor, öretal dropped.
4. Skattereduktioner in the order of 67 kap. 2 § (`Reductions.applyReductions`).
5. Fees: allmän pensionsavgift, public service-avgift, begravningsavgift.

The household's interest, dividends, capital gains (listed shares, 30 % with no exemption: IL 42 kap., 48 kap.) and
rental income are split equally between two adults (contract). Rental income is taken as letting of a private home
(IL 42 kap. 30-31 §§: deduction "40 000 kronor per år" per dwelling, once per household here, plus "20 procent av
intäkten"). Optional extension fields: `interestPaid` (ränteutgifter, deductible in inkomstslaget kapital),
`seKommunBp` (the municipal rate in basis points, default Stockholm 3060), `seBegravningBp`.

Age convention: the contract's `age` is the age reached during 2025 (at 31 December). "Har fyllt 66 år vid
beskattningsårets ingång" (63 kap. 3 a §, 67 kap. 8 §) is then `age ≥ 67`; public service "vid beskattningsårets
ingång har fyllt 18 år" is `age ≥ 19`.
-/

namespace SETax
open TaxKernel

/-- Everything one adult's assessment produces. -/
structure PersonResult where
  old : Bool
  tjanst : Int
  naring : Int
  egenavg : Int
  ffi : Int
  ga : Int
  bfi : Int
  kapital : Int
  municipalTax : Int
  stateTaxEarned : Int
  stateTaxCapital : Int
  fee : Int
  jsaAmount : Int
  fiAmount : Int
  deficitAmount : Int
  giftAmount : Int
  used : CreditsUsed
  publicServiceFee : Int
  burialFee : Int
  deriving Repr, Inhabited

/-- One adult. `kap` = this adult's capital surplus (negative: underskott); `gifts` = this adult's gifts. -/
def person (p : Params) (stateFirst : Bool) (age : Nat) (wages selfEmp pension kap gifts : Int) : PersonResult :=
  let old := age ≥ p.oldAge
  let eg := egenavgifter age selfEmp
  let naring := pos selfEmp - eg
  let tjanst := pos wages + pos pension
  let f := ffi (tjanst + naring)
  let g := ga p old f
  let b := pos (f - g)
  let kt := (municipalSchedule p).ticks b / BP
  let st := (stateSchedule p).ticks b / BP
  let ct := (dual p).capitalTicks kap / BP
  let fee := pensionFeeOn p wages naring
  -- 67 kap. 6 §: arbetsinkomster are wages (SFB 59 kap. 8-12 §§) and self-employment income, not pensions
  let j := jsa p old (pos wages + naring) g
  let fi := fiCredit b
  let dc := deficitCredit p (pos (-kap))
  let gc := giftCredit gifts
  let u0 := applyReductions stateFirst { municipal := kt, state := st + ct } fee j fi dc gc
  -- lag (2021:930) 6-7 §§: made after the IL reductions, against municipal and state income tax
  let (_, left2) := useBoth stateFirst (tempCredit p.year (arbetsinkomst (pos wages + naring))) u0.left
  let u := { u0 with left := left2 }
  { old, tjanst, naring, egenavg := eg, ffi := f, ga := g, bfi := b, kapital := kap, municipalTax := kt,
    stateTaxEarned := st, stateTaxCapital := ct, fee, jsaAmount := j, fiAmount := fi, deficitAmount := dc,
    giftAmount := gc, used := u, publicServiceFee := publicService p (age ≥ 19) b,
    burialFee := begravningsavgift p b }

/-- Municipal tax left after the credits allocated to it (kommunal inkomstskatt to pay). -/
def PersonResult.municipalNet (r : PersonResult) : Int := r.used.left.municipal
/-- State income tax left (earned + capital). -/
def PersonResult.stateNet (r : PersonResult) : Int := r.used.left.state
/-- Social contributions: allmän pensionsavgift + egenavgifter. -/
def PersonResult.social (r : PersonResult) : Int := r.fee + r.egenavg
/-- Everything this person pays (taxes, fees, contributions). -/
def PersonResult.total (r : PersonResult) : Int :=
  r.municipalNet + r.stateNet + r.social + r.publicServiceFee + r.burialFee

/-- Capital surplus of the household before splitting (IL 42 kap.): interest, dividends, capital gains, rental
income after the 42 kap. 30-31 §§ deductions, less interest paid. -/
def capitalSurplus (c : Canon) : Int :=
  let r := pos c.rentalIncome
  let rentNet := pos (r - min r (40000 + 20 * r / 100))
  c.interest + c.dividends + c.capitalGains + rentNet - pos ((c.int? "interestPaid").getD 0)

/-- Household result. -/
structure HouseResult where
  persons : List PersonResult
  barnbidrag : Int
  deriving Repr, Inhabited

/-- Optional per-adult extension arrays (`"seKapital": [k1, k2]` overrides the equal split of the capital surplus;
`"seGifts": [g1, g2]` the split of gifts): used by the planning searches (who holds the loan, who gives). -/
def perAdult (c : Canon) (k : String) (i : Nat) : Option Int :=
  match c.raw.getObjVal? k with
  | .ok (.arr a) => match a[i]? with
    | some (.num n) => some (numToInt n)
    | _ => none
  | _ => none

def household (p : Params) (stateFirst : Bool) (c : Canon) : HouseResult :=
  let kap := capitalSurplus c
  let gifts := pos c.charitable
  let n := c.adults.length
  let one (i : Nat) (a : Adult) : PersonResult :=
    let k0 := if n = 2 then (if i = 0 then half1 kap else half2 kap) else kap
    let g0 := if n = 2 then (if i = 0 then half1 gifts else half2 gifts) else gifts
    let k := (perAdult c "seKapital" i).getD k0
    let g := (perAdult c "seGifts" i).getD g0
    person p stateFirst a.age a.wages a.selfEmployment a.pension k g
  { persons := (c.adults.zipIdx).map fun (a, i) => one i a,
    barnbidrag := barnbidragYear (c.childrenUnder 16) }

/-- Parameters for a household: the municipal rate may be overridden by the input field `seKommunBp`, the
begravningsavgift by `seBegravningBp`. -/
def paramsFor (base : Params) (c : Canon) : Params :=
  let q := yearParams base c.year
  { q with kommun := (c.int? "seKommunBp").getD q.kommun,
           begravning := (c.int? "seBegravningBp").getD q.begravning,
           begravning100k := match c.int? "seBegravning100k" with | some r => some r | none => q.begravning100k }

end SETax
