import CzTax.Tests

/-!
# Walls: notches and the new loopholes, kernel-checked on named households (`decide`)

Each statement is about the full household computation `compute` (tax + contributions + přídavek), so it is the
model's own arithmetic that is checked, not a hand calculation.
-/

namespace CzTax

def burden (r : Result) : Int := r.incomeTax + r.employeeSocial - r.benefits

/-- A couple with children aged 6 and 11, one earner of 730 930 Kč (1,25 AW), the other with no income. -/
def coupleKids (claim : List Nat) : Household :=
  { adults := [{ wages := 730930 }, { age := 38 }], married := true, children := [{ age := 6 }, { age := 11 }],
    childClaimants := claim }

/-- **N1 (new)**: letting the non-earning spouse claim the first child (who cannot use it: no § 6/§ 7 income, ZDP
§ 35c odst. 4) raises the earner's tax by 15 204 Kč but lowers the family's net income below 3,4 × životní minimum
(ZSSP § 5 odst. 1 písm. a): income "po odpočtu daně"), so the přídavek na dítě of 35 280 Kč is paid: the family
gains 20 076 Kč by forgoing a tax credit. -/
theorem n1_forgo_credit_gain :
    burden (compute (coupleKids [0, 0])) - burden (compute (coupleKids [1, 0])) = 20076 := by decide

/-- A couple with three children (4, 8, 12): 700 000 + 150 000 Kč of wages. -/
def couple3 (claim : List Nat) : Household :=
  { adults := [{ wages := 150000 }, { wages := 700000 }], married := true,
    children := [{ age := 4 }, { age := 8 }, { age := 12 }], childClaimants := claim }

/-- **N2 (new)**: the same zvýhodnění claimed by the low earner (paid as a refundable bonus, which ZSSP § 5 does not
count as income) instead of by the high earner (where it lowers the counted tax) leaves the household's tax unchanged
but its counted net income lower: přídavek 51 240 Kč a year. -/
theorem n2_allocation_gain :
    (compute (couple3 [0, 0, 0])).incomeTax = (compute (couple3 [1, 1, 1])).incomeTax ∧
    burden (compute (couple3 [1, 1, 1])) - burden (compute (couple3 [0, 0, 0])) = 51240 := by decide

/-- Paušální daň band edge (§ 2a odst. 5, § 7a odst. 1 písm. a)): receipts of the 40 % class (doctors, lawyers)
one crown above 1 000 000 Kč move the whole year to band 2: 96 348 Kč more for one crown. -/
theorem pausal_band_notch :
    (pausalYearTax (pausalBandFor 1000001 40) + pausalYearSocial (pausalBandFor 1000001 40))
      - (pausalYearTax (pausalBandFor 1000000 40) + pausalYearSocial (pausalBandFor 1000000 40)) = 96348 := by decide

/-- DPP limit (ZDP § 6 odst. 4 písm. a), zákon 187/2006 § 7a): one crown more a month brings social and health
insurance on the whole amount: 16 020 Kč a year at 11 500 Kč a month. -/
theorem dpp_notch_year : eeSocial (12 * 11500) + eeHealth false (12 * 11500) = 16020 := by decide

/-- Vedlejší OSVČ (zákon 155/1995 § 10 odst. 2): profit one crown above the rozhodná částka brings pension
insurance on 12 × 5 122 Kč at least. -/
theorem side_threshold_notch : seSocial 111736 true 600000 - seSocial 111735 true 600000 = 17948 := by decide

end CzTax
