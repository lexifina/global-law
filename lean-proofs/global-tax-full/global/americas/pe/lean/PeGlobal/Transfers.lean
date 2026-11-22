import PeGlobal.Pit

/-!
# PE 2025: Transfers family: impuesto predial (4100) and alcabala (4400)

Source: TUO de la Ley de Tributación Municipal (D.S. 156-2004-EF; El Peruano text in lexifina/peru-law, arts. unchanged since 2022), national rates collected by the districts. **Art. 13**: "El impuesto se calcula aplicando a la base imponible la escala progresiva acumulativa siguiente: Hasta 15 UIT 0.2% Más de 15 UIT y hasta 60 UIT 0.6% Más de 60 UIT 1.0%"; art. 11: the base is the total value of the contributor's predios in each district. **Art. 25**: alcabala "La tasa del impuesto es de 3%, siendo de cargo exclusivo del comprador ... No está afecto ... el tramo comprendido por las primeras 10 UIT". UIT 2025 S/ 5,350 (D.S. 260-2024-EF). Model: each person's real estate summed (one district), at its statutory value; alcabala on each real-estate purchase price. Not applied (flagged): municipal minimum, art. 19 deduction, art. 13-A additional rate, art. 24 floor.
-/

namespace PeGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon PeGlobal

/-- D.S. 260-2024-EF art. 1: UIT 2025 = S/ 5,350. -/
def uit : Int := 5350

/-- TUO LTM art. 13: cumulative progressive scale on the value of a person's predios (marginal bands). -/
def predialSched : Schedule := Schedule.ofList [(0, 20), (15 * uit, 60), (60 * uit, 100)]
def predialTax (v : Int) : Int := predialSched.tax {} (pos v)

/-- art. 25: 3 % of the transfer value above 10 UIT, on the buyer. -/
def alcabala (price : Int) : Int := divR .down (300 * pos (price - 10 * uit)) BP

def predialF : Family :=
  { name := "4100 impuesto predial (TUO LTM)", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      let re := g.assets.filter (·.kind.isRealEstate)
      (re.map (·.person)).eraseDups.map fun p =>
        let v := isum ((re.filter (·.person == p)).map (fun a => pos a.statutoryValue))
        charge .propertyRecurrent "Impuesto predial" v (fun _ => v) (fun _ => predialTax v)
          (event := s!"person {p + 1}, 1 January 2025") (level := .local) (statute := "TUO de la Ley de Tributación Municipal (D.S. 156-2004-EF) art. 11 (base: total value of the contributor's predios in each district), art. 13 (escala progresiva acumulativa: to 15 UIT 0.2 %, 15-60 UIT 0.6 %, above 60 UIT 1.0 %); UIT 2025 S/ 5,350 (D.S. 260-2024-EF art. 1)") }

def alcabalaF : Family :=
  { name := "4400 impuesto de alcabala (TUO LTM)", covers := [.transactions],
    run := fun _ g _ =>
      (g.purchases.zipIdx.filter fun (p, _) => p.kind.isRealEstate).map fun (p, i) =>
        charge .transactions "Impuesto de alcabala" p.price (fun b => pos (b - 10 * uit)) alcabala
          (event := s!"purchase {i + 1}") (level := .local) (statute := "TUO LTM art. 21 (alcabala on transfers of real estate), art. 24 (base: transfer value, not below the autoavalúo), art. 25: 3 %, borne by the buyer, the first 10 UIT not taxed; UIT 2025 S/ 5,350") }

def families : List Family := [predialF, alcabalaF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity != .company && g.assets.any (·.kind.isRealEstate)) "impuesto predial on each person's real estate summed at its statutory value (the autoavalúo where `assessed` is given, else market value), all in one district; the municipal minimum (0.6 % UIT), the pensioner/older-person deduction of 50 UIT (art. 19), the art. 13-A additional rate on unbuilt urban land and co-ownership shares not applied"
  ++ when (g.entity == .company && g.assets.any (·.kind.isRealEstate)) "impuesto predial on company-owned real estate not computed (company assets not routed)"
  ++ when (g.purchases.any (·.kind.isRealEstate)) "alcabala on the price (art. 24 floor: the autoavalúo adjusted by the IPM not applied); first sale by a construction company (art. 22) not distinguished"

#guard predialTax 80250 == 160
#guard predialTax 321000 == 1605
#guard predialTax 1000000 == 8395
#guard alcabala 53500 == 0
#guard alcabala 553500 == 15000

end PeGlobal.Transfers
