import AuTax.Household

/-!
# Named households: notches, cliffs and known techniques, as statements about the model (2024-25)

`burdenOf h` = income tax + Medicare levy + MLS + Div 293 + contributions tax + HELP - FTB (- PP(S)), in cents.
Each theorem compares two households that differ in one dollar of income (a notch) or in one choice (a technique).
-/

namespace AuTax

def burdenOf (h : Household) : Int := burden (compute h)

def soleParent (w : Int) (isup : Bool := false) : Household :=
  { id := "sp", persons := [{ wages := w }], children := [6, 11], incomeSupport := isup }
def oneEarnerCouple (w : Int) (int1 int2 : Int := 0) : Household :=
  { id := "c1", persons := [{ wages := w, interest := int1 }, { interest := int2 }], married := true, children := [6, 11] }
def singleP (x : Person) : Household := { id := "s", persons := [x] }

/-- FA Act Sch 1 cl 38A(1A): one more dollar of family ATI above $80,000 removes the FTB A supplement for both
children ($916.15 each): the household pays $1,832.82 more for earning $1 more. -/
theorem notch_ftb_supplement :
    burdenOf (soleParent 80001) - burdenOf (soleParent 80000) = 183282 := by native_decide

/-- Sch 1 cl 28B(1) (indexed primary earner limit $117,194): the whole of FTB Part B ($3,883.60) goes at $117,195. -/
theorem notch_ftb_b_primary_limit :
    burdenOf (oneEarnerCouple 117195) - burdenOf (oneEarnerCouple 117194) = 388422 := by native_decide

/-- MLA s. 8B(2) with the indexed singles tier 1 threshold $97,000: without hospital cover the surcharge (1 % of
all taxable income) starts at $97,001: $970.33 more tax for $1 more income. -/
theorem notch_mls_single :
    burdenOf (singleP { wages := 97001, privateCover := false }) -
      burdenOf (singleP { wages := 97000, privateCover := false }) = 97033 := by native_decide

/-- HESA s. 154-20 (2024-25 table): repayment of 1 % of all repayment income from $54,435: $544.68 more for $1. -/
theorem cliff_help_2425 :
    burdenOf (singleP { wages := 54435, helpDebt := true }) -
      burdenOf (singleP { wages := 54434, helpDebt := true }) = 54468 := by native_decide

/-- 2025-26 (marginal repayments, HESA s. 154-10 $67,000): the same step costs 47 cents (30 % tax + 2 % levy + 15 % HELP). -/
theorem no_cliff_help_2526 :
    burdenOf { singleP { wages := 67001, helpDebt := true } with year := 2026 } -
      burdenOf { singleP { wages := 67000, helpDebt := true } with year := 2026 } ≤ 100 := by native_decide

/-- The income-support passport (FA Act Sch 1 cl 38L): a sole parent with a residual Parenting Payment (Single)
has no FTB A income test; when the residual runs out (annualised: $72,078), the family loses the PP(S) residual,
the pharmaceutical and telephone allowances and the FTB A income-test exemption at once: $1,701.63. -/
theorem notch_income_support_passport :
    burdenOf (soleParent 72078 true) - burdenOf (soleParent 72077 true) = 170163 := by native_decide

/-- Splitting $20,000 of interest with the non-earning spouse at $100,000 (K4 + the FTB B primary limit): moving
$5,000 saves $5,483.60, more than the amount moved. -/
theorem split_crosses_ftb_b :
    burdenOf (oneEarnerCouple 100000 20000 0) - burdenOf (oneEarnerCouple 100000 15000 5000) = 548360 := by
  native_decide

/-- Salary sacrifice does not reach the FTB A supplement: reportable super contributions count in ATI (FA Act
Sch 3 cl 2), so $3,000 sacrificed at $82,000 saves only the income tax and levy (32 % less the fund's 15 %). -/
theorem sacrifice_blocked_ftb :
    burdenOf (soleParent 82000) -
      burdenOf { soleParent 82000 with persons := [{ wages := 82000, superContrib := 3000, sacrifice := true }] }
      = 51000 := by native_decide

end AuTax
