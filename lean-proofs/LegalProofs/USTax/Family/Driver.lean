import LegalProofs.USTax.Family.Kiddie
import LegalProofs.USTax.Family.Trust

/-!
# A family over many years

Two parents, their children, and optionally one non-grantor trust for the children, followed year by year from now to
the parents' death, with every year's income tax computed by the 2025 household model (`TaxCode/Individual`), the kiddie
tax (`Kiddie.lean`) and the trust rules (`Trust.lean`).

**The law is the 2025 law in every year.** All amounts are in real (2025) dollars: wages, spending, returns and
balances are real, and the 2025 brackets, thresholds and limits are held fixed in real terms, which is what indexing
does for the indexed figures. The figures that are not indexed (the §1411 thresholds, the §86 base amounts, the §1(g)
amounts are indexed but the $250,000 NIIT threshold is not) are therefore treated as if they were; and the 2026-and-later
changes of Pub. L. 119-21 and of earlier law (the 2026 premium tax credit cliff, the §170 floor, the §68 limit, the
SALT phase-down's end in 2030) are out of scope. Every result below is "under 2025 law, forever".

What a year does, in order:

1. Pay last year's taxes. A tax is paid the year after it accrues (returns are filed in April). Parents pay from cash
   flow, then by selling shares; a child or the trust sells shares. Distributions the trust decided for last year are
   paid now too (§663(b) lets a distribution in the first 65 days count for the year before) and the child reinvests
   them. Every sale realises gain in proportion to basis (average basis, held over a year).
2. Gifts at the start of the year: shares (at their value, with the donor's basis, §1015) to a child's account or to
   the trust. Gifts above the $19,000 annual exclusion per donor and donee (§2503(b), split by the spouses, §2513) use
   unified credit and are added back at death (§2001(b)).
3. Income: wages, the head's business profit (Schedule C) less wages paid to the children, Social Security from the
   claiming age, required minimum distributions (§401(a)(9), Uniform Lifetime Table, on last year-end's balance),
   Roth conversions (§408A(d)(3): the converted amount is a taxable distribution; tax is paid from outside the IRA),
   dividends and interest on every taxable account. Charitable gifts (cash, or shares, which realise no gain,
   §170(e)(1) with long-term capital gain property). Wanted gain realisations ("harvest": sell and buy back; §1091 does
   not reach gains).
4. Returns: the parents' (joint, or two separate ones with the joint account split equally and the children claimed by
   the head; both itemise or neither, §63(c)(6)(A)); each child's (a dependent while under 19 or a student under 24),
   with §1(g) when it applies and the parent's election under §1(g)(7) if made; the trust's, with each child's §662
   inclusion carried into that child's return.
5. Growth: shares grow by the price return; IRAs and Roth accounts by the total return.

At the horizon the parents die together. Their taxable account takes a basis equal to its value (§1014); the estate tax
is 40% of the estate (every account, plus gifts over the exclusions) above two exclusions of $13,990,000 (portability,
§2010(c)(4)). The children inherit equally. An inherited traditional IRA is withdrawn over ten years (§401(a)(9)(H)) on
top of the child's own wage; a child's (and the trust's, distributed in kind, §643(e)) unrealised gain is taxed as if
sold over ten years the same way; Roth accounts are tax-free. The family's after-tax wealth is what is left.
-/

namespace Legal.USTax.Family
open TaxCode.Individual

/-! ## Inputs -/

structure Acct where
  value : Int
  basis : Int
  deriving Repr, Inhabited, DecidableEq

structure ParentSpec where
  age : Nat
  wage : Int := 0
  ira : Int := 0
  roth : Int := 0
  ss : Int := 0           -- annual Social Security benefit once claimed
  ssAge : Nat := 67
  rmdAge : Nat := 75      -- §401(a)(9)(C)(v): 75 for those born after 1959
  retireAge : Nat := 65
  deriving Repr, Inhabited

structure KidSpec where
  age : Nat
  studentThrough : Nat := 22   -- a full-time student through this age
  adultWage : Int := 50000     -- the child's own wage from the year after
  support : Int := 25000       -- total support each year while a dependent
  deriving Repr, Inhabited

structure Spec where
  head : ParentSpec
  spouse : ParentSpec
  brokerage : Acct
  business : Int := 0          -- the head's Schedule C profit while working, before wages paid to the children
  spending : Int
  charity : Int := 0           -- the family's cash gifts to charity each year
  mortgage : Int := 0
  salt : Int := 0
  kids : List KidSpec
  growthBp : Int               -- real price return on shares (basis points)
  divBp : Int                  -- qualified dividend yield
  intBp : Int                  -- taxable interest yield
  premium : Int := 0           -- marketplace premium (= benchmark) while the head is under 65
  horizon : Nat
  gainsInDni : Bool := false   -- the trust instrument allocates capital gains to income
  kidWageCap : List (Nat × Int) := []  -- (age from which, most the business could reasonably pay a child)
  deriving Repr, Inhabited

/-- The choices for one year. Lists are per child, in the order of `Spec.kids`; a missing entry means none. -/
structure YearPlan where
  convH : Int := 0             -- convert this much of the head's IRA
  convS : Int := 0
  convTo : Int := 0            -- if positive: convert (head's IRA first) until the parents' taxable income reaches this
  harvestTo : Int := 0         -- if positive: parents realise gain until their taxable income reaches this
  gifts : List Int := []       -- shares given to each child's account
  trustFund : Int := 0         -- shares given to the trust
  trustDistBp : List Int := [] -- each child's distribution, in basis points of the trust's DNI for the year
  trustHarvestTo : Int := 0    -- if positive: the trust realises gain until its taxable income reaches this
  kidWage : List Int := []     -- wages the head's business pays each child
  kidRoth : List Bool := []    -- the child puts what it can of its wage in a Roth IRA (§408A(c)(2), §219(b)(1))
  kidHarvestTo : List Int := []
  form8814 : List Bool := []
  charity : Int := -1          -- −1: the usual amount
  charityShares : Bool := false
  mfs : Bool := false
  deriving Repr, Inhabited

/-! ## Constants (2025) -/

def giftExclusion : Int := 19000          -- §2503(b), Rev. Proc. 2024-40 §2.43
def estateExclusion : Int := 13990000     -- §2010(c)(3), Rev. Proc. 2024-40 §2.41
def kidRothLimit : Int := 7000            -- §219(b)(5)(A)

/-- Uniform Lifetime Table (Treas. Reg. §1.401(a)(9)-9(c)), distribution period in tenths, ages 72–100; 6.4 after. -/
def ult : List Int := [274, 265, 255, 246, 237, 229, 220, 211, 202, 194, 185, 177, 168, 160, 152, 144, 137, 129, 122,
  115, 108, 101, 95, 89, 84, 78, 73, 68, 64]

def rmdFor (age : Nat) (rmdAge : Nat) (bal : Int) : Int :=
  if age < rmdAge || bal ≤ 0 then 0 else bal * 10 / (ult.getD (age - 72) 64)

/-! ## Helpers -/

def pctBp (x r : Int) : Int := x * r / 10000

/-- Sell shares for cash `x`: returns the account after the sale and the gain realised. -/
def sell (a : Acct) (x : Int) : Acct × Int :=
  if x ≤ 0 then (a, 0) else
  if a.value ≤ 0 then ({ a with value := a.value - x }, 0) else
  let take := min x a.value
  let b := a.basis * take / a.value
  ({ value := a.value - x, basis := a.basis - b }, take - b)

/-- Move shares worth `x` out of an account (a gift): the value and a proportional basis leave together. If the
account holds less than `x` of shares, the rest is given in cash (which is its own basis) and the account goes into
debt by that much. -/
def carve (a : Acct) (x : Int) : Acct × Acct :=
  if x ≤ 0 then (a, ⟨0, 0⟩) else
  let take := min x (max 0 a.value)
  let b := if a.value ≤ 0 then 0 else a.basis * take / a.value
  (⟨a.value - x, a.basis - b⟩, ⟨x, b + (x - take)⟩)

def buy (a : Acct) (x : Int) : Acct := { value := a.value + x, basis := a.basis + x }

/-- Cash `c` in or out: buy shares with a surplus, sell for a shortfall. Returns the account and the gain realised. -/
def settle (a : Acct) (c : Int) : Acct × Int := if 0 ≤ c then (buy a c, 0) else sell a (-c)

def unrealised (a : Acct) : Int := max 0 (a.value - a.basis)

/-- Taxable income alone (no credits, no AMT): enough to aim at a target. -/
def tiOnly (h : Household) (f : B.Facts := {}) : Int :=
  let h := withScheduleCQbi h
  B.taxableIncome h (A.agi h) f

/-- The largest `x` in `[0, cap]` (to within `cap / 2^18`) with `ti (bump x) ≤ target`, by bisection; the taxable income
of `bump x` never falls as `x` grows in every use below. -/
def aim (ti : Int → Int) (target cap : Int) : Int :=
  if cap ≤ 0 || target ≤ ti 0 then 0 else if ti cap ≤ target then cap else
  let rec go : Nat → Int → Int → Int
    | 0, lo, _ => lo
    | n + 1, lo, hi => if hi - lo ≤ 1 then lo else
      let mid := (lo + hi) / 2
      if ti mid ≤ target then go n mid hi else go n lo mid
  go 18 0 cap

/-! ## State -/

structure St where
  brok : Acct
  iraH : Int
  iraS : Int
  rothH : Int
  rothS : Int
  kid : List Acct
  kidRoth : List Int
  trust : Acct
  owePar : Int := 0
  oweKid : List Int
  oweTrust : Int := 0
  trustPay : List Int
  carryCash : Int := 0         -- §170(d)(1) carryover of cash gifts
  carryShares : Int := 0       -- §170(b)(1)(C)(ii) carryover of share gifts, still under the 30% limit
  giftsOver : Int := 0
  taxPaid : Int := 0            -- every income and payroll tax accrued so far, all taxpayers
  payrollKids : Int := 0
  deriving Repr, Inhabited

def St.init (s : Spec) : St :=
  let n := s.kids.length
  { brok := s.brokerage, iraH := s.head.ira, iraS := s.spouse.ira, rothH := s.head.roth, rothS := s.spouse.roth,
    kid := List.replicate n ⟨0, 0⟩, kidRoth := List.replicate n 0, trust := ⟨0, 0⟩,
    oweKid := List.replicate n 0, trustPay := List.replicate n 0 }

/-- A child is the parents' dependent (qualifying child, §152(c)(3)) while under 19, or a student under 24. -/
def isDependent (k : KidSpec) (age : Nat) : Bool := age < 19 || (age ≤ k.studentThrough && age < 24)

def kidWageCapAt (s : Spec) (age : Nat) : Int :=
  (s.kidWageCap.filter (fun p => p.1 ≤ age)).foldl (fun _ p => p.2) 0

/-- Zip helpers that tolerate short plan lists. -/
def getI (l : List Int) (i : Nat) : Int := l.getD i 0
def getB (l : List Bool) (i : Nat) : Bool := l.getD i false

/-! ## The parents' return(s) -/

structure ParentsYear where
  tax : Int           -- income tax net of refundable credits, SE tax, NIIT, additional Medicare, + Form 8814 amounts
  pf : Filing         -- the filing status of the §1(g)(5) parent
  pti : Int           -- that parent's taxable income
  pcg : Int           -- that parent's qualified dividends and net capital gain
  deriving Repr

def personOf (age : Nat) : Person := { age := age }

/-- Split a joint household into two separate ones: each spouse's own items stay theirs; the joint account's income,
the deductions and the charity are split equally; the children go with the head. -/
def splitHousehold (h : Household) (wH wS ssH ssS iraDH iraDS : Int) : Household × Household :=
  let half (x : Int) := x / 2
  let a : Household := { h with
      filing := .mfs, spouse := none, wages := wH, wagesSpouse := 0, socialSecurity := ssH,
      iraDistributions := iraDH,
      taxableInterest := half h.taxableInterest, ordinaryDividends := half h.ordinaryDividends,
      qualifiedDividends := half h.qualifiedDividends, longTermGains := half h.longTermGains,
      stateLocalTaxes := half h.stateLocalTaxes, mortgageInterest := half h.mortgageInterest,
      charitableCash := half h.charitableCash, marketplacePremium := 0, benchmarkPremium := 0 }
  let b : Household := { h with
      filing := .mfs, head := h.spouse.getD default, spouse := none, dependents := [],
      wages := wS, wagesSpouse := 0, seIncome := 0, qbi := 0, socialSecurity := ssS, iraDistributions := iraDS,
      taxableInterest := h.taxableInterest - half h.taxableInterest,
      ordinaryDividends := h.ordinaryDividends - half h.ordinaryDividends,
      qualifiedDividends := h.qualifiedDividends - half h.qualifiedDividends,
      longTermGains := h.longTermGains - half h.longTermGains,
      stateLocalTaxes := h.stateLocalTaxes - half h.stateLocalTaxes,
      mortgageInterest := h.mortgageInterest - half h.mortgageInterest,
      charitableCash := h.charitableCash - half h.charitableCash, marketplacePremium := 0, benchmarkPremium := 0 }
  (a, b)

def parentsReturn (h : Household) (mfs : Bool) (wH wS ssH ssS iraDH iraDS : Int) : ParentsYear :=
  if !mfs then
    let l := form1040 h
    ⟨l.netTax, .mfj, l.taxableIncome, B.netCapitalGain h⟩
  else
    let (a, b) := splitHousehold h wH wS ssH ssS iraDH iraDS
    let both (e : Bool) := (form1040With { electItemize := some e } a, form1040With { electItemize := some e } b)
    let (la, lb) := both true
    let (la', lb') := both false
    let (la, lb) := if la'.netTax + lb'.netTax ≤ la.netTax + lb.netTax then (la', lb') else (la, lb)
    if lb.taxableIncome > la.taxableIncome then ⟨la.netTax + lb.netTax, .mfs, lb.taxableIncome, B.netCapitalGain b⟩
    else ⟨la.netTax + lb.netTax, .mfs, la.taxableIncome, B.netCapitalGain a⟩

/-! ## One year -/

structure YearLog where
  parents : Int
  kids : Int
  trust : Int
  conv : Int
  harvest : Int
  brok : Int          -- the parents' taxable account at the end of the year (negative: debt)
  deriving Repr

def kidHousehold (k : KidSpec) (age : Nat) (wage : Int) : Household :=
  { filing := .single, head := personOf age, canBeClaimedAsDependent := isDependent k age, wages := wage }

def year (s : Spec) (p : YearPlan) (y : Nat) (st : St) : St × YearLog :=
  let n := s.kids.length
  let ageH := s.head.age + y
  let ageS := s.spouse.age + y
  let working := ageH < s.head.retireAge
  let kAges := s.kids.map (·.age + y)
  -- 1. last year's trust bills: the trust sells for its tax and the distributions it decided
  let (trust1, gT1) := sell st.trust (st.oweTrust + st.trustPay.sum)
  -- 2. gifts
  let (brok1, giftAccts) := (List.range n).foldl (fun (acc : Acct × List Acct) i =>
      let (b, g) := carve acc.1 (getI p.gifts i); (b, acc.2 ++ [g])) (st.brok, [])
  let (brok2, toTrust) := carve brok1 p.trustFund
  let giftsOver := st.giftsOver + (List.range n).foldl (fun t i => t + max 0 (getI p.gifts i - 2 * giftExclusion)) 0
    + max 0 p.trustFund   -- §2503(b)(1): a discretionary trust's beneficiaries hold future interests; no exclusion
  let trust2 : Acct := ⟨trust1.value + toTrust.value, trust1.basis + toTrust.basis⟩
  -- children's accounts: receive gifts and last year's distributions, pay last year's tax
  let kidPre := (List.range n).map fun i =>
    let a := st.kid.getD i ⟨0, 0⟩
    let g := giftAccts.getD i ⟨0, 0⟩
    let a := buy ⟨a.value + g.value, a.basis + g.basis⟩ (getI st.trustPay i)
    sell a (getI st.oweKid i)
  -- 3. the parents' income
  let kidWages := (List.range n).map fun i =>
    if working && s.business > 0 then max 0 (min (getI p.kidWage i) (kidWageCapAt s (kAges.getD i 0))) else 0
  -- §3121(b)(3)(A): no FICA on a sole proprietor's child under 18; otherwise 7.65% from each side
  let employerFica := (List.range n).foldl (fun t i => t + if kAges.getD i 0 < 18 then 0 else pctBp (getI kidWages i) 765) 0
  let business := if working then s.business - kidWages.sum - employerFica else 0
  let wH := if working then s.head.wage else 0
  let wS := if ageS < s.spouse.retireAge then s.spouse.wage else 0
  let ssH := if ageH ≥ s.head.ssAge then s.head.ss else 0
  let ssS := if ageS ≥ s.spouse.ssAge then s.spouse.ss else 0
  let rmdH := rmdFor ageH s.head.rmdAge st.iraH
  let rmdS := rmdFor ageS s.spouse.rmdAge st.iraS
  let charityAmt := if p.charity < 0 then s.charity else p.charity
  let (brok3, _) := if p.charityShares then carve brok2 charityAmt else (brok2, ⟨0, 0⟩)
  let div := pctBp (max 0 brok3.value) s.divBp
  let int := pctBp (max 0 brok3.value) s.intBp
  let charityCash := if p.charityShares then 0 else charityAmt
  let premium := if ageH < 65 then s.premium else 0
  let cash := wH + wS + business + ssH + ssS + rmdH + rmdS + div + int - s.spending - charityCash - st.owePar - premium
  let (brok4, gSale) := settle brok3 cash
  let iraH1 := st.iraH - rmdH
  let iraS1 := st.iraS - rmdS
  let deps : List Dependent := (List.range n).filterMap fun i =>
    let a := kAges.getD i 0
    if isDependent (s.kids.getD i default) a then some { age := a, student := decide (19 ≤ a) } else none
  let base (convH convS harvest : Int) (charityDed : Int) : Household :=
    { filing := .mfj, head := personOf ageH, spouse := some (personOf ageS), dependents := deps,
      wages := wH + wS, wagesSpouse := wS, seIncome := business, taxableInterest := int, ordinaryDividends := div,
      qualifiedDividends := div, longTermGains := gSale + harvest, socialSecurity := ssH + ssS,
      iraDistributions := rmdH + rmdS + convH + convS, stateLocalTaxes := s.salt, mortgageInterest := s.mortgage,
      charitableCash := charityDed, marketplacePremium := premium, benchmarkPremium := premium }
  -- charity: shares are limited to 30% of AGI (§170(b)(1)(C)), cash to 60% (in the model); the excess carries over
  let agi0 := A.agi (withScheduleCQbi (base p.convH p.convS 0 0))
  let shareAll := (if p.charityShares then charityAmt else 0) + st.carryShares
  let shareDed := min shareAll (max 0 (agi0 * 30 / 100))
  let cashAll := charityCash + st.carryCash
  let cashDed := min cashAll (max 0 (agi0 * 60 / 100 - shareDed))
  let charityDed := shareDed + cashDed
  -- Roth conversions
  let convFix := (min p.convH iraH1, min p.convS iraS1)
  let convTot := if p.convTo > 0 then
      aim (fun x => tiOnly (base (convFix.1 + x) convFix.2 0 charityDed)) p.convTo
        (iraH1 - convFix.1 + iraS1 - convFix.2)
    else 0
  let extraH := min convTot (iraH1 - convFix.1)
  let convH := convFix.1 + extraH
  let convS := convFix.2 + (convTot - extraH)
  -- gain harvesting
  let harvest := if p.harvestTo > 0 then
      aim (fun x => tiOnly (base convH convS x charityDed)) p.harvestTo (unrealised brok4) else 0
  let brok5 := { brok4 with basis := brok4.basis + harvest }
  -- §1(g)(7) elections fold the children's interest and dividends into the parents' return
  let kidDiv := (List.range n).map fun i => pctBp ((kidPre.getD i default).1.value) s.divBp
  let kidInt := (List.range n).map fun i => pctBp ((kidPre.getD i default).1.value) s.intBp
  -- 4. the trust
  let tDiv := pctBp trust2.value s.divBp
  let tInt := pctBp trust2.value s.intBp
  let tIncome0 : TrustIncome := ⟨tInt, tDiv, tDiv, gT1, 0⟩
  let tHarvest := if p.trustHarvestTo > 0 then
      aim (fun x => (trustReturn s.gainsInDni { tIncome0 with ltGain := gT1 + x } []).taxableIncome) p.trustHarvestTo
        (unrealised trust2) else 0
  let tIncome := { tIncome0 with ltGain := gT1 + tHarvest }
  let tDni := dni s.gainsInDni tIncome
  let dists := (List.range n).map fun i => if trust2.value ≤ 0 then 0 else min (trust2.value) (tDni * getI p.trustDistBp i / 10000)
  let tr := trustReturn s.gainsInDni tIncome dists
  let trust3 : Acct := ⟨trust2.value + tDiv + tInt, trust2.basis + tDiv + tInt + tHarvest⟩
  -- the children's households (before §1(g))
  let kidH := (List.range n).map fun i =>
    let k := s.kids.getD i default
    let a := kAges.getD i 0
    let ownWage := if isDependent k a then 0 else k.adultWage
    let hh := kidHousehold k a (ownWage + getI kidWages i)
    let hh := { hh with taxableInterest := getI kidInt i, ordinaryDividends := getI kidDiv i,
                        qualifiedDividends := getI kidDiv i, longTermGains := (kidPre.getD i default).2 }
    addCarry hh (tr.carries.getD i {})
  let kidHarv := (List.range n).map fun i =>
    let t := getI p.kidHarvestTo i
    if t > 0 then aim (fun x => tiOnly { (kidH.getD i default) with longTermGains := (kidH.getD i default).longTermGains + x }) t
      (unrealised (kidPre.getD i default).1) else 0
  let kidH := (List.range n).map fun i =>
    let hh := kidH.getD i default
    { hh with longTermGains := hh.longTermGains + getI kidHarv i }
  let kidFacts := (List.range n).map fun i =>
    let k := s.kids.getD i default
    let a := kAges.getD i 0
    ({ age := a, student := decide (a ≤ k.studentThrough), earned := B.earnedIncome (kidH.getD i default),
       support := k.support } : ChildFacts)
  let elect := (List.range n).map fun i =>
    !p.mfs && getB p.form8814 i && form8814Eligible (kidFacts.getD i default) (kidH.getD i default)
  let parentsH := (List.range n).foldl (fun h i => if getB elect i then form8814Include h (kidH.getD i default) else h)
    (base convH convS harvest charityDed)
  let extra8814 := (List.range n).foldl (fun t i =>
    let c := kidH.getD i default
    t + if getB elect i then form8814Tax (c.taxableInterest + c.ordinaryDividends + c.longTermGains) else 0) 0
  let py := parentsReturn parentsH p.mfs wH wS ssH ssS (rmdH + convH) (rmdS + convS)
  let parentsTax := py.tax + extra8814
  -- each child's return; §1(g) with all the parent's §1(g) children
  let kidLines := (List.range n).map fun i => form1040With {} (kidH.getD i default)
  let subj := (List.range n).map fun i => (kidFacts.getD i default).subject && !getB elect i
  let lines : List ChildLine := (List.range n).filterMap fun i =>
    if getB subj i then
      let hh := kidH.getD i default
      let l := kidLines.getD i default
      let nui := netUnearned hh l.taxableIncome
      some ⟨l.taxableIncome, nui, childQdcg hh, nuiQdcg hh nui⟩
    else none
  let kidTax := (List.range n).map fun i =>
    if getB elect i then 0 else
    let hh := kidH.getD i default
    let l := kidLines.getD i default
    if getB subj i then
      let nui := netUnearned hh l.taxableIncome
      let me : ChildLine := ⟨l.taxableIncome, nui, childQdcg hh, nuiQdcg hh nui⟩
      childTotal hh l true (kiddieTax py.pf py.pti py.pcg lines me)
    else
      -- an adult child's tax on their own wage is theirs, the same in every plan: only the excess is the family's
      let k := s.kids.getD i default
      let a := kAges.getD i 0
      if isDependent k a then l.netTax
      else l.netTax - (form1040With {} (kidHousehold k a k.adultWage)).netTax
  let payrollK := (List.range n).foldl (fun t i => t + if kAges.getD i 0 < 18 then 0 else 2 * pctBp (getI kidWages i) 765) 0
  -- the children's accounts: income reinvested, wages saved (Roth first if chosen)
  let kidRothAdd := (List.range n).map fun i =>
    if getB p.kidRoth i then min kidRothLimit (max 0 (getI kidWages i - pctBp (getI kidWages i) 765 *
      (if kAges.getD i 0 < 18 then 0 else 1))) else 0
  let kid2 := (List.range n).map fun i =>
    let a := (kidPre.getD i default).1
    let w := getI kidWages i - (if kAges.getD i 0 < 18 then 0 else pctBp (getI kidWages i) 765)
    let a := buy a (getI kidDiv i + getI kidInt i + w - getI kidRothAdd i)
    { a with basis := a.basis + getI kidHarv i }
  -- 5. growth
  let g := s.growthBp
  let tot := s.growthBp + s.divBp + s.intBp
  -- a negative balance is debt: it compounds at the total return and is never deductible
  let grow (a : Acct) : Acct := { a with value := a.value + pctBp a.value (if a.value < 0 then tot else g) }
  let total := parentsTax + kidTax.sum + tr.total + payrollK
  ({ brok := grow brok5, iraH := (iraH1 - convH) + pctBp (iraH1 - convH) tot,
     iraS := (iraS1 - convS) + pctBp (iraS1 - convS) tot,
     rothH := (st.rothH + convH) + pctBp (st.rothH + convH) tot,
     rothS := (st.rothS + convS) + pctBp (st.rothS + convS) tot,
     kid := kid2.map grow,
     kidRoth := (List.range n).map fun i => let r := getI st.kidRoth i + getI kidRothAdd i; r + pctBp r tot,
     trust := grow trust3,
     owePar := parentsTax, oweKid := kidTax, oweTrust := tr.total, trustPay := dists,
     carryCash := cashAll - cashDed, carryShares := shareAll - shareDed, giftsOver := giftsOver, taxPaid := st.taxPaid + total,
     payrollKids := st.payrollKids + payrollK },
   ⟨parentsTax, kidTax.sum + payrollK, tr.total, convH + convS, harvest, (grow brok5).value⟩)

/-! ## The horizon -/

structure Outcome where
  wealth : Int          -- after-tax family wealth at the parents' death
  parents : Int         -- the parents' estate after estate tax, before the children's tax on inherited IRAs
  estateTax : Int
  kidsLatentTax : Int   -- tax the children pay withdrawing inherited IRAs and selling what they hold
  kidsHeld : Int        -- the children's own accounts, Roth IRAs and the trust, before that tax
  taxPaid : Int         -- income and payroll tax over the years, every taxpayer
  log : List YearLog
  deriving Repr

/-- Ten equal years of withdrawals `ira` and gains `gain` on top of an adult child's wage: the extra tax. `ird` is the
child's §691(c) deduction (the estate tax attributable to the IRA), taken in step with the withdrawals; it is an
itemized deduction outside the §67 floor (§67(b)(7)) and is entered in the household model's only uncapped itemized
field. -/
def tenYearTax (k : KidSpec) (ira gain ird : Int) : Int :=
  let h0 : Household := { filing := .single, head := personOf 40, wages := k.adultWage }
  let h1 := { h0 with iraDistributions := ira / 10, longTermGains := gain / 10, mortgageInterest := ird / 10 }
  10 * ((form1040 h1).netTax - (form1040 h0).netTax)

def finish (s : Spec) (st : St) (log : List YearLog) : Outcome :=
  let n := s.kids.length
  -- last year's bills
  let brok := { st.brok with value := st.brok.value - st.owePar }
  let (trust, gT) := sell st.trust (st.oweTrust + st.trustPay.sum)
  let kidsG := (List.range n).map fun i =>
    let a := buy (st.kid.getD i ⟨0, 0⟩) (getI st.trustPay i)
    sell a (getI st.oweKid i)
  let kids := kidsG.map (·.1)
  let estate := brok.value + st.iraH + st.iraS + st.rothH + st.rothS
  let estTaxOn (e : Int) := max 0 (e + st.giftsOver - 2 * estateExclusion) * 40 / 100
  let estTax := estTaxOn estate
  -- §691(c): the estate tax attributable to the IRAs, deductible by the heirs as they include them
  let ird := if n = 0 then 0 else (estTax - estTaxOn (estate - st.iraH - st.iraS)) / n
  -- the estate tax is charged to the taxable account first
  let afterEst := estate - estTax
  let iraShare := if n = 0 then 0 else (st.iraH + st.iraS) / n
  let trustShare : Acct := if n = 0 then ⟨0, 0⟩ else ⟨trust.value / n, trust.basis / n⟩
  let latent := (List.range n).foldl (fun t i =>
    let k := s.kids.getD i default
    let a := kids.getD i ⟨0, 0⟩
    -- gains realised by the last sales (the trust's share is split equally) are taxed with the latent gain
    let realised := (kidsG.getD i (⟨0, 0⟩, 0)).2 + (if n = 0 then 0 else gT / n)
    t + tenYearTax k iraShare (unrealised a + unrealised trustShare + realised) ird) 0
  let held := (kids.map (·.value)).sum + st.kidRoth.sum + trust.value
  let wealth := (if n = 0 then afterEst - (st.iraH + st.iraS) * 40 / 100 else afterEst) + held - latent
  ⟨wealth, afterEst, estTax, latent, held, st.taxPaid, log⟩

def simulate (s : Spec) (plan : List YearPlan) : Outcome :=
  let rec go : Nat → List YearPlan → St → List YearLog → St × List YearLog
    | 0, _, st, log => (st, log)
    | k + 1, ps, st, log =>
      let y := s.horizon - (k + 1)
      let (st', l) := year s (ps.headD {}) y st
      go k ps.tail st' (log ++ [l])
  let (st, log) := go s.horizon plan (St.init s) []
  finish s st log

end Legal.USTax.Family
