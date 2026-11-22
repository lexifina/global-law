import CuGlobal.Pit

/-!
# Cuba 2025: Impuesto sobre Transmisión de Bienes y Herencias (4400, 4300)

Source: Ley 113 as modified (Gaceta Oficial 4 de febrero de 2021; `world/B13-caribbean/cu/law/l113.txt`), applied in
2025 by Ley 174 art. 90 ("de conformidad con lo establecido en la Ley 113").
* **art. 205 a)**: transfers of real estate and registered movables "con el cuatro por ciento (4 %) sobre el valor
  del bien o derecho que se adquiera" (base: art. 201, the declared value or the official reference value).
* **art. 205 d)** and **Anexo No. 3**: inheritances and legacies, on each heir's share: spouses, ascendants and
  descendants exempt to $1.000, then 2 % … 25 % above $1.000.000; siblings 4 % … 35 %; uncles, aunts, nephews, nieces
  8 % … 50 %; others 14 % … 65 %. The Anexo lists brackets without saying whether the rate is marginal or applies to
  the whole share: marginal taken (flagged).
-/

namespace CuGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon CuGlobal

def transmision : TransferDuty :=
  { name := "Impuesto sobre Transmisión de Bienes (4 %)", sched := Schedule.flat 400,
    kinds := [.home, .realEstate, .land, .vehicle] }
def transF : Family := transferFamily "4400 transmisión de bienes" [(transmision, "Ley 113 art. 205 a) (4 %); Ley 174 art. 90", .central)]

def esc (rows : List (Int × Int)) : Schedule := Schedule.ofList rows
def classes : List TaxClass :=
  [{ allowance := 0, sched := esc [(0, 0), (1000, 200), (5000, 300), (15000, 500), (30000, 700), (50000, 1000), (100000, 1300), (250000, 1600), (500000, 1900), (750000, 2200), (1000000, 2500)] },
   { allowance := 0, sched := esc [(0, 400), (5000, 600), (15000, 800), (30000, 1000), (50000, 1400), (100000, 1800), (250000, 2200), (500000, 2600), (750000, 3000), (1000000, 3500)] },
   { allowance := 0, sched := esc [(0, 800), (5000, 1200), (15000, 1600), (30000, 2000), (50000, 2500), (100000, 3000), (250000, 3500), (500000, 4000), (750000, 4500), (1000000, 5000)] },
   { allowance := 0, sched := esc [(0, 1400), (5000, 1900), (15000, 2400), (30000, 2900), (50000, 3500), (100000, 4100), (250000, 4700), (500000, 5300), (750000, 6000), (1000000, 6500)] }]
def classOf (r : Relation) : Nat :=
  match r with
  | .spouse | .child | .grandchild | .parent => 0
  | .sibling => 1
  | .nieceNephew => 2
  | _ => 3
def herencias : InheritanceTax :=
  { name := "Impuesto sobre Herencias (Anexo 3)", classOf := classOf, classes := classes, exemptRelations := [.charity] }
def herF : Family :=
  { name := "4300 herencias", covers := [.estate],
    run := fun _ g _ => herencias.charges (g.transfers.filter (·.kind == .inheritance)) "Ley 113 art. 205 d), Anexo No. 3 (marginal reading)" }

def families : List Family := [transF, herF]

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 12): Constitución (2019) art. 108 m): \"establecer, modificar o extinguir los tributos\" (`cu/law/const_art-108.md`). no law read in this build levies a recurrent tax on net wealth (laws read include: Ley 113 arts. 132-150; Ley 174 (2025) art. 69; Ley 113/2012 arts. 73 párr. 2, 98, 99: personas jurídicas extranjeras sin establecimiento permanente 4 % of gross income, retenido por el pagador; 1.x model (see its summary.json); Ley 174 art. 19; Ley 174 art. 91)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.transfers.any (·.kind == .gift)) "gifts: taxed under art. 205 a) (4 %) when they transfer registered property; not computed from the transfer records"
  ++ when (!g.transfers.isEmpty) "Anexo No. 3 read as marginal brackets (the Anexo does not say); art. 208 20 % relief for dependent heirs not modelled"
  ++ when (g.purchases.any (·.kind == .vehicle)) "art. 206: +100 % of the rate per vehicle already owned not modelled"

#guard transmision.amount { kind := .home, price := 1000000 } == 40000
#guard herencias.tax { kind := .inheritance, value := 1000, relation := .child } == 0
#guard herencias.tax { kind := .inheritance, value := 5000, relation := .child } == 80
#guard herencias.tax { kind := .inheritance, value := 5000, relation := .unrelated } == 700

end CuGlobal.Transfers
