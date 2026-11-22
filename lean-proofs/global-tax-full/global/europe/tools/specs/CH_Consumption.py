S = dict(cc="CH", fam="Consumption", family_name="5111 MWST, 5121 MinöSt TSt AlkSt",
doc=r'''# Switzerland 2025: Mehrwertsteuer (5111) and the main federal excises (5121)

Sources: fedlex consolidations in force on 1 July 2025 (`ch/law/*.html`, sha256 in `law/SHA256SUMS`, URLs in
`law/ARCHIVE_INDEX.tsv`): MWSTG SR 641.20 (version 2025-03-31), TStG SR 641.31 (2025-01-01), MinöStG SR 641.61
(2025-01-01), AlkV SR 680.11 (2022-01-01, the last consolidation before 2025-07-01), AlkG SR 680 (2024-06-01).
* **MWSTG Art. 25 (1)**: "Die Steuer beträgt 8,1 Prozent (Normalsatz)"; **(2)** "Der reduzierte Steuersatz von 2,6
  Prozent findet Anwendung: a. auf der Lieferung folgender Gegenstände: 1. Wasser in Leitungen, 2. Lebensmittel nach
  dem Lebensmittelgesetz ..., mit Ausnahme alkoholischer Getränke, ... 8. Medikamente, 9. Zeitungen, Zeitschriften,
  Bücher"; **(4)** "Die Steuer auf Beherbergungsleistungen beträgt 3,8 Prozent (Sondersatz)".
* **Art. 21 (2)** exempt: Ziff. 2, 3 hospital and medical treatment, 11 education, 18 insurance, 19 money and capital
  transactions, 21 letting of immovable property. **Art. 10 (2) lit. a**: not liable if "weniger als 100 000 Franken
  Umsatz".
* **MinöStG Art. 12 (1)** and Anhang 1: petrol ("Benzin und seine Fraktionen", Treibstoff) 431.20 Fr., Dieselöl 458.70
  Fr. je 1000 l bei 15 °C; **Art. 12 (2)**: "Der Mineralölsteuerzuschlag beträgt 300 Franken je 1000 l bei 15 °C".
* **TStG** (cigarettes): "Die Steuer beträgt 11,832 Rappen je Stück und 25 Prozent des Kleinhandelspreises, mindestens
  21,210 Rappen je Stück."
* **AlkV Art. 21** (Art. 22 Abs. 1 AlkG): "Die Steuer beträgt 29 Franken je Liter reinen Alkohol."
''',
vat=dict(name="Mehrwertsteuer", standard=810, reduced=260, reduced2=380, threshold=99999,
  statute="MWSTG Art. 25 (1) 8,1 %, (2) 2,6 %, (4) 3,8 %; Art. 21 (2) Ziff. 2, 3, 11, 18, 19, 21; Art. 10 (2) lit. a (< 100 000 Fr.)",
  classes={"food": "reduced", "nonAlcoholic": "reduced", "water": "reduced", "medicines": "reduced", "books": "reduced",
           "newspapers": "reduced", "hotels": "reduced2",
           "health": "exempt", "education": "exempt", "insurance": "exempt", "financial": "exempt", "rent": "exempt"}),
excise=[dict(good="petrol", name="Mineralölsteuer + Zuschlag (Benzin)", num=73120, den=100000, statute="MinöStG Art. 12 (1) Anhang 1 (431.20 Fr.) + Art. 12 (2) (300 Fr.) je 1000 l"),
        dict(good="diesel", name="Mineralölsteuer + Zuschlag (Dieselöl)", num=75870, den=100000, statute="MinöStG Art. 12 (1) Anhang 1 (458.70 Fr.) + Art. 12 (2) (300 Fr.) je 1000 l"),
        dict(good="cigarettes", name="Tabaksteuer (Zigaretten)", num=11832, den=100000, adv=2500, minNum=21210, minDen=100000, statute="TStG: 11,832 Rp./Stück + 25 % des Kleinhandelspreises, mindestens 21,210 Rp./Stück"),
        dict(good="spirits", name="Alkoholsteuer", num=29, den=1, pure=True, statute="AlkV Art. 21 (AlkG Art. 22): 29 Fr. je Liter reinen Alkohol")],
notes=["CH 5111/5121: fedlex consolidations in force on 2025-07-01"],
unsupported=[("g.consumption.any (fun s => s.good == .beer)", "Biersteuer (BStG, by Stammwürze class) not read: not modelled"),
  ("g.consumption.any (fun s => s.good == .restaurants)", "restaurant meals taken at the standard rate (gastgewerbliche Leistungen; Art. 25 (3) not quoted)"),
  ("g.consumption.any (fun s => s.good == .tobaccoOther || s.good == .heatingOil || s.good == .gas)", "fine-cut tobacco, cigars, heating oil and gas taxes (incl. CO2-Abgabe) not modelled")],
guards=["vat.embedded { good := .clothing, amount := 1081 } == 81",
        "vat.embedded { good := .food, amount := 1026 } == 26",
        "vat.embedded { good := .hotels, amount := 1038 } == 38",
        "vat.net { turnover := 99999, sales := [{ good := .other, net := 99999 }] } == 0",
        "vat.net { turnover := 100000, sales := [{ good := .other, net := 100000 }] } == 8100",
        "excise.duty { good := .petrol, amount := 2000, quantity := 1000000 } == 731",
        "excise.duty { good := .diesel, amount := 2000, quantity := 1000000 } == 758",
        "-- 100 000 cigarettes: the minimum (21 210 Fr.) binds at a retail price of 30 000 Fr. (11 832 + 7 500)",
        "excise.duty { good := .cigarettes, amount := 30000, quantity := 100000000 } == 21210",
        "excise.duty { good := .cigarettes, amount := 60000, quantity := 100000000 } == 11832 + 15000",
        "excise.duty { good := .spirits, amount := 3000, quantity := 100000, abvBp := 4000 } == 1160"],
taxes=[{"oecd": "5111", "tax": "Mehrwertsteuer", "statute": "MWSTG Art. 10 (2), 21 (2), 25", "dated": "fedlex consolidation 2025-03-31", "grade": "A", "kernel_parts": ["Vat"], "unsupported": ["reduced-rate list item by item (Art. 25 (2) lit. a Ziff. 3-7, 10; lit. b-c)", "restaurant rule (Art. 25 (3)) not quoted"]},
 {"oecd": "5121", "tax": "Mineralölsteuer + Mineralölsteuerzuschlag (petrol, diesel)", "statute": "MinöStG Art. 12 (1), (2), Anhang 1", "dated": "fedlex consolidation 2025-01-01", "grade": "A", "kernel_parts": ["ExciseRate"], "unsupported": ["heating oil, gas, renewable-fuel reliefs (Art. 12a, 12b)"]},
 {"oecd": "5121", "tax": "Tabaksteuer (cigarettes)", "statute": "TStG (Zigaretten: 11,832 Rp. + 25 %, mindestens 21,210 Rp.)", "dated": "fedlex consolidation 2025-01-01", "grade": "A", "kernel_parts": ["ExciseRate (minimum)"], "unsupported": ["cigars, fine-cut (46 Fr./kg + 25 %, min 90 Fr./kg), other tobacco"]},
 {"oecd": "5121", "tax": "Alkoholsteuer (spirits)", "statute": "AlkG Art. 22; AlkV Art. 21", "dated": "fedlex AlkV consolidation 2022-01-01 (last before 2025-07-01)", "grade": "A", "kernel_parts": ["ExciseRate (pure alcohol)"], "unsupported": ["small-producer relief (Art. 22 (2) AlkG)"]},
 {"oecd": "5121", "tax": "Biersteuer", "statute": "Biersteuergesetz (BStG, SR 641.411)", "grade": "C", "status": "unsupported", "kernel_parts": [], "unsupported": ["BStG consolidation not fetched (fedlex search by title gave only the ordinances); would unlock: BStG SR 641.411 in force 2025"]}])

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
