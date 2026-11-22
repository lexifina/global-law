import TaxKernel.World2
import Lean.Data.Json

/-!
# TaxKernel.Global.Types (2.0.0, 2026-11-21): the canonical entity for every tax (`CanonGlobal`)

Kernel 2.0 widens the model from the personal income tax on a household to every tax a jurisdiction levies, in the
OECD Revenue Statistics classification (Interpretative Guide; codes 1100 … 6000). This file holds the inputs only:

* `Oecd`: the categories a charge is booked under (1100 individuals' income, 1200 corporate, 2100/2200/2300 social
  security by payer, 3000 payroll, 4100 … 4400 property, 5111 VAT, 5121 excises, 6000 other).
* `CanonGlobal`: one **entity** (a household or a company) with
  - `household : Canon`, the 1.x household **verbatim** (the existing 197 PIT models read only this);
  - `incomes`: income items in more detail than the legacy aggregates (kind, person, foreign source);
  - `assets`: holdings at the valuation date (market value, the statute's assessed value, debt, region);
  - `disposals`: sales of shares, property and other assets (proceeds, cost, holding period, main home, stake);
  - `transfers`: inheritances and gifts received (value, relationship to the deceased or donor, prior gifts);
  - `purchases`: acquisitions that attract transfer or stamp duty (price, assessed value, first or extra home);
  - `consumption`: a basket of spending, tax-inclusive, with physical quantities for per-unit excises;
  - `company`: the company side (turnover, profit, interest, losses, payroll, VAT supplies, payments abroad).

**Backward compatibility.** The legacy household is a field, not a projection: `CanonGlobal.ofCanon c` puts `c` there
unchanged and leaves every new list empty, and `(ofCanon c).household = c` holds by `rfl`. A 1.x input line read in
global mode is exactly `ofCanon` of its legacy parse (`parseGlobal`). The detail lists are **additional** events: an
amount already in `household.capitalGains` must not be repeated as a `disposal` (each country's routing says which
legacy field, if any, a detail item feeds; see `Master.route`).

Units as in 1.x: money `Int` whole units of the local currency; rates `Int` basis points; physical quantities in
**thousandths** of the canonical unit named on each `Good`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-- OECD Revenue Statistics headings a charge is booked under (Interpretative Guide). -/
inductive Oecd where
  /-- 1100 taxes on income, profits and capital gains of individuals -/
  | pit
  /-- 1200 … of corporations -/
  | cit
  /-- 1300 unallocable between 1100 and 1200 (e.g. a final withholding on payments to anyone) -/
  | incomeOther
  /-- 2100 social security, employees -/
  | sscEmployee
  /-- 2200 social security, employers -/
  | sscEmployer
  /-- 2300 social security, self-employed or non-employed -/
  | sscSelf
  /-- 3000 taxes on payroll and workforce -/
  | payroll
  /-- 4100 recurrent taxes on immovable property -/
  | propertyRecurrent
  /-- 4200 recurrent taxes on net wealth -/
  | wealth
  /-- 4300 estate, inheritance and gift taxes -/
  | estate
  /-- 4400 taxes on financial and capital transactions -/
  | transactions
  /-- 4500/4600 other non-recurrent and recurrent taxes on property -/
  | propertyOther
  /-- 5111 value added taxes -/
  | vat
  /-- 5112-5113 sales and other general taxes on goods and services -/
  | salesTax
  /-- 5121 excises -/
  | excise
  /-- 5122-5128 other taxes on specific goods and services (customs 5123, specific services 5126 …) -/
  | goodsOther
  /-- 5200 taxes on use of goods and on permission to use goods (motor vehicles …) -/
  | useOfGoods
  /-- 6000 other taxes -/
  | other
  deriving Repr, DecidableEq, Inhabited, BEq

namespace Oecd
def code : Oecd → String
  | pit => "1100" | cit => "1200" | incomeOther => "1300" | sscEmployee => "2100" | sscEmployer => "2200"
  | sscSelf => "2300" | payroll => "3000" | propertyRecurrent => "4100" | wealth => "4200" | estate => "4300"
  | transactions => "4400" | propertyOther => "4500" | vat => "5111" | salesTax => "5112" | excise => "5121"
  | goodsOther => "5120" | useOfGoods => "5200" | other => "6000"

def all : List Oecd :=
  [pit, cit, incomeOther, sscEmployee, sscEmployer, sscSelf, payroll, propertyRecurrent, wealth, estate, transactions,
   propertyOther, vat, salesTax, excise, goodsOther, useOfGoods, other]

def ofCode? (s : String) : Option Oecd := all.find? (·.code == s)

/-- The top-level family (1000 … 6000). -/
def family (k : Oecd) : String := (k.code.take 1).toString ++ "000"

theorem ofCode_code (k : Oecd) : ofCode? k.code = some k := by cases k <;> rfl
end Oecd

inductive IncomeKind where
  | wages | selfEmployment | pension | interest | dividend | rent | royalty | services | other
  deriving Repr, DecidableEq, Inhabited, BEq

def IncomeKind.ofString : String → IncomeKind
  | "wages" => .wages | "selfEmployment" => .selfEmployment | "pension" => .pension | "interest" => .interest
  | "dividend" => .dividend | "dividends" => .dividend | "rent" => .rent | "rentalIncome" => .rent
  | "royalty" => .royalty | "royalties" => .royalty | "services" => .services | _ => .other

def IncomeKind.name : IncomeKind → String
  | .wages => "wages" | .selfEmployment => "selfEmployment" | .pension => "pension" | .interest => "interest"
  | .dividend => "dividend" | .rent => "rent" | .royalty => "royalty" | .services => "services" | .other => "other"

/-- An income item beyond the legacy aggregates (a foreign dividend, a royalty, a second rent …). -/
structure Income where
  kind : IncomeKind
  amount : Int
  /-- 0 = first adult (or the company), 1 = second adult -/
  person : Nat := 0
  foreign : Bool := false
  /-- tax withheld at source (domestic withholding or foreign tax), for credits -/
  withheld : Int := 0
  deriving Repr, Inhabited

inductive AssetKind where
  | home | realEstate | land | listedShares | unlistedShares | bonds | deposits | business | pensionFund | vehicle
  | other
  deriving Repr, DecidableEq, Inhabited, BEq

def AssetKind.ofString : String → AssetKind
  | "home" => .home | "realEstate" => .realEstate | "land" => .land | "listedShares" => .listedShares
  | "unlistedShares" => .unlistedShares | "bonds" => .bonds | "deposits" => .deposits | "business" => .business
  | "pensionFund" => .pensionFund | "vehicle" => .vehicle | _ => .other

def AssetKind.isRealEstate : AssetKind → Bool
  | .home | .realEstate | .land => true
  | _ => false

def AssetKind.isShares : AssetKind → Bool
  | .listedShares | .unlistedShares => true
  | _ => false

/-- A holding at the valuation date (wealth, property and inheritance taxes). -/
structure Asset where
  kind : AssetKind
  /-- market value -/
  value : Int
  /-- the statute's own value (cadastral value, Einheitswert/Grundsteuerwert, avalúo fiscal, annual value); −1 = not given -/
  assessed : Int := -1
  /-- debt secured on it or attributable to it -/
  debt : Int := 0
  person : Nat := 0
  /-- municipality or region code, for local rates -/
  region : String := ""
  /-- annual rent or annual value where the statute taxes that (−1 = not given) -/
  annualValue : Int := -1
  deriving Repr, Inhabited

/-- The base a statute values an asset at: its own assessed value where given, else market value. -/
def Asset.statutoryValue (a : Asset) : Int := if a.assessed < 0 then a.value else a.assessed

/-- A sale of an asset (capital gains, securities and property transfer taxes on the seller). -/
structure Disposal where
  kind : AssetKind
  proceeds : Int
  /-- acquisition cost (historical, unindexed) -/
  cost : Int
  /-- incidental costs of acquisition and sale -/
  costs : Int := 0
  /-- holding period in months at the date of sale -/
  heldMonths : Nat := 0
  /-- year acquired (for indexation tables); 0 = unknown -/
  acquiredYear : Nat := 0
  person : Nat := 0
  mainHome : Bool := false
  /-- shareholding in the company sold, basis points (participation and "substantial holding" rules) -/
  stakeBp : Int := 0
  listed : Bool := false
  /-- statutory index factor for the cost over the holding period, bp (10000 = none; CL LIR art. 17 N° 8: IPC variation,
  IN cost inflation index, …), as published for the dates of acquisition and sale -/
  indexBp : Int := 10000
  deriving Repr, Inhabited

/-- Nominal gain (may be negative: a loss). -/
def Disposal.gain (d : Disposal) : Int := d.proceeds - d.cost - d.costs

inductive TransferKind where
  | inheritance | gift
  deriving Repr, DecidableEq, Inhabited, BEq

/-- Relationship of the recipient to the deceased or donor (inheritance and gift tax classes). -/
inductive Relation where
  | spouse | child | grandchild | parent | sibling | nieceNephew | otherRelative | unrelated | charity
  deriving Repr, DecidableEq, Inhabited, BEq

def Relation.ofString : String → Relation
  | "spouse" => .spouse | "child" => .child | "grandchild" => .grandchild | "parent" => .parent
  | "sibling" => .sibling | "nieceNephew" => .nieceNephew | "otherRelative" => .otherRelative
  | "charity" => .charity | _ => .unrelated

/-- An inheritance or gift **received** by the entity (recipient-based taxes), or the estate it describes
(estate-based taxes read the same records from the deceased's side). -/
structure Transfer where
  kind : TransferKind
  /-- market value of what passes -/
  value : Int
  /-- statutory value where the statute values differently (−1 = not given) -/
  assessed : Int := -1
  relation : Relation
  /-- earlier gifts from the same donor: (value, years before this transfer) -/
  prior : List (Int × Nat) := []
  person : Nat := 0
  recipientAge : Nat := 40
  /-- part of `value` that is the family home, business property (reliefs) -/
  homeValue : Int := 0
  businessValue : Int := 0
  deriving Repr, Inhabited

def Transfer.statutoryValue (t : Transfer) : Int := if t.assessed < 0 then t.value else t.assessed

/-- An acquisition attracting a transfer or stamp duty (paid by the buyer unless the statute says otherwise). -/
structure Purchase where
  kind : AssetKind
  price : Int
  assessed : Int := -1
  firstHome : Bool := false
  /-- an additional dwelling (surcharges) -/
  additionalHome : Bool := false
  nonResident : Bool := false
  region : String := ""
  deriving Repr, Inhabited

/-- Consumption categories (COICOP-like) with the canonical unit of each per-unit excise. -/
inductive Good where
  | food | nonAlcoholic
  /-- litre of beverage (strength in `abvBp`) -/
  | beer | wine | spirits
  /-- cigarette (stick) -/
  | cigarettes | tobaccoOther
  | clothing | rent | water
  /-- kWh -/
  | electricity | gas
  /-- litre -/
  | petrol | diesel | heatingOil
  | medicines | health | transport | communication | recreation | books | newspapers | education | restaurants
  | hotels | financial | insurance | other
  deriving Repr, DecidableEq, Inhabited, BEq

def Good.all : List Good :=
  [.food, .nonAlcoholic, .beer, .wine, .spirits, .cigarettes, .tobaccoOther, .clothing, .rent, .water, .electricity,
   .gas, .petrol, .diesel, .heatingOil, .medicines, .health, .transport, .communication, .recreation, .books,
   .newspapers, .education, .restaurants, .hotels, .financial, .insurance, .other]

def Good.name : Good → String
  | .food => "food" | .nonAlcoholic => "nonAlcoholic" | .beer => "beer" | .wine => "wine" | .spirits => "spirits"
  | .cigarettes => "cigarettes" | .tobaccoOther => "tobaccoOther" | .clothing => "clothing" | .rent => "rent"
  | .water => "water" | .electricity => "electricity" | .gas => "gas" | .petrol => "petrol" | .diesel => "diesel"
  | .heatingOil => "heatingOil" | .medicines => "medicines" | .health => "health" | .transport => "transport"
  | .communication => "communication" | .recreation => "recreation" | .books => "books"
  | .newspapers => "newspapers" | .education => "education" | .restaurants => "restaurants" | .hotels => "hotels"
  | .financial => "financial" | .insurance => "insurance" | .other => "other"

def Good.ofString (s : String) : Good := (Good.all.find? (·.name == s)).getD .other

/-- One line of the consumption basket, or one sale. -/
structure Spend where
  good : Good
  /-- what the household pays, **tax-inclusive** (VAT and excises inside the price) -/
  amount : Int
  /-- physical quantity in thousandths of the good's canonical unit (litres, sticks, kWh) -/
  quantity : Int := 0
  /-- alcoholic strength, bp of volume (4.8 % vol = 480) -/
  abvBp : Int := 0
  deriving Repr, Inhabited

/-- A supply made or bought by a business, **net of VAT**. -/
structure Supply where
  good : Good
  net : Int
  exported : Bool := false
  deriving Repr, Inhabited

/-- A payment by the company to a non-resident (withholding at source). -/
structure Payment where
  kind : IncomeKind
  amount : Int
  /-- recipient is a company (else an individual) -/
  toCompany : Bool := true
  /-- recipient's stake in the payer, bp (parent-subsidiary rules) -/
  stakeBp : Int := 0
  deriving Repr, Inhabited

/-- The company side of an entity. Amounts for the tax year, local currency. -/
structure Company where
  turnover : Int := 0
  /-- profit before tax as per the accounts (interest expense, payroll already deducted) -/
  profit : Int := 0
  /-- non-deductible expenses added back -/
  addBacks : Int := 0
  /-- income exempt by statute (other than dividends below) -/
  exemptIncome : Int := 0
  /-- dividends received (included in `profit`) and the stake they come from -/
  dividendsReceived : Int := 0
  participationBp : Int := 0
  /-- net interest expense (deducted in `profit`) -/
  interestExpense : Int := 0
  /-- tax EBITDA for interest limitation; 0 = profit + interest expense -/
  ebitda : Int := 0
  debt : Int := 0
  equity : Int := 0
  lossesForward : Int := 0
  /-- balance-sheet total (minimum taxes on assets) -/
  assets : Int := 0
  employees : Nat := 0
  /-- gross wages paid (employer social security, payroll taxes) -/
  payroll : Int := 0
  sales : List Supply := []
  inputs : List Supply := []
  paymentsAbroad : List Payment := []
  dividendsPaid : Int := 0
  region : String := ""
  /-- trade/sector flags the statute keys regimes on (e.g. "smallBusinessElected", "listed") -/
  flags : List String := []
  deriving Repr, Inhabited

inductive EntityKind where
  | household | company
  deriving Repr, DecidableEq, Inhabited, BEq

/-- The canonical entity of kernel 2.0. -/
structure CanonGlobal where
  id : String
  year : Nat := 2025
  entity : EntityKind := .household
  /-- the 1.x household, verbatim (for a company: an empty household with the same id) -/
  household : Canon
  incomes : List Income := []
  assets : List Asset := []
  disposals : List Disposal := []
  transfers : List Transfer := []
  purchases : List Purchase := []
  consumption : List Spend := []
  company : Company := {}
  /-- the whole input line (extra fields: region, elections) -/
  raw : Json := Json.null
  deriving Inhabited

/-- A 1.x household as a global entity: the household verbatim, every new list empty. -/
def CanonGlobal.ofCanon (c : Canon) : CanonGlobal :=
  { id := c.id, year := c.year, household := c, raw := c.raw }

theorem CanonGlobal.ofCanon_household (c : Canon) : (CanonGlobal.ofCanon c).household = c := rfl

/-- True when the entity carries nothing beyond the 1.x household. -/
def CanonGlobal.isLegacy (g : CanonGlobal) : Bool :=
  g.entity == .household && g.incomes.isEmpty && g.assets.isEmpty && g.disposals.isEmpty && g.transfers.isEmpty
    && g.purchases.isEmpty && g.consumption.isEmpty && g.company.turnover == 0 && g.company.profit == 0
    && g.company.payroll == 0 && g.company.sales.isEmpty && g.company.inputs.isEmpty
    && g.company.paymentsAbroad.isEmpty

theorem CanonGlobal.ofCanon_isLegacy (c : Canon) : (CanonGlobal.ofCanon c).isLegacy = true := rfl

/-- An extra string field of the whole input line. -/
def CanonGlobal.str? (g : CanonGlobal) (k : String) : Option String :=
  match g.raw.getObjVal? k with
  | .ok (.str s) => some s
  | _ => none

/-! ## Reading the JSON line (`schema: "global/2.0"`) -/

def strField (j : Json) (k : String) (dflt : String := "") : String :=
  match j.getObjVal? k with
  | .ok (.str s) => s
  | _ => dflt

def strList (j : Json) (k : String) : List String :=
  (arrField j k).toList.filterMap fun x => match x with | .str s => some s | _ => none

def parseIncome (j : Json) : Income :=
  { kind := IncomeKind.ofString (strField j "kind"), amount := intField j "amount", person := natField j "person",
    foreign := boolField j "foreign", withheld := intField j "withheld" }

def parseAsset (j : Json) : Asset :=
  { kind := AssetKind.ofString (strField j "kind"), value := intField j "value", assessed := intField j "assessed" (-1),
    debt := intField j "debt", person := natField j "person", region := strField j "region",
    annualValue := intField j "annualValue" (-1) }

def parseDisposal (j : Json) : Disposal :=
  { kind := AssetKind.ofString (strField j "kind"), proceeds := intField j "proceeds", cost := intField j "cost",
    costs := intField j "costs", heldMonths := natField j "heldMonths", acquiredYear := natField j "acquiredYear",
    person := natField j "person", mainHome := boolField j "mainHome", stakeBp := intField j "stakeBp",
    listed := boolField j "listed", indexBp := intField j "indexBp" 10000 }

def parseTransfer (j : Json) : Transfer :=
  { kind := if strField j "kind" == "gift" then .gift else .inheritance, value := intField j "value",
    assessed := intField j "assessed" (-1), relation := Relation.ofString (strField j "relation"),
    prior := (arrField j "prior").toList.map fun p => (intField p "value", natField p "yearsBefore"),
    person := natField j "person", recipientAge := natField j "recipientAge" 40,
    homeValue := intField j "homeValue", businessValue := intField j "businessValue" }

def parsePurchase (j : Json) : Purchase :=
  { kind := AssetKind.ofString (strField j "kind"), price := intField j "price", assessed := intField j "assessed" (-1),
    firstHome := boolField j "firstHome", additionalHome := boolField j "additionalHome",
    nonResident := boolField j "nonResident", region := strField j "region" }

def parseSpend (j : Json) : Spend :=
  { good := Good.ofString (strField j "good"), amount := intField j "amount", quantity := intField j "quantity",
    abvBp := intField j "abvBp" }

def parseSupply (j : Json) : Supply :=
  { good := Good.ofString (strField j "good"), net := intField j "net", exported := boolField j "export" }

def parsePayment (j : Json) : Payment :=
  { kind := IncomeKind.ofString (strField j "kind"), amount := intField j "amount",
    toCompany := boolField j "toCompany" true, stakeBp := intField j "stakeBp" }

def parseCompany (j : Json) : Company :=
  { turnover := intField j "turnover", profit := intField j "profit", addBacks := intField j "addBacks",
    exemptIncome := intField j "exemptIncome", dividendsReceived := intField j "dividendsReceived",
    participationBp := intField j "participationBp", interestExpense := intField j "interestExpense",
    ebitda := intField j "ebitda", debt := intField j "debt", equity := intField j "equity",
    lossesForward := intField j "lossesForward", assets := intField j "assets", employees := natField j "employees",
    payroll := intField j "payroll", sales := (arrField j "sales").toList.map parseSupply,
    inputs := (arrField j "inputs").toList.map parseSupply,
    paymentsAbroad := (arrField j "paymentsAbroad").toList.map parsePayment,
    dividendsPaid := intField j "dividendsPaid", region := strField j "region", flags := strList j "flags" }

/-- Read one global line. A line without `"household"` is a 1.x household: the result is `ofCanon` of its parse. A
company line may omit `"household"`; it then gets an empty one-adult household with the same id. -/
def parseGlobal (j : Json) : Except String CanonGlobal := do
  let isCompany := strField j "entity" == "company"
  match j.getObjVal? "household" with
  | .ok h =>
    let h' := match h.getObjVal? "id", j.getObjVal? "id" with
      | .error _, .ok idv => h.setObjVal! "id" idv
      | _, _ => h
    let c ← parseCanon h'
    pure { id := c.id, year := natField j "year" c.year, entity := if isCompany then .company else .household,
           household := c, incomes := (arrField j "incomes").toList.map parseIncome,
           assets := (arrField j "assets").toList.map parseAsset,
           disposals := (arrField j "disposals").toList.map parseDisposal,
           transfers := (arrField j "transfers").toList.map parseTransfer,
           purchases := (arrField j "purchases").toList.map parsePurchase,
           consumption := (arrField j "consumption").toList.map parseSpend,
           company := match j.getObjVal? "company" with | .ok cj => parseCompany cj | _ => {},
           raw := j }
  | .error _ =>
    if isCompany then
      let id := match j.getObjVal? "id" with
        | .ok (.str s) => s | .ok (.num n) => toString (numToInt n) | _ => ""
      if id.isEmpty then throw "missing id"
      pure { id, year := natField j "year" 2025, entity := .company, household := { id, raw := Json.null },
             company := match j.getObjVal? "company" with | .ok cj => parseCompany cj | _ => {},
             disposals := (arrField j "disposals").toList.map parseDisposal,
             purchases := (arrField j "purchases").toList.map parsePurchase,
             assets := (arrField j "assets").toList.map parseAsset, raw := j }
    else
      let c ← parseCanon j
      pure (CanonGlobal.ofCanon c)

/-- A 1.x line read in global mode is exactly `ofCanon` of its 1.x parse. -/
theorem parseGlobal_legacy {e : String} (j : Json) (c : Canon) (hh : j.getObjVal? "household" = .error e)
    (hc : (strField j "entity" == "company") = false) (hp : parseCanon j = .ok c) :
    parseGlobal j = .ok (CanonGlobal.ofCanon c) := by
  simp [parseGlobal, hh, hc, hp, bind, Except.bind, pure, Except.pure]

end TaxKernel.Global
