import TaxCode.Individual.C.Table
import TaxCode.Forms.TaxTableData

/-!
# The 2025 Tax Table (as printed) and the Tax Computation Worksheet, against §1(j)

Form text: Publication 1040 (2025) "Tax Table" and "2025 Tax Computation Worksheet—Line 16"
(irs.gov/pub/irs-pdf/i1040tt.pdf). The table's 2,062 rows are parsed from the PDF text by
`tools/forms/parse_tax_table.py` into `TaxTableData.rows` (not regenerated from a rule); the parser checks that the
rows are contiguous from $0 to $100,000. Line 16 instructions: "If your taxable income is less than $100,000, you must
use the Tax Table".

Statute: §1(j)(2) with the 2025 brackets (Rev. Proc. 2024-40 §2.01), `C.scheduleCents` (exact tax in cents on whole-
dollar taxable income). §3(a) authorises the table "in lieu of" §1 tax, "computed on the basis of the rates prescribed
by section 1" — so a difference here is the price of the table, not an error; the question is how large it is.

Domain: whole-dollar taxable income `0 ≤ x < 100,000` (Form 1040 line 15 is whole dollars).

Method: one Boolean check per row (the row's value against the schedule at the row's first and last dollar), proved
sound once for all rows using that the schedule is increasing (`C.Sched.lipschitz`), then evaluated by the kernel
(`decide +kernel`; no `native_decide`).
-/

namespace TaxCode.Forms.TaxTable
open TaxCode.Individual TaxCode.Individual.C

abbrev Row := Int × Int × Int × Int × Int × Int

def Row.lo (r : Row) : Int := r.1
def Row.hi (r : Row) : Int := r.2.1

/-- The column for a filing status ("* This column must also be used by a qualifying surviving spouse"). -/
def Row.col (r : Row) : Filing → Int
  | .single => r.2.2.1
  | .mfj | .qss => r.2.2.2.1
  | .mfs => r.2.2.2.2.1
  | .hoh => r.2.2.2.2.2

/-- "At least X But less than Y": the first row containing `x`. -/
def find? : List Row → Int → Option Row
  | [], _ => none
  | r :: rs, x => if r.lo ≤ x ∧ x < r.hi then some r else find? rs x

/-- Line 16 by the Tax Table: the amount in the row containing line 15, in the filer's column. -/
def tableTax (f : Filing) (x : Int) : Int := ((find? rows x).map (·.col f)).getD 0

theorem find?_spec : ∀ (rs : List Row) (x : Int) (r : Row), find? rs x = some r → r ∈ rs ∧ r.lo ≤ x ∧ x < r.hi
  | [], _, _, h => by simp [find?] at h
  | s :: rs, x, r, h => by
    unfold find? at h
    split at h
    · cases h; exact ⟨List.mem_cons_self .., by omega, by omega⟩
    · have := find?_spec rs x r h; exact ⟨List.mem_cons_of_mem _ this.1, this.2⟩

/-- The rows run without gap from `a` to $100,000. -/
def chain : Int → List Row → Bool
  | a, [] => a == 100000
  | a, r :: rs => r.lo == a && decide (r.lo < r.hi) && chain r.hi rs

theorem chain_find : ∀ (rs : List Row) (a x : Int), chain a rs = true → a ≤ x → x < 100000 → (find? rs x).isSome
  | [], a, x, h, h1, h2 => by simp [chain] at h; omega
  | r :: rs, a, x, h, h1, h2 => by
    simp only [chain, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at h
    unfold find?
    split
    · rfl
    · exact chain_find rs r.hi x h.2 (by omega) h2

theorem rows_chain : chain 0 rows = true := by decide +kernel

/-! ## Exact maxima, per filing status -/

/-- A row is within `over` cents above and `under` cents below the schedule at both of its ends. -/
def rowOk (f : Filing) (over under : Int) (r : Row) : Bool :=
  decide (0 ≤ r.lo) && decide (100 * r.col f - scheduleCents f r.lo ≤ over) &&
    decide (scheduleCents f (r.hi - 1) - 100 * r.col f ≤ under)

theorem schedule_mono (f : Filing) (x y : Int) (hx : 0 ≤ x) (hxy : x ≤ y) : scheduleCents f x ≤ scheduleCents f y := by
  have := (Sched.lipschitz (sched f) (sched_ok f) x y hx hxy).1
  unfold scheduleCents; omega

/-- Soundness of the row check: if every row passes, the table is within the bounds at every whole dollar. -/
theorem bounds_of_rowOk (f : Filing) (over under : Int) (h : rows.all (rowOk f over under) = true) (x : Int)
    (h0 : 0 ≤ x) (h1 : x < 100000) :
    100 * tableTax f x - scheduleCents f x ≤ over ∧ scheduleCents f x - 100 * tableTax f x ≤ under := by
  have hs := chain_find rows 0 x rows_chain h0 h1
  cases hf : find? rows x with
  | none => rw [hf] at hs; simp at hs
  | some r =>
    have ⟨hm, hlo, hhi⟩ := find?_spec rows x r hf
    have hr := List.all_eq_true.mp h r hm
    simp only [rowOk, Bool.and_eq_true, decide_eq_true_eq] at hr
    have m1 := schedule_mono f r.lo x hr.1.1 hlo
    have m2 := schedule_mono f x (r.hi - 1) h0 (by omega)
    simp only [tableTax, hf, Option.map_some, Option.getD_some]
    omega

theorem rows_ok_single : rows.all (rowOk .single 600 478) = true := by decide +kernel
theorem rows_ok_mfj : rows.all (rowOk .mfj 600 478) = true := by decide +kernel
theorem rows_ok_mfs : rows.all (rowOk .mfs 600 478) = true := by decide +kernel
theorem rows_ok_hoh : rows.all (rowOk .hoh 600 478) = true := by decide +kernel

/-- **The printed 2025 Tax Table never charges more than $6.00 above, nor $4.78 below, the exact §1(j) tax**, for
every filing status and every whole-dollar taxable income under $100,000 ... -/
theorem table_bounds (f : Filing) (x : Int) (h0 : 0 ≤ x) (h1 : x < 100000) :
    100 * tableTax f x - scheduleCents f x ≤ 600 ∧ scheduleCents f x - 100 * tableTax f x ≤ 478 := by
  apply bounds_of_rowOk f 600 478 _ x h0 h1
  cases f
  · exact rows_ok_single
  · exact rows_ok_mfj
  · exact rows_ok_mfs
  · exact rows_ok_hoh
  · exact (by decide +kernel : rows.all (rowOk .qss 600 478) = true)

/-- ... and both bounds are attained in every column (all four are in their 22% bracket there): +$6.00 at $99,950
(the row $99,950–$100,000 charges the tax on its midpoint $99,975, rounded to the dollar), −$4.78 at $99,999. -/
theorem table_bounds_attained (f : Filing) :
    100 * tableTax f 99950 - scheduleCents f 99950 = 600 ∧ scheduleCents f 99999 - 100 * tableTax f 99999 = 478 := by
  cases f <;> decide +kernel

/-- In whole dollars against the schedule rounded to the dollar (`C.scheduleTax`): at most $6 over, $5 under. -/
theorem table_bounds_rounded (f : Filing) (x : Int) (h0 : 0 ≤ x) (h1 : x < 100000) :
    tableTax f x - scheduleTax f x ≤ 6 ∧ scheduleTax f x - tableTax f x ≤ 5 := by
  have := table_bounds f x h0 h1
  unfold scheduleTax roundDollar; omega

theorem table_bounds_rounded_attained (f : Filing) :
    tableTax f 99950 - scheduleTax f 99950 = 6 ∧ scheduleTax f 99999 - tableTax f 99999 = 5 := by
  cases f <;> decide +kernel

/-! ## The printed table is the model's midpoint rule, row by row -/

/-- Every printed amount equals `C.tableTax` (the schedule tax on the row's midpoint, rounded half up) at the row's
first dollar; with `C.midpoint2` constant on each printed row (lines $5/$10/$10, then $25 to $3,000, then $50), the
model's regenerated table and the printed table agree everywhere. -/
def rowMid (r : Row) : Bool :=
  [Filing.single, .mfj, .mfs, .hoh].all fun f =>
    r.col f == C.tableTax f r.lo && C.midpoint2 r.lo == C.midpoint2 (r.hi - 1) && C.midpoint2 r.lo == r.lo + r.hi

theorem rows_midpoint : rows.all rowMid = true := by decide +kernel

/-! ## Tax Computation Worksheet (taxable income $100,000 or more) -/

/-- The worksheet as printed (Sections A–D, columns (a)–(d)): "(c) Multiply (a) by (b)", "Subtract (d) from (c)",
in cents. Multiplication amounts 22%, 24%, 32%, 35%, 37%; subtraction amounts as printed. -/
def tcwForm (f : Filing) (x : Int) : Int :=
  match f with
  | .single =>  -- Section A
    if x ≤ 103350 then 22 * x - 508600 else if x ≤ 197300 then 24 * x - 715300
    else if x ≤ 250525 then 32 * x - 2293700 else if x ≤ 626350 then 35 * x - 3045275 else 37 * x - 4297975
  | .mfj | .qss =>  -- Section B
    if x ≤ 206700 then 22 * x - 1017200 else if x ≤ 394600 then 24 * x - 1430600
    else if x ≤ 501050 then 32 * x - 4587400 else if x ≤ 751600 then 35 * x - 6090550 else 37 * x - 7593750
  | .mfs =>  -- Section C
    if x ≤ 103350 then 22 * x - 508600 else if x ≤ 197300 then 24 * x - 715300
    else if x ≤ 250525 then 32 * x - 2293700 else if x ≤ 375800 then 35 * x - 3045275 else 37 * x - 3796875
  | .hoh =>  -- Section D
    if x ≤ 103350 then 22 * x - 682500 else if x ≤ 197300 then 24 * x - 889200
    else if x ≤ 250500 then 32 * x - 2467600 else if x ≤ 626350 then 35 * x - 3219100 else 37 * x - 4471800

/-- **The printed Tax Computation Worksheet is the §1(j) schedule to the cent for every taxable income ≥ $100,000.** -/
theorem tcw_eq_statute (f : Filing) (x : Int) (hx : 100000 ≤ x) : tcwForm f x = scheduleCents f x := by
  have := tcw_eq_schedule f x hx
  have e : tcwForm f x = tcwCents f x := by cases f <;> rfl
  omega

/-- Across the $100,000 seam the table and the worksheet differ by the table's own rounding only. -/
theorem seam : tableTax .single 99999 = 16909 ∧ roundDollar (tcwForm .single 100000) 100 = 16914 := by decide +kernel

end TaxCode.Forms.TaxTable

#print axioms TaxCode.Forms.TaxTable.table_bounds
#print axioms TaxCode.Forms.TaxTable.table_bounds_attained
#print axioms TaxCode.Forms.TaxTable.table_bounds_rounded
#print axioms TaxCode.Forms.TaxTable.rows_midpoint
#print axioms TaxCode.Forms.TaxTable.tcw_eq_statute
