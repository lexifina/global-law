import ArGlobal.Pit

/-!
# Argentina 2025: capital income and gains (1100): stacking on the 1.x model and the impuesto cedular

* Pass 1 (unchanged): additional interest, dividends, rent and listed-share gains held over 12 months are routed into the
  1.x household and charged as `stackedTax`.
* **Impuesto cedular** (Ley de Impuesto a las Ganancias, t.o. Decreto 824/2019, texto actualizado, local copy
  `ar/law/lig_actualizado.txt`): **art. 99** "La ganancia de las personas humanas ... derivada de la enajenación de ...
  inmuebles situados en la REPÚBLICA ARGENTINA, tributará a la alícuota del QUINCE POR CIENTO (15 %)"; the gain is the
  price less the cost "actualizado mediante la aplicación del índice mencionado en el segundo párrafo del artículo 93";
  **art. 98 c)**: shares that do not meet art. 26 u) or that "no cotizan" in authorised markets: "QUINCE POR CIENTO
  (15 %)". Grade B: the IPIM indexation of the cost is not applied (historical cost: upper bound), and the rule is read
  for property acquired from 1 January 2018 (earlier acquisitions stay under the impuesto a la transferencia de
  inmuebles, Ley 23.905, not held: listed as unsupported).
-/

namespace ArGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon ArGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- LIG art. 99 (inmuebles) and art. 98 c) (acciones que no cotizan): the impuesto cedular at 15 %, for property acquired
from 2018 (an unknown year, 0, is read as from 2018). -/
def isCedular (d : Disposal) : Bool :=
  ((d.kind == .home || d.kind == .realEstate || d.kind == .land) && (d.acquiredYear == 0 || decide (d.acquiredYear ≥ 2018)))
  || d.kind == .unlistedShares
def cedTax (d : Disposal) : Int := divR .down (1500 * pos d.gain) BP

def cedF : Family :=
  { name := "1100 impuesto cedular: inmuebles y acciones que no cotizan (LIG arts. 98 c), 99)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.disposals.zipIdx.filter fun (d, _) => isCedular d).map fun (d, i) =>
        charge .pit "Impuesto cedular sobre la ganancia (15 %)" d.gain (fun _ => pos d.gain) (fun b => divR .down (1500 * b) BP)
          (event := s!"disposal {i + 1}")
          (statute := if d.kind == .unlistedShares then "LIG (t.o. 2019) art. 98 c): QUINCE POR CIENTO (15 %)" else "LIG (t.o. 2019) art. 99: QUINCE POR CIENTO (15 %)") }

def families : List Family := [capF, cedF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := stackUnsupported g
  ++ when (g.entity != .company && g.disposals.any fun d => (d.kind == .home || d.kind == .realEstate || d.kind == .land) && d.acquiredYear != 0 && decide (d.acquiredYear < 2018)) "property acquired before 2018: impuesto a la transferencia de inmuebles (Ley 23.905, 1.5 % of the price) not modelled"
  ++ when (g.entity != .company && g.disposals.any isCedular) "impuesto cedular on the historical cost (IPIM indexation, art. 99 a), not applied: upper bound); losses not offset"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
#guard cedTax { kind := .realEstate, proceeds := 100000000, cost := 60000000, heldMonths := 36, acquiredYear := 2019 } == 6000000
#guard isCedular { kind := .realEstate, proceeds := 10, cost := 5, acquiredYear := 2010 } == false
#guard isCedular { kind := .unlistedShares, proceeds := 10, cost := 5 } == true

end ArGlobal.Capital
