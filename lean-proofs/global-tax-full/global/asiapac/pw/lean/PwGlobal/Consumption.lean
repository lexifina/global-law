import PwGlobal.Pit

/-!
# Palau 2025: Palau Goods and Services Tax (5111), import taxes on alcohol and fuel and the tobacco excise (5121)

Sources (on the build server, `cmp20/world/B14-pacific/pw/law/`, sha256 in `law/SOURCES.tsv`):
* **RPPL 11-11** (Palau Goods and Services Tax Act, as enacted; PGST from 2023-01-01). § 1211 (b): "The rate of PGST
  is: (1) for a taxable supply that is a zero-rated supply, zero percent (0%); or (2) for any other taxable supply,
  ten percent (10%)". § 1213 (a): "a supply of financial services" is exempt. § 1221 (b): "The registration
  threshold is three hundred thousand dollars ($300,000)".
* **Palau National Code Title 40** (Supp. 10-12): § 1301 (a) import tax (5) "beer: three cents ($0.03) per ounce",
  (6) liquor "thirty cents ($0.30) per ounce", (7) wine "twenty cents ($0.20) per fluid ounce", (9) "liquid fuel …
  five cents ($0.05) per gallon"; § 2601 (a) (1) cigarettes "five dollars ($5.00) per 0.017 kilograms, and packs …
  weighing less than 0.017 kilograms … five dollars ($5.00) per pack" (a pack of 20 taken).
Units: US fluid ounce 29.5735 ml, US gallon 3.785411784 l; rounding "to the next ounce" per container is not applied.
-/

namespace PwGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Palau Goods and Services Tax", standard := 1000, threshold := 300000,
    classOf := fun gd => match gd with
      | .financial | .insurance => .exempt
      | _ => .standard }

def excise : Excise :=
  { rates := [
      { good := .beer, name := "Import tax (beer)", perUnitNum := 3000000, perUnitDen := 2957353,
        statute := "40 PNCA § 1301 (a) (5) ($0.03 per ounce)" },
      { good := .spirits, name := "Import tax (liquor)", perUnitNum := 30000000, perUnitDen := 2957353,
        statute := "40 PNCA § 1301 (a) (6) ($0.30 per ounce)" },
      { good := .wine, name := "Import tax (wine)", perUnitNum := 20000000, perUnitDen := 2957353,
        statute := "40 PNCA § 1301 (a) (7) ($0.20 per fluid ounce)" },
      { good := .petrol, name := "Import tax (liquid fuel)", perUnitNum := 5000, perUnitDen := 378541,
        statute := "40 PNCA § 1301 (a) (9) ($0.05 per gallon)" },
      { good := .diesel, name := "Import tax (liquid fuel)", perUnitNum := 5000, perUnitDen := 378541,
        statute := "40 PNCA § 1301 (a) (9) ($0.05 per gallon)" },
      { good := .cigarettes, name := "Tobacco excise tax", perUnitNum := 5, perUnitDen := 20,
        statute := "40 PNCA § 2601 (a) (1) ($5.00 per pack; pack of 20)" }] }

def vatStatute : String := "RPPL 11-11 § 1211 (b) (10 %), § 1213 (a) (financial services exempt), § 1221 (b) ($300,000)"

def families : List Family :=
  [{ name := "5111 PGST", covers := [.vat],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       }]

/-- Session 11: the 5121 import taxes are kept for a re-cite but not run (year-in-force audit, grade C). -/
def excisePre11Run (g : CanonGlobal) : List Charge := excise.charges g.consumption

def absent : List Absent := []
def notes : List String := ["PW 5111/5121: RPPL 11-11 (PGST) as enacted; PNC Title 40 §§ 1301, 2601"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty then ["5121 import taxes on beer, wine, liquor, fuel and tobacco not modelled (session 11 year-in-force audit: PNC Title 40 supplement whose date is not stated; no 2025 version reached: grade C)"] else []) ++
  (if g.consumption.any (·.good == .tobaccoOther) then ["other tobacco ($5.00 per 0.017 kg) needs weight: not modelled"] else [])
  ++ (if g.consumption.any (·.good == .insurance) then ["insurance taken as a financial service (exempt)"] else [])

#guard vat.embedded { good := .food, amount := 1100 } == 100
#guard vat.net { turnover := 300000, sales := [{ good := .other, net := 300000 }] } == 0
-- 100 litres of beer: 3 381 fl oz × $0.03 = $101
#guard excise.duty { good := .beer, amount := 400, quantity := 100000 } == 101
-- 50 packs of cigarettes: $250
#guard excise.duty { good := .cigarettes, amount := 600, quantity := 1000000 } == 250

end PwGlobal.Consumption
