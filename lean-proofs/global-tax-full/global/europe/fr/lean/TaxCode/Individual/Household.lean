/-!
# A household's return, tax year 2025

The inputs every provision of the individual income tax reads, and the schedule of figures the computation produces.
All amounts are whole dollars (`Int`). Each provision lives in its own file under `TaxCode/Individual/` and reads
only these fields; the order of computation follows the Code (gross income, adjusted gross income, taxable income,
tax, credits), which is also the order of Form 1040.

Tax year 2025, as amended by Pub. L. 119-21 (4 July 2025). Parameters cite Rev. Proc. 2024-40 as modified by Pub. L.
119-21 and Rev. Proc. 2025-32 where the 2025 Act changed them.
-/

namespace TaxCode.Individual

inductive Filing where
  | single | mfj | mfs | hoh | qss   -- qualifying surviving spouse
  deriving DecidableEq, Repr, Inhabited

structure Person where
  age : Nat
  blind : Bool := false
  deriving DecidableEq, Repr, Inhabited

structure Dependent where
  age : Nat
  ssn : Bool := true          -- §24(h)(7): SSN required for the child tax credit
  student : Bool := false     -- full-time student (§152(c)(3)(A)(ii))
  disabled : Bool := false
  monthsWithTaxpayer : Nat := 12
  deriving DecidableEq, Repr, Inhabited

structure Household where
  filing : Filing
  head : Person
  spouse : Option Person := none
  dependents : List Dependent := []
  canBeClaimedAsDependent : Bool := false
  -- income
  wages : Int := 0                 -- Form W-2 box 1 (both spouses)
  wagesSpouse : Int := 0           -- the spouse's share of `wages` (for per-person limits)
  seIncome : Int := 0              -- net earnings from self-employment before §1402(a)(12)
  taxableInterest : Int := 0
  taxExemptInterest : Int := 0
  ordinaryDividends : Int := 0
  qualifiedDividends : Int := 0    -- included in ordinaryDividends
  shortTermGains : Int := 0        -- net
  longTermGains : Int := 0         -- net (28% and §1250 gain not modelled)
  iraDistributions : Int := 0      -- taxable amount
  pensions : Int := 0              -- taxable amount
  socialSecurity : Int := 0        -- gross benefits (Form SSA-1099 box 5)
  unemployment : Int := 0
  otherIncome : Int := 0
  qbi : Int := 0                   -- qualified business income (non-SSTB, below the §199A thresholds' complications)
  -- adjustments and deductions
  iraContributions : Int := 0      -- traditional IRA contributions (both spouses)
  activeParticipant : Bool := false
  hsaContributions : Int := 0
  studentLoanInterest : Int := 0
  educatorExpenses : Int := 0
  qualifiedTips : Int := 0         -- §224
  qualifiedOvertime : Int := 0     -- §225: the premium portion only
  carLoanInterest : Int := 0       -- §163(h)(4)
  stateLocalTaxes : Int := 0       -- income or sales tax, plus property tax, paid
  mortgageInterest : Int := 0
  charitableCash : Int := 0
  medicalExpenses : Int := 0
  -- credits
  childCareExpenses : Int := 0
  qualifiedTuition : List Int := []  -- per eligible student, first four years (AOTC) — amounts paid
  retirementContributions : Int := 0 -- for §25B (elective deferrals and IRA contributions)
  marketplacePremium : Int := 0      -- annual premium of the plan enrolled in
  benchmarkPremium : Int := 0        -- annual second-lowest-cost silver plan premium for the family
  deriving Repr, Inhabited

def Household.persons (h : Household) : Nat := if h.spouse.isSome then 2 else 1
def Household.married (h : Household) : Bool := h.filing == .mfj || h.filing == .mfs

/-- The figures the computation produces, in Form 1040 order. -/
structure Return where
  grossIncome : Int := 0
  taxableSocialSecurity : Int := 0
  agi : Int := 0
  magi : Int := 0
  standardDeduction : Int := 0
  itemized : Int := 0
  deduction : Int := 0               -- the larger, or itemized if elected
  qbiDeduction : Int := 0
  belowTheLine : Int := 0            -- §§224, 225, 151(f), 163(h)(4) deductions taken after AGI
  taxableIncome : Int := 0
  regularTax : Int := 0
  amt : Int := 0
  nonrefundableCredits : Int := 0
  seTax : Int := 0
  niit : Int := 0
  additionalMedicare : Int := 0
  totalTax : Int := 0
  refundableCredits : Int := 0
  -- itemised components and credits, for testing each provision on its own
  ctc : Int := 0
  actc : Int := 0
  odc : Int := 0
  eitc : Int := 0
  cdcc : Int := 0
  aotcNonref : Int := 0
  aotcRef : Int := 0
  llc : Int := 0
  saver : Int := 0
  ptc : Int := 0
  deriving Repr, Inhabited

/-- `rate` basis points of `x`, rounded down. -/
def bp (x : Int) (rate : Int) : Int := x * rate / 10000

/-- Round to the nearest dollar, half up. -/
def roundDollar (num den : Int) : Int := (2 * num + den) / (2 * den)

end TaxCode.Individual
