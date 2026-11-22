#!/usr/bin/env python3
"""quickvat.py: write tools/specs/<CC>_Consumption.py for VAT-only family modules from the table below (countries
where the VAT act's rate article was read but the excises were not reached in the pass). Guards are computed here
from the rates (embedded VAT on 100 + rate; threshold edge)."""
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "specs")
EXC = "g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)"

ROWS = [
 dict(cc="HU", name="Általános forgalmi adó", std=2700, red=1800, sup=500, thr=0,
      classes={"medicines": "superReduced", "books": "superReduced", "newspapers": "superReduced", "restaurants": "superReduced",
               "hotels": "reduced", "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"},
      statute="2007. évi CXXVII. törvény 82. § (1) 27 %, (2) 5 % (3. melléklet), (3) 18 % (3/A. melléklet); 85.-86. § (mentes)",
      src="2007. évi CXXVII. törvény az általános forgalmi adóról, net.jogtar.hu (Wolters Kluwer, private publisher of the consolidated text; njt.hu reset the connection), `hu/law/afa.html`",
      quotes=["82. § (1): \"Az adó mértéke az adó alapjának 27 százaléka\"", "(2) \"A 3. számú mellékletben felsorolt termékek, szolgáltatások esetében ... 5 százaléka\"", "(3) \"A 3/A. számú mellékletben ... 18 százaléka\""],
      dated="consolidated text (jogtar), current", grade="B",
      uns=[("g.consumption.any (fun s => s.good == .food)", "food at 27 %; milk, eggs, pork, poultry and other 3. melléklet foods are 5 %"),
           ("g.entity == .company", "alanyi adómentesség (small-business exemption, 188. §) not read: no threshold applied")],
      excise="Jövedéki adóról szóló 2016. évi LXVIII. törvény"),
 dict(cc="IT", name="Imposta sul valore aggiunto", std=2200, red=1000, red2=500, sup=400, thr=0,
      classes={"food": "reduced", "water": "reduced", "medicines": "reduced", "hotels": "reduced", "restaurants": "reduced",
               "transport": "reduced", "electricity": "reduced", "books": "superReduced", "newspapers": "superReduced",
               "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"},
      statute="DPR 633/1972 art. 16 (22 %; 4, 5, 10 % per tabella A parti II, II-bis, III); art. 10 (esenzioni)",
      src="DPR 26 ottobre 1972 n. 633, Normattiva (official) multivigente text \"!vig=2025-07-01\" (`it/law/dpr633_art16.html`)",
      quotes=["art. 16: \"L'aliquota dell'imposta è stabilita nella misura del ventidue per cento\"", "\"L'aliquota è ridotta al quattro, al cinque e al dieci per cento per le operazioni che hanno per oggetto i beni e i servizi elencati, rispettivamente, nella parte II, nella parte II-bis e nella parte III dell'allegata tabella A\""],
      dated="Normattiva vigente al 2025-07-01", grade="B",
      uns=[("g.consumption.any (fun s => s.good == .food)", "food at 10 % (tabella A parte III); bread, milk, fresh produce and other parte II items are 4 %: tabella A not read item by item"),
           ("g.entity == .company", "no VAT registration threshold (the regime forfettario is an income-tax regime, not modelled)")],
      excise="D.Lgs. 26 ottobre 1995 n. 504 (testo unico accise)"),
 dict(cc="PT", name="Imposto sobre o valor acrescentado", std=2300, red=1300, sup=600, thr=0,
      classes={"food": "superReduced", "water": "superReduced", "books": "superReduced", "newspapers": "superReduced", "medicines": "superReduced",
               "hotels": "superReduced", "transport": "superReduced", "restaurants": "reduced",
               "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"},
      statute="CIVA art. 18.º n.º 1 a) 6 % (lista I), b) 13 % (lista II), c) 23 %; art. 9.º (isenções)",
      src="Código do IVA, Portal das Finanças (Autoridade Tributária, official), article page `pt/law/civa18.html` (current text)",
      quotes=["art. 18.º 1: \"a) Para as importações, transmissões de bens e prestações de serviços constantes da lista I anexa a este diploma, a taxa de 6%\"", "\"b) ... constantes da lista II ..., a taxa de 13%\""],
      dated="Portal das Finanças current text (continental rates)", grade="B",
      uns=[("g.entity == .company", "small-business exemption (art. 53.º) not read: no threshold applied"),
           ("!g.consumption.isEmpty", "continental rates (Açores and Madeira lower) ; lists I and II by category")],
      excise="Código dos Impostos Especiais de Consumo (DL 73/2010)"),
 dict(cc="RS", name="Porez na dodatu vrednost", std=2000, red=1000, thr=8000000,
      classes={"food": "reduced", "medicines": "reduced", "newspapers": "reduced", "books": "reduced", "hotels": "reduced", "water": "reduced",
               "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"},
      statute="Zakon o porezu na dodatu vrednost čl. 23 (20 %, 10 %); čl. 25 (oslobođenja); čl. 33 (8.000.000 dinara)",
      src="Zakon o porezu na dodatu vrednost, consolidated text published by Paragraf (private publisher; the official Pravno-informacioni sistem is script-only), `rs/law/pdv.html`",
      quotes=["čl. 23: \"Opšta stopa PDV za oporezivi promet dobara i usluga ili uvoz dobara iznosi 20%\"; \"Po posebnoj stopi PDV od 10% oporezuje se ...\"", "čl. 33: promet in the previous 12 months \"nije veći od 8.000.000 dinara\""],
      dated="consolidated text (Paragraf), current", grade="B",
      uns=[("g.consumption.any (fun s => s.good == .food)", "food at 10 % (čl. 23 st. 2: bread, milk, flour, sugar, oils ...); other food 20 %")],
      excise="Zakon o akcizama"),
 dict(cc="UA", name="Податок на додану вартість", std=2000, sup=700, thr=1000000,
      classes={"medicines": "superReduced", "hotels": "superReduced",
               "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt"},
      statute="Податковий кодекс ст. 193.1 (20 %, 0 %, 7 %, 14 %); ст. 196-197 (звільнення); ст. 181.1 (1000000 гривень)",
      src="Податковий кодекс України (2755-VI), zakon.rada.gov.ua (official) as captured by the Internet Archive on 2025-06-20 (`ua/law/ptk_wb20250620.txt`, copied from the 1.x model's law folder)",
      quotes=["193.1: \"а) 20 відсотків; б) 0 відсотків; в) 7 відсотків по операціях з: постачання ... лікарських засобів ...; постачання послуг із тимчасового розміщування (проживання), що надаються готелями\"", "181.1: registration when supplies \"перевищує 1000000 гривень (без урахування податку на додану вартість)\""],
      dated="zakon.rada.gov.ua via Internet Archive 2025-06-20", grade="A",
      uns=[], excise="Податковий кодекс розділ VI (акцизний податок, ст. 215.3: multi-year rate tables, not extracted in this pass)"),
 dict(cc="BY", name="Налог на добавленную стоимость", std=2000, red=1000, thr=0,
      classes={"food": "reduced"},
      statute="Налоговый кодекс (Особенная часть) ст. 122 п. 2 (10 %), п. 3 (20 %), п. 4 (25 %)",
      src="Налоговый кодекс Республики Беларусь, Особенная часть (НК 2009 № 71-З), pravo.by (official) as captured by the Internet Archive on 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`, from the 1.x model's law folder)",
      quotes=["ст. 122 п. 2: \"Ставка налога на добавленную стоимость в размере десять (10) процентов устанавливается при: ... 2.2. ввозе ... и (или) реализации продовольственных товаров и товаров для детей\" (by the list of the Council of Ministers)", "п. 3: \"в размере двадцать (20) процентов\"; п. 4: \"двадцать пять (25) процентов\" (telecommunication services)"],
      dated="pravo.by via Internet Archive 2025-06-14", grade="A",
      uns=[("g.consumption.any (fun s => s.good == .food)", "food at 10 % (ст. 122 п. 2.2: only foods on the Government's list; others 20 %)"),
           ("g.consumption.any (fun s => s.good == .communication)", "telecommunication services at 20 % (25 % under ст. 122 п. 4 not separated)"),
           ("g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance)", "exemptions (ст. 118) not read: taken at 20 %")],
      excise="Налоговый кодекс ст. 155 and приложение 1"),
 dict(cc="NL", name="Omzetbelasting", std=2100, red=900, thr=0,
      classes={"food": "reduced", "nonAlcoholic": "reduced", "water": "reduced", "medicines": "reduced", "books": "reduced", "newspapers": "reduced",
               "hotels": "reduced", "transport": "reduced", "restaurants": "reduced",
               "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"},
      statute="Wet op de omzetbelasting 1968 art. 9 lid 1 (21 %), lid 2 onderdeel a (9 %, tabel I); art. 11 (vrijstellingen); art. 25a (KOR)",
      src="Wet op de omzetbelasting 1968 (BWBR0002629), wetten.overheid.nl (official), version \"Geldend van 01-01-2025 t/m 31-12-2025\" (`nl/law/wetob_g2025.html`)",
      quotes=["art. 9: \"1 De belasting bedraagt 21 percent. 2 In afwijking van het eerste lid bedraagt de belasting: a. 9 percent voor leveringen van goederen en diensten, genoemd in de bij deze wet behorende tabel I\""],
      dated="wetten.overheid.nl, geldend 2025-01-01 t/m 2025-12-31", grade="A",
      uns=[("g.entity == .company", "kleineondernemersregeling (art. 25a, optional exemption up to 20 000 euro) not applied"),
           ("g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance)", "exemptions (art. 11) by category, not quoted")],
      excise="Wet op de accijns (BWBR0005135; fetched, rates not extracted in this pass)"),
 dict(cc="BG", name="Данък върху добавената стойност", std=2000, red=900, thr=0,
      classes={"hotels": "reduced", "books": "reduced",
               "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"},
      statute="ЗДДС чл. 66 ал. 1 (20 %), чл. 66а (9 %); чл. 38-50 (освободени доставки); чл. 96 (регистрация)",
      src="Закон за данък върху добавената стойност, lex.bg (private publisher of the consolidated text with the amendment notes of each provision), `bg/law/zdds.html`",
      quotes=["чл. 66 (изм. ДВ бр. 52 от 2022 г., в сила от 01.07.2022 г.) \"(1) Стандартната ставка на данъка е 20 на сто\"", "чл. 66а (в сила от 01.01.2023 г.) \"Ставката на данъка е 9 на сто за: 1. доставка на услуга по настаняване, предоставяно в хотели ...; 2. доставка на книги ...; 3. доставки на храни, подходящи за бебета\""],
      dated="lex.bg current text; arts. 66, 66a unchanged since 2022/2023 per their notes", grade="B",
      uns=[("g.entity == .company", "registration threshold (чл. 96) read only in its 2026 wording (EUR): not applied for 2025")],
      excise="Закон за акцизите и данъчните складове"),
 dict(cc="IS", name="Virðisaukaskattur", std=2400, red=1100, thr=2000000,
      classes={"food": "reduced", "nonAlcoholic": "reduced", "transport": "reduced", "hotels": "reduced", "books": "reduced", "newspapers": "reduced",
               "electricity": "reduced", "heatingOil": "reduced",
               "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"},
      statute="Lög nr. 50/1988 um virðisaukaskatt 14. gr. (24 %, 11 %); 2. gr. 3. mgr. (undanþegið); 4. gr. 3. tölul. (2.000.000 kr.)",
      src="Lög nr. 50/1988 um virðisaukaskatt, althingi.is (official) as captured by the Internet Archive on 2025-09-04 (`is/law/vsk_wb.html`)",
      quotes=["14. gr.: \"Virðisaukaskattur skal vera [24%]\"; \"skal virðisaukaskattur af sölu á eftirtalinni vöru og þjónustu vera [11%]: 1. Fólksflutningar ... 2. Útleiga hótel- og gistiherbergja ... 5. Sala ... tímarita, dagblaða ... 6. Sala bóka ... 7. Sala á heitu vatni, rafmagni og olíu til hitunar húsa\" (and food, item not quoted)", "4. gr. 3. tölul.: \"Þeir sem selja skattskylda vöru eða þjónustu fyrir [2.000.000 kr.]\""],
      dated="althingi.is via Internet Archive 2025-09-04", grade="A",
      uns=[("g.consumption.any (fun s => s.good == .food || s.good == .nonAlcoholic)", "food and non-alcoholic drinks at 11 % (14. gr. 2. mgr. item not quoted)")],
      excise="Lög nr. 96/1995 um gjald af áfengi og tóbaki; lög nr. 87/2004 um olíugjald"),
 dict(cc="MT", name="Value Added Tax", std=1800, red=700, sup=500, thr=0,
      classes={"hotels": "reduced", "electricity": "superReduced"},
      statute="VAT Act (Cap. 406) art. 19 (18 %); Eighth Schedule (7 % accommodation, 5 % electricity ...); Fifth Schedule (exemptions)",
      src="Value Added Tax Act, Cap. 406, legislation.mt consolidated PDF (official; it lists amendments up to Act III of 2026 and Legal Notices of 2026, so the 2025 wording is read through an unchanged rate structure), `mt/law/cap406.pdf`",
      quotes=["art. 19: tax \"at the rate of eighteen per cent of the taxable value of the supply\"", "Eighth Schedule: \"The letting of or the provision of accommodation in any premises ... 7%\"; \"2. The supply of electricity. 5%\""],
      dated="legislation.mt consolidation (to 2026)", grade="B",
      uns=[("g.consumption.any (fun s => s.good == .food || s.good == .medicines || s.good == .books || s.good == .newspapers || s.good == .transport || s.good == .restaurants)", "food, medicines (zero-rated, Fifth Schedule Part One), books (5 %), transport and restaurant rates not read item by item: taken at 18 %"),
           ("g.entity == .company", "small undertaking exemption (art. 11) not read: no threshold applied")],
      excise="Excise Duty Act (Cap. 382)"),
]


def guards(r):
    g = []
    std = r["std"]
    g.append(f"vat.embedded {{ good := .clothing, amount := {10000 + std} }} == {std}")
    for cls, key in (("reduced", "red"), ("reduced2", "red2"), ("superReduced", "sup")):
        if key in r:
            goods = [k for k, v in r["classes"].items() if v == cls]
            if goods:
                g.append(f"vat.embedded {{ good := .{goods[0]}, amount := {10000 + r[key]} }} == {r[key]}")
    if r["thr"] > 0:
        g.append(f"vat.net {{ turnover := {r['thr']}, sales := [{{ good := .other, net := {r['thr']} }}] }} == 0")
    return g


for r in ROWS:
    vat = dict(name=r["name"], standard=r["std"], threshold=r["thr"], statute=r["statute"], classes=r["classes"])
    for k, kk in (("red", "reduced"), ("red2", "reduced2"), ("sup", "superReduced")):
        if k in r: vat[kk] = r[k]
    doc = (f"# {r['cc']} 2025: {r['name']} (5111); excises not modelled in this pass\n\nSource: {r['src']}; sha256 in "
           "`law/SHA256SUMS`.\n" + "".join(f"* {q}\n" for q in r["quotes"]))
    uns = list(r["uns"]) + [(EXC, f"excise ({r['excise']}) not modelled in this pass")]
    taxes = [{"oecd": "5111", "tax": r["name"], "statute": r["statute"], "dated": r["dated"], "grade": r["grade"],
              "kernel_parts": ["Vat"], "unsupported": [t for _, t in r["uns"]]},
             {"oecd": "5121", "tax": "Excise duties", "statute": r["excise"], "grade": "C", "status": "unsupported",
              "kernel_parts": [], "unsupported": ["not read in the P1 pass: would unlock with the act's 2025 rate articles"]}]
    S = dict(cc=r["cc"], fam="Consumption", family_name="5111 " + r["name"], doc=doc, vat=vat,
             notes=[f"{r['cc']} 5111: {r['dated']}"], unsupported=uns, guards=guards(r), taxes=taxes)
    open(os.path.join(OUT, f"{r['cc']}_Consumption.py"), "w", encoding="utf-8").write("S = " + repr(S) + "\n")
    print(r["cc"], "spec written")
