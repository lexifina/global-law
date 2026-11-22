S = dict(cc="PL", fam="Consumption", family_name="5111 VAT",
doc=r'''# Poland 2025: podatek od towarów i usług (5111); excise not modelled

Source: ustawa z dnia 11 marca 2004 r. o podatku od towarów i usług, tekst jednolity Dz.U. 2024 poz. 361 (ELI API of
the Sejm, `pl/law/vat_tj2024.pdf`, sha256 in `law/SHA256SUMS`): the consolidated text of 2024, read for 2025 through
its transitional article (grade B: 2025 amendments not checked).
* **art. 41 ust. 1** "Stawka podatku wynosi 22 %", with **art. 146ef ust. 1 pkt 1** "stawka podatku, o której mowa w
  art. 41 ust. 1 i 13, ... wynosi 23 %" (and 8 % / 5 % for the reduced rates of art. 41 ust. 2, 2a; annexes 3 and 10:
  food mostly 5 %, books 5 %, medicines, hotels, restaurants and passenger transport 8 %).
* **art. 113 ust. 1**: exemption when sales in the previous year did not exceed "200 000 zł".
''',
vat=dict(name="Podatek od towarów i usług", standard=2300, reduced=800, superReduced=500, threshold=200000,
  statute="ustawa o VAT art. 41 ust. 1, 2, 2a, art. 146ef (23 %, 8 %, 5 %); art. 43 (zwolnienia); art. 113 ust. 1 (200 000 zł)",
  classes={"food": "superReduced", "books": "superReduced", "medicines": "reduced", "hotels": "reduced", "restaurants": "reduced", "transport": "reduced",
           "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"}),
notes=["PL 5111: Dz.U. 2024 poz. 361 (tekst jednolity)"],
unsupported=[("g.consumption.any (fun s => s.good == .food || s.good == .books || s.good == .medicines || s.good == .hotels || s.good == .restaurants || s.good == .transport)", "reduced-rate classes taken from annexes 3 and 10 by category (not item by item)"),
  ("g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)", "akcyza (ustawa o podatku akcyzowym, t.j. Dz.U. 2025 poz. 126, fetched) not modelled in this pass")],
guards=["vat.embedded { good := .clothing, amount := 123 } == 23",
        "vat.embedded { good := .hotels, amount := 108 } == 8",
        "vat.embedded { good := .food, amount := 105 } == 5",
        "vat.net { turnover := 200000, sales := [{ good := .other, net := 200000 }] } == 0"],
taxes=[{"oecd": "5111", "tax": "Podatek od towarów i usług", "statute": "ustawa o VAT art. 41, 43, 113, 146ef; załączniki 3, 10", "dated": "t.j. Dz.U. 2024 poz. 361", "grade": "B", "kernel_parts": ["Vat"], "unsupported": ["2025 amendments not checked", "annexes by category"]},
 {"oecd": "5121", "tax": "Podatek akcyzowy", "statute": "ustawa z 6 grudnia 2008 r. o podatku akcyzowym (t.j. Dz.U. 2025 poz. 126)", "grade": "B", "status": "not modelled (text fetched, rates not read in this pass)", "kernel_parts": [], "unsupported": ["rates not extracted"]}])

# ---- pass 2 (R1 Europe, 2026-11-21): akcyza from the t.j. Dz.U. 2025 poz. 126 ----
S["imports"] = ["TaxKernel.Global2"]
S["family_name"] = "5111 VAT, 5121 akcyza"
S["doc"] = S["doc"].replace("excise not modelled", "akcyza (5121)") + r'''
## Akcyza (5121), pass 2
Source: ustawa z dnia 6 grudnia 2008 r. o podatku akcyzowym, tekst jednolity Dz.U. 2025 poz. 126 (obwieszczenie of
23.12.2024; `pl/law/akcyza_tj2025.pdf`), which prints the amendment of 18.10.2024 (Dz.U. 2024 poz. 1681) "która
wejdzie w życie z dniem 1 stycznia 2025 r." in its 2025 wording (footnotes 27, 48, 49).
* **Art. 89 ust. 1 pkt 2**: motor petrol "– 1529 zł/1000 litrów"; **pkt 6**: diesel "– 1160 zł/1000 litrów".
* **Art. 165a ust. 1** ("W latach 2022–2026 stawki akcyzy na napoje alkoholowe wynoszą"), lit. d (2025): pkt 1 alkohol
  etylowy "7991,00 zł od 1 hektolitra alkoholu etylowego 100 % vol."; pkt 2 piwo "10,92 zł od 1 hektolitra za każdy
  stopień Plato"; pkt 3 wino "222,00 zł od 1 hektolitra gotowego wyrobu".
* **Art. 165a ust. 2 pkt 1 lit. d** (wording of footnote 49, from 1.1.2025): cigarettes "– 1 stycznia 2025 r. do dnia
  28 lutego 2025 r. – 276,00 zł za każde 1000 sztuk i 32,05 % maksymalnej ceny detalicznej, – 1 marca 2025 r. do dnia
  31 grudnia 2025 r. – 345,00 zł za każde 1000 sztuk i 32,05 % maksymalnej ceny detalicznej".
* Not applied: art. 99 ust. 4 minimum (105 % of the excise at the weighted average retail price, published by
  obwieszczenie).
'''
S["lean"] = (S.get("lean") or "") + r'''
def petrol : ExciseRule := { good := .petrol, name := "Akcyza (benzyny silnikowe)", perUnitNum := 1529, perUnitDen := 1000,
  statute := "ustawa o podatku akcyzowym art. 89 ust. 1 pkt 2 (1529 zł/1000 l)" }
def diesel : ExciseRule := { good := .diesel, name := "Akcyza (oleje napędowe)", perUnitNum := 1160, perUnitDen := 1000,
  statute := "ustawa o podatku akcyzowym art. 89 ust. 1 pkt 6 (1160 zł/1000 l)" }
def spirits : ExciseRule := { good := .spirits, name := "Akcyza (alkohol etylowy)", perUnitNum := 7991, perUnitDen := 100, onPureAlcohol := true,
  statute := "ustawa o podatku akcyzowym art. 93 ust. 4, art. 165a ust. 1 pkt 1 lit. d (7991,00 zł / hl 100 % vol., 2025)" }
def beer : ExciseRule := { good := .beer, name := "Akcyza (piwo)", perPlatoNum := 1092, perPlatoDen := 10000,
  statute := "ustawa o podatku akcyzowym art. 94 ust. 4, art. 165a ust. 1 pkt 2 lit. d (10,92 zł / hl and degree Plato, 2025)" }
def wine : ExciseRule := { good := .wine, name := "Akcyza (wino)", perUnitNum := 222, perUnitDen := 100,
  statute := "ustawa o podatku akcyzowym art. 95 ust. 4, art. 165a ust. 1 pkt 3 lit. d (222,00 zł / hl, 2025)" }
def cigTo : ExciseRule := { good := .cigarettes, name := "Akcyza (papierosy)", perUnitNum := 276, perUnitDen := 1000, adValoremBp := 3205,
  validTo := "2025-03-01", statute := "ustawa o podatku akcyzowym art. 99 ust. 2 pkt 1, art. 165a ust. 2 pkt 1 lit. d (276,00 zł / 1000 + 32,05 % MCD, 1.1-28.2.2025)" }
def cigFrom : ExciseRule := { good := .cigarettes, name := "Akcyza (papierosy)", perUnitNum := 345, perUnitDen := 1000, adValoremBp := 3205,
  validFrom := "2025-03-01", statute := "ustawa o podatku akcyzowym art. 99 ust. 2 pkt 1, art. 165a ust. 2 pkt 1 lit. d (345,00 zł / 1000 + 32,05 % MCD, from 1.3.2025)" }
def rules : List ExciseRule := [petrol, diesel, spirits, beer, wine, cigTo, cigFrom]
'''
S["extra_run"] = ["exciseRuleCharges rules g"]; S["extra_covers"] = [".excise"]
S["unsupported"] = [u for u in S["unsupported"] if "akcyza" not in u[1]] + [
  ("g.consumption.any (fun s => s.good == .beer)", "akcyza on beer by the line's \"platoBp\" (degree Plato x 100); a beer line without it bears none"),
  ("g.consumption.any (fun s => s.good == .cigarettes)", "cigarettes: the line's amount is taken as the maximum retail price; art. 99 ust. 4 minimum (105 % at the weighted average price) not applied; undated lines split 59/365 and 306/365"),
  ("g.consumption.any (fun s => s.good == .electricity || s.good == .gas)", "akcyza on electricity (art. 89 ust. 4) and gas not modelled")]
S["notes"] = S.get("notes", []) + ["PL 5121: akcyza t.j. Dz.U. 2025 poz. 126 (2025 rates of art. 165a)"]
S["guards"] = S["guards"] + [
  "petrol.dutyOn { good := .petrol, amount := 6000, quantity := 1000000 } {} == 1529",
  "diesel.dutyOn { good := .diesel, amount := 6000, quantity := 1000000 } {} == 1160",
  "-- 100 l at 40 %: 40 l x 79,91",
  "spirits.dutyOn { good := .spirits, amount := 9000, quantity := 100000, abvBp := 4000 } {} == 3196",
  "beer.dutyOn { good := .beer, amount := 900, quantity := 100000 } { platoBp := 1200 } == 131",
  "wine.dutyOn { good := .wine, amount := 2000, quantity := 100000 } {} == 222",
  "-- 1 000 cigarettes at 800 zł: 276 + 256,40; from March 345 + 256,40",
  "cigTo.dutyOn { good := .cigarettes, amount := 800, quantity := 1000000 } {} == 532",
  "cigFrom.dutyOn { good := .cigarettes, amount := 800, quantity := 1000000 } {} == 601"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "5121"] + [
 {"oecd": "5121", "tax": "Akcyza (paliwa silnikowe)", "statute": "ustawa o podatku akcyzowym art. 89 ust. 1 pkt 2, 6", "dated": "t.j. Dz.U. 2025 poz. 126 (no transitional rate for 2025)", "grade": "A", "kernel_parts": ["ExciseRule"], "unsupported": ["LPG, heating oils, electricity"]},
 {"oecd": "5121", "tax": "Akcyza (alkohol etylowy, piwo, wino)", "statute": "ustawa o podatku akcyzowym art. 93-95, art. 165a ust. 1 lit. d", "dated": "t.j. Dz.U. 2025 poz. 126; the 2025 row of art. 165a", "grade": "A", "kernel_parts": ["ExciseRule (pure alcohol, per degree Plato)"], "unsupported": ["small producers (50 %)", "intermediate products, fermented drinks"]},
 {"oecd": "5121", "tax": "Akcyza (papierosy)", "statute": "ustawa o podatku akcyzowym art. 99 ust. 2 pkt 1, art. 165a ust. 2 pkt 1 lit. d", "dated": "wording of the act of 18.10.2024 (Dz.U. 2024 poz. 1681) from 1.1.2025: two periods", "grade": "B", "kernel_parts": ["ExciseRule (validFrom/validTo, specific + ad valorem)"], "unsupported": ["art. 99 ust. 4 minimum (weighted average price)", "tobacco for smoking, heated tobacco, e-liquids"]}]

S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")


# ---- FT review (2026-11-21, third pass): heating oil, opłata paliwowa, opłata emisyjna (ftd_ec_oilbulletin_excise_2025 dev; IMPROVE_FT D5-3, D5-4) ----
S["doc"] += r'''
## FT review (2026-11-21, third pass): heating oil and the two fuel charges
* **Akcyza art. 89 ust. 1 pkt 9** (same t.j. Dz.U. 2025 poz. 126): "olejów napędowych przeznaczonych do celów
  opałowych o kodach CN od 2710 19 43 do 2710 19 48 i od 2710 20 11 do 2710 20 19, zabarwionych na czerwono i
  oznaczonych znacznikiem zgodnie z przepisami szczególnymi – 232,00 zł/1000 litrów". The household's `heatingOil` is
  read as such marked gas oil (pkt 10 lit. a, light fuel oils, has the same 232,00 zł).
* **Opłata paliwowa** (ustawa z 27 października 1994 r. o autostradach płatnych oraz o Krajowym Funduszu Drogowym, art.
  37h-37j; the yearly rate under art. 37m ust. 4): **Obwieszczenie Ministra Infrastruktury z 4 grudnia 2024 r., M.P.
  2024 poz. 1034** (`pl/law/mp2024_1034_oplata_paliwowa.pdf`): "1) 202,20 zł za 1000 l benzyn silnikowych ...; 2) 436,07
  zł za 1000 l olejów napędowych ...". Payable by the producer or importer with the excise (art. 37h), revenue of the
  Krajowy Fundusz Drogowy.
* **Opłata emisyjna** (ustawa Prawo ochrony środowiska, t.j. Dz.U. 2025 poz. 647, `pl/law/pos_tj2025_647.pdf`):
  art. 321a ust. 1, 3 (motor petrol CN 2710 12 45, 2710 12 49; diesel CN 2710 19 42, 2710 19 44, 2710 20 11), art. 321d
  ust. 1 (due with the excise liability), **art. 321f**: "1) benzyn silnikowych – wynosi 80 zł za 1000 litrów; 2)
  olejów napędowych – wynosi 80 zł za 1000 litrów"; revenue of NFOŚiGW (95 %) and the bus fund (5 %), art. 321b.
Both charges are compulsory, unrequited payments to government funds levied on the same release for consumption as the
excise: taxes on specific goods (5121; OECD Revenue Statistics Interpretative Guide, payments to extrabudgetary funds
count as taxes). Neither applies to heating oil (art. 37h ust. 4 and art. 321a ust. 3 name motor fuels only).
'''
S["lean"] = S["lean"] + r'''
def heatingOil : ExciseRule := { good := .heatingOil, name := "Akcyza (oleje opałowe)", perUnitNum := 232, perUnitDen := 1000, statute := "ustawa o podatku akcyzowym art. 89 ust. 1 pkt 9 (232,00 zł/1000 l, olej napędowy do celów opałowych, zabarwiony i oznaczony)" }
def oplPalPetrol : ExciseRule := { good := .petrol, name := "Opłata paliwowa (benzyny silnikowe)", perUnitNum := 20220, perUnitDen := 100000, statute := "ustawa o autostradach płatnych oraz o KFD art. 37h, 37j; M.P. 2024 poz. 1034 (202,20 zł/1000 l, 2025)" }
def oplPalDiesel : ExciseRule := { good := .diesel, name := "Opłata paliwowa (oleje napędowe)", perUnitNum := 43607, perUnitDen := 100000, statute := "ustawa o autostradach płatnych oraz o KFD art. 37h, 37j; M.P. 2024 poz. 1034 (436,07 zł/1000 l, 2025)" }
def oplEmPetrol : ExciseRule := { good := .petrol, name := "Opłata emisyjna (benzyny silnikowe)", perUnitNum := 80, perUnitDen := 1000, statute := "Prawo ochrony środowiska art. 321a, 321f pkt 1 (80 zł/1000 l; t.j. Dz.U. 2025 poz. 647)" }
def oplEmDiesel : ExciseRule := { good := .diesel, name := "Opłata emisyjna (oleje napędowe)", perUnitNum := 80, perUnitDen := 1000, statute := "Prawo ochrony środowiska art. 321a, 321f pkt 2 (80 zł/1000 l; t.j. Dz.U. 2025 poz. 647)" }
def fuelCharges : List ExciseRule := [heatingOil, oplPalPetrol, oplPalDiesel, oplEmPetrol, oplEmDiesel]
'''
S["extra_run"] = S["extra_run"] + ["exciseRuleCharges fuelCharges g"]
S["guards"] = S["guards"] + [
  "heatingOil.dutyOn { good := .heatingOil, amount := 3000, quantity := 1000000 } {} == 232",
  "oplPalPetrol.dutyOn { good := .petrol, amount := 6000, quantity := 1000000 } {} == 202",
  "oplPalDiesel.dutyOn { good := .diesel, amount := 6000, quantity := 1000000 } {} == 436",
  "oplEmPetrol.dutyOn { good := .petrol, amount := 6000, quantity := 1000000 } {} == 80",
  "oplEmDiesel.dutyOn { good := .diesel, amount := 6000, quantity := 1000000 } {} == 80"]
S["notes"] = S["notes"] + ["PL 5121: opłata paliwowa (M.P. 2024 poz. 1034) and opłata emisyjna (POŚ art. 321f) booked as separate 5121 charges (FT review, third pass)"]
for _t in S["taxes"]:
    if _t.get("tax") == "Akcyza (paliwa silnikowe)":
        _t["tax"] = "Akcyza (paliwa silnikowe, oleje opałowe)"
        _t["statute"] = "ustawa o podatku akcyzowym art. 89 ust. 1 pkt 2, 6, 9"
        _t["unsupported"] = ["LPG, electricity"]
S["taxes"] = S["taxes"] + [
 {"oecd": "5121", "tax": "Opłata paliwowa", "statute": "ustawa o autostradach płatnych oraz o KFD art. 37h-37j, 37m ust. 4", "dated": "M.P. 2024 poz. 1034 (2025 rates)", "grade": "A", "kernel_parts": ["ExciseRule"], "unsupported": ["LPG and gases (246,87 zł/1000 kg)"]},
 {"oecd": "5121", "tax": "Opłata emisyjna", "statute": "Prawo ochrony środowiska art. 321a-321f", "dated": "t.j. Dz.U. 2025 poz. 647", "grade": "A", "kernel_parts": ["ExciseRule"], "unsupported": []}]


# ---- FT review (2026-11-21, third pass): water and newspapers 8 % (ftd_ec_tedb_vat_2025 dev; IMPROVE_FT D3-7) ----
S["doc"] += """
## FT review (2026-11-21, third pass): water and newspapers
Same t.j. (`pl/law/vat_tj2024.txt`), **załącznik nr 3** (rate of art. 41 ust. 2, 8 % under art. 146ef): poz. 16 "ex 2201
Wody ... wyłącznie woda dostarczana za pośrednictwem sieci wodociągowych, cysternami lub innymi środkami transportu";
poz. 24 "36.00.20.0 Usługi związane z uzdatnianiem i dostarczaniem wody za pośrednictwem sieci wodociągowych"; poz. 17
"ex 4902 Gazety, dzienniki i czasopisma, nawet ilustrowane lub zawierające materiały reklamowe – z wyłączeniem czasopism
regionalnych lub lokalnych" (those are 5 %, załącznik nr 10). The model had both at 23 %.
"""
S["vat"]["classes"]["water"] = "reduced"
S["vat"]["classes"]["newspapers"] = "reduced"
S["unsupported"] = S["unsupported"] + [("g.consumption.any (fun s => s.good == .newspapers)", "newspapers at 8 % (zał. 3 poz. 17); regional or local periodicals are 5 % (zał. 10), specialist periodicals as listed")]
S["guards"] = S["guards"] + ["vat.embedded { good := .water, amount := 108 } == 8", "vat.embedded { good := .newspapers, amount := 108 } == 8"]

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
