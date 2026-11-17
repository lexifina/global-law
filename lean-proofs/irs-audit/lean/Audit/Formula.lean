/-
  The statutory inflation adjustment of Title 26, as one computable function.

  §1(f)(3) (as amended by Pub. L. 115-97): the cost-of-living adjustment (COLA) for calendar year Y is the
  percentage by which the C-CPI-U for Y-1 exceeds "the CPI for calendar year 2016, multiplied by" the ratio
  C-CPI-U(2016)/CPI(2016) (§1(f)(3)(B)). A provision indexed "by substituting 'calendar year B' for 'calendar year
  2016' in subparagraph (A)(ii)" therefore uses
     B ≥ 2016 (via §1(f)(3)(C) when B > 2016):  ratio = C(Y-1) / C(B)
     B < 2016:                                  ratio = C(Y-1) · P(2016) / (P(B) · C(2016))
  where C(y), P(y) are the averages of the monthly C-CPI-U and CPI-U for the 12 months ending August 31 of y
  (§1(f)(4), §1(f)(6)(B)). The twelve-month averages enter only as ratios, so we work with twelve-month SUMS of the
  published 3-decimal index values, held as whole thousandths. All arithmetic is exact (Nat), so every result is a
  rational computation followed by the rounding rule the statute names.

  §1(f)(6)(A): the C-CPI-U values used for the COLA for year Y are "the latest values so published as of the date on
  which [BLS] publishes the initial value ... for the month of August for the preceding calendar year" — the vintage
  of the August (Y-1) release. `CPI.lean` holds those vintages (from ALFRED) and the latest values (BLS API).
-/
namespace TaxCode.Indexing

/-- A monthly index series: (year, month, value in thousandths of an index point). -/
abbrev Series := List (Nat × Nat × Nat)

/-- Value for a month, if published. -/
def Series.get? (s : Series) (y m : Nat) : Option Nat :=
  match s.find? (fun o => o.1 == y && o.2.1 == m) with
  | some o => some o.2.2
  | none => none

/-- The twelve months September (y-1) .. August y (§1(f)(4)). -/
def months12 (y : Nat) : List (Nat × Nat) :=
  [(y-1, 9), (y-1, 10), (y-1, 11), (y-1, 12), (y, 1), (y, 2), (y, 3), (y, 4), (y, 5), (y, 6), (y, 7), (y, 8)]

/-- Twelve-month sum ending August y; a missing month counts 0 (see `complete`). -/
def ysum (s : Series) (y : Nat) : Nat :=
  (months12 y).foldl (fun acc ym => acc + (s.get? ym.1 ym.2).getD 0) 0

/-- Every month of the twelve-month period is published. -/
def complete (s : Series) (y : Nat) : Bool :=
  (months12 y).all (fun ym => (s.get? ym.1 ym.2).isSome)

/-- Base year of an adjustment: a calendar year, or the medical care cost adjustment of §213(d)(10)(B)(ii). -/
inductive Base where
  | year (b : Nat)
  | medical
  deriving DecidableEq, Repr

/-- The index ratio num/den = 1 + COLA (§1(f)(3)) for calendar year `cy`, base `b`.
    `C` = C-CPI-U (the §1(f)(6)(A) vintage), `P` = CPI-U, `M` = medical C-CPI-U, `PM` = medical CPI-U. -/
def ratio (C P M PM : Series) (b : Base) (cy : Nat) : Nat × Nat :=
  match b with
  | .year by_ =>
    if 2016 ≤ by_ then (ysum C (cy - 1), ysum C by_)
    else (ysum C (cy - 1) * ysum P 2016, ysum P by_ * ysum C 2016)
  | .medical =>
    -- §213(d)(10)(B)(ii): medical C-CPI-U for August of the preceding year vs. the medical CPI for August 1996
    -- multiplied by the §1(f)(3)(B) amount C(2016)/P(2016)
    ((M.get? (cy - 1) 8).getD 0 * ysum P 2016, (PM.get? 1996 8).getD 0 * ysum C 2016)

/-- Rounding rules found in Title 26. -/
inductive Rnd where
  /-- "If any increase ... is not a multiple of $m, such increase shall be rounded to the next lowest multiple" -/
  | incDown (m : Nat)
  /-- "... such increase shall be rounded to the nearest multiple of $m" (a half rounds up) -/
  | incNear (m : Nat)
  /-- "If any amount as adjusted ... is not a multiple of $m, such amount shall be rounded to the next lowest multiple" -/
  | amtDown (m : Nat)
  /-- "... such amount shall be rounded to the nearest multiple of $m" (a half rounds up) -/
  | amtNear (m : Nat)
  /-- §6652(c)(7)(B), §6695(h)(2), §6721(f)(2), §6722(f)(2): amounts of at least `thr` round down to `big`,
      others down to `small` -/
  | pen (thr big small : Nat)
  /-- no statutory rounding: the exact amount, truncated to the unit (only used to bound the published figure) -/
  | none
  deriving DecidableEq, Repr

/-- nearest multiple of m to n/d, a half rounding up -/
def roundNear (n d m : Nat) : Nat := m * ((2 * n + m * d) / (2 * m * d))

/-- The adjusted amount: `base` increased by `base × COLA`, rounded by `r`. -/
def adjustND (base num den : Nat) : Rnd → Nat
  | .incDown m => base + m * (base * (num - den) / (den * m))
  | .incNear m => base + roundNear (base * (num - den)) den m
  | .amtDown m => m * (base * num / (den * m))
  | .amtNear m => roundNear (base * num) den m
  | .pen thr big small =>
      if thr * den ≤ base * num then big * (base * num / (den * big)) else small * (base * num / (den * small))
  | .none => base * num / den

def adjust (C P M PM : Series) (base : Nat) (b : Base) (cy : Nat) (r : Rnd) : Nat :=
  let q := ratio C P M PM b cy
  adjustND base q.1 q.2 r

/-- Several statutory amounts added before one rounding to the nearest m (§32(j)(2)(A): the §32(b)(2)(A) phaseout
    amount "after being increased under subparagraph (B)" [the joint-return $5,000], after indexing). -/
def adjustSumNear (C P M PM : Series) (parts : List (Nat × Nat)) (cy m : Nat) : Nat :=
  -- exact sum of base_i × num_i/den_i as one fraction
  let fr := parts.foldl (fun (acc : Nat × Nat) (p : Nat × Nat) =>
      let q := ratio C P M PM (.year p.2) cy
      (acc.1 * q.2 + p.1 * q.1 * acc.2, acc.2 * q.2)) (0, 1)
  roundNear fr.1 fr.2 m

/-- Tax (in cents) at each bracket top of a §1 rate table: rates in percent, tops in dollars. -/
def bracketTaxes : List Nat → List Nat → List Nat
  | rates, tops =>
    let rec go : List Nat → List Nat → Nat → Nat → List Nat
      | r :: rs, t :: ts, prev, acc => (acc + r * (t - prev)) :: go rs ts t (acc + r * (t - prev))
      | _, _, _, _ => []
    go rates tops 0 0

/-! ## General facts about the rounding rules (for all inputs) -/

theorem roundNear_dvd (n d m : Nat) : m ∣ roundNear n d m := ⟨_, rfl⟩

/-- Rounding the increase down to a multiple of m: the result is base plus a multiple of m. So a base that is not a
    multiple of m yields only amounts congruent to base mod m — e.g. a $175 base rounded by $10 increases ends in 5. -/
theorem incDown_mod (base num den m : Nat) :
    (adjustND base num den (.incDown m)) % m = base % m := by
  simp [adjustND, Nat.add_mul_mod_self_left]

theorem incNear_mod (base num den m : Nat) :
    (adjustND base num den (.incNear m)) % m = base % m := by
  simp [adjustND, roundNear, Nat.mul_assoc, Nat.add_mul_mod_self_left]

/-- When the base is a multiple of m, rounding the increase down and rounding the amount down agree. -/
theorem incDown_eq_amtDown (k num den m : Nat) (hm : 0 < m) (hd : 0 < den) (h : den ≤ num) :
    adjustND (m * k) num den (.incDown m) = adjustND (m * k) num den (.amtDown m) := by
  simp only [adjustND]
  have e1 : m * k * num = m * k * (num - den) + den * m * k := by
    have : num = (num - den) + den := (Nat.sub_add_cancel h).symm
    conv => lhs; rw [this]
    rw [Nat.mul_add, Nat.mul_comm (m * k) den, Nat.mul_assoc den m k]
  rw [e1, Nat.add_mul_div_left _ _ (Nat.mul_pos hd hm)]
  rw [Nat.mul_add, Nat.add_comm]

end TaxCode.Indexing
