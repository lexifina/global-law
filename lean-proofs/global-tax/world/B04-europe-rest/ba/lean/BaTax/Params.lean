import TaxKernel.World

/-!
# Bosnia and Herzegovina 2025, default entity: the Federation of BiH (whole KM)

Personal income tax in BiH is entity law. Default: **the Federation of Bosnia and Herzegovina** (FBiH). Republika
Srpska and the Brčko District are not modelled (`unsupported` when `"region"` names them).

Sources (Global law, corpus `bosnia-and-herzegovina/federation/acts`, as enacted, Službene novine FBiH; copies in
`../src/`):
* Zakon o porezu na dohodak, SN FBiH 10/08 (in force 2008-03-13), amended by 9/10, 44/11, 7/13, 65/13 (each read; none
  changes the rate or the amounts used here). The record holds no later amending law to 2026-11.
* Zakon o doprinosima, SN FBiH 35/98, rates as replaced by 14/08 (član 10); 33/25 (in force 1 July 2025) changes only
  the employer's rates (član 10 tačka 2). The 99/19 amendment cited by 33/25 is not in the record (FINDINGS F4).
-/

namespace BaTax
open TaxKernel

/-- Zakon o porezu na dohodak član 9: "Porez na dohodak plaća se po stopi od 10%." -/
def rate : Int := 1000
def schedule : Schedule := Schedule.flat rate

/-- Član 24 (1): "osnovni lični odbitak u visini od 3.600,00 KM za porezni period". -/
def basicDeduction : Int := 3600

/-- Član 24 (2) as factors of the basic deduction, in thousandths: spouse 0,5; first child 0,5; second 0,7; third and
each further 0,9. -/
def spouseFactor : Int := 500
def childFactors : List Int := [500, 700, 900]

/-- Zakon o doprinosima član 10 tačka 1 (as replaced by SN FBiH 14/08): "na teret obveznika doprinosa iz osnovice ...
17,00 % za penzijsko i invalidsko osiguranje, 12,50 % za osnovno zdravstveno osiguranje, 1,50 % za osiguranje od
nezaposlenosti". -/
def pio : Int := 1700
def health : Int := 1250
def unemployment : Int := 150

/-- Zakon o porezu na dohodak član 21 (2) 1): rent of immovable property, expenses "30% prihoda ostvarenog od
iznajmljivanja nepokretne imovine"; član 9: 10 %. -/
def rentCostRate : Int := 3000

end BaTax
