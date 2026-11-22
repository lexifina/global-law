import TaxCode.Individual.Form1040
import TaxCode.Individual.PriorYears
import Compare.Canon

/-!
# United States, tax year 2025: the canonical household on the existing Form 1040 model

The income tax is `TaxCode.Individual.form1040`, the model in `wt/publish/lean-proofs/TaxCode/Individual` (copied
here unchanged; hashes in `refs/us_sources.sha256`): regular tax, AMT, credits, self-employment tax, the additional
Medicare tax (§§3101(b)(2), 1401(b)(2)) and the net investment income tax (§1411), as amended by Pub. L. 119-21.

This file adds only what the model's output leaves out:
* the employee's share of FICA on wages (§3101(a), (b)(1)), which the model computes only inside the additional child
  tax credit (`ficaEmployee`) and does not report;
* rents in the §1411 base (§1411(c)(1)(A)(i)), which the model's `Household` has no field for.

How the household is put on returns (the comparison's choices for the US):
* married: one joint return (§6013); one adult: head of household with a child (§2(b)), single otherwise;
* two unmarried adults: two returns, the children with the first adult (head of household), the second single;
  household investment and rental income, gifts and pension contributions split equally (first return gets the odd
  dollar);
* dividends are qualified dividends and gains are long-term (the contract: "long-held listed shares");
* rents are net rental income (Schedule E) carried in `otherIncome`; gifts are cash gifts to public charities
  (itemized, §170); pension contributions are traditional IRA contributions (§219) by people who are not active
  participants; pensions are fully taxable private pensions (no Social Security benefits).
-/

namespace Compare.Us
open TaxCode.Individual Lean

/-- Social Security Act §230 contribution and benefit base for 2025: $176,100 (SSA, "Cost-of-Living Increase and
Other Determinations for 2025", 89 FR 85276, 25 October 2024: "The OASDI contribution and benefit base is $176,100").
§3121(a)(1): remuneration above it paid by one employer in a year is not "wages" for §3101(a). -/
def wageBase : Int := 176100

/-- **IRC §3101(a).** "a tax equal to 6.2 percent of the wages (as defined in section 3121(a)) received by the
individual". One employer per person; exact, rounded to the nearest dollar. -/
def oasdi (w : Int) : Int := roundDollar (62 * max 0 (min w wageBase)) 1000

/-- **IRC §3101(b)(1).** "1.45 percent of the wages ... received by the individual" (the 0.9% of §3101(b)(2) above
$200,000 is the additional Medicare tax, which the model computes on Form 8959 and the contract lists as a surtax). -/
def hospital (w : Int) : Int := roundDollar (145 * max 0 w) 10000

/-- Employee FICA of one person. -/
def fica (w : Int) : Int := oasdi w + hospital w

/-- **IRC §1411(a)(1), (c)(1)(A)(i).** 3.8% of the lesser of net investment income ("gross income from interest,
dividends, annuities, royalties, and rents", and net gain) and modified AGI over the threshold. The model's
`A.netInvestmentIncome` has no rents; this adds the rents the adapter carries in `otherIncome`. Same rounding as
`A.niit`. -/
def niitWithRents (h : Household) (agi rents : Int) : Int :=
  roundDollar (38 * min (A.netInvestmentIncome h + max 0 rents) (max 0 (agi - A.niitThreshold h.filing))) 1000

/-- One return built from the canonical household. -/
structure Ret where
  h : Household
  rents : Int
  people : List Adult

def mkHousehold (filing : Filing) (people : List Adult) (kids : List Child)
    (interest dividends gains rents gifts pc : Int) : Household :=
  let head := people.headD {}
  let spouse := people.tail.head?
  { filing := filing, head := { age := head.age }, spouse := spouse.map fun s => ({ age := s.age } : Person),
    dependents := kids.map fun k => ({ age := k.age } : Dependent),
    wages := people.foldl (fun a p => a + p.wages) 0,
    wagesSpouse := (match spouse with | some s => s.wages | none => 0),
    seIncome := people.foldl (fun a p => a + p.selfEmployment) 0,
    taxableInterest := interest, ordinaryDividends := dividends, qualifiedDividends := dividends,
    longTermGains := gains, pensions := people.foldl (fun a p => a + p.pension) 0,
    otherIncome := rents, charitableCash := gifts,
    iraContributions := pc, retirementContributions := pc }

def returns (c : Canon) : List Ret :=
  let fs (kids : List Child) : Filing := if kids.isEmpty then .single else .hoh
  match c.adults with
  | [a] => [{ h := mkHousehold (fs c.children) [a] c.children c.interest c.dividends c.capitalGains c.rentalIncome
                c.charitable c.pensionContributions, rents := c.rentalIncome, people := [a] }]
  | [a, b] =>
    if c.married then
      [{ h := mkHousehold .mfj [a, b] c.children c.interest c.dividends c.capitalGains c.rentalIncome c.charitable
          c.pensionContributions, rents := c.rentalIncome, people := [a, b] }]
    else
      [{ h := mkHousehold (fs c.children) [a] c.children (half1 c.interest) (half1 c.dividends)
          (half1 c.capitalGains) (half1 c.rentalIncome) (half1 c.charitable) (half1 c.pensionContributions),
         rents := half1 c.rentalIncome, people := [a] },
       { h := mkHousehold .single [b] [] (half2 c.interest) (half2 c.dividends) (half2 c.capitalGains)
          (half2 c.rentalIncome) (half2 c.charitable) (half2 c.pensionContributions),
         rents := half2 c.rentalIncome, people := [b] }]
  | _ => []

def filingName : Filing → String
  | .single => "single" | .mfj => "mfj" | .mfs => "mfs" | .hoh => "hoh" | .qss => "qss"

structure Res where
  incomeTax : Int := 0
  niit : Int := 0
  addl : Int := 0
  fica : Int := 0
  se : Int := 0
  agi : Int := 0
  ti : Int := 0
  regular : Int := 0
  amt : Int := 0
  nonref : Int := 0
  refundable : Int := 0
  ctc : Int := 0
  actc : Int := 0
  odc : Int := 0
  eitc : Int := 0
  std : Int := 0
  itemized : Int := 0
  deduction : Int := 0
  filings : List String := []

def Res.add (r : Res) (x : Ret) : Res :=
  let l := form1040 x.h
  let niit := niitWithRents x.h l.agi x.rents
  { incomeTax := r.incomeTax + (l.incomeTaxAfterCredits - l.refundableCredits), niit := r.niit + niit,
    addl := r.addl + l.additionalMedicare,
    fica := r.fica + x.people.foldl (fun a p => a + Compare.Us.fica p.wages) 0,
    se := r.se + l.seTax, agi := r.agi + l.agi, ti := r.ti + l.taxableIncome, regular := r.regular + l.regularTax,
    amt := r.amt + l.amt, nonref := r.nonref + l.nonrefundableCredits,
    refundable := r.refundable + l.refundableCredits,
    ctc := r.ctc + l.ctc, actc := r.actc + l.actc, odc := r.odc + l.odc, eitc := r.eitc + l.eitc,
    std := r.std + l.standardDeduction, itemized := r.itemized + l.itemized, deduction := r.deduction + l.deduction,
    filings := r.filings ++ [filingName x.h.filing] }

/-- Employee FICA of one person with another year's contribution and benefit base (`Prior.YP.wageBase`). -/
def ficaY (wb w : Int) : Int := roundDollar (62 * max 0 (min w wb)) 1000 + hospital w

/-- One return for tax years 2022-2024 (`TaxCode.Individual.Prior`, wages-only returns). -/
def Res.addPrior (y : Prior.YP) (r : Res) (x : Ret) : Res :=
  let l := Prior.compute y x.h
  { r with
    incomeTax := r.incomeTax + l.incomeTax
    addl := r.addl + l.addl
    fica := r.fica + x.people.foldl (fun a p => a + ficaY y.wageBase p.wages) 0
    agi := r.agi + l.agi
    ti := r.ti + l.ti
    regular := r.regular + l.regular
    nonref := r.nonref + l.ctc
    refundable := r.refundable + l.actc + l.eic
    ctc := r.ctc + l.ctc
    actc := r.actc + l.actc
    eitc := r.eitc + l.eic
    std := r.std + l.std
    deduction := r.deduction + l.deduction
    niit := r.niit + l.niit
    se := r.se + l.se
    filings := r.filings ++ [filingName x.h.filing] }

/-- The tax year: 2022-2024 by `Prior` (round 3), 2025 (and any other year) by the 2025 Form 1040 model. -/
def compute (c : Canon) : Res :=
  match Prior.yearParams? c.year with
  | some y => (returns c).foldl (Res.addPrior y) {}
  | none => (returns c).foldl Res.add {}

/-- What the 2022-2024 path does not model (it computes wages only). -/
def priorUnsupported (c : Canon) : List String :=
  match Prior.yearParams? c.year with
  | none => []
  | some _ =>
    []  -- round 5: self-employment, QBI and the saver's credit are modelled for 2022-2024 too

def out (c : Canon) : Out :=
  let r := compute c
  let i (x : Int) : Json := Lean.toJson x
  let unsup : List String :=
    ["state and local income taxes (not modelled; the federal return only)"] ++ priorUnsupported c
      ++ (if c.adults.length = 2 && c.married && c.adults.all (fun p => p.selfEmployment ≠ 0) then
            ["self-employment tax per spouse (the model puts all self-employment income on the head)"] else [])
      ++ (if c.adults.any (fun p => p.pension ≠ 0) then
            ["Social Security benefits (pensions read as fully taxable private pensions)"] else [])
  { id := c.id, country := "US", currency := "USD", incomeTax := r.incomeTax,
    surtaxes := [("NIIT", r.niit), ("AdditionalMedicare", r.addl)], localIncomeTax := 0,
    employeeSocial := r.fica + r.se, benefits := 0,
    detail := [("taxYear", Lean.toJson (if (Prior.yearParams? c.year).isSome then c.year else 2025)),
      ("filing", Json.arr (r.filings.map Json.str).toArray), ("agi", i r.agi), ("taxableIncome", i r.ti),
      ("standardDeduction", i r.std), ("itemized", i r.itemized), ("deduction", i r.deduction),
      ("regularTax", i r.regular), ("amt", i r.amt), ("nonrefundableCredits", i r.nonref),
      ("refundableCredits", i r.refundable), ("ctc", i r.ctc), ("actc", i r.actc), ("odc", i r.odc),
      ("eitc", i r.eitc), ("ficaEmployee", i r.fica), ("seTax", i r.se)],
    unsupported := unsup }

/-! ## Checks -/

-- FICA at the OECD Taxing Wages 2025 average wage ($73,520): 7.65% = $5,624.28 (OECD EECSSC: 5,624).
#guard fica 73520 = 5624
-- At the wage base: 6.2% of $176,100 = $10,918.20; above it only the 1.45% grows.
#guard oasdi 176100 = 10918 && oasdi 300000 = 10918
-- The model's own `ficaEmployee` (rounded down, both spouses) agrees at this wage.
#guard ficaEmployee { filing := .single, head := { age := 40 }, wages := 73520 } = 5624

end Compare.Us
