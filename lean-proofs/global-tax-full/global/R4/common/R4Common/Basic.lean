import TaxKernel.Global

/-!
# R4Common: shared parts for the Sub-Saharan Africa builders (kernel 2.0)

Every country of the region books its taxes through these builders, so the country files hold only the statute's
numbers (with their provisions) and the classes of goods its annexes give.

* `vatFamily`: VAT on the household basket (`Vat.basketCharge`) and on a company's supplies (`Vat.businessCharge`).
* `Exc` / `exciseFamily`: excise duties as the region's statutes write them. The francophone codes (CGI "droits
  d'accises", base: the ex-factory price or the customs value) and the Commonwealth excise acts (ad valorem on the
  "excisable value") levy the ad valorem part on the value **before** excise and VAT, not on the retail price the
  kernel's `ExciseRate.adValorem` reads. The household gives the tax-inclusive amount `p`; with VAT `v` charged on
  the excise-inclusive price and a specific part `s`: `p = (b + s + a·b)(1 + v)`, so
  `b = (p / (1 + v) − s) / (1 + a)` and the duty is `s + a·b` (`Exc.duty`). Margins between the producer and the
  household are not known: the base is the price net of VAT and excise (flagged in each country's summary).
* `MinTax` / `corpFamily`: CIT with the region's minimum taxes, which have a floor and often a cap (OHADA codes:
  "minimum forfaitaire" / "impôt minimum forfaitaire" as a share of turnover with a minimum and a maximum amount;
  the higher of the CIT and the minimum is due). The kernel's `CorpRegime.minimumTax` has no floor or cap, so the
  minimum is computed here and the CIT due is `max regular minimum` (`corp_ge_min`, `corp_ge_regular`).
* Withholding on payments abroad comes straight from the kernel's `Wht.charges`.
-/

namespace R4
open TaxKernel TaxKernel.Global

/-! ## 5111 VAT -/

/-- VAT on the basket (household) and on the company's supplies. -/
def vatFamily (v : Vat) (statute : String) : Family :=
  { name := s!"5111 {v.name}", covers := [.vat],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else [v.basketCharge g.consumption statute])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then [v.businessCharge g.company statute] else []) }

/-! ## 5121 excises -/

structure Exc where
  good : Good
  name : String
  /-- specific duty, `perUnitNum / perUnitDen` money units per canonical unit (litre, stick, kWh) -/
  perUnitNum : Int := 0
  perUnitDen : Int := 1
  /-- the specific duty is per litre of pure alcohol -/
  onPureAlcohol : Bool := false
  /-- ad valorem rate on the value before excise and VAT, bp -/
  advBp : Int := 0
  /-- VAT rate charged on the excise-inclusive price (stripped to find the base), bp -/
  vatBp : Int := 0
  /-- strength band the rate applies to: `minAbvBp < strength ≤ maxAbvBp` (bp of volume; default: any) -/
  minAbvBp : Int := -1
  maxAbvBp : Int := 100000
  /-- origin the rate applies to: `none` any; `some true` imported goods only; `some false` local production only.
  A good is imported when the input line lists it in `"importedGoods"` (default: local production). -/
  imported : Option Bool := none
  /-- minimum duty per canonical unit, `minNum / minDen` (0: none); the duty is the larger of the two -/
  minNum : Int := 0
  minDen : Int := 1
  statute : String := ""
  deriving Repr, Inhabited

namespace Exc
def originOk (e : Exc) (imp : Bool) : Bool := match e.imported with | none => true | some b => b == imp
def appliesTo (e : Exc) (s : Spend) (imp : Bool := false) : Bool :=
  e.good == s.good && decide (e.minAbvBp < s.abvBp) && decide (s.abvBp ≤ e.maxAbvBp) && e.originOk imp
def units (e : Exc) (s : Spend) : Int := if e.onPureAlcohol then divR .down (s.quantity * s.abvBp) BP else s.quantity
def specific (e : Exc) (s : Spend) : Int := divR .down (e.units s * e.perUnitNum) (e.perUnitDen * 1000)
/-- Price net of VAT. -/
def netOfVat (e : Exc) (s : Spend) : Int := divR .down (pos s.amount * BP) (BP + e.vatBp)
/-- Value before excise: the net-of-VAT price less the specific duty, divided by (1 + ad valorem rate). -/
def base (e : Exc) (s : Spend) : Int := divR .down (pos (e.netOfVat s - e.specific s) * BP) (BP + e.advBp)
def adValorem (e : Exc) (s : Spend) : Int := divR .down (e.advBp * e.base s) BP
def minimum (e : Exc) (s : Spend) : Int := divR .down (s.quantity * e.minNum) (e.minDen * 1000)
def duty (e : Exc) (s : Spend) : Int := max (e.specific s + e.adValorem s) (e.minimum s)
end Exc

theorem Exc.duty_ge_min (e : Exc) (s : Spend) : e.minimum s ≤ e.duty s := by unfold Exc.duty; omega

/-- Excise charges, one per (rate, basket line) pair that matches the good (`imported`: the goods the line says are
imported). -/
def exciseCharges (xs : List Exc) (basket : List Spend) (imported : List String := []) : List Charge :=
  basket.flatMap fun s => (xs.filter (·.appliesTo s (imported.contains s.good.name))).map fun e =>
    charge .excise e.name s.amount (fun _ => e.base s) (fun _ => e.duty s) (event := s.good.name) (bearer := .consumer)
      (statute := e.statute)

def exciseFamily (name : String) (xs : List Exc) : Family :=
  { name := s!"5121 {name}", covers := [.excise],
    run := fun _ g _ => exciseCharges xs g.consumption (strList g.raw "importedGoods") }

theorem Exc.adValorem_nonneg (e : Exc) (s : Spend) (h3 : 0 ≤ e.advBp) : 0 ≤ e.adValorem s := by
  unfold Exc.adValorem Exc.base
  have hb : 0 ≤ divR .down (pos (e.netOfVat s - e.specific s) * BP) (BP + e.advBp) := by
    simp only [divR, BP]; exact Int.ediv_nonneg (Int.mul_nonneg (pos_nonneg _) (by omega)) (by omega)
  generalize divR .down (pos (e.netOfVat s - e.specific s) * BP) (BP + e.advBp) = b at *
  simp only [divR, BP]; exact Int.ediv_nonneg (Int.mul_nonneg h3 hb) (by omega)

/-! ## 1200 corporate income tax with the region's minimum taxes -/

/-- A minimum tax: `fixed` + `bp` of turnover (or of assets), at least `floor`, at most `cap` (−1: no cap). -/
structure MinTax where
  bp : Int := 0
  onAssets : Bool := false
  fixed : Int := 0
  floor : Int := 0
  cap : Int := -1
  deriving Repr, Inhabited

def MinTax.amount (m : MinTax) (co : Company) : Int :=
  let x := max (m.fixed + divR .down (m.bp * pos (if m.onAssets then co.assets else co.turnover)) BP) m.floor
  if m.cap < 0 then x else min x m.cap

/-- Taxable profit rounded down to a multiple of `step` (OHADA codes: "toute fraction du bénéfice imposable inférieure
à mille francs est négligée"). -/
def taxableStep (r : CorpRegime) (step : Int) (co : Company) : Int :=
  if step ≤ 1 then r.taxableProfit co else (r.taxableProfit co / step) * step

/-- The regular tax on the (rounded) taxable profit, with the kernel's small-business schedule choice. -/
def regularStep (r : CorpRegime) (step : Int) (co : Company) : Int :=
  (if r.isSmall co then r.smallSched else r.sched).tax r.round (taxableStep r step co)

/-- CIT due: the higher of the regular tax (kernel `CorpRegime`: losses, interest rules, participation exemption,
small-business schedule) and the minimum tax. -/
def corpTax (r : CorpRegime) (m : MinTax) (co : Company) (step : Int := 1) : Int :=
  max (regularStep r step co) (m.amount co)

theorem corp_ge_min (r : CorpRegime) (m : MinTax) (co : Company) (step : Int) : m.amount co ≤ corpTax r m co step := by
  unfold corpTax; omega

theorem corp_ge_regular (r : CorpRegime) (m : MinTax) (co : Company) (step : Int) :
    regularStep r step co ≤ corpTax r m co step := by
  unfold corpTax; omega

theorem regularStep_one (r : CorpRegime) (co : Company) : regularStep r 1 co = r.regularTax co := by
  simp [regularStep, taxableStep, CorpRegime.regularTax]

theorem MinTax.amount_le_cap (m : MinTax) (co : Company) (h : 0 ≤ m.cap) : m.amount co ≤ m.cap := by
  unfold MinTax.amount; simp only; split <;> omega

/-- The CIT charge. -/
def citCharge (r : CorpRegime) (m : MinTax) (co : Company) (statute : String) (credit : Int := 0) (step : Int := 1) :
    Charge :=
  charge .cit r.name (r.beforeLosses co) (fun _ => taxableStep r step co) (fun _ => corpTax r m co step) credit
    (statute := statute)

/-- Corporate family: the CIT (with its minimum), the statutory withholding on payments abroad, and any extra
company charges the country writes (`extra`). -/
def corpFamily (name : String) (r : CorpRegime) (m : MinTax) (statute : String) (w : Wht)
    (extra : Company → List Charge := fun _ => []) (step : Int := 1) : Family :=
  { name := s!"1200 {name}", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [citCharge r m g.company statute (step := step)] ++ w.charges g.company ++ extra g.company }

/-! ## Checks of the parts -/

-- beer: 1 000 for 1 litre, VAT 18 %, ad valorem 50 %: net of VAT 847, base 564, duty 282
#guard (({ good := .beer, name := "x", advBp := 5000, vatBp := 1800 } : Exc).duty { good := .beer, amount := 1000, quantity := 1000 }) == 282
-- specific 100 per litre + 20 % ad valorem, VAT 16 %: net 862, base (862 − 100) / 1,2 = 635, duty 100 + 127
#guard (({ good := .petrol, name := "x", perUnitNum := 100, advBp := 2000, vatBp := 1600 } : Exc).duty { good := .petrol, amount := 1000, quantity := 1000 }) == 227
-- minimum tax 1 % of turnover, floor 500 000, cap 5 000 000
#guard (({ bp := 100, floor := 500000, cap := 5000000 } : MinTax).amount { turnover := 10000000 }) == 500000
#guard (({ bp := 100, floor := 500000, cap := 5000000 } : MinTax).amount { turnover := 100000000 }) == 1000000
#guard (({ bp := 100, floor := 500000, cap := 5000000 } : MinTax).amount { turnover := 1000000000 }) == 5000000

end R4
