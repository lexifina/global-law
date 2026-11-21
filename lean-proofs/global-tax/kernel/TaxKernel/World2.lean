import TaxKernel.World

/-!
# TaxKernel.World2 (1.4.0, 2026-11-20): parts the world batches asked for (world/KERNEL_REQUESTS.md), added only

Import it explicitly (`import TaxKernel.World2`, which imports `TaxKernel.World` and the whole kernel). Neither the root
module `TaxKernel` nor `TaxKernel.World` imports it, so every model built so far (the 38 and the world models on 1.3.0)
is unchanged by construction; all were rebuilt against 1.4.0 in a copy and gave byte-identical output (world/kcheck).
A model that imports it calls `TaxKernel.worldMain14` (prints kernel 1.4.0 under `--version`).

* **Column tariffs: the band set is chosen by the size of the whole income** (EG Law 91/2005 art. 8 as replaced by
  Law 7/2024: six columns by total net income; any statute whose lower bands are withdrawn above an income limit).
  `pickColumn cols dflt x` (the first column whose limit `x` does not exceed, else `dflt`), `columnTicks cols dflt x`
  (that column's schedule applied to the whole income). `columnTicks_succ`: away from the column limits the marginal
  rate is the chosen schedule's band rate, so **every jump (notch) sits at a column limit**; `columnJumps cols dflt`
  lists the jump at each limit (computable: check it with `#guard` / `decide`). `Extra38.rateOfBase` picks one rate;
  this picks a whole schedule.
* **Amounts indexed by a published coefficient** (AR Ley 27.743 arts. 30 and 94: base amount × the IPC coefficient,
  adjusted in January and July; any "updated by the CPI factor" rule): `indexAmount m num den base` (= base × num/den,
  rounded by `m`), `indexChain m [(num, den), …] base` (successive adjustments, rounded at each step as statutes that
  publish each step's amounts do), `Schedule.indexed s m num den` (thresholds indexed, rates kept:
  `indexed_rates`), and `indexReproduces m num den pairs tol` (every printed amount reproduced from its base within
  `tol`: the `#guard` that a single coefficient explains a published table). `indexAmount_mono`.
-/

namespace TaxKernel
open Lean

def kernelVersionWorld14 : String := "TaxKernel 1.4.0 (2026-11-20)"

/-- `countryMain`, but `--version` / `--help` name kernel 1.4.0. -/
def worldMain14 (k : Country) (args : List String) : IO UInt32 := do
  if args.contains "--version" then
    IO.println (Json.compress (Json.mkObj [("country", Json.str k.code), ("name", Json.str k.name),
      ("currency", Json.str k.currency), ("year", Json.str k.year), ("kernel", Json.str kernelVersionWorld14)]))
    return 0
  if args.contains "--help" then
    IO.println s!"usage: {k.code.toLower}tax [options] < households.jsonl > results.jsonl\n{k.name} {k.year}, {kernelVersionWorld14}"
    return 0
  countryMain k args

/-! ## Column tariffs -/

/-- The schedule of the first column whose limit is at least `x` (columns in increasing limit order); `dflt` above
the last limit. -/
def pickColumn : List (Int × Schedule) → Schedule → Int → Schedule
  | [], d, _ => d
  | (lim, s) :: rest, d, x => if x ≤ lim then s else pickColumn rest d x

/-- Ticks of the chosen column's schedule on the whole income. -/
def columnTicks (cols : List (Int × Schedule)) (dflt : Schedule) (x : Int) : Int :=
  (pickColumn cols dflt x).ticks x

/-- The jump at each column limit `L`: ticks at `L + 1` minus ticks at `L`, less the marginal rate of the column
chosen at `L` (0 = no notch). -/
def columnJumps (cols : List (Int × Schedule)) (dflt : Schedule) : List (Int × Int) :=
  cols.map fun p => (p.1, columnTicks cols dflt (p.1 + 1) - columnTicks cols dflt p.1 - (pickColumn cols dflt p.1).rate p.1)

theorem pickColumn_succ (dflt : Schedule) (x : Int) :
    ∀ (cols : List (Int × Schedule)), (∀ p ∈ cols, p.1 ≠ x) → pickColumn cols dflt (x + 1) = pickColumn cols dflt x
  | [], _ => rfl
  | (lim, s) :: rest, h => by
    have hl : lim ≠ x := h (lim, s) (by simp)
    have hr : ∀ p ∈ rest, p.1 ≠ x := fun p hp => h p (by simp [hp])
    simp only [pickColumn]
    by_cases h1 : x ≤ lim
    · rw [if_pos (by omega), if_pos h1]
    · rw [if_neg (by omega), if_neg h1]
      exact pickColumn_succ dflt x rest hr

/-- Away from the column limits the tariff moves by the chosen schedule's band rate: notches only at the limits. -/
theorem columnTicks_succ (cols : List (Int × Schedule)) (dflt : Schedule) (x : Int) (h : ∀ p ∈ cols, p.1 ≠ x) :
    columnTicks cols dflt (x + 1) - columnTicks cols dflt x = (pickColumn cols dflt x).rate x := by
  unfold columnTicks
  rw [pickColumn_succ dflt x cols h]
  exact Schedule.ticks_succ _ _

/-! ## Amounts indexed by a published coefficient -/

/-- `base × num / den`, rounded by `m` (e.g. num/den = 1.4567 as 14567/10000). -/
def indexAmount (m : Round) (num den base : Int) : Int := divR m (base * num) den

/-- Successive adjustments, each rounded. -/
def indexChain (m : Round) : List (Int × Int) → Int → Int
  | [], b => b
  | (n, d) :: rest, b => indexChain m rest (indexAmount m n d b)

/-- Thresholds indexed, rates unchanged. -/
def Schedule.indexed (s : Schedule) (m : Round) (num den : Int) : Schedule := s.mapLo (indexAmount m num den)

/-- Every printed amount equals its base amount indexed, within `tol`. -/
def indexReproduces (m : Round) (num den : Int) (pairs : List (Int × Int)) (tol : Int := 0) : Bool :=
  pairs.all fun p => decide ((indexAmount m num den p.1 - p.2).natAbs ≤ tol.toNat)

theorem indexed_rates (s : Schedule) (m : Round) (num den : Int) :
    (s.indexed m num den).bands.map Band.rate = s.bands.map Band.rate := by
  simp [Schedule.indexed, Schedule.mapLo, List.map_map, Function.comp_def]

theorem indexAmount_mono (m : Round) (hm : m.isMonotoneMode) {num den : Int} (hd : 0 < den) (hn : 0 ≤ num)
    {a b : Int} (h : a ≤ b) : indexAmount m num den a ≤ indexAmount m num den b := by
  unfold indexAmount
  exact divR_mono m den hd hm (Int.mul_le_mul_of_nonneg_right h hn)

end TaxKernel
