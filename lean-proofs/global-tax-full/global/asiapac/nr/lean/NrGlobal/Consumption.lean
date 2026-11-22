import NrGlobal.Pit
import TaxKernel.Global2

/-!
# Nauru 2025: import excise (5121); no VAT or GST

Source: Customs Tariff Act 2014 Schedule 1 (Harmonized System Nomenclature of Nauru), RONLAW's current official reprint of
14 June 2024 (Sch 1 substituted by Act 3 of 2023 from 7 June 2023, amended by SL 1, 9 and 19 of 2024, the last from 14 June
2024), read in lexifina/nauru-law `acts/customs-tariff-act-2014/schedule/1.md` (retrieved October 2026: no later reprint,
so the 2025 text). Each tariff item has an import duty rate and an import excise rate; for the goods below the import
duty is 0 % and the import excise is:
* 2402.20.00 cigarettes containing tobacco: $0.45 per stick;
* 2203.00.10-.30 beer: $4.80 a litre (3.5 % vol or less), $5.20 (over 3.5 % to 4.9 %), $5.90 (over 4.9 %);
* 2204.21.10-.30 wine in containers of 2 litres or less: $9.00 a litre (10 % or less), $9.50 (over 10 % to 13.5 %), $10.50
  (over 13.5 %) (sparkling wine 2204.10.00: $10.00);
* 2710.12.10 motor spirit and 2710.12.30 automotive diesel: $0.60 a litre.
Spirits (2208) are listed: the rate depends on the kind of spirit (whisky, rum, gin, brandy $13.40, vodka $26.70, liqueurs and
others $14.00 a litre between 14 % and 48 %), which the basket does not give. Sugar and confectionery (50 %) and
sweetened drinks ($0.60 a litre or 60 %) are inside mixed basket classes: not booked. Nauru produces almost none of these
goods: every line is taken as imported.

**Customs import duty (5123, kernel 2.8.0 `TariffRule`)**: the same Schedule's import duty column, for the headings read
(each checked uniform over its national lines): 0901 coffee 10 %; 1701 sugar 0 %; 2203 beer, 2204 wine, 2208 spirits,
2402 cigars and cigarettes 0 %; 2710.12.10 motor spirit, 2710.12.20 leaded, 2710.12.30 automotive diesel 0 % (the other
2710.12 lines are 10 %: a 6-digit 2710.12 code is grade C); 6109 T-shirts, 6203 men's suits and trousers, 8471 computers,
8517 telephones 10 %. No general rate for other goods (grade C); no preference declared (none read). Only lines given as
imported (`"imported"`, a foreign `"origin"`) pay; the customs value is the price before tax (Nauru has no VAT).
-/

namespace NrGlobal.Consumption
open TaxKernel TaxKernel.Global

def st (i : String) : String := "Customs Tariff Act 2014 Schedule 1 (reprint 14 June 2024) tariff item " ++ i ++ ", import excise"

/-- The import excise on one basket line ($); `none` when not booked. -/
def exciseOn (s : Spend) : Option (Int × String) :=
  match s.good with
  | .cigarettes => if s.quantity ≤ 0 then none else some (divR .down (s.quantity * 45) 100000, st "2402.20.00 ($0.45 per stick)")
  | .beer => if s.quantity ≤ 0 || s.abvBp ≤ 0 then none
      else if s.abvBp ≤ 350 then some (divR .down (s.quantity * 480) 100000, st "2203.00.10 ($4.80 a litre)")
      else if s.abvBp ≤ 490 then some (divR .down (s.quantity * 520) 100000, st "2203.00.20 ($5.20 a litre)")
      else some (divR .down (s.quantity * 590) 100000, st "2203.00.30 ($5.90 a litre)")
  | .wine => if s.quantity ≤ 0 || s.abvBp ≤ 0 then none
      else if s.abvBp ≤ 1000 then some (divR .down (s.quantity * 900) 100000, st "2204.21.10 ($9.00 a litre)")
      else if s.abvBp ≤ 1350 then some (divR .down (s.quantity * 950) 100000, st "2204.21.20 ($9.50 a litre)")
      else some (divR .down (s.quantity * 1050) 100000, st "2204.21.30 ($10.50 a litre)")
  | .petrol => if s.quantity ≤ 0 then none else some (divR .down (s.quantity * 60) 100000, st "2710.12.10 ($0.60 a litre)")
  | .diesel => if s.quantity ≤ 0 then none else some (divR .down (s.quantity * 60) 100000, st "2710.12.30 ($0.60 a litre)")
  | _ => none

def exciseCharges (xs : List Spend) : List Charge :=
  (xs.zipIdx.filterMap fun (s, k) => (exciseOn s).map fun (d, stt) => (s, k, d, stt)).map fun (s, k, d, stt) =>
    charge .excise "Import excise" s.amount id (fun _ => d) (event := s!"line {k + 1} ({s.good.name})") (bearer := .consumer) (statute := stt)

/-- Customs Tariff Act 2014 Schedule 1 (reprint 14 June 2024), import duty column, headings read. -/
def nrTariff : TariffRule :=
  { name := "Import duty (Customs Tariff Act 2014)", country := "NR",
    lines := [{ hs := "0901", adValoremBp := 1000, statute := "0901 (10 %)" }, { hs := "1701", statute := "1701 (0 %)" },
      { hs := "2203", statute := "2203 (0 %)" }, { hs := "2204", statute := "2204 (0 %)" }, { hs := "2208", statute := "2208 (0 %)" },
      { hs := "2402", statute := "2402 (0 %)" }, { hs := "27101210", statute := "2710.12.10 (0 %)" },
      { hs := "27101220", statute := "2710.12.20 (0 %)" }, { hs := "27101230", statute := "2710.12.30 (0 %)" },
      { hs := "6109", adValoremBp := 1000, statute := "6109 (10 %)" }, { hs := "6203", adValoremBp := 1000, statute := "6203 (10 %)" },
      { hs := "8471", adValoremBp := 1000, statute := "8471 (10 %)" }, { hs := "8517", adValoremBp := 1000, statute := "8517 (10 %)" }],
    statute := "Customs Tariff Act 2014 Schedule 1 (reprint 14 June 2024), import duty column" }

def families : List Family :=
  [{ name := "5121 import excise (Customs Tariff Act 2014)", covers := [.excise],
     run := fun _ g _ => exciseCharges g.consumption }, customsFamily [nrTariff] "5123 customs import duty (Customs Tariff Act 2014)"]

def absent : List Absent :=
  [{ oecd := .vat, why := "no VAT or GST statute among the Laws of Nauru (registry 2026-11-21); revenue comes from the Employment and Services Tax Act 2014 and customs duties" }]

def notes : List String := ["NR 5121: Customs Tariff Act 2014 Schedule 1 import excise (reprint 2024-06-14), lexifina/nauru-law"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  nrTariff.unknown g
  ++ (if g.consumption.any (fun s => s.good == .spirits) then ["5121 import excise on spirits (Schedule 1 heading 22.08): the rate depends on the kind of spirit, not in the input: not booked (grade C)"] else [])
  ++ (if g.consumption.any (fun s => [Good.cigarettes, .beer, .wine, .petrol, .diesel].contains s.good && (exciseOn s).isNone) then ["5121 import excise: a line without its quantity (or strength): not booked (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .tobaccoOther) then ["5121 import excise on other tobacco ($390.40 a kg): the basket line has no mass: not booked (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .wine) then ["5121 import excise: wine taken as still wine in containers of 2 litres or less (2204.21)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food || s.good == .nonAlcoholic) then ["5121 import excise on sugar and confectionery (50 %) and sweetened drinks ($0.60 a litre or 60 %): inside mixed basket classes: not booked"] else [])

-- 20 sticks: $9
#guard (exciseOn { good := .cigarettes, amount := 30, quantity := 20000 }).map (·.1) == some 9
-- 10 litres of 5 % beer: $59
#guard (exciseOn { good := .beer, amount := 120, quantity := 10000, abvBp := 500 }).map (·.1) == some 59
#guard (exciseOn { good := .wine, amount := 40, quantity := 2000, abvBp := 1200 }).map (·.1) == some 19
#guard (exciseOn { good := .petrol, amount := 100, quantity := 50000 }).map (·.1) == some 30
#guard (exciseOn { good := .spirits, amount := 100, quantity := 1000, abvBp := 4000 }).isNone
#guard (nrTariff.charges { id := "t", household := { id := "t" }, consumption := [{ good := .other, amount := 110 }], raw := (Lean.Json.parse "{\"consumption\": [{\"hs\": \"0901\", \"origin\": \"AU\"}]}").toOption.getD Lean.Json.null }).map (·.due) == [10]
#guard (nrTariff.charges { id := "t", household := { id := "t" }, consumption := [{ good := .other, amount := 110 }], raw := (Lean.Json.parse "{\"consumption\": [{\"hs\": \"0901\", \"origin\": \"domestic\"}]}").toOption.getD Lean.Json.null }).length == 0
#guard (nrTariff.unknown { id := "t", household := { id := "t" }, consumption := [{ good := .petrol, amount := 110, quantity := 50000 }], raw := (Lean.Json.parse "{\"consumption\": [{\"hs\": \"2710.12\", \"origin\": \"AU\"}]}").toOption.getD Lean.Json.null }).length == 1
#guard absent.length == 1

end NrGlobal.Consumption
