import CoGlobal.Pit

/-!
# Colombia 2025: capital income and gains (1100): stacking on the 1.x model and ganancias ocasionales

* Pass 1 (unchanged): additional interest, dividends, rent and listed-share gains held over 12 months are routed into the
  1.x household and charged as `stackedTax`.
* **Ganancias ocasionales** (Estatuto Tributario, local copy `co/law/et/`): **art. 300** "Se consideran ganancias
  ocasionales ... las provenientes de la enajenación de bienes de cualquier naturaleza, que hayan hecho parte del activo
  fijo del contribuyente por un término de dos años o más. Su cuantía se determina por la diferencia entre el precio de
  enajenación y el costo fiscal"; **art. 314** (Ley 2277 de 2022 art. 33): "la tarifa única ... es quince por ciento
  (15%)"; **art. 311-1** (Ley 2277 art. 31): "Estarán exentas las primeras cinco mil (5.000) UVT de la utilidad generada
  en la venta de la casa o apartamento de habitación" (AFC deposit conditions assumed met). UVT 2025 of the 1.x model
  (49,799). Grade A for the rule; the fiscal cost is the line's historical cost (art. 70/73 adjustments not applied).
* Gains on assets held under two years are ordinary income (renta líquida, cédula general): not modelled (listed).
-/

namespace CoGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon CoGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

def uvt : Int := CoTax.uvt
/-- ET art. 300: assets held two years or more (other than listed shares held over 12 months, routed above). -/
def isGo (d : Disposal) : Bool := decide (d.heldMonths ≥ 24) && !isLongListed d
/-- ET art. 311-1: the first 5,000 UVT of the gain on the sale of the home are exempt (AFC deposit conditions). -/
def goGain (d : Disposal) : Int := if d.mainHome && d.kind == .home then pos (d.gain - 5000 * uvt) else pos d.gain
def goTax (d : Disposal) : Int := divR .down (1500 * goGain d) BP

def goF : Family :=
  { name := "1100 ganancias ocasionales (ET arts. 300, 311-1, 314)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.disposals.zipIdx.filter fun (d, _) => isGo d).map fun (d, i) =>
        charge .pit "Impuesto de ganancias ocasionales" d.gain (fun _ => goGain d) (fun b => divR .down (1500 * b) BP) (event := s!"disposal {i + 1}")
          (statute := "ET art. 300 (held 2 years or more), art. 311-1 (5,000 UVT home), art. 314 (15 %, Ley 2277 de 2022)") }

def families : List Family := [capF, goF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := stackUnsupported g
  ++ when (g.entity != .company && g.disposals.any fun d => decide (d.heldMonths < 24) && !isLongListed d) "gains on assets held under two years (ordinary income, cédula general) not modelled"
  ++ when (g.entity != .company && g.disposals.any isGo) "ganancia ocasional on the historical cost (fiscal-cost adjustments of ET arts. 70, 73 not applied); losses not offset"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
#guard uvt == 49799
#guard goTax { kind := .realEstate, proceeds := 500000000, cost := 300000000, heldMonths := 36 } == 30000000
#guard goTax { kind := .home, proceeds := 500000000, cost := 100000000, heldMonths := 36, mainHome := true } == 22650750
#guard isGo { kind := .unlistedShares, proceeds := 10, cost := 5, heldMonths := 12 } == false

end CoGlobal.Capital
