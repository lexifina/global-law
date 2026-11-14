p='core.lean'
s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n, (s.count(a),a)
    s=s.replace(a,b)
# --- types
rep("""structure Inst where
  name : String""","""/-- Kinds of distribution: a dividend that can be qualified dividend income (§1(h)(11)(B)); a capital gain dividend
of a regulated investment company (§852(b)(3)(C)); an exempt-interest dividend (§852(b)(5)); any other dividend. -/
inductive DK where
  | qdi | cgd | exempt | ord
  deriving Repr, BEq, Hashable, Inhabited

structure Inst where
  name : String""")
rep("""  m2m : Bool         -- section 1256 contract (§1256(b))
""","""  m2m : Bool         -- section 1256 contract (§1256(b))
  dist : List (Nat × Int × DK) := []   -- (index of the date on which it goes ex, amount per unit, kind)
""")
rep("""  csClosed : Option Nat := none        -- §1259(c)(3): the day that transaction was closed
""","""  csClosed : Option Nat := none        -- §1259(c)(3): the day that transaction was closed
  divs : List (Nat × Int × DK) := []   -- distributions received on this position: (ex day, amount, kind)
  hedge : List (Nat × Nat) := []       -- periods in which risk of loss was diminished, §246(c)(4)
""")
rep("""  m : Int := 0         -- net gain or loss from section 1256 contracts
""","""  m : Int := 0         -- net gain or loss from section 1256 contracts
  ord : Int := 0       -- dividends taxed at ordinary rates
  qd : Int := 0        -- qualified dividend income, §1(h)(11)
""")
# --- price
rep("""def yearOf (d : Nat) : Nat := d / 365""","""/-- Price of instrument `i` at date index `di`: the common total-return path less what it has distributed. -/
def pxOf (sc : Sc) (i di : Nat) : Int :=
  (sc.world[i]!).dist.foldl (fun p (ix, a, _) => if ix ≤ di then p - a else p) (sc.px[di]!)

/-- Days in `[a, b]` during which the position's risk of loss was diminished. -/
def hedgedIn (l : Lot) (a b : Int) : Int :=
  l.hedge.foldl (fun acc (x, y) => acc + max 0 (min b (y : Int) - max a (x : Int))) 0

/-- §246(c)(3), (4): days held, the day of disposition but not of acquisition counted, §1223(3) not applied,
reduced for periods of diminished risk. -/
def heldAtRisk (l : Lot) (t : Nat) : Int := (t : Int) - l.opened - hedgedIn l l.opened t

/-- §1(h)(11)(B)(iii)(I) with §246(c)(1)(A): held more than 60 days during the 121-day period beginning 60 days
before the ex-dividend date. `t` is the day of disposition. -/
def qdiMet (l : Lot) (ex t : Nat) : Bool :=
  let a := max (l.opened : Int) ((ex : Int) - 60)
  let b := min (t : Int) ((ex : Int) + 60)
  b - a - hedgedIn l a b > 60

def yearOf (d : Nat) : Nat := d / 365""")
rep("""def book (s : St) (y : Nat) (amt : Int) (ch : Ch) : St := { s with yrs := modAt s.yrs y (addYr · amt ch) }""",
"""def book (s : St) (y : Nat) (amt : Int) (ch : Ch) : St := { s with yrs := modAt s.yrs y (addYr · amt ch) }

/-- The dividends received on a position are classified when it is disposed of on day `t`. -/
def settleDivs (s : St) (l : Lot) (t : Nat) : St :=
  l.divs.foldl (fun s (ex, a, kd) =>
    match kd with
    | .qdi => if qdiMet l ex t then { s with yrs := modAt s.yrs (yearOf ex) fun y => { y with qd := y.qd + a } }
              else { s with yrs := modAt s.yrs (yearOf ex) fun y => { y with ord := y.ord + a } }
    | .ord => { s with yrs := modAt s.yrs (yearOf ex) fun y => { y with ord := y.ord + a } }
    | .cgd => book s (yearOf ex) a .lt        -- §852(b)(3)(B)
    | .exempt => s) s                          -- §852(b)(5)(B), §103(a)

/-- A loss on a share on which dividends were received, split into parts by character.
§852(b)(4)(B): held 6 months or less, disallowed to the extent of exempt-interest dividends.
§852(b)(4)(A): held 6 months or less, long-term to the extent of capital gain dividends.
§1(h)(11)(D)(ii): long-term to the extent of extraordinary dividends (§1059(c)(1), (2)(B): 10% of basis) that were
qualified dividend income. Returns the parts (negative amounts). -/
def lossParts (l : Lot) (t : Nat) (amt : Int) (ch : Ch) : List (Int × Ch) :=
  let short6 := heldAtRisk l t ≤ 183
  let sumK := fun (f : Nat × Int × DK → Bool) => (l.divs.filter f).foldl (fun a d => a + d.2.1) (0 : Int)
  let ex := if short6 then sumK (fun d => d.2.2 == DK.exempt) else 0
  let loss := -amt
  let dis := min loss ex
  let loss := loss - dis
  let cg := if short6 then sumK (fun d => d.2.2 == DK.cgd) else 0
  let xd := sumK (fun d => d.2.2 == DK.qdi && d.2.1 * 10 ≥ l.basis && qdiMet l d.1 t)
  let ltPart := if ch == Ch.st then min loss (cg + xd) else 0
  (if ltPart > 0 then [(-ltPart, Ch.lt)] else []) ++ (if loss - ltPart > 0 then [(-(loss - ltPart), ch)] else [])""")
# --- lossEvent takes parts
rep("""def lossEvent (sc : Sc) (s : St) (closed : Lot) (t : Nat) (amt : Int) (ch : Ch) (held : Int) (isShort : Bool) : St :=
  let I := sc.world[closed.inst]!""","""def lossEvent (sc : Sc) (s : St) (closed : Lot) (t : Nat) (amt0 : Int) (ch : Ch) (held : Int) (isShort : Bool) : St :=
  let I := sc.world[closed.inst]!
  let parts := if isShort then [(amt0, ch)] else lossParts closed t amt0 ch
  let amt := parts.foldl (fun a q => a + q.1) 0
  if amt == 0 then s else""")
rep("""    let ch' := ch
    { s with pls := { inst := closed.inst, opened := closed.opened, cls := I.cls, day := t, amt := amt, ch := ch',
                      held := held, year := yearOf t, offs := offLots.map (fun x => (x.inst, x.opened)),
                      washA := I.security && !isShort, washE := I.security && isShort, final := false } :: s.pls }""",
"""    { s with pls := (parts.map fun (a, c) =>
                    ({ inst := closed.inst, opened := closed.opened, cls := I.cls, day := t, amt := a, ch := c,
                       held := held, year := yearOf t, offs := offLots.map (fun x => (x.inst, x.opened)),
                       washA := I.security && !isShort, washE := I.security && isShort, final := false } : PL)) ++ s.pls }""")
# --- prices in trades
rep("""  let p := sc.px[s.di]!
  let J := sc.world[j]!
  -- §1259(c)(3)(A)(iii) with §246(c)(4)(C)""","""  let p := pxOf sc j s.di
  let J := sc.world[j]!
  -- §1259(c)(3)(A)(iii) with §246(c)(4)(C)""")
rep("""  let p := sc.px[s.di]!
  let J := sc.world[j]!
  let s := s.lots.foldl""","""  let p := pxOf sc j s.di
  let J := sc.world[j]!
  let s := s.lots.foldl""")
rep("""  let p := sc.px[s.di]!
  let K := sc.world[k.inst]!
  let (s, k) := csGain s k          -- §1259(e)(1): the position deemed sold is now disposed of
  let s := dropLot s k""","""  let p := pxOf sc k.inst s.di
  let K := sc.world[k.inst]!
  let (s, k) := csGain s k          -- §1259(e)(1): the position deemed sold is now disposed of
  let s := settleDivs (dropLot s k) k t""")
rep("""  let p := sc.px[s.di]!
  let K := sc.world[k.inst]!
  let (s, k) := csGain s k
  let s := dropLot s k
  let (s, cost, heldLT, dl) := match deliv with
    | none => (s, p, false, none)
    | some l =>
      let (s, l) := csGain s l
      (dropLot s l, l.basis,""","""  let p := pxOf sc k.inst s.di
  let K := sc.world[k.inst]!
  let (s, k) := csGain s k
  let s := dropLot s k
  let (s, cost, heldLT, dl) := match deliv with
    | none => (s, p, false, none)
    | some l =>
      let (s, l) := csGain s l
      (settleDivs (dropLot s l) l t, l.basis,""")
# --- year end
rep("def yearEndProc (sc : Sc) (s : St) (y : Nat) (p : Int) : St :=","def yearEndProc (sc : Sc) (s : St) (y : Nat) : St :=")
rep("""    if (sc.world[x.inst]!).m2m then
      let amt := if x.long then p - x.basis else x.basis - p""","""    if (sc.world[x.inst]!).m2m then
      let p := pxOf sc x.inst s.di
      let amt := if x.long then p - x.basis else x.basis - p""")
rep("""          if q.offs.contains (x.inst, x.opened) then
            a + max 0 (if x.long then p - x.basis else x.basis - p) else a) (0 : Int)""","""          if q.offs.contains (x.inst, x.opened) then
            let p := pxOf sc x.inst s.di
            a + max 0 (if x.long then p - x.basis else x.basis - p) else a) (0 : Int)""")
rep("yearEndProc sc s (yearOf t) (sc.px[s.di]!)","yearEndProc sc s (yearOf t)",3)
rep("""  let p := sc.px[s.di]!
  s.lots.foldl (fun a x => a + (if x.long then p - x.basis else x.basis - p)) 0""","""  s.lots.foldl (fun a x => let p := pxOf sc x.inst s.di; a + (if x.long then p - x.basis else x.basis - p)) 0""")
# --- advance: distributions and hedge log
rep("""  { s with di := s.di + 1
           buys :=""","""  -- distributions to the holders on the ex-dividend date, and the §246(c)(4) record
  let hedged := fun (x : Lot) => s.lots.any fun n => n.long != x.long
  let lots2 : List Lot := s.lots.map (fun (x : Lot) =>
    let x := if hedged x then { x with hedge := x.hedge ++ [(t, t')] } else x
    if x.long then
      { x with divs := x.divs ++ ((sc.world[x.inst]!).dist.filter (fun d => d.1 == s.di + 1)).map (fun d => (t', d.2.1, d.2.2)) }
    else x)
  let s : St := { s with lots := lots2 }
  { s with di := s.di + 1
           buys :=""")
# --- tax: ord and qd
rep("def taxFV (yrs : List (Int × Int × Int)) (elect : Nat → Bool) : Int := Id.run do","def taxFV (yrs : List (Int × Int × Int × Int × Int)) (elect : Nat → Bool) : Int := Id.run do")
rep("    let (s0, l0, m) := yrs[y]!","    let (s0, l0, m, od, qd) := yrs[y]!")
rep("    cash := cash.push txy","    -- dividends: ordinary rates, or §1(h)(11) rates for qualified dividend income; §1411 on both\n    cash := cash.push (txy + od * (ordR + niitR) + qd * (ltR + niitR))")
rep("def yearFigures (sc : Sc) (s : St) : List (Int × Int × Int) :=","def yearFigures (sc : Sc) (s : St) : List (Int × Int × Int × Int × Int) :=")
rep("  yrs.mapIdx fun i y => (y.st + (sc.gST.getD i 0), y.lt + (sc.gLT.getD i 0), y.m)","  yrs.mapIdx fun i y => (y.st + (sc.gST.getD i 0), y.lt + (sc.gLT.getD i 0), y.m, y.ord, y.qd)")
# --- holdOut settles dividends for kept lots
rep("""  s.lots.foldl (fun s x => match x.cs, x.csClosed with
    | some _, none => (csGain s x).1
    | _, _ => s) s""","""  let s := s.lots.foldl (fun s x => match x.cs, x.csClosed with
    | some _, none => (csGain s x).1
    | _, _ => s) s
  -- dividends on positions still held: the holding-period windows are assumed to run out unhedged
  s.lots.foldl (fun s x => settleDivs s x (t + 200)) s""")
# --- no short position over an ex-dividend date (payments in lieu, §263(h), are not modelled)
rep("""      if (sc.expo[i]!).contains (exposure s) then""","""      let shortOverEx := s.lots.any fun x => !x.long && (sc.world[x.inst]!).dist.any fun d => d.1 == i + 1
      if (sc.expo[i]!).contains (exposure s) && !shortOverEx then""")
open(p,'w',encoding='utf-8',newline='\n').write(s)
print("ok")
