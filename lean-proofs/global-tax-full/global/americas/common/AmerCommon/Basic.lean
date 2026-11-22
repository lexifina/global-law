import TaxKernel.Global

/-!
# AmerCommon: helpers shared by the Americas (R2) kernel-2.0 country models

Every helper builds charges only through the kernel constructor `charge` (so `Charge.WF` holds by `charge_wf`), and a
family built here sees the earlier charges like any other (`withFamily_charges`). Nothing here holds a statutory
number: each country module passes its own cited parameters.

* `vatFamily`: VAT/GST (5111) or a general sales tax (5112) on the household basket (tax-inclusive amounts, kernel
  `Vat.embedded`) and on a company's supplies (output − input with pro rata, kernel `Vat.net`).
* `ExLine` / `exciseFamily`: an excise per good with a specific duty (per canonical unit or per unit of pure alcohol)
  and/or an ad valorem duty **on the price before the excise and the VAT**, read from a consumer amount that includes
  both (the usual Latin American and Caribbean base: "precio de venta del fabricante / valor CIF", not the retail
  price): with VAT rate v inside the amount P, net price N = P / (1 + v); N = b + s + r·b, so b = (N − s)/(1 + r).
* `corpFamily`: CIT by `CorpRegime` + statutory withholding on payments abroad (`Wht`) + country extras.
* `employerFamily`: employer contributions (2200) on each adult's wages (a share of the annual wage may be outside
  the base: the 13th/14th-month rule) and on a company's payroll (per employee average when `employees > 0`).
* `payrollFamily`: payroll taxes (3000) on the same bases.
* `propertyFamily`, `transferFamily`, `estateFamily`: kernel `PropertyTax`, `TransferDuty`, `InheritanceTax`.
-/

namespace AmerCommon
open TaxKernel TaxKernel.Global

/-! ## 5111 / 5112 -/

def vatFamily (fname : String) (v : Vat) (statute : String) (oecd : Oecd := .vat) (level : Level := .central) :
    Family :=
  { name := fname, covers := [oecd],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else [{ v.basketCharge g.consumption statute with oecd, level }])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [{ v.businessCharge g.company statute with oecd, level }] else []) }

/-! ## 5121 -/

structure ExLine where
  good : Good
  name : String
  /-- specific duty `num/den` per canonical unit (litre, stick, kWh) or per litre of pure alcohol -/
  num : Int := 0
  den : Int := 1
  pure : Bool := false
  /-- ad valorem rate on the price before the excise and the VAT, bp -/
  advBp : Int := 0
  /-- VAT (or sales tax) rate inside the consumer amount, bp -/
  vatBp : Int := 0
  statute : String := ""
  deriving Repr, Inhabited

namespace ExLine
def units (e : ExLine) (s : Spend) : Int := if e.pure then divR .down (s.quantity * s.abvBp) BP else s.quantity
def specific (e : ExLine) (s : Spend) : Int := divR .down (e.units s * e.num) (e.den * 1000)
/-- price before excise and VAT -/
def netBase (e : ExLine) (s : Spend) : Int :=
  divR .down (pos (divR .down (pos s.amount * BP) (BP + e.vatBp) - e.specific s) * BP) (BP + e.advBp)
def adValorem (e : ExLine) (s : Spend) : Int := divR .down (e.advBp * e.netBase s) BP
def duty (e : ExLine) (s : Spend) : Int := e.specific s + e.adValorem s
end ExLine

def exciseCharges (xs : List ExLine) (sp : List Spend) : List Charge :=
  sp.filterMap fun s => (xs.find? (·.good == s.good)).map fun e =>
    charge .excise e.name s.amount id (fun _ => e.duty s) (event := s.good.name) (bearer := .consumer)
      (statute := e.statute)

def exciseFamily (fname : String) (xs : List ExLine) : Family :=
  { name := fname, covers := [.excise], run := fun _ g _ => exciseCharges xs g.consumption }

-- 100 % ad valorem on the price before excise, VAT 10 %: 220 paid = 100 price + 100 excise + 20 VAT
#guard ({ good := .spirits, name := "x", advBp := 10000, vatBp := 1000 } : ExLine).duty { good := .spirits, amount := 220 } == 100
-- specific 2 per litre on 10 litres, no ad valorem
#guard ({ good := .petrol, name := "x", num := 2 } : ExLine).duty { good := .petrol, amount := 500, quantity := 10000 } == 20

theorem ExLine.netBase_nonneg (e : ExLine) (s : Spend) (h : 0 ≤ e.advBp) : 0 ≤ e.netBase s := by
  unfold ExLine.netBase
  simp only [divR, BP]
  exact Int.ediv_nonneg (Int.mul_nonneg (pos_nonneg _) (by omega)) (by omega)

/-- The ad valorem part of an excise is never negative. -/
theorem ExLine.adValorem_nonneg (e : ExLine) (s : Spend) (h : 0 ≤ e.advBp) : 0 ≤ e.adValorem s := by
  have hb := ExLine.netBase_nonneg e s h
  unfold ExLine.adValorem
  simp only [divR, BP]
  exact Int.ediv_nonneg (Int.mul_nonneg h hb) (by omega)

/-! ## 1200 -/

def corpFamily (fname : String) (regime : Company → CorpRegime) (statute : Company → String) (wht : Wht)
    (extra : CanonGlobal → List Charge := fun _ => []) : Family :=
  { name := fname, covers := [.cit, .incomeOther],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [(regime g.company).citCharge g.company (statute g.company)] ++ wht.charges g.company ++ extra g }

def corpInputsUnread (g : CanonGlobal) (losses debt participation : Bool) : List String :=
  if g.entity != .company then [] else
  (if losses && g.company.lossesForward ≠ 0 then ["losses brought forward: carry-forward rule not modelled; not offset"] else [])
  ++ (if debt && (g.company.debt ≠ 0 || g.company.interestExpense ≠ 0) then ["interest limitation / thin capitalisation not modelled; interest taken as deductible"] else [])
  ++ (if participation && g.company.dividendsReceived ≠ 0 then ["dividends received: taxed in profit as given (exemption not modelled)"] else [])

/-! ## 2200 / 3000 -/

/-- Base of an employer charge on an annual wage: `inBp` of it (10000 = all; 12/13 of a wage that includes an
aguinaldo outside the base = 9231). -/
def baseShare (inBp w : Int) : Int := divR .down (pos w * inBp) BP

/-- Company payroll: per-employee average when the head count is given (ceilings are per employee). -/
def payrollAmount (f : Int → Int) (co : Company) : Int :=
  if co.employees = 0 then f co.payroll
  else f (co.payroll / (co.employees : Int)) * (co.employees : Int)

def employerFamily (fname : String) (cs : List Contribution) (statute : String) (inBp : Int := 10000)
    (oecd : Oecd := .sscEmployer) (level : Level := .social) : Family :=
  { name := fname, covers := [oecd],
    run := fun _ g _ =>
      if g.entity == .company then
        cs.map fun c => charge oecd c.name g.company.payroll id (fun _ => payrollAmount (fun w => c.amount (baseShare inBp w)) g.company)
          (event := "payroll") (level := level) (bearer := .entity) (statute := statute)
      else
        (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).flatMap fun (a, i) =>
          cs.map fun c => charge oecd c.name a.wages (baseShare inBp) (fun b => c.amount b)
            (event := s!"adult {i + 1}") (level := level) (bearer := .employer) (statute := statute) }

def payrollFamily (fname : String) (p : PayrollTax) (statute : String) (level : Level := .central)
    (onAdults : Bool := true) : Family :=
  { name := fname, covers := [.payroll],
    run := fun _ g _ =>
      if g.entity == .company then
        [charge .payroll p.name g.company.payroll id (fun b => p.amount b) (event := "payroll") (level := level)
          (statute := statute)]
      else if !onAdults then [] else
        (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
          charge .payroll p.name a.wages id (fun b => p.amount b) (event := s!"adult {i + 1}") (level := level)
            (bearer := .employer) (statute := statute) }

#guard baseShare 9231 1300 == 1200

/-! ## 4100 / 4400 / 4300 -/

def propertyFamily (fname : String) (p : PropertyTax) (statute : String) (level : Level := .local) : Family :=
  { name := fname, covers := [.propertyRecurrent], run := fun _ g _ => p.charges g.assets statute level }

def transferFamily (fname : String) (ds : List (TransferDuty × String × Level)) : Family :=
  { name := fname, covers := [.transactions],
    run := fun _ g _ => ds.flatMap fun (d, st, lv) => d.charges g.purchases st lv }

/-- A flat charge on the value of each disposal of a kind (securities transaction / stamp taxes on the seller). -/
def disposalCharges (oecd : Oecd) (name : String) (kinds : List AssetKind) (rateBp : Int) (statute : String)
    (g : CanonGlobal) : List Charge :=
  (g.disposals.zipIdx.filter fun (d, _) => kinds.contains d.kind).map fun (d, i) =>
    charge oecd name d.proceeds id (fun b => divR .down (rateBp * pos b) BP) (event := s!"disposal {i + 1}")
      (statute := statute)

def estateFamily (fname : String) (it : InheritanceTax) (statute : String) (level : Level := .central) : Family :=
  { name := fname, covers := [.estate],
    run := fun _ g _ => (it.charges g.transfers statute).map fun c => { c with level } }


/-! ## 1100: detail items routed into the 1.x household (stacking)

The 1.x contract's `capitalGains` is the gain on long-held listed shares, and `interest`, `dividends`, `rentalIncome`
are household totals. A global line's **additional** items of exactly those kinds are routed into the same fields and
taxed as the 1.x model taxes them: the charge is `stackedTax` (PIT with them − PIT without them). Everything else
(property, unlisted shares, short holdings, other income kinds) is listed as unsupported by the country module. -/

def isLongListed (d : Disposal) : Bool := d.kind == .listedShares && decide (d.heldMonths > 12)

def routedAdd (g : CanonGlobal) : HouseholdAdd :=
  { capitalGains := pos (isum ((g.disposals.filter isLongListed).map (·.gain))),
    interest := isum ((g.incomes.filter (·.kind == .interest)).map (·.amount)),
    dividends := isum ((g.incomes.filter (·.kind == .dividend)).map (·.amount)),
    rentalIncome := isum ((g.incomes.filter (·.kind == .rent)).map (·.amount)) }

def stackFamily (pitOf : List String → Canon → Int) (statute : String) : Family :=
  { name := "1100 capital income and gains stacked on the 1.x model", covers := [],
    run := fun args g _ =>
      if g.entity == .company then [] else
      let a := routedAdd g
      let tot := a.capitalGains + a.interest + a.dividends + a.rentalIncome
      if tot == 0 then [] else
      [charge .pit "Income tax on additional capital income and gains (1.x model, stacked)" tot id
        (fun _ => stackedTax (pitOf args) g.household a) (event := "capital income") (statute := statute)] }

def stackUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then [] else
  (if g.disposals.any fun d => !isLongListed d then
    ["disposals other than listed shares held over 12 months (real estate, unlisted shares, short holdings): gains rules not modelled"] else [])
  ++ (if g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent then
    ["additional income items other than interest, dividends and rent: not taxed by this family"] else [])
  ++ (if g.disposals.any isLongListed || g.incomes.any fun i => i.kind == .interest || i.kind == .dividend || i.kind == .rent then
    ["additional capital income is routed into the 1.x household totals and taxed as the 1.x model taxes them (its conventions: split between adults, long-held listed shares)"] else [])

#guard (routedAdd { id := "x", household := { id := "x" }, disposals := [{ kind := .listedShares, proceeds := 300, cost := 100, heldMonths := 30 }] }).capitalGains == 200

theorem stackFamily_legacy (p : List String → Canon → Int) (s : String) (args : List String) (c : Canon) (l : List Charge) :
    (stackFamily p s).run args (CanonGlobal.ofCanon c) l = [] := by
  simp [stackFamily, CanonGlobal.ofCanon, routedAdd, isum, pos]

/-! ## Absences -/

def absentAll (ks : List Oecd) (why : String) : List Absent := ks.map fun k => { oecd := k, why }

/-- What a family does not model, listed for an entity that holds it. -/
def when (b : Bool) (msg : String) : List String := if b then [msg] else []

end AmerCommon
