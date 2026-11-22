import HuTax.Theorems

/-!
# The households of FINDINGS.md, proved by `decide` on the model

Each theorem evaluates the model (`stage1`, `compute`, `capitalSzocho`) on the named household; the numbers are the
ones FINDINGS.md quotes. AW = 8 455 487 forint (OECD TW 2025 average wage, Hungary).
-/

namespace HuTax
open TaxKernel

/-! ## F3 (gov-error): NAV 73 § 13, the Kedves family: Orsi earns 2 400 000, of which 600 000 in October-December
qualifies for the three-children mothers' allowance; her base left for the family allowance is 1 800 000, not the
2 000 000 the booklet lets her claim. -/
theorem f3_orsi_base : (stage1 { age := 45, wages := 2400000, mother3 := true, q4 := 600000 }).rest = 1800000 := by
  decide

/-! ## F4 (loophole-new): mother of three, átalány income 6 000 000 (taxable 4 255 200), husband at 1 AW, three
children: receipts moved into October-December 2025 (2025. évi XV. tv. 4. §) cut the family's taxes by 478 710. -/
def f4House (q4 : Int) : House :=
  { persons := [{ age := 35, atalany := 6000000, mother3 := true, q4 }, { age := 37, wages := 8455487 }],
    couple := true, deps := 3, bens := 3, disabledKids := 0 }
theorem f4_mother3_q4 :
    (compute (f4House 1063800)).burden = 2590686 ∧ (compute (f4House 4255200)).burden = 2111976 := by decide

/-! ## F5 (loophole-new): turning 25 in June 2025 on 300 000 a month: a 2 000 000 bonus accounted to June or
earlier is inside the unused under-25 cap (6 × 656 785 − 1 800 000 = 2 140 710); accounted to July or later it is
taxed: 300 000 forint. -/
theorem f5_birthday_bonus :
    pct pitRate (stage1 { age := 25, birthMonth := 6, wages := 5600000, youthIncome := 3800000 }).rest = 270000 ∧
    pct pitRate (stage1 { age := 25, birthMonth := 6, wages := 5600000, youthIncome := 1800000 }).rest = 570000 := by
  decide

/-! ## F6 (loophole-new): lone parent of three on 0.6 AW (5 073 292): 1 000 000 of pay moved from 2025 into 2026
(the family frame rises from 9 900 000 to 12 × 3 × 440 000 = 15 840 000) removes the 2025 TB of 214 553 and adds no
burden in 2026 (2025 rules otherwise). -/
def f6House (w : Int) (frame : Option Int) : House :=
  { persons := [{ wages := w }], couple := false, deps := 3, bens := 3, disabledKids := 0, frame }
theorem f6_year_shift :
    (compute (f6House 5073292 none)).burden + (compute (f6House 5073292 (some 15840000))).burden
      - ((compute (f6House 4073292 none)).burden + (compute (f6House 6073292 (some 15840000))).burden) = 214553 := by
  decide

/-! ## F7 (loophole-known mechanism): dividends of 6 979 200 every year vs 13 958 400 every second year, no wages:
the szocho ceiling is annual (Szocho tv. § 2 (2)): 907 296 forint saved per two years. -/
theorem f7_dividend_bunching :
    2 * capitalSzocho { dividends := 6979200 } (stage1 { dividends := 6979200 })
      - capitalSzocho { dividends := 13958400 } (stage1 { dividends := 13958400 }) = 907296 := by decide

/-! ## F8 (statute-fault, design): a lone parent of three aged 24 on 0.5 AW pays exactly what the same parent aged
30 pays: the under-25 allowance (nominally 15 % × 4 227 744 = 634 162) is worth nothing to them. -/
def f8House (age : Nat) : House :=
  { persons := [{ age, wages := 4227744 }], couple := false, deps := 3, bens := 3, disabledKids := 0 }
theorem f8_young_parent : (compute (f8House 24)).burden = (compute (f8House 30)).burden ∧
    (compute (f8House 30)).burden = -612000 := by decide

/-! ## F9 (loophole-new, lead): an employee at 1 AW pays 13 % szocho on bank interest but none on dividends or
fund gains (wages already exceed 24 × minimum wage): 5 000 000 of interest bears 650 000 more. -/
theorem f9_interest_vs_gains :
    capitalSzocho { wages := 8455487, interest := 5000000 } (stage1 { wages := 8455487 }) = 650000 ∧
    capitalSzocho { wages := 8455487, gains := 5000000 } (stage1 { wages := 8455487 }) = 0 := by decide

/-! ## F10 (loophole-known, recreated): a service business with 1 AW of revenue and no real costs as a flat-rate
(átalány, 40 %) sole trader pays 1 655 204 in personal taxes and contributions; the same 1 AW as an employer's total
cost (wage 7 482 732 + 13 % szocho) costs 3 479 470 (employee 2 506 715 + employer szocho 972 755). -/
def f10Atalany : House :=
  { persons := [{ atalany := atalanyIncome 8455487 atalanyCostDefault }], couple := false, deps := 0, bens := 0,
    disabledKids := 0 }
def f10Salary : House :=
  { persons := [{ wages := 7482732 }], couple := false, deps := 0, bens := 0, disabledKids := 0 }
theorem f10_atalany_vs_salary :
    (compute f10Atalany).burden = 1655204 ∧ (compute f10Salary).burden = 2506715 ∧
    pct szochoRate 7482732 = 972755 := by decide

/-! ## F11 (statute-fault): Cst. § 11 (1) amounts in the version of 2009.I.1 (`refs/jogtar/cst_20090101.html`) are
the 2025 amounts. -/
def cspCouple2009 : List Int := [12200, 13300, 16000]
def cspSingle2009 : List Int := [13700, 14800, 17000]
theorem f11_csp_frozen : cspCouple = cspCouple2009 ∧ cspSingle = cspSingle2009 := by decide

end HuTax
