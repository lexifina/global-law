import Penalties
open Pen

/-!
  Run 2 (RUN2.md): kernel-checked statements behind each item verified by hand in the full Tax Court set.
  Amounts in cents, as the opinions print them.
-/

/-- T.C. Summary Opinion 2005-96 (docket 779-04), 2001: understatement $4,318, tax required to be shown $6,932.
  The court: "the amount of the understatement exceeds 10 percent of the tax required to be shown on the return.
  Therefore, there was a substantial understatement", and (n.9) did not reach negligence. The 10% limb holds, but the
  test is "the greater of" 10% or $5,000, and $4,318 does not exceed $5,000. -/
theorem so2005_96 : decide (100 * 431800 > 10 * 693200) = true ∧ substantialIndiv 10 431800 693200 = false := by decide

/-- T.C. Summary Opinion 2006-108 (docket 12423-04), 2002: deficiency $1,296; the court found the burden of production
  met "with respect to petitioners' substantial understatement". Never substantial, whatever the tax required. -/
theorem so2006_108 (t : Nat) : substantialIndiv 10 129600 t = false := not_substantial_small 10 129600 t (by decide)

/-- T.C. Memo. 2006-253 (docket 24854-04), 2002, no return filed: deficiency $8,716, §6651(a)(1) addition $2,614.80,
  sustained. That is exactly 30%; the cap is 25% ($2,179). -/
theorem tcm2006_253 : 871600 * 30 / 100 = 261480 ∧ atMost 261480 25 100 871600 100 = false := by decide

/-- T.C. Memo. 1996-260 (docket 222-94), 1990: deficiency $1,181.38, §6651(a)(1) $6,503.94, §6662 $6,607.52; both
  sustained, decision for respondent. Each exceeds its cap on the stated deficiency several times over. -/
theorem tcm1996_260 : atMost 660752 20 100 118138 100 = false ∧ atMost 650394 25 100 118138 100 = false := by decide

/-- T.C. Memo. 2001-6 (docket 12390-96): 1990 deficiency $66,194 with §6662 $53,620; 1993 $96,884 with $22,048. -/
theorem tcm2001_6 : atMost 5362000 20 100 6619400 100 = false ∧ atMost 2204800 20 100 9688400 100 = false := by decide

/-- T.C. Memo. 2013-282 (docket 14733-12), 2008: deficiency $118,156, §6662(a) $97,205.25, §6663 $83,684.25. -/
theorem tcm2013_282 : atMost 9720525 20 100 11815600 100 = false ∧ atMost 9720525 40 100 11815600 100 = false := by decide

/-- T.C. Memo. 2026-53 (docket 24068-22, Rule 155), Waimana: 2003 deficiency $20,746 with §6663 $68,360; 2008
  deficiency $2,062 with §6663 $2,706. -/
theorem tcm2026_53 : atMost 6836000 75 100 2074600 100 = false ∧ atMost 270600 75 100 206200 100 = false := by decide

/-- §6665(b)(1) shape, T.C. Memo. 1997-64 (docket 10433-95), 1987: deficiency $7,954; the late 1987 return
  (filed 4 March 1992) showed tax of $4,379; §6651(a)(1) $2,815 exceeds 25% of the deficiency but not 25% of
  deficiency plus reported tax. -/
theorem tcm1997_64 : atMost 281500 25 100 795400 100 = false ∧ atMost 281500 25 100 (795400 + 437900) 0 = true := by decide

/-- §6665(b)(1) shape, T.C. Summary Opinion 2012-104 (docket 30651-08, Rule 155), 2004 (return filed late, 14 Aug
  2006): deficiency $4,820, §6651(a)(1) $1,344 (25% = $1,205). -/
theorem so2012_104 : atMost 134400 25 100 482000 100 = false := by decide

/-- Penalties above 20% of the stated deficiency, not reconciled in the opinion (lawful only if the underpayment
  exceeds the deficiency, which the opinion does not say): T.C. Memo. 2018-79 (2014: $5,261 on $20,305), T.C. Memo.
  2021-129 (2017: $1,422 on $4,413), T.C. Memo. 2022-37 (2013: $184,676 on $923,280), T.C. Summary Opinion 2014-28
  (2010: $1,401 on $5,618). -/
theorem unreconciled_20 : atMost 526100 20 100 2030500 100 = false ∧ atMost 142200 20 100 441300 100 = false
    ∧ atMost 18467600 20 100 92328000 100 = false ∧ atMost 140100 20 100 561800 100 = false := by decide

/-- Bench opinion, docket 11519-05, 2003: deficiency $518, §6651(a)(1) $139.80 (25% = $129.50); respondent conceded
  a reduction to $127 before decision. -/
theorem bench_11519_05 : atMost 13980 25 100 51800 100 = false ∧ atMost 12700 25 100 51800 100 = true := by decide

#print axioms so2005_96
#print axioms tcm2006_253
