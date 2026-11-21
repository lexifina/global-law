import TaxKernel.World

/-!
# Liberia: income tax of a resident natural person, Liberia Revenue Code (Revenue Code of 2000) as amended, tax year 2025

Sources (Liberia Revenue Authority, lra.gov.lr "Domestic Tax Laws & Regulations" and "Laws and Amendments" pages; files
in `lr/law/`):
* "Liberia Consolidated Revenue Code As Amended - 2020" (LRA, `REVENUE-CODE-LIBERIA-REVENUE-CODE-AMENDEMENT-2020-min.pdf`,
  250 pages, text layer) s. 200(a)(3)(A): "Tax Table for Resident Natural Persons | Taxable Income of— (Liberian Dollars)
  | Tax Rate and Computation (Liberian Dollars) | 1 | 0 to 70,000 | Nil | 2 | 70,001 to 200,000 | 5% of the excess
  over 70,000 | 3 | 200,001 to 800,000 | 6,500 + 15% of the excess over 200,000 | 4 | 800,001 and above | 96,500 + 25%
  of the excess over 800,000"; s. 205(a): "An annual standard deduction for a natural person, in an amount of up to
  $70,000, is reflected in the tax table of Section 200(a) as a zero bracket amount."
* Amending Acts on the LRA page, read by OCR: the Tax Amendment Act of 2024 (chapters 8 and 10: withholding, goods and
  services tax), the Tax Amendment Act of December 2024 (ss. 602, 702, 741, withholding on payments, excise), the Act
  amending ss. 1003 and 1066(a) (VAT 15 %), the Tax Amendment Act of December 2025 (excise; for 2026): none amends
  s. 200(a). Amendments between the 2020 consolidation and 2024 that the LRA page does not list were not searched
  (no other source): grade A with that caveat.
Currency: the table is in Liberian dollars (LRD); amounts in US dollars must be converted by the user.
Not reached: NASSCORP employee contribution (social security decree): optional input `nasscorpEmployee` (annual LRD),
reported only.
-/

namespace LrTax
open TaxKernel

/-- s. 200(a)(3)(A), annual, Liberian dollars. -/
def sched : Schedule := Schedule.ofList [(0, 0), (70000, 500), (200000, 1500), (800000, 2500)]

def person (a : Adult) : Int × Int :=
  let ti := pos (a.wages + a.selfEmployment)
  (sched.tax Rule.unitDown ti, ti)

def out (c : Canon) : Out :=
  let ps := c.adults.map person
  let soc := (c.int? "nasscorpEmployee").getD 0
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 then ["interest, dividends and rents: final withholding rules not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "LR" "LRD" (sumInts (ps.map (·.1))) (employeeSocial := pos soc)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.2))),
      Out.dStr "note" "individual taxation; s. 200(a) table (standard deduction 70,000 as the zero bracket, s. 205(a)); LRD"])
    (unsupported := unsup ++ ["NASSCORP employee contribution: decree not reached (input nasscorpEmployee reported only)",
      "business income taxed on the same table without business deductions", "amounts paid in US dollars must be converted to LRD by the user"])

def country : Country := { code := "LR", name := "Liberia (Revenue Code 2000 as amended)", currency := "LRD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- The printed fixed amounts of the s. 200(a) table: 6,500 at 200,000 and 96,500 at 800,000. -/
#guard sched.tax Rule.unitDown 200000 = 6500 ∧ sched.tax Rule.unitDown 800000 = 96500
#guard sched.tax Rule.unitDown 70000 = 0

end LrTax
