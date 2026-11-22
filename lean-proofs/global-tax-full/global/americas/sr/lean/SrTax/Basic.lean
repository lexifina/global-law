import TaxKernel.World

/-!
# Suriname: inkomstenbelasting of a resident natural person (wages), belastingjaar 2025

Sources (Belastingdienst Suriname, belastingdienst.sr, answering only from a second machine; files in `sr/law/`):
* Wet Inkomstenbelasting 1922 (G.B. 1921 no. 112, "geldende tekst G.B. 1960 no. 84, zoals laatstelijk gewijzigd bij
  S.B. 2024 no. 3"), the authority's consolidation `Wet-Inkomstenbelasting.pdf` (uploaded 2024-10):
  - art. 34 lid 1: "over het eerste gehele bedrag van SRD 108.000.- van het zuiver inkomen bedraagt de belasting
    nihil; vervolgens ... boven SRD 108.000,- tot en met SRD 150.000,- 8%; ... boven SRD 150.000,- tot en met SRD
    192.000,- 18%; ... boven SRD 192.000.- tot en met SRD 234.000,- 28%; ... boven SRD 234.000,- 38%"; lid 1a
    (solidariteitsheffing) "gaat in op 1 februari 2021 en vervalt op 1 januari 2022".
  - art. 18 lid 3: for wages "de aftrekbare kosten, bedoeld in het eerste lid van artikel 10 gesteld op 4 (Vier)
    percent van het loon met een maximum van SRD 4800 ... per jaar".
  - art. 31 lid 1: married couples: deductions of art. 18 go to "de echtgenoot met het hoogste onzuiver inkomen";
    otherwise each spouse is assessed alone.
  - art. 52h: amounts and rates may be changed "Bij staatsbesluit".
* Staatsbesluit of 11 January 2024 (S.B. 2024 no. 2, Wet Loonbelasting art. 18a), in force 1 January 2024:
  belastingvrije som "SRD 108.000,-" a year and wage-tax tariff 8/18/28/38 % on 42,000-wide bands (consistent with
  art. 34). No 2025 staatsbesluit was found on belastingdienst.sr.
W5 pattern A (2026-11-20): AOV premium. Wet Algemeen Oudedagsvoorzieningsfonds (Wet van 20 maart 1981, S.B. 1981
no. 30, "zoals laatstelijk gewijzigd bij S.B. 2002 no. 96"; Belastingdienst consolidation `Wet-AOV.pdf`, uploaded
2024-10, `sr/law/w5/`): art. 19 lid 1 "Premieplichtig is de ingezetene van Suriname ... die ... loon uit
dienstbetrekking geniet en de leeftijd van 60 jaar nog niet heeft bereikt"; art. 20 lid 1 "De grondslag van de heffing
is het zuiver inkomen ... en - ingeval loonbelasting verschuldigd is- het zuiver loon in de zin van de Wet
Loonbelasting"; lid 2 "De hoogte van de premie bedraagt 4% (vier percent) van de heffings-grondslag". Zuiver loon =
loon less the aftrekbare kosten (Wet Loonbelasting art. 4 lid 2; the 4 % / SRD 4,800 of IB art. 18 lid 3). No ceiling,
no franchise in the Act. Not deductible: IB art. 18 lid 1 (b) allows premiums for the periodic payments of art. 8 lid
1, and art. 8 lid 2 (a) excludes "uitkeringen ... ingevolge de Wet Algemene Oudedagsvoorziening fonds". The
Basiszorgverzekering and the Pensioenwet contributions were not reached (unsupported). Input `"w5Contrib": false`
drops the AOV premium.
-/

namespace SrTax
open TaxKernel

/-- art. 34 lid 1. -/
def sched : Schedule := Schedule.ofList [(0, 0), (108000, 800), (150000, 1800), (192000, 2800), (234000, 3800)]

/-- art. 18 lid 3: 4 % of wages, at most 4,800. -/
def costs (w : Int) : Int := min 4800 (divR .down (400 * pos w) 10000)

structure Person where
  zuiver : Int
  tax : Int

def person (a : Adult) : Person :=
  let w := pos a.wages
  let zuiver := pos (w - costs w + pos a.selfEmployment + pos a.pension)
  { zuiver := zuiver, tax := sched.tax Rule.unitDown zuiver }

/-- Wet AOV art. 19-20: 4 % of zuiver loon (wages less the art. 18 lid 3 costs) for a resident under 60. -/
def aov (a : Adult) : Int :=
  if a.age ≥ 60 then 0 else divR .down (400 * pos (pos a.wages - costs (pos a.wages))) BP

#guard aov { age := 40, wages := 120000 } = 4608   -- (120,000 - 4,800) x 4 %
#guard aov { age := 60, wages := 120000 } = 0

def out (c : Canon) : Out :=
  let ps := c.adults.map person
  let w5 := (c.bool? "w5Contrib").getD true
  let prem := if w5 then sumInts (c.adults.map aov) else 0
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["interest, dividends (dividendbelasting), rents and gains not modelled"] else []) ++
    (if c.pensionContributions ≠ 0 || c.charitable ≠ 0 then ["art. 18 deductions (premiums, gifts) not modelled"] else [])
  Out.make c "SR" "SRD" (sumInts (ps.map (·.tax))) (employeeSocial := prem)
    (detail := [Out.d "aovPremium" prem, Out.d "taxableIncome" (sumInts (ps.map (·.zuiver))),
      Out.dStr "note" "individual assessment (art. 31); zuiver inkomen = wages less 4 % costs (max 4,800, art. 18(3)); art. 34: nil to 108,000 then 8/18/28/38 %"])
    (unsupported := unsup ++ ["Basiszorgverzekering and Pensioenwet contributions not reached (AOV premium modelled; AOV on self-employment profit not modelled)",
      "consolidation 'laatstelijk gewijzigd bij S.B. 2024 no. 3': a 2025 staatsbesluit under art. 52h, if any, not reached"])

def country : Country := { code := "SR", name := "Suriname (Wet Inkomstenbelasting 1922)", currency := "SRD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard sched.tax Rule.unitDown 150000 = 3360
#guard sched.tax Rule.unitDown 234000 = 22680
#guard costs 200000 = 4800

end SrTax
