S = dict(cc="ES", fam="Consumption", family_name="5111 IVA, 5121 IIEE",
doc=r'''# Spain 2025 (territorio común): Impuesto sobre el Valor Añadido (5111) and Impuestos Especiales (5121)

Sources: BOE legislación consolidada (`es/law/liva.html` Ley 37/1992, `es/law/liiee.html` Ley 38/1992, current text
"Última actualización publicada el 07/10/2026"; sha256 in `law/SHA256SUMS`). Each provision used carries BOE's
amendment notes, which date the 2025 wording: art. 91 last amended by Ley 7/2024 and, "con efectos desde el 1 de
enero de 2025", by RDL 4/2024; art. 60 "con efectos desde el 1 de enero de 2025" by Ley 7/2024 (disp. final 2.9);
arts. 39 and 50 unchanged since 2016 and 2013.
* **LIVA art. 90 Uno**: "El Impuesto se exigirá al tipo del 21 por ciento"; **art. 91 Uno** 10 %: 1.1.º food
  products, 1.4.º "Las aguas aptas para la alimentación humana", 2.1.º "Los transportes de viajeros", 2.2.º "Los
  servicios de hostelería, acampamento y balneario, los de restaurantes", 2.6.º entry to museums, cinemas, theatres;
  **art. 91 Dos** 4 %: 1.1.º basic foods (bread, milk, eggs, fruit, vegetables ...), 1.2.º "Los libros, periódicos y
  revistas", 1.3.º "Los medicamentos de uso humano". Exemptions art. 20 Uno (medical care, education, insurance,
  financial, residential letting).
* **LIIEE art. 50.1**: epígrafe 1.2.2 "Las demás gasolinas sin plomo: 400,69 euros por 1.000 litros de tipo general y
  72 euros por 1.000 litros de tipo especial"; epígrafe 1.3 "Gasóleos para uso general: 307 euros ... y 72 euros".
  **Art. 60.1 epígrafe 2**: cigarettes "Tipo proporcional: 48,5 por 100. Tipo específico: 33,50 euros por cada 1.000
  cigarrillos. El importe del impuesto no puede ser inferior al tipo único de 150 euros por cada 1.000 cigarrillos."
  **Art. 39**: "El impuesto se exigirá al tipo de 958,94 euros por hectolitro de alcohol puro".
''',
vat=dict(name="Impuesto sobre el Valor Añadido", standard=2100, reduced=1000, superReduced=400, threshold=0,
  statute="Ley 37/1992 art. 90 (21 %), art. 91 Uno (10 %), Dos (4 %); art. 20 Uno (exenciones)",
  classes={"food": "reduced", "water": "reduced", "transport": "reduced", "hotels": "reduced", "restaurants": "reduced",
           "books": "superReduced", "newspapers": "superReduced", "medicines": "superReduced",
           "health": "exempt", "education": "exempt", "insurance": "exempt", "financial": "exempt", "rent": "exempt"}),
excise=[dict(good="petrol", name="Impuesto sobre Hidrocarburos (gasolina)", num=47269, den=100000, statute="Ley 38/1992 art. 50.1 epígrafe 1.2.2: 400,69 + 72 EUR / 1.000 l"),
        dict(good="diesel", name="Impuesto sobre Hidrocarburos (gasóleo)", num=379, den=1000, statute="Ley 38/1992 art. 50.1 epígrafe 1.3: 307 + 72 EUR / 1.000 l"),
        dict(good="cigarettes", name="Impuesto sobre las Labores del Tabaco (cigarrillos)", num=335, den=10000, adv=4850, minNum=150, minDen=1000, statute="Ley 38/1992 art. 60.1 epígrafe 2: 48,5 % + 33,50 EUR / 1.000, mínimo 150 EUR / 1.000"),
        dict(good="spirits", name="Impuesto sobre el Alcohol y Bebidas Derivadas", num=95894, den=10000, pure=True, statute="Ley 38/1992 art. 39: 958,94 EUR / hl de alcohol puro")],
notes=["ES 5111/5121: territorio común (Canarias IGIC, Ceuta and Melilla IPSI not modelled)"],
unsupported=[("g.consumption.any (fun s => s.good == .food)", "food at 10 % (art. 91 Uno 1.1.º); the basic foods of art. 91 Dos 1.1.º (bread, milk, eggs, fruit, vegetables, oils ...) are 4 %"),
  ("g.consumption.any (fun s => s.good == .beer)", "Impuesto sobre la Cerveza (by degree Plato, art. 26) not modelled"),
  ("g.consumption.any (fun s => s.good == .recreation)", "cultural entries at 10 % (art. 91 Uno 2.6.º) not separated from recreation (21 %)"),
  ("g.consumption.any (fun s => s.good == .wine)", "Impuesto sobre el Vino y Bebidas Fermentadas not modelled (its article not read)")],
guards=["vat.embedded { good := .clothing, amount := 121 } == 21",
        "vat.embedded { good := .food, amount := 110 } == 10",
        "vat.embedded { good := .books, amount := 104 } == 4",
        "excise.duty { good := .petrol, amount := 1600, quantity := 1000000 } == 472",
        "excise.duty { good := .diesel, amount := 1500, quantity := 1000000 } == 379",
        "-- 1 000 cigarettes at 200 EUR: 97 + 33 < 150 (the tipo único binds); at 400 EUR: 194 + 33",
        "excise.duty { good := .cigarettes, amount := 200, quantity := 1000000 } == 150",
        "excise.duty { good := .cigarettes, amount := 400, quantity := 1000000 } == 227",
        "excise.duty { good := .spirits, amount := 1500, quantity := 100000, abvBp := 4000 } == 383"],
taxes=[{"oecd": "5111", "tax": "Impuesto sobre el Valor Añadido", "statute": "Ley 37/1992 arts. 20 Uno, 90, 91", "dated": "BOE consolidado; art. 91 in its 2025 wording (Ley 7/2024, RDL 4/2024 from 1.1.2025)", "grade": "A", "kernel_parts": ["Vat"], "unsupported": ["4 % basic foods not separated from food", "recargo de equivalencia, régimen simplificado"]},
 {"oecd": "5121", "tax": "Impuesto sobre Hidrocarburos (petrol, diesel)", "statute": "Ley 38/1992 art. 50.1 epígrafes 1.2.2, 1.3", "dated": "BOE consolidado (unchanged since 2013)", "grade": "A", "kernel_parts": ["ExciseRate"], "unsupported": ["regional refunds, professional diesel refund"]},
 {"oecd": "5121", "tax": "Impuesto sobre las Labores del Tabaco (cigarettes)", "statute": "Ley 38/1992 art. 60.1 epígrafe 2", "dated": "BOE consolidado; Ley 7/2024 from 1.1.2025", "grade": "A", "kernel_parts": ["ExciseRate (minimum)"], "unsupported": ["cigars, fine-cut, other tobacco"]},
 {"oecd": "5121", "tax": "Impuesto sobre el Alcohol y Bebidas Derivadas", "statute": "Ley 38/1992 art. 39", "dated": "BOE consolidado", "grade": "A", "kernel_parts": ["ExciseRate (pure alcohol)"], "unsupported": ["productos intermedios (art. 32)"]},
 {"oecd": "5121", "tax": "Impuesto sobre la Cerveza", "statute": "Ley 38/1992 art. 26", "grade": "A", "status": "not modelled (kernel input: degree Plato)", "kernel_parts": [], "unsupported": ["per hl and degree Plato"]}])


# ---- FT review (2026-11-21, third pass): heating oil (ftd_ec_oilbulletin_excise_2025 dev; IMPROVE_FT D5-3) ----
S["doc"] += r'''
## FT review (2026-11-21, third pass): heating oil
Same BOE consolidated text (`es/law/liiee.txt`). **Ley 38/1992 art. 50.1, epígrafe 1.4**: "Gasóleos utilizables como
carburante en los usos previstos en el apartado 2 del artículo 54 y, en general, como combustible: 78,71 euros por
1.000 litros de tipo general y 18 euros por 1.000 litros de tipo especial" (96,71 euros, the two summed as for
epígrafes 1.2.2 and 1.3). The household's `heatingOil` is gasóleo used as combustible.
'''
S["excise"] = S["excise"] + [dict(good="heatingOil", name="Impuesto sobre Hidrocarburos (gasóleo de calefacción)", num=9671, den=100000,
    statute="Ley 38/1992 art. 50.1 epígrafe 1.4: 78,71 + 18 EUR / 1.000 l")]
S["guards"] = S["guards"] + ["excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 96"]
for _t in S["taxes"]:
    if _t.get("oecd") == "5121" and "Hidrocarburos" in _t.get("tax", ""):
        _t["statute"] = _t.get("statute", "") + "; epígrafe 1.4 (gasóleo combustible)"

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
