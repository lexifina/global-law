import TaxKernel

/-!
# TaxKernel.World (1.3.0, 2026-11-20): parts for the world expansion (CONTRACTWORLD.md), added only

Import it explicitly (`import TaxKernel.World`, which also imports the whole of `TaxKernel`). It is **not** imported by
the root module `TaxKernel`, so the 38 existing models and their oleans are unchanged by construction; every name of
1.2.1 keeps its meaning. A world model's `main` should call `TaxKernel.worldMain` (prints kernel 1.3.0 under
`--version`, otherwise exactly `countryMain`).

Patterns the remaining countries need, written once:

* **Amounts fixed in an indexed unit** (CL UTM/UTA, CO UVT, PE UIT, UY BPC, VE unidad tributaria, BO/TR minimum-wage
  multiples): `unitsToMoney`, `moneyToUnits`, `Schedule.ofUnits` (thresholds given in units, scaled by `scale`, e.g.
  1000 = thousandths of a unit), `viaUnits` (statutes that compute the tax *in units* and convert the result: CO ET
  art. 241). The statute's own rounding of the conversion is the `Round` argument; `ofUnits_rates` proves the
  conversion keeps every band's rate, `unitsToMoney_mono` that it keeps the order of the thresholds.
* **Schedular (cedular) systems** (CR salary tax beside other rents, RS salary tax + annual citizens' income tax, LB
  LY SY CD ET category taxes, PE work/capital categories, UY IRPF categories, CO cedulas): `Cedula {name base tax}`,
  `cedularTotal`, `cedularBase`, `cedularDetail` (ready for `Out.detail` / `surtaxes`), and an annual **overlay** on
  the sum of the categories (`overlayTax f cs credit`): with `credit = true` the category taxes already paid are
  credited (CL global complementario with the impuesto unico credit: `overlay_credit_total` proves the household then
  pays exactly `max (category taxes) (global tax)`); with `false` the overlay is added (RS annual tax on citizens'
  income above a threshold, on top of the salary tax).
* **Zakat and other all-or-nothing levies** (2.5 % above a nisab; where a statute levies zakat on wages or savings:
  check yours): `zakat nisab rate` is a `Contribution` with `floor := nisab`, so `Contribution.amount` computes it and
  `zakat_notch` instantiates `Contribution.floor_notch` (crossing the nisab costs `rate × nisab` at once). Zakat as a
  credit against income tax (MY ITA s. 6A(3)) is `applyCredits`; as a deduction from income (ID) is `taxableAfter`.
* **Territorial taxation** (PA, CR, PY, BO, HK-style source rules): `sourceBase territorial domestic foreign`, with the
  optional household field `"foreignIncome"` (whole local units, household total; read with `Canon.foreignIncome`).
  A model that taxes residents on worldwide income adds it; a territorial one does not. The contract is unchanged:
  households without the field have `foreignIncome = 0`.
* **"The tax on the minimum wage is exempt"** (TR GVK art. 23/18 and 32, and any exemption written as the tax on an
  amount rather than the amount): `exemptTaxOf f exempt x = pos (f x - f (min x exempt))`; `exemptTaxOf_below` (nothing
  is due up to the exempt amount) and `exemptTaxOf_le` (never more than the tax without it, for `f ≥ 0` monotone).
* **Cumulative withholding** (monthly tax on the cumulative base, minus the tax already withheld: TR, ZA/KE/UK-style
  PAYE): `cumWithholdings f prev cumBases` and `cumWithholdings_sum` (the instalments add up to `f` of the last
  cumulative base: no annual adjustment is needed when the monthly table is the annual one).

Recipes that need no new part: flat tax with a monthly threshold (TL) `perPeriod 12 (fun m => (Schedule.flatAbove t r)
.tax rule m) annual`; credit points (IL) a non-refundable `Credit` worth `points × point value`; dependants with a cap on
their number (ID PTKP up to 3) `perChildByRank [a, a, a, 0] n`; family parts (SN, CG, GA) `quotient` /
`cappedQuotient`; municipal or communal surcharges (CM CAC, LI, ME) `Multiplier`; no income tax at all (Gulf states,
BS, BN, MC, VA, VU, AG, KN) `incomeTax := 0` with only `employeeSocial` and a `detail` note naming the statute that
levies the contributions.
-/

namespace TaxKernel
open Lean

def kernelVersionWorld : String := "TaxKernel 1.3.0 (2026-11-20)"

/-- `countryMain`, but `--version` / `--help` name kernel 1.3.0. -/
def worldMain (k : Country) (args : List String) : IO UInt32 := do
  if args.contains "--version" then
    IO.println (Json.compress (Json.mkObj [("country", Json.str k.code), ("name", Json.str k.name),
      ("currency", Json.str k.currency), ("year", Json.str k.year), ("kernel", Json.str kernelVersionWorld)]))
    return 0
  if args.contains "--help" then
    IO.println s!"usage: {k.code.toLower}tax [options] < households.jsonl > results.jsonl\n{k.name} {k.year}, {kernelVersionWorld}"
    return 0
  countryMain k args

/-! ## Indexed units -/

/-- `u` units, given in `1/scale` of a unit, at `unitValue` money per unit, rounded by `m`. -/
def unitsToMoney (m : Round) (scale unitValue u : Int) : Int := divR m (u * unitValue) scale

/-- Money `x` expressed in `1/scale` of a unit worth `unitValue`, rounded by `m`. -/
def moneyToUnits (m : Round) (scale unitValue x : Int) : Int := divR m (x * scale) unitValue

/-- A band schedule whose thresholds the statute prints in units: `[(0, 0), (13500, 400), …]` with `scale = 1000`
means 13.5 units at 4 %. -/
def Schedule.ofUnits (l : List (Int × Int)) (m : Round) (scale unitValue : Int) : Schedule :=
  Schedule.ofList (l.map fun p => (unitsToMoney m scale unitValue p.1, p.2))

/-- A tax the statute computes in units (income converted with `mIn`, the result converted back with `mOut`). -/
def viaUnits (f : Int → Int) (mIn mOut : Round) (scale unitValue x : Int) : Int :=
  unitsToMoney mOut scale unitValue (f (moneyToUnits mIn scale unitValue x))

theorem ofUnits_rates (l : List (Int × Int)) (m : Round) (scale unitValue : Int) :
    (Schedule.ofUnits l m scale unitValue).bands.map Band.rate = l.map Prod.snd := by
  simp [Schedule.ofUnits, Schedule.ofList, List.map_map, Function.comp_def]

theorem unitsToMoney_mono (m : Round) (hm : m.isMonotoneMode) {scale unitValue : Int} (hs : 0 < scale)
    (hv : 0 ≤ unitValue) {a b : Int} (h : a ≤ b) : unitsToMoney m scale unitValue a ≤ unitsToMoney m scale unitValue b := by
  unfold unitsToMoney
  exact divR_mono m scale hs hm (Int.mul_le_mul_of_nonneg_right h hv)

/-! ## Schedular systems -/

/-- One category of income with its own base and its own tax. -/
structure Cedula where
  name : String
  base : Int
  tax : Int → Int

def Cedula.amount (c : Cedula) : Int := c.tax c.base

def cedularTotal : List Cedula → Int
  | [] => 0
  | c :: cs => c.amount + cedularTotal cs

def cedularBase : List Cedula → Int
  | [] => 0
  | c :: cs => c.base + cedularBase cs

def cedularDetail (cs : List Cedula) : List (String × Int) := cs.map fun c => (c.name, c.amount)

/-- An annual tax `f` on the sum of the category bases; with `credit` the category taxes are credited against it
(never below zero). -/
def overlayTax (f : Int → Int) (cs : List Cedula) (credit : Bool) : Int :=
  if credit then pos (f (cedularBase cs) - cedularTotal cs) else f (cedularBase cs)

theorem cedularTotal_append (a b : List Cedula) : cedularTotal (a ++ b) = cedularTotal a + cedularTotal b := by
  induction a with
  | nil => simp [cedularTotal]
  | cons c cs ih => simp only [List.cons_append, cedularTotal, ih]; omega

/-- With the credit, categories + overlay = the larger of the category taxes and the global tax. -/
theorem overlay_credit_total (f : Int → Int) (cs : List Cedula) :
    cedularTotal cs + overlayTax f cs true = max (cedularTotal cs) (f (cedularBase cs)) := by
  unfold overlayTax pos
  simp only [ite_true]
  omega

theorem overlay_credit_nonneg (f : Int → Int) (cs : List Cedula) : 0 ≤ overlayTax f cs true := by
  unfold overlayTax; simp only [ite_true]; exact pos_nonneg _

/-! ## Zakat (all-or-nothing levy above a nisab) -/

def zakat (nisab rate : Int) : Contribution := { name := "zakat", sched := Schedule.flat rate, floor := nisab }

/-- Crossing the nisab by one unit costs the levy on the whole nisab. -/
theorem zakat_notch (nisab rate : Int) :
    (zakat nisab rate).ticks nisab - (zakat nisab rate).ticks (nisab - 1) = (Schedule.flat rate).ticks nisab := by
  have h := Contribution.floor_notch (zakat nisab rate)
  simpa [zakat, Contribution.base] using h

/-! ## Territorial taxation -/

def sourceBase (territorial : Bool) (domestic foreign : Int) : Int :=
  if territorial then domestic else domestic + foreign

/-- Optional household field `"foreignIncome"` (whole local units; 0 when absent). -/
def Canon.foreignIncome (c : Canon) : Int := (c.int? "foreignIncome").getD 0

theorem sourceBase_territorial_le {domestic foreign : Int} (h : 0 ≤ foreign) (t : Bool) :
    sourceBase true domestic foreign ≤ sourceBase t domestic foreign := by
  cases t <;> simp [sourceBase] <;> omega

/-! ## An exemption written as the tax on an amount -/

def exemptTaxOf (f : Int → Int) (exempt x : Int) : Int := pos (f x - f (min x exempt))

theorem exemptTaxOf_below (f : Int → Int) {exempt x : Int} (h : x ≤ exempt) : exemptTaxOf f exempt x = 0 := by
  unfold exemptTaxOf
  rw [show min x exempt = x by omega]
  simp [pos]

theorem exemptTaxOf_le (f : Int → Int) (hf : ∀ y, 0 ≤ f y) (exempt x : Int) : exemptTaxOf f exempt x ≤ f x := by
  unfold exemptTaxOf pos
  have := hf (min x exempt)
  have := hf x
  omega

/-! ## Cumulative withholding -/

/-- Instalments on cumulative bases `cs` (non-decreasing in practice), `prev` = the base already taxed (0 in January). -/
def cumWithholdings (f : Int → Int) : Int → List Int → List Int
  | _, [] => []
  | p, c :: cs => (f c - f p) :: cumWithholdings f c cs

def lastOr : Int → List Int → Int
  | p, [] => p
  | _, c :: cs => lastOr c cs

def listSum : List Int → Int
  | [] => 0
  | x :: xs => x + listSum xs

/-- The instalments telescope: their sum is the tax on the last cumulative base less the tax on `prev`. -/
theorem cumWithholdings_sum (f : Int → Int) : ∀ (p : Int) (cs : List Int),
    listSum (cumWithholdings f p cs) = f (lastOr p cs) - f p
  | p, [] => by simp [cumWithholdings, listSum, lastOr]
  | p, c :: cs => by
    simp only [cumWithholdings, listSum, lastOr]
    rw [cumWithholdings_sum f c cs]
    omega

end TaxKernel
