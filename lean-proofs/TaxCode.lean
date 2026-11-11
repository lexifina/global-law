import TaxCode.Model
import TaxCode.Checks
import TaxCode.Individual.Household
import TaxCode.Individual.Form1040
import TaxCode.Individual.A.AGI
import TaxCode.Individual.A.Adjustments
import TaxCode.Individual.A.SelfEmployment
import TaxCode.Individual.A.SocialSecurity
import TaxCode.Individual.A.Tests
import TaxCode.Individual.B.Axioms
import TaxCode.Individual.B.Deductions
import TaxCode.Individual.B.Forms
import TaxCode.Individual.B.Properties
import TaxCode.Individual.C.AMT
import TaxCode.Individual.C.All
import TaxCode.Individual.C.CapitalGains
import TaxCode.Individual.C.Schedule
import TaxCode.Individual.C.Table
import TaxCode.Individual.D.Axioms
import TaxCode.Individual.D.Basic
import TaxCode.Individual.D.ChildTaxCredit
import TaxCode.Individual.D.DependentCare
import TaxCode.Individual.D.EICTableData
import TaxCode.Individual.D.EarnedIncome
import TaxCode.Individual.D.Education
import TaxCode.Individual.D.Ordering
import TaxCode.Individual.D.PremiumTaxCredit
import TaxCode.Individual.D.Saver

/-! Root of the `TaxCode` library: the Title 26 drafting checks and the 2025 individual income tax.

The two command-line runners (`TaxCode/Main.lean`, `TaxCode/Individual/Run.lean`) each define `main`, so they are
run with `lake env lean --run` rather than imported here. The certificates are the separate `TaxCodeCerts` library. -/
