S = {'cc': 'PL', 'fam': 'Property', 'doc': '# PL 2025: transfer duties on purchases (4400); recurrent property tax not modelled\n\nSource: ustawa o podatku od czynności cywilnoprawnych, tekst jednolity Dz.U. 2024 poz. 295 (Sejm ELI API, `pl/law/pcc_tj.pdf`); sha256 in `law/SHA256SUMS`.\n* art. 7 ust. 1 pkt 1 lit. a: "przy przeniesieniu własności nieruchomości, rzeczy ruchomych, prawa użytkowania wieczystego ... – 2%"\n', 'lean': 'def d0 : TransferDuty :=\n  { name := "Podatek od czynności cywilnoprawnych (sprzedaż nieruchomości)",\n    sched := Schedule.flat 200,\n    kinds := [.home, .realEstate, .land] }', 'families': [('4400 transfer duties', ['.transactions'], 'd0.charges g.purchases "ustawa o PCC art. 7 ust. 1 pkt 1 lit. a (2 %)"')], 'notes': ['PL 4400: t.j. Dz.U. 2024 poz. 295'], 'unsupported': [('!g.purchases.isEmpty', 'sales subject to VAT (new dwellings from developers) are outside PCC (art. 2 pkt 4): not separated; 2025 amendments not checked; the 6 % rate for multiple dwellings not modelled'), ('g.assets.any (·.kind.isRealEstate)', 'recurrent property tax (4100) not modelled')], 'guards': ['d0.amount { kind := .home, price := 200000 } == 4000', 'd0.amount { kind := .home, price := 2000000 } == 40000'], 'taxes': [{'oecd': '4400', 'tax': 'Podatek od czynności cywilnoprawnych (sprzedaż nieruchomości)', 'statute': 'ustawa o PCC art. 7 ust. 1 pkt 1 lit. a (2 %)', 'dated': 't.j. Dz.U. 2024 poz. 295', 'grade': 'B', 'kernel_parts': ['TransferDuty'], 'unsupported': ['sales subject to VAT (new dwellings from developers) are outside PCC (art. 2 pkt 4): not separated; 2025 amendments not checked; the 6 % rate for multiple dwellings not modelled']}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'local', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'unsupported': ["the default municipality's act and rate not read in the P5 pass; would unlock: the property-tax act and the reference municipality's rate (registry choice)"]}]}

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
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

# ---- local-tax framework pass (R1 Europe, 2026-11-22): LocalTax with the rate as input (tools/plfw_rows.py, tools/lfw_rows.json) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/plfw_rows.py")).read())
plfw_rows(S)
p6_finish(S)
