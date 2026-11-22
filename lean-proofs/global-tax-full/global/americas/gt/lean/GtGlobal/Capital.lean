import GtGlobal.Pit

/-!
# GT 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

## Pass 11 (2026-11-21): capital gains of individuals

Decreto 10-2012 Título IV (`world/B12-latin-america/gt/src/d10_2012.txt`): **art. 92** "para las ganancias de capital es
del diez por ciento (10%)", **art. 89** base = price less the acquisition value less selling costs (at most 15 % of the
price), **art. 15** taxed separately, **art. 87** personal movables exempt except registered vehicles, boats and aircraft.
No main-home or stock-exchange exemption in the text. Long-held listed shares stay with the 1.x model (10 % gross).
-/

namespace GtGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon GtGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- One charge per taxable disposal: base = the price, relieved = the taxable gain, due = `tax d`. -/
def cgtCharges (name statute : String) (taxable : Disposal → Bool) (gain tax : Disposal → Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.disposals.zipIdx.filter fun (d, _) => taxable d).map fun (d, i) =>
    charge .pit name d.proceeds (fun _ => gain d) (fun _ => tax d) (event := s!"disposal {i + 1}") (statute := statute)

def other3 (d : Disposal) : Bool := d.kind == .deposits || d.kind == .pensionFund

/-- Long-held listed shares stay in the 1.x model (`capitalGains`, art. 92 10 % on the gross amount); art. 87: personal
movables (`other`) are not taxed; deposits and pension-fund rights are not capital-gain assets here. -/
def taxable (_g : CanonGlobal) (d : Disposal) : Bool := !isLongListed d && d.kind != .other && !other3 d
/-- Art. 89: price less acquisition value less selling costs capped at 15 % of the price. -/
def gainOf (d : Disposal) : Int := pos (d.proceeds - d.cost - min (pos d.costs) (divR .down (1500 * d.proceeds) BP))
def taxOf (d : Disposal) : Int := divR .down (1000 * gainOf d) BP

def cgF : Family :=
  { name := "1100 ganancias de capital (Decreto 10-2012 arts. 87-92)", covers := [.pit],
    run := fun _ g _ => cgtCharges "Impuesto sobre ganancias de capital (10 %)" "Decreto 10-2012 (Ley de Actualización Tributaria, reformed by Decreto 19-2013) art. 89: \"el precio de la enajenación de los bienes o derechos menos el costo\" (non-bookkeepers: \"el valor de adquisición\"), selling costs \"como máximo al equivalente del quince por ciento (15%) del valor de la enajenación\"; art. 92: \"para las ganancias de capital es del diez por ciento (10%)\"; art. 15: taxed separately; art. 87: personal movables exempt \"salvo ... vehículos, embarcaciones y aeronaves\"" (taxable g) gainOf taxOf g }

def families : List Family := [capF, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.entity == .company then [] else
  when (g.disposals.any fun d => taxable g d) "capital gains: each disposal on its own (art. 91: losses only against future gains of the same kind within 2 years, not modelled); historical cost (no indexation in art. 89)"
  ++ when (g.disposals.any fun d => d.kind == .other) "personal movables (art. 87): not taxed")
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"
  ++ when (g.entity != .company && (g.disposals.any isLongListed || g.incomes.any fun i => i.kind == .interest || i.kind == .dividend || i.kind == .rent)) "additional capital income is routed into the 1.x household totals and taxed as the 1.x model taxes them (its conventions: split between adults, long-held listed shares)"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
-- 1,000,000 - 600,000 - min(200,000, 150,000) = 250,000; 10 % = 25,000
#guard taxOf { kind := .realEstate, proceeds := 1000000, cost := 600000, costs := 200000 } == 25000
#guard taxable { id := "g", household := { id := "g" } } { kind := .other, proceeds := 1, cost := 0 } == false
#guard taxable { id := "g", household := { id := "g" } } { kind := .vehicle, proceeds := 1, cost := 0 } == true

end GtGlobal.Capital
