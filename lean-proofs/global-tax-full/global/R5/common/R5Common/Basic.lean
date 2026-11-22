import TaxKernel.Global

/-!
# R5 common parts (MENA + Western Asia): helpers shared by the R5 country models

* `inclusiveAdValorem`: an ad valorem excise levied on the price **before** the excise and the VAT, read from a
  consumer amount that includes both (GCC excise laws: the tax on the retail selling price net of the tax itself and of
  VAT; the same arithmetic serves any "tax on the price excluding tax" read from a tax-inclusive spend):
      excise = amount × r / ((1 + r) (1 + v)).
* `perLitre` / `perStick`: specific duties per litre or per stick as `ExciseRate`s (kernel `ExciseRate`, quantity in
  thousandths of the canonical unit).
* `exciseCharge`: one excise charge from a computed duty (consumer-borne, OECD 5121).
* `zakatOnBase`: zakat at 2.5 % (or the statute's rate) of a base, as a charge under the heading the statute books it
  (DESIGN §1: zakat where levied as a tax is booked by its base).
-/

namespace R5Common
open TaxKernel TaxKernel.Global

/-- Excise at `rBp` on the price before excise and VAT, inside a consumer amount that includes excise and VAT at `vBp`. -/
def inclusiveAdValorem (rBp vBp amount : Int) : Int :=
  divR .down (pos amount * rBp * BP) ((BP + rBp) * (BP + vBp))

-- 100 % excise, 5 % VAT: a 210 pack holds 100 of excise (price 100, excise 100, VAT 10)
#guard inclusiveAdValorem 10000 500 210 == 100
#guard inclusiveAdValorem 5000 1500 1725 == 500

theorem inclusiveAdValorem_nonneg (r v a : Int) (hr : 0 ≤ r) (hv : 0 ≤ v) : 0 ≤ inclusiveAdValorem r v a := by
  unfold inclusiveAdValorem
  simp only [divR, BP]
  have h1 := Int.mul_nonneg (Int.mul_nonneg (pos_nonneg a) hr) (show (0:Int) ≤ 10000 by omega)
  exact Int.ediv_nonneg h1 (Int.mul_nonneg (by omega) (by omega))

/-- A specific duty of `num/den` money per litre (or per stick, per kWh: the good's canonical unit). -/
def perUnit (good : Good) (name : String) (num den : Int) (statute : String) : ExciseRate :=
  { good, name, perUnitNum := num, perUnitDen := den, statute }

/-- One consumer-borne excise charge (OECD 5121) with a duty computed by the country module. -/
def exciseCharge (name : String) (s : Spend) (duty : Int) (statute : String) : Charge :=
  charge .excise name s.quantity id (fun _ => duty) (event := s.good.name) (bearer := .consumer) (statute := statute)

/-- Zakat at `rateBp` on a base (booked under `oecd`). -/
def zakatOnBase (oecd : Oecd) (name : String) (base rateBp : Int) (statute : String) (event : String := "year") : Charge :=
  charge oecd name base pos (fun b => divR .down (rateBp * b) BP) (event := event) (statute := statute)

#guard (zakatOnBase .cit "zakat" 1000000 250 "x").due == 25000

/-- A corporate family (OECD 1200): the CIT of the regime chosen for the company, then statutory withholding on its
payments abroad (kernel `Wht.charges`: booked 1200 for a corporate recipient, 1100 for an individual, borne by the
recipient), then any country extras. Households get no charge. -/
def corpFamily (name : String) (regime : Company → CorpRegime) (statute : Company → String) (wht : Wht)
    (extra : CanonGlobal → List Charge := fun _ => []) : Family :=
  { name, covers := [.cit, .incomeOther],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [(regime g.company).citCharge g.company (statute g.company)] ++ wht.charges g.company ++ extra g }

/-- The company inputs a CIT module did not read the statute for (listed, never silently ignored). -/
def corpInputsUnread (g : CanonGlobal) (losses debt interest participation : Bool) : List String :=
  if g.entity != .company then [] else
  (if losses && g.company.lossesForward ≠ 0 then ["losses brought forward: carry-forward rule not read; not offset"] else [])
  ++ (if debt && (g.company.debt ≠ 0 || g.company.interestExpense ≠ 0) then ["interest limitation / thin capitalisation not read; interest taken as deductible"] else [])
  ++ (if participation && g.company.dividendsReceived ≠ 0 then ["dividends received: participation exemption not read; taxed in profit as given"] else [])

/-- Detail capital income of a household routed through the 1.x PIT model (DESIGN §6: never re-implement the PIT):
the year's net gain on disposals goes to `capitalGains`, extra interest, dividends and rents to their 1.x fields, and
the charge is the 1.x income tax with them less without them (`stackedTax`). -/
def routedAdd (g : CanonGlobal) : HouseholdAdd :=
  let inc (k : IncomeKind) : Int := isum ((g.incomes.filter (·.kind == k)).map (·.amount))
  { capitalGains := pos (isum (g.disposals.map (·.gain))), interest := inc .interest, dividends := inc .dividend,
    rentalIncome := inc .rent }

def stackedCapital (pit : List String → Canon → Int) (name statute : String) : Family :=
  { name, covers := [],
    run := fun args g _ =>
      if g.entity == .company then [] else
      let a := routedAdd g
      if a.capitalGains = 0 ∧ a.interest = 0 ∧ a.dividends = 0 ∧ a.rentalIncome = 0 then [] else
      [charge .pit name (a.capitalGains + a.interest + a.dividends + a.rentalIncome) id
        (fun _ => stackedTax (pit args) g.household a) (event := "capital income (routed)") (statute := statute)] }

/-- An employer contribution of `rateBp` on each adult's wages up to `cap` (−1: none), OECD 2200, borne by the employer. -/
def employerOn (name statute : String) (rateBp cap : Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
    charge .sscEmployer name a.wages (fun w => if cap < 0 then pos w else min (pos w) cap) (fun b => divR .down (rateBp * b) BP)
      (event := s!"adult {i + 1}") (level := .social) (bearer := .employer) (statute := statute)

end R5Common
