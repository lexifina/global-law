S = {'cc': 'MT', 'fam': 'Consumption', 'family_name': '5111 Value Added Tax', 'doc': '# MT 2025: Value Added Tax (5111); excises not modelled in this pass\n\nSource: Value Added Tax Act, Cap. 406, legislation.mt consolidated PDF (official; it lists amendments up to Act III of 2026 and Legal Notices of 2026, so the 2025 wording is read through an unchanged rate structure), `mt/law/cap406.pdf`; sha256 in `law/SHA256SUMS`.\n* art. 19: tax "at the rate of eighteen per cent of the taxable value of the supply"\n* Eighth Schedule: "The letting of or the provision of accommodation in any premises ... 7%"; "2. The supply of electricity. 5%"\n', 'vat': {'name': 'Value Added Tax', 'standard': 1800, 'threshold': 0, 'statute': 'VAT Act (Cap. 406) art. 19 (18 %); Eighth Schedule (7 % accommodation, 5 % electricity ...); Fifth Schedule (exemptions)', 'classes': {'hotels': 'reduced', 'electricity': 'superReduced'}, 'reduced': 700, 'superReduced': 500}, 'notes': ['MT 5111: legislation.mt consolidation (to 2026)'], 'unsupported': [('g.consumption.any (fun s => s.good == .food || s.good == .medicines || s.good == .books || s.good == .newspapers || s.good == .transport || s.good == .restaurants)', 'food, medicines (zero-rated, Fifth Schedule Part One), books (5 %), transport and restaurant rates not read item by item: taken at 18 %'), ('g.entity == .company', 'small undertaking exemption (art. 11) not read: no threshold applied'), ('g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)', 'excise (Excise Duty Act (Cap. 382)) not modelled in this pass')], 'guards': ['vat.embedded { good := .clothing, amount := 11800 } == 1800', 'vat.embedded { good := .hotels, amount := 10700 } == 700', 'vat.embedded { good := .electricity, amount := 10500 } == 500'], 'taxes': [{'oecd': '5111', 'tax': 'Value Added Tax', 'statute': 'VAT Act (Cap. 406) art. 19 (18 %); Eighth Schedule (7 % accommodation, 5 % electricity ...); Fifth Schedule (exemptions)', 'dated': 'legislation.mt consolidation (to 2026)', 'grade': 'B', 'kernel_parts': ['Vat'], 'unsupported': ['food, medicines (zero-rated, Fifth Schedule Part One), books (5 %), transport and restaurant rates not read item by item: taken at 18 %', 'small undertaking exemption (art. 11) not read: no threshold applied']}, {'oecd': '5121', 'tax': 'Excise duties', 'statute': 'Excise Duty Act (Cap. 382)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'unsupported': ["not read in the P1 pass: would unlock with the act's 2025 rate articles"]}]}

# ---- FT review (2026-11-21): Fifth Schedule exemptions for food, medicines, scheduled passenger transport, water ----
S["doc"] += r'''
## FT review (2026-11-21, second pass): Fifth Schedule exemptions (ftd_ec_tedb_vat_2025 dev failures)
Same consolidation (`mt/law/cap406.pdf`, `cap406.txt`), Fifth Schedule:
* **Part One "Exemptions with credit"** (art. 2 "exempt with credit supply": no tax charged, input tax deductible):
  item 9 "The supply of food for human consumption, excluding food supplied in the course of catering."; item 10 "The
  supply of pharmaceutical goods."; item 11 "The supply of: (a) transport by scheduled bus service consisting of trips
  on scheduled routes; (b) scheduled inter-island sea transport of passengers ...; (e) scheduled passenger transport
  services by means of public lift". The household's `transport` is read as scheduled public passenger transport.
* **Part Two "Exemptions without credit"**, item 15 "The supply of water services by a public authority." (the
  household's `water` is the public supply): no tax charged on the supply.
'''
S["vat"]["classes"].update({"food": "zero", "medicines": "zero", "transport": "zero", "water": "exempt"})
_mt_old = 'food, medicines (zero-rated, Fifth Schedule Part One), books (5 %), transport and restaurant rates not read item by item: taken at 18 %'
_mt_new = 'books (5 %), newspapers and restaurant rates not read item by item: taken at 18 %; transport read as scheduled passenger transport (Fifth Schedule Part One item 11; taxis and other transport are taxable)'
S["unsupported"] = [(c.replace("s.good == .food || s.good == .medicines || ", "").replace(" || s.good == .transport", " || s.good == .transport"), _mt_new) if u == _mt_old else (c, u) for c, u in S["unsupported"]]
for _t in S["taxes"]:
    if _t["oecd"] == "5111":
        _t["unsupported"] = [_mt_new if u == _mt_old else u for u in _t["unsupported"]]
        _t["statute"] = _t["statute"].replace("Fifth Schedule (exemptions)", "Fifth Schedule Part One items 9-11 (food, pharmaceutical goods, scheduled passenger transport: exempt with credit), Part Two item 15 (water by a public authority: exempt)")
S["vat"]["statute"] = S["vat"]["statute"].replace("Fifth Schedule (exemptions)", "Fifth Schedule Part One items 9-11 (food, pharmaceutical goods, scheduled passenger transport: exempt with credit), Part Two item 15 (water by a public authority: exempt)")
S["guards"] += ["vat.embedded { good := .food, amount := 11800 } == 0", "vat.embedded { good := .medicines, amount := 11800 } == 0",
                "vat.embedded { good := .transport, amount := 11800 } == 0", "vat.embedded { good := .water, amount := 11800 } == 0",
                "vat.embedded { good := .other, amount := 11800 } == 1800"]

# ---- pass 16 (R1 Europe, 2026-11-21): year-in-force audit (tools/p16_rows.py, tools/yif16_rows.json) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p16_rows.py")).read())
p16_rows(S)
p6_finish(S)

# ---- pass 17 (R1 Europe, 2026-11-21): kernel 2.7.0 items, audit follow-ups (tools/p17_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p16_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p17_rows.py")).read())
p17_rows(S)
p6_finish(S)

# ---- gap pass (R1 Europe, 2026-11-21): gap-closing pass (tools/pgap_rows.py, tools/gap_rows.json) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p16_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p17_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p18_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/pgap_rows.py")).read())
pgap_rows(S)
p6_finish(S)
