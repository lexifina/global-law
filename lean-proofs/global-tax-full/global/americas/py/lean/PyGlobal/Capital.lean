import PyGlobal.Pit

/-!
# PY 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

## Pass 11 (2026-11-21): capital gains of individuals

Ley 6380/2019, IRP (`world/B12-latin-america/py/src/l6380page.txt`): **art. 60** 8 %, **art. 59.1** renta neta = the lesser of
30 % of the price and price less purchase price and selling costs, **art. 53** each category separately, **art. 56** exemptions
(num. 3 movables to G. 20.000.000 a year, num. 9-10 securities through the Bolsa). No main-home exemption.

**Pass 12:** the vendored 1.x model was refreshed after the PIT fix agent's MS-1 fix (Ley 6380 art. 56 num. 10: gains on listed shares traded through the Bolsa exempt); the stacked 1.x line now charges them 0, as the statute does.
-/

namespace PyGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon PyGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- One charge per taxable disposal: base = the price, relieved = the taxable gain, due = `tax d`. -/
def cgtCharges (name statute : String) (taxable : Disposal → Bool) (gain tax : Disposal → Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.disposals.zipIdx.filter fun (d, _) => taxable d).map fun (d, i) =>
    charge .pit name d.proceeds (fun _ => gain d) (fun _ => tax d) (event := s!"disposal {i + 1}") (statute := statute)

def other3 (d : Disposal) : Bool := d.kind == .deposits || d.kind == .pensionFund

def movable (d : Disposal) : Bool := d.kind == .vehicle || d.kind == .other
def movTotal (g : CanonGlobal) : Int := isum ((g.disposals.filter movable).map (·.proceeds))
/-- Art. 56 num. 9-10: listed shares and listed bonds exempt; num. 3: movables while the year's total is at most
G. 20.000.000. -/
def taxable (g : CanonGlobal) (d : Disposal) : Bool :=
  d.kind == .realEstate || d.kind == .land || d.kind == .home || d.kind == .unlistedShares || d.kind == .business
    || (d.kind == .bonds && !d.listed) || (movable d && decide (movTotal g > 20000000))
/-- Art. 59.1: the lesser of 30 % of the price and the price less the purchase price and selling costs. -/
def gainOf (d : Disposal) : Int := pos (min (divR .down (3000 * d.proceeds) BP) (d.proceeds - d.cost - d.costs))
def taxOf (d : Disposal) : Int := divR .down (800 * gainOf d) BP

def cgF : Family :=
  { name := "1100 IRP rentas y ganancias del capital (Ley 6380 arts. 56, 59, 60)", covers := [.pit],
    run := fun _ g _ => cgtCharges "IRP: rentas y ganancias del capital (8 %)" "Ley 6380/2019 IRP art. 60: \"La tasa aplicable para las rentas y ganancias del capital será del 8% (ocho por ciento)\"; art. 59.1: \"la Renta Neta constituirá la que resulte menor entre: El 30% (treinta por ciento) del valor de venta; o b) La diferencia entre el precio de venta y el precio de compra del bien más los gastos de venta\"; art. 56 num. 3 (movables to G. 20.000.000 a year), num. 9-10 (securities traded through the Bolsas de Valores)" (taxable g) gainOf taxOf g }

def families : List Family := [capF, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.entity == .company then [] else
  when (g.disposals.any fun d => taxable g d) "IRP gains: each disposal on its own (art. 53: separate by category; losses not offset here); option b) of art. 59.1 assumes documented purchase price"
  ++ when (g.disposals.any isLongListed) "listed shares held over 12 months are routed into the 1.x `capitalGains`, which the 1.x model exempts (art. 56 num. 10; 1.x fix MS-1, vendored copy refreshed in pass 12)"
  ++ when (g.disposals.any fun d => d.kind == .home && d.mainHome) "no main-home exemption in Ley 6380 (the home is taxed like other real estate)")
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"
  ++ when (g.entity != .company && (g.disposals.any isLongListed || g.incomes.any fun i => i.kind == .interest || i.kind == .dividend || i.kind == .rent)) "additional capital income is routed into the 1.x household totals and taxed as the 1.x model taxes them (its conventions: split between adults, long-held listed shares)"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
-- min(30 % x 1,000,000,000, 500,000,000) = 300,000,000; 8 % = 24,000,000
#guard taxOf { kind := .realEstate, proceeds := 1000000000, cost := 500000000 } == 24000000
-- min(300,000,000, 100,000,000) = 100,000,000 -> 8,000,000
#guard taxOf { kind := .realEstate, proceeds := 1000000000, cost := 900000000 } == 8000000
#guard taxable { id := "g", household := { id := "g" }, disposals := [{ kind := .vehicle, proceeds := 15000000, cost := 0 }] } { kind := .vehicle, proceeds := 15000000, cost := 0 } == false
#guard taxable { id := "g", household := { id := "g" } } { kind := .listedShares, proceeds := 1, cost := 0 } == false

end PyGlobal.Capital
