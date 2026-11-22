import ChGlobal.Pit

/-!
# Switzerland 2025: direkte Bundessteuer on company profits (1200) and Verrechnungssteuer (1200, withholding)

Sources: fedlex consolidations in force on 1 July 2025: DBG SR 642.11 (2025-01-01, `ch/law/dbg_20250101.html`),
VStG SR 642.21 (2025-01-01, `ch/law/vstg_20250101.html`); sha256 in `law/SHA256SUMS`.
* **DBG Art. 68**: "Die Gewinnsteuer der Kapitalgesellschaften und Genossenschaften beträgt 8,5 Prozent des
  Reingewinns." **Art. 59 (1) lit. a**: "Zum geschäftsmässig begründeten Aufwand gehören auch: a. die eidgenössischen,
  kantonalen und kommunalen Steuern": the federal tax is deductible from its own base, so with the profit before tax P
  and no other tax, t = 8,5 % × (P − t), i.e. t = 8,5 / 108,5 × P (the cantonal and communal taxes, also deductible,
  are not modelled: StG ZH not read).
* **VStG Art. 13 (1) lit. a**: "Die Steuer beträgt: a. 35 Prozent auf Kapitalerträgen" (dividends and bond interest,
  Art. 4 (1) lit. a, b), withheld whoever the recipient is.

## Kanton and Stadt Zürich (pass 2)
Sources: Steuergesetz ZH (LS 631.1), zhlex Nachtrag 127 (pages "1. 1. 25 - 127", `ch/law/stgzh_127.pdf`); Steuerfüsse
2025 from the ESTV Steuerrechner (`TaxRates` of a TaxYear 2025 calculation for TaxLocationID 800100000, Zürich 8001:
"...RateCanton":98, "...RateCity":119; `ch/law/estv_taxrates_2025_zh8001.json`).
* **StG ZH § 71**: "Die Gewinnsteuer der Kapitalgesellschaften und Genossenschaften beträgt 7 Prozent des steuerbaren
  Gewinns" (einfache Steuer), times the Steuerfuss of the canton (98 %) and of the City of Zürich (119 %).
* **DBG Art. 59 (1) lit. a** and **StG ZH § 65 (1) lit. a**: the federal, cantonal and communal taxes are deductible:
  with 8,5 % + 7 % x 217 % = 23,69 % on the profit after taxes, that profit is P x 10 000 / 12 369 (the federal
  charge used P x 850 / 10 850 in pass 1, i.e. without the cantonal taxes).


## 1200 Verrechnungssteuer (royalties, services): royalty, services (pass 8, grade A)
Source: Bundesgesetz über die Verrechnungssteuer, fedlex Fassung vom 1. Januar 2025 (`ch/law/vstg_20250101.txt`).
* Art. 4 (1): the Verrechnungssteuer on income from movable capital falls on interest, annuities, profit shares and other income of bonds and similar debt, of shares, GmbH and cooperative shares, of collective investments and of customer deposits with Swiss banks; licence fees and service fees are not listed
-/

namespace ChGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- DBG Art. 68 with Art. 59 (1) lit. a: 8,5 % of the profit after the federal, cantonal and communal profit taxes
(8,5 % + 7 % x 217 % = 23,69 %: the profit after taxes is P x 10 000 / 12 369). -/
def bundessteuer (profitBeforeTax : Int) : Int := divR .down (850 * pos profitBeforeTax) 12369

def wht : Wht :=
  { name := "Verrechnungssteuer", rules := [
    { kind := .dividend, rateBp := 3500, statute := "VStG Art. 4 (1) lit. b, Art. 13 (1) lit. a: 35 %" },   { kind := .interest, rateBp := 3500, statute := "VStG Art. 4 (1) lit. a, Art. 13 (1) lit. a: 35 % (bond and bank interest)" }] }

/-- StG ZH § 71: einfache Gewinnsteuer 7 % of the profit after taxes (§ 65 (1) lit. a). -/
def einfacheGewinnsteuer (p : Int) : Int := divR .down (700 * pos p) 12369
/-- Steuerfuss 2025: Kanton 98 %, Stadt Zürich 119 % (ESTV TaxRates 2025). -/
def staatssteuer (p : Int) : Int := divR .down (98 * einfacheGewinnsteuer p) 100
def gemeindesteuer (p : Int) : Int := divR .down (119 * einfacheGewinnsteuer p) 100

/-- VStG Art. 4 (1) (objects of the Verrechnungssteuer) -/
def p8wht2 : Wht :=
  { name := "Verrechnungssteuer (royalties, services)", rules := [
    { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "VStG Art. 4 (1): the objects are income of bonds, shares and similar participations, collective investments and customer deposits: none on royalties" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "VStG Art. 4 (1): none on service fees (not an object of the tax)" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 direkte Bundessteuer, Verrechnungssteuer, Gewinnsteuer Kanton/Stadt Zürich", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [charge .cit "Direkte Bundessteuer (Gewinnsteuer)" g.company.profit id (fun p => bundessteuer p) (statute := "DBG Art. 68 (8,5 % des Reingewinns), Art. 59 (1) lit. a")] else [])
       ++ (if g.entity == .company then wht.charges g.company else [])
       ++ (if g.entity == .company then [charge .cit "Staatssteuer Zürich (Gewinnsteuer)" g.company.profit id (fun p => staatssteuer p) (level := .state) (statute := "StG ZH § 71 (7 %), § 65 (1) lit. a; Steuerfuss Kanton 98 % (2025)"), charge .cit "Gemeindesteuer Stadt Zürich (Gewinnsteuer)" g.company.profit id (fun p => gemeindesteuer p) (level := .local) (statute := "StG ZH § 71 (7 %), § 65 (1) lit. a; Steuerfuss Stadt Zürich 119 % (2025)")] else []) },
   { name := "1200 Verrechnungssteuer (royalties, services) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["CH 1200: Gewinnsteuer of Kanton (98 %) and Stadt Zürich (119 %), taxes deductible jointly", "CH 1200 withholding pass 8 (royalty, services): SR 642.21, Fassung 01.01.2025 (`ch/law/vstg_20250101.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["Kantons- und Gemeindesteuern on profit and capital (StG ZH) not modelled; the federal tax is computed as if it were the only deductible tax"] else [])
  ++ (if g.entity == .company && g.company.lossesForward > 0 then ["loss carry-forward (DBG Art. 67, seven years) not modelled"] else [])
  ++ (if g.entity == .company && g.company.dividendsReceived > 0 then ["Beteiligungsabzug (DBG Art. 69-70) not modelled"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => (p.kind == .royalty || p.kind == .services) && !p.toCompany) then ["1200 withholding: cantonal source taxes on certain income of non-resident individuals (DBG Art. 91-97: performers, board fees) not read"] else [])

#guard wht.amount { kind := .dividend, amount := 100000 } == 35000
#guard wht.amount { kind := .royalty, amount := 100000 } == 0
-- profit before taxes 1 236 900: after the taxes 1 000 000; 85 000 + 68 600 + 83 300 = 236 900
#guard bundessteuer 1236900 == 85000
#guard einfacheGewinnsteuer 1236900 == 70000
#guard staatssteuer 1236900 == 68600
#guard gemeindesteuer 1236900 == 83300
#guard bundessteuer 1236900 + staatssteuer 1236900 + gemeindesteuer 1236900 == 1236900 - 1000000
#guard p8wht2.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end ChGlobal.Corporate
