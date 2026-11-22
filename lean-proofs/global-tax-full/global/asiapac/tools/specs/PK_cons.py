S = dict(cc="PK", family_name="5111 Sales tax on goods (federal)",
doc=r'''# Pakistan 2025: federal sales tax on goods (5111); provincial sales tax on services and federal excise not modelled

Source: Sales Tax Act, 1990 "As amended up to 30th June, 2025" (FBR consolidation, Finance Act 2025;
`download1.fbr.gov.pk/Docs/202586148252375SalesTaxActupdatedupto2025-26.pdf`, fetched 2026-11-21;
`pk/law/pk_sales_tax_act1990_upto_2025-06-30.pdf`, sha256 in `SHA256SUMS`).
* **s. 3 (1)**: "there shall be charged, levied and paid a tax known as sales tax at the rate of [eighteen] per cent of the
  value of (a) taxable supplies made by a registered person …" (18 % unchanged through 2025).
* **Sixth Schedule Table-1** (exempt, s. 13 (1)): S. No. 21 rice, wheat and meslin and other unprocessed food items of the
  Table; S. Nos. 32-33 books, newsprint; S. No. 176 (inserted by Finance Act 2024) "POL products: (i) MS (Petrol) (ii) High
  Speed Diesel Oil (iii) Kerosene (iv) Light Diesel Oil".
* **Eighth Schedule S. No. 81**: "Substances registered as drugs under the Drugs Act, 1976": 1 %, charged at manufacture or
  import as final discharge (`superReduced` 1 %, applied to the retail amount: flagged).
The federal Act taxes goods; services (restaurants, hotels, transport, telecoms, health, education, finance, insurance)
fall under provincial sales tax on services (Punjab Sales Tax on Services Act 2012), not modelled: those classes carry no
federal tax here. Rent of dwellings is not a supply of goods. Grade B (class-level mapping of HS-coded schedules).''',
vat=dict(name="Sales tax", standard=1800, superReduced=100, statute="Sales Tax Act, 1990 s. 3 (1) (18 %), Sixth Schedule Table-1 S. Nos. 21, 32, 33, 176, Eighth Schedule S. No. 81 (1 %) (as amended up to 30 June 2025)",
  classes=dict(**{g:"exempt" for g in ["food","books","newspapers","petrol","diesel","heatingOil","rent","restaurants","hotels","transport","communication","health","education","financial","insurance"]}, medicines="superReduced")),
notes=["PK 5111: Sales Tax Act 1990 (as amended up to 30 June 2025) s. 3 (1), Sixth and Eighth Schedules"],
unsupported=[[["food"],"food taken as exempt (Sixth Schedule Table-1: unprocessed staples); processed and packaged food is taxable at 18 % or under the Third Schedule on retail price"],
 [["medicines"],"drugs: 1 % on the manufacturer's or importer's value (Eighth Schedule S. No. 81) applied to the retail amount"],
 [["restaurants","hotels","transport","communication","health","education","financial","insurance"],"provincial sales tax on services (e.g. Punjab Sales Tax on Services Act 2012, 16 %) not modelled"],
 [["cigarettes","tobaccoOther","nonAlcoholic"],"federal excise duty (Federal Excise Act 2005, First Schedule) not modelled"]],
guards=["vat.embedded { good := .clothing, amount := 11800 } == 1800","vat.embedded { good := .petrol, amount := 11800 } == 0","vat.embedded { good := .medicines, amount := 10100 } == 100"],
taxes=[{"oecd":"5111","tax":"Sales tax on goods (federal, 18 %)","statute":"Sales Tax Act, 1990 s. 3 (1); Sixth Schedule Table-1 S. Nos. 21, 32, 33, 176; Eighth Schedule S. No. 81","dated":"FBR consolidation as amended up to 30 June 2025 (rate and POL exemption unchanged since Finance Act 2024)","grade":"B","kernel_parts":["Vat"],"unsupported":["HS-level schedules mapped to classes (food, drugs)","cottage-industry and retailer regimes (s. 2 (5AB), Third Schedule retail price) not modelled","no registration threshold applied"]},
 {"oecd":"5126","tax":"Provincial sales tax on services (Punjab)","statute":"Punjab Sales Tax on Services Act 2012, Second Schedule","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["not reached this session; would unlock: the Punjab Revenue Authority consolidation as in force 2025"]},
 {"oecd":"5121","tax":"Federal excise duty","statute":"Federal Excise Act 2005, First Schedule","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["not reached this session; would unlock: FBR's Federal Excise Act updated to 30 June 2025 (download1.fbr.gov.pk, same series as the Sales Tax Act)"]}])

# ---- R3 session 6 (2026-11-21): federal excise duty on cigarettes (Federal Excise Act 2005, First Schedule Table I
# S. Nos. 9-10), FBR consolidations as amended up to 30 June 2024 and up to 30 June 2025 (identical entries, so the
# whole of 2025); pk/law/pk_fed_act2005_upto_2024-06-30.pdf, pk_fed_act2005_upto_2025-06-30.pdf. Pre-change copy:
# tools/bak6/PK_cons.py.
S["doc"] = S["doc"] + r'''

**Federal excise duty (session 6, grade A)**: Federal Excise Act 2005 s. 3, First Schedule Table I (FBR consolidations
as amended up to 30 June 2024 and up to 30 June 2025: the entries below are the same in both). **S. No. 9**: locally
produced cigarettes whose on-pack printed retail price exceeds Rs 12,500 per thousand: Rs 16,500 per thousand;
**S. No. 10**: not exceeding Rs 12,500 per thousand: Rs 5,050 per thousand. The tier is chosen from the household's price
per stick (tax-inclusive, as printed on the pack). **S. No. 8** (imported cigarettes: 65 % of retail price or the S. No. 9
rate, whichever is higher) is not applied (the basket has no origin). **S. Nos. 4-6** aerated waters 20 % of retail price:
the non-alcoholic class mixes aerated waters with other drinks: not modelled. No duty on alcoholic beverages in the
First Schedule.'''
S["extra_lean"] = r'''/-- Federal Excise Act 2005, First Schedule Table I S. Nos. 9-10: rupees per thousand locally produced cigarettes,
chosen by the printed retail price per thousand (amount × 10^6 / quantity, quantity in thousandths of a stick). -/
def fedCigRate (s : Spend) : Int :=
  if s.quantity <= 0 then 0
  else if s.amount * 1000000 > 12500 * s.quantity then 16500 else 5050

def fedCig (s : Spend) : Int := divR .down (s.quantity * fedCigRate s) 1000000

def fedCharges (xs : List Spend) : List Charge :=
  (xs.filter fun s => s.good == .cigarettes).map fun s =>
    charge .excise "Federal excise duty (cigarettes)" s.amount id (fun _ => fedCig s) (event := s.good.name) (bearer := .consumer)
      (statute := s!"Federal Excise Act 2005 s. 3, First Schedule Table I S. No. {(if fedCigRate s == 16500 then 9 else 10 : Int)} (Rs {fedCigRate s} per thousand)")'''
S["extra_run"] = S.get("extra_run", []) + ["fedCharges g.consumption"]
S["extra_covers"] = S.get("extra_covers", []) + [".excise"]
S["unsupported"] = [u for u in S["unsupported"] if "federal excise duty" not in u[1]] + [
 [["cigarettes"], "federal excise duty: cigarettes taken as locally produced (First Schedule Table I S. Nos. 9-10); imported cigarettes (S. No. 8: 65 % of retail price or the S. No. 9 rate, whichever is higher) not distinguished; a line without a quantity bears no duty"],
 [["nonAlcoholic"], "federal excise duty on aerated waters, 20 % of retail price (First Schedule Table I S. Nos. 4-6): not modelled (the class mixes aerated waters with other drinks)"],
 [["tobaccoOther"], "federal excise duty on other tobacco (S. Nos. 7, 8a-8d: per kg) not modelled"]]
S["guards"] = S["guards"] + [
 "fedCig { good := .cigarettes, amount := 400, quantity := 20000 } == 330",
 "fedCig { good := .cigarettes, amount := 200, quantity := 20000 } == 101",
 "fedCig { good := .cigarettes, amount := 400 } == 0"]
S["notes"] = S["notes"] + ["PK 5121: Federal Excise Act 2005 First Schedule Table I S. Nos. 9-10 (cigarettes), FBR consolidations to 30 June 2024 and 30 June 2025"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "5121"] + [
 {"oecd": "5121", "tax": "Federal excise duty on cigarettes (Rs 16,500 / 5,050 per thousand by printed retail price)",
  "statute": "Federal Excise Act 2005 s. 3, First Schedule Table I S. Nos. 9-10",
  "dated": "FBR consolidations as amended up to 30 June 2024 and up to 30 June 2025 (entries identical): all of 2025",
  "grade": "A", "kernel_parts": ["Family", "charge"],
  "unsupported": ["imported cigarettes (S. No. 8) not distinguished", "aerated waters 20 % of retail price not modelled (class mix)", "other tobacco per kg not modelled"]}]
