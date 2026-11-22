S = {'cc': 'IT', 'fam': 'Consumption', 'family_name': '5111 Imposta sul valore aggiunto', 'doc': '# IT 2025: Imposta sul valore aggiunto (5111); excises not modelled in this pass\n\nSource: DPR 26 ottobre 1972 n. 633, Normattiva (official) multivigente text "!vig=2025-07-01" (`it/law/dpr633_art16.html`); sha256 in `law/SHA256SUMS`.\n* art. 16: "L\'aliquota dell\'imposta è stabilita nella misura del ventidue per cento"\n* "L\'aliquota è ridotta al quattro, al cinque e al dieci per cento per le operazioni che hanno per oggetto i beni e i servizi elencati, rispettivamente, nella parte II, nella parte II-bis e nella parte III dell\'allegata tabella A"\n', 'vat': {'name': 'Imposta sul valore aggiunto', 'standard': 2200, 'threshold': 0, 'statute': 'DPR 633/1972 art. 16 (22 %; 4, 5, 10 % per tabella A parti II, II-bis, III); art. 10 (esenzioni)', 'classes': {'food': 'reduced', 'water': 'reduced', 'medicines': 'reduced', 'hotels': 'reduced', 'restaurants': 'reduced', 'transport': 'reduced', 'electricity': 'reduced', 'books': 'superReduced', 'newspapers': 'superReduced', 'health': 'exempt', 'education': 'exempt', 'financial': 'exempt', 'insurance': 'exempt', 'rent': 'exempt'}, 'reduced': 1000, 'reduced2': 500, 'superReduced': 400}, 'notes': ['IT 5111: Normattiva vigente al 2025-07-01'], 'unsupported': [('g.consumption.any (fun s => s.good == .food)', 'food at 10 % (tabella A parte III); bread, milk, fresh produce and other parte II items are 4 %: tabella A not read item by item'), ('g.entity == .company', 'no VAT registration threshold (the regime forfettario is an income-tax regime, not modelled)'), ('g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)', 'excise (D.Lgs. 26 ottobre 1995 n. 504 (testo unico accise)) not modelled in this pass')], 'guards': ['vat.embedded { good := .clothing, amount := 12200 } == 2200', 'vat.embedded { good := .food, amount := 11000 } == 1000', 'vat.embedded { good := .books, amount := 10400 } == 400'], 'taxes': [{'oecd': '5111', 'tax': 'Imposta sul valore aggiunto', 'statute': 'DPR 633/1972 art. 16 (22 %; 4, 5, 10 % per tabella A parti II, II-bis, III); art. 10 (esenzioni)', 'dated': 'Normattiva vigente al 2025-07-01', 'grade': 'B', 'kernel_parts': ['Vat'], 'unsupported': ['food at 10 % (tabella A parte III); bread, milk, fresh produce and other parte II items are 4 %: tabella A not read item by item', 'no VAT registration threshold (the regime forfettario is an income-tax regime, not modelled)']}, {'oecd': '5121', 'tax': 'Excise duties', 'statute': 'D.Lgs. 26 ottobre 1995 n. 504 (testo unico accise)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'unsupported': ["not read in the P1 pass: would unlock with the act's 2025 rate articles"]}]}

# ---- pass 2 (R1 Europe, 2026-11-21): accise from the TUA as in force 2025 ----
S["imports"] = ["TaxKernel.Global2"]
S["family_name"] = "5111 IVA, 5121 accise"
S["doc"] += r'''
## Accise (5121), pass 2
Sources: D.Lgs. 26 ottobre 1995 n. 504 (TUA), normattiva Akoma Ntoso export `vigente al 2025-07-01`
(`it/law/tua504_akn20250701.xml`), and the Decreto MEF 14 maggio 2025 (G.U. 14/5/2025 n. 110, 25A02968,
`it/law/dm20250514_accise.html`); sha256 in `law/SHA256SUMS`.
* **DM 14 maggio 2025**, premise: "l'aliquota di accisa sulla benzina e' pari a euro 728,40 per mille litri e quella
  dell'aliquota di accisa sul gasolio impiegato come carburante e' pari a euro 617,40"; art. 1: from the day after
  publication (15.5.2025) petrol "ridotta di 1,50 centesimi di euro per litro", diesel "aumentata di 1,50 centesimi";
  art. 2 c. 1 (TUA All. I, AGGIORNAMENTO (130)): "a) benzina: euro 713,40 per mille litri; b) gasolio usato come
  carburante: euro 632,40 per mille litri".
* **TUA art. 39-octies c. 3**: cigarettes "a) un importo specifico fisso ... a decorrere dall'anno 2025, in 29,50 euro
  per 1.000 sigarette; b) ... l'aliquota di base, di cui alla voce "Tabacchi lavorati", lettera c), dell'allegato I, al
  prezzo di vendita al pubblico"; All. I "c) sigarette 49,50 per cento"; **c. 10** "non puo' essere inferiore a euro
  90 per mille sigarette".
* **Birra**: L. 30 dicembre 2021 n. 234 art. 1 c. 986 (as amended by D.L. 198/2022), All. I AGGIORNAMENTO (114):
  "a decorrere dal 1° gennaio 2024, in euro 2,99 per ettolitro e per grado-Plato". **Vino**: All. I "Vino: lire zero".
* Not modelled: alcole etilico. All. I prints 765,44 EUR per hl anidro; D.L. 104/2013 art. 25 c. 3 b) set 1019,21
  from 2015; the rate actually applied since 2015 comes from an ADM determinazione that is not in normattiva (not read).
'''
S["lean"] = (S.get("lean") or "") + r'''
/-- TUA All. I, benzina, before the DM 14 maggio 2025 (its premise: 728,40 EUR per 1 000 l). -/
def petrolTo : ExciseRule := { good := .petrol, name := "Accisa sulla benzina", perUnitNum := 72840, perUnitDen := 100000,
  validTo := "2025-05-15", statute := "D.Lgs. 504/1995 All. I (benzina 728,40 EUR / 1 000 l, DM 14.5.2025 premessa), to 14.5.2025" }
def petrolFrom : ExciseRule := { good := .petrol, name := "Accisa sulla benzina", perUnitNum := 71340, perUnitDen := 100000,
  validFrom := "2025-05-15", statute := "D.Lgs. 504/1995 All. I; DM 14.5.2025 art. 2 c. 1 a) (713,40 EUR / 1 000 l from 15.5.2025)" }
def dieselTo : ExciseRule := { good := .diesel, name := "Accisa sul gasolio usato come carburante", perUnitNum := 61740, perUnitDen := 100000,
  validTo := "2025-05-15", statute := "D.Lgs. 504/1995 All. I (gasolio 617,40 EUR / 1 000 l, DM 14.5.2025 premessa), to 14.5.2025" }
def dieselFrom : ExciseRule := { good := .diesel, name := "Accisa sul gasolio usato come carburante", perUnitNum := 63240, perUnitDen := 100000,
  validFrom := "2025-05-15", statute := "D.Lgs. 504/1995 All. I; DM 14.5.2025 art. 2 c. 1 b) (632,40 EUR / 1 000 l from 15.5.2025)" }
def cigarettes : ExciseRule := { good := .cigarettes, name := "Accisa sui tabacchi lavorati (sigarette)", perUnitNum := 2950,
  perUnitDen := 100000, adValoremBp := 4950, minNum := 90, minDen := 1000,
  statute := "D.Lgs. 504/1995 art. 39-octies c. 3 (29,50 EUR / 1 000 + 49,50 % of the retail price, All. I c)), c. 10 (at least 90 EUR / 1 000)" }
def beer : ExciseRule := { good := .beer, name := "Accisa sulla birra", perPlatoNum := 299, perPlatoDen := 10000,
  statute := "D.Lgs. 504/1995 All. I; L. 234/2021 art. 1 c. 986 (2,99 EUR per hl and degree Plato from 2024)" }
def rules : List ExciseRule := [petrolTo, petrolFrom, dieselTo, dieselFrom, cigarettes, beer]
'''
S["extra_run"] = ["exciseRuleCharges rules g"]; S["extra_covers"] = [".excise"]
S["unsupported"] = [u for u in S["unsupported"] if "excise" not in u[1]] + [
  ("g.consumption.any (fun s => s.good == .spirits)", "accisa sull'alcole etilico not modelled: the rate applied in 2025 is set by an ADM determinazione not in normattiva (All. I prints 765,44; D.L. 104/2013 art. 25 c. 3 b) 1019,21 from 2015)"),
  ("g.consumption.any (fun s => s.good == .beer)", "accisa sulla birra by the line's \"platoBp\" (degree Plato x 100); a beer line without it bears none"),
  ("g.consumption.any (fun s => s.good == .cigarettes)", "cigarettes: onere fiscale minimo (art. 39-octies c. 6-8, 98,80 % of excise + VAT at the PMP-sigarette) not applied; the retail price is the line's amount"),
  ("g.consumption.any (fun s => s.good == .petrol || s.good == .diesel)", "fuel: undated lines are split 134/365 at the rate before and 231/365 after 15.5.2025; regional surcharges and the 2026 riallineamento (D.Lgs. 43/2025) not applied")]
S["notes"] = S.get("notes", []) + ["IT 5121: TUA vigente 2025-07-01 (normattiva AKN), DM 14.5.2025; vino lire zero (All. I)"]
S["guards"] = S["guards"] + [
  "petrolTo.dutyOn { good := .petrol, amount := 1800, quantity := 1000000 } {} == 728",
  "petrolFrom.dutyOn { good := .petrol, amount := 1800, quantity := 1000000 } {} == 713",
  "dieselTo.dutyOn { good := .diesel, amount := 1700, quantity := 1000000 } {} == 617",
  "dieselFrom.dutyOn { good := .diesel, amount := 1700, quantity := 1000000 } {} == 632",
  "-- 1 000 cigarettes at 400 EUR: 29,50 + 198,00 (rounded down); at 100 EUR: 29,50 + 49,50 = 79 < 90 (c. 10 binds)",
  "cigarettes.dutyOn { good := .cigarettes, amount := 400, quantity := 1000000 } {} == 227",
  "cigarettes.dutyOn { good := .cigarettes, amount := 100, quantity := 1000000 } {} == 90",
  "beer.dutyOn { good := .beer, amount := 300, quantity := 100000 } { platoBp := 1200 } == 35"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "5121"] + [
 {"oecd": "5121", "tax": "Accisa sui prodotti energetici (benzina, gasolio carburante)", "statute": "D.Lgs. 504/1995 All. I; DM 14 maggio 2025 art. 1-2", "dated": "normattiva vigente 2025-07-01; two periods (to 14.5.2025: 728,40 / 617,40; from 15.5.2025: 713,40 / 632,40 EUR per 1 000 l)", "grade": "A", "kernel_parts": ["ExciseRule (validFrom/validTo, kernel 2.1)"], "unsupported": ["GPL, metano, heating uses", "D.Lgs. 43/2025 2026 changes (outside 2025)"]},
 {"oecd": "5121", "tax": "Accisa sui tabacchi lavorati (sigarette)", "statute": "D.Lgs. 504/1995 art. 39-octies c. 3, 10; All. I Tabacchi lavorati c)", "dated": "normattiva vigente 2025-07-01 (29,50 EUR / 1 000 'a decorrere dall'anno 2025')", "grade": "B", "kernel_parts": ["ExciseRule (specific + ad valorem + minimum)"], "unsupported": ["onere fiscale minimo (c. 6-8) needs the PMP-sigarette", "other tobacco products"]},
 {"oecd": "5121", "tax": "Accisa sulla birra", "statute": "D.Lgs. 504/1995 All. I; L. 234/2021 art. 1 c. 986", "dated": "2,99 EUR per hl and degree Plato from 1.1.2024", "grade": "A", "kernel_parts": ["ExciseRule (per degree Plato, kernel 2.1)"], "unsupported": ["small breweries"]},
 {"oecd": "5121", "tax": "Accisa sul vino", "statute": "D.Lgs. 504/1995 All. I (Vino: lire zero)", "dated": "normattiva vigente 2025-07-01", "grade": "A", "kernel_parts": [], "status": "rate zero (cited)", "unsupported": []},
 {"oecd": "5121", "tax": "Accisa sull'alcole etilico", "statute": "D.Lgs. 504/1995 All. I; D.L. 104/2013 art. 25 c. 3", "grade": "C", "status": "unsupported", "kernel_parts": [], "tried": "normattiva TUA vigente 2025-07-01: All. I prints 765,44 EUR/hl anidro, D.L. 104/2013 art. 25 c. 3 b) 1019,21 from 2015; the rate applied in 2025 rests on an ADM determinazione not in normattiva", "unsupported": ["would unlock: the ADM determinazione setting the alcohol rate (adm.gov.it, Wayback)"]}]

S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")


# ---- FT review (2026-11-21, third pass): heating oil (ftd_ec_oilbulletin_excise_2025 dev; IMPROVE_FT D5-3) ----
S["doc"] += r'''
## FT review (2026-11-21, third pass): heating oil
Same normattiva AKN text (vigente 2025-07-01). All. I prints "Oli da gas o gasolio: ... usato come combustibile per
riscaldamento: lire 747.470 per mille litri" with no update note; the D.L. 201/2011 art. 15 c. 1 (normattiva, read)
re-sets only benzina, gasolio carburante, GPL and metano carburante. The euro rate applied in 2025 comes from acts not
in the consolidated Allegato (as for alcole etilico above): not read. Heating oil is listed as grade C, not booked at 0.
'''
S["unsupported"] = S["unsupported"] + [
  ("g.consumption.any (fun s => s.good == .heatingOil)", "5121 heating oil (gasolio per riscaldamento): not modelled (grade C: All. I prints lire 747.470 / 1 000 l; the 2025 euro rate is set outside the consolidated Allegato, not read)")]

# ---- pass 18 (R1 Europe, 2026-11-21): item-5 leftovers, audit, GR ENFIA, vehicles (tools/p18_rows.py) ----
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
p18_rows(S)
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
