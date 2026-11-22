import ChTax.Assess

/-!
# Switzerland (federal + canton and City of Zürich), 2025: the household in, the contract out

Layers (family decision for CH, see PROGRESS.md): `incomeTax` = direct federal tax (DBG); `localIncomeTax` =
Zürich Staatssteuer (einfache Staatssteuer × 98 %) + City of Zürich Gemeindesteuer (× 119 %) + Personalsteuer
(24 per adult) [+ Kirchensteuer × 10 % with `--church reformed|catholic`]. `--canton-only` is the literal
CONTRACT38 reading (canton only: no Gemeindesteuer, no Personalsteuer). Employee social contributions: AHV/IV/EO and
ALV (+ NBU with `--nbu BP`); the occupational pension (BVG) is deducted for tax but not counted in
`employeeSocial` (as the OECD does). Benefits: family allowances (FamZG, EG FamZG ZH).

Options: `--oecd` (OECD Taxing Wages conventions: BVG 7.83 % of the wage above 26 460, Berufskosten on the wage
before BVG, 268 per child and month, federal band sum), `--bandsum`, `--canton-only`, `--church reformed|catholic`,
`--nbu BP`, `--ins-literal`, `--estv` (ESTV calculator conventions: NBU 0.4 %, family allowances left out of
taxable income; BVG taken from the input fields `bvg1`/`bvg2`).
Extra input fields: `church` ("reformed"/"catholic"/"none"), `qualifying` (bool: dividends from a ≥ 10 %
participation), `bvg1`/`bvg2` (employee BVG contribution in francs, overriding the statutory minimum),
`buyIn1`/`buyIn2` (pension-fund buy-ins), `noFund1`/`noFund2` (no pension fund: Säule 3a cap 20 % / 36 288),
`capitalWithdrawal` (pension capital paid out to adult 1 this year, DBG Art. 38 / StG ZH § 37).
-/

namespace ChTax
open TaxKernel

structure Opts where
  oecd : Bool := false
  bandsum : Bool := false
  cantonOnly : Bool := false
  church : Option String := none
  nbuBp : Int := 0
  insLiteral : Bool := false
  /-- family allowances counted in taxable income (DBG Art. 17 Abs. 1); the ESTV calculator leaves them out -/
  allowInIncome : Bool := true
  deriving Repr, Inhabited

partial def parseOpts : List String → Opts → Opts
  | "--oecd" :: r, o => parseOpts r { o with oecd := true, bandsum := true }
  | "--bandsum" :: r, o => parseOpts r { o with bandsum := true }
  | "--canton-only" :: r, o => parseOpts r { o with cantonOnly := true }
  | "--church" :: c :: r, o => parseOpts r { o with church := some c }
  | "--nbu" :: b :: r, o => parseOpts r { o with nbuBp := (b.toInt?).getD 0 }
  | "--ins-literal" :: r, o => parseOpts r { o with insLiteral := true }
  | "--estv" :: r, o => parseOpts r { o with nbuBp := 40, allowInIncome := false }
  | _ :: r, o => parseOpts r o
  | [], o => o

/-! ## Employee social contributions -/

/-- AHV/IV/EO on wages (Rp): 5.3 %; after the reference age only above the 16 800 allowance. -/
def ahvWageRp (age : Nat) (wage : Int) : Int :=
  let base := if age ≥ referenceAge then pos (wage - ahvRetireeFree) else pos wage
  divR .halfUp (base * ahvEmployeeBp) 100

/-- AHVV Art. 21 sinkende Skala: the AHV rate (bp) for self-employed income `y` (rounded down to 100). -/
def ahvSelfRateBp (y : Int) : Int :=
  if y < 10100 then 435 else
  match (ahvSelfScale.reverse.find? fun (lo, _) => decide (lo ≤ y)) with
  | some (_, r) => r
  | none => 435

/-- Self-employed AHV/IV/EO (Rp): AHV by the scale, IV+EO scaled in the same proportion (IVG Art. 3 Abs. 1 / EOG:
"in gleicher Weise abgestuft"; the IVV/EOV tables round each rate, a convention here). -/
def ahvSelfRp (age : Nat) (selfInc : Int) : Int :=
  let y := (if age ≥ referenceAge then pos (selfInc - ahvRetireeFree) else pos selfInc) / 100 * 100
  if y ≤ 0 then 0 else
  let r := ahvSelfRateBp y
  let total := r + divR .halfUp (r * ivEoSelfBp) ahvSelfBp
  divR .halfUp (y * total) 100

/-- ALV (Rp): 1.1 % up to 148 200; not after the reference age (AVIG Art. 2 Abs. 2 lit. c). -/
def alvRp (age : Nat) (wage : Int) : Int :=
  if age ≥ referenceAge then 0 else divR .halfUp (min (pos wage) uvgMaxInsured * alvEmployeeBp) 100

/-- NBU (Rp) at an insurer-specific rate `bp` (UVG Art. 91 Abs. 2), up to the insured maximum. -/
def nbuRp (bp : Int) (wage : Int) : Int := divR .halfUp (min (pos wage) uvgMaxInsured * bp) 100

/-- Statutory minimum BVG employee contribution (Rappen): half the age credit on the coordinated wage. -/
def bvgStatutoryRp (age : Nat) (wage : Int) (yr : Nat := 2025) : Int :=
  let F := fedFor yr
  if wage ≤ F.bvgEntry then 0 else
  let coord := max F.bvgCoordMin (min wage F.bvgCoordHi - F.bvgCoordLo)
  divR .halfUp (coord * bvgCreditBp age) 200

/-- OECD convention: 7.83 % of the wage above 26 460. -/
def bvgOecdRp (wage : Int) : Int := divR .halfUp (pos (wage - bvgCoordLo) * oecdBvgBp) 100

/-! ## Family allowances -/

/-- Annual allowance for one child (francs). -/
def famAllowance (oecd : Bool) (age : Nat) (yr : Nat := 2025) : Int :=
  let F := fedFor yr
  if oecd then (if age < 16 then 12 * kzOld else if age < 25 then 12 * azMonthly else 0)
  else if age < 12 then 12 * F.kzYoung else if age < 16 then 12 * F.kzOld else if age < 25 then 12 * F.az else 0

/-! ## The household -/

def personOf (o : Opts) (c : Canon) (i : Nat) (a : Adult) : Person :=
  let k := toString (i + 1)
  let ahv := ahvWageRp a.age a.wages + ahvSelfRp a.age a.selfEmployment
  let bvg := match c.int? ("bvg" ++ k) with
    | some v => 100 * v
    | none => if o.oecd then bvgOecdRp a.wages else bvgStatutoryRp a.age a.wages c.year
  { age := a.age, wage := a.wages, self := a.selfEmployment, pension := a.pension, ahvRp := ahv,
    alvRp := alvRp a.age a.wages, nbuRp := nbuRp o.nbuBp a.wages, bvgRp := bvg,
    buyIn := (c.int? ("buyIn" ++ k)).getD 0 }

/-- Säule 3a cap of a person (BVV 3 Art. 7 Abs. 1). -/
def p3aCap (c : Canon) (i : Nat) (p : Person) : Int :=
  let earn := p.wage + p.self
  if earn ≤ 0 then 0 else
  let noFund := (c.bool? ("noFund" ++ toString (i + 1))).getD (p.bvgRp = 0 && p.buyIn = 0)
  let F := fedFor c.year
  if noFund then min F.p3aWithout (earn / 5) else F.p3aWith

/-- The household's `pensionContributions` go to Säule 3a, adult 1 first, each up to their cap. -/
def allocate3a (c : Canon) (ps : List Person) : List Person :=
  let rec go (i : Nat) (left : Int) : List Person → List Person
    | [] => []
    | p :: rest =>
      let x := min (pos left) (p3aCap c i p)
      { p with p3a := x } :: go (i + 1) (left - x) rest
  go 0 c.pensionContributions ps

structure Result where
  fedRp : Int
  fedBeforeRp : Int
  fedTaxable : Int
  zhTaxable : Int
  zhSimpleRp : Int
  cantonRp : Int
  cityRp : Int
  churchRp : Int
  personal : Int
  fedCapRp : Int := 0
  zhCapSimpleRp : Int := 0
  deriving Repr, Inhabited

def churchMult (s : Option String) : Option Multiplier :=
  match s with
  | some "reformed" => some zhChurchReformedMult
  | some "catholic" => some zhChurchCatholicMult
  | _ => none

/-- Assess one return. -/
def assess (o : Opts) (cv : Conv) (church : Option String) (r : Ret) : Result :=
  let fti := taxable cv (fedLayerY (fedFor r.yr)) r
  let before := fedBeforeCreditRp o.bandsum r fti
  let fed := fedFinalRp before r.kidCredits (fedFor r.yr).childCreditRp
  let zti := taxable cv (zhLayerY (fedFor r.yr)) r
  let simple := zhSimpleRp r zti
  let canton := multRp (fedFor r.yr).zhCanton simple
  let city := if o.cantonOnly then 0 else multRp zhCityMult simple
  let ch := match churchMult church with | some m => multRp m simple | none => 0
  let pers := if o.cantonOnly then 0 else zhPersonalTax * r.persons.length
  { fedRp := fed, fedBeforeRp := before, fedTaxable := fti, zhTaxable := zti, zhSimpleRp := simple,
    cantonRp := canton, cityRp := city, churchRp := ch, personal := pers }

def rpToChf (x : Int) : Int := divR .halfUp x 100

/-- FamZG entitlement of a household: an earner at or above the minimum income (Art. 13 Abs. 3, no income test),
or else, as non-employed (Art. 19 Abs. 1bis), a taxable income of at most 45 360 (Art. 19 Abs. 2). -/
def famzgEntitled (earnings : List Int) (taxableIncome : Int) (nKids : Nat) : Bool :=
  nKids > 0 && (earnings.any (fun e => decide (e ≥ famzgMinIncome)) || decide (taxableIncome ≤ famzgNonEarnerMax))

def out (o : Opts) (c : Canon) : Out :=
  let cv : Conv := { berufBeforeBvg := o.oecd, insLiteral := o.insLiteral }
  let ps0 := (c.adults.zipIdx).map fun (a, i) => personOf o c i a
  let ps := allocate3a c ps0
  let n := c.nChildren
  let earner := ps.any fun p => decide (p.wage + p.self ≥ famzgMinIncome)
  let full := sumInts (c.children.map fun k => famAllowance o.oecd k.age c.year)
  let qual := (c.bool? "qualifying").getD false
  let church := match o.church with | some s => some s | none => c.str? "church"
  let retsOf (allowTx : Int) : List Ret :=
    match ps with
    | [a, b] =>
      if c.married then
        [{ persons := [a, b], married := true, kidHalves := 2 * n, kidCredits := n, interest := c.interest,
           dividends := c.dividends, qualifying := qual, rental := c.rentalIncome, famAllow := allowTx,
           charitable := c.charitable, yr := c.year }]
      else
        -- concubinage: two returns; the higher earner supports the children (Elterntarif, 263 credits, the
        -- allowances); the child deductions are split in half (DBG Art. 35 Abs. 1 lit. a, StG ZH § 34)
        let aFirst := decide (a.wage + a.self + a.pension ≥ b.wage + b.self + b.pension)
        let mk (p : Person) (main : Bool) (inv : Int → Int) : Ret :=
          { persons := [p], married := false, parent := main && n > 0, kidHalves := n,
            kidCredits := if main then n else 0, interest := inv c.interest, dividends := inv c.dividends,
            qualifying := qual, rental := inv c.rentalIncome, famAllow := if main then allowTx else 0,
            charitable := inv c.charitable, yr := c.year }
        [mk a aFirst half1, mk b (!aFirst) half2]
    | _ =>
      let p := ps.headD {}
      [{ persons := [p], parent := n > 0, kidHalves := 2 * n, kidCredits := n, interest := c.interest,
         dividends := c.dividends, qualifying := qual, rental := c.rentalIncome, famAllow := allowTx,
         charitable := c.charitable, yr := c.year }]
  -- FamZG Art. 19 Abs. 1bis-2: a household whose earners all stay below the minimum income counts as
  -- non-employed and gets the allowances only if its taxable income (here: federal, before the allowances)
  -- does not exceed 1.5 x the maximum full AHV old-age pension
  let allow := if famzgEntitled (ps.map fun p => p.wage + p.self) (sumInts ((retsOf 0).map fun r => taxable cv (fedLayerY (fedFor r.yr)) r)) n then full else 0
  let allowTx := if o.allowInIncome then allow else 0
  let rets := retsOf allowTx
  let res := rets.map (assess o cv church)
  let s (f : Result → Int) := sumInts (res.map f)
  -- capital withdrawal (adult 1), separate annual tax
  let cap := (c.int? "capitalWithdrawal").getD 0
  let capFedRp := fedCapitalRp c.married cap c.year
  let capSimple := zhCapitalSimpleRp c.married cap c.year
  let capLocalRp := multRp (fedFor c.year).zhCanton capSimple + (if o.cantonOnly then 0 else multRp zhCityMult capSimple)
    + (match churchMult church with | some m => multRp m capSimple | none => 0)
  let fedRp := s (·.fedRp) + capFedRp
  let localRp := s (·.cantonRp) + s (·.cityRp) + s (·.churchRp) + 100 * s (·.personal) + capLocalRp
  let social := rpToChf (sumInts (ps.map fun p => p.ahvRp + p.alvRp + p.nbuRp))
  let unsup := (if c.capitalGains ≠ 0 then ["capitalGains: private capital gains are tax-free (DBG Art. 16 Abs. 3)"] else [])
    ++ (if ps.any (fun p => decide (p.self > 0)) then
         ["self-employment: AHV contributions on the reported amount (no AHVV Art. 9 Abs. 4 grossing-up), IV/EO scale proportional"] else [])
    ++ (if !earner && n > 0 then ["family allowances as a non-employed household (FamZG Art. 19): no EL assumed; income test on federal taxable income"] else [])
    ++ (if yearSupported c.year then [] else [s!"tax year {c.year} not implemented: 2025 law applied"])
    ++ ["wealth tax not modelled", "Fahrkosten/Verpflegung (DBG Art. 26 lit. a/b) not claimed", "BVG risk premiums not included"]
  Out.make c "CH" "CHF" (rpToChf fedRp) (localIncomeTax := rpToChf localRp) (employeeSocial := social)
    (benefits := allow)
    (detail := [Out.d "fedTaxable" (s (·.fedTaxable)), Out.d "fedTaxBeforeChildCreditRp" (s (·.fedBeforeRp)),
      Out.d "fedTaxRp" fedRp, Out.d "zhTaxable" (s (·.zhTaxable)), Out.d "zhSimpleTaxRp" (s (·.zhSimpleRp)),
      Out.d "cantonTaxRp" (s (·.cantonRp)), Out.d "cityTaxRp" (s (·.cityRp)), Out.d "churchTaxRp" (s (·.churchRp)),
      Out.d "personalTax" (s (·.personal)), Out.d "capitalFedRp" capFedRp, Out.d "capitalLocalRp" capLocalRp,
      Out.d "bvgEmployee" (rpToChf (sumInts (ps.map (·.bvgRp)))), Out.d "pillar3a" (sumInts (ps.map (·.p3a))),
      Out.d "ahvIvEoRp" (sumInts (ps.map (·.ahvRp))), Out.d "alvRp" (sumInts (ps.map (·.alvRp))),
      Out.d "nbuRp" (sumInts (ps.map (·.nbuRp))), Out.d "returns" rets.length,
      Out.d "familyAllowances" allow])
    (unsupported := unsup)

def country : Country :=
  { code := "CH", name := "Switzerland (federal + canton and City of Zürich)", currency := "CHF", year := "2022-2025",
    compute := out {}, computeWith := fun args c => out (parseOpts args {}) c }

end ChTax
