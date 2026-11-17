import Penalties
open Pen

/-!
  Kernel-checked statements behind each disagreement in RUN1.md (amounts in cents, as the opinions state them).
  `#print axioms` on each: none beyond `propext`/`Quot.sound` where `simp` is used, none for `decide`.
-/

/-- Ni v. Commissioner, 115 T.C. No. 37 (2000): The Nis Family Trust, 1995, deficiency $83, penalty $17.
  The court found that "all of the underpayments of tax here in question are attributable to substantial
  understatements of tax". An understatement of at most $83 cannot exceed $5,000, whatever the tax required. -/
theorem ni_trust_not_substantial (t : Nat) : substantialIndiv 10 8300 t = false :=
  not_substantial_small 10 8300 t (by decide)
/-- The $17 penalty itself is 20% of $83 to the dollar (16.60 → 17). -/
theorem ni_trust_penalty : near 1700 20 100 8300 100 = true := by decide

/-- Watts v. Commissioner, T.C. Memo. 1999-416, 1994: deficiency $3,624, §6651(a)(1) $7,035, §6662 $5,628.
  20% of $3,624 is $724.80 and 25% is $906; the stated penalties are 20% and 25% of $28,140 instead. -/
theorem watts_1994_acc : acc20 362400 = 72480 ∧ near 562800 20 100 2814000 0 = true ∧ atMost 562800 20 100 362400 100 = false := by decide
theorem watts_1994_ftf : near 703500 25 100 2814000 0 = true ∧ atMost 703500 25 100 362400 100 = false := by decide
/-- 1995: deficiency $5,150, §6662 $2,567 (20% of $12,835), §6651(a)(1) $2,431. -/
theorem watts_1995 : near 256700 20 100 1283500 0 = true ∧ atMost 256700 20 100 515000 100 = false
    ∧ atMost 243100 25 100 515000 100 = false := by decide

/-- Cordes v. Commissioner, T.C. Memo. 2002-125, Joseph P. and Jean Ann Richard: 1994 deficiency $1,757,554,
  penalty $351,590 (20% = $351,510.80); 1995 deficiency $980,285, penalty $196,884 (20% = $196,057). -/
theorem richard_1994 : acc20 175755400 = 35151080 ∧ atMost 35159000 20 100 175755400 100 = false := by decide
theorem richard_1995 : acc20 98028500 = 19605700 ∧ atMost 19688400 20 100 98028500 100 = false := by decide

/-- Norton v. Commissioner, T.C. Memo. 2002-137, 1994: deficiency $101,230, §6651(a)(1) $25,457
  (25% = $25,307.50). -/
theorem norton_1994 : 10123000 * 25 / 100 = 2530750 ∧ atMost 2545700 25 100 10123000 100 = false := by decide

/-- Chamberlin v. Commissioner, T.C. Memo. 2000-50, 1985: deficiency $0 with §6651(a)(1) $212 and (a)(2) $192.
  No part of either can be attributable to a deficiency of zero. -/
theorem chamberlin_1985 : atMost 21200 25 100 0 0 = false ∧ atMost 19200 25 100 0 0 = false := by decide

/-- Brown v. Commissioner, T.C. Memo. 2018-91, 2009: deficiency $5,538; late return (filed during the exam) reported
  a balance due of $7,228; the notice's §6651(a)(1) $3,192 is 25% of the sum, not of the deficiency ($1,384.50). -/
theorem brown_2009 : near 319200 25 100 (553800 + 722800) 100 = true ∧ atMost 319200 25 100 553800 100 = false := by decide
/-- 2010: deficiency $20,394, reported balance due $7,129, §6651(a)(1) $6,881. -/
theorem brown_2010 : near 688100 25 100 (2039400 + 712900) 100 = true ∧ atMost 688100 25 100 2039400 100 = false := by decide

/-- Summary Opinion 2010-109: total tax $19,821 less the $5,231 actually shown is $14,590; the IRS subtracted $5,261
  and determined $14,560. Its §6651(a)(1) $4,947.75 is 25% of $19,791 (deficiency plus tax shown on the late return). -/
theorem so2010_109 : 1982100 - 523100 = 1459000 ∧ 1982100 - 526100 = 1456000 ∧ 1979100 * 25 / 100 = 494775 := by decide

/-- A court applying the threshold correctly: T.C. Summ. Op. 2008-57, understatement $4,970. -/
theorem so2008_57 (t : Nat) : substantialIndiv 10 497000 t = false := not_substantial_small 10 497000 t (by decide)
