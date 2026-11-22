import SeGlobal.Pit

/-!
# SE 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Lag (1984:404) om stämpelskatt (1,5 % / 4,25 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Lag (2007:1398) om kommunal fastighetsavgift): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Stämpelskatt (lagfart) (pass 6)
Source: Lag (1984:404), data.riksdagen.se `sfs-1984-404.text` (`se/law/sfs-1984-404.txt`, ändrad t.o.m. SFS 2025:391).
* 8 §: "Stämpelskatten är femton kronor för varje fullt tusental kronor av egendomens värde. Förvärvas egendomen av en juridisk person är dock skatten fyrtiotvå kronor och femtio öre för varje fullt tusental kronor"


## 4100 Kommunal fastighetsavgift (pass 6)
Source: Lag (2007:1398) om kommunal fastighetsavgift, data.riksdagen.se (`se/law/sfs-2007-1398.txt`); Förordning (2007:1023) and (2024:987) om inkomstbasbelopp (`se/law/sfs-2007-1023.txt`, `sfs-2024-987.txt`).
* 3 § a): "6 000 kronor per sådant småhus, dock högst 0,75 procent av byggnadsvärdet och markvärdet"; "För år 2009 och senare kalenderår uppgår fastighetsavgiften per småhus ... till fastighetsavgiften för år 2008 ökad eller minskad med ett belopp motsvarande inkomstbasbeloppets förändring mellan år 2008 och det aktuella kalenderåret uttryckt i procent med två decimaler. Avgiften uttrycks i hela krontal så att öretal faller bort."
* SFS 2007:1023: inkomstbasbeloppet "48 000 kronor för år 2008"; SFS 2024:987 1 §: "80 600 kronor för år 2025"
-/

namespace SeGlobal.Property
open TaxKernel TaxKernel.Global

/-- Lag (1984:404) om stämpelskatt vid inskrivningsmyndigheter 8 § (15 kr per full 1 000 kr; legal persons 42,50 kr) -/
def p6stamp : TransferDuty := { name := "Stämpelskatt (lagfart)", sched := Schedule.flat 150, kinds := [.home, .realEstate, .land] }

/-- Lag (2007:1398) om kommunal fastighetsavgift 3 § a) (6 000 kr per småhus for 2008, indexed by the inkomstbasbelopp; at most 0,75 % of the taxeringsvärde); IBB 2008 48 000 kr (SFS 2007:1023), 2025 80 600 kr (SFS 2024:987): +67,92 %. -/
def p6fastCap : Int := 6000 + divR .down (6000 * 6792) 10000
def p6fastighetsavgift (a : Asset) : Int :=
  if a.kind == .home then min p6fastCap (divR .down (75 * pos a.statutoryValue) 10000) else 0
def p6fastCharges (as : List Asset) : List Charge :=
  (as.zipIdx.filter fun (a, _) => a.kind == .home).map fun (a, i) =>
    charge .propertyRecurrent "Kommunal fastighetsavgift (småhus)" a.statutoryValue (fun v => v) (fun _ => p6fastighetsavgift a)
      (event := s!"asset {i + 1}") (level := .local) (statute := "Lag (2007:1398) om kommunal fastighetsavgift 3 § a) (6 000 kr per småhus for 2008, indexed by the inkomstbasbelopp; at most 0,75 % of the taxeringsvärde)")

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Stämpelskatt (lagfart)", covers := [.transactions],
     run := fun args g prev =>
       p6stamp.charges g.purchases "Lag (1984:404) om stämpelskatt vid inskrivningsmyndigheter 8 § (15 kr per full 1 000 kr; legal persons 42,50 kr)" },
   { name := "4100 Kommunal fastighetsavgift", covers := [.propertyRecurrent],
     run := fun args g prev =>
       p6fastCharges g.assets }]

def absent : List Absent :=
  []

def notes : List String := ["SE 4400 Stämpelskatt (lagfart): data.riksdagen.se (ändrad t.o.m. SFS 2025:391) (grade A)", "SE 4100: Lag (2007:1398) 3 § with IBB 2008/2025 (A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty then ["4400 the value is not rounded down to full thousands (at most 15 kr); a company buyer pays 4,25 % (not separated); the value may be the taxeringsvärde where higher (not read); pantbrev 2 % not modelled"] else [])
  ++ (if g.assets.any (fun a => a.kind == .home && a.assessed < 0) then ["4100 fastighetsavgift: no taxeringsvärde given: the market value stands in (the taxeringsvärde is about 75 % of it)"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate) then ["4100 fastighetsavgift: hyreshus (1 027 kr per lägenhet indexed, at most 0,3 %) and the statlig fastighetsskatt on commercial property not modelled"] else [])

#guard p6stamp.amount { kind := .home, price := 200000 } == 3000
#guard p6stamp.amount { kind := .home, price := 2000000 } == 30000
#guard p6stamp.amount { kind := .vehicle, price := 100000 } == 0
-- 6 000 x (1 + (80 600 - 48 000) / 48 000 = 67,92 %) = 10 075,20 -> 10 075 kr (öretal faller bort)
#guard p6fastCap == 10075
#guard p6fastighetsavgift { kind := .home, value := 1000000 } == 7500
#guard p6fastighetsavgift { kind := .home, value := 3000000, assessed := 1343333 } == 10074
#guard p6fastighetsavgift { kind := .home, value := 5000000 } == 10075
#guard p6fastighetsavgift { kind := .realEstate, value := 5000000 } == 0

end SeGlobal.Property
