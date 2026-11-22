import SvGlobal.Pit

/-!
# SV 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

## Pass 11 (2026-11-21): capital gains of individuals

LISR D.L. 134 (`americas/sv/law/ssf_lisr.txt`, reforms to D.L. 233 of 14 Dec 2012): **art. 42** 10 % on the net gain unless
the asset is sold within 12 months of acquisition (then ordinary income: grade C), **art. 14** gain = transaction value
less basic cost, improvements and costs, **art. 14-A** securities at 10 % separately. Grade B (later reforms not checked).
-/

namespace SvGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon SvGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- One charge per taxable disposal: base = the price, relieved = the taxable gain, due = `tax d`. -/
def cgtCharges (name statute : String) (taxable : Disposal → Bool) (gain tax : Disposal → Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.disposals.zipIdx.filter fun (d, _) => taxable d).map fun (d, i) =>
    charge .pit name d.proceeds (fun _ => gain d) (fun _ => tax d) (event := s!"disposal {i + 1}") (statute := statute)

def other3 (d : Disposal) : Bool := d.kind == .deposits || d.kind == .pensionFund

def isSec (d : Disposal) : Bool := d.kind == .listedShares || d.kind == .unlistedShares || d.kind == .bonds
/-- Art. 42: 10 % when held more than 12 months (sold within 12 months: ordinary income, not here); art. 14-A securities
10 % separately; the first home (art. 4 num. 12, to 723 salarios mínimos) is not charged here (listed). -/
def taxable (_g : CanonGlobal) (d : Disposal) : Bool :=
  !other3 d && !(d.kind == .home && d.mainHome) && (isSec d || decide (d.heldMonths > 12))
def gainOf (d : Disposal) : Int := pos (d.proceeds - d.cost - d.costs)
def taxOf (d : Disposal) : Int := divR .down (1000 * gainOf d) BP

def cgF : Family :=
  { name := "1100 ganancia de capital (LISR arts. 14, 14-A, 42)", covers := [.pit],
    run := fun _ g _ => cgtCharges "Impuesto sobre la ganancia de capital (10 %)" "LISR (D.L. 134, text with reforms to D.L. 233 of 2012) art. 42: \"EL DIEZ POR CIENTO (10%) DE DICHAS GANANCIAS, SALVO CUANDO EL BIEN SE REALICE DENTRO DE LOS DOCE MESES SIGUIENTES A LA FECHA DE SU ADQUISICIÓN\"; art. 14 (valor de la transacción less costo básico, mejoras and gastos); art. 14-A (securities: \"A UNA TASA DEL DIEZ POR CIENTO, LA CUAL SE LIQUIDARÁ SEPARADAMENTE\")" (taxable g) gainOf taxOf g }

def families : List Family := [capF, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.entity == .company then [] else
  when (g.disposals.any fun d => !other3 d && !isSec d && decide (d.heldMonths ≤ 12)) "assets other than securities sold within 12 months: ganancia added to the renta neta imponible ordinaria (art. 42): not modelled (grade C)"
  ++ when (g.disposals.any fun d => d.kind == .home && d.mainHome) "first home (art. 4 num. 12: exempt when the price is at most 723 salarios mínimos; salario mínimo not held): not charged (grade C)"
  ++ when (g.disposals.any fun d => taxable g d) "ganancia de capital: held LISR text has reforms to 2012 only (later reforms not checked); each disposal on its own (loss offset and 5-year carry-forward not modelled)")
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"
  ++ when (g.entity != .company && (g.disposals.any isLongListed || g.incomes.any fun i => i.kind == .interest || i.kind == .dividend || i.kind == .rent)) "additional capital income is routed into the 1.x household totals and taxed as the 1.x model taxes them (its conventions: split between adults, long-held listed shares)"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
#guard taxOf { kind := .realEstate, proceeds := 200000, cost := 120000, heldMonths := 36 } == 8000
#guard taxable { id := "g", household := { id := "g" } } { kind := .realEstate, proceeds := 1, cost := 0, heldMonths := 12 } == false
#guard taxable { id := "g", household := { id := "g" } } { kind := .unlistedShares, proceeds := 1, cost := 0, heldMonths := 3 } == true

end SvGlobal.Capital
