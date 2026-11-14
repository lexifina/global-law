import Std

/-!
# Individuals crossing borders: residence, source and expatriation rules as enacted

One individual, a salary that follows the person, one appreciated asset, and a calendar. The first part (`Rules`)
writes down what each provision says about who is a resident on which days, where a gain is sourced, and what is
taxed. It names no technique. The second part searches every sequence of moves.

Calendar. Each calendar year (365 days) is cut at the day-count thresholds the statute itself uses, so that being
present or absent on whole segments is enough to land on either side of each threshold:

  segment 0: days   1– 30  (30 days)   one day short of the 31 days of §7701(b)(3)(A)(i)
  segment 1: days  31–120  (90 days)   through day 120 (120 + 120/3 + 120/6 = 180 < 183)
  segment 2: days 121–182  (62 days)   through day 182, one short of 183 (§7701(b)(3)(B)(i), §871(a)(2))
  segment 3: day  183      (1 day)
  segment 4: days 184–365  (182 days)  the last 182 days of the year

Simplifications, each stated once:
* flat rates for a top-bracket individual: ordinary 35% (illustrative), long-term gain 20% (§1(h)(1)(D)),
  net investment income tax 3.8% (§1411(a)), nonresident flat tax 30% (§871(a));
* salary accrues evenly by day and is sourced where the person is that day (§861(a)(3), §862(a)(3)); a nonresident's
  salary for US days is effectively connected (§864(b), §871(b));
* "tax home" and "closer connection" are one fact, changed by `relocate`. To keep the fact honest, in a year with
  183 or more US days the tax home may be foreign only after the last day of presence, or before the first day if
  the year began with a foreign tax home (§911(d)(3) second sentence: no foreign tax home while the abode is in
  the US);
* the 10 days of nominal presence (§7701(b)(2)(C)), the first-year election (§7701(b)(4)), medical days, commuters
  and transit days are left out; treaties are left out; states are left out;
* a citizen year counts as a resident year for §7701(b)(2)(A) (conservative: residency then starts on 1 January);
* the asset does not grow, so the built-in gain is fixed; holding period is long-term;
* after the horizon the person is assumed absent (zero US days) with the status held at the end.
Figures: §877A(a)(3) exclusion $890,000 (2025, Rev. Proc. 2024-40); §911(b)(2)(D) exclusion $130,000 (2025).
-/

namespace Legal.USTax.Hunt.Residence

/-! ## Rules -/

def bit (m i : Nat) : Bool := (m >>> i) % 2 == 1
def daysOf (g : Array Nat) (m : Nat) : Nat := (List.range g.size).foldl (fun a i => if bit m i then a + g[i]! else a) 0
def firstSegBelow (n m k : Nat) : Nat := ((List.range k).find? (bit m)).getD n
def lastSeg (n m : Nat) : Nat := ((List.range n).reverse.find? (bit m)).getD 0

inductive Asset where
  | usStock        -- stock of a domestic corporation
  | foreignStock   -- stock of a foreign corporation that is not a PFIC or CFC
  | usRealty       -- a United States real property interest, §897(c)
  deriving BEq, Hashable, Repr, DecidableEq

structure Params where
  grid : Array Nat      -- lengths of the segments the year is cut into (sum 365)
  asset : Asset
  salary : Nat          -- per year, follows the person
  gain : Nat            -- built-in long-term gain
  div : Nat             -- yearly dividend while the asset is held (stock only)
  f : Nat               -- foreign income tax on salary earned abroad with a foreign tax home, basis points
  fg : Nat              -- foreign income tax on the gain if sold with a foreign tax home, basis points
  covered : Bool        -- meets §877(a)(2)(A), (B) or (C) (net worth $2,000,000 or more, etc.)
  student : Bool        -- exempt individual for every day of every year, §7701(b)(5)(A)(iii), (D)
  horizon : Nat
  maxReloc : Nat
  gifts : Bool          -- allow the gift moves
  basis : Nat           -- adjusted basis of the asset (value = basis + gain)
  endInUS : Bool        -- search filter: count only plans with 183 or more US days in the last year
  deriving Repr

def ordBp : Nat := 3500
def ltcgBp : Nat := 2000     -- §1(h)(1)(D)
def niitBp : Nat := 380      -- §1411(a)(1); not for nonresident aliens, §1411(e)(1)
def nraBp : Nat := 3000      -- §871(a)(1), (a)(2)
def exitExclusion : Nat := 890000   -- §877A(a)(3), 2025
def feie : Nat := 130000            -- §911(b)(2)(D), 2025
def bp (rate amt : Nat) : Nat := rate * amt / 10000

/-- What is kept about a finished calendar year until the next year shows whether residence continued
(§7701(b)(2)(B)(iii) looks one year ahead). -/
structure Pend where
  mask : Nat        -- segments present in the US
  homeMask : Nat    -- segments with the tax home in the US
  saleSeg : Nat     -- segment of the sale, 9 if none
  saleGain : Nat
  divSegs : Nat     -- the asset was held during segments 0..divSegs-1
  citUntil : Nat    -- citizen during segments 0..citUntil-1
  lprUntil : Nat    -- lawful permanent resident during segments 0..lprUntil-1
  d1 : Nat          -- countable US days, preceding year
  d2 : Nat          -- countable US days, second preceding year
  resPrev : Bool    -- resident at any time during the preceding year
  deriving BEq, Hashable, Repr

/-- §7701(b)(1)(A), (3): is the alien a resident with respect to the calendar year? Returns (resident under the
substantial presence test, closer-connection exception used). -/
def sptOf (p : Params) (pd : Pend) : Bool × Bool :=
  let days := daysOf p.grid pd.mask
  let cd := if p.student then 0 else days                         -- §7701(b)(3)(D)(i): exempt days are not days
  -- §7701(b)(3)(A): 31 days, and days + 1/3 + 1/6 ≥ 183 (multiplied through by 6)
  let spt := cd ≥ 31 && 6 * cd + 2 * pd.d1 + pd.d2 ≥ 1098
  -- §7701(b)(3)(B): fewer than 183 days, foreign tax home and closer connection for the year
  let closer := cd < 183 && pd.homeMask == 0
  (spt && !closer, spt && closer)

def resAnyOf (p : Params) (pd : Pend) : Bool := pd.lprUntil > 0 || (sptOf p pd).1   -- §7701(b)(1)(A)(i), (ii)

structure YearTax where
  us : Nat
  foreign : Nat
  gainTax : Nat
  head877 : Nat   -- excess of §877(b) tax over §871 tax, nonresident segments before residence starts (or whole year)
  tail877 : Nat   -- same, nonresident segments after residence ends
  resAny : Bool
  tags : Nat
  deriving Repr

def tSoldWW : Nat := 1
def tSoldNRAForeign : Nat := 2
def tSoldNRAUsUnder183 : Nat := 4
def tSold871a2 : Nat := 8
def tLapse : Nat := 16
def tMTM : Nat := 32
def t911 : Nat := 64
def tCloser : Nat := 128
def tExpat : Nat := 256
def tRealtyNRA : Nat := 512

/-- Tax for one calendar year, once it is known whether the person is a resident in the following year. -/
def yearTax (p : Params) (pd : Pend) (resNext : Bool) : YearTax := Id.run do
  let n := p.grid.size
  let days := daysOf p.grid pd.mask
  let (sptRes, usedCloser) := sptOf p pd
  let lprAny := pd.lprUntil > 0
  let resAny := lprAny || sptRes
  -- §7701(b)(2)(A): first year. Resident from 1 January if resident at any time in the preceding year; otherwise
  -- from the first day present (substantial presence) or the first day present as a permanent resident.
  let start :=
    if !resAny then n else if pd.resPrev then 0
    else min (if sptRes then firstSegBelow n pd.mask n else n) (if lprAny then firstSegBelow n pd.mask pd.lprUntil else n)
  -- §7701(b)(2)(B): last year. Not a resident after the last day present (or last day as a permanent resident) if
  -- closer connection to a foreign country for the rest of the year and not a resident at any time next year.
  let last := max (if sptRes then lastSeg n pd.mask else 0) (if lprAny then pd.lprUntil - 1 else 0)
  let foreignAfter := (List.range n).all fun i => i ≤ last || !bit pd.homeMask i
  let stop := if resNext then n - 1 else if foreignAfter then last else n - 1
  let ww := fun (i : Nat) => i < pd.citUntil || (resAny && start ≤ i && i ≤ stop)   -- §1, §61: worldwide income
  let mut us := 0
  let mut foreign := 0
  let mut gainTax := 0
  let mut head871 := 0
  let mut head877 := 0
  let mut tail871 := 0
  let mut tail877 := 0
  let mut wwForeignSalary := 0
  let mut tags := if usedCloser then tCloser else 0
  let stock := p.asset != .usRealty
  for i in [0:n] do
    let sal := p.salary * p.grid[i]! / 365
    let dv := if stock && i < pd.divSegs then p.div * p.grid[i]! / 365 else 0
    let present := bit pd.mask i
    let homeUS := bit pd.homeMask i
    let sale := if pd.saleSeg == i then pd.saleGain else 0
    if !present && !homeUS then foreign := foreign + bp p.f sal
    if sale > 0 && !homeUS then foreign := foreign + bp p.fg sale
    if ww i then
      if present || homeUS then us := us + bp ordBp sal
      else wwForeignSalary := wwForeignSalary + sal
      us := us + bp (ltcgBp + niitBp) dv
      if sale > 0 then
        -- §865(g)(2): foreign source for a citizen or resident alien only if 10% foreign tax is actually paid;
        -- then the credit of §901(b)(1), (3), limited by §904(a) to the US tax on that income.
        let credit := if !homeUS && p.fg ≥ 1000 then min (bp p.fg sale) (bp ltcgBp sale) else 0
        let t := bp (ltcgBp + niitBp) sale - credit
        us := us + t; gainTax := gainTax + t; tags := tags ||| tSoldWW
    else
      -- nonresident alien: §871(b) on effectively connected salary, §871(a)(1)(A) 30% on US-source dividends
      let salT := if present then bp ordBp sal else 0
      let d871 := if p.asset == .usStock then bp nraBp dv else 0
      let d877 := if p.asset == .usStock then bp ltcgBp dv else 0
      let mut g871 := 0
      let mut g877 := 0
      if sale > 0 then
        if p.asset == .usRealty then
          -- §897(a)(1): treated as effectively connected; §1(h) rate; no §1411 (§1411(e)(1))
          g871 := bp ltcgBp sale; g877 := g871; tags := tags ||| tRealtyNRA
        else
          -- §865(a), (g)(1)(A)(i)(II): US source only if the nonresident alien's tax home is in the US.
          -- §871(a)(2): 30% if present 183 days or more "during the taxable year" (every physical day counts,
          -- exempt-individual days included: the exclusion in §7701(b)(3)(D) is "for purposes of this subsection").
          let usSource := homeUS
          if usSource && days ≥ 183 then g871 := bp nraBp sale; tags := tags ||| tSold871a2
          else if usSource then tags := tags ||| tSoldNRAUsUnder183
          else tags := tags ||| tSoldNRAForeign
          -- §877(b), (d)(1)(B): stock of a domestic corporation is US source whatever the tax home
          g877 := if p.asset == .usStock || usSource then bp ltcgBp sale else 0
      if i < start then
        head871 := head871 + salT + d871 + g871; head877 := head877 + salT + d877 + g877
      else
        tail871 := tail871 + salT + d871 + g871; tail877 := tail877 + salT + d877 + g877
      us := us + salT + d871 + g871; gainTax := gainTax + g871
  -- foreign salary of a citizen or resident: credit (§901, §904(a)) or, at the taxpayer's election, §911(a)(1)
  -- when the tax home is foreign all year and 330 full days are spent abroad (§911(d)(1)(B); here: the calendar year)
  let base := fun (x : Nat) => bp ordBp x - min (bp p.f x) (bp ordBp x)
  let all5 := (List.range n).all ww
  let q911 := all5 && pd.homeMask == 0 && days ≤ 35 && wwForeignSalary > 0
  if q911 then
    us := us + base (wwForeignSalary - min wwForeignSalary feie); tags := tags ||| t911
  else us := us + base wwForeignSalary
  return { us, foreign, gainTax, head877 := head877 - min head877 head871, tail877 := tail877 - min tail877 tail871,
           resAny, tags }

structure St where
  yr : Nat
  seg : Nat
  mask : Nat
  home : Bool        -- tax home (and closer connection) in the US now
  homeY0 : Bool      -- tax home in the US when the year began
  homeMask : Nat
  saleSeg : Nat
  saleGain : Nat
  held : Bool
  heldY0 : Bool
  gainLeft : Nat
  isCit : Bool
  isLPR : Bool
  covExpat : Bool    -- a covered expatriate, §877A(g)(1)
  citUntil : Nat
  lprUntil : Nat
  lprYears : Nat     -- taxable years as a lawful permanent resident so far, §877(e)(2)
  d1 : Nat
  d2 : Nat
  resPrev : Bool
  consec : Nat       -- consecutive calendar years as a resident alien, §7701(b)(10)(A)
  lapseC : Nat       -- first calendar year after the initial residency period closed (99: none)
  lapseExtra : Nat   -- §877(b) excess accumulated since then
  pend : Option Pend
  relocs : Nat
  usTax : Nat
  forTax : Nat
  gainTax : Nat      -- US tax on the gain: income tax (also the donee's), §877A, §7701(b)(10), gift tax, §2801
  exemption : Nat    -- unified credit used, as an amount of taxable gifts (§2505)
  usDays : Nat
  tags : Nat
  deriving BEq, Hashable, Repr, Inhabited

inductive Move where
  | present      -- be in the US for the whole of the next segment
  | absent       -- be outside the US for the whole of the next segment
  | relocate     -- move the tax home and closer connection (US ↔ foreign country), from this day
  | sell         -- sell the asset on the first day of the next segment
  | renounce (certify : Bool)   -- relinquish citizenship, §877A(g)(4); certify 5 years' compliance or not, §877(a)(2)(C)
  | abandon (certify : Bool)    -- cease to be a lawful permanent resident, §7701(b)(6); same certification
  | giftUS       -- give the asset to a US citizen or resident (not a spouse), who sells it
  | giftNRA      -- give the asset to a nonresident alien with a foreign tax home (not a spouse), who sells it
  deriving BEq, Hashable, Repr, DecidableEq

/-- Settle a finished year and carry the §7701(b)(10) bookkeeping. -/
def settle (p : Params) (s : St) (pd : Pend) (y : Nat) (resNext : Bool) : St :=
  let t := yearTax p pd resNext
  let s := { s with usTax := s.usTax + t.us, forTax := s.forTax + t.foreign, gainTax := s.gainTax + t.gainTax,
                    tags := s.tags ||| t.tags }
  if t.resAny then
    -- §7701(b)(10): resident again before the close of the 3rd calendar year beginning after the close of the
    -- initial residency period: the interval is taxed under §877(b) if that is more than the §871 tax.
    let hit := s.lapseC != 99 && y ≤ s.lapseC + 2
    let due := if hit then s.lapseExtra + t.head877 else 0
    let s := { s with usTax := s.usTax + due, gainTax := s.gainTax + due,
                      tags := if due > 0 then s.tags ||| tLapse else s.tags, lapseC := 99, lapseExtra := 0 }
    let c := s.consec + 1
    if resNext then { s with consec := c }
    else if c ≥ 3 then { s with consec := 0, lapseC := y + 1, lapseExtra := t.tail877 }   -- §7701(b)(10)(A): 3 years
    else { s with consec := 0 }
  else
    if s.consec ≥ 3 then { s with consec := 0, lapseC := y, lapseExtra := t.head877 }      -- closed on 31 December
    else if s.lapseC != 99 && y ≤ s.lapseC + 2 then { s with consec := 0, lapseExtra := s.lapseExtra + t.head877 }
    else { s with consec := 0, lapseC := 99, lapseExtra := 0 }

def endYear (p : Params) (s : St) : Option St :=
  let n := p.grid.size
  let days := daysOf p.grid s.mask
  -- the tax-home fact must be honest (see header)
  let fp := firstSegBelow n s.mask n
  let lp := lastSeg n s.mask
  if days ≥ 183 && !((List.range n).all fun i => bit s.homeMask i || (i < fp && !s.homeY0) || i > lp) then none else
  let pd : Pend := { mask := s.mask, homeMask := s.homeMask, saleSeg := s.saleSeg, saleGain := s.saleGain,
                     divSegs := if !s.heldY0 then 0 else if s.saleSeg == 9 then n else s.saleSeg,
                     citUntil := s.citUntil, lprUntil := s.lprUntil, d1 := s.d1, d2 := s.d2, resPrev := s.resPrev }
  let res := resAnyOf p pd
  let s := match s.pend with
    | some q => settle p s q (s.yr - 1) res
    | none => s
  let cd := if p.student then 0 else days
  let s := { s with yr := s.yr + 1, seg := 0, mask := 0, homeMask := 0, saleSeg := 9, saleGain := 0,
                    heldY0 := s.held, homeY0 := s.home, citUntil := if s.isCit then n else 0, lprUntil := if s.isLPR then n else 0,
                    lprYears := s.lprYears + (if s.lprUntil > 0 then 1 else 0),
                    d2 := s.d1, d1 := cd, resPrev := res || s.citUntil > 0, pend := some pd }
  if s.yr == p.horizon then some { settle p s pd (s.yr - 1) s.isLPR with pend := none } else some s

/-- §877A(a): a covered expatriate's property is treated as sold the day before; gain above the exclusion is taxed
(still a citizen or resident that day, so §1411 applies); basis is adjusted (§877A(a)(2), last sentence). -/
def exitTax (p : Params) (s : St) (expat certify : Bool) : St :=
  -- §877A(g)(1)(A), §877(a)(2): covered if the tax or net-worth test is met, or if compliance is not certified
  if expat && (p.covered || !certify) then
    let g := if s.held then s.gainLeft - min s.gainLeft exitExclusion else 0
    let t := bp (ltcgBp + niitBp) g
    { s with usTax := s.usTax + t, gainTax := s.gainTax + t, gainLeft := 0, covExpat := true,
             tags := s.tags ||| tMTM ||| tExpat }
  else { s with tags := s.tags ||| tExpat }

def annualExclusion : Nat := 19000   -- §2503(b), 2025
def giftRateBp : Nat := 4000         -- §2001(c) top rate, used flat (§2502, §2801(a)(1))

/-- Chapter 12 and §2801 on a gift of the asset. "Resident" in chapter 12 is domicile; the model uses the tax home
as the domicile fact (a simplification: domicile is harder to move than a tax home). -/
def giftTransfer (p : Params) (s : St) (doneeUS : Bool) : St :=
  let value := p.basis + p.gain
  let taxable := value - min value annualExclusion
  if s.isCit || s.home then
    -- §2501(a)(1), §2505: a citizen or resident's gift uses the unified credit
    { s with exemption := s.exemption + taxable }
  else
    -- nonresident not a citizen: §2511(a) only US-situs property; §2501(a)(2) no tax on intangibles (stock);
    -- no §2505 credit (it is for "a citizen or resident")
    let chapter12 := if p.asset == .usRealty then bp giftRateBp taxable else 0
    -- §2801(a), (c), (e)(1)(A), (e)(2)(A): a US donee of a covered expatriate pays the top rate unless the gift is
    -- a taxable gift shown on a timely gift tax return
    let s2801 := if s.covExpat && doneeUS && p.asset != .usRealty then bp giftRateBp taxable else 0
    { s with usTax := s.usTax + chapter12 + s2801, gainTax := s.gainTax + chapter12 + s2801 }

def step (p : Params) (s : St) : Move → Option St
  | .present =>
    let s := { s with mask := s.mask ||| (1 <<< s.seg), homeMask := if s.home then s.homeMask ||| (1 <<< s.seg) else s.homeMask,
                      usDays := s.usDays + p.grid[s.seg]!, seg := s.seg + 1 }
    if s.seg == p.grid.size then endYear p s else some s
  | .absent =>
    let s := { s with homeMask := if s.home then s.homeMask ||| (1 <<< s.seg) else s.homeMask, seg := s.seg + 1 }
    if s.seg == p.grid.size then endYear p s else some s
  | .relocate => if s.relocs < p.maxReloc then some { s with home := !s.home, relocs := s.relocs + 1 } else none
  | .sell => if s.held then some { s with held := false, saleSeg := s.seg, saleGain := s.gainLeft, gainLeft := 0 } else none
  | .renounce c =>
    -- §877A(g)(2)(A): any citizen who relinquishes citizenship is an expatriate. A sale earlier the same day was
    -- made as a citizen; the model keeps one order (status change, then sale) per day.
    if s.isCit && s.saleSeg != s.seg then some (exitTax p { s with isCit := false, citUntil := s.seg } true c) else none
  | .abandon c =>
    -- §877A(g)(2)(B), §877(e)(2): only a long-term resident (permanent resident in 8 of the last 15 taxable years)
    if s.isLPR && s.saleSeg != s.seg then
      some (exitTax p { s with isLPR := false, lprUntil := s.seg } (s.lprYears + 1 ≥ 8) c)
    else none
  | .giftUS =>
    if p.gifts && s.held then
      -- §1015(a): the donee takes the donor's basis; a resident donee's sale is taxed under §1(h), §1411
      let t := bp (ltcgBp + niitBp) s.gainLeft
      let s := giftTransfer p s true
      some { s with held := false, saleSeg := s.seg, saleGain := 0, gainLeft := 0, usTax := s.usTax + t,
                    gainTax := s.gainTax + t, tags := s.tags ||| 1024 }
    else none
  | .giftNRA =>
    if p.gifts && s.held then
      -- donee: §865(a)(2) foreign source for stock; §897(a) for realty
      let t := if p.asset == .usRealty then bp ltcgBp s.gainLeft else 0
      let s := giftTransfer p s false
      some { s with held := false, saleSeg := s.seg, saleGain := 0, gainLeft := 0, usTax := s.usTax + t,
                    gainTax := s.gainTax + t, tags := s.tags ||| 2048 }
    else none

/-! ## Search -/

structure Start where
  name : String
  isCit : Bool
  isLPR : Bool
  lprYears : Nat
  priorDays : Nat     -- US days in each of the two preceding years
  resPrev : Bool
  consec : Nat
  homeUS : Bool

def initSt (p : Params) (b : Start) : St :=
  { yr := 0, seg := 0, mask := 0, home := b.homeUS, homeY0 := b.homeUS, homeMask := 0, saleSeg := 9, saleGain := 0, held := true,
    heldY0 := true, gainLeft := p.gain, isCit := b.isCit, isLPR := b.isLPR, covExpat := false,
    citUntil := if b.isCit then p.grid.size else 0,
    lprUntil := if b.isLPR then p.grid.size else 0, lprYears := b.lprYears, d1 := if p.student then 0 else b.priorDays,
    d2 := if p.student then 0 else b.priorDays, resPrev := b.resPrev, consec := b.consec, lapseC := 99,
    lapseExtra := 0, pend := none, relocs := 0, usTax := 0, forTax := 0, gainTax := 0, exemption := 0, usDays := 0,
    tags := 0 }

def allMoves : List Move :=
  [.present, .absent, .relocate, .sell, .renounce true, .renounce false, .abandon true, .abandon false, .giftUS, .giftNRA]

def tagNames (t : Nat) : String :=
  let names := [(tSoldWW, "sold while taxed on worldwide income"), (tSoldNRAForeign, "sold as nonresident, foreign tax home"),
    (tSoldNRAUsUnder183, "sold as nonresident, US tax home, under 183 days"), (tSold871a2, "sold as nonresident, §871(a)(2) 30%"),
    (tLapse, "§7701(b)(10) charge"), (tMTM, "§877A mark to market"), (t911, "§911 exclusion"),
    (tCloser, "closer-connection exception"), (tExpat, "gave up citizenship / green card"),
    (tRealtyNRA, "realty sold as nonresident (§897)"), (1024, "gift to US person"), (2048, "gift to nonresident alien")]
  ", ".intercalate ((names.filter fun (b, _) => t &&& b != 0).map (·.2))

/-- Render a path year by year. -/
def showPath (g : Array Nat) (path : List Move) : String := Id.run do
  let mut out := ""
  let mut yr := 0
  let mut seg := 0
  let mut day := 1
  let mut cur := s!"  y{yr}:"
  for m in path do
    match m with
    | .present => cur := cur ++ s!" US[{day}-{day + g[seg]! - 1}]"; day := day + g[seg]!; seg := seg + 1
    | .absent => cur := cur ++ s!" out[{day}-{day + g[seg]! - 1}]"; day := day + g[seg]!; seg := seg + 1
    | .relocate => cur := cur ++ " RELOCATE"
    | .sell => cur := cur ++ " SELL"
    | .renounce c => cur := cur ++ (if c then " RENOUNCE" else " RENOUNCE(no certification)")
    | .abandon c => cur := cur ++ (if c then " ABANDON-LPR" else " ABANDON-LPR(no certification)")
    | .giftUS => cur := cur ++ " GIFT-TO-US-PERSON"
    | .giftNRA => cur := cur ++ " GIFT-TO-NONRESIDENT"
    if seg == g.size then
      out := out ++ cur ++ "\n"; yr := yr + 1; seg := 0; day := 1; cur := s!"  y{yr}:"
  return out

structure Best where
  us : Nat
  gainTax : Nat
  exemption : Nat
  days : Nat
  path : List Move

/-- Exhaustive depth-first search with deduplication. Objective: US tax on the built-in gain over the horizon
(asset disposed of), ties broken by more days in the US. Plans are grouped by which rules ended up applying. -/
def search (p : Params) (b : Start) : IO Unit := do
  let mut stack : Array (St × List Move) := #[(initSt p b, [])]
  let mut seen : Std.HashSet St := {}
  let mut fam : Std.HashMap Nat Best := {}
  let mut front : Std.HashMap Nat Best := {}
  let mut terminals := 0
  while !stack.isEmpty do
    let (s, path) := stack.back!
    stack := stack.pop
    if s.yr == p.horizon then
      if !s.held && (!p.endInUS || s.d1 ≥ 183 || p.student) then
        terminals := terminals + 1
        let better := fun (o : Option Best) => match o with
          | none => true
          | some x => s.gainTax < x.gainTax || (s.gainTax == x.gainTax && s.usDays > x.days)
        let cand : Best := ⟨s.usTax, s.gainTax, s.exemption, s.usDays, path⟩
        if better (fam.get? s.tags) then fam := fam.insert s.tags cand
        if better (front.get? s.usDays) then front := front.insert s.usDays cand
    else
      for m in allMoves do
        match step p s m with
        | none => pure ()
        | some s' =>
          if !seen.contains s' then
            seen := seen.insert s'
            stack := stack.push (s', m :: path)
  IO.println s!"=== {b.name}; {repr p.asset}; grid {p.grid}; horizon {p.horizon}y; student {p.student}; gifts {p.gifts}; foreign tax: salary {p.f}bp, gain {p.fg}bp ==="
  IO.println s!"positions {seen.size}, finished plans (asset disposed of) {terminals}, families {fam.size}"
  let maxDays := 365 * p.horizon
  -- baseline: sell on day 1, be in the US every day, change nothing
  let plain := (List.replicate (p.horizon * p.grid.size) Move.present).foldl
    (fun (o : Option St) m => o.bind fun s => step p s m)
    ((step p (initSt p b) .sell).bind fun s => if s.home then some s else step p s .relocate)
  match plain with
  | some x => IO.println s!"baseline (sell, in the US every day, no other move): tax on the gain ${x.gainTax}, all US tax ${x.usTax}"
  | none => IO.println "baseline: none"
  let fams := fam.toList.toArray.qsort (fun a b => a.2.gainTax < b.2.gainTax || (a.2.gainTax == b.2.gainTax && a.2.days > b.2.days))
  for (t, x) in fams do
    IO.println s!"- gain tax ${x.gainTax} (all US tax ${x.us}; exemption used ${x.exemption}); US days {x.days}/{maxDays}: {tagNames t}"
    IO.print (showPath p.grid x.path.reverse)
  IO.println "frontier (most US days for each level of tax on the gain):"
  let fr := front.toList.toArray.qsort (fun a b => a.1 > b.1)
  let mut bestSoFar : Option Nat := none
  for (d, x) in fr do
    if bestSoFar.all (fun t => x.gainTax < t) then
      bestSoFar := some x.gainTax
      IO.println s!"  days {d}: gain tax ${x.gainTax} (all US tax ${x.us})"
      IO.print (showPath p.grid x.path.reverse)

/-- The fine grid (see header). -/
def fine : Array Nat := #[30, 90, 62, 1, 182]
/-- Three cuts: day 30 and day 182. -/
def coarse : Array Nat := #[30, 152, 183]
/-- Whole years. -/
def whole : Array Nat := #[365]
/-- One cut after day 183: the last 182 days of the year. -/
def arrival : Array Nat := #[183, 182]

def base : Params :=
  { grid := fine, asset := .usStock, salary := 300000, gain := 1000000, div := 30000, f := 0, fg := 0, covered := true,
    student := false, horizon := 2, maxReloc := 2, gifts := false, basis := 500000, endInUS := false }

def visaHolder : Start := ⟨"alien resident by substantial presence (no green card), 5 years in", false, false, 0, 365, true, 5, true⟩
def greenCard9 : Start := ⟨"green-card holder, 9th year (long-term resident)", false, true, 8, 365, true, 8, true⟩
def greenCard3 : Start := ⟨"green-card holder, 3rd year", false, true, 2, 365, true, 2, true⟩
def citizen : Start := ⟨"citizen", true, false, 0, 365, true, 0, true⟩
def newcomer : Start := ⟨"alien abroad, never resident", false, false, 0, 0, false, 0, false⟩
def student : Start := ⟨"F-1 student, in the US", false, false, 0, 365, false, 0, true⟩

/-! Recorded runs -/

/-!
The searches below run in about a minute together. Other recorded runs (output in `tools/hunt/out/Residence/`):
the fine grid over two years for the visa holder, the newcomer and the student; citizen and green-card holders with
and without the §877(a)(2) wealth test; US realty; gifts; foreign tax 25% / 15%; whole-year grid over six years.
-/

-- foreign-corporation stock, three years: the year of absence and the return
#eval search { base with grid := coarse, asset := .foreignStock, horizon := 3 } visaHolder
-- the same with domestic stock
#eval search { base with grid := coarse, horizon := 3 } visaHolder
-- long-term green-card holder below the wealth test, US realty
#eval search { base with grid := coarse, asset := .usRealty, covered := false } greenCard9
-- long-term green-card holder above the wealth test, domestic stock
#eval search { base with grid := coarse } greenCard9
-- arriving
#eval search { base with grid := arrival } newcomer
#eval search { base with grid := arrival, student := true } student
-- six whole years, plans that end back in the US
#eval search { base with grid := whole, horizon := 6, maxReloc := 4, endInUS := true } visaHolder

end Legal.USTax.Hunt.Residence
