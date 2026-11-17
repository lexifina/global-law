/-
  Monthly applicable-federal-rate revenue rulings (IRB 1996-2026), checked against the statute.

  Rates are whole hundredths of a percent ("bp" below: 4.37% = 437); the §7520 and §642(c)(5) rates are whole tenths
  of a percent. A published rate stands for every true rate in [v - 1/2, v + 1/2) of its last printed digit, so every
  check asks whether SOME true input is consistent with the printed figures (an interval test, exact in Nat).
  A check fails only when no true input, under the stated rule, gives the printed figure.

  Rules (statute / regulation):
  * conv  : one rate, four compounding periods (annual, semiannual, quarterly, monthly): (1 + r_k/k)^k is the same
            effective yield for k = 1, 2, 4, 12 (Reg. 1.1274-4(b); equivalent rates).
  * mult  : 110/120/130/150/175% AFR = that percent of the AFR (semiannual compounding, Sec. 1274(b)(2)(B)),
            rounded to the bp.
  * s382  : Sec. 382(f)(1): long-term tax-exempt rate = the highest adjusted federal long-term rate for the current
            month and the two before it.
  * s7520 : Sec. 7520(a)(2): 120 percent of the federal mid-term rate (annual compounding, Reg. 20.7520-1(b)(1)),
            rounded to the nearest 2/10ths of 1 percent.
  * s42   : Sec. 42(b) (before 2008: (b)(2)(B)-(C)): percentages that give a present value of 70% / 30% over 10 years,
            credits at the end of each year, discounted to the end of year 1 at 72% of the average of the annual
            mid-term and long-term AFRs, compounded annually.
  * s642  : Reg. 1.642(c)-6(e)(4): one percent less than the highest annual average of the monthly Sec. 7520 rates
            for the three preceding calendar years, rounded to the nearest 2/10ths of 1 percent.
-/
namespace AFR

structure Row where
  a : Nat
  s : Nat
  q : Nat
  m : Nat
deriving Repr

structure Ruling where
  item : String
  y : Nat
  mo : Nat
  t1 : List Row      -- short: AFR,110,120,130; mid: AFR,110,120,130,150,175; long: AFR,110,120,130
  t2 : List Row      -- adjusted AFR short, mid, long
  adjLt : Option Nat
  ltEx : Option Nat
  l70 : Option Nat
  l30 : Option Nat
  r7520 : Option Nat
  deemed : Option Nat

/-- x/y ≤ u/v for positive denominators. -/
def qle (x y u v : Nat) : Bool := x * v ≤ u * y

/-- Effective annual growth factor of a nominal rate with k periods, rate = t/20000 (t = twice the bp value ± 1). -/
def growth (k t : Nat) : Nat × Nat := ((20000 * k + t) ^ k, (20000 * k) ^ k)

/-- conv: some effective yield is consistent with all four printed columns. -/
def conv (r : Row) : Bool :=
  let ks := [(1, r.a), (2, r.s), (4, r.q), (12, r.m)]
  let los := ks.map (fun (k, v) => growth k (2 * v - 1))
  let his := ks.map (fun (k, v) => growth k (2 * v + 1))
  los.all (fun lo => his.all (fun hi => qle lo.1 lo.2 hi.1 hi.2))

/-- mult: printed value v of the pct% row is a rounding of pct% of a true rate in [s - 1/2, s + 1/2]. -/
def mult (pct s v : Nat) : Bool :=
  100 * (2 * v - 1) ≤ pct * (2 * s + 1) && pct * (2 * s - 1) ≤ 100 * (2 * v + 1)

/-- s7520: printed t (tenths, a multiple of 2) is the nearest 2/10ths of 120% of a mid-term rate in [a-1/2, a+1/2] bp. -/
def s7520 (a t : Nat) : Bool :=
  t % 2 == 0 && 10 * (10 * t - 10) ≤ 6 * (2 * a + 1) && 6 * (2 * a - 1) ≤ 10 * (10 * t + 10)

/-- Σ_{i=0}^{9} D^i (D+N)^(9-i) -/
def annS (N D : Nat) : Nat := (List.range 10).foldl (fun acc i => acc + D ^ i * (D + N) ^ (9 - i)) 0

/-- s42: printed p (bp) for present-value share c/10 (c = 7 or 3), mid M, long L (annual bp). -/
def s42 (c M L p : Nat) : Bool :=
  let D := 1000000
  let Nlo := 36 * (M + L - 1)
  let Nhi := 36 * (M + L + 1)
  -- p(r) = 1000 c (D+N)^9 / annS N D bp, increasing in r
  (2 * p - 1) * annS Nhi D ≤ 2 * 1000 * c * (D + Nhi) ^ 9 &&
  2 * 1000 * c * (D + Nlo) ^ 9 ≤ (2 * p + 1) * annS Nlo D

/-- s642: printed d (tenths) vs the twelve monthly §7520 rates (tenths) of the best year, summed: sum. -/
def s642 (sum d : Nat) : Bool :=
  d % 2 == 0 && 12 * d + 120 ≤ sum + 12 && sum ≤ 12 * d + 120 + 12

end AFR
