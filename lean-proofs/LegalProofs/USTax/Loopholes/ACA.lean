import LegalProofs.USTax.Loopholes.Common

/-!
# The $23,402 dollar (§36B, 2026)

The premium tax credit pays the cost of the benchmark silver plan above an "applicable percentage" of household income.
From 2021 to 2025 the enhanced credit had no income ceiling. It expired on 31 December 2025: for 2026 the credit stops
entirely above 400% of the federal poverty line (§36B(c)(1)(A)), and the top applicable percentage is 9.96%
(Rev. Proc. 2025-25).

For a married couple aged 60 the benchmark plan costs about $31,828 a year (KFF: $15,914 for a 60-year-old in 2026).
400% of the 2025 poverty line for two ($21,150) is $84,600. At that income they pay 9.96% of it and the credit pays the
rest; one dollar more and they pay all of it.

The loophole runs the other way: income here means modified AGI, and a deductible IRA or HSA contribution lowers it.
One dollar into an IRA buys back the whole credit.
-/

namespace Legal.USTax.Loopholes.ACA

def fplTwo : Nat := 21150
def benchmarkCouple60 : Nat := 31828
def ceilingPct : Nat := 996        -- 9.96%, the applicable percentage from 300% to 400% of the poverty line

/-- The credit for incomes from 300% of the poverty line up (the band this file models). -/
def credit (magi : Nat) : Nat := if 4 * fplTwo < magi then 0 else benchmarkCouple60 - magi * ceilingPct / 10000

/-- **The cliff, for every income.** Above 400% of the poverty line there is no credit at all. -/
theorem none_above (magi : Nat) (h : 4 * fplTwo < magi) : credit magi = 0 := by simp [credit, h]

/-- Below it, the couple's share of the benchmark premium never exceeds 9.96% of income. -/
theorem capped_below (magi : Nat) (h : magi ≤ 4 * fplTwo) :
    benchmarkCouple60 - credit magi ≤ magi * ceilingPct / 10000 := by
  simp only [credit, Nat.not_lt.mpr h, ite_false]; omega

/-- **One dollar of income costs $23,402.** -/
theorem cliff : credit 84600 = 23402 ∧ credit 84601 = 0 := by decide

/-- A traditional IRA contribution is deducted in arriving at AGI, and so at MAGI. -/
def magi (wages ira : Nat) : Nat := wages - ira

/-- **One dollar into an IRA is worth $23,402.** The couple earning $84,601 who put $1 in an IRA get the credit back. -/
theorem ira_dollar : credit (magi 84601 1) - credit (magi 84601 0) = 23402 := by decide

/-- A couple earning $100,000 can contribute $15,400 between them ($7,700 each, inside the 2026 limit of $8,600 a person
from age 50): their savings stay theirs, and the credit returned is $23,402: a 152% immediate return. -/
theorem ira_at_100k : credit (magi 100000 15400) = 23402 ∧ credit (magi 100000 0) = 0 := by decide

end Legal.USTax.Loopholes.ACA
