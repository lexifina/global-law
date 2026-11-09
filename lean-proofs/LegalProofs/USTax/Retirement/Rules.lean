/-!
# Retirement-account rules, as enacted (tax year 2025)

One person's retirement accounts for one year, and the moves the Code allows between them. Each move is written from the
provision that governs it, with the 2025 figures (IRS Notice 2024-80). Nothing here mentions a "backdoor" or any other
planning technique: the file only says what each provision permits and what it taxes. Whether the provisions, put
together, let a high earner do what one of them forbids is left to the search (`Search.lean`) and the theorems
(`Theorems.lean`).

Simplifications, each stated once here:
* one taxable year, no investment growth inside the accounts (so the only basis questions are about contributions);
* the person is an active participant in a workplace plan (§219(g)(5)) whose plan accepts after-tax contributions and
  allows in-plan Roth rollovers (both are plan-design choices the Code permits, §§402A(c)(4), 415(c));
* no employer contributions; no catch-up contributions; single filer.
-/

namespace Legal.USTax.Retirement

/-! ## 2025 figures -/

/-- §219(b)(5)(A), indexed: the IRA contribution limit, shared by traditional and Roth IRAs (§408A(c)(2)). -/
def iraLimit : Nat := 7000
/-- §408A(c)(3): the Roth contribution phase-out range for a single filer. -/
def rothLo : Nat := 150000
def rothHi : Nat := 165000
/-- §219(g)(3)(B): the deduction phase-out range for an active participant filing single. -/
def dedLo : Nat := 79000
def dedHi : Nat := 89000
/-- §402(g)(1): elective deferrals. -/
def deferralLimit : Nat := 23500
/-- §415(c)(1)(A): all annual additions to a defined contribution plan. -/
def additionsLimit : Nat := 70000

/-- Round down to a multiple of $10, and raise a positive amount below $200 to $200 (§219(g)(2)(B)–(C), applied to
the Roth limit by §408A(c)(3)(A)). -/
def roundLimit (x : Nat) : Nat := if x = 0 then 0 else max 200 (x / 10 * 10)

/-- §408A(c)(3)(A): the most that may be contributed to a Roth IRA, reduced ratably across the phase-out range. -/
def rothLimit (magi : Nat) : Nat :=
  if magi ≤ rothLo then iraLimit
  else if rothHi ≤ magi then 0
  else roundLimit (iraLimit * (rothHi - magi) / (rothHi - rothLo))

/-- §219(g)(2): the deductible part of a traditional IRA contribution for an active participant. -/
def dedLimit (magi : Nat) : Nat :=
  if magi ≤ dedLo then iraLimit
  else if dedHi ≤ magi then 0
  else roundLimit (iraLimit * (dedHi - magi) / (dedHi - dedLo))

/-! ## Accounts -/

structure Acct where
  ira : Nat           -- every traditional IRA, aggregated: §408(d)(2)(A) treats them as one contract
  basis : Nat         -- investment in the contract (§72): nondeductible contributions, §408(o)
  plan : Nat          -- pre-tax 401(k) balance
  planAfterTax : Nat  -- after-tax employee contributions held in the 401(k): basis inside the plan
  roth : Nat          -- Roth IRA and designated Roth account together
  cash : Nat          -- money outside every account
  iraContrib : Nat    -- IRA contributions made for the year (traditional and Roth share one limit)
  deferrals : Nat     -- elective deferrals for the year
  additions : Nat     -- annual additions to the plan for the year
  deducted : Nat      -- IRA contributions deducted under §219
  taxed : Nat         -- amounts included in gross income by these moves
  deriving DecidableEq, Repr, Hashable

/-- The moves. Amounts are whole dollars. -/
inductive Act where
  | rothContrib (a : Nat)    -- contribute to a Roth IRA, §408A(c)
  | tradContrib (a : Nat)    -- contribute to a traditional IRA, §219 / §408(o)
  | convert (a : Nat)        -- qualified rollover contribution from a traditional to a Roth IRA, §408A(d)(3)
  | rollIn (a : Nat)         -- roll IRA money into the 401(k), §408(d)(3)(A)(ii)
  | defer (a : Nat)          -- elective deferral to the 401(k), §402(g)
  | afterTax (a : Nat)       -- after-tax employee contribution to the 401(k), §415(c)
  | inPlanRoth (a : Nat)     -- in-plan rollover of after-tax money to the designated Roth account, §402A(c)(4)
  deriving DecidableEq, Repr

/-- One move, if the Code allows it. -/
def step (magi : Nat) (s : Acct) : Act → Option Acct
  | .rothContrib a =>
    if 0 < a ∧ a ≤ s.cash ∧ s.iraContrib + a ≤ rothLimit magi ∧ s.iraContrib + a ≤ iraLimit then
      some { s with cash := s.cash - a, roth := s.roth + a, iraContrib := s.iraContrib + a }
    else none
  | .tradContrib a =>
    -- §408(o): any part that may not be deducted may still be contributed, and becomes basis
    if 0 < a ∧ a ≤ s.cash ∧ s.iraContrib + a ≤ iraLimit then
      let d := min a (dedLimit magi - min (dedLimit magi) s.deducted)
      some { s with cash := s.cash - a, ira := s.ira + a, basis := s.basis + (a - d),
                    iraContrib := s.iraContrib + a, deducted := s.deducted + d }
    else none
  | .convert a =>
    -- §408(d)(1)–(2), §72: the distribution carries basis in proportion to the whole of all IRAs
    if 0 < a ∧ a ≤ s.ira then
      let n := a * s.basis / s.ira
      some { s with ira := s.ira - a, basis := s.basis - n, roth := s.roth + a, taxed := s.taxed + (a - n) }
    else none
  | .rollIn a =>
    -- §408(d)(3)(A)(ii): only the part that would be includible may go to a plan; §408(d)(3)(H): that part is taken
    -- from income first, so the basis stays behind in the IRA
    if 0 < a ∧ a ≤ s.ira - s.basis then some { s with ira := s.ira - a, plan := s.plan + a } else none
  | .defer a =>
    if 0 < a ∧ a ≤ s.cash ∧ s.deferrals + a ≤ deferralLimit ∧ s.additions + a ≤ additionsLimit then
      some { s with cash := s.cash - a, plan := s.plan + a, deferrals := s.deferrals + a, additions := s.additions + a }
    else none
  | .afterTax a =>
    if 0 < a ∧ a ≤ s.cash ∧ s.additions + a ≤ additionsLimit then
      some { s with cash := s.cash - a, planAfterTax := s.planAfterTax + a, additions := s.additions + a }
    else none
  | .inPlanRoth a =>
    -- §402A(c)(4): taxable only to the extent it would be includible; after-tax contributions are basis
    if 0 < a ∧ a ≤ s.planAfterTax then
      some { s with planAfterTax := s.planAfterTax - a, roth := s.roth + a }
    else none

/-- A sequence of moves; `none` as soon as one is not allowed. -/
def run (magi : Nat) : Acct → List Act → Option Acct
  | s, [] => some s
  | s, a :: as => (step magi s a).bind (run magi · as)

end Legal.USTax.Retirement
