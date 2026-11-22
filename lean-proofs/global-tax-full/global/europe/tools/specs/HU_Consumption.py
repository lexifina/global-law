S = {'cc': 'HU', 'fam': 'Consumption', 'family_name': '5111 Általános forgalmi adó', 'doc': '# HU 2025: Általános forgalmi adó (5111); excises not modelled in this pass\n\nSource: 2007. évi CXXVII. törvény az általános forgalmi adóról, net.jogtar.hu (Wolters Kluwer, private publisher of the consolidated text; njt.hu reset the connection), `hu/law/afa.html`; sha256 in `law/SHA256SUMS`.\n* 82. § (1): "Az adó mértéke az adó alapjának 27 százaléka"\n* (2) "A 3. számú mellékletben felsorolt termékek, szolgáltatások esetében ... 5 százaléka"\n* (3) "A 3/A. számú mellékletben ... 18 százaléka"\n', 'vat': {'name': 'Általános forgalmi adó', 'standard': 2700, 'threshold': 0, 'statute': '2007. évi CXXVII. törvény 82. § (1) 27 %, (2) 5 % (3. melléklet), (3) 18 % (3/A. melléklet); 85.-86. § (mentes)', 'classes': {'medicines': 'superReduced', 'books': 'superReduced', 'newspapers': 'superReduced', 'restaurants': 'superReduced', 'hotels': 'reduced', 'health': 'exempt', 'education': 'exempt', 'financial': 'exempt', 'insurance': 'exempt', 'rent': 'exempt'}, 'reduced': 1800, 'superReduced': 500}, 'notes': ['HU 5111: consolidated text (jogtar), current'], 'unsupported': [('g.consumption.any (fun s => s.good == .food)', 'food at 27 %; milk, eggs, pork, poultry and other 3. melléklet foods are 5 %'), ('g.entity == .company', 'alanyi adómentesség (small-business exemption, 188. §) not read: no threshold applied'), ('g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)', 'excise (Jövedéki adóról szóló 2016. évi LXVIII. törvény) not modelled in this pass')], 'guards': ['vat.embedded { good := .clothing, amount := 12700 } == 2700', 'vat.embedded { good := .hotels, amount := 11800 } == 1800', 'vat.embedded { good := .medicines, amount := 10500 } == 500'], 'taxes': [{'oecd': '5111', 'tax': 'Általános forgalmi adó', 'statute': '2007. évi CXXVII. törvény 82. § (1) 27 %, (2) 5 % (3. melléklet), (3) 18 % (3/A. melléklet); 85.-86. § (mentes)', 'dated': 'consolidated text (jogtar), current', 'grade': 'B', 'kernel_parts': ['Vat'], 'unsupported': ['food at 27 %; milk, eggs, pork, poultry and other 3. melléklet foods are 5 %', 'alanyi adómentesség (small-business exemption, 188. §) not read: no threshold applied']}, {'oecd': '5121', 'tax': 'Excise duties', 'statute': 'Jövedéki adóról szóló 2016. évi LXVIII. törvény', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'unsupported': ["not read in the P1 pass: would unlock with the act's 2025 rate articles"]}]}

# ---- FT review (2026-11-21, second pass): daily newspapers 0 % (82. § (4), 3/B. melléklet) and accommodation 5 % ----
S["doc"] += r'''
## FT review (2026-11-21, second pass): daily newspapers and commercial accommodation (ftd_ec_tedb_vat_2025 dev failures)
Same text (`hu/law/afa.txt`, net.jogtar.hu, with its amendment notes in `afa.html`):
* **82. § (4)**: "A 3/B. számú mellékletben felsorolt termékek esetében az adó mértéke az adó alapjának 0 százaléka."
  **3/B. számú melléklet 1.**: "Napilap (hetenként legalább négyszer megjelenő kiadvány)" (vtsz. 4902-ből); inserted
  by 2023. évi LIX. törvény 68. §, 3. melléklet, in force from 2024-01-01 (the transitional rule: "a 3/B. számú
  mellékletben foglalt táblázat 1. pontját ... 2024. január 1-jére vagy azt követő időpontra esik"). The household's
  `newspapers` is read as daily newspapers; periodicals ("Folyóirat, más újság", 3. melléklet I. 16.) stay 5 %.
  Items 2-3 of 3/B (prescription-only medicines) were inserted by 2026. évi XL. törvény from 2026-09-01: not 2025.
* **82. § (2)** with **3. melléklet II. rész 5.**: "Kereskedelmi szálláshely-szolgáltatás" at 5 % (established by
  2018. évi XLI. törvény 88. §, 10. melléklet); the model had accommodation at 18 % (3/A., whose II. 1. is repealed).
'''
S["vat"]["classes"].update({"newspapers": "zero", "hotels": "superReduced"})
_hu_st = "2007. évi CXXVII. törvény 82. § (1) 27 %, (2) 5 % (3. melléklet, II. 5. szálláshely), (3) 18 % (3/A. melléklet), (4) 0 % (3/B. melléklet 1. napilap, from 2024-01-01); 85.-86. § (mentes)"
S["vat"]["statute"] = _hu_st
for _t in S["taxes"]:
    if _t["oecd"] == "5111":
        _t["statute"] = _hu_st
        _t["unsupported"] = _t["unsupported"] + ["newspapers read as daily newspapers (0 %, 3/B. 1.); periodicals 5 % (3. melléklet I. 16.) not distinguished"]
S["unsupported"] = S["unsupported"] + [("g.consumption.any (fun s => s.good == .newspapers)", "newspapers read as daily newspapers (0 %, 3/B. 1.); periodicals 5 % (3. melléklet I. 16.) not distinguished")]
S["guards"] = [g for g in S["guards"] if ".hotels" not in g] + [
    "vat.embedded { good := .hotels, amount := 10500 } == 500", "vat.embedded { good := .newspapers, amount := 10500 } == 0",
    "vat.embedded { good := .restaurants, amount := 10500 } == 500", "vat.embedded { good := .transport, amount := 12700 } == 2700"]

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
