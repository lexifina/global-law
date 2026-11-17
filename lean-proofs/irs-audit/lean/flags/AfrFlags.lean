/- Kernel-checked statements behind the verified AFR flags (definitions copied from lean/afr/Checker.lean). -/
def qle (x y u v : Nat) : Bool := x * v ≤ u * y
def growth (k t : Nat) : Nat × Nat := ((20000 * k + t) ^ k, (20000 * k) ^ k)
structure Row where
  a : Nat
  s : Nat
  q : Nat
  m : Nat
/-- some effective yield is consistent with all four printed columns (rounded to 0.01%) -/
def conv (r : Row) : Bool :=
  let ks := [(1, r.a), (2, r.s), (4, r.q), (12, r.m)]
  let los := ks.map (fun (k, v) => growth k (2 * v - 1))
  let his := ks.map (fun (k, v) => growth k (2 * v + 1))
  los.all (fun lo => his.all (fun hi => qle lo.1 lo.2 hi.1 hi.2))

/-- Rev. Rul. 2012-9 (March 2012), Table 2 long-term adjusted AFR as printed: no single rate gives these. -/
theorem rr2012_9_table2 : conv ⟨347, 295, 294, 293⟩ = false := by decide
/-- The corrected figure (Rev. Rul. 2012-12) is consistent. -/
theorem rr2012_12_table2 : conv ⟨297, 295, 294, 293⟩ = true := by decide
/-- §382(f)(1): highest adjusted federal long-term rate of March, February, January 2012 = 3.47%, not 3.55%. -/
theorem rr2012_9_s382 : max 297 (max 326 347) = 347 ∧ (355 : Nat) ≠ 347 := by decide
/-- Rev. Rul. 2014-22 (September 2014), IRB 2014-37, Table 2 long-term adjusted AFR. -/
theorem rr2014_22_table2 : conv ⟨249, 292, 291, 290⟩ = false ∧ conv ⟨294, 292, 291, 290⟩ = true := by decide
/-- Rev. Rul. 2014-26 (October 2014), IRB 2014-41, long-term 110% AFR. -/
theorem rr2014_26_lt110 : conv ⟨318, 316, 315, 310⟩ = false ∧ conv ⟨318, 316, 315, 314⟩ = true := by decide
/-- Rev. Rul. 2014-31 (December 2014), IRB 2014-50, short-term 130% AFR. -/
theorem rr2014_31_st130 : conv ⟨44, 44, 44, 47⟩ = false ∧ conv ⟨44, 44, 44, 44⟩ = true := by decide
/-- §7520 for August 2018: 120% mid-term AFR (annual) printed 3.37% → nearest 0.2% is 3.4%, not 0.4%. -/
theorem rr2018_21_7520 : (10 * 34 ≤ 337 + 10 ∧ 337 ≤ 10 * 34 + 10) ∧ ¬ (10 * 4 ≤ 337 + 10 ∧ 337 ≤ 10 * 4 + 10) := by decide
#print axioms rr2012_9_table2
#print axioms rr2014_31_st130
