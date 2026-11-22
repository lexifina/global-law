import TaxKernel.Global2.WhtState

/-!
# TaxKernel.Global2.Employer (2.6.0, 2026-11-21): the employer of a household's wages (R4-14-1)

Several employer levies depend on the employer, not on the employee: NA VET levy (GN 67 of 2021 para 3: 1 % of payroll
for employers with an annual payroll of N$1 000 000 or more), CD INPP (rates by the size of the workforce), NA
Employees' Compensation (rate by the employer's risk class, ECA 1941 s. 69). A household line gave each adult's `wages`
only, so these were booked on company lines and households had no charge.

**The input** (optional, on each `household.adults` record; read like `company.payroll` / `employees` / `sector`):

| JSON field | `EmployerFacts` | meaning (not given: −1 / `none` / `""`) |
|---|---|---|
| `"employerPayroll"` | `payroll` | the employer's annual gross payroll, local currency |
| `"employerEmployees"` | `employees` | the employer's headcount |
| `"employerSector"` | `sectors` | the employer's sector, a string or an array (names as `company.sector`, `Sector.canonical`) |
| `"employerRiskClass"` | `riskClass` | the employer's risk or tariff class (a string or a number, read as text) |

`Adult` is unchanged; `employerOf g i` reads adult `i`'s record from the household's input line. A 1.x household
gives none of them (`employerOf_null`).

**The levy** (`EmployerLevy`): rules tried in order (`EmployerRule`: a rate in bp of the wages, optionally capped per
employee, and `tests` on the employer: `payrollAtLeast`, `payrollBelow`, `employeesAtLeast`, `employeesAtMost`,
`inSectors`, `notInSectors`, `riskClasses`); the first whose tests hold applies. As `StateRule` (2.4.0), **what an absent
fact means is declared per rule, with no default** (`ifUnknown : StateUnknown`): `.general` (passed over: the next rule
is tried, and `notes` says so), `.presume` (applied as the statute presumes; the statute text ends with
`employerPresumedNote`), `.gradeC` (no charge for that adult; `unknown` lists it as grade C). No rule applying (facts
given, thresholds not met) is no charge. One charge per adult with wages (> 0): base = the wages, relieved = the wages up
to `wageCap`, due = rate × relieved (`round`), bearer `employer` (heading `oecd`, 3000 by default; 2200 for an
employer social contribution), event `"adult <i> wages"`.

`levy.family name` books it for household entities (and, with `companies := true`, for a company entity on its own
`company.payroll`, the facts being the company's: `"payroll"`, `"employees"`, `"sector"`, `"riskClass"` on the company
record).

Theorems: `employerOf_null`, `EmployerTest.eval_none`, `EmployerRule.check_plain`, `employerPick_noFacts` (no fact given
never yields a rate from a conditional rule unless the rule presumes it), `EmployerLevy.charges_noWages`,
`chargeOf_wf`, `chargeOf_due_nonneg`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-- What the line says of an employer. -/
structure EmployerFacts where
  payroll : Int := -1
  employees : Int := -1
  sectors : Option (List String) := none
  riskClass : String := ""
  /-- 2.7.0 (R4-18-1): the employer's annual turnover (−1: not given) -/
  turnover : Int := -1
  deriving Repr, Inhabited, BEq

/-- A string or array of strings at key `k` (`none`: absent or empty). -/
def jsonStrings (j : Json) (k : String) : Option (List String) :=
  match j.getObjVal? k with
  | .ok (.str s) => if s.isEmpty then none else some [s]
  | .ok (.arr a) =>
    let l := a.toList.filterMap fun x => match x with | .str s => some s | _ => none
    if l.isEmpty then none else some l
  | _ => none

/-- A string or number at key `k`, as text (`""`: absent). -/
def jsonText (j : Json) (k : String) : String :=
  match j.getObjVal? k with
  | .ok (.str s) => s
  | .ok (.num n) => toString (numToInt n)
  | _ => ""

/-- Facts from a record with the given keys. -/
def EmployerFacts.ofJson (j : Json) (payroll employees sector risk : String) (turnover : String := "") : EmployerFacts :=
  { payroll := intField j payroll (-1), employees := intField j employees (-1), sectors := jsonStrings j sector,
    riskClass := jsonText j risk, turnover := if turnover.isEmpty then -1 else intField j turnover (-1) }

/-- The record of adult `i` (0-based) in the household's input line. -/
def adultJson (g : CanonGlobal) (i : Nat) : Json := (arrField g.household.raw "adults").toList.getD i Json.null

/-- Adult `i`'s employer, from `"employerPayroll"`, `"employerEmployees"`, `"employerSector"`, `"employerRiskClass"`. -/
def employerOf (g : CanonGlobal) (i : Nat) : EmployerFacts :=
  EmployerFacts.ofJson (adultJson g i) "employerPayroll" "employerEmployees" "employerSector" "employerRiskClass"
    "employerTurnover"

/-- A company entity as an employer: `"payroll"`, `"employees"`, `"sector"`, `"riskClass"` on its company record. -/
def companyEmployer (g : CanonGlobal) : EmployerFacts :=
  let cj := match g.raw.getObjVal? "company" with | .ok c => c | .error _ => Json.null
  EmployerFacts.ofJson cj "payroll" "employees" "sector" "riskClass" "turnover"

/-- A record without the fields gives no fact. -/
theorem employerOf_null : EmployerFacts.ofJson Json.null "employerPayroll" "employerEmployees" "employerSector"
    "employerRiskClass" = {} := by
  rfl

inductive EmployerTest where
  /-- payroll ≥ x -/
  | payrollAtLeast (x : Int)
  /-- payroll < x -/
  | payrollBelow (x : Int)
  /-- employees ≥ n -/
  | employeesAtLeast (n : Int)
  /-- employees ≤ n -/
  | employeesAtMost (n : Int)
  | inSectors (l : List String)
  | notInSectors (l : List String)
  | riskClasses (l : List String)
  /-- 2.7.0 (R4-18-1): turnover ≥ x -/
  | turnoverAtLeast (x : Int)
  /-- 2.7.0 (R4-18-1): turnover < x -/
  | turnoverBelow (x : Int)
  deriving Repr, Inhabited, BEq

namespace EmployerTest

/-- `some` the test's value when its fact is given, `none` when not. -/
def eval : EmployerTest → EmployerFacts → Option Bool
  | .payrollAtLeast x, f => if f.payroll < 0 then none else some (decide (x ≤ f.payroll))
  | .payrollBelow x, f => if f.payroll < 0 then none else some (decide (f.payroll < x))
  | .employeesAtLeast n, f => if f.employees < 0 then none else some (decide (n ≤ f.employees))
  | .employeesAtMost n, f => if f.employees < 0 then none else some (decide (f.employees ≤ n))
  | .inSectors l, f => f.sectors.map fun s => s.any l.contains
  | .notInSectors l, f => f.sectors.map fun s => !s.any l.contains
  | .riskClasses l, f => if f.riskClass == "" then none else some (l.contains f.riskClass)
  | .turnoverAtLeast x, f => if f.turnover < 0 then none else some (decide (x ≤ f.turnover))
  | .turnoverBelow x, f => if f.turnover < 0 then none else some (decide (f.turnover < x))

def fact : EmployerTest → String
  | .payrollAtLeast _ | .payrollBelow _ => "employerPayroll"
  | .employeesAtLeast _ | .employeesAtMost _ => "employerEmployees"
  | .inSectors _ | .notInSectors _ => "employerSector"
  | .riskClasses _ => "employerRiskClass"
  | .turnoverAtLeast _ | .turnoverBelow _ => "employerTurnover"

/-- With no fact given, no test is decided. -/
theorem eval_none (t : EmployerTest) : t.eval {} = none := by
  cases t <;> simp [eval]

end EmployerTest

structure EmployerRule where
  /-- rate on the wages, bp -/
  rateBp : Int
  /-- every test must hold -/
  tests : List EmployerTest := []
  /-- what an absent fact means (no default: every rule says it) -/
  ifUnknown : StateUnknown
  /-- wages counted per employee at most this (−1: no cap) -/
  wageCap : Int := -1
  statute : String
  deriving Repr, Inhabited

namespace EmployerRule

/-- `some true`: every test holds; `some false`: a given fact fails one; `none`: no test fails but a fact is missing. -/
def check (r : EmployerRule) (f : EmployerFacts) : Option Bool :=
  let vs := r.tests.map (·.eval f)
  if vs.any (· == some false) then some false else if vs.all (· == some true) then some true else none

def missing (r : EmployerRule) (f : EmployerFacts) : List String :=
  ((r.tests.filter fun t => (t.eval f).isNone).map (·.fact)).eraseDups

theorem check_plain (rate : Int) (u : StateUnknown) (cap : Int) (st : String) (f : EmployerFacts) :
    ({ rateBp := rate, ifUnknown := u, wageCap := cap, statute := st } : EmployerRule).check f = some true := by
  simp [check]

end EmployerRule

inductive EmployerPick where
  | rule (r : EmployerRule) (presumed : Bool)
  | gradeC (r : EmployerRule)
  | none
  deriving Repr, Inhabited

/-- The first rule whose tests hold (`.presume` on a missing fact: applied; `.gradeC`: stop), with the `.general` rules
passed over for a missing fact. -/
def employerPick (f : EmployerFacts) : List EmployerRule → EmployerPick × List EmployerRule
  | [] => (.none, [])
  | r :: rs =>
    match r.check f with
    | some true => (.rule r false, [])
    | some false => employerPick f rs
    | none =>
      match r.ifUnknown with
      | .general => let q := employerPick f rs; (q.1, r :: q.2)
      | .presume => (.rule r true, [])
      | .gradeC => (.gradeC r, [])

/-- The note a presumed rate's statute carries. -/
def employerPresumedNote : String := " (employer facts not given: applied as the statute presumes)"

/-- **No fact given never yields a rate silently**: the rule picked is unconditional (no tests) or presumed (its charge
says so). -/
theorem employerPick_noFacts (rs : List EmployerRule) (r : EmployerRule) (p : Bool)
    (h : (employerPick {} rs).1 = .rule r p) : r.tests = [] ∨ p = true := by
  induction rs with
  | nil => simp [employerPick] at h
  | cons r' rs ih =>
    by_cases ht : r'.tests = []
    · have hc : r'.check {} = some true := by simp [EmployerRule.check, ht]
      simp only [employerPick, hc] at h
      simp at h
      obtain ⟨rfl, -⟩ := h
      exact Or.inl ht
    · have hc : r'.check {} = none := by
        unfold EmployerRule.check
        obtain ⟨t, ts, hts⟩ := List.exists_cons_of_ne_nil ht
        simp [hts, EmployerTest.eval_none]
      simp only [employerPick, hc] at h
      cases hu : r'.ifUnknown <;> simp only [hu] at h
      · exact ih h
      · simp at h; exact Or.inr h.2
      · simp at h

structure EmployerLevy where
  name : String
  /-- 3000 payroll tax by default; `.sscEmployer` (2200) for an employer social contribution -/
  oecd : Oecd := .payroll
  level : Level := .central
  rules : List EmployerRule
  round : Rule := {}
  /-- also a company entity, on its own `company.payroll` -/
  companies : Bool := false
  deriving Repr, Inhabited

namespace EmployerLevy

/-- The charge on `wages` paid by an employer with facts `f` (`none`: no rule applies, or grade C). -/
def chargeOf (l : EmployerLevy) (f : EmployerFacts) (wages : Int) (event : String) : Option Charge :=
  match (employerPick f l.rules).1 with
  | .rule r pres =>
    let relieved := if 0 ≤ r.wageCap then min (pos wages) r.wageCap else pos wages
    some (charge l.oecd l.name wages (fun _ => relieved) (fun x => l.round.ofTicks (pos r.rateBp * x))
      (event := event) (level := l.level) (bearer := .employer)
      (statute := if pres then r.statute ++ employerPresumedNote else r.statute))
  | _ => none

/-- Each wage line the levy reads: (facts, wages, event, label for notes). -/
def lines (l : EmployerLevy) (g : CanonGlobal) : List (EmployerFacts × Int × String) :=
  if g.entity == .company then
    (if l.companies && 0 < g.company.payroll then [(companyEmployer g, g.company.payroll, "payroll")] else [])
  else
    (g.household.adults.zipIdx.filter fun (a, _) => 0 < a.wages).map fun (a, i) =>
      (employerOf g i, a.wages, s!"adult {i + 1} wages")

def charges (l : EmployerLevy) (g : CanonGlobal) : List Charge :=
  (l.lines g).filterMap fun (f, w, e) => l.chargeOf f w e

/-- For `unsupported`: wage lines whose rate depends on a fact not given (grade C). -/
def unknown (l : EmployerLevy) (g : CanonGlobal) : List String :=
  (l.lines g).filterMap fun (f, _, e) =>
    match (employerPick f l.rules).1 with
    | .gradeC r => some s!"{l.oecd.code} {l.name}: {e}: the rate depends on {", ".intercalate (r.missing f)}, not given ({r.statute}) (grade C)"
    | _ => none

/-- For `notes`: conditional rates passed over for a fact not given (`.general`), with what was booked instead. -/
def notes (l : EmployerLevy) (g : CanonGlobal) : List String :=
  (l.lines g).flatMap fun (f, _, e) =>
    let q := employerPick f l.rules
    q.2.map fun r =>
      s!"{l.oecd.code} {l.name}: {e}: conditional rate {r.rateBp} bp ({r.statute}) not tested: {", ".intercalate (r.missing f)} not given; "
        ++ (match q.1 with | .rule r' _ => s!"{r'.rateBp} bp booked ({r'.statute})" | _ => "no other rate")

/-- The levy as a family (its heading covered). -/
def family (l : EmployerLevy) (name : String := "") : Family :=
  { name := s!"{l.oecd.code} {if name.isEmpty then l.name else name}", covers := [l.oecd],
    run := fun _ g _ => l.charges g }

/-- A household without wages (every adult's wages ≤ 0) gets no charge. -/
theorem charges_noWages (l : EmployerLevy) (g : CanonGlobal) (hh : (g.entity == .company) = false)
    (hw : ∀ a ∈ g.household.adults, a.wages ≤ 0) : l.charges g = [] := by
  have : l.lines g = [] := by
    simp only [lines, hh, Bool.false_eq_true, ↓reduceIte, List.map_eq_nil_iff, List.filter_eq_nil_iff]
    intro p hp
    have := hw p.1 (List.fst_mem_of_mem_zipIdx hp)
    simp; omega
  simp [charges, this]

theorem chargeOf_wf (l : EmployerLevy) (f : EmployerFacts) (w : Int) (e : String) (c : Charge)
    (h : l.chargeOf f w e = some c) : c.WF := by
  unfold chargeOf at h
  split at h
  · simp at h; subst h; exact charge_wf ..
  · simp at h

/-- A levy charge is never negative (rates and wages are taken at least 0). -/
theorem chargeOf_due_nonneg (l : EmployerLevy) (f : EmployerFacts) (w : Int) (e : String) (c : Charge)
    (h : l.chargeOf f w e = some c) (hr : ∀ t, 0 ≤ t → 0 ≤ l.round.ofTicks t) : 0 ≤ c.due := by
  unfold chargeOf at h
  split at h
  · simp at h; subst h
    apply charge_nonneg
    apply hr
    apply Int.mul_nonneg (pos_nonneg _)
    split
    · exact Int.le_min.mpr ⟨pos_nonneg _, by omega⟩
    · exact pos_nonneg _
  · simp at h

end EmployerLevy

end TaxKernel.Global
