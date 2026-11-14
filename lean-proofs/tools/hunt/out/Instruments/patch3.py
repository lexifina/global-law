p='core.lean'
s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n, (s.count(a),a)
    s=s.replace(a,b)
rep("""  hedge : List (Nat × Nat) := []       -- periods in which risk of loss was diminished, §246(c)(4)
""","""  hedge : List (Nat × Nat) := []       -- periods in which risk of loss was diminished, §246(c)(4)
  hedgeSI : List (Nat × Nat) := []     -- periods in which substantially identical property was held, §263(h)(4)(A)
""")
rep("""  qd : Int := 0        -- qualified dividend income, §1(h)(11)
""","""  qd : Int := 0        -- qualified dividend income, §1(h)(11)
  inv : Int := 0       -- investment interest paid, §163(d)(3) (payments in lieu of dividends on short sales, (d)(3)(C))
""")
rep("""  gLT : List Int         -- other long-term gain of each year
""","""  gLT : List Int         -- other long-term gain of each year
  gOrd : List Int := []  -- other ordinary investment income of each year (interest), §163(d)(4)(B)(i)
""")
# payments in lieu when a short is closed
rep("""/-- A loss on a share on which dividends were received, split into parts by character.""","""/-- §263(h): a payment in lieu of a dividend on stock sold short is not deductible if the short sale is closed on or
before the 45th day after it was made (1 year for an extraordinary dividend, §1059(c) applied to the amount realized
in the short sale); it is added to the basis of the stock used to close. The period is suspended while the taxpayer
holds substantially identical stock ((h)(4)(A)) or, under regulations, has diminished risk through substantially
similar or related property ((h)(4)(B); applied only when `regs`). Otherwise the payment is investment interest
(§163(d)(3)(C)). Returns the state and the amount added to basis. -/
def settleLieu (sc : Sc) (s : St) (k : Lot) (t : Nat) : St × Int :=
  k.divs.foldl (fun (s, add) (ex, a, _) =>
    let susp := (if sc.regs then k.hedge else k.hedgeSI).foldl (fun acc (x, y) => acc + ((y : Int) - x)) 0
    let run := (t : Int) - k.opened - susp
    let need : Int := if a * 10 ≥ k.basis then 365 else 45
    if run ≤ need then (s, add + a)
    else ({ s with yrs := modAt s.yrs (yearOf ex) fun y => { y with inv := y.inv + a } }, add)) (s, 0)

/-- A loss on a share on which dividends were received, split into parts by character.""")
rep("""  let (s, k) := csGain s k
  let s := dropLot s k
  let (s, cost, heldLT, dl) := match deliv with""","""  let (s, k) := csGain s k
  let s := dropLot s k
  let (s, lieu) := settleLieu sc s k t
  let (s, cost, heldLT, dl) := match deliv with""")
rep("""  let amt := k.basis - cost
  let ch := if K.m2m then Ch.m""","""  let amt := k.basis - cost - lieu
  let ch := if K.m2m then Ch.m""")
# advance: shorts receive the record too; related payments deny QDI
rep("""  let hedged := fun (x : Lot) => s.lots.any fun n => n.long != x.long
  let lots2 : List Lot := s.lots.map (fun (x : Lot) =>
    let x := if hedged x then { x with hedge := x.hedge ++ [(t, t')] } else x
    if x.long then
      { x with divs := x.divs ++ ((sc.world[x.inst]!).dist.filter (fun d => d.1 == s.di + 1)).map (fun d => (t', d.2.1, d.2.2)) }
    else x)""","""  let hedged := fun (x : Lot) => s.lots.any fun n => n.long != x.long
  let hedgedSI := fun (x : Lot) => s.lots.any fun n => n.long != x.long && (sc.world[n.inst]!).cls == (sc.world[x.inst]!).cls
  let goesEx := fun (i : Nat) => (sc.world[i]!).dist.filter (fun d => d.1 == s.di + 1)
  -- §1(h)(11)(B)(iii)(II): not qualified to the extent the taxpayer must make related payments on positions in
  -- substantially similar or related property (here: any short position paying in lieu on the same date)
  let pays := s.lots.any fun n => !n.long && !(goesEx n.inst).isEmpty
  let lots2 : List Lot := s.lots.map (fun (x : Lot) =>
    let x := if hedged x then { x with hedge := x.hedge ++ [(t, t')] } else x
    let x := if hedgedSI x then { x with hedgeSI := x.hedgeSI ++ [(t, t')] } else x
    { x with divs := x.divs ++ (goesEx x.inst).map (fun d =>
        (t', d.2.1, if x.long && pays && d.2.2 == DK.qdi then DK.ord else d.2.2)) })""")
rep("""      let shortOverEx := s.lots.any fun x => !x.long && (sc.world[x.inst]!).dist.any fun d => d.1 == i + 1
      if (sc.expo[i]!).contains (exposure s) && !shortOverEx then""","""      if (sc.expo[i]!).contains (exposure s) then""")
# tax
rep("def taxFV (yrs : List (Int × Int × Int × Int × Int)) (elect : Nat → Bool) : Int := Id.run do","def taxFV (yrs : List (Int × Int × Int × Int × Int × Int × Int)) (elect : Nat → Bool) : Int := Id.run do")
rep("    let (s0, l0, m, od, qd) := yrs[y]!","    let (s0, l0, m, od, qd, inv, gOrd) := yrs[y]!")
rep("""    -- dividends: ordinary rates, or §1(h)(11) rates for qualified dividend income; §1411 on both
    cash := cash.push (txy + od * (ordR + niitR) + qd * (ltR + niitR))""","""    -- §163(d)(1), (4): investment interest is allowed up to net investment income: ordinary investment income plus
    -- net gain in excess of net capital gain (the net short-term gain); the rest carries forward, (d)(2).
    -- (d)(4)(B)(iii) election: in the last year only, long-term gain and qualified dividends are elected in
    -- (and lose their rate, §1(h)(2), (11)(D)(i)) as far as the remaining interest needs.
    let S1 := S - sCF
    let L1 := L - lCF
    let netST : Int := if S1 > 0 then (if L1 < 0 then max 0 (S1 + L1) else S1) else 0
    let ncg : Int := if L1 > 0 then (if S1 < 0 then max 0 (S1 + L1) else L1) else 0
    let due := inv + invCF
    let ded := min due (od + gOrd + netST)
    let el := if y + 1 == n then min (due - ded) (ncg + qd) else 0
    invCF := due - ded - el
    -- dividends: ordinary rates, or §1(h)(11) rates for qualified dividend income; §1411 on both
    cash := cash.push (txy + od * (ordR + niitR) + qd * (ltR + niitR) - ded * (ordR + niitR) - el * (ltR + niitR))""")
rep("""  let mut sCF : Int := 0
  let mut lCF : Int := 0
  for y in [0:n] do""","""  let mut sCF : Int := 0
  let mut lCF : Int := 0
  let mut invCF : Int := 0
  for y in [0:n] do""")
rep("def yearFigures (sc : Sc) (s : St) : List (Int × Int × Int × Int × Int) :=","def yearFigures (sc : Sc) (s : St) : List (Int × Int × Int × Int × Int × Int × Int) :=")
rep("  yrs.mapIdx fun i y => (y.st + (sc.gST.getD i 0), y.lt + (sc.gLT.getD i 0), y.m, y.ord, y.qd)","  yrs.mapIdx fun i y => (y.st + (sc.gST.getD i 0), y.lt + (sc.gLT.getD i 0), y.m, y.ord, y.qd, y.inv, sc.gOrd.getD i 0)")
# hold-out: shorts kept
rep("""  s.lots.foldl (fun s x => settleDivs s x (t + 200)) s""","""  s.lots.foldl (fun s x => if x.long then settleDivs s x (t + 200) else (settleLieu sc s x (t + 400)).1) s""")
# replay of a fixed plan
rep("""def search (sc : Sc) (top : Nat := 8) : IO Unit := do""","""/-- Tax (everything sold at the end) of one fixed plan: for each date, the kinds of trade to make, in order. -/
def replay (sc : Sc) (plan : List (List String)) : Option Int := Id.run do
  let mut s := init sc
  for i in [0:sc.days.size - 1] do
    for kd in plan.getD i [] do
      match (expand sc false s).find? (fun x => x.1.1 == kd) with
      | some x => s := x.2
      | none => return none
    if !(sc.expo[i]!).contains (exposure s) then return none
    s := advance sc s
  return some (bestTax sc (liquidate sc s))

def check (sc : Sc) (title : String) (plan : List (List String)) : IO Unit :=
  IO.println s!"{sc.name}: {title}: tax ${replay sc plan}"

def search (sc : Sc) (top : Nat := 8) : IO Unit := do""")
open(p,'w',encoding='utf-8',newline='\n').write(s)
print("ok")
