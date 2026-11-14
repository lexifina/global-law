-- T5: free lunch, unmodified rules (all knobs default).
/-- Everything the tax computation sees (gain, loss, dividends, less investment interest) net of the given gains,
plus losses still deferred at the end. -/
def recognized (sc : Sc) (s : St) : Int :=
  let f := yearFigures sc s
  let tot := f.foldl (fun a (st, lt, m, od, qd, inv, _) => a + st + lt + m + od + qd - inv) (0 : Int)
  let given := (sc.gST.foldl (· + ·) 0) + (sc.gLT.foldl (· + ·) 0)
  let deferred := s.pls.foldl (fun a q => if q.final || q.offs.isEmpty then a else a + q.amt) (0 : Int)
  tot - given + deferred

/-- Over every final position (everything sold): recognized income minus the pre-tax result `econ`.
Negative = income that vanished or a loss counted twice (free lunch); positive = a loss the rules destroyed. -/
def conserve (sc : Sc) (econ : Int) : IO Unit := do
  let (visited, frontier) := explore sc false
  let mut lo : Int := 0
  let mut hi : Int := 0
  let mut nlo := 0
  let mut nhi := 0
  let mut n := 0
  let mut minTax : Option Int := none
  let mut loPath : Path := []
  let mut maxLT : Int := 0
  let mut minST : Int := 0
  for (s, path) in frontier do
    let s' := liquidate sc s
    let gap := recognized sc s' - econ
    n := n + 1
    if gap < 0 then nlo := nlo + 1
    if gap > 0 then nhi := nhi + 1
    if gap < lo then lo := gap; loPath := path
    if gap > hi then hi := gap
    let tx := bestTax sc s'
    if minTax.all (tx < ·) then minTax := some tx
    let f := yearFigures sc s'
    let lt := f.foldl (fun a x => a + x.2.1) (0 : Int) - sc.gLT.foldl (· + ·) 0
    let st := f.foldl (fun a x => a + x.1) (0 : Int) - sc.gST.foldl (· + ·) 0
    if lt > maxLT then maxLT := lt
    if st < minST then minST := st
  IO.println s!"{sc.name}: positions {visited}, finals {n}; recognized − economic: min {lo} ({nlo} finals below 0), max {hi} ({nhi} above 0); lowest tax ${minTax}; largest net LT {maxLT}, lowest net ST {minST}"
  for (_, txt) in loPath.reverse do IO.println s!"     {txt}"

#eval conserve (exDate 50000 "T5 C2 g=50k") 5000
#eval conserve (exDate 0 "T5 C2 g=0") 5000
#eval conserve (distScen distWorld 50000 0 "T5 C1 g=50k") 5000
#eval conserve (distScen distWorld 0 0 "T5 C1 g=0") 5000
-- absurd goal: no dividend in the world, flat year 1: can any plan get below the tax on the only income there is?
#eval conserve { exDate 0 "T5 no distributions, g=0" with world := distWorld1.map fun i => { i with dist := [] } } 5000
-- floor: with no other income the best possible is two years of the §1211(b) $3,000 at 37%: −(1110·1.04 + 1110) = −2264
