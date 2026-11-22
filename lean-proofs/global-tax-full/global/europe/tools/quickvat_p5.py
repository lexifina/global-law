#!/usr/bin/env python3
"""quickvat_p5.py [CC ...]: pass-5 VAT rows (same generator as quickvat_p4.py: quickvat.py's guards() and spec writer,
quickvat.py's own ROWS not rewritten). Sources: PwC Worldwide Tax Summaries as captured by the Internet Archive in 2025
(reliable secondary host, grade B) for ME MK BA AL XK MD; RU from a 2022 capture checked against the 2024 amending act.
Excise entries stay grade C."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "quickvat.py"), encoding="utf-8").read()
HEAD, GEN = SRC.split("\nROWS = [", 1)[0], "\ndef guards" + SRC.split("\ndef guards", 1)[1]
EXEMPT = {"health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"}
EXN = ("g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance)",
       "exempt supplies taken from the EU-style structure the source describes (health, education, finance, insurance, residential rent), not quoted item by item")
SEC = "the act's own text not reached: rates from PwC Worldwide Tax Summaries (reliable secondary host)"
FOODN = lambda what: ("g.consumption.any (fun s => s.good == .food)", f"food at the standard rate: the reduced rate covers only {what} (not separable in the basket's food line)")


def pwc(slug, ts, cc):
    # pass 7: provenance in the short form; the facts below are restated, no PwC wording is copied
    country = slug.replace("-", " ").title().replace(" And ", " and ")
    return f"PwC Worldwide Tax Summaries, {country}, Corporate - Other taxes, accessed {ts} (Wayback capture; `{cc}/law/pwc_other_wb2025.html`)"


ROWS = [
 dict(cc="ME", name="Porez na dodatu vrijednost", std=2100, red=1500, red2=700, thr=30000,
      classes=dict(EXEMPT, books="reduced", newspapers="reduced", hotels="reduced", medicines="reduced2", transport="reduced2"),
      statute="Zakon o porezu na dodatu vrijednost (21 %, 15 %, 7 %; registration above 30 000 EUR)",
      src=pwc("montenegro", "2025-07-18", "me"),
      quotes=["VAT 21 %; 15 %: books, publications, some hospitality and accommodation; 7 %: bread, flour, milk and dairy, schoolbooks, medicines, orthopaedic / prosthetic devices, public transport",
              "registration: turnover > EUR 30 000 in the last 12 months (PwC page reviewed 15 July 2025)"],
      dated="PwC, last reviewed 15 July 2025", grade="B",
      uns=[EXN, FOODN("bread, flour, milk and dairy products (7 %)"), ("g.consumption.any (fun s => s.good == .restaurants)", "restaurants at 21 %: the hospitality services at 15 % are not specified"), ("!g.consumption.isEmpty", SEC)],
      excise="Zakon o akcizama (not read)"),
 dict(cc="MK", name="Данок на додадена вредност", std=1800, red=500, red2=1000, thr=2000000,
      classes=dict(EXEMPT, food="reduced", water="reduced", medicines="reduced", books="reduced", newspapers="reduced", electricity="reduced",
                   transport="reduced", hotels="reduced", restaurants="reduced2"),
      statute="Закон за данокот на додадена вредност (18 %, 5 %, 10 %; registration above MKD 2 000 000)",
      src=pwc("north-macedonia", "2025-08-10", "mk"),
      quotes=["VAT 18 %; preferential 5 % and 10 %",
              "5 %: food, public drinking water, medicines and medical equipment, books / newspapers, household electricity, passenger transport, accommodation; 10 %: restaurant and catering services (alcohol excluded)",
              "registration: annual turnover > MKD 2 000 000 (PwC page reviewed 18 February 2025)"],
      dated="PwC, last reviewed 18 February 2025", grade="B", uns=[EXN, ("!g.consumption.isEmpty", SEC)],
      excise="Закон за акцизите (not read)"),
 dict(cc="BA", name="Porez na dodanu vrijednost", std=1700, thr=100000, classes=dict(EXEMPT),
      statute="Zakon o porezu na dodanu vrijednost BiH (17 %, no reduced rate; registration above BAM 100 000)",
      src=pwc("bosnia-and-herzegovina", "2025-07-31", "ba"),
      quotes=["VAT 17 %, one rate in the whole country; no reduced rate",
              "registration: taxable supplies > BAM 100 000 (PwC page reviewed 6 February 2025)"],
      dated="PwC, last reviewed 6 February 2025", grade="B", uns=[EXN, ("!g.consumption.isEmpty", SEC)],
      excise="Zakon o akcizama BiH (PwC: tobacco 42 % of retail price + BAM 0.75 a pack; not modelled)"),
 dict(cc="AL", name="Tatimi mbi vlerën e shtuar", std=2000, red=600, thr=10000000,
      classes=dict(EXEMPT, hotels="reduced", books="reduced"),
      statute="Ligji për TVSH (20 %, 6 %; registration above ALL 10 000 000)",
      src=pwc("albania", "2025-08-03", "al"),
      quotes=["VAT 20 %; registration: annual turnover > ALL 10 000 000",
              "6 %: accommodation, certified agritourism, audiovisual advertising, books, ... (PwC page reviewed 30 June 2025)"],
      dated="PwC, last reviewed 30 June 2025", grade="B", uns=[EXN, ("!g.consumption.isEmpty", SEC)],
      excise="Ligji për akcizat (not read)"),
 dict(cc="XK", name="Tatimi mbi vlerën e shtuar", std=1800, red=800, thr=30000,
      classes=dict(EXEMPT, water="reduced", electricity="reduced", books="reduced"),
      statute="Ligji Nr. 05/L-037 për TVSH (18 %, 8 %; registration above EUR 30 000)",
      src=pwc("kosovo", "2025-06-24", "xk"),
      quotes=["law: Ligji Nr. 05/L-037 për TVSH; registration: turnover > EUR 30 000 in a calendar year",
              "VAT 18 %; 8 %: water (not bottled), electricity, grains and grain products, dairy, textbooks and serials, library book lending, ... (PwC page reviewed 22 January 2025)"],
      dated="PwC, last reviewed 22 January 2025", grade="B",
      uns=[EXN, FOODN("grain products, oils, dairy, salt and eggs (8 %)"), ("!g.consumption.isEmpty", SEC)],
      excise="Ligji për akcizat (not read)"),
 dict(cc="MD", name="Taxa pe valoarea adăugată", std=2000, red=800, thr=1200000,
      classes=dict(EXEMPT, hotels="reduced", restaurants="reduced"),
      statute="Codul fiscal Titlul III art. 96 (20 %, 8 %); registration at MDL 1 200 000",
      src=pwc("moldova", "2025-05-25", "md"),
      quotes=["VAT 20 %; 8 %: bread and bakery products, milk and dairy, ...; hotels, restaurants, cafes 8 % (12 % before 10.8.2023)",
              "registration: turnover ≥ MDL 1 200 000 in the last 12 months (PwC page reviewed 20 January 2025)"],
      dated="PwC, last reviewed 20 January 2025", grade="B",
      uns=[EXN, FOODN("bread, bakery and dairy products (8 %)"), ("!g.consumption.isEmpty", SEC)],
      excise="Codul fiscal Titlul IV (not read)"),
 dict(cc="RU", name="Налог на добавленную стоимость", std=2000, red=1000, thr=0,
      classes=dict(EXEMPT, food="reduced", medicines="reduced", books="reduced", newspapers="reduced"),
      statute="Налоговый кодекс РФ ст. 164 п. 2 (10 %), п. 3 (20 %); п. 8 (5 % / 7 %, УСН, from 1.1.2025, 176-ФЗ)",
      src="PwC Worldwide Tax Summaries, Russian Federation, Corporate - Other taxes, accessed 2022-01-17 (Wayback capture; `ru/law/pwc_other_wb2025.html`; PwC no longer publishes the page), checked against Федеральный закон от 12.07.2024 № 176-ФЗ (kremlin.ru, the 1.x model's `fz176_2024_clean.txt`): its amendments to ст. 164 add п. 8 and change п. 4 only",
      quotes=["VAT 20 % (18 % before 2019); 10 %: some basic foods, children's clothes, medicines, medical goods, printed matter (PwC page reviewed 12 February 2021)",
              "176-ФЗ ст. 2 п. 5: \"в статье 164: а) в пункте 4 слова \\\"пунктом 2 или 3\\\" заменить словами \\\"пунктом 2, 3 или 8\\\"; б) дополнить пунктом 8 ...\" (5 % / 7 % for simplified-regime taxpayers): п. 2-3 unchanged for 2025"],
      dated="PwC 2021 review (rates of п. 2-3 unchanged in 2025 per 176-ФЗ)", grade="B",
      uns=[EXN, ("g.consumption.any (fun s => s.good == .food)", "food at 10 % (some basic foods only: the 10 % list of п. 2 not read item by item)"),
           ("g.entity == .company", "exemption of ст. 145 (revenue thresholds) and the 5 % / 7 % simplified-regime rates of п. 8 not modelled: every company line taxed at 20 %"),
           ("!g.consumption.isEmpty", "ст. 164 itself not read (consultant.ru is script-built); rates from PwC")],
      excise="Налоговый кодекс РФ гл. 22 (not read)"),
]

if __name__ == "__main__":
    g = {"__file__": os.path.join(HERE, "quickvat.py")}
    exec(HEAD, g)
    sel = sys.argv[1:]
    g["ROWS"] = [r for r in ROWS if not sel or r["cc"] in sel]
    exec(GEN, g)
