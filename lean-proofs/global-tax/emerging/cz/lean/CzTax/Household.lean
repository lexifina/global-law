import CzTax.Social

/-!
# The canonical household, Czech law

Czech income tax is individual (no joint filing). The household elements are: the sleva na manžela (§ 35bb), the
choice of which parent claims each child (§ 35c odst. 9: only one per child and month), and the přídavek na dítě,
which tests the whole family's income (ZSSP § 17).

Contract mapping (state the conventions):
* `selfEmployment` is the § 7 dílčí základ (receipts − actual expenses) unless the Czech field `czSelfReceipts` is
  given, in which case expenses are the § 7 odst. 7 percentage `czExpenseRate` (80/60/40/30, default 60).
* `interest`, `dividends`: 15 % withheld at source, final (§ 36 odst. 2, § 8 odst. 1); `capitalGains` on long-held
  listed shares: exempt (§ 4 odst. 1 písm. u)) up to the 40 M Kč cap (§ 4 odst. 3), applied per person to the gain
  as given (the statute caps proceeds; with cost unknown the model treats proceeds = gain, an upper bound on the taxed
  part). Investment income is split equally between married adults (contract convention).
* `rentalIncome`: § 9, 30 % flat expenses; split equally between married adults.
* `pension`: statutory pension, exempt up to 36 × minimum wage (§ 4 odst. 1 písm. g)).
* `charitable`, `pensionContributions` (retirement products, paid evenly by month), `czMortgageInterest`: § 15,
  claimed by adult `czDeductionsBy` (default the first adult).
* Children: claimed by adult 0 unless `czChildClaimants` lists the claimant per child (§ 35c odst. 9); the order of
  children (first, second, third…) is the household order of the input list.
* Regimes per adult (`czRegime`): "standard" (default), "pausal" (paušální daň, § 2a/§ 7a: only if eligible,
  otherwise standard with a note), "sro" (the business is a one-person s.r.o.: `selfEmployment` = the company's profit
  before the owner's pay; `czSroSalary` paid as wage; CIT 21 % and 15 % on the dividend; employer contributions and
  the owner's health insurance as a person without taxable income (ZPVZP § 3b) when no salary is paid).

Output: `incomeTax` = the persons' final PIT (bonus negative) + paušální daň + withheld tax + CIT (s.r.o.);
`employeeSocial` = employee and OSVČ contributions, plus for the s.r.o. regime the employer's contributions and the
owner's own health premium (so that net income stays gross − tax − contributions); `benefits` = přídavek na dítě.
-/

namespace CzTax

inductive Regime | standard | pausal | sro
  deriving Repr, DecidableEq, Inhabited

structure Adult where
  age : Int := 40
  wages : Int := 0
  selfEmployment : Int := 0
  pension : Int := 0
  selfReceipts : Int := 0      -- czSelfReceipts (0 = selfEmployment is the profit)
  expenseRate : Int := 60      -- czExpenseRate
  regime : Regime := .standard -- czRegime
  pausalBand : Nat := 0        -- czPausalBand (0 = lowest eligible)
  sroSalary : Int := 0         -- czSroSalary
  stateInsured : Option Bool := none -- czStateInsured (none = decide from the household)
  dppMonthly : Int := 0        -- czDppMonthly (a dohoda o provedení práce at another employer, every month)
  dppInReturn : Bool := false  -- czDppInReturn (§ 36 odst. 7: include the DPP income in the return)
  deriving Repr, Inhabited

structure Child where
  age : Int := 0
  deriving Repr, Inhabited

structure Household where
  id : String := ""
  year : Int := 2025
  adults : List Adult := []
  married : Bool := false
  children : List Child := []
  interest : Int := 0
  dividends : Int := 0
  capitalGains : Int := 0
  rentalIncome : Int := 0
  charitable : Int := 0
  pensionContributions : Int := 0
  mortgageInterest : Int := 0           -- czMortgageInterest
  deductionsBy : Nat := 0               -- czDeductionsBy
  childClaimants : List Nat := []       -- czChildClaimants (per child; default all adult 0)
  pridavekMonths : Int := 12            -- czPridavekMonths (months of 2025 under ZSSP §§ 17-18)
  shortGains : Int := 0                 -- czShortGains: § 10 gains on securities held ≤ 3 years (not exempt)
  coopPct : Int := 0                    -- czCoopPct: share (≤ 50 %) of adult 0's § 7 income given to the spouse (§ 13)
  /-- `cztax --oecd` (convention mode, never the default): the OECD's arithmetic (no monthly rounding, no base
  rounding), see `eeSocialOecd`, `eeHealthOecd` and `TaxIn.noRound`. -/
  oecd : Bool := false
  /-- `cztax --june30` (convention mode for the EUROMOD grids only; never the default). EUROMOD's policies are those
  of 30 June of the policy year: country report Y16_CR_CZ section 2.4 (Policy extensions: "Full Year Adjustment (FYA),
  allowing the user to choose between policies as of 30th June (extension off) or modelling annual policies (extension
  on) … The default for the baselines is off") and section 2.5 Table 2.5 (MLS amounts of 2022 effective from April and
  from July, "Change introduced in the model by using the FYA switch"); EUROMOD "Nowcasting prices" note (Feb 2025)
  sections 1.3–1.4. In 2022–2025 the only mid-year change of a parameter this model uses is the životní minimum of
  2022 (1 April and 1 July 2022, the přídavek na dítě test, ZSSP §§ 17–18); with the flag every month of 2022 uses the
  amounts in force on 30 June 2022 (the April amounts). Tax and contribution parameters have no mid-year change in
  2022–2025. -/
  june30 : Bool := false
  /-- `cztax --no-skolkovne` (convention mode for the EUROMOD grids only): switches off the `--oecd` assumption that
  the household pays kindergarten fees (§ 35bc). Country report Y16_CR_CZ section 2.7.6.1.1 (EUROMOD modelling): "Due to
  lack of data about the kindergarten costs, the corresponding tax credit is not simulated." -/
  noSkolkovne : Bool := false
  deriving Repr, Inhabited

/-- One adult's computed lines. -/
structure PersonOut where
  regime : Regime
  pausalBand : Nat
  seProfit : Int
  tax : TaxOut
  pit : Int             -- final PIT (or paušální daň)
  social : Int          -- employee + OSVČ social security
  health : Int          -- employee + OSVČ health
  sroCit : Int
  sroDividend : Int
  sroDivTax : Int
  sroEmployer : Int     -- employer social + health on the owner's salary
  sroOwnHealth : Int    -- ZPVZP § 3b premium of an owner with no salary
  netForBenefit : Int   -- ZSSP § 5 odst. 1 písm. a): income after expenses, contributions and tax
  workIncomeMonthly : Bool -- ZSSP § 18 odst. 2: work income in every month (zvýšená výměra)
  workWageMonthly : Int := 0   -- wages a month, for the month-by-month § 18 odst. 2 test (round 2)
  workOther : Bool := false
  deriving Repr

structure Result where
  persons : List PersonOut
  incomeTax : Int
  employeeSocial : Int
  benefits : Int
  withheld : Int
  pridavekEligible : Bool
  familyNetMonthly : Int
  zmFamily : Int
  notes : List String
  deriving Repr

def nth (l : List Int) (i : Nat) : Int := (l.drop i).headD 0

/-- Which adult claims child `k` (§ 35c odst. 9). -/
def claimant (h : Household) (k : Nat) : Nat :=
  match (h.childClaimants.drop k).head? with
  | some i => i
  | none => 0

/-- § 35c: the zvýhodnění claimed by adult `i`: each child counts by its order in the household. -/
def childCreditsFor (h : Household) (i : Nat) : Int :=
  ((List.range h.children.length).filter (fun k => claimant h k = i ∧ (h.children.getD k default).age < 26)).foldl
    (fun s k => s + childCredit k) 0

def hasChildUnder3 (h : Household) : Bool := h.children.any (fun c => c.age < 3)

/-- Share of household investment / rental income attributed to each adult (equal split when married). -/
def shareOf (h : Household) (x : Int) (i : Nat) : Int :=
  if h.married && h.adults.length = 2 then (if i = 0 then x / 2 else x - x / 2) else (if i = 0 then x else 0)

/-- § 7 dílčí základ and receipts of an adult. -/
def seLinesOwn (a : Adult) : Int × Int :=
  if a.selfReceipts > 0 then (a.selfReceipts - flatExpenses a.selfReceipts a.expenseRate, a.selfReceipts)
  else (a.selfEmployment, pos a.selfEmployment)

/-- § 13 odst. 3: a spolupracující manžel may receive at most 50 % of the income and expenses, and at most 540 000 Kč
of profit (45 000 Kč a month). The share actually given (profit, receipts). -/
def coopShare (h : Household) : Int × Int :=
  let a := h.adults.getD 0 default
  let (p, r) := seLinesOwn a
  if h.married && h.adults.length = 2 && h.coopPct > 0 && a.regime = .standard then
    let pct := min h.coopPct 50
    let sp := min (p * pct / 100) 540000
    let sr := if p > 0 then r * sp / p else r * pct / 100
    (sp, sr)
  else (0, 0)

/-- § 7 dílčí základ and receipts of adult `i` after the § 13 split. -/
def seLinesH (h : Household) (i : Nat) : Int × Int :=
  let a := h.adults.getD i default
  let (p, r) := seLinesOwn a
  let (sp, sr) := coopShare h
  if i = 0 then (p - sp, r - sr) else if i = 1 then (p + sp, r + sr) else (p, r)

def seLines (a : Adult) : Int × Int := seLinesOwn a

/-- ZDP § 35bb odst. 2 písm. b): the spouse's "vlastní příjem" (wages, self-employment profit, pension, own share of
investment income; benefits excluded under odst. 4). -/
def ownIncome (h : Household) (i : Nat) : Int :=
  let a := h.adults.getD i default
  pos a.wages + pos (seLinesH h i).1 + pos a.pension + pos a.sroSalary + 12 * pos a.dppMonthly
    + shareOf h (h.interest + h.dividends + h.rentalIncome + h.capitalGains) i

/-- Paušální režim eligibility (§ 2a odst. 1 písm. b)–c), § 7a odst. 1 písm. b)): no employment, receipts within a
band, other (capital, rent) income at most 50 000 Kč besides withheld income. -/
def pausalBand (h : Household) (i : Nat) (a : Adult) : Nat :=
  let receipts := (seLinesH h i).2
  let other := shareOf h h.rentalIncome i
  if a.wages > 0 || other > 50000 then 0
  else
    let b := if a.pausalBand = 0 then pausalBandFor receipts a.expenseRate else a.pausalBand
    if b ≥ 1 && b ≤ 3 && receipts ≤ pausalLimit b a.expenseRate then b else 0

/-- ZVZP § 7 odst. 1: the state pays the health premium for (among others) pensioners and a parent caring for a child
under 7. Default: an adult with a pension or aged 65+, and the lower earner of a household with a child under 7;
`czStateInsured` overrides. -/
def stateInsured (h : Household) (i : Nat) : Bool :=
  let a := h.adults.getD i default
  match a.stateInsured with
  | some b => b
  | none =>
    let o := h.adults.getD (if i = 0 then 1 else 0) default
    let ea := a.wages + pos a.selfEmployment + pos a.selfReceipts
    let eo := o.wages + pos o.selfEmployment + pos o.selfReceipts
    decide (a.pension > 0) || decide (a.age ≥ 65) ||
    (h.children.any (fun c => decide (c.age < 7)) &&
      (decide (h.adults.length = 1) || decide (ea < eo) || (decide (ea = eo) && decide (i = 1))))

def person (h : Household) (i : Nat) : PersonOut :=
  let a := h.adults.getD i default
  let spouse := if i = 0 then 1 else 0
  let p := yearP h.year
  -- § 35ba odst. 1 písm. b) (2022, 2023: no condition on the children) / § 35bb odst. 2 (2024, 2025: a child under 3)
  let spouseCredit := h.married && h.adults.length = 2 && (!p.spouseNeedsChildUnder3 || hasChildUnder3 h)
    && decide (ownIncome h spouse ≤ spouseIncomeLimit)
    && decide ((coopShare h).1 = 0)  -- § 13 odst. 4 písm. c)
  let (seP, seR) := seLinesH h i
  let band := if a.regime = .pausal then pausalBand h i a else 0
  -- s.r.o.: company profit P, salary S, employer contributions, CIT, dividend
  let isSro := a.regime = .sro
  let sroP := if isSro then pos a.selfEmployment else 0
  let sroS := if isSro then min (pos a.sroSalary) sroP else 0
  let sroER := if isSro then erSocial sroS + erHealth sroS else 0
  let sroCitV := if isSro then cit (pos (sroP - sroS - sroER)) else 0
  let sroDiv := if isSro then pos (sroP - sroS - sroER - sroCitV) else 0
  let sroDivTax := withheld sroDiv
  -- DPP (ZDP § 6 odst. 4 písm. a)): up to the participation limit no contributions and a final 15 % withholding,
  -- unless the poplatník includes it in the return (§ 36 odst. 7); above it, ordinary wages.
  let dppSmall := decide (a.dppMonthly > 0) && decide (a.dppMonthly < dppLimit)
  let dppYear := 12 * pos a.dppMonthly
  let dppFinal := if dppSmall && !a.dppInReturn then withheld dppYear else 0
  let dppTaxed := if dppSmall then (if a.dppInReturn then dppYear else 0) else dppYear
  let wagesAll := a.wages + sroS + dppTaxed
  let wagesContrib := a.wages + sroS + (if dppSmall then 0 else dppYear)
  let seProfit := if isSro then 0 else seP
  let seRec := if isSro then 0 else seR
  let pensionTaxable := pos (a.pension - p.pensionExempt)
  let gains := shareOf h h.capitalGains i
  let gainsTaxable := pos (gains - shareExemptCap)
  let rent := shareOf h h.rentalIncome i
  let rentBase := rent - rentExpenses rent
  let mine := h.deductionsBy = i
  let tin : TaxIn :=
    { wages := wagesAll, seProfit := seProfit, seReceipts := seRec, rentBase := rentBase,
      otherBase := pensionTaxable + gainsTaxable + shareOf h h.shortGains i,
      gifts := if mine then h.charitable else 0, mortgage := if mine then h.mortgageInterest else 0,
      retirement := if mine then h.pensionContributions else 0,
      spouseCredit := spouseCredit, childCredits := childCreditsFor h i, noRound := h.oecd,
      thr23 := p.threshold23, bonusIncomeMinY := p.bonusIncomeMin,
      -- § 35bc (2022, 2023): `--oecd` only: the OECD's households pay kindergarten fees of at least the minimum wage
      -- for a child aged 3 to 6 (the statute mode has no fee input and claims nothing)
      extraSleva := if h.oecd && p.skolkovne && !h.noSkolkovne then
        p.minWage * ((List.range h.children.length).filter (fun k => claimant h k = i ∧
          3 ≤ (h.children.getD k default).age ∧ (h.children.getD k default).age ≤ 6)).length else 0 }
  let t := computeTax tin
  let side := wagesAll > 0
  let insured := stateInsured h i
  let eeSoc := if h.oecd then eeSocialOecdAt p.eeSocialRate p.socialCeiling wagesContrib
    else eeSocialAt p.eeSocialRate p.socialCeiling wagesContrib
  let eeHea := if h.oecd then eeHealthOecdAt p.minWage (!insured) wagesContrib else eeHealthAt p.minWage (!insured) wagesContrib
  let eeBase := min (pos wagesContrib) p.socialCeiling
  let (pit, soc, hea) :=
    if band > 0 then
      (pausalYearTax band, 12 * bpCeil (pausalSocialBase band) seSocialRate,
        12 * bpCeil (pausalHealthYear band / 12) healthRate)
    else
      let seSoc := if seProfit ≠ 0 || seRec > 0 then seSocial seProfit side eeBase else 0
      let seHea := if seProfit ≠ 0 || seRec > 0 then seHealth seProfit side else 0
      (t.finalTax + dppFinal, eeSoc + seSoc, eeHea + seHea)
  -- ZPVZP § 3b: a person with no employment, no self-employment and not insured by the state pays 13,5 % of the
  -- minimum wage each month (osoba bez zdanitelných příjmů).
  let ownHealth := if wagesContrib ≤ 0 && seProfit = 0 && seRec = 0 && band = 0 && !insured && a.age ≥ 18
    then 12 * bpCeil p.minWage healthRate else 0
  -- ZSSP § 5 odst. 1 písm. a): income counted after expenses, contributions and the tax on it (capital income
  -- under ZDP § 8, e.g. dividends, is not in the list); a bonus is not income.
  let netB := pos wagesAll + (if dppTaxed = 0 then dppYear else 0) + pos seProfit + pos rentBase - soc - hea - pos pit
    - ownHealth
  let workMonthly := decide (wagesAll / 12 ≥ zmSingle) || seRec > 0 || band > 0 || a.pension > 0
  { regime := a.regime, pausalBand := band, seProfit := seProfit, tax := t, pit := pit, social := soc, health := hea,
    sroCit := sroCitV, sroDividend := sroDiv, sroDivTax := sroDivTax, sroEmployer := sroER,
    sroOwnHealth := ownHealth, netForBenefit := netB, workIncomeMonthly := workMonthly,
    workWageMonthly := wagesAll / 12, workOther := seRec > 0 || band > 0 || a.pension > 0 }

/-- ZSSP §§ 17–18 with the životní minimum of the family (NV 436/2022: the first adult, further adults, then the
children by age). Rozhodný příjem: the family's monthly net income (the yearly figure / 12; the statute uses the
previous calendar quarter, ZSSP § 6 písm. a)). -/
def zmFamily (h : Household) : Int :=
  let nA := h.adults.length
  (if nA ≥ 1 then zmFirst else 0) + (if nA ≥ 2 then zmAdult * (nA - 1) else 0)
    + (h.children.map (fun c => zmChild c.age)).foldl (· + ·) 0

/-- The family's životní minimum with one month's amounts (`zmP`, tests round 2). -/
def zmFamilyAt (h : Household) (z : ZmP) : Int :=
  let nA := h.adults.length
  (if nA ≥ 1 then z.first else 0) + (if nA ≥ 2 then z.adult * (nA - 1) else 0)
    + (h.children.map (fun c => z.child c.age)).foldl (· + ·) 0

def compute (h : Household) : Result :=
  let ps := (List.range h.adults.length).map (person h)
  let wht := withheld (h.interest + h.dividends)
  let pit := (ps.map (fun p => p.pit + p.sroCit + p.sroDivTax)).foldl (· + ·) 0
  let soc := (ps.map (fun p => p.social + p.health + p.sroEmployer + p.sroOwnHealth)).foldl (· + ·) 0
  let net := (ps.map (·.netForBenefit)).foldl (· + ·) 0
  let netM := net / 12
  let y := h.year
  let pY := yearP y
  let zm := zmFamilyAt h (zmP y 1)
  let kids := h.children.filter (fun c => c.age < 26)
  -- ZSSP §§ 17–18 month by month with that month's životní minimum (in 2022 it changed on 1 April and 1 July)
  let monthAmt (m : Nat) : Int :=
    let z := zmP y (if h.june30 then 6 else m)
    let ok := !kids.isEmpty && decide (netM * 100 ≤ zmFamilyAt h z * pridavekCoefPct)
    let raisedM := ps.any (fun q => decide (q.workWageMonthly ≥ z.single) || q.workOther)
    if ok then (kids.map (fun c => pY.pridavek raisedM c.age)).foldl (· + ·) 0 else 0
  let total12 := ((List.range 12).map (fun k => monthAmt (k + 1))).foldl (· + ·) 0
  let eligible := !kids.isEmpty && decide (netM * 100 ≤ zm * pridavekCoefPct)
  let raised := ps.any (·.workIncomeMonthly)
  let perMonth := (kids.map (fun c => if raised then pridavekRaised c.age else pridavekBasic c.age)).foldl (· + ·) 0
  let ben := if y = 2025 then (if eligible then perMonth * h.pridavekMonths else 0) else total12 * h.pridavekMonths / 12
  let notes :=
    (if h.adults.any (fun a => a.regime = .pausal) && ps.any (fun p => p.regime = .pausal && p.pausalBand = 0)
      then ["czRegime pausal requested but not eligible (§ 2a): taxed in the standard regime"] else [])
    ++ (if y ≠ 2025 then [s!"tax year {y}: ZDP, ZPSZ, ZSSP and the životní minimum of {y} (Params.yearP, zmP); OSVČ minimum bases, the paušální režim and the DPP limit are the 2025 values"] else [])
    ++ ["ZSSP 117/1995 přídavek na dítě applied for czPridavekMonths months (default 12, the OECD convention); from 2025-10-01 the zákon č. 152/2025 Sb. reform moved it toward the dávka státní sociální pomoci"]
  { persons := ps, incomeTax := pit + wht, employeeSocial := soc, benefits := ben, withheld := wht,
    pridavekEligible := eligible, familyNetMonthly := netM, zmFamily := zm, notes := notes }

end CzTax
