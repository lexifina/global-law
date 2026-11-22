import ItGlobal.Pit

/-!
# IT 2025: IMU (4100), Roma

* 4400 Real-estate transfer and stamp duties (DPR 131/1986 Tariffa art. 1 (registro 9 %, 2 % prima casa)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)

## IMU, Roma 2025 (pass 3)
Sources (sha256 in `law/SHA256SUMS`, provenance in `law/ARCHIVE_INDEX.tsv`):
* **L. 27 dicembre 2019 n. 160, art. 1** (normattiva, vigente al 2025-07-01, commi 701-800:
  `it/law/l160_2019_art1_c701-800_vig20250701.html`): c. 740 "Il possesso dell'abitazione principale o assimilata
  ... non costituisce presupposto dell'imposta, salvo che si tratti di un'unità abitativa classificata nelle
  categorie catastali A/1, A/8 o A/9"; c. 745 base = "rendite risultanti in catasto, vigenti al 1° gennaio dell'anno
  di imposizione, rivalutate del 5 per cento ... i seguenti moltiplicatori: a) 160 per i fabbricati classificati nel
  gruppo catastale A e nelle categorie catastali C/2, C/6 e C/7, con esclusione della categoria catastale A/10 ...
  e) 65 per i fabbricati classificati nel gruppo catastale D"; c. 746 aree fabbricabili at the "valore venale in
  comune commercio"; c. 754 "aliquota di base è pari allo 0,86 per cento e i comuni ... possono aumentarla sino
  all'1,06 per cento"; c. 755 a further "0,08 per cento" where the commune kept the TASI maggiorazione.
* **Roma Capitale, Deliberazione dell'Assemblea Capitolina n. 182 del 19-12-2024**, Prospetto aliquote IMU 2025
  (MEF Dipartimento delle Finanze, Regolamenti e aliquote, anno 2025, cc H501, published 24-01-2025:
  `it/law/roma_imu_2025_delibera182.pdf`): "Abitazione principale di categoria catastale A/1, A/8 e A/9 e relative
  pertinenze 0,6%"; "Fabbricati appartenenti al gruppo catastale D (esclusa la categoria catastale D/10) 1,06%";
  "Aree fabbricabili 1,14%"; "Altri fabbricati (fabbricati diversi dall'abitazione principale e dai fabbricati
  appartenenti al gruppo catastale D) 1,14%"; "Terreni agricoli 1,06%".
Base: `home` is the abitazione principale (c. 740: not taxed; A/1, A/8, A/9 flagged); `realEstate` an "altro
fabbricato" of gruppo A (moltiplicatore 160, 1,14 %) on its rendita catastale (`annualValue`), or, without it, on
its `assessed` IMU value, else its market value; `land` an area fabbricabile at its market value (c. 746), 1,14 %.
Tax rounded down to whole euros.


## 4400 Imposta di registro (trasferimenti immobiliari) (pass 6)
Source: DPR 131/1986 (TU imposta di registro), Tariffa parte I art. 1, normattiva vigente al 2025-07-01 (`it/law/tur131_vig20250701_art1_1.txt`).
* Tariffa I art. 1: "Atti traslativi a titolo oneroso della proprietà di beni immobili in genere ... 9 per cento"; "Se il trasferimento ha per oggetto case di abitazione, ad eccezione di quelle di categoria catastale A1, A8 e A9, ove ricorrano le condizioni di cui alla nota II-bis) 2 per cento"; terreni agricoli to non-farmers "15 per cento"
* nota II-bis: the 2 % needs residence in the comune and no other home there or bought with the relief (the input's firstHome flag stands for these conditions)
-/

namespace ItGlobal.Property
open TaxKernel TaxKernel.Global

/-- Delibera AC 182/2024 (prospetto 2025): altri fabbricati and aree fabbricabili 1,14 % (bp). -/
def aliquotaAltriRoma : Int := 114
/-- L. 160/2019 art. 1 c. 745: rendita rivalutata del 5 % x 160 (gruppo A); in euros, rounded down. -/
def valoreImu (rendita : Int) : Int := divR .down (pos rendita * 105 * 160) 100
/-- The IMU value of a building: from the rendita where given, else the assessed value, else market value. -/
def baseImu (a : Asset) : Int :=
  if a.kind == .land then pos a.value
  else if 0 ≤ a.annualValue then valoreImu a.annualValue else a.statutoryValue
def imuRoma (base : Int) : Int := divR .down (pos base * aliquotaAltriRoma) 10000
def imuCharges (as : List Asset) : List Charge :=
  (as.zipIdx.filter fun (a, _) => a.kind == .realEstate || a.kind == .land).map fun (a, i) =>
    charge .propertyRecurrent "IMU (Roma)" (baseImu a) (fun v => v) (fun v => imuRoma v)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "L. 160/2019 art. 1 c. 740, 745, 746, 754, 755; Delibera Assemblea Capitolina n. 182/2024 (1,14 %)")

/-- DPR 131/1986 Tariffa parte I art. 1 (9 %; 2 % prima casa, nota II-bis) -/
def p6reg : TransferDuty := { name := "Imposta di registro (trasferimenti immobiliari)", sched := Schedule.flat 900, kinds := [.home, .realEstate, .land], firstHomeCap := 1000000000000, firstHomeSched := Schedule.flat 200 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4100 IMU (Roma)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       imuCharges g.assets },
   { name := "4400 Imposta di registro (trasferimenti immobiliari)", covers := [.transactions],
     run := fun args g prev =>
       p6reg.charges g.purchases "DPR 131/1986 Tariffa parte I art. 1 (9 %; 2 % prima casa, nota II-bis)" }]

def absent : List Absent :=
  []

def notes : List String := ["IT 4100: IMU L. 160/2019 vigente 2025-07-01; Roma prospetto aliquote 2025 (Delibera AC 182/2024)", "IT 4400 Imposta di registro (trasferimenti immobiliari): normattiva vigente al 2025-07-01 (Tariffa parte I art. 1, `it/law/tur131_vig20250701_art1_1.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .home) then ["4100 IMU: the abitazione principale is taken as not A/1, A/8, A/9 (c. 740, no tax); luxury categories (0,6 %, EUR 200 detrazione c. 749) need the category"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate && a.annualValue < 0) then ["4100 IMU: no rendita catastale (annualValue) given: the assessed or market value stands in for the c. 745 value"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate) then ["4100 IMU: realEstate taken as gruppo A (160, 1,14 %); gruppo D (65, 1,06 %), A/10, C/1 and the reduced Roma rates (canone concordato, comodato) not applied"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 base: the price (the prezzo-valore rule on cadastral value for homes, L. 266/2005 c. 497, not applied); minimum EUR 1 000 (D.Lgs. 23/2011 art. 10, not read); imposte ipotecaria/catastale EUR 50 + 50; agricultural land 15 %; sales by builders under IVA (registro EUR 200) not separated"] else [])

-- rendita 1 000: 1 000 x 1,05 x 160 = 168 000; x 1,14 % = 1 915,20
#guard valoreImu 1000 == 168000
#guard imuRoma (valoreImu 1000) == 1915
-- area fabbricabile 100 000 (valore venale): 1 140
#guard imuRoma 100000 == 1140
#guard imuRoma 0 == 0
#guard p6reg.amount { kind := .home, price := 200000 } == 18000
#guard p6reg.amount { kind := .home, price := 2000000 } == 180000
#guard p6reg.amount { kind := .home, price := 1000000000000, firstHome := true } == 20000000000
#guard p6reg.amount { kind := .home, price := 1000000000001, firstHome := true } == 90000000000
#guard p6reg.amount { kind := .vehicle, price := 100000 } == 0

end ItGlobal.Property
