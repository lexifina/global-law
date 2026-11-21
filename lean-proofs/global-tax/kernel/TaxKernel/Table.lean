import TaxKernel.Rounding

/-!
# TaxKernel.Table: banded lookup tables (added in 1.1; asked for by KR and MX)

Some statutes govern by a printed table rather than a formula: Korea's 근로장려금 / 자녀장려금 산정표 (조특법 시행령
별표 11), Mexico's monthly and annual tarifas (LISR art. 96, 152), withholding tables. A `Table` is a list of rows
`⟨lo, hi, value⟩`: income in `[lo, hi]` gets `value`. The checks are `Bool`s, so a concrete table's property (or its
failure: a finding) is proved by `decide` / `native_decide`:

* `Table.contiguous t`: the rows cover a range without gaps or overlaps (`hi + 1 = next lo`);
* `Table.valuesMono t`: values never fall from one row to the next (a tax table should not; a phase-out table
  should never rise: use `valuesAnti`);
* `Table.agreesWith t f probe tol`: every row's value is within `tol` of the formula `f` evaluated at the row's
  `probe` point (e.g. `fun r => r.hi`, the statute's "largest value on the row");
* `Table.disagreements t f probe tol`: the rows that do not (the evidence for a table ≠ formula finding).

`Table.lookup t x d` is the value of the first row containing `x` (`d` if none).
Theorem: `lookup_of_mem` (a row that contains `x` and comes first gives the value).
-/

namespace TaxKernel

structure Row where
  lo : Int
  hi : Int
  value : Int
  deriving Repr, DecidableEq, Inhabited

abbrev Table := List Row

namespace Table

def lookup : Table → Int → Int → Int
  | [], _, d => d
  | r :: rest, x, d => if r.lo ≤ x ∧ x ≤ r.hi then r.value else lookup rest x d

def contiguous : Table → Bool
  | [] => true
  | [r] => decide (r.lo ≤ r.hi)
  | r :: s :: rest => decide (r.lo ≤ r.hi) && decide (r.hi + 1 = s.lo) && contiguous (s :: rest)

def valuesMono : Table → Bool
  | [] => true
  | [_] => true
  | r :: s :: rest => decide (r.value ≤ s.value) && valuesMono (s :: rest)

def valuesAnti : Table → Bool
  | [] => true
  | [_] => true
  | r :: s :: rest => decide (s.value ≤ r.value) && valuesAnti (s :: rest)

def agreesWith (t : Table) (f : Int → Int) (probe : Row → Int) (tol : Int := 0) : Bool :=
  t.all fun r => decide (r.value - f (probe r) ≤ tol) && decide (f (probe r) - r.value ≤ tol)

def disagreements (t : Table) (f : Int → Int) (probe : Row → Int) (tol : Int := 0) : List (Row × Int) :=
  (t.filter fun r => !(decide (r.value - f (probe r) ≤ tol) && decide (f (probe r) - r.value ≤ tol))).map
    fun r => (r, f (probe r))

/-- Rows of width `w` from `lo` to `hi` with values `g` of each row (to build a table from a formula and compare). -/
def ofFormula (lo hi w : Nat) (g : Int → Int → Int) : Table :=
  (List.range ((hi - lo) / w + 1)).map fun (i : Nat) =>
    let a : Int := (lo : Int) + (i : Int) * (w : Int)
    let b : Int := a + (w : Int) - 1
    ⟨a, b, g a b⟩

theorem lookup_of_mem (r : Row) (rest : Table) (x d : Int) (h : r.lo ≤ x ∧ x ≤ r.hi) :
    lookup (r :: rest) x d = r.value := by
  simp [lookup, h]

end Table

/-! ## Contributions computed per period

Several statutes charge contributions per month (CZ monthly assessment and rounding, KR's monthly premium with July-
June bases, JP's 標準報酬 grades) rather than on the year's pay. `perPeriod n f annual` splits the annual amount into
`n` equal periods (the first `annual % n` periods get one unit more) and sums `f` over them: the annual figure a
monthly rule produces for an even income stream. -/
def perPeriod (n : Nat) (f : Int → Int) (annual : Int) : Int :=
  let q := annual / n
  let r := (annual % n).toNat
  (List.range n).foldl (fun acc i => acc + f (q + if i < r then 1 else 0)) 0

theorem perPeriod_linear (n : Nat) (k annual : Int) (h : annual % n = 0) :
    perPeriod n (fun x => k * x) annual = (List.range n).foldl (fun acc _ => acc + k * (annual / n)) 0 := by
  unfold perPeriod
  simp [h]

end TaxKernel
