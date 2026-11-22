import PeGlobal.Pit

/-!
# PE 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

## Pass 11 (2026-11-21): second-category capital gains (LIR arts. 2, 21, 36, 52-A)

Source: LIR TUO (D.S. 179-2004-EF), SUNAT consolidated text, chapters I, IV, V, VI, VII (`pe/law/lir_cap*.txt`,
fetched 2026-11-21). The 1.x model ignores `capitalGains` (its own note), so the stacked route charged 0 for gains.
Now: an individual's gain on shares, bonds and other securities (art. 2 a), DL 1120) and on real estate other than
the casa habitación (art. 2, DL 945, "No constituye ganancia de capital gravable ... i) Inmuebles ocupados como
casa habitación"; movables excluded, ii)) is renta de segunda categoría: **art. 36** "se deducirá por todo
concepto el veinte por ciento (20%) del total de la renta bruta" (dividends excepted), securities losses offset in
the year only; **art. 52-A** "seis coma veinticinco por ciento (6,25%)" on the renta neta, i.e. 5 % of the gain.
Real-estate cost: **art. 21.1 a.1)** reajustado by the MEF index (`indexBp`). The art. 19 p) 5 UIT exemption was
repealed by DL 1120 (from 2013) and the Ley 30341 listed-share exemption was last extended to 31.12.2023 (Ley 31662):
neither applies in 2025. Per person (each seller's disposals). Listed (grade C or flagged): real estate acquired
before 2004 (DL 945 transitional rule, not held), habitualidad (art. 4), business sales.
-/

namespace PeGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon PeGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- LIR art. 2 a): shares, participations, bonds and other securities (an individual's gain on them is always second
category: DL 1112, tercera disposición complementaria final). -/
def isSec (d : Disposal) : Bool := d.kind == .listedShares || d.kind == .unlistedShares || d.kind == .bonds
/-- Real estate, not the casa habitación (art. 2 i)); acquired before 2004: not charged here (listed, grade C). -/
def isRe (d : Disposal) : Bool :=
  (d.kind == .realEstate || d.kind == .land || (d.kind == .home && !d.mainHome)) && (d.acquiredYear == 0 || decide (d.acquiredYear ≥ 2004))
/-- Art. 21.1 a.1): real estate cost reajustado by the MEF index (`indexBp`). -/
def reGain (d : Disposal) : Int := d.proceeds - divR .down (d.cost * d.indexBp) BP - d.costs
/-- Renta bruta of one person: securities gains net of securities losses (art. 36, second paragraph: the same year
only), plus real-estate gains (a real-estate loss is not offset). -/
def brutaOf (ds : List Disposal) : Int :=
  pos (isum ((ds.filter isSec).map (·.gain))) + isum ((ds.filter isRe).map fun d => pos (reGain d))
/-- Art. 36: renta neta = renta bruta less 20 %. -/
def netaOf (b : Int) : Int := b - divR .down (2000 * b) BP
def cgTax (b : Int) : Int := divR .down (625 * netaOf b) BP

def cgF : Family :=
  { name := "1100 rentas de segunda categoría: ganancias de capital (LIR arts. 2, 36, 52-A)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.disposals.map (·.person)).eraseDups.filterMap fun p =>
        let ds := g.disposals.filter (·.person == p)
        if ds.any (fun d => isSec d || isRe d) then some (p, brutaOf ds) else none).map fun (p, b) =>
        charge .pit "Impuesto a la renta de segunda categoría: ganancias de capital (6,25 % de la renta neta)" b netaOf
          (fun r => divR .down (625 * r) BP) (event := s!"person {p + 1} disposals") (statute := "LIR (TUO D.S. 179-2004-EF, SUNAT consolidated text) art. 2 a) (DL 1120: acciones, bonos y otros valores mobiliarios) and art. 2 (DL 945: inmuebles; \"No constituye ganancia de capital gravable ... i) Inmuebles ocupados como casa habitación del enajenante\"); art. 21.1 a.1) (costo computable reajustado por los índices de corrección monetaria); art. 36 (\"se deducirá por todo concepto el veinte por ciento (20%) del total de la renta bruta\"; losses on art. 2 a) assets offset in the year only); art. 52-A (\"seis coma veinticinco por ciento (6,25%)\")") }

def families : List Family := [capF, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.entity == .company then [] else
  when (g.disposals.any fun d => d.kind == .business || d.kind == .pensionFund || d.kind == .deposits) "disposals of a business (negocios o empresas: third category, art. 2 b) 5)), pension-fund or deposit rights: not modelled (grade C); movables (vehicles, other) are outside the gain (art. 2 ii))"
  ++ when (g.disposals.any fun d => (d.kind == .realEstate || d.kind == .land || (d.kind == .home && !d.mainHome)) && d.acquiredYear != 0 && decide (d.acquiredYear < 2004)) "real estate acquired before 1.1.2004: outside the second-category gain (DL 945 transitional rule, text not held): not charged (grade C)"
  ++ when (g.disposals.any fun d => (d.kind == .realEstate || d.kind == .land || d.kind == .home) && d.acquiredYear == 0) "real estate without an acquisition year: read as acquired from 2004"
  ++ when (decide ((g.disposals.filter isRe).length ≥ 3)) "three or more real-estate sales in the year: habitualidad (LIR art. 4, third category) not modelled; taxed here as second category"
  ++ when (g.disposals.any isSec) "securities: historical cost (DCT 3 of DL 972 valuation of pre-2009 shares not applied); art. 36 wash-sale rule not modelled; listed shares are also routed (1.x capitalGains, which the 1.x model ignores: 0)")
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"
  ++ when (g.entity != .company && (g.disposals.any isLongListed || g.incomes.any fun i => i.kind == .interest || i.kind == .dividend || i.kind == .rent)) "additional capital income is routed into the 1.x household totals and taxed as the 1.x model taxes them (its conventions: split between adults, long-held listed shares)"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
-- 500,000 - 300,000 = 200,000; less 20 % = 160,000; x 6.25 % = 10,000 (5 % of the gain)
#guard cgTax (brutaOf [{ kind := .realEstate, proceeds := 500000, cost := 300000, acquiredYear := 2010 }]) == 10000
-- securities: 40,000 gain - 20,000 loss = 20,000 -> 16,000 -> 1,000
#guard cgTax (brutaOf [{ kind := .listedShares, proceeds := 100000, cost := 60000 }, { kind := .unlistedShares, proceeds := 50000, cost := 70000 }]) == 1000
-- a real-estate loss does not offset a share gain: 50,000 -> 40,000 -> 2,500
#guard cgTax (brutaOf [{ kind := .realEstate, proceeds := 100000, cost := 150000 }, { kind := .listedShares, proceeds := 100000, cost := 50000 }]) == 2500
-- MEF index 1.25: 400,000 - 250,000 = 150,000 -> 120,000 -> 7,500
#guard cgTax (brutaOf [{ kind := .land, proceeds := 400000, cost := 200000, indexBp := 12500, acquiredYear := 2015 }]) == 7500
#guard isRe { kind := .home, proceeds := 10, cost := 5, mainHome := true } == false
#guard isRe { kind := .realEstate, proceeds := 10, cost := 5, acquiredYear := 2003 } == false
#guard ((cgF.run [] { id := "g", household := { id := "g" }, disposals := [{ kind := .realEstate, proceeds := 500000, cost := 300000 }, { kind := .listedShares, proceeds := 10, cost := 5, person := 1 }] } []).map (·.due)) == [10000, 0]

end PeGlobal.Capital
