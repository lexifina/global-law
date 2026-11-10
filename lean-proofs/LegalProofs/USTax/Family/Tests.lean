import LegalProofs.USTax.Family.Driver

/-!
# Tests: the kiddie tax, the parent's election and the trust, against IRS examples and hand computations

Sources (downloaded to `tax-formalization-data/hunt/family/docs/`): 2025 Instructions for Form 8814 (p. 3, "Fred"),
2025 Instructions for Form 8615 (pp. 3–9: "Amanda Black", the Persimmon children, the line 5 worksheets and the line
9/10/15/18 rules), Rev. Proc. 2024-40 §§3.01–3.03, 3.12, Pub. 590-B (2025) p. 8 and Appendix B Table III. Where the IRS
gives no numbers (Form 1041 has no worked example of DNI), the expected value is computed by hand from the statute in
the comment above the test.
-/

namespace Legal.USTax.Family.Tests
open Legal.USTax.Family TaxCode.Individual

/-! ## §1(g)(7): Form 8814, "Fred" (2025 Instructions for Form 8814, p. 3)

Ordinary dividends $2,190, all qualified; capital gain distributions $610. Line 4 $2,800; line 6 $100; line 9 $78 to
the parent's qualified dividends; line 10 $22 to Schedule D; line 12 $0 to Schedule 1. Line 15: line 14 is $1,450, not
under $1,350, so $135. -/

def fred : Household :=
  { filing := .single, head := { age := 6 }, canBeClaimedAsDependent := true,
    ordinaryDividends := 2190, qualifiedDividends := 2190, longTermGains := 610 }

/-- Fred's capital gain distribution counts as a dividend under §1(g)(7)(A)(i); the household model cannot tell it from
a sale, so the model's eligibility test (conservatively) asks for no gain at all. Without it Fred is eligible. -/
theorem fred_eligible : form8814Eligible { age := 6 } { fred with longTermGains := 0 } = true := by decide
theorem fred_parent :
    let p := form8814Include ({ filing := .mfj, head := { age := 40 } } : Household) fred
    p.ordinaryDividends = 78 ∧ p.qualifiedDividends = 78 ∧ p.longTermGains = 22 ∧ p.taxableInterest = 0 := by decide
theorem fred_tax : form8814Tax 2800 = 135 := by decide
/-- Under $2,700 nothing is included, and the tax is 10% of the excess over $1,350 (form line 15). -/
theorem small_child : form8814Tax 2000 = 65 ∧
    (form8814Include ({ filing := .mfj, head := { age := 40 } } : Household)
      { fred with ordinaryDividends := 2000, qualifiedDividends := 2000, longTermGains := 0 }).ordinaryDividends = 0 := by
  decide
/-- §1(g)(7)(A)(ii): "less than 10 times" $1,350; and a child who sold stock (a gain that is not a capital gain
distribution is modelled as a short-term gain here) or has wages is not eligible. -/
theorem not_eligible : form8814Eligible { age := 6 } { fred with ordinaryDividends := 13500, longTermGains := 0 } = false ∧
    form8814Eligible { age := 6 } { fred with wages := 100 } = false ∧
    form8814Eligible { age := 6 } { fred with shortTermGains := 5 } = false := by decide

/-! ## §1(g)(4): "Amanda Black" (2025 Instructions for Form 8615, p. 3)

Dividends $1,300 (qualified), wages $2,100, taxable interest $1,400, tax-exempt interest $100, capital gains $300,
capital losses ($200). Unearned income (line 1) $2,800. Her standard deduction is the greater of $1,350 or $2,100 + $450
= $2,550; AGI $4,900; taxable income $2,350; net unearned income min($2,350, $2,800 − $2,700) = $100. -/

def amanda : Household :=
  { filing := .single, head := { age := 13 }, canBeClaimedAsDependent := true,
    wages := 2100, ordinaryDividends := 1300, qualifiedDividends := 1300, taxableInterest := 1400,
    taxExemptInterest := 100, longTermGains := 300, shortTermGains := -200 }

theorem amanda_line1 : unearnedIncome amanda = 2800 := by decide
theorem amanda_nui : (form1040With {} amanda).taxableIncome = 2350 ∧
    netUnearned amanda (form1040With {} amanda).taxableIncome = 100 := by decide

/-! ## §1(g)(3)(B): the Persimmon children (2025 Instructions for Form 8615, pp. 4 and 8)

Line 5 amounts: Sharon $3,000, Jerry $2,800, Mike $3,200; line 12a $9,000 for each; Sharon's line 12b 0.333. With the
parents' joint taxable income at $120,000 (inside the 22% row), the allocable parental tax is 22% of $9,000 = $1,980
and Sharon's share is $660 (= $1,980 × 3,000/9,000). Her taxable income is $5,700 − $1,350 = $4,350 of interest,
of which $3,000 is net unearned income; the rest, $1,350, is taxed at her own rate: the Tax Table row $1,350–$1,375
gives $136 (10% of the midpoint $1,362.50). Line 16 = $796; line 17 (her own tax on $4,350, row $4,350–$4,400, 10% of
$4,375) = $438; line 18 = $796. -/

def child (interest : Int) : Household :=
  { filing := .single, head := { age := 10 }, canBeClaimedAsDependent := true, taxableInterest := interest }

def lineOf (interest : Int) : ChildLine :=
  let h := child interest
  let ti := (form1040With {} h).taxableIncome
  let n := netUnearned h ti
  ⟨ti, n, childQdcg h, nuiQdcg h n⟩

theorem persimmon_nui : (lineOf 5700).nui = 3000 ∧ (lineOf 5500).nui = 2800 ∧ (lineOf 5900).nui = 3200 := by decide
theorem persimmon_parental : allocableParentalTax .mfj 120000 0 [lineOf 5700, lineOf 5500, lineOf 5900] = 1980 := by
  decide
theorem sharon : kiddieTax .mfj 120000 0 [lineOf 5700, lineOf 5500, lineOf 5900] (lineOf 5700) = 796 := by decide
/-! ## §1(g)(2): who it applies to -/

theorem under18 : ({ age := 17, earned := 1000000, support := 0 } : ChildFacts).subject = true := by decide
theorem eighteen_earner : ({ age := 18, earned := 15001, support := 30000 } : ChildFacts).subject = false ∧
    ({ age := 18, earned := 15000, support := 30000 } : ChildFacts).subject = true := by decide
theorem student_23 : ({ age := 23, student := true, earned := 0, support := 30000 } : ChildFacts).subject = true ∧
    ({ age := 23, student := false, earned := 0, support := 30000 } : ChildFacts).subject = false ∧
    ({ age := 24, student := true, earned := 0, support := 30000 } : ChildFacts).subject = false := by decide

/-! ## Qualified dividends inside net unearned income (Line 5 Worksheet #1)

$10,000 of qualified dividends and nothing else: line 1 $10,000, line 5 $7,300; worksheet line 4 = 1.000, line 6 =
$2,700, line 8 = $10,000 − $2,700 = $7,300 of qualified dividends on line 5. The proportional rule gives the same. -/
theorem qd_in_nui :
    let h : Household := { child 0 with ordinaryDividends := 10000, qualifiedDividends := 10000 }
    nuiQdcg h (netUnearned h (form1040With {} h).taxableIncome) = 7300 := by decide

/-! ## The trust (§1(e), §1(h), §§643, 661, 662, 1411(a)(2)); values by hand -/

/-- $20,000 of ordinary taxable income: $3,777 + 37% × $4,350 = $5,386.50, rounded to $5,387. -/
theorem trust_rate : trustTax 20000 0 = 5387 := by decide
/-- Rev. Proc. 2024-40 §3.01 Table 5 row bases: $315 at $3,150, $2,307 at $11,450, $3,777 at $15,650. -/
theorem trust_rows : trustTax 3150 0 = 315 ∧ trustTax 11450 0 = 2307 ∧ trustTax 15650 0 = 3777 := by decide
/-- $19,900 of gain: 0% to $3,250, 15% of $12,650 = $1,897.50, 20% of $4,000 = $800: $2,697.50 → $2,698. -/
theorem trust_gain : trustTax 19900 19900 = 2698 := by decide

/-- Interest $10,000, qualified dividends $10,000, tax-exempt interest $5,000, gains $20,000 allocated to corpus; $15,000
paid to one beneficiary. DNI $25,000 (§643(a)(3), (5)); the beneficiary includes $15,000, of which (§662(b)) $3,000
tax-exempt, $6,000 interest, $6,000 qualified dividends; the deduction is $12,000 (§661(c)); trust taxable income
$40,000 − $12,000 − $100 = $27,900, of which $24,000 is net capital gain and qualified dividends ($4,000 + $20,000):
$495 on $3,900, 15% of $12,000, 20% of $12,000 = $4,695. NIIT: 3.8% of the lesser of $28,000 undistributed and
$27,900 − $15,650 = $12,250: $465.50 → $466. -/
def tinc : TrustIncome := ⟨10000, 10000, 10000, 20000, 5000⟩
theorem trust_example :
    let r := trustReturn false tinc [15000]
    r.dni = 25000 ∧ r.carries = [⟨6000, 0, 6000, 0, 3000⟩] ∧ r.distributionDeduction = 12000 ∧
      r.taxableIncome = 27900 ∧ r.regularTax = 4695 ∧ r.niit = 466 := by decide
/-- §662(a)(2) second sentence: distributions of $20,000 each against DNI of $25,000: each includes $12,500. -/
theorem trust_prorata : (trustReturn false tinc [20000, 20000]).carries.map Carry.total = [12500, 12500] := by decide
/-- With gains in DNI the whole $45,000 can be carried out; the trust is left with $0 of taxable income
(less than the $100 exemption) and pays nothing. -/
theorem trust_all_out : (trustReturn true tinc [45000]).total = 0 ∧
    (trustReturn true tinc [45000]).distributionDeduction = 40000 := by decide

/-! ## Required minimum distributions (Pub. 590-B (2025) p. 8: $100,000 at 75 → $4,065) -/
theorem rmd_example : rmdFor 75 75 100000 = 4065 ∧ rmdFor 74 75 100000 = 0 := by decide

end Legal.USTax.Family.Tests
