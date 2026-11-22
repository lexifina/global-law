S = dict(cc="NZ", family_name="5111 GST",
doc=r'''# New Zealand 2025: goods and services tax (5111); excise not modelled

Source: Goods and Services Tax Act 1985, legislation.govt.nz "latest" whole act as archived by the Internet Archive on
2025-02-03 ("Version as at 1 April 2024", i.e. no amendment in force between April 2024 and February 2025;
`nz/law/wb/gst_whole_wb20250203.html`, timestamp and sha256 in `ARCHIVE_INDEX.tsv`).
* **s. 8 (1)**: goods and services tax "shall be charged … at the rate of 15 % on the supply (but not including an
  exempt supply)".
* **s. 14 (1)**: exempt (a) financial services; (c) "the supply of accommodation in any dwelling by way of— (i) hire".
* **s. 51 (1) (a)**: registration when supplies in 12 months have "exceeded $60,000".''',
vat=dict(name="Goods and services tax", standard=1500, threshold=60000, statute="GST Act 1985 s. 8 (1) (15 %), s. 14 (1) (a), (c), s. 51 (1) (a) ($60,000)",
  classes={"financial":"exempt","insurance":"exempt","rent":"exempt"}),
notes=["NZ 5111: GST Act 1985, version as at 1 April 2024 (archived 2025-02-03)"],
unsupported=[[["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"excise and excise-equivalent duty (Customs and Excise Act 2018, Tariff), road user charges: not modelled"],
 [["insurance"],"insurance taken as a financial service (life insurance is; general insurance is taxable in NZ)"]],
guards=["vat.embedded { good := .food, amount := 1150 } == 150","vat.embedded { good := .rent, amount := 1150 } == 0","vat.net { turnover := 60000, sales := [{ good := .other, net := 60000 }] } == 0"],
taxes=[{"oecd":"5111","tax":"Goods and services tax","statute":"GST Act 1985 ss. 8 (1), 14 (1), 51 (1)","dated":"version as at 1 April 2024, archived 2025-02-03 (in force into 2025)","grade":"B","kernel_parts":["Vat"],"unsupported":["mid-2025 version not confirmed","s. 14 other exempt supplies"]},
 {"oecd":"5121","tax":"Excise duty (alcohol, tobacco, fuel)","statute":"Customs and Excise Act 2018, Excise and Excise-equivalent Duties Table","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["the Table (CPI-indexed each 1 July) was not reached; legislation.govt.nz answers 202 to scripts; would unlock: an archived 2025 copy of the Table"]}])

# ---- R3 session 8 (2026-11-21): excise duty (5121), Excise and Excise-equivalent Duties Table (grade A).
# Pre-change copy: tools/bak8/NZ_cons.py. Sources: Customs Working Tariff Document, Excise and Excise-equivalent Duties
# Table, replacement pages January 2025 and July 2025 (Internet Archive captures 20250404002355 of
# customs.govt.nz/globalassets/documents/tariff-documents/wtd-2025/excise-duties.pdf and 20250708145920 of
# customs.govt.nz/media/bpdlril4/03-excise-and-excise-equivalent-duties-table.pdf): nz/law/nz_eedt_jan2025_wb.pdf,
# nz_eedt_jul2025_wb.pdf.
S["imports"] = ["TaxKernel.Global2"]
S["family_name"] = "5111 GST; 5121 excise duty"
S["doc"] = S["doc"].replace("; excise not modelled", "; excise duty (5121)") + r'''

**Excise duty (session 8, grade A)**: Customs and Excise Act 2018 Schedule 3 cl. 1 (Part A, goods manufactured in New
Zealand) and cl. 14 (Part B, excise-equivalent duty on imports at the same rates): the Excise and Excise-equivalent
Duties Table as amended by Orders in Council, in the Customs Working Tariff Document replacement pages of January 2025
(last amendment: Tobacco Products Indexation and Reduction Amendment Order 2024) and July 2025 (adds the Alcoholic
Beverages Indexation Amendment Order 2025, from 1 July 2025). Part A items:
* **99.75.23D / 99.75.37D** motor spirit 70.024 c per litre (all 2025; the lead charge of 8 c per g is not applied);
  **99.75.49H** automotive diesel Free (diesel vehicles pay road user charges, not modelled).
* **99.10** beer: more than 1.15 % to 2.5 % 55.351 c / 56.747 c per litre; above 2.5 % $36.905 / $37.836 per litre of
  alcohol (to 30 June / from 1 July 2025).
* **99.20.20L** wine (other) $3.6905 / $3.7836 per litre; **99.20.11A** above 14 % fortified $67.220 / $68.915 per l al.
* **99.45** spirits: brandy, whisky, rum, gin, vodka, other $67.220 / $68.915 per litre of alcohol; spirit-based beverages
  by strength (99.45.72F-99.45.90D): 1.15-2.5 % 55.351 c / 56.747 c per l; 2.5-6 % $36.905 / $37.836 per l al; 6-9 %
  $2.9524 / $3.0268 per l; 9-14 % $3.6905 / $3.7836 per l; above 14 % $67.220 / $68.915 per l al.
* **99.60.29F** cigarettes not over 0.8 g of tobacco: $1,272.01 per 1,000 (all 2025); **99.65.21B** smoking tobacco
  $1,812.61 per kg of tobacco content (needs the line's `"massG"`).'''
S["extra_lean"] = r'''/-- One alcohol period of the Table (rates in cents/1000 per litre, or per litre of alcohol), `firstOnly` order. -/
def nzAlcohol (fr to : String) (low ral l69 l914 hi : Int) : List ExciseRule :=
  let st (it r : String) := s!"Customs and Excise Act 2018 Sch. 3 cl. 1, Excise and Excise-equivalent Duties Table Part A item {it}: {r}"
  let pl (g : Good) (it : String) (lo hi n d : Int) : ExciseRule :=
    { good := g, name := "Excise duty (alcohol)", perUnitNum := n, perUnitDen := d, minAbvBp := lo, maxAbvBp := hi,
      validFrom := fr, validTo := to, statute := st it s!"{n}/{d} dollars per litre" }
  let pa (g : Good) (it : String) (lo hi n : Int) : ExciseRule :=
    { good := g, name := "Excise duty (alcohol)", perUnitNum := n, perUnitDen := 1000, onPureAlcohol := true,
      minAbvBp := lo, maxAbvBp := hi, validFrom := fr, validTo := to, statute := st it s!"{n}/1000 dollars per litre of alcohol" }
  [pl .beer "99.10.25F" 115 250 low 100000, pa .beer "99.10.50G" 250 100000 ral,
   pa .wine "99.20.11A" 1400 100000 hi, pl .wine "99.20.20L" (-1) 1400 l914 10000,
   pl .spirits "99.45.72F" 115 250 low 100000, pa .spirits "99.45.76J" 250 600 ral,
   pl .spirits "99.45.78E" 600 900 l69 10000, pl .spirits "99.45.80G" 900 1400 l914 10000,
   pa .spirits "99.45.10F-99.45.45J, 99.45.86F, 99.45.90D" 1400 100000 hi]

def nzOther : List ExciseRule :=
  [{ good := .petrol, name := "Excise duty (motor spirit)", perUnitNum := 70024, perUnitDen := 100000,
     statute := "Customs and Excise Act 2018 Sch. 3 cl. 1, Excise and Excise-equivalent Duties Table Part A item 99.75.23D / 99.75.37D: 70.024 c per litre" },
   { good := .cigarettes, name := "Excise duty (cigarettes)", perUnitNum := 127201, perUnitDen := 100000,
     statute := "Customs and Excise Act 2018 Sch. 3 cl. 1, Excise and Excise-equivalent Duties Table Part A item 99.60.29F: $1,272.01 per 1,000 cigarettes" },
   { good := .tobaccoOther, name := "Excise duty (smoking tobacco)", perKgNum := 181261, perKgDen := 100,
     statute := "Customs and Excise Act 2018 Sch. 3 cl. 1, Excise and Excise-equivalent Duties Table Part A item 99.65.21B: $1,812.61 per kg of tobacco content" }]

def nzPeriods : List (List ExciseRule) :=
  [nzAlcohol "" "2025-07-01" 55351 36905 29524 36905 67220,
   nzAlcohol "2025-07-01" "" 56747 37836 30268 37836 68915, nzOther]

def nzExciseCharges (g : CanonGlobal) : List Charge :=
  nzPeriods.flatMap fun rs => exciseRuleCharges rs g (firstOnly := true)'''
S["extra_run"] = S.get("extra_run", []) + ["nzExciseCharges g"]
S["extra_covers"] = S.get("extra_covers", []) + [".excise"]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("excise and excise-equivalent duty (Customs")] + [
 [["diesel"], "automotive diesel is Free of excise (item 99.75.49H); road user charges (Road User Charges Act 2012) are not modelled"],
 [["tobaccoOther"], "smoking tobacco (item 99.65.21B) needs the line's \"massG\"; a line without it is charged 0"],
 [["beer", "wine", "spirits"], "alcohol lines need a strength (\"abvBp\"): beer and spirits at 1.15 % or less are not dutiable; wine above 14 % is taken as fortified (99.20.11A)"]]
S["guards"] = S["guards"] + [
 "nzPeriods.length == 3",
 "(nzOther.find? (fun e => e.good == .petrol)).map (fun e => e.dutyOn { good := .petrol, amount := 300, quantity := 100000 } {}) == some 70",
 "(nzOther.find? (fun e => e.good == .cigarettes)).map (fun e => e.dutyOn { good := .cigarettes, amount := 50, quantity := 20000 } {}) == some 25",
 "((nzPeriods.getD 1 []).find? (fun e => e.good == .beer && e.onPureAlcohol)).map (fun e => e.dutyOn { good := .beer, amount := 60, quantity := 9000, abvBp := 500 } {}) == some 17",
 "((nzPeriods.getD 0 []).find? (fun e => e.good == .wine && e.maxAbvBp == 1400)).map (fun e => e.dutyOn { good := .wine, amount := 20, quantity := 750, abvBp := 1300 } {}) == some 2"]
S["notes"] = S["notes"] + ["NZ 5121: Excise and Excise-equivalent Duties Table (Customs and Excise Act 2018 Sch. 3), WTD replacement pages Jan and Jul 2025"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "5121"] + [
 {"oecd": "5121", "tax": "Excise and excise-equivalent duty (motor spirit, beer, wine, spirits, tobacco)",
  "statute": "Customs and Excise Act 2018 Sch. 3 cl. 1, 14; Excise and Excise-equivalent Duties Table Part A items 99.10, 99.20, 99.45, 99.60.29F, 99.65.21B, 99.75",
  "dated": "Working Tariff Document replacement pages January 2025 and July 2025 (Alcoholic Beverages Indexation Amendment Order 2025 from 1 July 2025)",
  "grade": "A", "kernel_parts": ["ExciseRule"],
  "unsupported": ["road user charges on diesel vehicles not modelled", "lead surcharge on motor spirit not applied", "smoking tobacco needs the line's mass"]}]
