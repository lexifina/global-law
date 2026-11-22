import PtGlobal.Pit

/-!
# PT 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (CIMT art. 17 (IMT tables) and Imposto do Selo verba 1.1 (0,8 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (CIMI art. 112 (IMI, Lisboa)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4100 Recurrent property tax (pass 6 note, grade C)**: CIMI art. 112 (IMI, Lisboa): IMI: municipal rates on the valor patrimonial tributário (0,3-0,45 % for urban property, CIMI art. 112); Lisboa's deliberação not read (pass 6 note (PwC WWTS 2025 captures on disk))


## 4400 IMT (pass 6)
Source: Código do IMT art. 17.º, Portal das Finanças (`pt/law/cimt17_portal.txt`); Lei n.º 45-A/2024 (OE 2025) art. 100.º (`pt/law/Lei_45_A_2024.txt`).
* art. 17.º n.º 1 a) (HPP): marginal 0 / 2 / 5 / 7 / 8 %, then "6 (taxa única)" and "7,5 (taxa única)"; 2025 limits (Lei 45-A/2024 art. 100.º): "Até 104 261", 142 618, 194 458, 324 058, 648 022, "Superior a 1 128 287"
* c) other dwellings: from 1 % marginal, limits as a) to 324 058, then 621 501; d) "Aquisição de prédios rústicos - 5%"; e) "Aquisição de outros prédios urbanos e outras aquisições onerosas - 6,5%"


## 4100 Imposto municipal sobre imóveis (prédios urbanos, Lisboa) (pass 6)
Source: CIMI art. 112.º, Portal das Finanças (`pt/law/cimi112_portal.html`); the Lisbon rate from a news report of the Câmara's 2025 budget (the Assembleia Municipal deliberation was not read).
* art. 112.º n.º 1 c): prédios urbanos, de 0,3 % a 0,45 %; a): prédios rústicos 0,8 %
* art. 112.º n.º 5: the municipal assembly fixes each year's rate within the c) interval, possibly by parish
* Lisboa: 0,3 % (the statutory minimum) for the tax of 2025, with the +30 % for degraded and -30 % for listed buildings (n.º 6-8) not modelled
* Not modelled: the tripled rate for vacant buildings (n.º 3), 7,5 % for owners in listed low-tax jurisdictions (n.º 4), the IMI familiar deduction (art. 112.º-A), the temporary own-home exemption (EBF art. 46.º), the AIMI (art. 135.º-A ff.) and rústicos


## 4100 Adicional ao IMI (AIMI) (pass 6)
Source: Código do IMI, Portal das Finanças (`pt/law/cimi135a_portal.html`, `cimi135b_portal.html`, `cimi135c_portal.html`, `cimi135f_portal.html`, `cimi135i_portal.html`).
* art. 135.º-A: individuals and companies owning, holding in usufruct or surface right urban buildings in Portugal, status fixed at 1 January
* art. 135.º-B: the base is the sum of the VPT of the owner's urban buildings; commercial, industrial, service and 'outros' buildings excluded (n.º 2, Lei 56/2023)
* art. 135.º-C n.º 2 a): EUR 600 000 deducted for an individual; art. 135.º-D: married couples and unions may opt for joint taxation, the deduction summed
* art. 135.º-F: 0,7 % for individuals on the value after the deduction; marginal 1 % on the part of the value (before the deduction) above EUR 1 000 000 up to 2 000 000 and 1,5 % above 2 000 000; the limits doubled on the joint option; companies 0,4 %
* art. 135.º-I: deductible from the IRS on rental income from the buildings (not modelled: the 1.x PIT is not reduced)
* Hand check: one person, a home with VPT 1 500 000: 0,7 % x 400 000 + 1 % x 500 000 = 2 800 + 5 000 = 7 800; married, the same home in halves: 2 x 0,7 % x 150 000 = 2 100
-/

namespace PtGlobal.Property
open TaxKernel TaxKernel.Global

/-- CIMT art. 17.º n.º 1 a), c), d), e) (rates: redação Lei 82/2023 and DL 48-A/2024) with the 2025 limits of Lei 45-A/2024 art. 100.º (HPP 0/2/5/7/8 % marginal to EUR 648 022, then 6 % / 7,5 % on the whole value; other dwellings from 1 %; rústicos 5 %; other urban 6,5 %) -/
def p7imtWhole (top : Int) (b : List (Int × Int)) (v : Int) : Int :=
  if v ≤ top then (Schedule.ofList b).tax {} v else if v ≤ 1128287 then divR .down (600 * v) 10000 else divR .down (750 * v) 10000
def p7imt (p : Purchase) : Int :=
  match p.kind with
  | .home => if p.additionalHome then p7imtWhole 621501 [(0, 100), (104261, 200), (142618, 500), (194458, 700), (324058, 800)] p.price
             else p7imtWhole 648022 [(0, 0), (104261, 200), (142618, 500), (194458, 700), (324058, 800)] p.price
  | .realEstate => divR .down (650 * pos p.price) 10000
  | .land => divR .down (500 * pos p.price) 10000
  | _ => 0
def p7imtCharges (ps : List Purchase) : List Charge :=
  (ps.zipIdx.filter fun (p, _) => [AssetKind.home, .realEstate, .land].contains p.kind).map fun (p, i) =>
    charge .transactions "Imposto municipal sobre as transmissões onerosas de imóveis (IMT)" p.price (fun v => v) (fun _ => p7imt p) (event := s!"purchase {i + 1}") (statute := "CIMT art. 17.º n.º 1 a), c), d), e) (rates: redação Lei 82/2023 and DL 48-A/2024) with the 2025 limits of Lei 45-A/2024 art. 100.º (HPP 0/2/5/7/8 % marginal to EUR 648 022, then 6 % / 7,5 % on the whole value; other dwellings from 1 %; rústicos 5 %; other urban 6,5 %)")

/-- Código do IMI art. 112.º n.º 1 c), n.º 5 (redação da Lei n.º 7-A/2016); Município de Lisboa: 0,3 % for 2025 -/
def p6ptImi : PropertyTax := { name := "Imposto municipal sobre imóveis (prédios urbanos, Lisboa)", sched := Schedule.flat 30, kinds := [.home, .realEstate] }

/-- Código do IMI art. 135.º-B, 135.º-C n.º 2 a), 135.º-D, 135.º-F n.º 1-3 (adicional ao IMI; redação da Lei n.º 71/2018 e da Lei n.º 56/2023) -/
def p13ptAimi : WealthTax :=
  { name := "Adicional ao imposto municipal sobre imóveis (AIMI)", sched := Schedule.ofList [(0, 0), (600000, 70), (1000000, 100), (2000000, 150)],   deductDebts := false, exemptKinds := [.land, .listedShares, .unlistedShares, .bonds, .deposits, .business, .pensionFund, .vehicle, .other] }
/-- a married couple: each spouse on half (art. 135.º-D: the joint option doubles the deduction and the band limits, the same result) -/
def p13ptAimiTax (married : Bool) (as : List Asset) : Int :=
  if married then 2 * ({ p13ptAimi with valuation := fun _ => 5000 }).gross as else p13ptAimi.gross as
def p13ptAimiCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company || g.assets.isEmpty then [] else
  [charge .propertyRecurrent p13ptAimi.name (p13ptAimi.netWealth g.assets) (fun _ => p13ptAimi.base g.assets)
     (fun _ => p13ptAimiTax g.household.married g.assets) (event := "2025") (level := .central) (statute := "Código do IMI art. 135.º-B, 135.º-C n.º 2 a), 135.º-D, 135.º-F n.º 1-3 (adicional ao IMI; redação da Lei n.º 71/2018 e da Lei n.º 56/2023)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Imposto municipal sobre as transmissões onerosas de imóveis (IMT)", covers := [.transactions],
     run := fun args g prev =>
       p7imtCharges g.purchases },
   { name := "4100 Imposto municipal sobre imóveis (prédios urbanos, Lisboa)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       p6ptImi.charges g.assets "Código do IMI art. 112.º n.º 1 c), n.º 5 (redação da Lei n.º 7-A/2016); Município de Lisboa: 0,3 % for 2025" (level := .local) },
   { name := "4100 Adicional ao IMI (AIMI)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       p13ptAimiCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["PT 4400: CIMT art. 17.º (Portal das Finanças) + Lei 45-A/2024 art. 100.º limits for 2025 (A)", "PT 4100 Imposto municipal sobre imóveis (prédios urbanos, Lisboa): Portal das Finanças, códigos tributários, CIMI art. 112.º (fetched 2026-11-21, `pt/law/cimi112_portal.txt`); Lisbon's rate from the 2025 municipal budget as reported (rr.pt, 29.11.2024: the urban rate stays at 0,3 %) (grade B)", "PT 4100 AIMI: Portal das Finanças CIMI art. 135.º-A to 135.º-I (fetched 2026-11-21); last amended by Lei 56/2023 (art. 135.º-B) and Lei 71/2018 (art. 135.º-F), so the wording read is the 2025 wording (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.purchases.any (·.kind == .home) then ["4400 IMT: a home is taken as habitação própria e permanente unless additionalHome; IMT Jovem (art. 9.º n.º 2-5, buyers up to 35: table b)) and the 10 % rate for buyers in listed tax havens are not applied; base = the higher of price and VPT (art. 12.º: the price stands in)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400: imposto do selo verba 1.1 (0,8 % on acquisitions of real estate) not read: not modelled"] else [])
  ++ (if g.assets.any (fun a => a.kind == .home || a.kind == .realEstate) then ["4100 IMI: the asset's value is taken as the valor patrimonial tributário; the own-home exemption (EBF art. 46.º), the art. 112.º-A family deduction and the AIMI are not applied"] else [])
  ++ (if g.assets.any (fun a => a.kind == .land) then ["4100 IMI on land: rústico (0,8 %) or terreno para construção (urban, 0,3 %) cannot be told apart from the input (grade C)"] else [])
  ++ (if g.entity == .company then ["4100 AIMI on companies (0,4 % without the deduction, art. 135.º-F n.º 1) not modelled: a company's urban property is not in the input as dwellings"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate) then ["4100 AIMI: real estate other than the home is taken as residential (habitacional); commercial, industrial and service buildings are excluded by art. 135.º-B n.º 2 and cannot be told apart in the input"] else [])
  ++ (if g.assets.any (fun a => a.kind == .land) then ["4100 AIMI: land is left out (a terreno para construção is in the base, a rústico is not; the input does not say which)"] else [])
  ++ (if g.household.married && g.assets.any (fun a => a.kind == .home || a.kind == .realEstate) then ["4100 AIMI: a married couple's dwellings are taken as owned in equal halves"] else [])

#guard p7imt { kind := .home, price := 100000 } == 0
#guard p7imt { kind := .home, price := 300000 } == 10747
#guard p7imt { kind := .home, price := 648022 } == 38348
#guard p7imt { kind := .home, price := 700000 } == 42000
#guard p7imt { kind := .home, price := 2000000 } == 150000
#guard p7imt { kind := .home, price := 100000, additionalHome := true } == 1000
#guard p7imt { kind := .home, price := 300000, additionalHome := true } == 11789
#guard p7imt { kind := .home, price := 700000, additionalHome := true } == 42000
#guard p7imt { kind := .realEstate, price := 1000000 } == 65000
#guard p7imt { kind := .land, price := 1000000 } == 50000
#guard p7imt { kind := .vehicle, price := 1000000 } == 0
#guard p6ptImi.amount { kind := .home, value := 300000 } == 900
#guard p6ptImi.amount { kind := .home, value := 3000000 } == 9000
#guard p6ptImi.amount { kind := .realEstate, value := 300000 } == 900
#guard p6ptImi.amount { kind := .realEstate, value := 3000000 } == 9000
#guard p6ptImi.amount { kind := .deposits, value := 100000 } == 0
#guard p13ptAimiTax false [{ kind := .home, value := 600000 }] == 0
#guard p13ptAimiTax false [{ kind := .home, value := 1500000 }] == 7800
#guard p13ptAimiTax false [{ kind := .home, value := 3000000 }, { kind := .deposits, value := 5000000 }] == 27800
#guard p13ptAimiTax true [{ kind := .home, value := 1500000 }] == 2100
#guard p13ptAimiTax false [{ kind := .home, value := 2000000, debt := 1500000 }] == 12800
#guard p13ptAimiTax false [{ kind := .land, value := 2000000 }] == 0

end PtGlobal.Property
