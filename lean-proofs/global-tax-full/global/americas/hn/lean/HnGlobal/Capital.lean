import HnGlobal.Pit

/-!
# HN 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

## Pass 11 (2026-11-21): capital gains of individuals

LISR consolidated to Acuerdo SAR 07-2025 (`world/B12-latin-america/hn/src/lisr.txt`): **art. 10** impuesto único 10 % on
ganancias de capital, outside the progressive scale. The held text has no base, exemption or loss rule: the base is read
as price less cost and costs (grade B). The 1.x model ignores `capitalGains`, so every kind is charged here.
-/

namespace HnGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon HnGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- One charge per taxable disposal: base = the price, relieved = the taxable gain, due = `tax d`. -/
def cgtCharges (name statute : String) (taxable : Disposal → Bool) (gain tax : Disposal → Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.disposals.zipIdx.filter fun (d, _) => taxable d).map fun (d, i) =>
    charge .pit name d.proceeds (fun _ => gain d) (fun _ => tax d) (event := s!"disposal {i + 1}") (statute := statute)

def other3 (d : Disposal) : Bool := d.kind == .deposits || d.kind == .pensionFund

def taxable (_g : CanonGlobal) (d : Disposal) : Bool := !other3 d
/-- The held text gives no base rule: price less cost and costs (our reading; grade B). -/
def gainOf (d : Disposal) : Int := pos (d.proceeds - d.cost - d.costs)
def taxOf (d : Disposal) : Int := divR .down (1000 * gainOf d) BP

def cgF : Family :=
  { name := "1100 ganancias de capital (LISR art. 10)", covers := [.pit],
    run := fun _ g _ => cgtCharges "Impuesto único sobre ganancias de capital (10 %)" "LISR (consolidated to Acuerdo SAR 07-2025) art. 10: \"las ganancias de capital obtenidas por las personas naturales ... pagarán un impuesto único del 10% (diez por ciento) por lo que no estarán sujetas a la tarifa progresiva\"; base read as price less cost (not defined in the held text)" (taxable g) gainOf taxOf g }

def families : List Family := [capF, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.entity == .company then [] else
  when (g.disposals.any fun d => taxable g d) "ganancias de capital: the base (price less cost and costs) is not defined in the held text; no exemption read (main home, listed shares, movables); losses not offset")
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"
  ++ when (g.entity != .company && (g.disposals.any isLongListed || g.incomes.any fun i => i.kind == .interest || i.kind == .dividend || i.kind == .rent)) "additional capital income is routed into the 1.x household totals and taxed as the 1.x model taxes them (its conventions: split between adults, long-held listed shares)"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
#guard taxOf { kind := .realEstate, proceeds := 1000000, cost := 700000, costs := 50000 } == 25000

end HnGlobal.Capital
