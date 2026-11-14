import Std

/-!
# Financial instruments: timing and character of investment gain (tax years 2025–2026 rates)

Part A of this file writes down what the Code does to an individual investor's positions in actively traded property:
when gain or loss is taken into account, and whether it is short-term, long-term or 60/40. Part B is a blind search
over every sequence of trades that keeps the investor's market exposure equal to a prescribed schedule, so the pre-tax
economic result of every plan is the same and only the tax differs.

Nothing in Part A names a technique. Each rule cites its provision.

Simplifications, each stated once:
* positions are single units of one "index" exposure; every instrument in a world follows the same price path
  (so a switch between instruments leaves the pre-tax result unchanged; real substitutes track less than perfectly);
* no transaction costs, no dividends or interest in this part (Part C has income instruments);
* the taxpayer is an individual in the top brackets: ordinary 37% (§1(j)), net capital gain 20% (§1(h)(1)(D)),
  §1411 3.8% on net gain; the §1211(b) $3,000 is deducted at 37%;
* "substantially identical" is decided by an instrument's class; an index future is treated as a contract to acquire
  the index fund of its class (conservative for §1091(a) and §1259(c)(1)(C));
* any long and any short position in the same world are treated as offsetting (§1092(c)(2), (d)(3)(A)(i)), again the
  conservative reading;
* `regs = true` adds Temp. Reg. §1.1092(b)-2T (holding period and loss character in straddles), which §1092(b)(1)
  directs; `regs = false` is the statute alone.
-/

namespace Legal.USTax.Hunt.Instruments

/-! ## Part A. Rules -/

structure Inst where
  name : String
  cls : Nat          -- instruments of one class are "substantially identical" to each other
  security : Bool    -- "stock or securities": §1091(a), §1233(e)(2)(A)
  acq : Bool         -- acquiring it is acquiring stock or securities, or a contract to acquire them: §1091(a)
  afp : Bool         -- stock, debt instrument, partnership interest (§1259(b)(1)) or actively traded trust (§1259(e)(2))
  m2m : Bool         -- section 1256 contract (§1256(b))
  deriving Repr, BEq, Hashable, Inhabited

/-- Character: short-term, long-term (§1222), section 1256 (60/40 under §1256(a)(3)), or 60/40 assigned by
Temp. Reg. §1.1092(b)-2T(b)(2) to a loss on the non-1256 leg of a mixed straddle. -/
inductive Ch where
  | st | lt | m | split
  deriving Repr, BEq, Hashable

structure Lot where
  inst : Nat
  long : Bool
  opened : Nat                         -- day
  basis : Int                          -- cost (long) or sale proceeds (short), after adjustments
  hp : Int                             -- day the holding period starts (§1223)
  noHP : Bool := false                 -- §1233(b)(2): holding period begins only when the short is closed
  stGain : Bool := false               -- short: §1233(b)(1)
  ltLoss : Bool := false               -- short: §1233(d)
  mixed : Bool := false                -- has been the non-1256 leg of a mixed straddle (§1256(d)(4))
  cs : Option (Nat × Int) := none      -- §1259: a transaction that would be a constructive sale (day, price)
  csClosed : Option Nat := none        -- §1259(c)(3): the day that transaction was closed
  deriving Repr, BEq, Hashable

/-- A realized loss that is not yet final: §1091 can still reach it for 30 days, and §1092(a)(1) tests it at year end. -/
structure PL where
  inst : Nat
  opened : Nat
  cls : Nat
  day : Nat
  amt : Int            -- negative
  ch : Ch
  held : Int
  year : Nat
  offs : List (Nat × Nat)   -- (inst, opened) of the offsetting positions when the loss arose
  washA : Bool         -- loss on a sale of stock or securities, §1091(a)
  washE : Bool         -- loss on closing a short sale of stock or securities, §1091(e)
  final : Bool
  deriving Repr, BEq, Hashable

structure Yr where
  st : Int := 0
  lt : Int := 0
  m : Int := 0         -- net gain or loss from section 1256 contracts
  deriving Repr, BEq, Hashable

structure St where
  di : Nat
  lots : List Lot
  yrs : List Yr
  pls : List PL
  buys : List (Nat × Nat × Nat)          -- acquisitions in the last 30 days: (inst, class, day)
  sales : List (Nat × Nat × Nat × Bool)  -- sales and short sales in the last 30 days: (inst, class, day, is a short sale)
  deriving Repr, BEq, Hashable

structure Sc where
  name : String
  world : Array Inst
  days : Array Nat
  px : Array Int
  expo : Array (List Int) -- net units of exposure the investor may hold on leaving each date
  start : List Lot := []
  gST : List Int         -- other short-term gain of each year (given, not chosen)
  gLT : List Int         -- other long-term gain of each year
  regs : Bool := true
  maxLots : Nat := 3
  maxTrades : Nat := 2

def yearOf (d : Nat) : Nat := d / 365
def yearEnd (y : Nat) : Nat := y * 365 + 364

def modAt (l : List α) (i : Nat) (f : α → α) : List α := l.mapIdx fun j x => if j == i then f x else x

def addYr (yr : Yr) (amt : Int) : Ch → Yr
  | .st => { yr with st := yr.st + amt }
  | .lt => { yr with lt := yr.lt + amt }
  | .m => { yr with m := yr.m + amt }
  | .split => { yr with st := yr.st + amt * 4 / 10, lt := yr.lt + (amt - amt * 4 / 10) }

def book (s : St) (y : Nat) (amt : Int) (ch : Ch) : St := { s with yrs := modAt s.yrs y (addYr · amt ch) }

def sameLot (a b : Lot) : Bool := a.inst == b.inst && a.opened == b.opened && a.long == b.long
def setLot (s : St) (l : Lot) : St := { s with lots := s.lots.map fun x => if sameLot x l then l else x }
def dropLot (s : St) (l : Lot) : St := { s with lots := s.lots.filter fun x => !sameLot x l }

/-- §1259(a): gain is recognized as if the position were sold at its value on the day of the constructive sale; basis
is adjusted and the holding period starts again on that day. -/
def csGain (s : St) (l : Lot) : St × Lot :=
  match l.cs with
  | none => (s, l)
  | some (t1, p1) =>
    let g := if l.long then p1 - l.basis else l.basis - p1
    let ch := if l.long && !l.noHP && (t1 : Int) - l.hp > 365 then Ch.lt else Ch.st
    (book s (yearOf t1) g ch, { l with basis := p1, hp := t1, cs := none, csClosed := none })

/-- Do a long position `l` and a short position in `sh` fall under the short-sale holding-period rules?
§1233(b), (d) with (e)(2)(A): stocks and securities that are substantially identical. Temp. Reg. §1.1092(b)-2T(a), (b)
extends the same principles to every straddle (not one made only of section 1256 contracts, §1256(a)(4)). -/
def hpRule (sc : Sc) (l sh : Inst) : Bool :=
  !l.m2m && ((l.cls == sh.cls && l.security && sh.security) || (sc.regs && !(l.m2m && sh.m2m)))

/-- A loss has been realized on `closed` (already removed from `s.lots`). -/
def lossEvent (sc : Sc) (s : St) (closed : Lot) (t : Nat) (amt : Int) (ch : Ch) (held : Int) (isShort : Bool) : St :=
  let I := sc.world[closed.inst]!
  -- §1091(a): substantially identical stock or securities acquired within the 30 days before the sale
  let prior := if I.security && !isShort then
      s.buys.find? fun (i, c, d) => c == I.cls && !(i == closed.inst && d == closed.opened) && d + 30 ≥ t
    else none
  match prior with
  | some (i, c, d) =>
    -- §1091(d): the loss goes into the basis of the replacement; §1223(3): its holding period includes the old one
    { s with buys := s.buys.erase (i, c, d)
             lots := s.lots.map fun x => if x.inst == i && x.opened == d && x.long then
               -- Temp. Reg. §1.1092(b)-1T(c): a straddle loss keeps the character fixed at the disposition
               { x with basis := x.basis - amt, hp := if x.noHP then x.hp else x.hp - held,
                        mixed := x.mixed || ch == Ch.split } else x }
  | none =>
  -- §1091(e): within the 30 days before closing the short, substantially identical stock or securities were sold or
  -- another short sale was entered into
  let priorE := if I.security && isShort then
      s.sales.find? fun (i, c, d, so) => c == I.cls && !(so && i == closed.inst && d == closed.opened) && d + 30 ≥ t
    else none
  match priorE with
  | some (i, c, d, so) =>
    { s with sales := s.sales.erase (i, c, d, so)
             lots := s.lots.map fun x => if so && x.inst == i && x.opened == d && !x.long then
               { x with basis := x.basis + amt, mixed := x.mixed || ch == Ch.split } else x }
  | none =>
    -- §1092(a)(1): held for the year-end test against unrecognized gain in the offsetting positions
    let offLots := s.lots.filter fun x => x.long != closed.long && !((sc.world[x.inst]!).m2m && I.m2m)
    let ch' := ch
    { s with pls := { inst := closed.inst, opened := closed.opened, cls := I.cls, day := t, amt := amt, ch := ch',
                      held := held, year := yearOf t, offs := offLots.map (fun x => (x.inst, x.opened)),
                      washA := I.security && !isShort, washE := I.security && isShort, final := false } :: s.pls }

/-- Bookkeeping after `closed` leaves the position at day `t`. -/
def afterClose (sc : Sc) (s : St) (closed : Lot) (t : Nat) : St :=
  let C := sc.world[closed.inst]!
  let lots' : List Lot := s.lots.map (fun (x : Lot) =>
      let X := sc.world[x.inst]!
      -- §1259(c)(3)(A)(i): the transaction that would cause the constructive sale is closed
      let x := match x.cs, x.csClosed with
        | some (t1, _), none =>
          if x.long != closed.long && X.cls == C.cls && closed.opened ≥ t1 &&
             !(s.lots.any fun n => n.long != x.long && (sc.world[n.inst]!).cls == X.cls && n.opened ≥ t1)
          then { x with csClosed := some t } else x
        | _, _ => x
      -- §1233(b)(2): the holding period begins on the date of the closing of the short sale
      if x.long && x.noHP && !closed.long &&
         !(s.lots.any fun n => !n.long && hpRule sc X (sc.world[n.inst]!))
      then { x with noHP := false, hp := t } else x)
  let s : St := { s with lots := lots' }
  -- §1259(c)(3)(A)(iii): the 60 days cannot start while another offsetting position is still held
  s.lots.foldl (fun s x =>
    if x.csClosed == some t && (s.lots.any fun n => n.long != x.long) then
      let (s, x') := csGain s x; setLot s x' else s) s

/-- §1256(d)(4): a straddle in which at least one but not all positions are section 1256 contracts. A new position
`lot` joins the positions of opposite sign already held. -/
def markMixed (sc : Sc) (s : St) (lot : Lot) : St × Lot :=
  let L := sc.world[lot.inst]!
  let opp := s.lots.filter fun x => x.long != lot.long
  if !sc.regs then (s, lot)
  else if L.m2m then
    ({ s with lots := s.lots.map fun x => if x.long != lot.long && !(sc.world[x.inst]!).m2m then { x with mixed := true } else x }, lot)
  else (s, { lot with mixed := opp.any fun x => (sc.world[x.inst]!).m2m })

/-- Buy one unit of `j` at today's price. -/
def openLong (sc : Sc) (s : St) (j : Nat) : St :=
  let t := sc.days[s.di]!
  let p := sc.px[s.di]!
  let J := sc.world[j]!
  -- §1259(c)(3)(A)(iii) with §246(c)(4)(C): during the 60 days after the transaction is closed, risk of loss is
  -- reduced again by a position in substantially similar or related property (any instrument of this world)
  let s := s.lots.foldl (fun s x =>
    if !x.long && x.cs.isSome && x.csClosed.isSome then
      let (s, x') := csGain s x; setLot s x' else s) s
  -- §1259(c)(1)(D): an appreciated short position and the taxpayer acquires the same or substantially identical property
  let hit := s.lots.find? fun x => !x.long && (sc.world[x.inst]!).afp && !(sc.world[x.inst]!).m2m &&
    (sc.world[x.inst]!).cls == J.cls && x.basis > p && x.cs.isNone
  let s := match hit with
    | some x => setLot s { x with cs := some (t, p) }
    | none => s
  -- §1233(b): substantially identical property acquired after the short sale and before its closing
  let shorts := s.lots.filter fun x => !x.long && hpRule sc J (sc.world[x.inst]!)
  let already := (s.lots.filter fun x => x.long && x.noHP).length
  let noHP := !shorts.isEmpty && (sc.regs || already < shorts.length)
  let s := if noHP then
      { s with lots := s.lots.map fun x => if !x.long && hpRule sc J (sc.world[x.inst]!) then { x with stGain := true } else x }
    else s
  let lot : Lot := { inst := j, long := true, opened := t, basis := p, hp := t, noHP := noHP }
  let (s, lot) := markMixed sc s lot
  -- §1091(a): acquired within the 30 days after a sale at a loss
  let pend := if J.acq then s.pls.find? fun q => q.washA && q.cls == J.cls && q.day + 30 ≥ t else none
  match pend with
  | some q =>
    let same := fun (r : PL) => r.inst == q.inst && r.opened == q.opened && r.day == q.day
    let tot := (s.pls.filter same).foldl (fun a r => a + r.amt) 0
    let lot := { lot with basis := p - tot, hp := if noHP then lot.hp else lot.hp - q.held,
                          mixed := lot.mixed || q.ch == Ch.split }
    { s with pls := s.pls.filter (fun r => !same r), lots := s.lots ++ [lot] }
  | none =>
    { s with lots := s.lots ++ [lot], buys := if J.acq then (j, J.cls, t) :: s.buys else s.buys }

/-- Sell one unit of `j` short at today's price. -/
def openShort (sc : Sc) (s : St) (j : Nat) : St :=
  let t := sc.days[s.di]!
  let p := sc.px[s.di]!
  let J := sc.world[j]!
  let s := s.lots.foldl (fun s x =>
    if x.long && x.cs.isSome && x.csClosed.isSome then
      let (s, x') := csGain s x; setLot s x' else s) s
  -- §1233(b), (d), read at the date of the short sale, before §1259 resets anything
  let cands := s.lots.filter fun x => x.long && hpRule sc (sc.world[x.inst]!) J
  let ltLoss := cands.any fun x => !x.noHP && (t : Int) - x.hp > 365
  let young := cands.filter fun x => x.noHP || (t : Int) - x.hp ≤ 365
  let hitHP := if sc.regs then young else (young.filter fun x => !x.noHP).take 1
  let s := { s with lots := s.lots.map fun x => if hitHP.any (sameLot x) then { x with noHP := true } else x }
  -- §1259(c)(1)(A), (C): short sale of, or futures contract to deliver, the same or substantially identical property
  let hit := s.lots.find? fun x => x.long && (sc.world[x.inst]!).afp && !(sc.world[x.inst]!).m2m &&
    (sc.world[x.inst]!).cls == J.cls && p > x.basis && x.cs.isNone
  let s := match hit with
    | some x => setLot s { x with cs := some (t, p) }
    | none => s
  let lot : Lot := { inst := j, long := false, opened := t, basis := p, hp := t, stGain := !young.isEmpty, ltLoss := ltLoss }
  let (s, lot) := markMixed sc s lot
  -- §1091(e)(2): another short sale within the 30 days after closing a short at a loss
  let pend := if J.security then s.pls.find? fun q => q.washE && q.cls == J.cls && q.day + 30 ≥ t else none
  match pend with
  | some q =>
    let same := fun (r : PL) => r.inst == q.inst && r.opened == q.opened && r.day == q.day
    let tot := (s.pls.filter same).foldl (fun a r => a + r.amt) 0
    { s with pls := s.pls.filter (fun r => !same r), lots := s.lots ++ [{ lot with basis := p + tot, mixed := lot.mixed || q.ch == Ch.split }] }
  | none =>
    { s with lots := s.lots ++ [lot], sales := if J.security then (j, J.cls, t, true) :: s.sales else s.sales }

/-- Sell a long position at today's price. -/
def sellLong (sc : Sc) (s : St) (k : Lot) : St :=
  let t := sc.days[s.di]!
  let p := sc.px[s.di]!
  let K := sc.world[k.inst]!
  let (s, k) := csGain s k          -- §1259(e)(1): the position deemed sold is now disposed of
  let s := dropLot s k
  let amt := p - k.basis
  let held := (t : Int) - k.hp
  let ch := if K.m2m then Ch.m else if !k.noHP && held > 365 then Ch.lt else Ch.st   -- §1222; §1233(b)(2)
  let ch := if k.mixed && amt < 0 then Ch.split else ch       -- Temp. Reg. §1.1092(b)-2T(b)(2)
  let s := if amt ≥ 0 then book s (yearOf t) amt ch else lossEvent sc s k t amt ch (if k.noHP then 0 else held) false
  -- §1091(e)(1): substantially identical stock sold within the 30 days after closing a short at a loss
  let s := if K.security then
      match s.pls.find? fun q => q.washE && q.cls == K.cls && q.day + 30 ≥ t with
      | some q => { s with pls := s.pls.filter fun r => !(r.inst == q.inst && r.opened == q.opened && r.day == q.day) }
      | none => { s with sales := (k.inst, K.cls, t, false) :: s.sales }
    else s
  afterClose sc s k t

/-- Close a short position, by buying at today's price or by delivering a long position already held (§1233(a)). -/
def closeShort (sc : Sc) (s : St) (k : Lot) (deliv : Option Lot) : St :=
  let t := sc.days[s.di]!
  let p := sc.px[s.di]!
  let K := sc.world[k.inst]!
  let (s, k) := csGain s k
  let s := dropLot s k
  let (s, cost, heldLT, dl) := match deliv with
    | none => (s, p, false, none)
    | some l =>
      let (s, l) := csGain s l
      (dropLot s l, l.basis, !l.noHP && (t : Int) - l.hp > 365, some l)
  let amt := k.basis - cost
  let ch := if K.m2m then Ch.m
    else if amt ≥ 0 then (if k.stGain || !heldLT then Ch.st else Ch.lt)     -- §1233(a), (b)(1)
    else (if k.mixed then Ch.split                                          -- Temp. Reg. §1.1092(b)-2T(b)(2)
          else if k.ltLoss || heldLT then Ch.lt else Ch.st)                 -- §1233(d)
  let s := if amt ≥ 0 then book s (yearOf t) amt ch else lossEvent sc s k t amt ch 0 true
  let s := afterClose sc s k t
  match dl with
  | some l => afterClose sc s l t
  | none => s

/-- The close of taxable year `y`, at price `p`. -/
def yearEndProc (sc : Sc) (s : St) (y : Nat) (p : Int) : St :=
  -- §1256(a)(1)–(2): each section 1256 contract is treated as sold at its value; later gain or loss is adjusted.
  -- §1092(d)(5)(A): a loss so taken on a contract in a mixed straddle is subject to §1092(a).
  let s := s.lots.foldl (fun s x =>
    if (sc.world[x.inst]!).m2m then
      let amt := if x.long then p - x.basis else x.basis - p
      let s := setLot s { x with basis := p }
      if amt ≥ 0 then book s y amt .m else
        let offs := s.lots.filter fun n => n.long != x.long && !(sc.world[n.inst]!).m2m
        if offs.isEmpty then book s y amt .m else
          { s with pls := { inst := x.inst, opened := x.opened, cls := (sc.world[x.inst]!).cls, day := yearEnd y, amt := amt,
                            ch := .m, held := 0, year := y, offs := offs.map (fun n => (n.inst, n.opened)),
                            washA := false, washE := false, final := false } :: s.pls }
    else s) s
  -- §1092(a)(1)(A): a loss is taken into account only to the extent it exceeds the unrecognized gain (§1092(a)(3)(A))
  -- in the offsetting positions at the close of the year; (B): the rest is treated as sustained in the next year.
  { s with pls := s.pls.flatMap fun q =>
      if q.final || q.year != y then [q]
      else if q.offs.isEmpty then [{ q with final := true }]
      else
        let u := s.lots.foldl (fun a x =>
          if q.offs.contains (x.inst, x.opened) then
            a + max 0 (if x.long then p - x.basis else x.basis - p) else a) (0 : Int)
        let d := min (-q.amt) u
        (if q.amt + d < 0 then [{ q with amt := q.amt + d, final := true }] else []) ++
        (if d > 0 then [{ q with amt := -d, year := y + 1 }] else []) }

def exposure (s : St) : Int := s.lots.foldl (fun a x => a + (if x.long then 1 else -1)) 0

/-- Move to the next date. -/
def advance (sc : Sc) (s : St) : St :=
  let t := sc.days[s.di]!
  let s := if t == yearEnd (yearOf t) then yearEndProc sc s (yearOf t) (sc.px[s.di]!) else s
  let t' := sc.days[s.di + 1]!
  -- §1259(c)(3)(A): the transaction is disregarded only if closed by the 30th day after the year and the position is
  -- then held, unhedged, for 60 days
  let s := s.lots.foldl (fun s x =>
    match x.cs, x.csClosed with
    | some (t1, _), none => if t' > yearEnd (yearOf t1) + 30 then (let (s, x') := csGain s x; setLot s x') else s
    | some _, some t2 => if t' ≥ t2 + 60 then setLot s { x with cs := none, csClosed := none } else s
    | _, _ => s) s
  { s with di := s.di + 1
           buys := s.buys.filter (fun (_, _, d) => d + 30 ≥ t')
           sales := s.sales.filter (fun (_, _, d, _) => d + 30 ≥ t') }

/-! ### Tax for the years (§§1(h), 1211(b), 1212(b), 1212(c), 1222, 1256(a)(3), 1411) -/

def ordR : Int := 3700
def ltR : Int := 2000
def niitR : Int := 380

/-- One year. `st`, `lt` are the year's net short- and long-term amounts before carryovers. Returns tax ×10000 and
the carryovers to the next year (§1212(b)(1), with the §1211(b) amount treated as short-term gain, §1212(b)(2)). -/
def yearTax (st lt stCF ltCF : Int) : Int × Int × Int :=
  let S := st - stCF
  let L := lt - ltCF
  if S ≥ 0 && L ≥ 0 then (S * (ordR + niitR) + L * (ltR + niitR), 0, 0)
  else if S + L ≥ 0 then
    if S < 0 then ((S + L) * (ltR + niitR), 0, 0) else ((S + L) * (ordR + niitR), 0, 0)
  else
    let ded := min 3000 (-(S + L))
    let S2 := S + ded
    (-(ded * ordR), max 0 (-S2 - max 0 L), max 0 (-L - max 0 S2))

/-- Future value at the end of the last year of all tax, ×10000, at 4% a year. `elect y` is the §1212(c) election for
a net section 1256 contracts loss of year `y`: carried back to the three preceding years against net section 1256
contract gain, 40% short-term and 60% long-term; the refund is counted as received in the loss year. -/
def taxFV (yrs : List (Int × Int × Int)) (elect : Nat → Bool) : Int := Id.run do
  let n := yrs.length
  let mut st : Array Int := #[]
  let mut lt : Array Int := #[]
  let mut mg : Array Int := #[]      -- net section 1256 contract gain still open to carrybacks, §1212(c)(5)
  let mut cfIn : Array (Int × Int) := #[]
  let mut cur : Array Int := #[]     -- tax of each year as last recomputed
  let mut cash : Array Int := #[]    -- cash paid (or refunded) at the end of each year
  let mut sCF : Int := 0
  let mut lCF : Int := 0
  for y in [0:n] do
    let (s0, l0, m) := yrs[y]!
    let S := s0 + m * 4 / 10         -- §1256(a)(3)
    let L := l0 + (m - m * 4 / 10)
    let (tx, s1, l1) := yearTax S L sCF lCF
    let mut txy := tx
    let mut s1 := s1
    let mut l1 := l1
    st := st.push S; lt := lt.push L; cfIn := cfIn.push (sCF, lCF)
    mg := mg.push (max 0 (min m (S - sCF + L - lCF)))
    if elect y && m < 0 && s1 + l1 > 0 then
      let mut a := min (-m) (s1 + l1)          -- §1212(c)(4)
      let mut used : Int := 0
      for p in [(if y ≥ 3 then y - 3 else 0):y] do
        let u := min a mg[p]!                  -- §1212(c)(3)(A)
        if u > 0 then
          let S' := st[p]! - u * 4 / 10
          let L' := lt[p]! - (u - u * 4 / 10)
          let (c1, c2) := cfIn[p]!
          let (tnew, _, _) := yearTax S' L' c1 c2
          txy := txy - (cur[p]! - tnew)
          st := st.set! p S'; lt := lt.set! p L'; cur := cur.set! p tnew
          mg := mg.set! p (mg[p]! - u)
          a := a - u; used := used + u
      -- §1212(c)(6)(A): the amount carried back is treated as gain of the loss year in computing the carryover
      let (_, s2, l2) := yearTax (S + used * 4 / 10) (L + (used - used * 4 / 10)) sCF lCF
      s1 := s2; l1 := l2
    cur := cur.push tx
    cash := cash.push txy
    sCF := s1; lCF := l1
  let mut fv : Int := 0
  for y in [0:n] do
    fv := fv * 104 / 100 + cash[y]!
  return fv

/-- The year figures: what was booked, plus the losses that became final, plus the given other gains. -/
def yearFigures (sc : Sc) (s : St) : List (Int × Int × Int) :=
  let yrs := s.pls.foldl (fun ys q => if q.final || q.offs.isEmpty then modAt ys q.year (addYr · q.amt q.ch) else ys) s.yrs
  yrs.mapIdx fun i y => (y.st + (sc.gST.getD i 0), y.lt + (sc.gLT.getD i 0), y.m)

/-- Tax (future value, dollars) with the §1212(c) election made or not in each year, whichever is lower. -/
def bestTax (sc : Sc) (s : St) : Int :=
  let f := yearFigures sc s
  let n := f.length
  let cands := (List.range (2 ^ n)).map fun mask => taxFV f (fun y => (mask / 2 ^ y) % 2 == 1)
  (cands.foldl min (cands.headD 0)) / 10000

/-! ## Part B. Search

Every sequence of at most `maxTrades` trades at each date, at most `maxLots` positions open, such that the net
exposure on leaving each date equals the schedule. Two valuations at the last date (a 31 December):
`sold` closes everything (so every plan ends in cash); `kept` keeps the final positions (unrealized gain untaxed,
as at a §1014 step-up or indefinite deferral). The score is the future value of all tax; pre-tax wealth is the same
for every plan. Plans are grouped into families by the kinds of trade they use. -/

def iname (sc : Sc) (i : Nat) : String := (sc.world[i]!).name

def expand (sc : Sc) (plainOnly : Bool) (s : St) : List ((String × String) × St) :=
  let t := sc.days[s.di]!
  let room := s.lots.length < sc.maxLots
  if plainOnly then
    (if s.lots.isEmpty then [((s!"buy {iname sc 0}", s!"day {t}: buy {iname sc 0}"), openLong sc s 0)] else []) ++
    (s.lots.filter (fun x => x.opened != t)).map fun x =>
      ((s!"sell {iname sc 0}", s!"day {t}: sell {iname sc 0} (bought day {x.opened})"), sellLong sc s x)
  else
  let opens := (List.range sc.world.size).flatMap fun j =>
    let J := sc.world[j]!
    let hasToday := fun (lg : Bool) => s.lots.any fun x => x.inst == j && x.opened == t && x.long == lg
    -- a section 1256 contract is one contract: the opposite trade closes it
    let opp := fun (lg : Bool) => J.m2m && s.lots.any fun x => x.inst == j && x.long != lg
    (if room && !hasToday true && !opp true then
       [((s!"buy {J.name}", s!"day {t}: buy {J.name}"), openLong sc s j)] else []) ++
    (if room && !hasToday false && !opp false then
       [((s!"short {J.name}", s!"day {t}: sell {J.name} short"), openShort sc s j)] else [])
  let closes := s.lots.flatMap fun x =>
    if x.opened == t then [] else
    let n := iname sc x.inst
    if x.long then
      [((s!"sell {n}", s!"day {t}: sell {n} (bought day {x.opened})"), sellLong sc s x)] ++
      (s.lots.filter (fun k => !k.long && k.inst == x.inst && k.opened != t && !(sc.world[x.inst]!).m2m)).map fun k =>
        ((s!"deliver {n}", s!"day {t}: deliver {n} (bought day {x.opened}) to close the short of day {k.opened}"),
         closeShort sc s k (some x))
    else
      [((s!"cover {n}", s!"day {t}: buy to close the {n} short of day {x.opened}"), closeShort sc s x none)]
  opens ++ closes

def liquidate (sc : Sc) (s : St) : St := Id.run do
  let mut s := s
  for _ in [0:sc.maxLots + 1] do
    match s.lots.head? with
    | none => pure ()
    | some x => s := if x.long then sellLong sc s x else closeShort sc s x none
  let t := sc.days[s.di]!
  return yearEndProc sc s (yearOf t) (sc.px[s.di]!)

def holdOut (sc : Sc) (s : St) : St :=
  let t := sc.days[s.di]!
  let s := yearEndProc sc s (yearOf t) (sc.px[s.di]!)
  -- a constructive-sale transaction still open will pass the §1259(c)(3) deadline
  s.lots.foldl (fun s x => match x.cs, x.csClosed with
    | some _, none => (csGain s x).1
    | _, _ => s) s

def unrealized (sc : Sc) (s : St) : Int :=
  let p := sc.px[s.di]!
  s.lots.foldl (fun a x => a + (if x.long then p - x.basis else x.basis - p)) 0

def init (sc : Sc) : St :=
  { di := 0, lots := sc.start, yrs := sc.gST.map (fun _ => {}), pls := [], buys := [], sales := [] }

abbrev Path := List (String × String)

def family (p : Path) : List String :=
  ((p.map (·.1)).foldl (fun acc k => if acc.contains k then acc else acc ++ [k]) []).toArray.qsort (· < ·) |>.toList

def explore (sc : Sc) (plainOnly : Bool) : Nat × Std.HashMap St Path := Id.run do
  let mut frontier : Std.HashMap St Path := {}
  frontier := frontier.insert (init sc) []
  let n := sc.days.size
  let mut visited := 0
  for i in [0:n - 1] do
    let mut all := frontier
    let mut layer := frontier
    for _ in [0:sc.maxTrades] do
      let mut nxt : Std.HashMap St Path := {}
      for (s, path) in layer do
        for (lab, s') in expand sc plainOnly s do
          match all.get? s' with
          | none =>
            all := all.insert s' (lab :: path)
            nxt := nxt.insert s' (lab :: path)
          | some old => if path.length + 1 < old.length then all := all.insert s' (lab :: path)
      layer := nxt
    let mut nf : Std.HashMap St Path := {}
    for (s, path) in all do
      if (sc.expo[i]!).contains (exposure s) then
        let s' := advance sc s
        if (nf.get? s').all (fun old => path.length < old.length) then nf := nf.insert s' path
    visited := visited + all.size
    frontier := nf
  return (visited, frontier)

def search (sc : Sc) (top : Nat := 8) : IO Unit := do
  let (visited, frontier) := explore sc false
  -- the plain plan: only buying and selling the first instrument, with the fewest trades
  let mut base : Option (Nat × Int × Int) := none
  for (s, path) in (explore sc true).2 do
    if base.all (fun b => path.length < b.1) then
      base := some (path.length, bestTax sc (liquidate sc s), bestTax sc (holdOut sc s))
  -- valuation
  let mut famL : Std.HashMap (List String) (Int × Int × Int × Path) := {}
  let mut famH : Std.HashMap (List String) (Int × Int × Int × Path) := {}
  for (s, path) in frontier do
    let tl := bestTax sc (liquidate sc s)
    let sh := holdOut sc s
    let th := bestTax sc sh
    let u := unrealized sc sh
    let f := family path
    if (famL.get? f).all (fun b => tl < b.1) then famL := famL.insert f (tl, th, u, path)
    if (famH.get? f).all (fun b => th < b.2.1 || (th == b.2.1 && tl < b.1)) then famH := famH.insert f (tl, th, u, path)
  let (_, bl, bh) := base.getD (0, 0, 0)
  IO.println s!"=== {sc.name} (regs {sc.regs}) ==="
  IO.println s!"positions examined {visited}; final positions {frontier.size}; families {famL.size}"
  IO.println s!"plain plan: tax (future value) if everything is sold at the end ${bl}; if the final position is kept ${bh}"
  let show1 := fun (title : String) (arr : Array (List String × (Int × Int × Int × Path))) (useHold : Bool) => do
    IO.println s!"-- {title} --"
    for (f, (tl, th, u, path)) in arr.toList.take top do
      let d := if useHold then bh - th else bl - tl
      IO.println s!"saves ${d} (tax sold ${tl}, kept ${th}, unrealized at end ${u}) using {f}"
      for (_, txt) in path.reverse do IO.println s!"     {txt}"
  show1 "best families, everything sold at the end" (famL.toArray.qsort (fun a b => a.2.1 < b.2.1)) false
  show1 "best families, final position kept" (famH.toArray.qsort (fun a b => a.2.2.1 < b.2.2.1)) true

/-! ### Worlds -/

/-- An index fund share, a second fund that is not substantially identical, and the regulated futures contract. -/
def stockWorld : Array Inst := #[
  { name := "FundA", cls := 0, security := true, acq := true, afp := true, m2m := false },
  { name := "FundB", cls := 1, security := true, acq := true, afp := true, m2m := false },
  { name := "IndexFuture", cls := 0, security := true, acq := true, afp := false, m2m := true }]

/-- A digital asset held directly (not stock, not a security: outside §1091, §1233(b)/(d), §1259), a share of an
actively traded grantor trust holding it (stock for §1259 by §1259(e)(2); treated as a security for §1091, the
conservative reading), and the regulated futures contract on it (§1256(b)(1)(A)). -/
def digitalWorld : Array Inst := #[
  { name := "Coin", cls := 0, security := false, acq := false, afp := false, m2m := false },
  { name := "CoinTrust", cls := 0, security := true, acq := true, afp := true, m2m := false },
  { name := "CoinFuture", cls := 0, security := false, acq := false, afp := false, m2m := true }]

def k (x : Int) : Int := x * 1000

def held (day : Nat) (basis : Int) : Lot := { inst := 0, long := true, opened := day, basis := basis, hp := day }

/-- Bought in January of year 1 at 100; dip to 80 in June; 120 at year end; 150 at the end of year 2.
Exposure of one unit throughout. `g` is other short-term gain in each year. -/
def dip (w : Array Inst) (g : Int) (regs : Bool) (nm : String) : Sc :=
  { name := nm, world := w, days := #[150, 170, 190, 364, 729],
    px := #[k 80, k 82, k 85, k 120, k 150], expo := #[[1], [1], [1], [1], [1]], start := [held 5 (k 100)],
    gST := [g, g], gLT := [0, 0], regs := regs }

/-- Bought on day 100 at 60, worth 100 on 6 December of year 1 (held 240 days). The investor wants no exposure from
that day on. The plain plan sells. -/
def exit (w : Array Inst) (regs : Bool) (nm : String) : Sc :=
  { name := nm, world := w, days := #[340, 364, 385, 470, 729],
    px := #[k 100, k 100, k 104, k 108, k 120], expo := #[[0], [0], [0], [0], [0]], start := [held 100 (k 60)],
    gST := [0, 0], gLT := [0, 0], regs := regs }

/-- Nothing held. One unit of exposure wanted from day 5 (100) to day 300 (125), a dip to 80 on day 150, none after. -/
def shortHorizon (w : Array Inst) (g : Int) (regs : Bool) (nm : String) : Sc :=
  { name := nm, world := w, days := #[5, 150, 300, 364, 729],
    px := #[k 100, k 80, k 125, k 125, k 125], expo := #[[1], [1], [0], [0], [0]],
    gST := [g, g], gLT := [0, 0], regs := regs }

/-- Nothing held. One unit of exposure throughout; up 30 in year 1, down 25 in year 2. -/
def upDown (w : Array Inst) (regs : Bool) (nm : String) : Sc :=
  { name := nm, world := w, days := #[5, 364, 500, 729],
    px := #[k 100, k 130, k 120, k 105], expo := #[[1], [1], [1], [1]],
    gST := [0, 0], gLT := [0, 0], regs := regs }

/-- The fund and its futures contract only (no second fund). -/
def stockWorld2 : Array Inst := #[stockWorld[0]!, stockWorld[2]!]

/-- As `exit`, but the investor tolerates exposure of one unit between 20 January and 31 March of year 2
(the price is the same on both days, so the pre-tax result is unchanged after the fact). -/
def exitWindow (w : Array Inst) (regs : Bool) (nm : String) : Sc :=
  { exit w regs nm with px := #[k 100, k 100, k 104, k 104, k 120], expo := #[[0], [0], [0, 1], [0], [0]] }

/-- Nothing held and no exposure wanted at any date. Other short-term gain `g` in each year (and other long-term
gain `gl`). The price moves from 100 to `p1` during year 1 and stays there. -/
def flat (w : Array Inst) (p1 : Int) (g gl : Int) (regs : Bool) (nm : String) : Sc :=
  { name := nm, world := w, days := #[5, 364, 385, 729],
    px := #[k 100, k p1, k p1, k p1], expo := #[[0], [0], [0], [0]],
    gST := [g, g], gLT := [gl, gl], regs := regs }
#eval search (top := 300) (flat stockWorld 75 50000 0 true "stock: no exposure, market down 25, other ST gains 50k")
end Legal.USTax.Hunt.Instruments
