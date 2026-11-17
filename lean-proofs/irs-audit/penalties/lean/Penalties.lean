/-
  Civil tax penalties whose amount or trigger the Internal Revenue Code fixes mechanically, written from the words
  of the statute in force for the years concerned (US Code history, ~/irs-audit/tools/usc_at.sh). Money is in cents
  (Nat), percentages are exact fractions: nothing is rounded except where the statute rounds.

  §6662(a)  "there shall be added to the tax an amount equal to 20 percent of the portion of the underpayment to which
            this section applies."
  §6662(b)  (flush) "This section shall not apply to any portion of an underpayment on which a penalty is imposed under
            section 6663."
  §6662(d)(1)(A) "there is a substantial understatement of income tax for any taxable year if the amount of the
            understatement for the taxable year exceeds the greater of (i) 10 percent of the tax required to be shown on
            the return for the taxable year, or (ii) $5,000."
  §6662(d)(1)(B) corporations: before the American Jobs Creation Act of 2004 "the greater of 10 percent ... or $10,000";
            for taxable years beginning after 22 October 2004 "exceeds the lesser of (i) 10 percent of the tax required to
            be shown on the return for the taxable year (or, if greater, $10,000), or (ii) $10,000,000."
  §6662(d)(1)(C) (taxable years after 2017) taxpayers claiming a §199A deduction: "5 percent" for "10 percent".
  §6662(h)(1) "the first paragraph of this section shall be applied with respect to such portion by substituting
            '40 percent' for '20 percent'."  (Also §6662(i)(1) and §6662(j)(3): 40 percent.)
  §6663(a)  "there shall be added to the tax an amount equal to 75 percent of the portion of the underpayment which is
            attributable to fraud."
  §6651(a)(1) "5 percent of the amount of such tax if the failure is for not more than 1 month, with an additional
            5 percent for each additional month or fraction thereof during which such failure continues, not exceeding
            25 percent in the aggregate"; (a)(2), (a)(3): "0.5 percent ... not exceeding 25 percent in the aggregate".
  §6651(a) flush: if a return is not filed within 60 days of its due date, the (a)(1) addition "shall not be less than
            the lesser of $[100/135/205/435, indexed under (j)] or 100 percent of the amount required to be shown as tax".
  §6651(c)(1) "the amount of the addition under paragraph (1) of subsection (a) shall be reduced by the amount of the
            addition under paragraph (2) of subsection (a) for any month (or fraction thereof) to which an addition to
            tax applies under both paragraphs (1) and (2)."
  §6651(f)  fraudulent failure to file: "15 percent" for "5 percent" and "75 percent" for "25 percent".
  §6654(e)(1) no addition if the tax (after the §31 credit) "is less than $1,000" ($500 for taxable years before 1998).
-/
namespace Pen

/-- `p` (cents) equals `num/den` of `base` (cents) up to `tol` cents: |p·den − num·base| ≤ tol·den. -/
def near (p num den base tol : Nat) : Bool :=
  let a := p * den; let b := num * base
  (if a ≥ b then a - b else b - a) ≤ tol * den

/-- `p` is at most `num/den` of `base`, up to `tol` cents. -/
def atMost (p num den base tol : Nat) : Bool := p * den ≤ num * base + tol * den

/-! ### §6662 -/
def acc20 (u : Nat) : Nat := u * 20 / 100
def acc40 (u : Nat) : Nat := u * 40 / 100
def fraud75 (u : Nat) : Nat := u * 75 / 100

/-- §6662(d)(1)(A) (individuals): understatement `u`, tax required to be shown `t`, both in cents; `pct` is 10
  (5 under (d)(1)(C) for §199A claimants after 2017). Exceeds the greater of pct% of t or $5,000. -/
def substantialIndiv (pct u t : Nat) : Bool := decide (100 * u > pct * t) && decide (u > 500000)

/-- §6662(d)(1)(B) (corporations), by taxable year: `post2004` = taxable year beginning after 22 Oct 2004. -/
def substantialCorp (post2004 : Bool) (u t : Nat) : Bool :=
  let greater10 := decide (10 * u > t) && decide (u > 1000000)       -- 10% or, if greater, $10,000
  if post2004 then greater10 || decide (u > 1000000000)             -- ... or $10,000,000, whichever is less
  else greater10

/-- An understatement of at most $5,000 is never substantial for an individual, whatever the tax required. -/
theorem not_substantial_small (pct u t : Nat) (h : u ≤ 500000) : substantialIndiv pct u t = false := by
  unfold substantialIndiv
  have : decide (u > 500000) = false := by simp; omega
  simp [this]

/-- The §6662(b) ordering: the 20% and 75% portions are disjoint parts of one underpayment `d`, so their bases sum
  to at most `d`; hence 5·P(6662) + (4/3)·P(6663) ≤ d (cents, before rounding). -/
theorem disjoint_bases (x y d : Nat) (h : x + y ≤ d) : x * 20 * 5 + y * 75 * 4 / 3 ≤ d * 100 := by
  omega

/-! ### §6651 -/
/-- (a)(1) percentage for `m` months (or fractions) late: 5 per month, at most 25. -/
def ftfPct (m : Nat) : Nat := min (5 * m) 25
/-- (a)(2)/(a)(3) in tenths of a percent: 5 per month (0.5%), at most 250 (25%). -/
def ftpTenths (m : Nat) : Nat := min (5 * m) 250

/-- (a)(1) addition after the (c)(1) reduction, when (a)(2) runs on the same base for the same months. -/
def ftfReduced (m base : Nat) : Nat := base * ftfPct m / 100 - base * ftpTenths (min m 5) / 1000

/-- With (a)(2) running from the due date on the same base, the reduced (a)(1) addition is at most 22.5%. -/
theorem ftf_reduced_cap : ∀ m ∈ [1,2,3,4,5,6,12,60], ftfReduced m 100000 ≤ 22500 := by decide

/-- Minimum (a)(1) addition by calendar year in which the return was required to be filed (dollars), from the
  statute as amended (TEFRA 1982: $100; HAPA 2008: $135 for returns due after 2008; Pub. L. 114-27 (2015): $205 for
  returns due after 2015; Pub. L. 116-94 (2019): $435 for returns due after 2019) with the indexed amounts the IRS
  published under §6651(j) (2018-2019 $210; 2022 $435 ... 2026 $525). `none` before 1983. -/
def minimumFtf (dueYear : Nat) : Option Nat :=
  if dueYear < 1983 then none
  else if dueYear ≤ 2008 then some 100
  else if dueYear ≤ 2015 then some 135
  else if dueYear ≤ 2017 then some 205
  else if dueYear ≤ 2019 then some 210
  else if dueYear ≤ 2022 then some 435
  else if dueYear = 2023 then some 450
  else if dueYear = 2024 then some 485
  else if dueYear = 2025 then some 510
  else some 525

/-- The (a)(1) addition for a return more than 60 days late, base `b` cents: max(ftf, min(minimum, b)). -/
def ftfWithMin (dueYear m b : Nat) : Nat :=
  let f := b * ftfPct m / 100
  match minimumFtf dueYear with
  | none => f
  | some d => max f (min (d * 100) b)

/-- §6654(e)(1) threshold in dollars by taxable year. -/
def estThreshold (taxYear : Nat) : Nat := if taxYear ≥ 1998 then 1000 else 500

/-! ### Classification of one year of a notice of deficiency, as stated in an opinion -/
structure Row where
  id : String
  year : Nat
  defic : Nat                    -- cents
  pens : List (String × Nat)     -- section, cents
deriving Repr

def get? (r : Row) (s : String) : Option Nat := (r.pens.find? (·.1 == s)).map (·.2)
def has (r : Row) (s : String) : Bool := (get? r s).isSome

def isAcc (s : String) : Bool := s == "6662(a)" || s == "6662" || s == "6662(b)(1)" || s == "6662(b)(2)"
def isAcc40 (s : String) : Bool := s == "6662(h)" || s == "6662(i)" || s == "6662(j)" || s == "6662(h)(1)"
def isOld (s : String) : Bool :=
  s.startsWith "6653" || s.startsWith "6659" || s.startsWith "6661" || s.startsWith "6660" || s == "6651(a)"
    || s.startsWith "6655" || s.startsWith "6656" || s.startsWith "6662A" || s.startsWith "6673"

/-- Outcome labels for the accuracy/fraud family on one year. Tolerance: $1 per amount (opinions round to dollars). -/
def classifyAcc (r : Row) : Option String :=
  let a := r.pens.filter (isAcc ·.1) |>.map (·.2) |>.foldl (· + ·) 0
  let h := r.pens.filter (isAcc40 ·.1) |>.map (·.2) |>.foldl (· + ·) 0
  let f := (get? r "6663").getD 0
  if a + h + f == 0 then none else
  let d := r.defic
  -- implied bases (×300 to stay in Nat): a/0.20 = 5a, h/0.40 = 2.5h, f/0.75 = (4/3)f
  let lhs := 1500 * a + 750 * h + 400 * f
  let tol := 300 * (500 + 250 + 133) + 300   -- $1 on each amount, scaled
  if h == 0 && f == 0 then
    if near a 20 100 d 100 then some "agrees: 20% of deficiency"
    else if atMost a 20 100 d 100 then some "consistent: 20% of part of the deficiency"
    else if near a 40 100 d 100 then some "FLAG: 6662(a) amount is 40% of deficiency"
    else some "FLAG: 6662(a) exceeds 20% of deficiency"
  else if a == 0 && f == 0 then
    if near h 40 100 d 100 then some "agrees: 40% of deficiency"
    else if atMost h 40 100 d 100 then some "consistent: 40% of part of the deficiency"
    else some "FLAG: 6662(h) exceeds 40% of deficiency"
  else if a == 0 && h == 0 then
    if near f 75 100 d 100 then some "agrees: 75% of deficiency"
    else if atMost f 75 100 d 100 then some "consistent: 75% of part of the deficiency"
    else some "FLAG: 6663 exceeds 75% of deficiency"
  else
    if lhs ≤ 300 * d + tol then
      (if lhs + tol ≥ 300 * d then some "agrees: mixed rates on disjoint portions summing to the deficiency"
       else some "consistent: mixed rates on disjoint portions within the deficiency")
    else some "FLAG: portions overlap (sum of implied bases exceeds deficiency)"

def classifyFtf (r : Row) : Option String :=
  match get? r "6651(a)(1)" with
  | none => none
  | some p =>
    let d := r.defic
    if near p 25 100 d 100 then some "agrees: 25% of deficiency (maximum)"
    else if near p 225 1000 d 100 then some "agrees: 22.5% of deficiency (25% less (c)(1) reduction)"
    else if atMost p 25 100 d 100 then some "consistent: within 25% of deficiency"
    else match minimumFtf (r.year + 1) with
      | some m => if near p 1 1 (min (m * 100) d) 100 then some "agrees: §6651(a) minimum"
                  else some "FLAG: 6651(a)(1) exceeds 25% of deficiency and is not the minimum"
      | none => some "FLAG: 6651(a)(1) exceeds 25% of deficiency"

def classifyFtp (r : Row) : Option String :=
  let p := (get? r "6651(a)(2)").getD 0 + (get? r "6651(a)(3)").getD 0
  if p == 0 then none
  else if atMost p 25 100 r.defic 100 then some "consistent: within 25% of deficiency"
  else some "FLAG: 6651(a)(2)/(3) exceeds 25% of deficiency"

def classifyFraudFtf (r : Row) : Option String :=
  match get? r "6651(f)" with
  | none => none
  | some p => if near p 75 100 r.defic 100 then some "agrees: 75% of deficiency (maximum)"
              else if atMost p 75 100 r.defic 100 then some "consistent: within 75% of deficiency"
              else some "FLAG: 6651(f) exceeds 75% of deficiency"

/-- (c)(1): an (a)(1) addition of exactly 25% together with an (a)(2) addition for the same year. -/
def classifyC1 (r : Row) : Option String :=
  match get? r "6651(a)(1)", get? r "6651(a)(2)" with
  | some p, some q => if q > 0 && near p 25 100 r.defic 100 then some "CHECK: (a)(1) at 25% alongside (a)(2) - (c)(1) reduction?" else none
  | _, _ => none

def classifyEst (r : Row) : Option String :=
  match get? r "6654" with
  | none => none
  | some _ =>
    if has r "6651(a)(1)" && r.defic < estThreshold r.year * 100 then
      some "CHECK: 6654 on a non-filer whose deficiency is under the (e)(1) threshold"
    else some "not checkable: needs installment dates and payments"

def classify (r : Row) : List (String × String) :=
  let one (k : String) (o : Option String) := o.map (fun v => (k, v))
  let base := [one "acc" (classifyAcc r), one "6651a1" (classifyFtf r), one "6651a2" (classifyFtp r),
               one "6651f" (classifyFraudFtf r), one "c1" (classifyC1 r), one "6654" (classifyEst r)].filterMap id
  let old := r.pens.filter (fun p => isOld p.1) |>.map (fun p => ("other", "out of scope: " ++ p.1))
  base ++ old

end Pen
