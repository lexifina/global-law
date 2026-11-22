import EcGlobal.Pit

/-!
# EC 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

## Pass 11 (2026-11-21): capital gains of individuals

LRTI, last reform 24 Oct 2025 (`world/B12-latin-america/ec/src/lrti.txt`): impuesto a la renta único **10 %** on the gain on
shares (artículo innumerado, RO 587 of 2021), base = real value less cost and directly related costs. **Art. 9 num. 14**
(RO 699 of 9 Dec 2024): occasional real-estate sales exempt, up to two a year (modelled as no charge). Listed shares
(50 fracciones básicas exemption, value not held) and other assets: listed, grade C.
-/

namespace EcGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon EcGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- One charge per taxable disposal: base = the price, relieved = the taxable gain, due = `tax d`. -/
def cgtCharges (name statute : String) (taxable : Disposal → Bool) (gain tax : Disposal → Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.disposals.zipIdx.filter fun (d, _) => taxable d).map fun (d, i) =>
    charge .pit name d.proceeds (fun _ => gain d) (fun _ => tax d) (event := s!"disposal {i + 1}") (statute := statute)

def other3 (d : Disposal) : Bool := d.kind == .deposits || d.kind == .pensionFund

def isRe (d : Disposal) : Bool := d.kind == .realEstate || d.kind == .land || d.kind == .home
def reCount (g : CanonGlobal) : Nat := (g.disposals.filter isRe).length
/-- Unlisted shares: impuesto único 10 %. Listed shares (art. 9 num. 24: exempt to 50 fracciones básicas a year) and
other assets (progressive scale) are listed, not charged; occasional real estate, up to two sales a year, is exempt. -/
def taxable (_g : CanonGlobal) (d : Disposal) : Bool := d.kind == .unlistedShares
def gainOf (d : Disposal) : Int := pos (d.proceeds - d.cost - d.costs)
def taxOf (d : Disposal) : Int := divR .down (1000 * gainOf d) BP

def cgF : Family :=
  { name := "1100 impuesto a la renta único: utilidad en la enajenación de acciones (LRTI)", covers := [.pit],
    run := fun _ g _ => cgtCharges "Impuesto a la renta único sobre utilidades en la enajenación de acciones (10 %)" "LRTI (last reform 24 Oct 2025) artículo innumerado: share gains of individuals \"estarán sujetas, al momento de la enajenación, a un impuesto a la renta único con tarifa del 10%\"; base: \"valor real de la enajenación\" less acquisition cost and \"gastos directamente relacionados\"; art. 9 num. 14 (RO 699 of 9 Dec 2024): \"la enajenación ocasional de inmuebles ... hasta por dos (2) enajenaciones por año\" exempt" (taxable g) gainOf taxOf g }

def families : List Family := [capF, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.entity == .company then [] else
  when (g.disposals.any fun d => d.kind == .listedShares) "listed shares: exempt to 50 fracciones básicas a year (art. 9 num. 24; 2025 fracción básica not held), excess 5 %: not charged (grade C)"
  ++ when (decide (reCount g > 2)) "more than two real-estate sales in the year: not occasional (art. 9 num. 14), progressive scale: not modelled (grade C)"
  ++ when (g.disposals.any fun d => !isRe d && d.kind != .unlistedShares && d.kind != .listedShares && !other3 d) "gains on other assets (bonds, movables, business): renta gravada at the art. 36 scale (no separate rate in the held text): not modelled (grade C)")
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"
  ++ when (g.entity != .company && (g.disposals.any isLongListed || g.incomes.any fun i => i.kind == .interest || i.kind == .dividend || i.kind == .rent)) "additional capital income is routed into the 1.x household totals and taxed as the 1.x model taxes them (its conventions: split between adults, long-held listed shares)"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
#guard taxOf { kind := .unlistedShares, proceeds := 50000, cost := 20000 } == 3000
#guard reCount { id := "g", household := { id := "g" }, disposals := [{ kind := .home, proceeds := 1, cost := 0 }, { kind := .listedShares, proceeds := 1, cost := 0 }] } == 1

end EcGlobal.Capital
