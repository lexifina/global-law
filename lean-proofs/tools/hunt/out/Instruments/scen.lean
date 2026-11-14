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

/-- Funds with distributions. FundA distributes nothing. GainFund is a regulated investment company that pays a
capital gain dividend of 10 on day 130 (date index 2). DivStock pays a dividend of 3 on day 130 that can be qualified
dividend income. All three have the same total return. -/
def distWorld : Array Inst := #[
  { name := "FundA", cls := 0, security := true, acq := true, afp := true, m2m := false },
  { name := "GainFund", cls := 1, security := true, acq := true, afp := true, m2m := false, dist := [(2, 10000, .cgd)] },
  { name := "DivStock", cls := 2, security := true, acq := true, afp := true, m2m := false, dist := [(2, 3000, .qdi)] }]

/-- FundA bought on day 5 at 100. Total return path flat at 100 until day 364, 105 at the end of year 2. One unit
of exposure throughout. Other short-term gain `g` and long-term gain `gl` each year. Dates: 100, 120, ex-date 130,
195 (65 days after 120), 310 (190 days after 120), year end, end. -/
def distScen (w : Array Inst) (g gl : Int) (nm : String) : Sc :=
  { name := nm, world := w, days := #[100, 120, 130, 195, 310, 364, 729],
    px := #[k 100, k 100, k 100, k 100, k 100, k 100, k 105], expo := #[[1], [1], [1], [1], [1], [1], [1]],
    start := [held 5 (k 100)], gST := [g, g], gLT := [gl, gl], maxTrades := 2, maxLots := 2 }

/-- As `distScen`, for a taxpayer with a $300,000 capital loss (short-term) in year 1 and $50,000 a year of interest
income, and no other gains. -/
def lieuScen (regs : Bool) (nm : String) : Sc :=
  { distScen distWorld 0 0 nm with gST := [-300000, 0], gOrd := [50000, 50000], regs := regs, maxLots := 3 }

/-- `distWorld` with the distributions on date index 1. -/
def distWorld1 : Array Inst := distWorld.map fun i => { i with dist := i.dist.map fun (_, a, kd) => (1, a, kd) }

/-- A taxpayer with a $300,000 short-term capital loss in year 1 and $50,000 a year of interest income, no other
gains; FundA held; one unit of exposure throughout; dates 120, ex-date 130, 195, year end, end. -/
def lieuScen1 (regs : Bool) (nm : String) : Sc :=
  { name := nm, world := distWorld1, days := #[120, 130, 195, 364, 729],
    px := #[k 100, k 100, k 100, k 100, k 105], expo := #[[1], [1], [1], [1], [1]],
    start := [held 5 (k 100)], gST := [-300000, 0], gLT := [0, 0], gOrd := [50000, 50000], regs := regs }

/-- FundA held. Dates: the day before GainFund goes ex, the ex-date, the day after, 33 days after the first date,
day 330, year end, end. -/
def exDate (g : Int) (nm : String) : Sc :=
  { name := nm, world := distWorld1, days := #[129, 130, 131, 162, 330, 364, 729],
    px := #[k 100, k 100, k 100, k 100, k 100, k 100, k 105], expo := #[[1], [1], [1], [1], [1], [1], [1]],
    start := [held 5 (k 100)], gST := [g, g], gLT := [0, 0], maxLots := 2 }

/-- `lieuScen1` with fewer dates. -/
def lieuScen2 (regs : Bool) (nm : String) : Sc :=
  { lieuScen1 regs nm with days := #[120, 130, 364, 729], px := #[k 100, k 100, k 100, k 105],
                           expo := #[[1], [1], [1], [1]] }

/-- `dip` without the day-190 date. -/
def dip3 (w : Array Inst) (g : Int) (regs : Bool) (nm : String) : Sc :=
  { dip w g regs nm with days := #[150, 170, 364, 729], px := #[k 80, k 82, k 120, k 150], expo := #[[1], [1], [1], [1]] }
