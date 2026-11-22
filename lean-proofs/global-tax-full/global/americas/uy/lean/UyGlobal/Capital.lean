import UyGlobal.Pit

/-!
# UY 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

**Pass 12 (2026-11-21), incrementos patrimoniales of individuals (IRPF Categoría I, grade A):** T.O. DGI 2023 Título 7
(IMPO `bases/todgi-2023/7-2024`, fetched 2026-11-21, `uy/law/todgi_t7_2024.*`; the incisos added by Ley 20.446 of
16.12.2025 apply from 2026 and are not used). **Art. 29** (inmuebles): gain = price less the "costo fiscal actualizado"
(acquisition value x the UI increase: the disposal's `indexBp`) plus the seller's ITP (read as the disposal's `costs`);
for non-rural property acquired before 1 July 2007 the taxpayer may take 15 % of the price instead (taken when lower:
`acquiredYear` <= 2006; 2007 acquisitions and an unknown year get no option). **Art. 32** (other transmissions): the same
rules; for goods acquired before Ley 18.083 the option of 20 % of the price (taken when lower). **Art. 37**: "Restantes
Rentas 12 %". Not charged here: listed shares (art. 38 E exempts shares listed at 30 Sep 2010 and others meeting its
conditions; long-held listed shares stay in the 1.x route, which does not tax them), public-debt bonds (art. 38 A; all
bonds read so), deposits and pension funds; the vivienda permanente (art. 38 L: price <= 1,200,000 UI and 50 % reinvested
- reinvestment and the UI value are not inputs: grade C); small transmissions of art. 38 I (30,000 / 90,000 UI: the UI
value of the sale date not held - not applied, upper bound); loss offset (art. 34) not modelled.
-/

namespace UyGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon UyGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- One charge per taxable disposal: base = the price, relieved = the taxable gain, due = `tax d`. -/
def cgtCharges (name statute : String) (taxable : Disposal → Bool) (gain tax : Disposal → Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.disposals.zipIdx.filter fun (d, _) => taxable d).map fun (d, i) =>
    charge .pit name d.proceeds (fun _ => gain d) (fun _ => tax d) (event := s!"disposal {i + 1}") (statute := statute)

/-- Not charged by this family: listed shares (art. 38 E), bonds (art. 38 A), deposits, pension funds, the main home (art. 38 L, grade C). -/
def taxable (d : Disposal) : Bool :=
  d.kind != .listedShares && d.kind != .bonds && d.kind != .deposits && d.kind != .pensionFund && !(d.kind == .home && d.mainHome)
/-- Arts. 29, 32: price less the UI-updated cost and the seller's costs (ITP). -/
def fullGain (d : Disposal) : Int := pos (d.proceeds - divR .down (d.cost * d.indexBp) BP - pos d.costs)
/-- Art. 29 (non-rural property bought before 1 July 2007: 15 % of the price) and art. 32 (goods bought before Ley 18.083: 20 %). -/
def gainOf (d : Disposal) : Int :=
  if d.acquiredYear != 0 && d.acquiredYear ≤ 2006 then
    min (fullGain d) (divR .down ((if d.kind.isRealEstate then 1500 else 2000) * d.proceeds) BP)
  else fullGain d
def taxOf (d : Disposal) : Int := divR .down (1200 * gainOf d) BP

def cgF : Family :=
  { name := "1100 IRPF incrementos patrimoniales (T.O. DGI Título 7 arts. 26-37)", covers := [.pit],
    run := fun _ g _ => cgtCharges "IRPF Categoría I: incrementos patrimoniales (12 %)" "T.O. DGI 2023 Título 7 art. 29 (price less the costo fiscal actualizado by the UI, plus the seller's ITP; non-rural property acquired before 1.7.2007: optionally 15 % of the price), art. 32 (other transmissions: same rules; goods acquired before Ley 18.083: optionally 20 % of the price), art. 37 (restantes rentas 12 %)" taxable gainOf taxOf g }

def families : List Family := [capF, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := stackUnsupported g ++ (if g.entity == .company then [] else
  when (g.disposals.any taxable) "incrementos patrimoniales: each disposal on its own (art. 34 loss offset not modelled); the disposal's costs read as the seller's ITP; the art. 38 I small-transmission exemption (30,000 / 90,000 UI) not applied (UI value of the sale date not held); land read as non-rural for the 15 % option"
  ++ when (g.disposals.any fun d => d.kind == .home && d.mainHome) "vivienda permanente (art. 38 L: exempt up to 1,200,000 UI if at least 50 % is reinvested in a new permanent home): reinvestment and the UI value are not inputs - not charged (grade C)"
  ++ when (g.disposals.any fun d => d.kind == .listedShares || d.kind == .bonds) "listed shares (art. 38 E) and bonds (art. 38 A, read as public debt): not charged")

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
-- 1,000,000 - 600,000 x 1.2 - 20,000 = 260,000; 12 % = 31,200
#guard taxOf { kind := .realEstate, proceeds := 1000000, cost := 600000, costs := 20000, indexBp := 12000, acquiredYear := 2015 } == 31200
-- bought 2005: gain 800,000, 15 % of the price 150,000 is lower: 18,000
#guard taxOf { kind := .realEstate, proceeds := 1000000, cost := 200000, acquiredYear := 2005 } == 18000
-- a vehicle bought 2004 for nothing documented: 20 % of 100,000 = 20,000; 12 % = 2,400
#guard taxOf { kind := .vehicle, proceeds := 100000, cost := 0, acquiredYear := 2004 } == 2400
#guard taxable { kind := .home, proceeds := 1, cost := 0, mainHome := true } == false

end UyGlobal.Capital
