import UkTax.Person

/-!
# The canonical household (contract `cmp/shared/CONTRACT.md`) under the UK rules

Individuals are taxed separately (there is no joint return). Mapping of the household totals:

* `interest`, `dividends`, `capitalGains`, `rentalIncome`: split equally between two adults (the first takes an
  odd pound). HMRC splits joint accounts equally (gov.uk/apply-tax-free-interest-on-savings: "HMRC will split the
  interest earned equally between the account holders"); jointly held assets of spouses are treated as held in
  equal shares for income tax (ITA 2007 s. 836).
* `charitable`: Gift Aid donations (the amount paid, s. 414), made by the adult with the larger income (the one who
  can use the relief).
* `pensionContributions`: gross personal pension contributions under relief at source (FA 2004 s. 192), the
  amount credited to the pension (the member pays 80 %), shared in proportion to relevant UK earnings.
* Two adults are partners for the child benefit charge whether or not married (ITEPA 2003 s. 681G(3)); only a
  married couple can make the marriage allowance election (s. 55C(1)(a)).
* Children under 20 are counted for child benefit (a child under 16, or a qualifying young person under 20 in
  approved education or training, SSCBA 1992 s. 142; dependants aged 16 to 19 are assumed to qualify).

Elections a couple makes are chosen to minimise the couple's income tax and capital gains tax: the marriage
allowance in either direction or none; the married couple's allowance when either was born before 6 April 1935
(here: aged 90 or more on 6 April 2025), claimed by the spouse with the higher net income (s. 46(2)(e)) with any
unused part transferred (s. 51); a blind spouse's unused allowance always transferred (s. 39).
-/

namespace UkTax

structure Adult where
  age : Nat := 40
  wages : Int := 0
  selfEmployment : Int := 0
  pension : Int := 0
  blind : Bool := false
  deriving Repr, DecidableEq, Inhabited

structure Household where
  id : String := ""
  year : Nat := 2025
  adults : List Adult := []
  married : Bool := false
  children : List Nat := []
  interest : Int := 0
  dividends : Int := 0
  capitalGains : Int := 0
  rentalIncome : Int := 0
  charitable : Int := 0
  pensionContributions : Int := 0
  /-- Extension: the adults are Scottish taxpayers (`"region": "scotland"`). -/
  scottish : Bool := false
  deriving Repr, Inhabited

/-- The first adult's share of an amount split equally (it takes the odd pound). -/
def share1 (x : Int) : Int := x - x / 2
def share2 (x : Int) : Int := x / 2

/-- The persons of a household of one or two adults. -/
def persons (h : Household) : List Person :=
  match h.adults with
  | [a] =>
    [{ age := a.age, blind := a.blind, scottish := h.scottish, employment := a.wages, trading := a.selfEmployment,
       pension := a.pension, property := h.rentalIncome, interest := h.interest, dividends := h.dividends,
       gains := h.capitalGains, giftAid := h.charitable, rasGross := h.pensionContributions }]
  | [a, b] =>
    let base (x : Adult) (k : Int → Int) : Person :=
      { age := x.age, blind := x.blind, scottish := h.scottish, employment := x.wages, trading := x.selfEmployment,
        pension := x.pension, property := k h.rentalIncome, interest := k h.interest, dividends := k h.dividends,
        gains := k h.capitalGains }
    let pa := base a share1
    let pb := base b share2
    -- Gift Aid by the adult with the larger total income
    let aGives := decide (pa.totalIncome ≥ pb.totalIncome)
    -- pension contributions in proportion to relevant UK earnings
    let ea := pos (a.wages + a.selfEmployment)
    let eb := pos (b.wages + b.selfEmployment)
    let pc := h.pensionContributions
    let ca := if ea + eb > 0 then pc * ea / (ea + eb) else share1 pc
    [{ pa with giftAid := if aGives then h.charitable else 0, rasGross := ca },
     { pb with giftAid := if aGives then 0 else h.charitable, rasGross := pc - ca }]
  | _ => []

/-- SSCBA 1992 s. 142 (child under 16, or qualifying young person under 20), see the module note. -/
def cbQualifies (age : Nat) : Bool := decide (age < 20)

/-- S.I. 2006/965 reg. 2(1): the enhanced rate for the eldest child, the other rate for each other child; for the
52 weeks of 2025-26 (pence). Reg. 2(2): partners living together get one enhanced rate between them. -/
def childBenefit (p : Params) (children : List Nat) : Int :=
  let k : Int := (children.filter cbQualifies).length
  if k = 0 then 0 else p.cbWeeks * (p.cbEnhancedWeekly + p.cbOtherWeekly * (k - 1))

/-- **ITEPA 2003 s. 681C**: the charge for adjusted net income `a` (pence) on child benefit `cb` (pence), in pence.
(2): the appropriate percentage is 100 %, or if less `(ANI − L) / X` %; (3): the child benefit total, the
percentage and the charge are each "rounded down to the nearest whole number". s. 681B(1)(a): no charge unless
adjusted net income "exceeds £60,000". -/
def hicbc (p : Params) (a cb : Int) : Int :=
  if a ≤ gbp p.hicbcThreshold then 0
  else
    let pct := min 100 ((a - gbp p.hicbcThreshold) / gbp p.hicbcStep)
    gbp (pct * (cb / 100) / 100)

/-- `--oecd` convention: child benefit for (days in the tax year)/7 weeks (pence, rounded half up): the weekly total
x 365 / 7 (366 / 7 in 2023-24, which contains 29 February 2024). -/
def childBenefitOecd (p : Params) (children : List Nat) : Int :=
  let k : Int := (children.filter cbQualifies).length
  if k = 0 then 0 else (2 * p.taxYearDays * (p.cbEnhancedWeekly + p.cbOtherWeekly * (k - 1)) + 7) / 14

/-- `--oecd` convention: the charge as the continuous share `(ANI − L) / (100 X)` of child benefit, capped at all of
it, rounded to the penny (no rounding of the percentage or of the charge, unlike s. 681C(3)). -/
def hicbcContinuous (p : Params) (a cb : Int) : Int :=
  if a ≤ gbp p.hicbcThreshold then 0
  else
    let num := min (a - gbp p.hicbcThreshold) (100 * gbp p.hicbcStep)
    (2 * cb * num + 100 * gbp p.hicbcStep) / (2 * 100 * gbp p.hicbcStep)

-- 2025-26: two children, 365/7 weeks of £43.30 = £2,257.79 (the statute's 52 Mondays: £2,251.60)
#guard childBenefitOecd p2025 [6, 11] = 225779 ∧ childBenefit p2025 [6, 11] = 225160
#guard hicbcContinuous p2025 (gbp 70000) 225779 = 112890 ∧ hicbcContinuous p2025 (gbp 90000) 225779 = 225779
#guard hicbcContinuous p2025 (gbp 60000) 225779 = 0

/-- s. 45 / 46: the married couple's allowance reduction (ticks) for a claimant with adjusted net income `a`
(pence): 10 % of £11,270 "reduced by half the excess" over £37,700, not below the minimum amount £4,360. -/
def mcaReduction (p : Params) (a : Int) : Int :=
  -- the amount in half-pence, then 10 % in ticks (pence × basis points): half-pence × rate / 2
  let amountHalfPence := max (2 * gbp p.mcaMinimum) (2 * gbp p.mcaAmount - pos (a - gbp p.mcaIncomeLimit))
  amountHalfPence * p.mcaRate / 2

/-- Born before 6 April 1935: aged 90 or more on 6 April 2025. -/
def bornBefore1935 (x : Person) : Bool := decide (x.age ≥ 90)

structure Option2 where
  name : String
  e1 : Elections
  e2 : Elections
  deriving Repr

/-- s. 39: the excess of a blind person's allowance over the remaining relievable income (net income less the
personal allowance), in whole pounds (rounded down). -/
def bpaExcess (p : Params) (x : Person) (r : PersonResult) : Int :=
  if x.blind then pos (p.blindAllowance - pos ((r.netIncome - gbp r.pa) / 100)) else 0

structure HouseholdResult where
  persons : List Person
  results : List PersonResult
  election : String
  childBenefit : Int
  hicbc : Int
  /-- Index of the adult liable to the child benefit charge, if any. -/
  hicbcPayer : Option Nat
  incomeTax : Int
  cgt : Int
  employeeSocial : Int
  benefits : Int
  unsupported : List String
  deriving Repr

def coupleTotal (rs : List PersonResult) : Int := (rs.map fun r => r.liability + r.cgt).foldl (· + ·) 0

def calcWith (p : Params) (rd : Reading) (xs : List Person) (es : List Elections) : List PersonResult :=
  (xs.zip es).map fun (x, e) => personCalc p rd x e

/-- The couple's elections and the results under them. -/
def chooseElections (p : Params) (rd : Reading) (h : Household) (xs : List Person) :
    String × List PersonResult :=
  match xs with
  | [x1, x2] =>
    if !h.married then ("none", calcWith p rd xs [{}, {}]) else
    let base := calcWith p rd xs [{}, {}]
    let (b1, b2) := match base with
      | [r1, r2] => (bpaExcess p x1 r1, bpaExcess p x2 r2)
      | _ => (0, 0)
    let e0 : Elections × Elections := ({ bpaReceived := b2 }, { bpaReceived := b1 })
    let noneRs := calcWith p rd xs [e0.1, e0.2]
    -- marriage allowance: valid only if the relinquishing spouse would pay no more than basic-rate tax with the
    -- reduced allowance (s. 55C(1)(c), (ca)) and the gaining spouse pays no more than basic-rate tax (s. 55B(2)(b),
    -- (ba)); otherwise there is no reduction and the allowance is not reduced.
    let ma (giverFirst : Bool) : Option (List PersonResult) :=
      if rd.peMaUnused then
        -- PolicyEngine: the partner's unused allowance, capped at 10 %, rounded up to £10; no reduction for the giver
        match noneRs with
        | [r1, r2] =>
          let g := if giverFirst then r1 else r2
          let unused := pos (g.pa - pos (g.netIncome / 100))
          let amt := 10 * ceilDiv (min unused (p.personalAllowance * p.maTransferRate / 10000)) 10
          if amt ≤ 0 then none else
          let es := if giverFirst then [e0.1, { e0.2 with maReceive := true, maAmount := some amt }]
                    else [{ e0.1 with maReceive := true, maAmount := some amt }, e0.2]
          let rs := calcWith p rd xs es
          match rs with
          | [q1, q2] => if (if giverFirst then q2 else q1).maReduction > 0 then some rs else none
          | _ => none
        | _ => none
      else
      let es := if giverFirst then [{ e0.1 with maGive := true }, { e0.2 with maReceive := true }]
                else [{ e0.1 with maReceive := true }, { e0.2 with maGive := true }]
      let rs := calcWith p rd xs es
      match rs with
      | [r1, r2] =>
        let (g, rcv) := if giverFirst then (r1, r2) else (r2, r1)
        if g.maRates && rcv.maRates && decide (rcv.maReduction > 0) then some rs else none
      | _ => none
    let mca : Option (List PersonResult) :=
      if rd.peNoMca || !(bornBefore1935 x1 || bornBefore1935 x2) then none else
      match noneRs with
      | [r1, r2] =>
        let firstClaims := decide (r1.netIncome ≥ r2.netIncome)
        let red := mcaReduction p (if firstClaims then r1.ani else r2.ani)
        let es1 := if firstClaims then [{ e0.1 with mcaReduction := red }, e0.2] else [e0.1, { e0.2 with mcaReduction := red }]
        let rs1 := calcWith p rd xs es1
        match rs1 with
        | [q1, q2] =>
          let used := if firstClaims then q1.mcaUsed else q2.mcaUsed
          let rest := red - used
          let es2 := if firstClaims then [{ e0.1 with mcaReduction := red }, { e0.2 with mcaReduction := rest }]
                     else [{ e0.1 with mcaReduction := rest }, { e0.2 with mcaReduction := red }]
          some (calcWith p rd xs es2)
        | _ => none
      | _ => none
    let opts : List (String × Option (List PersonResult)) :=
      [("marriage allowance 1→2", ma true), ("marriage allowance 2→1", ma false), ("married couple's allowance", mca)]
    opts.foldl (fun (best : String × List PersonResult) (o : String × Option (List PersonResult)) =>
      match o.2 with
      | some rs => if coupleTotal rs < coupleTotal best.2 then (o.1, rs) else best
      | none => best) ("none", noneRs)
  | _ => ("none", calcWith p rd xs (xs.map fun _ => {}))

def sumBy (rs : List PersonResult) (f : PersonResult → Int) : Int := (rs.map f).foldl (· + ·) 0

/-- The household's figures under the contract. -/
def householdCalc (p : Params) (rd : Reading) (h : Household) : HouseholdResult :=
  let xs := persons h
  let (election, rs) := chooseElections p rd h xs
  let cb := if rd.oecdCbAnnual then childBenefitOecd p h.children else childBenefit p h.children
  let hicbcF : Int → Int → Int := if rd.oecdHicbcContinuous then hicbcContinuous p else hicbc p
  -- s. 681B: the partner with the higher adjusted net income (the claimant if equal)
  let payer : Option Nat :=
    match rs with
    | [r] => if r.ani > gbp p.hicbcThreshold && cb > 0 then some 0 else none
    | [r1, r2] =>
      let i := if r2.ani > r1.ani then 1 else 0
      let a := if i = 1 then r2.ani else r1.ani
      if a > gbp p.hicbcThreshold && cb > 0 then some i else none
    | _ => none
  let charge : Int :=
    match payer, rs with
    | some 0, r :: _ => hicbcF r.ani cb
    | some 1, [_, r] => hicbcF r.ani cb
    | _, _ => 0
  let liab := sumBy rs fun r => ticksToPence r.liability
  let ras := sumBy rs fun r => ticksToPence r.rasRelief
  let unsupported : List String :=
    (if h.adults.length = 0 || h.adults.length > 2 then ["households of other than one or two adults"] else [])
    ++ (if h.year < 2022 || h.year > 2025 then [s!"tax year {h.year} not modelled; computed with the {p.taxYear} rules"] else [])
    ++ (if h.year ≠ 2025 && h.scottish then ["Scottish rates are modelled for 2025-26 only; rest-of-UK rates used"] else [])
    ++ (if h.year = 2024 && h.capitalGains > 0 then ["CGT 2024-25: rates changed on 30 October 2024 (10/20 % to 18/24 %); the earlier rates are used"] else [])
    ++ (if h.adults.any (fun a => decide (a.age ≥ 66)) then
          ["winter fuel payment and its charge (Finance Act 2026 Sch. 10) not modelled"] else [])
    ++ (if h.capitalGains < 0 then ["capital losses (carried forward) not modelled"] else [])
    ++ (if xs.any (fun x => decide (x.rasGross > 60000)) then ["pension annual allowance charge not modelled"] else [])
  { persons := xs, results := rs, election, childBenefit := cb, hicbc := charge, hicbcPayer := payer,
    incomeTax := liab - ras,
    cgt := sumBy rs fun r => ticksToPence r.cgt,
    employeeSocial := sumBy rs fun r => ticksToPence (r.class1 + r.class4),
    benefits := cb - charge,
    unsupported }

end UkTax
