S = dict(cc="MN", family_name="5111 Value added tax",
doc=r'''# Mongolia 2025: value added tax (5111); excise tax not modelled

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
  medicines, which stay at 10 %); **13.5.13** public transport under the Auto Transport Law 3.1.11.''',
vat=dict(name="Value added tax", standard=1000, threshold=50000000, statute="Law on VAT 2015 art. 11.1 (10 %), 5.2 and 13.6 (50 million tugrik in 2025), 13.1, 13.5",
  classes={"financial":"exempt","insurance":"exempt","rent":"exempt","education":"exempt","health":"exempt","transport":"exempt","gas":"exempt"}),
notes=["MN 5111: Law on VAT 2015 (restated) as amended, legalinfo.mn consolidation read 2026-11-21; 2025 wording from the amendment notes"],
unsupported=[[["petrol","diesel"],"VAT on petrol and diesel is 0-10 % as set by the Government (Law on VAT 2015 art. 11.3-11.4); the 2025 resolution was not read: modelled at 10 %"],
 [["food"],"domestic grain, potatoes, vegetables, flour, meat and milk are exempt when supplied by their producers (art. 13.1.15-13.1.17, 13.10); the basket's food is modelled at 10 %"],
 [["transport"],"only public transport under the Auto Transport Law art. 3.1.11 is exempt (art. 13.5.13); applied to the whole class"],
 [["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"excise tax (Law on Excise Tax 2006 as amended) not modelled: per-unit rates not read"]],
extra_run=[],
guards=["vat.embedded { good := .clothing, amount := 1100 } == 100","vat.embedded { good := .medicines, amount := 1100 } == 100","vat.embedded { good := .health, amount := 1100 } == 0","vat.embedded { good := .rent, amount := 1100 } == 0","vat.net { turnover := 50000000, sales := [{ good := .other, net := 50000000 }] } == 0"],
taxes=[{"oecd":"5111","tax":"Value added tax (10 %)","statute":"Law on Value Added Tax 2015 (restated) art. 5.2, 11.1-11.4, 12.1, 13.1, 13.5, 13.6, 13.7","dated":"legalinfo.mn consolidation read 2026-11-21 (amendments to 2026-06-26 noted); 2025 wording reconstructed from the amendment notes (threshold 50 million to 31 Dec 2026)","grade":"A","kernel_parts":["Vat"],"unsupported":["petrol and diesel: 0-10 % by Government resolution (art. 11.3-11.4), resolution not read: modelled at 10 %","producer-only exemptions for domestic food (art. 13.1.15-13.1.17) not applied to the basket"]},
 {"oecd":"5121","tax":"Excise tax","statute":"Law on Excise Tax (2006) as amended","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: legalinfo.mn (reachable from a second machine; the excise law id was not looked up in this pass); would unlock: the Law on Excise Tax consolidation (tugrik per litre by strength, per 1,000 cigarettes; fuel per tonne by Government within ranges)"]}])

# ---- R3 session 6 (2026-11-21): excise tax (Law on Excise Tax 2006, legalinfo.mn /mn/detail/434, read 2026-11-21;
# mn/law/mn_excise2006_legalinfo434.html). Pre-change copy: tools/bak6/MN_cons.py.
S["imports"] = ["TaxKernel.Global2"]
S["family_name"] = "5111 Value added tax; 5121 excise tax"
S["doc"] = S["doc"].replace("; excise tax not modelled", "; excise tax (5121)") + r'''

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
  (domestic) and per border port (imports): the Government's 2025 rates were not read: not modelled.'''
S["extra_lean"] = r'''/-- Law on Excise Tax 2006 art. 6.1 and 6.1.1 (2025 column): tugrik per litre or stick; bands [X, Y) as `minAbvBp := X - 1`,
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
     statute := "Law on Excise Tax 2006 art. 6.1 table item 6: 4 180 tugrik per 100 sticks" }]'''
S["extra_run"] = S.get("extra_run", []) + ["exciseRuleCharges mnExcise g (firstOnly := true)"]
S["extra_covers"] = S.get("extra_covers", []) + [".excise"]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("excise tax (Law on Excise Tax 2006")] + [
 [["petrol", "diesel"], "excise tax on petrol and diesel: per tonne within ranges set by the Government (Law on Excise Tax 2006 art. 6.1 items 8-9, 6.2, 6.7); the 2025 rates were not read: not modelled"],
 [["tobaccoOther"], "excise tax on loose tobacco (art. 6.1 item 7: 3 130 per kg) not modelled (no mass on the line)"],
 [["spirits"], "spirits without a strength on the line fall in the lowest band; cognac, whisky, rum and gin need the line field \"sub\": \"whisky\""]]
S["guards"] = S["guards"] + [
 "(mnExcise.find? (fun e => e.good == .spirits && e.sub == \"\" && e.minAbvBp < 4000 && 4000 <= e.maxAbvBp)).map (·.perUnitNum) == some 34450",
 "(mnExcise.find? (fun e => e.good == .spirits && e.sub == \"\" && e.minAbvBp < 3800 && 3800 <= e.maxAbvBp)).map (·.perUnitNum) == some 11500",
 "(mnExcise.find? (fun e => e.good == .spirits && e.sub == \"\" && e.minAbvBp < 2500 && 2500 <= e.maxAbvBp)).map (·.perUnitNum) == some 7700",
 "(mnExcise.filter (fun e => e.good == .cigarettes)).length == 1"]
S["notes"] = S["notes"] + ["MN 5121: Law on Excise Tax 2006 art. 6.1, 6.1.1 (legalinfo.mn /mn/detail/434, 2025 column); fuel not modelled"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "5121"] + [
 {"oecd": "5121", "tax": "Excise tax on alcohol and cigarettes (per litre by strength band; 4 180 per 100 cigarettes)",
  "statute": "Law on Excise Tax 2006 as amended art. 4.1, 5, 6.1, 6.1.1",
  "dated": "legalinfo.mn consolidation read 2026-11-21 (amendments to 2 July 2026 noted); 2025 column of art. 6.1.1",
  "grade": "A", "kernel_parts": ["ExciseRule"],
  "unsupported": ["petrol and diesel: per-tonne rates set by the Government within statutory ranges (not read)", "loose tobacco per kg not modelled"]}]
