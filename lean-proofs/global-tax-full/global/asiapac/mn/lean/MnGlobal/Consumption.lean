import MnGlobal.Pit
import TaxKernel.Global2

/-!
# Mongolia 2025: value added tax (5111); excise tax (5121)

Source: Law on Value Added Tax of 9 July 2015 (restated), consolidated text on legalinfo.mn (`/mn/detail/11227`, read
2026-11-21; `mn/law/mn_vat2015_legalinfo.txt`, sha256 in `SHA256SUMS`). The consolidation prints each amendment note;
the version in force in 2025 is read through them (the law of 26 June 2026 changes "50" to "400" million in 4.1.8, 5.2,
5.3, 5.5 and 13.6 from 1 January 2027: not applied to 2025).
* **art. 11.1**: tax at 10 % on the value of supplies under 7.1.1 and imports under 7.1.2; **11.2, 12.1**: exports 0 %.
* **art. 11.3-11.4**: petrol and diesel at 0-10 % as set by the Government (the 2025 resolution was not read: modelled
  at 10 % and flagged).
* **art. 5.2, 13.6** (2025 wording): a person is a VAT withholder (registered) when sales reach 50 million tugrik;
  persons selling below 50 million a year (other than importers) are exempt. Threshold 50 000 000.
* **art. 13.1.7** sale of dwellings; **13.1.9** gas fuel; **13.1.15-13.1.17** domestic grain, potatoes, vegetables,
  flour, meat and milk supplied by their producers (13.10: not by resellers: food is modelled at 10 % and flagged).
* **art. 13.5** exempt services: 13.5.1-13.5.7 currency exchange, banking, insurance, securities, loans; **13.5.8**
  letting of dwellings; **13.5.9** licensed education; **13.5.10** health services (13.7: not the manufacture or sale of
  medicines, which stay at 10 %); **13.5.13** public transport under the Auto Transport Law 3.1.11.

**Excise tax (session 6, grade A)**: Law on Excise Tax of 29 June 2006 as amended, legalinfo.mn consolidation
(`/mn/detail/434`, read 2026-11-21; `mn/law/mn_excise2006_legalinfo434.html`): amendment notes to 2 July 2026, none
changing the 2025 rates below (the 2024 sugary-drinks clause 4.1.6 / 6.9 applies from 1 January 2027).
* **art. 6.1.1** (added 6 July 2022), column "from 1 January 2025 to 1 January 2027", tugrik per litre: vodka, liqueurs,
  cordials and other spirits: below 25 % 3 900; 25-34 % 7 700; 34-36 % 10 440; 36-40 % 11 500; 40 % and above 34 450.
  Cognac, whisky, rum, gin (line field `"sub": "whisky"`): 9 600; 19 200; 26 100; 28 700; 44 000. Bands read as "from X
  up to Y" = [X, Y).
* **art. 6.1 table** (column "2020 and after"): wine below 35 % 870 per litre (35 % and above 7 830); beer 350 per litre;
  cigarettes 4 180 per 100 sticks.
* **art. 6.1, 6.2, 6.7**: petrol and diesel 0-15 950 / 0-17 400 / 0-21 750 per tonne within ranges set by the Government
  (domestic) and per border port (imports): the Government's 2025 rates were not read: not modelled.
-/

namespace MnGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value added tax", standard := 1000, threshold := 50000000,
    classOf := fun gd => match gd with
      | .financial | .insurance | .rent | .education | .health | .transport | .gas => .exempt
      | _ => .standard }

def vatStatute : String := "Law on VAT 2015 art. 11.1 (10 %), 5.2 and 13.6 (50 million tugrik in 2025), 13.1, 13.5"

/-- Law on Excise Tax 2006 art. 6.1 and 6.1.1 (2025 column): tugrik per litre or stick; bands [X, Y) as `minAbvBp := X - 1`,
`maxAbvBp := Y - 1`. Sub-specific rules first (`firstOnly`). -/
def mnExcise : List ExciseRule :=
  let sp (sub nm : String) (lo hi r : Int) : ExciseRule :=
    { good := .spirits, sub := sub, name := nm, perUnitNum := r, minAbvBp := lo - 1, maxAbvBp := hi - 1,
      statute := s!"Law on Excise Tax 2006 art. 6.1.1 (2025-2026 column): {r} tugrik per litre" }
  [sp "whisky" "Excise tax (cognac, whisky, rum, gin)" 0 2500 9600, sp "whisky" "Excise tax (cognac, whisky, rum, gin)" 2500 3400 19200,
   sp "whisky" "Excise tax (cognac, whisky, rum, gin)" 3400 3600 26100, sp "whisky" "Excise tax (cognac, whisky, rum, gin)" 3600 4000 28700,
   sp "whisky" "Excise tax (cognac, whisky, rum, gin)" 4000 100001 44000,
   sp "" "Excise tax (vodka and other spirits)" 0 2500 3900, sp "" "Excise tax (vodka and other spirits)" 2500 3400 7700,
   sp "" "Excise tax (vodka and other spirits)" 3400 3600 10440, sp "" "Excise tax (vodka and other spirits)" 3600 4000 11500,
   sp "" "Excise tax (vodka and other spirits)" 4000 100001 34450,
   { good := .wine, name := "Excise tax (wine)", perUnitNum := 870, maxAbvBp := 3499,
     statute := "Law on Excise Tax 2006 art. 6.1 table item 4: wine below 35 %, 870 tugrik per litre" },
   { good := .wine, name := "Excise tax (wine)", perUnitNum := 7830, minAbvBp := 3499,
     statute := "Law on Excise Tax 2006 art. 6.1 table item 4: wine 35 % and above, 7 830 tugrik per litre" },
   { good := .beer, name := "Excise tax (beer)", perUnitNum := 350,
     statute := "Law on Excise Tax 2006 art. 6.1 table item 5: 350 tugrik per litre" },
   { good := .cigarettes, name := "Excise tax (cigarettes)", perUnitNum := 4180, perUnitDen := 100,
     statute := "Law on Excise Tax 2006 art. 6.1 table item 6: 4 180 tugrik per 100 sticks" }]

def families : List Family :=
  [{ name := "5111 Value added tax; 5121 excise tax", covers := [.vat, .excise],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ exciseRuleCharges mnExcise g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["MN 5111: Law on VAT 2015 (restated) as amended, legalinfo.mn consolidation read 2026-11-21; 2025 wording from the amendment notes", "MN 5121: Law on Excise Tax 2006 art. 6.1, 6.1.1 (legalinfo.mn /mn/detail/434, 2025 column); fuel not modelled"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then ["VAT on petrol and diesel is 0-10 % as set by the Government (Law on VAT 2015 art. 11.3-11.4); the 2025 resolution was not read: modelled at 10 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food) then ["domestic grain, potatoes, vegetables, flour, meat and milk are exempt when supplied by their producers (art. 13.1.15-13.1.17, 13.10); the basket's food is modelled at 10 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .transport) then ["only public transport under the Auto Transport Law art. 3.1.11 is exempt (art. 13.5.13); applied to the whole class"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then ["excise tax on petrol and diesel: per tonne within ranges set by the Government (Law on Excise Tax 2006 art. 6.1 items 8-9, 6.2, 6.7); the 2025 rates were not read: not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .tobaccoOther) then ["excise tax on loose tobacco (art. 6.1 item 7: 3 130 per kg) not modelled (no mass on the line)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits) then ["spirits without a strength on the line fall in the lowest band; cognac, whisky, rum and gin need the line field \"sub\": \"whisky\""] else [])

#guard vat.embedded { good := .clothing, amount := 1100 } == 100
#guard vat.embedded { good := .medicines, amount := 1100 } == 100
#guard vat.embedded { good := .health, amount := 1100 } == 0
#guard vat.embedded { good := .rent, amount := 1100 } == 0
#guard vat.net { turnover := 50000000, sales := [{ good := .other, net := 50000000 }] } == 0
#guard (mnExcise.find? (fun e => e.good == .spirits && e.sub == "" && e.minAbvBp < 4000 && 4000 <= e.maxAbvBp)).map (·.perUnitNum) == some 34450
#guard (mnExcise.find? (fun e => e.good == .spirits && e.sub == "" && e.minAbvBp < 3800 && 3800 <= e.maxAbvBp)).map (·.perUnitNum) == some 11500
#guard (mnExcise.find? (fun e => e.good == .spirits && e.sub == "" && e.minAbvBp < 2500 && 2500 <= e.maxAbvBp)).map (·.perUnitNum) == some 7700
#guard (mnExcise.filter (fun e => e.good == .cigarettes)).length == 1

end MnGlobal.Consumption
