import NiGlobal.Pit

/-!
# NI 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

## Pass 11 (2026-11-21): capital gains of individuals

Ley 822 (Ley de Concertación Tributaria) as reformed by Ley 891 (2014) and **Ley 987** (28 Feb 2019; `world/B12-latin-america/ni/src/`,
`americas/ni/law/ley987_leybook.txt`): **art. 87 num. 2** 15 % for residents; **arts. 82-83** gain = transmission value less
acquisition cost updated by the córdoba/dollar rate (`indexBp`). Registered property (num. 4 bands) stays grade C.
-/

namespace NiGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon NiGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- One charge per taxable disposal: base = the price, relieved = the taxable gain, due = `tax d`. -/
def cgtCharges (name statute : String) (taxable : Disposal → Bool) (gain tax : Disposal → Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.disposals.zipIdx.filter fun (d, _) => taxable d).map fun (d, i) =>
    charge .pit name d.proceeds (fun _ => gain d) (fun _ => tax d) (event := s!"disposal {i + 1}") (statute := statute)

def other3 (d : Disposal) : Bool := d.kind == .deposits || d.kind == .pensionFund

def isReg (d : Disposal) : Bool := d.kind == .realEstate || d.kind == .land || d.kind == .home || d.kind == .vehicle
/-- Ley 987 art. 87 num. 2: 15 %. Registered property (real estate, vehicles: art. 87 num. 4, definitive withholding by
value band) is listed, not charged here. -/
def taxable (_g : CanonGlobal) (d : Disposal) : Bool := !isReg d && !other3 d
/-- Art. 83: transmission value less acquisition cost updated by the exchange rate (`indexBp`) and costs. -/
def gainOf (d : Disposal) : Int := pos (d.proceeds - divR .down (d.cost * d.indexBp) BP - d.costs)
def taxOf (d : Disposal) : Int := divR .down (1500 * gainOf d) BP

def cgF : Family :=
  { name := "1100 ganancias de capital (Ley 822 arts. 82-87, Ley 987)", covers := [.pit],
    run := fun _ g _ => cgtCharges "IR de rentas de capital y ganancias de capital: ganancias (15 %)" "Ley 822 (LCT) art. 87 as amended by Ley 987 (28 Feb 2019): \"2. Quince por ciento (15%), para residentes y no residentes\"; arts. 82-83: \"la diferencia entre el valor de transmisión y su costo de adquisición\", cost updated by the córdoba/dollar exchange rate (Ley 891 art. 83.1.d)" (taxable g) gainOf taxOf g }

def families : List Family := [capF, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.entity == .company then [] else
  when (g.disposals.any isReg) "registered property (real estate, vehicles): definitive withholding of 1-7 % of the value by band (art. 87 num. 4; columns of the held text not read reliably): not charged (grade C)"
  ++ when (g.disposals.any fun d => taxable g d) "ganancias de capital: the 60 % presumed gain without documented cost (art. 83.3) and the loss carry-forward (art. 86) not modelled")
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"
  ++ when (g.entity != .company && (g.disposals.any isLongListed || g.incomes.any fun i => i.kind == .interest || i.kind == .dividend || i.kind == .rent)) "additional capital income is routed into the 1.x household totals and taxed as the 1.x model taxes them (its conventions: split between adults, long-held listed shares)"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
#guard taxOf { kind := .unlistedShares, proceeds := 100000, cost := 50000, indexBp := 11000 } == 6750
#guard taxable { id := "g", household := { id := "g" } } { kind := .realEstate, proceeds := 1, cost := 0 } == false

end NiGlobal.Capital
