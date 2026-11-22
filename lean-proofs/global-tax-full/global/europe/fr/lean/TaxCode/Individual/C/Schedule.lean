import TaxCode.Individual.Household

/-!
# §1(j)(2): the 2025 rate schedules

IRC §1(j)(2)(A)–(D) (as amended by Pub. L. 119-21 §70101) prints four seven-bracket tables ("If taxable income is:
Over X but not over Y — The tax is: $B, plus R% of the excess over X"); §1(j)(3)(B) has the Secretary re-index them
each year. The 2025 tables are Rev. Proc. 2024-40 §2.01, Tables 1–4 (pp. 5–7). Pub. L. 119-21 §70101 made §1(j)
permanent and changed the indexing of the 12%/22% boundaries, but §70101(c) applies those amendments only "to taxable
years beginning after December 31, 2025": **no 2025 bracket changed** (see FINDINGS.md, F1).

Each table is copied in the statute's own shape: a chain of "over X but not over Y" rows, each with the base amount
printed in the Rev. Proc. (in cents, since some are printed with cents, e.g. $1,192.50). Amounts here are *cents*:
the rates are whole percents, so R% of a whole-dollar excess is exactly R cents per dollar. `scheduleTax` rounds to
whole dollars half up, the rule of the Form 1040 instructions ("drop amounts under 50 cents and increase amounts from
50 to 99 cents to the next dollar", 2025 Instructions for Form 1040, "Rounding Off to Whole Dollars").

The surviving-spouse column uses the joint table (§1(j)(2)(A) heading "Married individuals filing joint returns and
surviving spouses").
-/

namespace TaxCode.Individual.C
open TaxCode.Individual

/-- A seven-rate table in the shape of §1(j)(2): the tops of the 10%, 12%, 22%, 24%, 32% and 35% rows (`e1`…`e6`,
whole dollars) and the base amount printed on the row that starts at each of them (`b1`…`b6`, cents). -/
structure Sched where
  e1 : Int
  e2 : Int
  e3 : Int
  e4 : Int
  e5 : Int
  e6 : Int
  b1 : Int
  b2 : Int
  b3 : Int
  b4 : Int
  b5 : Int
  b6 : Int
  deriving Repr, DecidableEq

/-- The tax in cents on whole-dollar taxable income `x`, read off the table row by row. Taxable income of zero or
less gives zero (the table's first row "Not over $X: 10% of taxable income" would give a negative tax for a negative
taxable income, which §63 never produces). -/
def Sched.cents (s : Sched) (x : Int) : Int :=
  if x ≤ 0 then 0
  else if x ≤ s.e1 then 10 * x
  else if x ≤ s.e2 then s.b1 + 12 * (x - s.e1)
  else if x ≤ s.e3 then s.b2 + 22 * (x - s.e2)
  else if x ≤ s.e4 then s.b3 + 24 * (x - s.e3)
  else if x ≤ s.e5 then s.b4 + 32 * (x - s.e4)
  else if x ≤ s.e6 then s.b5 + 35 * (x - s.e5)
  else s.b6 + 37 * (x - s.e6)

/-- A table is *well formed* when its rows are in order and each printed base amount is exactly the tax at the top of
the row before (so the schedule has no jump at any bracket edge). -/
def Sched.Ok (s : Sched) : Prop :=
  0 < s.e1 ∧ s.e1 < s.e2 ∧ s.e2 < s.e3 ∧ s.e3 < s.e4 ∧ s.e4 < s.e5 ∧ s.e5 < s.e6 ∧
  s.b1 = 10 * s.e1 ∧ s.b2 = s.b1 + 12 * (s.e2 - s.e1) ∧ s.b3 = s.b2 + 22 * (s.e3 - s.e2) ∧
  s.b4 = s.b3 + 24 * (s.e4 - s.e3) ∧ s.b5 = s.b4 + 32 * (s.e5 - s.e4) ∧ s.b6 = s.b5 + 35 * (s.e6 - s.e5)

instance (s : Sched) : Decidable s.Ok := by unfold Sched.Ok; infer_instance

/-! ## The 2025 tables (Rev. Proc. 2024-40 §2.01) -/

/-- §1(j)(2)(C), unmarried individuals: Rev. Proc. 2024-40 §2.01 Table 3 (p. 6). -/
def single2025 : Sched :=
  ⟨11925, 48475, 103350, 197300, 250525, 626350, 119250, 557850, 1765100, 4019900, 5723100, 18876975⟩

/-- §1(j)(2)(A), married filing jointly and surviving spouses: Rev. Proc. 2024-40 §2.01 Table 1 (p. 5). -/
def mfj2025 : Sched :=
  ⟨23850, 96950, 206700, 394600, 501050, 751600, 238500, 1115700, 3530200, 8039800, 11446200, 20215450⟩

/-- §1(j)(2)(D), married filing separately: Rev. Proc. 2024-40 §2.01 Table 4 (p. 7). -/
def mfs2025 : Sched :=
  ⟨11925, 48475, 103350, 197300, 250525, 375800, 119250, 557850, 1765100, 4019900, 5723100, 10107725⟩

/-- §1(j)(2)(B), heads of households: Rev. Proc. 2024-40 §2.01 Table 2 (pp. 5–6). -/
def hoh2025 : Sched :=
  ⟨17000, 64850, 103350, 197300, 250500, 626350, 170000, 744200, 1591200, 3846000, 5548400, 18703150⟩

/-- The table for each filing status; a qualifying surviving spouse uses the joint table (§1(j)(2)(A), §2(a)). -/
def sched : Filing → Sched
  | .single => single2025
  | .mfj => mfj2025
  | .qss => mfj2025
  | .mfs => mfs2025
  | .hoh => hoh2025

/-- **Every printed base amount in Rev. Proc. 2024-40 Tables 1–4 is the exact tax at the top of the previous row.**
(A typo in any of the 24 printed numbers would make this fail.) -/
theorem sched_ok (f : Filing) : (sched f).Ok := by cases f <;> decide

/-- Tax from the rate schedule in cents (exact). -/
def scheduleCents (f : Filing) (ti : Int) : Int := (sched f).cents ti

/-- Tax from the rate schedule in whole dollars, rounded half up as the Form 1040 instructions direct. -/
def scheduleTax (f : Filing) (ti : Int) : Int := roundDollar (scheduleCents f ti) 100

/-! ## Tests: Rev. Proc. 2024-40 row values and the 2025 Tax Computation Worksheet -/

-- Each row's printed base is the tax at the row's start (Rev. Proc. 2024-40 §2.01, Tables 1-4).
#guard scheduleCents .single 48475 = 557850        -- $5,578.50 (Table 3)
#guard scheduleCents .single 626350 = 18876975     -- $188,769.75 (Table 3)
#guard scheduleCents .mfj 751600 = 20215450        -- $202,154.50 (Table 1)
#guard scheduleCents .hoh 626350 = 18703150        -- $187,031.50 (Table 2)
#guard scheduleCents .mfs 375800 = 10107725        -- $101,077.25 (Table 4)
#guard scheduleCents .qss 394600 = 8039800         -- $80,398 (Table 1, surviving spouses)

/-- The 2025 Tax Computation Worksheet (2025 Instructions for Form 1040, p. 80) for taxable income of $100,000 or more:
taxable income × the row's rate − a printed subtraction amount (in cents). -/
def tcwCents (f : Filing) (x : Int) : Int :=
  match f with
  | .single =>
    if x ≤ 103350 then 22 * x - 508600 else if x ≤ 197300 then 24 * x - 715300
    else if x ≤ 250525 then 32 * x - 2293700 else if x ≤ 626350 then 35 * x - 3045275 else 37 * x - 4297975
  | .mfj | .qss =>
    if x ≤ 206700 then 22 * x - 1017200 else if x ≤ 394600 then 24 * x - 1430600
    else if x ≤ 501050 then 32 * x - 4587400 else if x ≤ 751600 then 35 * x - 6090550 else 37 * x - 7593750
  | .mfs =>
    if x ≤ 103350 then 22 * x - 508600 else if x ≤ 197300 then 24 * x - 715300
    else if x ≤ 250525 then 32 * x - 2293700 else if x ≤ 375800 then 35 * x - 3045275 else 37 * x - 3796875
  | .hoh =>
    if x ≤ 103350 then 22 * x - 682500 else if x ≤ 197300 then 24 * x - 889200
    else if x ≤ 250500 then 32 * x - 2467600 else if x ≤ 626350 then 35 * x - 3219100 else 37 * x - 4471800

/-- **The Tax Computation Worksheet agrees with the statutory schedule to the cent, for every taxable income of
$100,000 or more and every filing status** (all 20 printed subtraction amounts are right). -/
theorem tcw_eq_schedule (f : Filing) (x : Int) (hx : 100000 ≤ x) : tcwCents f x = scheduleCents f x := by
  cases f <;> simp only [tcwCents, scheduleCents, sched, Sched.cents, single2025, mfj2025, mfs2025, hoh2025] <;>
    repeat' split
  all_goals omega

/-! ## Properties of every well-formed table -/

/-- On a well-formed table, `x ≤ y` (with `0 ≤ x`) raises the tax by at least 10 and at most 37 cents a dollar. -/
theorem Sched.lipschitz (s : Sched) (h : s.Ok) (x y : Int) (hx : 0 ≤ x) (hxy : x ≤ y) :
    10 * (y - x) ≤ s.cents y - s.cents x ∧ s.cents y - s.cents x ≤ 37 * (y - x) := by
  unfold Sched.Ok at h
  unfold Sched.cents
  repeat' split
  all_goals omega

/-- Below the top of the 22% row the marginal rate is at most 22%. -/
theorem Sched.lipschitz22 (s : Sched) (h : s.Ok) (x y : Int) (hx : 0 ≤ x) (hxy : x ≤ y) (hy : y ≤ s.e3) :
    s.cents y - s.cents x ≤ 22 * (y - x) := by
  unfold Sched.Ok at h
  unfold Sched.cents
  repeat' split
  all_goals omega

/-- The marginal rate *is* 37% above the last edge: the bound in `Sched.lipschitz` is attained. -/
theorem Sched.top_rate (s : Sched) (h : s.Ok) (x : Int) (hx : s.e6 ≤ x) : s.cents (x + 1) = s.cents x + 37 := by
  unfold Sched.Ok at h
  unfold Sched.cents
  repeat' split
  all_goals omega

/-! ## The 2025 schedules -/

/-- **Marginal rate never exceeds 37%, for every filing status** (and is never below 10% on positive income): for
any `0 ≤ x ≤ y`, the schedule tax on `y` exceeds that on `x` by between 10 and 37 cents per extra dollar. -/
theorem scheduleCents_marginal (f : Filing) (x y : Int) (hx : 0 ≤ x) (hxy : x ≤ y) :
    10 * (y - x) ≤ scheduleCents f y - scheduleCents f x ∧
      scheduleCents f y - scheduleCents f x ≤ 37 * (y - x) :=
  Sched.lipschitz _ (sched_ok f) x y hx hxy

/-- In whole dollars: one more dollar of taxable income never costs more than one dollar of tax, nor less than zero
(generalises `Legal.USTax.scheduleTax_step` to all five statuses and to the rounded amount). -/
theorem scheduleTax_step (f : Filing) (x : Int) (hx : 0 ≤ x) :
    scheduleTax f x ≤ scheduleTax f (x + 1) ∧ scheduleTax f (x + 1) ≤ scheduleTax f x + 1 := by
  have h := scheduleCents_marginal f x (x + 1) hx (by omega)
  unfold scheduleTax roundDollar
  omega

/-- Monotone over any distance: more taxable income never means less schedule tax. -/
theorem scheduleTax_mono (f : Filing) (x y : Int) (hx : 0 ≤ x) (hxy : x ≤ y) :
    scheduleTax f x ≤ scheduleTax f y := by
  have h := scheduleCents_marginal f x y hx hxy
  unfold scheduleTax roundDollar
  omega

/-- The 37% bound is attained for every status (so it is the maximum, not just a bound). -/
theorem scheduleCents_top (f : Filing) : ∃ x, scheduleCents f (x + 1) = scheduleCents f x + 37 :=
  ⟨(sched f).e6, Sched.top_rate _ (sched_ok f) _ (Int.le_refl _)⟩

/-- Below $100,000 (the Tax Table range) the marginal rate never exceeds 22%, for every status. -/
theorem scheduleCents_below100k (f : Filing) (x y : Int) (hx : 0 ≤ x) (hxy : x ≤ y) (hy : y ≤ 100000) :
    scheduleCents f y - scheduleCents f x ≤ 22 * (y - x) := by
  have h3 : 100000 ≤ (sched f).e3 := by cases f <;> decide
  exact Sched.lipschitz22 _ (sched_ok f) x y hx hxy (by omega)

/-- §1(f)(8)/§1(j)(2): the joint table's 10%, 12%, 22% and 24% edges are exactly twice the single table's (no
marriage penalty up to $394,600), but the 32% and 35% edges are not: the joint 35% row ends at $751,600, 1.2 times
the single $626,350. -/
theorem mfj_double_single_lower :
    mfj2025.e1 = 2 * single2025.e1 ∧ mfj2025.e2 = 2 * single2025.e2 ∧ mfj2025.e3 = 2 * single2025.e3 ∧
      mfj2025.e4 = 2 * single2025.e4 ∧ mfj2025.e5 = 2 * single2025.e5 ∧ mfj2025.e6 < 2 * single2025.e6 := by
  decide

/-- So two equal single earners pay no marriage penalty up to $375,800 each … -/
theorem no_marriage_penalty (x : Int) (hx : 0 ≤ x) (h : x ≤ 375800) :
    scheduleCents .mfj (2 * x) = 2 * scheduleCents .single x := by
  simp only [scheduleCents, sched, Sched.cents, single2025, mfj2025]
  repeat' split
  all_goals omega

/-- … but at $700,000 each the joint return costs $10,022 more than two single returns. -/
theorem marriage_penalty_700k :
    scheduleCents .mfj 1400000 - 2 * scheduleCents .single 700000 = 1002200 := by decide

/-- Married filing separately is exactly half the joint table at every income (§1(j)(2)(D) vs (A) as indexed). -/
theorem mfs_half_mfj (x : Int) (hx : 0 ≤ x) : 2 * scheduleCents .mfs x = scheduleCents .mfj (2 * x) := by
  simp only [scheduleCents, sched, Sched.cents, mfs2025, mfj2025]
  repeat' split
  all_goals omega

end TaxCode.Individual.C
