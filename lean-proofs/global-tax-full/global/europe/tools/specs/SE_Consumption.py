S = dict(cc="SE", fam="Consumption", family_name="5111 mervärdesskatt",
doc=r'''# Sweden 2025: mervärdesskatt (5111); excises not read

Source: mervärdesskattelag (2023:200), Riksdagen text of SFS 2023:200 (`se/law/ml2023.html`, current text
"Ändrad: t.o.m. SFS 2026:1025" with the amendment notes; sha256 in `law/SHA256SUMS`): grade B (the 2025 wording is
read through the amendment notes; 2026 changes are marked "Lag (2026:119)").
* **9 kap.**: "Normalskattesats - 25 procent"; "Reducerad skattesats - 12 procent": food ("sådana livsmedel som avses i
  artikel 2 i EU:s livsmedelsförordning", except water and "spritdrycker, vin och starköl"), "rumsuthyrning i
  hotellrörelse", "restaurang- och cateringtjänster"; 6 % for books, newspapers and passenger transport.
* **18 kap.** exemption for small businesses whose turnover "inte överstiger 120 000 kronor under kalenderåret".
''',
vat=dict(name="Mervärdesskatt", standard=2500, reduced=1200, superReduced=600, threshold=120000,
  statute="ML (2023:200) 9 kap. (25 %, 12 %, 6 %); 10 kap. (undantag); 18 kap. (120 000 kronor)",
  classes={"food": "reduced", "nonAlcoholic": "reduced", "hotels": "reduced", "restaurants": "reduced",
           "books": "superReduced", "newspapers": "superReduced", "transport": "superReduced",
           "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"}),
notes=["SE 5111: ML 2023:200, current text with amendment notes"],
unsupported=[("g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)", "energy tax, tobacco and alcohol taxes (LSE 1994:1776, LTS 1994:1563, LAS 2022:155) not read"),
  ("g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent)", "exemptions (10 kap.) taken from the act's structure, not quoted")],
guards=["vat.embedded { good := .clothing, amount := 125 } == 25",
        "vat.embedded { good := .food, amount := 112 } == 12",
        "vat.embedded { good := .books, amount := 106 } == 6",
        "vat.net { turnover := 120000, sales := [{ good := .other, net := 120000 }] } == 0"],
taxes=[{"oecd": "5111", "tax": "Mervärdesskatt", "statute": "ML (2023:200) 9, 10, 18 kap.", "dated": "current text (to SFS 2026:1025) with amendment notes", "grade": "B", "kernel_parts": ["Vat"], "unsupported": ["the 2025 SFS version not fetched as such"]},
 {"oecd": "5121", "tax": "Energiskatt, tobaksskatt, alkoholskatt", "statute": "LSE (1994:1776), LTS (1994:1563), LAS (2022:155)", "grade": "C", "status": "unsupported", "kernel_parts": [], "unsupported": ["not read in this pass; would unlock: the SFS texts with their 2025 rates (riksdagen data API)"]}])

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
