S = {'cc': 'HR', 'fam': 'Consumption', 'family_name': '5111 Porez na dodanu vrijednost', 'doc': '# HR 2025: Porez na dodanu vrijednost (5111); excises not modelled in this pass\n\nSource: Narodne novine (official gazette): Zakon o izmjenama i dopunama Zakona o PDV-u NN 39/2022 (čl. 38 as replaced), NN 35/2024, NN 152/2024 (`hr/law/nn2022_39_478_pdv.html`, `nn2024_35_539_pdv.html`, `nn2024_152_2508_pdv.html`); no consolidated official text; sha256 in `law/SHA256SUMS`.\n* čl. 38 (1): "PDV se obračunava i plaća po stopi od 25%." (2): "po sniženoj stopi od 5% na isporuke ...: a) sve vrste kruha, b) sve vrste mlijeka ..., c) knjige ..., d) lijekove ..., j) jestiva ulja i masti ..., l) ... svježeg ili rashlađenog mesa ..., o) ... svježe ili rashlađene ribe ..., r) ... svježeg ili rashlađenog povrća ..., s) ... svježeg i suhog voća ..., t) ... svježih jaja"\n* čl. 38 (3): "po sniženoj stopi od 13% ...: a) usluge smještaja ..., b) novine i časopise ..., e) isporuku vode ..., f) isporuku električne energije ..., g) isporuku prirodnog plina i grijanja ..., l) pripremanje i usluživanje jela i slastica u ugostiteljskom objektu"\n* čl. 90 (1) (NN 152/2024): "čiji godišnji promet u tuzemstvu nije bio veći od 60.000,00 eura oslobođen je plaćanja PDV-a"\n', 'vat': {'name': 'Porez na dodanu vrijednost', 'standard': 2500, 'threshold': 60000, 'statute': 'Zakon o PDV-u čl. 38 st. 1-3 (25 %, 5 %, 13 %; NN 39/22), st. 4-5 (NN 35/24: to 31.3.2025); čl. 90 st. 1 (60.000,00 eura; NN 152/24)', 'classes': {'health': 'exempt', 'education': 'exempt', 'financial': 'exempt', 'insurance': 'exempt', 'rent': 'exempt', 'food': 'superReduced', 'books': 'superReduced', 'medicines': 'superReduced', 'hotels': 'reduced', 'newspapers': 'reduced', 'water': 'reduced', 'electricity': 'reduced', 'restaurants': 'reduced'}, 'reduced': 1300, 'superReduced': 500}, 'notes': ['HR 5111: NN 39/2022 as amended by NN 113/2022, 35/2024, 152/2024 (in force 1.1.2025)'], 'unsupported': [('g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance)', "exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"), ('g.consumption.any (fun s => s.good == .food)', 'food at 5 %: the staples of čl. 38 (2) (bread, milk, oils, fresh meat, fish, fruit, vegetables, eggs, baby food); other processed food is 25 %'), ('g.consumption.any (fun s => s.good == .heatingOil)', 'gas and district heating at 5 % to 31.3.2025 (st. 4-5), then 13 %: not a household category here'), ('g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)', 'excise (Zakon o trošarinama (not read)) not modelled in this pass')], 'guards': ['vat.embedded { good := .clothing, amount := 12500 } == 2500', 'vat.embedded { good := .hotels, amount := 11300 } == 1300', 'vat.embedded { good := .food, amount := 10500 } == 500', 'vat.net { turnover := 60000, sales := [{ good := .other, net := 60000 }] } == 0'], 'taxes': [{'oecd': '5111', 'tax': 'Porez na dodanu vrijednost', 'statute': 'Zakon o PDV-u čl. 38 st. 1-3 (25 %, 5 %, 13 %; NN 39/22), st. 4-5 (NN 35/24: to 31.3.2025); čl. 90 st. 1 (60.000,00 eura; NN 152/24)', 'dated': 'NN 39/2022 as amended by NN 113/2022, 35/2024, 152/2024 (in force 1.1.2025)', 'grade': 'A', 'kernel_parts': ['Vat'], 'unsupported': ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item", 'food at 5 %: the staples of čl. 38 (2) (bread, milk, oils, fresh meat, fish, fruit, vegetables, eggs, baby food); other processed food is 25 %', 'gas and district heating at 5 % to 31.3.2025 (st. 4-5), then 13 %: not a household category here']}, {'oecd': '5121', 'tax': 'Excise duties', 'statute': 'Zakon o trošarinama (not read)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'unsupported': ["not read in the P1 pass: would unlock with the act's 2025 rate articles"]}]}


# ---- FT review (2026-11-21, third pass): natural gas 5 % through 2025 (ftd_ec_tedb_vat_2025 dev; IMPROVE_FT D3-7) ----
S["doc"] += """
## FT review (2026-11-21, third pass): natural gas
**Zakon o izmjeni Zakona o PDV-u, NN 52/2025** (`hr/law/nn2025_52_673.html`, in force 30.3.2025), čl. 1: "u članku 38.
stavku 4. riječi: »31. ožujka 2025.« zamjenjuju se riječima: »31. ožujka 2026.«. U stavku 5. riječi: »31. ožujka 2025.«
zamjenjuju se riječima: »31. ožujka 2026.«." Čl. 38 st. 4 (NN 39/2022 wording, extended by NN 35/2024 and NN 52/2025):
"na isporuke prirodnog plina, uključujući naknade vezane uz tu isporuku ... PDV se obračunava i plaća po sniženoj stopi
od 5%". So natural gas bears 5 % for the whole of 2025 (the model gave the `gas` line the standard 25 %).
"""
S["vat"]["classes"]["gas"] = "superReduced"
S["unsupported"] = [(c, t.replace("gas and district heating at 5 % to 31.3.2025 (st. 4-5), then 13 %: not a household category here",
                                  "district heating at 5 % (st. 5, to 31.3.2026 by NN 52/2025): not a household category here"))
                    for c, t in S["unsupported"]]
S["guards"] = S["guards"] + ["vat.embedded { good := .gas, amount := 105 } == 5"]

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
