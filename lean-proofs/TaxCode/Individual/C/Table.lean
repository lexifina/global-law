import TaxCode.Individual.C.Schedule

/-!
# §3: the Tax Table, and how far it departs from the §1(j) schedule

§3(a)(1) imposes, "in lieu of the tax imposed by section 1", a tax "determined under tables … prescribed by the
Secretary", whose amounts "shall be computed on the basis of the rates prescribed by section 1"; §3(c) treats it as
tax imposed by §1. The statute does not say *how* the table is built. The 2025 Tax Table (2025 Instructions for Form
1040, pp. 68–79) uses lines "At least X but less than Y": $5/$10/$10 lines up to $25, $25 lines up to $3,000, and $50
lines from $3,000 to $100,000; the tax shown is the schedule tax on the line's midpoint, rounded half up (every row
checked below reproduces this). "If your taxable income is less than $100,000, you must use the Tax Table" (Line 16
instructions); from $100,000 the Tax Computation Worksheet applies, which equals the schedule (`tcw_eq_schedule`).

`line16Tax` is that rule: the Table below $100,000, the schedule from $100,000.
-/

namespace TaxCode.Individual.C
open TaxCode.Individual

/-- The table with every edge and base doubled: its tax on `m` half-dollars is twice the schedule tax on `m/2`
dollars, so midpoints such as $12.50 can be evaluated exactly. -/
def Sched.dbl (s : Sched) : Sched :=
  ⟨2 * s.e1, 2 * s.e2, 2 * s.e3, 2 * s.e4, 2 * s.e5, 2 * s.e6,
   2 * s.b1, 2 * s.b2, 2 * s.b3, 2 * s.b4, 2 * s.b5, 2 * s.b6⟩

theorem Sched.dbl_ok (s : Sched) (h : s.Ok) : s.dbl.Ok := by
  unfold Sched.Ok Sched.dbl at *
  simp only at *
  omega

/-- On whole dollars the doubled table is exactly twice the schedule. -/
theorem Sched.dbl_cents (s : Sched) (x : Int) : s.dbl.cents (2 * x) = 2 * s.cents x := by
  unfold Sched.cents Sched.dbl
  simp only
  repeat' split
  all_goals omega

/-- Twice the midpoint of the Tax Table line containing `ti` (0 ≤ ti < 100,000): lines 0–5, 5–15, 15–25, then $25
lines to $3,000, then $50 lines. -/
def midpoint2 (ti : Int) : Int :=
  if ti < 5 then 5
  else if ti < 15 then 20
  else if ti < 25 then 40
  else if ti < 3000 then 2 * (ti / 25 * 25) + 25
  else 2 * (ti / 50 * 50) + 50

/-- The Tax Table entry: the schedule tax on the line's midpoint, rounded half up to whole dollars. -/
def tableTax (f : Filing) (ti : Int) : Int := roundDollar ((sched f).dbl.cents (midpoint2 ti)) 200

/-- Form 1040 line 16, ordinary case: the Tax Table below $100,000, the schedule (Tax Computation Worksheet) from
$100,000. -/
def line16Tax (f : Filing) (ti : Int) : Int := if ti < 100000 then tableTax f ti else scheduleTax f ti

/-! ## Tests against the printed 2025 Tax Table (2025 Instructions for Form 1040) -/

-- p. 68, first column (all four statuses alike): 0–5 → 0, 5–15 → 1, 15–25 → 2, 25–50 → 4, 50–75 → 6, 75–100 → 9,
-- 100–125 → 11; 975–1,000 → 99; second column 1,000–1,025 → 101, 1,025–1,050 → 104; third column 2,975–3,000 → 299.
#guard [0, 7, 20, 30, 60, 80, 110, 990, 1010, 1030, 2990].map (tableTax .single) =
  [0, 1, 2, 4, 6, 9, 11, 99, 101, 104, 299]
#guard [0, 7, 20, 30, 60, 80, 110, 990, 1010, 1030, 2990].map (tableTax .hoh) =
  [0, 1, 2, 4, 6, 9, 11, 99, 101, 104, 299]
-- p. 69: 3,000–3,050 → 303 (all); 11,900–11,950 → 1,193 (all).
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 3000) = [303, 303, 303, 303]
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 11949) = [1193, 1193, 1193, 1193]
-- p. 70: 14,000–14,050 → 1,445 / 1,403 / 1,445 / 1,403; 17,000–17,050 → 1,805 / 1,703 / 1,805 / 1,703;
-- 20,000–20,050 → 2,165 / 2,003 / 2,165 / 2,063 (columns Single, MFJ, MFS, HoH).
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 14000) = [1445, 1403, 1445, 1403]
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 17025) = [1805, 1703, 1805, 1703]
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 20049) = [2165, 2003, 2165, 2063]
-- p. 71: 23,850–23,900 → 2,627 / 2,388 / 2,627 / 2,525.
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 23850) = [2627, 2388, 2627, 2525]
-- p. 68 worked example: joint return, taxable income $25,300, tax $2,562 (the $25,300–25,350 line).
#guard tableTax .mfj 25300 = 2562
#guard tableTax .qss 25300 = 2562
-- p. 74: 48,450–48,500 → 5,579 / 5,340 / 5,579 / 5,477; 48,500–48,550 → 5,590 / 5,346 / 5,590 / 5,483;
-- 48,550–48,600 → 5,601 / 5,352 / 5,601 / 5,489; 50,000–50,050 → 5,920 / 5,526 / 5,920 / 5,663.
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 48450) = [5579, 5340, 5579, 5477]
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 48500) = [5590, 5346, 5590, 5483]
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 48599) = [5601, 5352, 5601, 5489]
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 50000) = [5920, 5526, 5920, 5663]
-- p. 75: 64,800–64,850 → 9,176 / 7,302 / 9,176 / 7,439; 64,850–64,900 → 9,187 / 7,308 / 9,187 / 7,448.
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 64800) = [9176, 7302, 9176, 7439]
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 64850) = [9187, 7308, 9187, 7448]
-- p. 77: 75,000–75,050 → 11,420 / 8,526 / 11,420 / 9,681.
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 75000) = [11420, 8526, 11420, 9681]
-- p. 79: 96,900–96,950 → 16,238 / 11,154 / 16,238 / 14,499; 96,950–97,000 → 16,249 / 11,163 / 16,249 / 14,510;
-- 99,950–100,000 → 16,909 / 11,823 / 16,909 / 15,170.
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 96900) = [16238, 11154, 16238, 14499]
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 96950) = [16249, 11163, 16249, 14510]
#guard [Filing.single, .mfj, .mfs, .hoh].map (tableTax · 99999) = [16909, 11823, 16909, 15170]

/-! ## How far the Table can be from the schedule -/

theorem midpoint2_near (ti : Int) (h0 : 0 ≤ ti) (h1 : ti < 100000) :
    0 ≤ midpoint2 ti ∧ midpoint2 ti ≤ 199950 ∧ midpoint2 ti - 2 * ti ≤ 50 ∧ 2 * ti - midpoint2 ti ≤ 48 := by
  unfold midpoint2
  repeat' split
  all_goals omega

/-- **Table vs schedule, general bound.** For any well-formed table whose 22% row reaches $100,000, the Table amount
is within $6 of the rounded schedule tax for every taxable income under $100,000. -/
theorem Sched.table_near (s : Sched) (h : s.Ok) (h3 : 100000 ≤ s.e3) (ti : Int) (h0 : 0 ≤ ti) (h1 : ti < 100000) :
    roundDollar (s.dbl.cents (midpoint2 ti)) 200 - roundDollar (s.cents ti) 100 ≤ 6 ∧
      roundDollar (s.cents ti) 100 - roundDollar (s.dbl.cents (midpoint2 ti)) 200 ≤ 6 := by
  have hd := Sched.dbl_ok s h
  have hm := midpoint2_near ti h0 h1
  have he : s.dbl.e3 = 2 * s.e3 := rfl
  have h2 := Sched.dbl_cents s ti
  rcases Int.le_total (midpoint2 ti) (2 * ti) with hle | hle
  · have := Sched.lipschitz22 s.dbl hd _ _ hm.1 hle (by omega)
    have := (Sched.lipschitz s.dbl hd _ _ hm.1 hle).1
    unfold roundDollar
    omega
  · have := Sched.lipschitz22 s.dbl hd _ _ (by omega) hle (by omega)
    have := (Sched.lipschitz s.dbl hd _ _ (by omega) hle).1
    unfold roundDollar
    omega

/-- **The 2025 Tax Table is never more than $6 above, nor more than $6 below, the schedule**, for every filing status
and every taxable income under $100,000. -/
theorem table_within_6 (f : Filing) (ti : Int) (h0 : 0 ≤ ti) (h1 : ti < 100000) :
    tableTax f ti - scheduleTax f ti ≤ 6 ∧ scheduleTax f ti - tableTax f ti ≤ 6 := by
  have h3 : 100000 ≤ (sched f).e3 := by cases f <;> decide
  exact Sched.table_near _ (sched_ok f) h3 ti h0 h1

/-- The +$6 is attained: single, $48,500 — the Table says $5,590 (2025 Tax Table p. 74), the schedule $5,584. -/
theorem table_plus6 : tableTax .single 48500 = 5590 ∧ scheduleTax .single 48500 = 5584 := by decide

/-- The joint, separate and head-of-household columns reach +$6 too ($96,950, $48,500, $64,850). -/
theorem table_plus6_all :
    tableTax .mfj 96950 - scheduleTax .mfj 96950 = 6 ∧ tableTax .mfs 48500 - scheduleTax .mfs 48500 = 6 ∧
      tableTax .hoh 64850 - scheduleTax .hoh 64850 = 6 := by decide

/-- Below, the worst case is −$5 (single $48,498: Table $5,579, schedule $5,584). -/
theorem table_minus5 : scheduleTax .single 48498 - tableTax .single 48498 = 5 ∧
    scheduleTax .mfj 96998 - tableTax .mfj 96998 = 5 ∧ scheduleTax .hoh 64898 - tableTax .hoh 64898 = 5 := by
  decide

theorem midpoint2_cases (ti : Int) :
    (ti < 5 ∧ midpoint2 ti = 5) ∨ (5 ≤ ti ∧ ti < 15 ∧ midpoint2 ti = 20) ∨ (15 ≤ ti ∧ ti < 25 ∧ midpoint2 ti = 40) ∨
      (25 ≤ ti ∧ ti < 3000 ∧ midpoint2 ti = 2 * (ti / 25 * 25) + 25) ∨
      (3000 ≤ ti ∧ midpoint2 ti = 2 * (ti / 50 * 50) + 50) := by
  unfold midpoint2
  repeat' split
  all_goals omega

/-- **The lower bound is exactly −$5 for every status**: the −$6 the general argument allows never happens. (Proved by
exhausting the piecewise-linear cases with `omega`, which reasons about the remainders of the midpoint tax.) -/
theorem table_ge_minus5 (f : Filing) (ti : Int) (h0 : 0 ≤ ti) (h1 : ti < 100000) :
    scheduleTax f ti - tableTax f ti ≤ 5 := by
  have hm := midpoint2_cases ti
  unfold tableTax scheduleTax scheduleCents roundDollar
  generalize midpoint2 ti = m at *
  cases f <;>
  · simp only [sched, Sched.dbl, Sched.cents, single2025, mfj2025, mfs2025, hoh2025]
    repeat' split
    all_goals omega

/-! ## The Table's own steps -/

theorem midpoint2_mono (x : Int) (h0 : 0 ≤ x) (h1 : x + 1 < 100000) :
    midpoint2 x ≤ midpoint2 (x + 1) ∧ midpoint2 (x + 1) - midpoint2 x ≤ 100 := by
  unfold midpoint2
  repeat' split
  all_goals omega

/-- **The Table is monotone and one more dollar never costs more than $11**: every Table line is flat, and the jump
from one line to the next is at most $11 (22% of $50). Across the $100,000 switch to the worksheet the step is also
at most $11 (it is $5 for single filers: $16,909 → $16,914). -/
theorem line16Tax_step (f : Filing) (x : Int) (h0 : 0 ≤ x) :
    line16Tax f x ≤ line16Tax f (x + 1) ∧ line16Tax f (x + 1) ≤ line16Tax f x + 11 := by
  have hok := Sched.dbl_ok _ (sched_ok f)
  have h3 : 100000 ≤ (sched f).e3 := by cases f <;> decide
  have he : (sched f).dbl.e3 = 2 * (sched f).e3 := rfl
  unfold line16Tax
  by_cases hx : x + 1 < 100000
  · rw [if_pos (by omega : x < 100000), if_pos hx]
    have hm := midpoint2_mono x h0 hx
    have hn := midpoint2_near x h0 (by omega)
    have := Sched.lipschitz22 _ hok _ _ hn.1 hm.1 (by have := midpoint2_near (x+1) (by omega) hx; omega)
    have := (Sched.lipschitz _ hok _ _ hn.1 hm.1).1
    unfold tableTax roundDollar
    omega
  · by_cases hx' : x < 100000
    · rw [if_pos hx', if_neg hx]
      obtain rfl : x = 99999 := by omega
      rw [show (99999 : Int) + 1 = 100000 by rfl]
      have hn := midpoint2_near 99999 (by omega) (by omega)
      have hmid : midpoint2 99999 = 199950 := by decide
      have h2 : (sched f).dbl.cents 200000 = 2 * (sched f).cents 100000 := Sched.dbl_cents _ 100000
      have := Sched.lipschitz22 _ hok 199950 200000 (by omega) (by omega) (by omega)
      have := (Sched.lipschitz _ hok 199950 200000 (by omega) (by omega)).1
      unfold tableTax scheduleTax scheduleCents roundDollar
      rw [hmid]
      omega
    · rw [if_neg hx', if_neg hx]
      have := scheduleTax_step f x h0
      omega

/-- The $11 is attained (single, $48,549 → $48,550: $5,590 → $5,601). -/
theorem line16Tax_jump11 : line16Tax .single 48550 - line16Tax .single 48549 = 11 := by decide

end TaxCode.Individual.C
