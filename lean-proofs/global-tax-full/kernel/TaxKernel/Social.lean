import TaxKernel.Schedule

/-!
# TaxKernel.Social: employee social contributions with floors, ceilings and caps

    Contribution.ticks c earnings
      = 0                                      if earnings < floor   (all-or-nothing entry threshold)
      = c.sched.ticks (min earnings ceiling)   otherwise             (ceiling < 0: none)

`sched` carries the rates by earnings band, so the UK's Class 1 primary contributions (8 % between the primary
threshold and the upper earnings limit, 2 % above) are `Schedule.ofList [(0,0),(12570,800),(50270,200)]` with no
ceiling, and Germany's pension contribution (9.3 % up to the Beitragsbemessungsgrenze) is
`{ sched := Schedule.flat 930, ceiling := 96600 }`. A floor below which nothing is due and above which the whole
earnings are charged is a **notch** (`Theorems.Social.floor_notch`): the scanners report it.

`Contribution.amount` rounds by `round`; `total` sums a list of contributions (pension, health, unemployment, …).
-/

namespace TaxKernel

structure Contribution where
  name : String := ""
  sched : Schedule
  /-- earnings below this: nothing at all -/
  floor : Int := 0
  /-- earnings above this are not counted (−1: no ceiling) -/
  ceiling : Int := -1
  round : Rule := {}
  deriving Repr, Inhabited

namespace Contribution

def base (c : Contribution) (earn : Int) : Int := if c.ceiling < 0 then earn else min earn c.ceiling

def ticks (c : Contribution) (earn : Int) : Int :=
  if earn < c.floor then 0 else c.sched.ticks (c.base earn)

def amount (c : Contribution) (earn : Int) : Int := c.round.ofTicks (c.ticks earn)

/-- A flat rate up to a ceiling (most continental contributions). -/
def flatCapped (name : String) (rate ceiling : Int) : Contribution :=
  { name, sched := Schedule.flat rate, ceiling }

end Contribution

/-- Sum of the contributions in units. -/
def contributionsTotal (cs : List Contribution) (earn : Int) : Int :=
  cs.foldl (fun a c => a + c.amount earn) 0

/-- Named lines for the output's `detail`. -/
def contributionsDetail (cs : List Contribution) (earn : Int) : List (String × Int) :=
  cs.map fun c => (c.name, c.amount earn)

end TaxKernel
