import EeTax.Basic
import EeTax.Theorems

/-!
# Concrete findings, checked by the kernel (`decide`; no `native_decide`, no `sorry`)

Amounts in cents. Names are referenced from FINDINGS.md.
-/

namespace EeTax
open TaxKernel

/-! ## Validation anchors (OECD Taxing Wages 2025, Estonia, no II pillar as the OECD assumes) -/

/-- S100 (gross 25 603.16): OECD CGITFP 5 542.571562; eetax 5 542.57. -/
theorem oecd_S100 : (person {wages := 2560316, p2Rate := 0}).tax = 554257 := by decide
/-- S67 (gross 17 154.12): OECD CGITFP 2 427.254228, BTA 5 846.675992; eetax 2 427.25 and 5 846.68. -/
theorem oecd_S67 : (person {wages := 1715412, p2Rate := 0}).tax = 242725 ∧
    (person {wages := 1715412, p2Rate := 0}).exemption = 584668 := by decide

/-! ## F3 The tax hump: 37.20 euro more income tax on 100 euro more wages (plus 3.60 UI + II pillar) -/

theorem hump_wages_100 : (person {wages := 2010000}).tax - (person {wages := 2000000}).tax = 3720 := by decide
theorem hump_wages_social : (person {wages := 2010000}).social - (person {wages := 2000000}).social = 360 := by decide

/-! ## F4 Estonian dividends switch off the exemption (§ 23(3)): 10 800 euro of dividends on top of 14 400 euro
of wages cost 1 726.56 euro of personal income tax, although the dividend itself is not taxed (§ 12(2)). -/

theorem dividend_hump : (person {wages := 1440000, dividendsEE := 1080000}).tax
    - (person {wages := 1440000}).tax = 172656 := by decide
theorem dividend_cit : citOnDividend 1080000 = 304615 := by decide

/-! ## F5 Timing across the hump: two years of 25 200 euro cost 1 726.57 euro more than 36 000 + 14 400 -/

theorem bunching_gain : 2 * (person {wages := 2520000}).tax
    - ((person {wages := 3600000}).tax + (person {wages := 1440000}).tax) = 172657 := by decide

/-! ## F9 Monthly withholding vs the annual return (§ 42(1) vs § 23) -/

/-- 11 months of 1 200 euro and a 12 000 euro bonus in December: the employer's withholding is 1 582.64 euro short
of the annual tax, a bill on the return. -/
theorem bonus_bill : yearSettlement 200 ((List.replicate 11 120000) ++ [1200000]) = -158264 := by decide
/-- Six months of 2 100 euro and then no pay: 1 726.57 euro refunded on the return. -/
theorem halfyear_refund : yearSettlement 200 ((List.replicate 6 210000) ++ (List.replicate 6 0)) = 172657 := by decide

/-! ## F10 Pension age: the same 25 200 euro of wages, 1 849.06 euro less income tax from the year of pension age -/

theorem pension_age_switch : (person {wages := 2520000}).tax - (person {wages := 2520000, pensionAge := true}).tax
    = 184906 := by decide

/-! ## F11 FIE entry notch (SMS § 2(5)): 1 euro of sole-trader profit carries 3 247.20 euro of social tax -/

theorem fie_entry : (person {business := 100}).fieSocial = 324720 := by decide

/-! ## L05 Splitting: 10 000 euro of interest is worth 1 726.56 euro more in the name of a spouse with no income -/

theorem spouse_split : (person {wages := 2560316, interest := 1000000}).tax - (person {wages := 2560316}).tax
    - (person {interest := 1000000}).tax = 172656 := by decide

end EeTax
