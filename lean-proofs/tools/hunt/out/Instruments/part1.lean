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
  deriving Repr, BEq, Hashable

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
  expo : Array Int       -- net units of exposure the investor must hold on leaving each date
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
               { x with basis := x.basis - amt, hp := if x.noHP then x.hp else x.hp - held } else x }
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
               { x with basis := x.basis + amt } else x }
  | none =>
    -- §1092(a)(1): held for the year-end test against unrecognized gain in the offsetting positions
    let offLots := s.lots.filter fun x => x.long != closed.long && !((sc.world[x.inst]!).m2m && I.m2m)
    -- Temp. Reg. §1.1092(b)-2T(b)(2): loss on the non-1256 leg of a mixed straddle is 60/40
    let ch' := if sc.regs && !I.m2m && offLots.any (fun x => (sc.world[x.inst]!).m2m) then Ch.split else ch
    { s with pls := { inst := closed.inst, opened := closed.opened, cls := I.cls, day := t, amt := amt, ch := ch',
                      held := held, year := yearOf t, offs := offLots.map (fun x => (x.inst, x.opened)),
                      washA := I.security && !isShort, washE := I.security && isShort, final := false } :: s.pls }

/-- Bookkeeping after `closed` leaves the position at day `t`. -/
def afterClose (sc : Sc) (s : St) (closed : Lot) (t : Nat) : St :=
  let C := sc.world[closed.inst]!
  { s with lots := s.lots.map fun x =>
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
      then { x with noHP := false, hp := t } else x }

/-- Buy one unit of `j` at today's price. -/
def openLong (sc : Sc) (s : St) (j : Nat) : St :=
  let t := sc.days[s.di]!
  let p := sc.px[s.di]!
  let J := sc.world[j]!
  -- §1259(c)(3)(A)(iii): a position being watched after a closed transaction has its risk reduced again
  let s := s.lots.foldl (fun s x =>
    if !x.long && (sc.world[x.inst]!).cls == J.cls && x.cs.isSome && x.csClosed.isSome then
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
  -- §1091(a): acquired within the 30 days after a sale at a loss
  let pend := if J.acq then s.pls.find? fun q => q.washA && q.cls == J.cls && q.day + 30 ≥ t else none
  match pend with
  | some q =>
    let same := fun (r : PL) => r.inst == q.inst && r.opened == q.opened && r.day == q.day
    let tot := (s.pls.filter same).foldl (fun a r => a + r.amt) 0
    let lot := { lot with basis := p - tot, hp := if noHP then lot.hp else lot.hp - q.held }
    { s with pls := s.pls.filter (fun r => !same r), lots := s.lots ++ [lot] }
  | none =>
    { s with lots := s.lots ++ [lot], buys := if J.acq then (j, J.cls, t) :: s.buys else s.buys }

/-- Sell one unit of `j` short at today's price. -/
def openShort (sc : Sc) (s : St) (j : Nat) : St :=
  let t := sc.days[s.di]!
  let p := sc.px[s.di]!
  let J := sc.world[j]!
  let s := s.lots.foldl (fun s x =>
    if x.long && (sc.world[x.inst]!).cls == J.cls && x.cs.isSome && x.csClosed.isSome then
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
  -- §1091(e)(2): another short sale within the 30 days after closing a short at a loss
  let pend := if J.security then s.pls.find? fun q => q.washE && q.cls == J.cls && q.day + 30 ≥ t else none
  match pend with
  | some q =>
    let same := fun (r : PL) => r.inst == q.inst && r.opened == q.opened && r.day == q.day
    let tot := (s.pls.filter same).foldl (fun a r => a + r.amt) 0
    { s with pls := s.pls.filter (fun r => !same r), lots := s.lots ++ [{ lot with basis := p + tot }] }
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
    else (if k.ltLoss || heldLT then Ch.lt else Ch.st)                      -- §1233(d)
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

