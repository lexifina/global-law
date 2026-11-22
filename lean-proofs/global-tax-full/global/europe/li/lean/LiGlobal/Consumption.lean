import LiGlobal.Pit

/-!
# LI 2025: Mehrwertsteuer (5111); excises not modelled in this pass

Source: MWSTG, gesetze.li (Lilex, Rechtsdienst der Regierung, official) consolidated PDF "Fassung: 01.01.2025" (`gesetze.li/konso/pdf/2009330000?version=22`, valid 01.01.2025-31.12.2025; `li/law/mwstg_fassung20250101.pdf`); sha256 in `law/SHA256SUMS`.
* Art. 25: "1) Die Steuer beträgt 8,1 % (Normalsatz) ... 2) Der reduzierte Steuersatz von 2,6 % findet Anwendung: a) auf der Lieferung folgender Gegenstände: 1. Wasser in Leitungen, 2. Lebensmittel ... mit Ausnahme alkoholischer Getränke, ... 8. Medikamente, 9. Zeitungen, Zeitschriften, Bücher ... 3) Für Lebensmittel, die im Rahmen von gastgewerblichen Leistungen abgegeben werden, gilt der Normalsatz. ... 4) Die Steuer auf Beherbergungsleistungen beträgt 3,8 % (Sondersatz)."
* Art. 10 Abs. 2: "Von der Steuerpflicht ist befreit, wer: a) innerhalb eines Jahres im In- und Ausland weniger als 100 000 Franken Umsatz aus Leistungen erzielt, die nicht nach Art. 21 Abs. 2 von der Steuer ausgenommen sind"
-/

namespace LiGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Mehrwertsteuer", standard := 810, reduced := 260, reduced2 := 380, threshold := 100000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .nonAlcoholic | .water | .medicines | .books | .newspapers => .reduced
      | .hotels => .reduced2
      | _ => .standard }

def vatStatute : String := "Mehrwertsteuergesetz (MWSTG, LGBl. 2009 Nr. 330) Art. 25 Abs. 1 (8,1 %), Abs. 2 (2,6 %), Abs. 3 (gastgewerbliche Leistungen Normalsatz), Abs. 4 (3,8 %); Art. 10 Abs. 2 Bst. a (100 000 Franken); Art. 21 (ausgenommene Leistungen)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Mehrwertsteuer", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["LI 5111: Lilex Fassung 01.01.2025 (valid to 31.12.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Mineralölsteuer, Tabaksteuer, Biersteuer under the customs treaty with Switzerland (Swiss acts; not read)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 10810 } == 810
#guard vat.embedded { good := .food, amount := 10260 } == 260
#guard vat.embedded { good := .hotels, amount := 10380 } == 380
#guard vat.net { turnover := 100000, sales := [{ good := .other, net := 100000 }] } == 0

end LiGlobal.Consumption
