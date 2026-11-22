import TaxKernel.Schedule
import TaxKernel.Credit

/-!
# TaxKernel.Multiplier (added in 1.2 for the 38): multipliers on a base tax, tax at an average rate, credit allocation

**Multipliers.** Several systems compute one "simple" tax from a tariff and then levy it several times at rates
set by different authorities: Switzerland's cantonal and municipal taxes (StG ZH § 2: "einfache Staatssteuer" ×
Steuerfuss of the canton and of the Gemeinde, e.g. 98 % and 119 %), Belgium's additional municipal tax (CIR 92
art. 465-466: a % of the state tax), Luxembourg's employment-fund surcharge (a % of the tax). A `Multiplier` is a
named rate in basis points **of the base tax** (9800 = 98 %); rates above 100 % are allowed.

    def kanton : Multiplier := { name := "cantonZH", rate := 9800 }
    def stadt  : Multiplier := { name := "cityZurich", rate := 11900 }
    applyMultipliers [kanton, stadt] einfacheSteuer    -- [("cantonZH", …), ("cityZurich", …)]

(`Surcharge.flatPct` is the same thing for one rate with no name; use either.)

**Tax at an average rate.** `atAverageRate m f rateIncome taxable` charges `taxable` at the average rate the tariff
`f` reaches on `rateIncome`: `f rateIncome × taxable / rateIncome`. One part, three statutes:
* the *progression clause* (Progressionsvorbehalt: DE EStG § 32b, AT EStG § 3 (3), LU LIR art. 134, BE "exonération
  sous réserve de progressivité", CH DBG Art. 7 (1) for income abroad): exempt income raises the rate, not the base;
* *rate splitting with a divisor* (Swiss cantons' Teilsplitting, e.g. a married couple's rate taken at income / 1.9):
  `rateSplitting m f divisorBp x` (divisor in bp: 19000 = 1.9; 20000 = full splitting);
* *rate-determining income* in general (Swiss "satzbestimmendes Einkommen" for part-year or partly taxable units).
`averageRateScaled f x scale` is the rate itself to `scale` (10000 = bp; 1000000 = a % to 4 decimals), for statutes
that round the rate before applying it (then `taxable * rate / scale`).

**Credit allocation.** A credit set against several taxes: in a fixed order (`allocateOrdered`: IS persónuafsláttur
against the state tax and then the municipal tax; NO/SE credits) or in proportion to them (`allocateProportional`:
FI TVL 143 §, a deduction from tax split over state, municipal, church and health-insurance tax in proportion).
Both return the amount used against each tax (same order); what is not used is lost unless the statute says so.

Theorems (`TaxKernel.Theorems.Parts38`): `Multiplier.amount_mono`, `atAverageRate_self` (rate income = taxable
gives the tariff), `rateSplitting_two` (divisor 2 on an even income = splitting), `allocateOrdered_total_le`
(never more than the credit), `allocateOrdered_each_le` (never more than each tax).
-/

namespace TaxKernel

structure Multiplier where
  name : String
  /-- bp of the base tax (Steuerfuss 98 % = 9800) -/
  rate : Int
  /-- rounding of the result -/
  round : Rule := {}
  deriving Repr, DecidableEq, Inhabited

namespace Multiplier
def ticks (m : Multiplier) (base : Int) : Int := m.rate * base
def amount (m : Multiplier) (base : Int) : Int := m.round.ofTicks (m.ticks base)
end Multiplier

/-- Every multiplier applied to the same base tax, with its name. -/
def applyMultipliers (ms : List Multiplier) (base : Int) : List (String × Int) :=
  ms.map fun m => (m.name, m.amount base)

/-- The total of the multiplied taxes. -/
def multipliedTotal (ms : List Multiplier) (base : Int) : Int := sumInts (ms.map fun m => m.amount base)

/-- `taxable` charged at the average rate of `f` at `rateIncome` (0 when `rateIncome ≤ 0`), rounded by `m`. -/
def atAverageRate (m : Round) (f : Int → Int) (rateIncome taxable : Int) : Int :=
  if rateIncome ≤ 0 then 0 else divR m (f rateIncome * taxable) rateIncome

/-- The average rate of `f` at `x`, as an integer over `scale` (rounded down; 0 when `x ≤ 0`). -/
def averageRateScaled (f : Int → Int) (x scale : Int) : Int :=
  if x ≤ 0 then 0 else f x * scale / x

/-- Rate splitting with a divisor (bp): the rate is `f`'s average rate at `x / divisor`, applied to all of `x`. -/
def rateSplitting (m : Round) (f : Int → Int) (divisorBp x : Int) : Int :=
  atAverageRate m f (x * BP / divisorBp) x

/-- A credit `v` used against taxes in order, each at most the tax left; the amounts used, per tax. -/
def allocateOrdered (v : Int) : List Int → List Int
  | [] => []
  | t :: rest => min (pos t) (pos v) :: allocateOrdered (v - min (pos t) (pos v)) rest

/-- A credit `v` (at most the taxes' total) split over the taxes in proportion to them, rounded down, the rounding
remainder to the first tax; the amounts used, per tax. -/
def allocateProportional (v : Int) (taxes : List Int) : List Int :=
  let tot := sumInts (taxes.map pos)
  let u := min (pos v) tot
  if tot = 0 then taxes.map fun _ => 0 else
    let shares := taxes.map fun t => u * pos t / tot
    match shares with
    | [] => []
    | s :: rest => (s + (u - sumInts shares)) :: rest

end TaxKernel
