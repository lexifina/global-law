import Std
/-!
# Real property held by a wage earner: what each provision permits and what it taxes

A married couple filing jointly, one wage earner, buys one property and holds it (or its like-kind replacement) for a
fixed number of years. Each year they choose a use; at the end they sell or die. Every plan has the same pre-tax
economics (the property yields the same net operating income whether it is let, let by the night, lived in, or used in
the owner's own production business, and it appreciates at the same rate), so the only thing that differs between
plans is tax. The first part states rules; nothing in it names a planning technique. The second part searches.

Figures: 2025 (Rev. Proc. 2024-40 brackets; standard deduction $31,500 as amended by Pub. L. 119-21). Statutory
amounts that are not indexed ($25,000 / $100,000 in §469(i); $250,000 / $500,000 in §121(b); $250,000 in §1411(b)) are
as enacted. §461(l)(3)(A)(ii)(II): $250,000 base, doubled on a joint return (the 2026 base after Pub. L. 119-21).
All years use the same figures (no inflation).

Simplifications (each one is conservative or neutral unless marked):
* Purchase price is 20% land, 60% building, 20% tangible personal property and land improvements with a recovery
  period of 20 years or less (§168(e)); the last is recovered over 5 equal years unless §168(k) applies. On any sale
  the amount realized is allocated in the same 20/60/20 proportions (so the components appreciate with the building:
  this maximises §1245 recapture).
* Whole years, no mid-month convention; building recovery is straight line over 27.5 years (residential rental
  property, §168(c), (e)(2)(A)) or 39 years (nonresidential: any year the units are let on a transient basis,
  §168(e)(2)(A)(ii)(I), and the production building).
* Debt is 70% of price, interest only, qualified nonrecourse financing (§465(b)(6)): the taxpayer is at risk for all of
  it, so §465 never limits a loss here. §163(j) does not apply (§163(j)(3), gross receipts under the §448(c) amount), so
  the §163(j)(7)(B) election (which would force the alternative system, §168(g)(1)(F), (8)) is never worth making and is
  not a move. Rental interest is not investment interest (§163(d)(5)(A)(ii), (d)(4)(D)).
* §1402 self-employment tax is not modelled (it would only add tax to the short-stay and production uses).
* §453 and §1400Z-2 are not moves (see FINDINGS).
-/
namespace Legal.USTax.Hunt.RealEstate

/-! ## Part 1. Rules -/

structure Cfg where
  wages : Int
  /-- a spouse with no other work who can meet both tests of §469(c)(7)(B) in a year -/
  pro : Bool
  /-- apply Temp. Reg. §1.469-1T(e)(3)(ii)(A): average customer use of 7 days or less is not a "rental activity".
  REGULATION-BASED. When false, §469(j)(8) alone governs and every letting is a rental activity (§469(c)(2)). -/
  regs : Bool
  /-- read §469(g)(1)(A) as satisfied by a sale on which §121 excludes gain (Chief Counsel Advice 201428008). When
  false (the conservative reading of "all gain ... realized ... is recognized") suspended losses are not released. -/
  relax121 : Bool
  /-- read §1245(a)(3)(G) literally: a building that is no longer "used by the taxpayer as an integral part of a
  qualified production activity" (§168(n)(2)(A)(ii)) is no longer qualified production property, hence §1250 property.
  When false the building stays §1245 property for ever. -/
  qppGap : Bool
  horizon : Nat
  maxSwitch : Nat
  maxExch : Nat
  price : Int := 1000000
  /-- cost of an improvement to the interior of the building, made by every plan at the start of the second year -/
  reno : Int := 0
  interest : Int := 42000
  deriving Repr

def stdDed : Int := 31500          -- §63(c)(2), (7) for 2025, joint return
def ebl : Int := 500000            -- §461(l)(3)(A)(ii)(II), joint return

/-- Tax (in dollars) on the slice of taxable income from `lo` to `hi` at the §1(j) joint-return rates, each rate
capped at `cap` per mille. -/
def taxSeg (lo hi cap : Int) : Int :=
  let bs : List (Int × Int × Int) :=
    [(0, 23850, 100), (23850, 96950, 120), (96950, 206700, 220), (206700, 394600, 240), (394600, 501050, 320),
     (501050, 751600, 350), (751600, 1000000000000, 370)]
  (bs.foldl (fun acc (a, b, r) => acc + max 0 (min hi b - max lo a) * min r cap) 0) / 1000

/-- §1(h)(1)(B)–(D): adjusted net capital gain stacked on top of `base`: 0% to $96,700, 15% to $600,050, 20% above. -/
def cgTax (base g : Int) : Int :=
  let hi := base + g
  (max 0 (min hi 600050 - max base 96700) * 150 + max 0 (hi - max base 600050) * 200) / 1000

/-- §1(h): ordinary taxable income `o`, unrecaptured §1250 gain `u` (25% maximum, §1(h)(1)(E)), other net capital
gain `l`. -/
def incomeTax (o u l : Int) : Int := taxSeg 0 o 1000 + taxSeg o (o + u) 250 + cgTax (o + u) l

inductive Use where
  | none
  | rentLong     -- let to a tenant; the owner actively participates but does no more
  | rentPro      -- let to a tenant in a year the household meets §469(c)(7)(B) and materially participates
  | strMP        -- let for stays averaging 7 days or less, owner materially participates (§469(h)(1))
  | strPassive   -- let for stays averaging 7 days or less, owner does not materially participate
  | liveIn       -- principal residence
  | mixed        -- let at fair rental 11 months, personal use 1 month (more than 14 days: §280A(d)(1))
  | produce      -- used by the owner as an integral part of manufacturing tangible personal property
  deriving BEq, Hashable, Repr, DecidableEq

inductive End where
  | go | sell | sellNo121 | die
  deriving BEq, Hashable, Repr, DecidableEq

inductive Move where
  | hold (u : Use) (e : End)   -- one year in a use; `e` says what happens on the last day
  | exchange                   -- §1031 exchange for like-kind real property of the same value
  deriving BEq, Repr

structure St where
  year : Nat
  prev : Use
  switches : Nat
  exch : Nat
  kind : Nat          -- 0 dwelling, 1 building suitable for production
  v : Int             -- fair market value
  land : Int          -- basis of land
  bAdj : Int          -- adjusted basis of building
  bBase : Int         -- unadjusted depreciable basis of building
  bDep : Int          -- depreciation adjustments on the building (§1250(b)(3))
  bSL : Int           -- what those adjustments would have been under the straight line method (§1250(b)(1))
  cAdj : Int          -- adjusted basis of the 20-year-or-less property
  cBase : Int
  cDep : Int
  cPIS : Bool         -- components already placed in service
  qAdj : Int          -- adjusted basis of qualified improvement property (§168(e)(6))
  qDep : Int
  qSL : Int
  bonus : Bool        -- no election out under §168(k)(7)
  qppElect : Bool     -- election under §168(n)(6) made for the building
  qpp : Bool          -- building is qualified production property now
  wasQpp : Bool       -- building was qualified production property and its allowance has not been recaptured
  qppY : Nat          -- years since the building was placed in service as qualified production property
  own : Nat           -- years this property has been owned (§121(a))
  resMask : Nat       -- last five years: bit set where principal residence
  nq : Nat            -- years of nonqualified use (§121(b)(5)(C))
  nonRes : Nat        -- non-residence years since the last residence year (not yet nonqualified)
  exY : Nat           -- years since acquired in a §1031 exchange (99 = not so acquired)
  pal : Int           -- §469(b) suspended losses allocable to the property
  c5 : Int            -- §280A(c)(5) carryover
  nol : Int           -- §172 carryover (including §461(l)(2) amounts)
  pendOrd : Int       -- ordinary income already recognized this year (on an exchange)
  pendLT : Int
  pendNII : Int
  tax : Int           -- income tax and §1411 tax paid so far
  taxPV : Int         -- the same, each year's tax discounted at 5% a year to the purchase date
  done : Nat          -- 0 holding, 1 sold, 2 died
  mustBiz : Bool      -- replacement property "is to be held" for business or investment (§1031(a)(1))
  deriving BEq, Hashable, Repr

def isLet : Use → Bool
  | .rentLong | .rentPro | .strMP | .strPassive => true
  | _ => false

def popcount5 (m : Nat) : Nat := (List.range 5).foldl (fun a i => a + (m >>> i) % 2) 0

def pos (x : Int) : Int := max 0 x

/-- Purchase. `bonus = false` is the §168(k)(7) election out; `qppElect` is the §168(n)(6) election. -/
def buy (c : Cfg) (kind : Nat) (bonus qppElect : Bool) : St :=
  let l := c.price * 20 / 100
  let b := c.price * 60 / 100
  let k := c.price - l - b
  { year := 0, prev := .none, switches := 0, exch := 0, kind, v := c.price, land := l, bAdj := b, bBase := b,
    bDep := 0, bSL := 0, cAdj := k, cBase := k, cDep := 0, cPIS := false, qAdj := 0, qDep := 0, qSL := 0, bonus, qppElect, qpp := false,
    wasQpp := false, qppY := 0, own := 0, resMask := 0, nq := 0, nonRes := 0, exY := 99, pal := 0, c5 := 0, nol := 0,
    pendOrd := 0, pendLT := 0, pendNII := 0, tax := 0, taxPV := 0, done := 0, mustBiz := false }

/-- §1031 exchange into like-kind real property of equal value and equal debt. -/
def exchange (c : Cfg) (s : St) : Option St :=
  -- §1031(a)(1): relinquished property held for productive use in a trade or business or for investment
  if s.done ≠ 0 ∨ s.exch ≥ c.maxExch ∨ s.mustBiz ∨ !(isLet s.prev || s.prev == .produce) then none else
  -- §1031(a)(1) (as amended 2017) covers real property only: the 20-year-or-less property is sold and bought.
  let arC := s.v * 20 / 100
  let gC := arC - s.cAdj
  let recC := pos (min s.cDep gC)                                   -- §1245(a)(1)
  -- §1245(b)(4): on a building that is §1245 property, recapture up to the value of non-§1245 property received
  let is1245 := s.qpp || (s.wasQpp && !c.qppGap)
  let recB := if is1245 then pos (min s.bDep (s.v * 60 / 100 - s.bAdj)) else 0
  let passivePrev := s.prev == .rentLong || s.prev == .strPassive || (s.prev == .strMP && !c.regs)
  some { s with
    exch := s.exch + 1, mustBiz := true,
    pendOrd := s.pendOrd + recC + recB, pendLT := s.pendLT + (gC - recC),
    pendNII := s.pendNII + (if passivePrev then gC + recB else 0),       -- §1411(c)(1)(A)(iii)
    cAdj := arC, cBase := arC, cDep := 0, cPIS := false,              -- purchased: §179(d)(2), (3); §168(k)(2)(E)(ii)
    bAdj := s.bAdj + recB, bDep := s.bDep - recB,                     -- §1031(d)
    qpp := false, wasQpp := false,
    own := 0, resMask := 0, nq := 0, nonRes := 0, exY := 0 }          -- §121(a), (d)(10)

/-- One year in use `u`, ending as `e` says. -/
def hold (c : Cfg) (s : St) (u : Use) (e : End) : Option St :=
  if s.done ≠ 0 ∨ u == .none then none else
  let okKind := if s.kind == 0 then u != .produce else (u == .produce || u == .rentLong || u == .rentPro)
  if !okKind ∨ (u == .rentPro && !c.pro) ∨ (s.mustBiz && !(isLet u || u == .produce)) then none else
  let sw := if s.prev == .none || s.prev == u then s.switches else s.switches + 1
  if sw > c.maxSwitch ∨ ((e != .go) != (s.year + 1 == c.horizon)) then none else
  let biz := isLet u || u == .produce || u == .mixed
  -- §168(n)(5): within 10 years, ceases production use and is put to another productive use
  let recapN := if s.qpp && u != .produce && s.qppY < 10 then s.bDep else 0
  -- the improvement: §168(e)(6) if the building is nonresidential real property this year (§168(e)(2)(A)(i) tests
  -- "for the taxable year"); otherwise it is recovered with the building (§168(i)(6))
  let renoNow := c.reno > 0 && s.year == 1
  let reno : Int := if renoNow then c.reno else 0
  let nonres := s.kind == 1 || u == .strMP || u == .strPassive
  let qip := renoNow && biz && nonres
  let v0 := s.v + reno
  let bAdj0 := s.bAdj + recapN + (if qip then 0 else reno)
  let bBase0 := if recapN > 0 then bAdj0 else s.bBase + (if qip then 0 else reno)
  let bDep0 := if recapN > 0 then 0 else s.bDep
  let bSL0 := if recapN > 0 then 0 else s.bSL
  let qpp0 := s.qpp && u == .produce
  let wasQpp0 := (s.wasQpp || s.qpp) && recapN == 0
  -- depreciation, §§167(a), 168(a)–(c); §168(n)(1); §168(k)(1)
  -- §168(n)(2)(A)(iv), (B)(i)(III): acquired by purchase, placed in service in production use
  let qppFirst := s.kind == 1 && s.qppElect && u == .produce && s.year == 0 && s.exch == 0
  let life2 : Int := if s.kind == 1 || u == .strMP || u == .strPassive then 78 else 55
  let f12 : Int := if u == .mixed then 11 else 12                    -- §280A(e)(1)
  let slYear := min (bBase0 - bSL0) (bBase0 * 2 / life2)
  let depB := if !biz then 0 else if qppFirst then bAdj0 else min bAdj0 (bBase0 * 2 / life2) * f12 / 12
  let depC := if !biz then 0 else if s.bonus && !s.cPIS then s.cAdj else min s.cAdj (s.cBase / 5) * f12 / 12
  let bAdj1 := bAdj0 - depB
  let bDep1 := bDep0 + depB
  let bSL1 := if biz then bSL0 + pos slYear else bSL0
  let qAdjIn := s.qAdj + (if qip then reno else 0)
  -- §168(k)(2)(A)(i)(I): 15-year property; otherwise straight line over 15 years (§168(b)(3)(G))
  let depQ := if !biz then 0 else if qip && s.bonus then qAdjIn else min qAdjIn (c.reno / 15)
  let qAdj1 := qAdjIn - depQ
  let qDep1 := s.qDep + depQ
  let qSL1 := if biz && (qAdjIn > 0 || s.qDep > 0) then min (s.qSL + c.reno / 15) (max c.reno s.qSL) else s.qSL
  let cAdj1 := s.cAdj - depC
  let cDep1 := s.cDep + depC
  let qpp1 := qpp0 || qppFirst
  let net := if biz then (v0 * 4 / 100 - c.interest) * f12 / 12 - depB - depC - depQ else 0
  -- how §469 sees the year
  let nonpassive := u == .rentPro || u == .produce || (u == .strMP && c.regs)       -- §469(c)(1), (c)(7); reg.
  let passive := isLet u && !nonpassive                                            -- §469(c)(2)
  let allowanceOK := passive && !(u == .strPassive && c.regs) && !(u == .strMP && c.regs)  -- §469(i)(1)
  -- the last day
  let v1 := v0 * 104 / 100
  let adj := s.land + bAdj1 + cAdj1 + qAdj1
  let selling := e == .sell || e == .sellNo121
  let arL := v1 * 20 / 100
  let arB := v1 * 60 / 100
  let arC := v1 - arL - arB
  let gC := arC - cAdj1
  let recC := pos (min cDep1 gC)                                                   -- §1245(a)(1)
  let gB := arB - bAdj1 - qAdj1
  let is1245 := qpp1 || (wasQpp0 && !c.qppGap)                                     -- §1245(a)(3)(G)
  let addlQ := pos (qDep1 - qSL1)
  let addl := pos (bDep1 - bSL1) + addlQ                                           -- §1250(b)(1)
  let recB := if is1245 then pos (min (bDep1 + addlQ) gB) else pos (min addl gB)   -- §1245(a)(1); §1250(a)(1)
  let u1250 := if is1245 then pos (min (qDep1 - addlQ) (gB - recB))
               else pos (min (bDep1 + qDep1 - addl) (gB - recB))                   -- §1(h)(6)(A)
  let ltAll := (gC - recC) + (gB - recB - u1250) + (arL - s.land)                  -- §1231(a)(1)
  let mask1 := ((s.resMask <<< 1) ||| (if u == .liveIn then 1 else 0)) &&& 31
  let nq1 := if u == .liveIn then s.nq + s.nonRes else s.nq                        -- §121(b)(5)(C)(i), (ii)(I)
  let nonRes1 := if u == .liveIn then 0 else s.nonRes + 1
  let own1 := s.own + 1
  -- §121(a), (d)(10); (d)(6) leaves the depreciation gain taxable; (b)(5) nonqualified share; (b)(2) $500,000
  let elig121 := e == .sell && s.kind == 0 && popcount5 mask1 ≥ 2 && s.exY + 1 > 5
  let r := pos ltAll
  let nqShare := r * (nq1 : Int) / (own1 : Int)
  let excl := if elig121 then min (r - nqShare) 500000 else 0
  let sOrd := if selling then recC + recB else 0
  let sU := if selling then u1250 else 0
  let sLT := if selling then ltAll - excl else 0
  let sGain := sOrd + sU + sLT
  -- §469: this year's result against passive income, then §469(i), then §469(b)
  let passGain := if passive then pos sGain else 0
  let loss := if passive then pos (-net) else 0
  let lossVsGain := min loss passGain
  let magi := c.wages + s.pendOrd + s.pendLT + sGain + recapN                      -- §469(i)(3)(E)
  let allowance := if allowanceOK then max 0 (min 25000 (25000 - pos (magi - 100000) / 2)) else 0
  let allowed := min (loss - lossVsGain) allowance
  let palAdd := loss - lossVsGain - allowed
  -- suspended losses against passive income (§469(b), (d)(1)) or income of a former passive activity (§469(f)(1)(A))
  let actIncome := if passive then pos net + passGain - lossVsGain else if nonpassive then pos (net + sGain) else 0
  let palUsed := min s.pal actIncome
  let pal1 := s.pal - palUsed + palAdd
  -- §469(g)(1)(A) on a fully taxable sale; (g)(2) at death
  let release := if selling then (if excl == 0 || c.relax121 then pal1 else 0)
                 else if e == .die then pos (pal1 - pos (v1 - adj)) else 0
  let pal2 := if e == .go then pal1 else 0
  -- §280A(c)(5) and §469(j)(10) for the mixed-use year
  let c5Used := if u == .mixed then min s.c5 (pos net) else 0
  let c5New := if u == .mixed then s.c5 - c5Used + pos (-net) else s.c5
  let mixedInc := if u == .mixed then pos net - c5Used else 0
  -- ordinary items
  let rentOrd := if passive then pos net - lossVsGain - allowed
                 else if nonpassive then net else mixedInc
  -- §461(l): trade-or-business deductions over trade-or-business income and gain, above $500,000
  let bizNet := if nonpassive then net + sGain else 0
  let eblDis := pos (-bizNet - ebl)
  let ordItems := s.pendOrd + recapN + sOrd + rentOrd - palUsed - release + eblDis
  -- §163(h)(3) with $10,000 of §164 taxes, or the standard deduction
  let ded := if u == .liveIn then max stdDed (10000 + c.interest) else stdDed
  let o0 := c.wages + ordItems - ded
  let u0 := sU
  let l0 := s.pendLT + sLT
  -- a deficit in ordinary income comes off the 25% gain first, then the rest (§1(h)(1)(E)(ii))
  let d1 := pos (-o0)
  let u1 := u0 - min u0 d1
  let d2 := d1 - min u0 d1
  let l1 := l0 - min (pos l0) d2
  let d3 := d2 - min (pos l0) d2
  let o1 := pos o0
  -- §172(a)(2): carryovers up to 80% of taxable income
  let ti := o1 + u1 + pos l1
  let nolUse := min s.nol (ti * 80 / 100)
  let o2 := o1 - min o1 nolUse
  let n2 := nolUse - min o1 nolUse
  let u2 := u1 - min u1 n2
  let n3 := n2 - min u1 n2
  let l2 := pos l1 - min (pos l1) n3
  let nol1 := s.nol - nolUse + d3 + eblDis
  -- §1411: rents and gain unless derived in / held in a trade or business that is not passive
  let niiRaw := s.pendNII + (if passive then net + sGain - palUsed - release
                            else if nonpassive then 0
                            else mixedInc + sGain)
  let agi := c.wages + ordItems + u0 + l0
  let niit := min (pos niiRaw) (pos (agi - 250000)) * 38 / 1000
  let t := incomeTax o2 u2 l2 + niit
  some { s with
    year := s.year + 1, prev := u, switches := sw, v := v1,
    bAdj := bAdj1, bBase := bBase0, bDep := bDep1, bSL := bSL1, cAdj := cAdj1, cDep := cDep1, qAdj := qAdj1, qDep := qDep1, qSL := qSL1,
    cPIS := s.cPIS || biz, qpp := qpp1, wasQpp := wasQpp0 || qpp1,
    qppY := if qpp1 || wasQpp0 then s.qppY + 1 else 0,
    own := own1, resMask := mask1, nq := nq1, nonRes := nonRes1, exY := if s.exY ≥ 99 then 99 else s.exY + 1,
    pal := pal2, c5 := c5New, nol := if e == .die then 0 else nol1,
    pendOrd := 0, pendLT := 0, pendNII := 0, tax := s.tax + t,
    taxPV := s.taxPV + t * (100 ^ (s.year + 1) : Nat) / (105 ^ (s.year + 1) : Nat),
    done := if selling then 1 else if e == .die then 2 else 0, mustBiz := false }

def step (c : Cfg) (s : St) : Move → Option St
  | .hold u e => hold c s u e
  | .exchange => exchange c s

/-! ## Part 2. Search -/

def allUses : List Use := [.rentLong, .rentPro, .strMP, .strPassive, .liveIn, .mixed, .produce]
def allMoves : List Move :=
  .exchange :: allUses.flatMap fun u => [.hold u .go, .hold u .sell, .hold u .sellNo121, .hold u .die]

def useName : Use → String
  | .none => "-" | .rentLong => "let" | .rentPro => "let(pro)" | .strMP => "short(mp)" | .strPassive => "short(passive)"
  | .liveIn => "live" | .mixed => "mixed" | .produce => "produce"
def endName : End → String
  | .go => "" | .sell => " SELL" | .sellNo121 => " SELL(no121)" | .die => " DIE"

/-- "let x3, live x2 SELL" -/
def showPath (p : List Move) : String := Id.run do
  let mut out : List String := []
  let mut cur : Option (Use × Nat) := none
  let mut tail := ""
  for m in p do
    match m with
    | .exchange =>
      if let some (u, n) := cur then out := out ++ [s!"{useName u} x{n}"]
      cur := none
      out := out ++ ["EXCHANGE"]
    | .hold u e =>
      match cur with
      | some (u', n) => if u' == u then cur := some (u, n + 1) else
          out := out ++ [s!"{useName u'} x{n}"]; cur := some (u, 1)
      | none => cur := some (u, 1)
      tail := endName e
  if let some (u, n) := cur then out := out ++ [s!"{useName u} x{n}"]
  return ", ".intercalate out ++ tail

/-- which uses a plan contains, whether it exchanges, how it ends -/
def family (label : String) (p : List Move) : String :=
  let us := allUses.filter fun u => p.any fun | .hold u' _ => u' == u | _ => false
  let x := if p.any (fun | .exchange => true | _ => false) then "+exchange" else ""
  let e := p.foldl (fun a m => match m with | .hold _ e => endName e | _ => a) ""
  s!"{label} | {"+".intercalate (us.map useName)}{x} |{e}"

def run (c : Cfg) (m : List Move) (s : St) : Option St := m.foldlM (step c) s

def starts (c : Cfg) : List (String × St) :=
  [("dwelling, SL", buy c 0 false false), ("dwelling, bonus", buy c 0 true false),
   ("factory, SL", buy c 1 false false), ("factory, bonus", buy c 1 true false),
   ("factory, QPP", buy c 1 false true), ("factory, QPP+bonus", buy c 1 true true)]

def search (title : String) (c : Cfg) (top : Nat := 14) : IO Unit := do
  IO.println s!"\n=== {title} ==="
  let h := c.horizon
  let pv := (← IO.getEnv "HUNT_PV").isSome
  let obj (s : St) : Int := if pv then s.taxPV else s.tax
  if pv then IO.println "(objective: present value of tax at 5% a year)"
  let baseSell := (run c ((List.replicate (h - 1) (.hold .rentLong .go)) ++ [.hold .rentLong .sell]) (buy c 0 false false)).map obj
  let baseDie := (run c ((List.replicate (h - 1) (.hold .rentLong .go)) ++ [.hold .rentLong .die]) (buy c 0 false false)).map obj
  let noProp := (h : Int) * incomeTax (c.wages - stdDed) 0 0
  IO.println s!"wages only, {h} years (nominal): {noProp}.  buy, let, straight line, sell: {baseSell.getD 0}.  same, die: {baseDie.getD 0}"
  let only := (← IO.getEnv "HUNT_START").getD ""
  let mut frontier : Array (St × String × List Move) :=
    ((starts c).filter fun (l, _) => only == "" || l == only).toArray.map fun (l, s) => (s, l, [])
  let mut seen : Std.HashSet St := {}
  let mut fam : Std.HashMap String (Int × List Move) := {}
  let mut visited := 0
  let mut terminals := 0
  while !frontier.isEmpty do
    let mut next : Array (St × String × List Move) := #[]
    for (s, l, p) in frontier do
      for m in allMoves do
        match step c s m with
        | none => pure ()
        | some s' =>
          if !seen.contains s' then
            seen := seen.insert s'
            visited := visited + 1
            let p' := m :: p
            if s'.done ≠ 0 then
              terminals := terminals + 1
              let k := family l p'.reverse
              match fam[k]? with
              | some (t, _) => if obj s' < t then fam := fam.insert k (obj s', p'.reverse)
              | none => fam := fam.insert k (obj s', p'.reverse)
            else next := next.push (s', l, p')
    frontier := next
  IO.println s!"positions {visited}, finished plans {terminals}, families {fam.size}"
  let rows := fam.toList.toArray.qsort (fun a b => a.2.1 < b.2.1)
  for (endTag, base) in [(" SELL", baseSell.getD 0), (" DIE", baseDie.getD 0)] do
    for lived in [true, false] do
      let which := if lived then "any use" else "never lived in"
      IO.println s!"-- best families ending{endTag}, {which} (saving vs. buy-let-straight-line{endTag}) --"
      let mut n := 0
      let mut lastTax : Int := -1
      for (k, t, p) in rows do
        let isLive := p.any fun | .hold .liveIn _ => true | _ => false
        if n < top ∧ t ≠ lastTax ∧ (lived ∨ !isLive) ∧ (k.endsWith endTag ∨ (endTag == " SELL" ∧ k.endsWith " SELL(no121)")) then
          n := n + 1
          lastTax := t
          IO.println s!"{base - t}  tax {t}  [{k}]  {showPath p}"

/-- Year-by-year tax of one plan. -/
def trace (c : Cfg) (label : String) (s0 : St) (p : List Move) : IO Unit := do
  IO.println s!"trace: {label}: {showPath p}"
  let mut s := s0
  for m in p do
    match step c s m with
    | none => IO.println "  (not allowed)"; return
    | some s' =>
      let dt := s'.tax - s.tax
      let line := s!"  y{s'.year} {showPath [m]}: tax {dt}, suspended {s'.pal}, nol {s'.nol}, carry280A {s'.c5}"
      IO.println (line ++ s!", bldg basis {s'.bAdj}, comp basis {s'.cAdj}, value {s'.v}")
      s := s'
  IO.println s!"  total {s.tax}"

def cfg0 : Cfg := { wages := 300000, pro := false, regs := false, relax121 := false, qppGap := false,
                    horizon := 12, maxSwitch := 2, maxExch := 1 }

def cfgF : Cfg := { wages := 600000, pro := true, regs := true, relax121 := true, qppGap := true, horizon := 12,
                    maxSwitch := 2, maxExch := 1, price := 4000000, interest := 168000 }

/-- Which run: set the environment variable HUNT_CFG to A, B, C, D, E or F (each about a minute); unset = a quick
8-year run of C. -/
def main' : IO Unit := do
  match (← IO.getEnv "HUNT_CFG") with
  | some "A" => search "A. statute only, no real-estate-professional spouse, wages 300k, 12 years" cfg0
  | some "B" => search "B. A + 7-day regulation" { cfg0 with regs := true }
  | some "C" => search "C. B + spouse can meet 469(c)(7)" { cfg0 with regs := true, pro := true }
  | some "D" => search "D. C + CCA reading of 469(g) + literal 1245(a)(3)(G)"
                  { cfg0 with regs := true, pro := true, relax121 := true, qppGap := true }
  | some "E" => search "E. B at wages 120k" { cfg0 with regs := true, wages := 120000 }
  | some "T" =>
    let c := { cfg0 with regs := true, pro := true }
    let g := { c with qppGap := true, relax121 := true }
    let h (u : Use) (n : Nat) : List Move := List.replicate n (.hold u .go)
    trace c "baseline" (buy c 0 false false) (h .rentLong 11 ++ [.hold .rentLong .sell])
    trace c "factory, straight line" (buy c 1 false false) (h .produce 11 ++ [.hold .produce .sell])
    trace c "factory, 168(n) election" (buy c 1 false true) (h .produce 11 ++ [.hold .produce .sell])
    trace c "168(n), leased in year 5" (buy c 1 false true) (h .produce 4 ++ h .rentLong 7 ++ [.hold .rentLong .sell])
    trace c "168(n), leased after year 10, 1245 reading" (buy c 1 false true) (h .produce 10 ++ h .rentLong 1 ++ [.hold .rentLong .sell])
    trace g "168(n), leased after year 10, literal reading" (buy c 1 false true) (h .produce 10 ++ h .rentLong 1 ++ [.hold .rentLong .sell])
    trace c "168(n), leased after year 10, exchange, 1245 reading" (buy c 1 false true) (h .produce 10 ++ h .rentLong 1 ++ [.exchange, .hold .rentLong .sell])
    trace g "168(n), leased after year 10, exchange, literal reading" (buy c 1 false true) (h .produce 10 ++ h .rentLong 1 ++ [.exchange, .hold .rentLong .sell])
    trace c "168(n), die" (buy c 1 false true) (h .produce 11 ++ [.hold .produce .die])
    trace c "bonus, short stay with material participation one year, then let" (buy c 0 true false) (h .strMP 1 ++ h .rentLong 10 ++ [.hold .rentLong .sell])
    trace c "same, sale in a 469(c)(7) year" (buy c 0 true false) (h .strMP 1 ++ h .rentLong 10 ++ [.hold .rentPro .sell])
    trace c "let 11 years, sale in a 469(c)(7) year" (buy c 0 false false) (h .rentLong 11 ++ [.hold .rentPro .sell])
    trace c "let 3, live 9" (buy c 0 false false) (h .rentLong 3 ++ h .liveIn 8 ++ [.hold .liveIn .sell])
    trace c "live 9, let 3" (buy c 0 false false) (h .liveIn 9 ++ h .rentLong 2 ++ [.hold .rentLong .sell])
    trace c "let 9, mixed 3" (buy c 0 false false) (h .rentLong 9 ++ h .mixed 2 ++ [.hold .mixed .sell])
    let r := { c with reno := 150000 }
    trace r "improvement in year 2 while let to a tenant" (buy r 0 true false) (h .rentLong 11 ++ [.hold .rentLong .sell])
    trace r "improvement in year 2 while let by the night (passive)" (buy r 0 true false) (h .rentLong 1 ++ h .strPassive 1 ++ h .rentLong 9 ++ [.hold .rentLong .sell])
    trace r "improvement in year 2 while let by the night (material participation)" (buy r 0 true false) (h .rentLong 1 ++ h .strMP 1 ++ h .rentLong 9 ++ [.hold .rentLong .sell])
    trace r "same, die" (buy r 0 true false) (h .rentLong 1 ++ h .strMP 1 ++ h .rentLong 9 ++ [.hold .rentLong .die])
    trace r "let throughout, die" (buy r 0 true false) (h .rentLong 11 ++ [.hold .rentLong .die])
  | some "G" => search "G. C + $150k interior improvement in year 2" { cfg0 with regs := true, pro := true, reno := 150000 }
  | some "F" => search "F. D with a $4m property, wages 600k (461(l) binds)"
                  cfgF
  | _ => search "quick: C at 8 years" { cfg0 with regs := true, pro := true, horizon := 8 }

#eval main'

end Legal.USTax.Hunt.RealEstate
