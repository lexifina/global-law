import DoGlobal.Pit
import TaxKernel.Global2

/-!
# DO 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

## Pass 11 (2026-11-21): capital gains at the art. 296 scale (kernel 2.5.0 `StackRule`)

Código Tributario Título II (`world/B13-caribbean/do/law/t2.txt`, consolidated to Ley 253-12): **art. 283** renta bruta
includes "toda otra ganancia", **art. 289** gain = price less cost adjusted by inflation (art. 327; `indexBp`), no separate
rate: the art. 296 scale. Stacked into each seller's `selfEmployment`, which the 1.x model adds in full to the taxable
income (`DoTax.person`: wages + selfEmployment, no income-tested credit, so the slice cannot fall). **Art. 299 m)**: the
first RD$500,000 of the gain on the casa habitación exempt (`mainHomeCap`). Guard: RD$1,000,000 gain on no other
income = 112,995 by hand from the DGII 2025 table.
-/

namespace DoGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon DoGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- CT art. 289: each gain (cost adjusted by inflation: `indexBp`) enters the renta bruta and the art. 296 scale; the 1.x
model taxes each adult's `selfEmployment` in full at that scale (no credit that falls with income); art. 299 m): the first
RD$500,000 of the gain on the casa habitación exempt. -/
def doCg : StackRule :=
  { name := "ISR: ganancia de capital en la renta neta gravable (CT arts. 283, 289, 296)",
    statute := "Código Tributario (Ley 11-92) Título II art. 283 (renta bruta includes \"toda otra ganancia\"), art. 289: \"se deducirá del precio o valor de enajenación del respectivo bien, el costo de adquisición o producción ajustado por inflación, conforme a lo previsto en el artículo 327\"; art. 299 m): \"El beneficio obtenido hasta la suma de RD$500,000.00 en la enajenación de la casa habitación\"; rates: art. 296 scale (1.x model, DGII 2025 table)",
    gainKinds := [.home, .realEstate, .land, .listedShares, .unlistedShares, .bonds, .business, .vehicle, .other],
    gainRule := { indexCost := true, mainHomeExempt := true, mainHomeCap := 500000 }, into := .selfEmployment }

def cgF : Family := stackRuleFamily base.pit base.route [doCg] "1100 ganancias de capital (CT arts. 289, 296)"

def gx (d : Disposal) : CanonGlobal := { id := "gx", household := { id := "gx", adults := [{}] }, disposals := [d] }

def families : List Family := [capF, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.entity == .company then [] else
  stackUnknown base.pit base.route [doCg] [] g
  ++ when (g.disposals.any fun d => d.kind == .home && d.mainHome) "casa habitación: the RD$500,000 exemption (art. 299 m) assumes the 3-year ownership and use condition is met"
  ++ when (g.disposals.any fun d => d.kind != .deposits && d.kind != .pensionFund) "ganancias de capital: losses offset within the year only (art. 289 i carry-forward not modelled); held Title II text consolidated to Ley 253-12; inflation factor only via indexBp"
  ++ when (g.disposals.any fun d => d.kind == .deposits || d.kind == .pensionFund) "deposits and pension-fund rights: not a capital-gain disposal here (grade C)")
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
-- gain 1,000,000 on no other income: 79,776 + 25 % x (1,000,000 - 867,123) = 112,995
#guard ((cgF.run [] (gx { kind := .realEstate, proceeds := 2000000, cost := 1000000 }) []).map (·.due)) == [112995]
-- casa habitación: 1,000,000 - 500,000 = 500,000 -> 15 % x 83,780 = 12,567; cost indexed x 1.5 likewise
#guard ((cgF.run [] (gx { kind := .home, proceeds := 2000000, cost := 1000000, mainHome := true }) []).map (·.due)) == [12567]
#guard ((cgF.run [] (gx { kind := .land, proceeds := 2000000, cost := 1000000, indexBp := 15000 }) []).map (·.due)) == [12567]

end DoGlobal.Capital
