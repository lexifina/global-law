import EsGlobal.Pit

/-!
# ES 2025: transfer duties on purchases (4400); IBI (4100), Madrid

Source: RDLeg 1/1993 (TRLITPAJD), BOE consolidado (`es/law/itpajd.html`); sha256 in `law/SHA256SUMS`.
* art. 11.1 a): "Si la Comunidad Autónoma no hubiese aprobado el tipo a que se refiere el párrafo anterior, se aplicará el 6 por 100 a la transmisión de inmuebles"


## Impuesto sobre Bienes Inmuebles, Madrid 2025 (pass 3)
Sources (sha256 in `law/SHA256SUMS`):
* **TRLRHL** (RDLeg 2/2004, BOE consolidated text, `es/law/trlrhl.html`): art. 65 "La base imponible de este impuesto
  estará constituida por el valor catastral de los bienes inmuebles"; art. 71.1 "La cuota íntegra de este impuesto
  será el resultado de aplicar a la base liquidable el tipo de gravamen".
* **Ordenanza Fiscal reguladora del Impuesto sobre Bienes Inmuebles (Madrid), de 15 de diciembre de 1989**, as
  amended by the Pleno del Ayuntamiento de Madrid (BOCM núm. 308, 27 de diciembre de 2024, BOCM-20241227-61;
  `es/law/madrid_ibi_bocm20241227_61.pdf`): art. 8.2 "El tipo de gravamen aplicable a los bienes inmuebles de
  naturaleza urbana queda fijado en el 0,428 %, el de los bienes de naturaleza rústica en el 0,567 % y el de los
  bienes inmuebles de características especiales en el 1,141 %"; art. 3.2 "Estarán asimismo exentos, los inmuebles
  de naturaleza rústica o urbana cuya cuota líquida por este impuesto no supere los seis euros"; "La ordenanza
  entrará en vigor el 1 de enero de 2025" (the preamble: "de un tipo de gravamen del 0,442 % al 0,428 %").
Base: the asset's `assessed` value is the valor catastral; without it the market value stands in. All real estate
is urban (0,428 %). Not read: the differentiated rates for non-residential uses above a value threshold (art. 8.3,
which the preamble says exist), the base-liquidable reduction (TRLRHL arts. 66-70) and the bonificaciones: grade B.
-/

namespace EsGlobal.Property
open TaxKernel TaxKernel.Global

def d0 : TransferDuty :=
  { name := "Impuesto sobre Transmisiones Patrimoniales Onerosas (inmuebles)",   sched := Schedule.flat 600,   kinds := [.home, .realEstate, .land] }
/-- Ordenanza IBI Madrid art. 8.2 (BOCM 27.12.2024): tipo urbano 0,428 % (thousandths of a percent). -/
def tipoUrbanoMadrid2025 : Int := 428
/-- TRLRHL arts. 65, 71.1: cuota = valor catastral x tipo (euros, rounded down); art. 3.2: exempt if not above 6 euros. -/
def ibiMadrid (vc : Int) : Int :=
  let c := divR .down (pos vc * tipoUrbanoMadrid2025) 100000
  if c ≤ 6 then 0 else c
def ibiCharges (as : List Asset) : List Charge :=
  (as.zipIdx.filter fun (a, _) => a.kind.isRealEstate).map fun (a, i) =>
    charge .propertyRecurrent "Impuesto sobre Bienes Inmuebles (Madrid)" a.statutoryValue (fun v => v) (fun v => ibiMadrid v)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "TRLRHL arts. 65, 71; Ordenanza Fiscal IBI Madrid arts. 3.2, 8.2 (BOCM 27.12.2024: 0,428 %)")

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 transfer duties", covers := [.transactions],
     run := fun args g prev =>
       d0.charges g.purchases "TRLITPAJD art. 11.1 a) (6 %, tipo supletorio)" },
   { name := "4100 IBI (Madrid)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       ibiCharges g.assets }]

def absent : List Absent :=
  []

def notes : List String := ["ES 4400: BOE consolidado (current text with amendment notes)", "ES 4100: IBI Madrid 2025 tipo urbano 0,428 % (BOCM 27.12.2024, BOCM-20241227-61)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty then ["the Comunidad de Madrid's own rate (DLeg 1/2010, not reached) replaces the 6 % default; new dwellings sold by developers bear IVA + AJD instead (not separated)"] else [])
  ++ (if g.assets.any (fun a => a.kind.isRealEstate && a.assessed < 0) then ["4100 IBI: no valor catastral given: the market value stands in"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate || a.kind == .land) then ["4100 IBI: differentiated rates for non-residential uses (ordenanza art. 8.3, not read), recargo on empty dwellings (TRLRHL art. 72.4), bonificaciones and the base-liquidable reduction (arts. 66-70) not applied"] else [])

#guard d0.amount { kind := .home, price := 200000 } == 12000
#guard d0.amount { kind := .home, price := 2000000 } == 120000
-- valor catastral 200 000 x 0,428 % = 856
#guard ibiMadrid 200000 == 856
-- art. 3.2: a cuota of 6 euros or less is exempt (1 400 x 0,428 % = 5,99)
#guard ibiMadrid 1400 == 0
#guard ibiMadrid 1700 == 7

end EsGlobal.Property
