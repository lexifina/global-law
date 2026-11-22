S = dict(cc="IE", fam="Consumption", family_name="5111 VAT",
doc=r'''# Ireland 2025: value-added tax (5111); excise not read

Source: Value-Added Tax Consolidation Act 2010, Revised Act (Law Reform Commission, revisedacts.lawreform.ie,
"Updated to 1 August 2026"; `ie/law/vatca2010.html`, sha256 in `law/SHA256SUMS`). The revision is later than 2025;
the provisions used carry their own periods or were unchanged in 2025 (grade B: the dated 2025 revision not read).
* **s. 46 (1) (c)**: "13.5 per cent of the amount on which tax is chargeable in relation to goods or services of a kind
  specified in Schedule 3" (fuel, construction, hotel and restaurant services from 1 September 2023 ...); **(ca)** 9 %
  for Schedule 3 paragraphs 7(a), 7A, 12, 12A (newspapers, sporting facilities ...); **(caa)** "during the period from
  1 May 2022 to 31 December 2030, 9 per cent in relation to goods of a kind specified in paragraph 17(2) and (3) of
  Schedule 3" (electricity, gas); s. 46 (1) (a) standard 23 %; (b) zero rate, Schedule 2 (food, books, oral
  medicines, children's clothing). Exempt, Schedule 1 (financial, insurance, medical, education, passenger transport,
  letting of residential property).
* **s. 2 (1)**: "goods threshold" means "€85,000"; "services threshold" "€42,500".
''',
vat=dict(name="Value-added tax", standard=2300, reduced=1350, reduced2=900, threshold=42500,
  statute="VATCA 2010 s. 46 (1) (a) 23 %, (b) zero (Sch. 2), (c) 13.5 % (Sch. 3), (ca), (caa) 9 %; Sch. 1 (exempt); s. 2 (1) services threshold €42,500",
  classes={"food": "zero", "books": "zero", "medicines": "zero", "newspapers": "reduced2", "electricity": "reduced2", "gas": "reduced2",
           "hotels": "reduced", "restaurants": "reduced", "heatingOil": "reduced",
           "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt", "transport": "exempt"}),
notes=["IE 5111: VATCA 2010 revised (LRC, updated to 1 August 2026)"],
unsupported=[("g.entity == .company", "registration threshold taken as the services threshold €42,500 (goods: €85,000)"),
  ("g.consumption.any (fun s => s.good == .restaurants)", "restaurant and catering at 13.5 %; the 9 % period from 26 November 2025 (s. 46 (1) (cac)) not applied"),
  ("g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)", "excise (Finance Act 1999 Part 2 mineral oil tax, tobacco products tax, alcohol products tax) not read")],
guards=["vat.embedded { good := .clothing, amount := 123 } == 23",
        "vat.embedded { good := .hotels, amount := 1135 } == 135",
        "vat.embedded { good := .electricity, amount := 109 } == 9",
        "vat.embedded { good := .food, amount := 100 } == 0",
        "vat.net { turnover := 42500, sales := [{ good := .other, net := 42500 }] } == 0"],
taxes=[{"oecd": "5111", "tax": "Value-added tax", "statute": "VATCA 2010 s. 2 (1), s. 46 (1), Sch. 1-3", "dated": "Revised Act updated to 1 August 2026 (provisions with their own periods)", "grade": "B", "kernel_parts": ["Vat"], "unsupported": ["the 2025 revision not read", "Schedules item by item", "goods threshold €85,000"]},
 {"oecd": "5121", "tax": "Excise (mineral oil, tobacco, alcohol products tax)", "statute": "Finance Act 1999 Part 2; Finance Act 2001 Part 2; Finance Act 2003 Part 2", "grade": "C", "status": "unsupported", "kernel_parts": [], "unsupported": ["not read in this pass; would unlock: the revised Finance Acts' rate schedules (revisedacts.lawreform.ie) dated 2025"]}])

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
