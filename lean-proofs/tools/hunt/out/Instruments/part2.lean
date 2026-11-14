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

def expand (sc : Sc) (s : St) : List ((String × String) × St) :=
  let t := sc.days[s.di]!
  let room := s.lots.length < sc.maxLots
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

def search (sc : Sc) (top : Nat := 8) : IO Unit := do
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
        for (lab, s') in expand sc s do
          if !all.contains s' then
            all := all.insert s' (lab :: path)
            nxt := nxt.insert s' (lab :: path)
      layer := nxt
    let mut nf : Std.HashMap St Path := {}
    for (s, path) in all do
      if exposure s == sc.expo[i]! then
        let s' := advance sc s
        if !nf.contains s' then nf := nf.insert s' path
    visited := visited + all.size
    frontier := nf
  -- valuation
  let w0 := iname sc 0
  let plain : List String := [s!"buy {w0}", s!"sell {w0}"]
  let mut base : Option (Nat × Int × Int) := none
  let mut famL : Std.HashMap (List String) (Int × Int × Int × Path) := {}
  let mut famH : Std.HashMap (List String) (Int × Int × Int × Path) := {}
  for (s, path) in frontier do
    let tl := bestTax sc (liquidate sc s)
    let sh := holdOut sc s
    let th := bestTax sc sh
    let u := unrealized sc sh
    let f := family path
    if f.all plain.contains then
      if base.all (fun b => path.length < b.1) then base := some (path.length, tl, th)
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

/-- Buy in January of year 1 at 100; dip to 80 in June; 120 at year end; 150 at the end of year 2. -/
def dip (w : Array Inst) (g : Int) (regs : Bool) (nm : String) : Sc :=
  { name := nm, world := w, days := #[5, 150, 170, 190, 364, 500, 729],
    px := #[k 100, k 80, k 82, k 85, k 120, k 110, k 150], expo := #[1, 1, 1, 1, 1, 1, 1],
    gST := [g, g], gLT := [0, 0], regs := regs }

#eval search (dip stockWorld 0 true "stock, dip and recovery, no other gains")

end Legal.USTax.Hunt.Instruments
