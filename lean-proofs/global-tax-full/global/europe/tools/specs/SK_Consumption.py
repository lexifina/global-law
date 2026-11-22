S = dict(cc="SK", fam="Consumption", family_name="5111 DPH, 5121 SDMO",
doc=r'''# Slovakia 2025: daň z pridanej hodnoty (5111), spotrebná daň z minerálneho oleja (5121)

Sources: Slov-Lex (official), static consolidations in force from 1 January 2025: zákon 222/2004 Z. z. o DPH
(`sk/law/dph_20250101.html`), zákon 98/2004 Z. z. o spotrebnej dani z minerálneho oleja
(`sk/law/akciza_mineral_20250101.html`); sha256 in `law/SHA256SUMS`.
* **§ 27 (1)**: "Základná sadzba dane na tovary a služby je 23 % zo základu dane"; (2) "Znížená sadzba dane 19 %" for
  goods in príloha č. 7 bod 1 and services in príloha č. 7a bod 1; (3) "Znížená sadzba dane 5 %" for príloha č. 7 body
  2 a 3, príloha č. 7a bod 2. The annexes are not in the consolidation file read: the reduced classes are not assigned.
* **§ 4 (1)**: registration when turnover "presiahla 50 000 eur".
* **Zákon 98/2004 § 7 (1)**: "a) motorový benzín ... 2710 12 41, 2710 12 45, 2710 12 49 514 eur/1 000 l"; "d) plynový
  olej ... 368 eur/1 000 l".
''',
vat=dict(name="Daň z pridanej hodnoty", standard=2300, reduced=1900, superReduced=500, threshold=50000,
  statute="zákon 222/2004 Z. z. § 27 (1) 23 %, (2) 19 %, (3) 5 %; § 4 (1) (50 000 eur)", classes={}),
excise=[dict(good="petrol", name="Spotrebná daň z minerálneho oleja (benzín)", num=514, den=1000, statute="zákon 98/2004 Z. z. § 7 (1) a): 514 eur / 1 000 l"),
        dict(good="diesel", name="Spotrebná daň z minerálneho oleja (plynový olej)", num=368, den=1000, statute="zákon 98/2004 Z. z. § 7 (1) d): 368 eur / 1 000 l")],
notes=["SK 5111/5121: Slov-Lex consolidations from 2025-01-01"],
unsupported=[("!g.consumption.isEmpty", "every basket line at 23 %: the 19 % and 5 % annexes (príloha č. 7, 7a) and the exemptions (§§ 28-42) not read"),
  ("g.consumption.any (fun s => s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)", "tobacco and alcohol duties (zákony 106/2004, 530/2011) not reached (Slov-Lex static file 404)")],
guards=["vat.embedded { good := .clothing, amount := 123 } == 23",
        "vat.net { turnover := 50000, sales := [{ good := .other, net := 50000 }] } == 0",
        "excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 514",
        "excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 368"],
taxes=[{"oecd": "5111", "tax": "Daň z pridanej hodnoty", "statute": "zákon 222/2004 Z. z. §§ 4, 27", "dated": "Slov-Lex znenie od 1. 1. 2025", "grade": "B", "kernel_parts": ["Vat"], "unsupported": ["19 % and 5 % annexes not read (all lines at 23 %)", "exemptions"]},
 {"oecd": "5121", "tax": "Spotrebná daň z minerálneho oleja", "statute": "zákon 98/2004 Z. z. § 7 (1) a), d)", "dated": "Slov-Lex znenie od 1. 1. 2025", "grade": "A", "kernel_parts": ["ExciseRate"], "unsupported": []},
 {"oecd": "5121", "tax": "Spotrebné dane z tabaku, liehu, piva, vína", "statute": "zákony 106/2004, 530/2011 Z. z.", "grade": "C", "status": "unsupported", "kernel_parts": [], "unsupported": ["static.slov-lex.sk answered 404 for these acts; would unlock: their 2025 consolidations"]}])


# ---- FT review (2026-11-21, third pass): heating oil (ftd_ec_oilbulletin_excise_2025 dev; IMPROVE_FT D5-3) ----
S["doc"] += r'''
## FT review (2026-11-21, third pass): heating oil
Slov-Lex znenie od 1. 1. 2025 (`sk/law/akciza_mineral_20250101.txt`; the rate section is printed there as **§ 6 (1)**,
the model's citations say § 7 (1)): "d) plynový olej kódu kombinovanej nomenklatúry 2710 19 43, 2710 19 46,
2710 19 47, 2710 19 48, 2710 20 11, 2710 20 16 a 2710 20 19 368 eur/1 000 l"; "e) vykurovací olej kódu kombinovanej
nomenklatúry 2710 19 62, 2710 19 66, 2710 19 67, 2710 20 32, 2710 20 38 a 2710 20 90 111,50 eura/1 000 kg". Gas oil
used as "palivo" (fuel for producing heat, § 3 (5)) has no rate of its own and no exemption (§ 10 (1) lists none for
heating; § 15 refunds only to tax warehouses and licensed user undertakings). The household's `heatingOil` (light
heating oil, gas oil by the kernel's reading) therefore bears the d) rate; heavy fuel oils of the e) codes (per kg) are
listed, not computed.
'''
S["excise"] = S["excise"] + [dict(good="heatingOil", name="Spotrebná daň z minerálneho oleja (plynový olej na vykurovanie)", num=368, den=1000,
    statute="zákon 98/2004 Z. z. § 6 (1) d) (znenie od 1. 1. 2025): 368 eur / 1 000 l plynového oleja; no heating rate or exemption for gas oil")]
S["unsupported"] = S["unsupported"] + [
  ("g.consumption.any (fun s => s.good == .heatingOil)", "heating oil read as gas oil (§ 6 (1) d), 368 eur / 1 000 l); a vykurovací olej of the e) codes (2710 19 62-67 ...) bears 111,50 eur / 1 000 kg instead (per kg: not computed)")]
S["guards"] = S["guards"] + ["excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 368"]

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
