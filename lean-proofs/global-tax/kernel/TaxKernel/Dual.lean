import TaxKernel.Schedule

/-!
# TaxKernel.Dual: separate schedules for capital income

Nordic dual income tax (SE, NO, DK), the Netherlands' boxes, Japan's separate taxation (分離課税), flat final
withholding on interest and dividends (IT, ES's savings base, PT, KR's separate taxation below a threshold, …):
earned income and capital income are taxed by different schedules, each on its own base, and the capital base may
carry its own allowance. A negative capital base can give a credit against the earned-income tax at `deficitRate`
(SE: skattereduktion för underskott av kapital, 30 % up to SEK 100,000 and 21 % above).

    Dual.ticks d earned capital
      = earned schedule on earned
      + capital schedule on (capital − capitalAllowance)⁺
      − deficit credit on (−capital)⁺        (never more than the earned tax: non-refundable)

The two schedules are independent `Schedule`s, so every Schedule theorem applies to each side, and
`Theorems.Dual.ticks_mono_capital` / `ticks_mono_earned` hold. The interesting cross-country fact is the *wedge*:
`Dual.wedge d e c` = earned-schedule rate at `e` − capital rate at `c`, the gain per unit from relabelling earnings
as capital (the owner-manager search measures it on the exes).
-/

namespace TaxKernel

structure Dual where
  earned : Schedule
  capital : Schedule
  capitalAllowance : Int := 0
  /-- credit for a capital deficit: schedule on the deficit (e.g. 30 % then 21 %), limited to the earned tax -/
  deficit : Schedule := Schedule.flat 0
  deriving Repr, Inhabited

namespace Dual

def earnedTicks (d : Dual) (e : Int) : Int := d.earned.ticks e
def capitalTicks (d : Dual) (c : Int) : Int := d.capital.ticks (pos (c - d.capitalAllowance))
def deficitTicks (d : Dual) (e c : Int) : Int := min (pos (d.earnedTicks e)) (d.deficit.ticks (pos (-c)))

def ticks (d : Dual) (e c : Int) : Int := d.earnedTicks e + d.capitalTicks c - d.deficitTicks e c

/-- Marginal rate on earned income minus marginal rate on capital income: per-unit gain from relabelling. -/
def wedge (d : Dual) (e c : Int) : Int := d.earned.rate e - d.capital.rate (pos (c - d.capitalAllowance))

end Dual
end TaxKernel
