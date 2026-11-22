import TaxKernel.Global
import R5Common

/-!
# United Arab Emirates 2025: Corporate Tax (1200)

Source: Federal Decree-Law No. 47 of 2022 (English, "not an official translation", `law/fdl47-2022_ct_en.pdf`):
* art. 3(1): "a. 0% … on the portion of the Taxable Income not exceeding the amount specified in a decision issued by
  the Cabinet"; "b. 9% … that exceeds" it. The amount (AED 375,000, Cabinet Decision 116/2022) was not read: grade B.
* art. 23: participation exemption from a 5 % ownership interest.
* art. 37(2): losses used "cannot exceed 75% … of the Taxable Income … before any Tax Loss relief".
* art. 45(1) (as replaced by FDL 40/2024): "The State Sourced Income of a Non-Resident Person shall be subject to tax at a
  rate of (0%) zero percent in the form of Withholding Tax"; art. 13(2): State Sourced Income includes services
  utilised in the State (b), intellectual property used in the State (f), interest from a resident borrower (g) and
  income derived from a Resident Person (1)(a), dividends included. Cited 0 % on all four kinds (kernel 2.3.0).
-/

namespace AeGlobal
open TaxKernel TaxKernel.Global R5Common

def ct : CorpRegime :=
  { name := "Corporate Tax", sched := Schedule.ofList [(0, 0), (375000, 900)], lossFull := 0, lossExcessBp := 7500,
    participationBp := 10000, participationMinBp := 500 }

def aeWht : Wht :=
  { name := "Withholding Tax", rules := Wht.zeroOn [.dividend, .interest, .royalty, .services]
      "FDL 47/2022 art. 45(1) (by FDL 40/2024): State Sourced Income of a non-resident 0 %; art. 13" }

def corporate : Family := corpFamily "1200 Corporate Tax" (fun _ => ct)
  (fun _ => "FDL 47/2022 art. 3(1) (0 % to AED 375,000 [Cabinet decision, not read], 9 % above), art. 23, art. 37(2) (75 %)")
  aeWht

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g false true false false
  ++ (if g.entity == .company then ["small business relief (Ministerial Decision 73/2023), free-zone 0 % and DMTT not modelled"] else [])

#guard ct.citTax { profit := 375000 } == 0
#guard aeWht.amount { kind := .royalty, amount := 100000 } == 0
#guard (aeWht.ruleFor { kind := .dividend, amount := 1, toCompany := false }).isSome
#guard ct.citTax { profit := 1375000 } == 90000
-- 75 % cap: 1 000 000 profit, 2 000 000 losses: 250 000 remain taxable
#guard ct.taxableProfit { profit := 1000000, lossesForward := 2000000 } == 250000

end AeGlobal
