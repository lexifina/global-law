# pass 10 rows (R1 Europe, 2026-11-21): vehicle taxes (kernel 2.4.0 VehicleTax), conditional withholding (StateWht),
# remaining withholding, carry-overs. exec'd by the spec after p6lib.py, p8_rows.py and p9_rows.py (helpers _q, _wx,
# _first8, _pay8, _ind9, _co9). Statute rows quote or cite the act read (grade A); official guides are grade B.


# ---------------------------------------------------------------- 1. vehicle taxes (5200)
def _vstart(S, rest_tax, rest_unlock):
    """First vehicle family of a country in pass 10: drop the grade-C 5200 entry and its model-level line, add a
    'rest' C entry naming the parts not modelled."""
    S.setdefault("families", []); S.setdefault("notes", []); S.setdefault("guards", []); S.setdefault("unsupported", [])
    S["families"] = list(S["families"] or [])
    S["imports"] = sorted(set(S.get("imports", []) + ["TaxKernel.Global2"]))
    S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == "5200" and t.get("grade") == "C")]
    S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("5200")]
    S["taxes"].append({"oecd": "5200", "tax": "Other taxes on use of goods (rest)", "statute": "", "dated": "", "grade": "C",
                       "status": "unsupported", "kernel_parts": [], "tried": "pass 10: " + rest_tax,
                       "unsupported": ["would unlock: " + rest_unlock]})


def _vfam(S, name, lean, ts, statute, dated, grade, src, facts, uns, guards, rest_veh, registration=False):
    """One VehicleTax family (first rule that computes, per vehicle). Model-level grade-C lines: a vehicle lacking an
    attribute the selected rule needs; a vehicle no rule selects (for a registration tax: only vehicles registered in the
    year)."""
    S["lean"] = (S.get("lean") or "") + lean
    S["families"].append((f"5200 {name} (pass 10)", [".useOfGoods"], f"vehicleTaxCharges {ts} g (firstOnly := true)"))
    um = (f"g.vehicles.any (fun v => v.newReg && !({ts}.any (·.selects g.year v)))" if registration
          else f"!(vehicleTaxUnmatched {_q(name)} {ts} g).isEmpty")
    S["unsupported"] += [(f"!(vehicleTaxUnknown {_q(name)} {ts} g).isEmpty", f"5200 {name}: a vehicle lacks an attribute the rate needs (grade C)"),
                         (um, f"5200 {name}: a vehicle no rule reaches: {rest_veh} (grade C)")] + list(uns)
    S["guards"] += list(guards)
    S["notes"].append(f"{S['cc']} 5200 {name} pass 10: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "5200", "tax": name, "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["VehicleTax (2.4.0)", "QtyTable"], "unsupported": [rest_veh] + [t for _, t in uns]})
    S["doc"] += f"\n\n## 5200 {name} (pass 10, kernel 2.4.0, grade {grade})\nSource: {src}.\n" + "".join(f"* {x}\n" for x in facts)


_NL_MRB = """
/-- Wet MRB 1994 art. 23 lid 1 (personenauto), per three months, in cents, for the eigen massa rounded by art. 22 lid 1 b 1° -/
def p10nlBase (r : Int) : Int :=
  if r ≤ 500 then 2086 else if r ≤ 600 then 2830 else if r ≤ 700 then 3596 else if r ≤ 800 then 4694
  else if r ≤ 3200 then 6243 + 1678 * ((r - 900) / 100) else 46076 + 1166 * ((r - 3300) / 100)
/-- art. 23 lid 2 a: brandstoftoeslag dieselolie (cents per three months) -/
def p10nlDiesel (r : Int) : Int :=
  if r ≤ 500 then 8177 else if r ≤ 600 then 9678 else if r ≤ 700 then 11179 else if r ≤ 800 then 12707
  else 14869 + 1610 * ((r - 900) / 100)
/-- art. 23 lid 2 b: brandstoftoeslag, other fuels (cents per three months) -/
def p10nlOther (r : Int) : Int :=
  if r ≤ 500 then 9593 else if r ≤ 600 then 11499 else if r ≤ 700 then 13406 else if r ≤ 800 then 15310
  else 16723 + 1771 * ((r - 900) / 100)
/-- art. 23 lid 3: CNG / LNG: nihil to 800 kg, 18,51 at 900 kg plus 18,51 per 100 kg above (cents per three months) -/
def p10nlGas (r : Int) : Int := if r ≤ 800 then 0 else 1851 + 1851 * ((r - 900) / 100)
/-- A year (four periods of three months, cents) on the eigen massa in kg: art. 22 lid 1 b 1° rounds to the nearest
100 kg, 50 kg down, so the band of r kg starts at r − 49 kg -/
def p10nlYear (f : Int → Int) : QtyTable :=
  { bands := (List.range 120).map fun (i : Nat) => let j : Int := i; (if i == 0 then (0 : Int) else 451 + 100 * j, 4 * f (500 + 100 * j)) }
def p10nlCar (fs : List VehicleFuel) (ps : List (VehicleAttr × QtyTable)) (bp : Int) (st : String) (f t : Nat := 0)
    (w : List (VehicleAttr × Int × Int) := []) : VehicleTax :=
  { name := "Motorrijtuigenbelasting (hoofdsom)", kinds := ["car"], fuels := fs, regFrom := f, regTo := t, when := w,
    parts := ps, multiplierBp := bp, statute := st }
/-- multiplierBp: cents to euros (100), × 1/4 (25) or 3/4 (75) by art. 23b, × 1,19 (119) by art. 23 lid 4 -/
def p10nlVeh : List VehicleTax :=
  [p10nlCar [.electric, .hydrogen] [(.massKg, p10nlYear p10nlBase)] 25 "Wet MRB 1994 art. 23b lid 1 a: CO2 0 g/km, a quarter of the art. 23 tax",
   p10nlCar [.pluginHybrid] [(.massKg, p10nlYear p10nlBase)] 75 "Wet MRB 1994 art. 23b lid 1 b: CO2 above 0 up to 50 g/km, three quarters of the art. 23 tax" (w := [(.co2GKm, 0, 50)]),
   p10nlCar [.petrol, .hybrid, .pluginHybrid] [(.massKg, p10nlYear p10nlBase)] 100 "Wet MRB 1994 art. 22 lid 1 b, art. 23 lid 1 (benzine: no brandstoftoeslag, lid 2)",
   p10nlCar [.diesel] [(.massKg, p10nlYear p10nlBase), (.massKg, p10nlYear p10nlDiesel)] 119 "Wet MRB 1994 art. 23 lid 1, 2 a, 4, 5: brandstoftoeslag diesel and fijnstoftoeslag 19 % (presumed for a first admission before 1 September 2009)" (t := 2008),
   p10nlCar [.diesel] [(.massKg, p10nlYear p10nlBase), (.massKg, p10nlYear p10nlDiesel)] 100 "Wet MRB 1994 art. 23 lid 1, 2 a: brandstoftoeslag diesel" (f := 2009),
   p10nlCar [.cng] [(.massKg, p10nlYear p10nlBase), (.massKg, p10nlYear p10nlGas)] 100 "Wet MRB 1994 art. 23 lid 1, 3: CNG/LNG",
   p10nlCar [.other] [(.massKg, p10nlYear p10nlBase), (.massKg, p10nlYear p10nlOther)] 100 "Wet MRB 1994 art. 23 lid 1, 2 b: other fuels"]
"""

_ES_IEDMT = """
def p10esIedmtR (lo hi bp : Int) (st : String) : VehicleTax :=
  { name := "Impuesto especial sobre determinados medios de transporte", kinds := ["car"], occasion := .registration,
    when := [(.co2GKm, lo, hi)], parts := [(.value, QtyTable.perUnit bp 10000)], statute := st }
/-- Ley 38/1992 art. 69 a), 70 (Península e Illes Balears, no autonomous rates): first definitive registration in Spain -/
def p10esIedmt : List VehicleTax :=
  [{ name := "Impuesto especial sobre determinados medios de transporte", kinds := ["car"], occasion := .registration,
     fuels := [.electric, .hydrogen], statute := "Ley 38/1992 art. 70.1 epígrafe 1.º b), 70.2 b): a single motor that is not of internal combustion, 0 por 100" },
   { name := "Impuesto especial sobre determinados medios de transporte", kinds := ["car"], occasion := .registration,
     when := [(.co2GKm, -1, 120)], statute := "Ley 38/1992 art. 70.1 epígrafe 1.º a), 70.2 b): CO2 not above 120 g/km, 0 por 100" },
   p10esIedmtR 120 159 475 "Ley 38/1992 art. 69 a), 70.1 epígrafe 2.º, 70.2 b): CO2 above 120 and below 160 g/km, 4,75 por 100",
   p10esIedmtR 159 199 975 "Ley 38/1992 art. 69 a), 70.1 epígrafe 3.º, 70.2 b): CO2 from 160 to below 200 g/km, 9,75 por 100",
   p10esIedmtR 199 1000000 1475 "Ley 38/1992 art. 69 a), 70.1 epígrafe 4.º a), 70.2 b): CO2 of 200 g/km or more, 14,75 por 100"]
/-- TRLRHL art. 95.1 A) turismos, in cents, by caballos fiscales (whole CVF): below 8, 8-11,99, 12-15,99, 16-19,99, 20 and more -/
def p10esIvtmT : QtyTable := QtyTable.ofCeilings [(7, 1262), (11, 3408), (15, 7194), (19, 8961)] 11200
def p10esIvtm : List VehicleTax :=
  [{ name := "Impuesto sobre vehículos de tracción mecánica", kinds := ["car"], parts := [(.fiscalHp, p10esIvtmT)],
     multiplierBp := 100, level := .local,
     statute := "TRLRHL (RDLeg. 2/2004) art. 95.1 A): cuadro de tarifas, turismos (without a municipal coefficient, art. 95.4)" }]
"""


def _fr_malus_lean():
    tab = [(113, 50), (114, 75), (115, 100), (116, 125), (117, 150), (118, 170), (119, 190), (120, 210), (121, 230), (122, 240),
           (123, 260), (124, 280), (125, 310), (126, 330), (127, 360), (128, 400), (129, 450), (130, 540), (131, 650), (132, 740),
           (133, 818), (134, 898), (135, 983), (136, 1074), (137, 1172), (138, 1276), (139, 1386), (140, 1504), (141, 1629),
           (142, 1761), (143, 1901), (144, 2049), (145, 2205), (146, 2370), (147, 2544), (148, 2726), (149, 2918), (150, 3119),
           (151, 3331), (152, 3552), (153, 3784), (154, 4026), (155, 4279), (156, 4543), (157, 4818), (158, 5105), (159, 5404),
           (160, 5715), (161, 6126), (162, 6537), (163, 7248), (164, 7959), (165, 8770), (166, 9681), (167, 10692), (168, 11803),
           (169, 13014), (170, 14325), (171, 15736), (172, 17247), (173, 18858), (174, 20569), (175, 22380), (176, 24291),
           (177, 26302), (178, 28413), (179, 30624), (180, 32935), (181, 35346), (182, 37857), (183, 40468), (184, 43179),
           (185, 45990), (186, 48901), (187, 51912), (188, 55023), (189, 58134), (190, 61245), (191, 64356), (192, 67467)]
    body = ", ".join(f"({g}, {a})" for g, a in [(112, 0)] + tab)
    return tab, f"""
/-- CIBS L. 421-62, barème WLTP for vehicles first registered from 1 March to 31 December 2025 (euros): below 113 g/km 0,
113 g/km 50, …, 192 g/km 67 467, above 192 g/km 70 000 -/
def p10frMalus : QtyTable := QtyTable.ofCeilings [{body}] 70000
def p10frVeh : List VehicleTax :=
  [{{ name := "Taxe sur les émissions de CO2 des véhicules de tourisme (malus)", kinds := ["car"], occasion := .registration,
     fuels := [.electric, .hydrogen], statute := "CIBS L. 421-67: a vehicle whose energy source is exclusively electricity, hydrogen or both is exempt" }},
   {{ name := "Taxe sur les émissions de CO2 des véhicules de tourisme (malus)", kinds := ["car"], occasion := .registration,
     regFrom := 2025, regTo := 2025, parts := [(.co2GKm, p10frMalus)],
     statute := "CIBS L. 421-59 1°, L. 421-62: barème WLTP of the year of first registration (2025, from 1 March 2025)" }}]
/-- CIBS L. 421-38: taxe fixe on the issue of a registration certificate, 11 € -/
def p10frFixe : List VehicleTax :=
  [{{ name := "Taxe fixe sur les certificats d'immatriculation", occasion := .registration, fixed := 11,
     statute := "CIBS L. 421-30 1°, L. 421-38: 11 €" }}]
"""


def _nl_mrb_py(m, fuel, year=2021, co2=120):
    def R(m):
        return 500 if m <= 550 else 500 + 100 * ((m - 551) // 100 + 1)
    def base(r):
        if r <= 500: return 2086
        if r <= 600: return 2830
        if r <= 700: return 3596
        if r <= 800: return 4694
        if r <= 3200: return 6243 + 1678 * ((r - 900) // 100)
        return 46076 + 1166 * ((r - 3300) // 100)
    def dsl(r):
        return {500: 8177, 600: 9678, 700: 11179, 800: 12707}.get(r) if r <= 800 else 14869 + 1610 * ((r - 900) // 100)
    r = R(m)
    if fuel == "electric":
        return 4 * base(r) * 25 // 10000
    if fuel == "diesel":
        c = 4 * (base(r) + dsl(r))
        return c * (119 if year <= 2008 else 100) // 10000
    return 4 * base(r) * 100 // 10000


def _veh10(S):
    cc = S["cc"]
    if S.get("fam") != "Other" or not any(str(t.get("oecd")) == "5200" and t.get("grade") == "C" and "rest" not in t.get("tax", "") for t in S["taxes"]):
        return
    if cc == "NL":
        _vstart(S, "motorrijtuigenbelasting (hoofdsom) on cars modelled; provinciale opcenten, BPM and the other vehicle classes not modelled",
                "Provinciewet art. 222 and the 2025 opcenten of a reference province; Wet BPM 1992 art. 9 (CO2 table) with the list price; Wet MRB art. 24-25 (bestelauto, motorrijwiel)")
        g = [f"(p10nlYear p10nlBase).amount 550 == 8344", "(p10nlYear p10nlBase).amount 551 == 11320",
             "(p10nlYear p10nlBase).amount 1320 == 51820", "(p10nlYear p10nlBase).amount 1350 == 51820", "(p10nlYear p10nlBase).amount 1351 == 58532",
             "(p10nlYear p10nlDiesel).amount 1320 == 85236", "(p10nlYear p10nlBase).amount 3400 == 188968",
             f"(p10nlVeh[2]!).amount 2025 {{ kind := \"car\", massKg := 1320, fuel := .petrol, firstRegYear := 2021 }} == {_nl_mrb_py(1320, 'petrol')}",
             f"(p10nlVeh[4]!).amount 2025 {{ kind := \"car\", massKg := 1320, fuel := .diesel, firstRegYear := 2015 }} == {_nl_mrb_py(1320, 'diesel', 2015)}",
             f"(p10nlVeh[3]!).amount 2025 {{ kind := \"car\", massKg := 1320, fuel := .diesel, firstRegYear := 2007 }} == {_nl_mrb_py(1320, 'diesel', 2007)}",
             f"(p10nlVeh[0]!).amount 2025 {{ kind := \"car\", massKg := 1800, fuel := .electric, firstRegYear := 2023 }} == {_nl_mrb_py(1800, 'electric')}",
             "((p10nlVeh.filter (·.computes 2025 { kind := \"car\", massKg := 1320, fuel := .diesel, firstRegYear := 2015 })).head!).multiplierBp == 100",
             "(p10nlVeh.filter (·.selects 2025 { kind := \"car\", massKg := 1320, fuel := .lpg, firstRegYear := 2015 })).isEmpty"]
        _vfam(S, "Motorrijtuigenbelasting", _NL_MRB, "p10nlVeh",
              "Wet op de motorrijtuigenbelasting 1994 art. 22, 23, 23b", "wetten.overheid.nl, geldend op 1 juli 2025 (`nl/law/mrb_g2025.txt`)", "A",
              "Wet op de motorrijtuigenbelasting 1994, wetten.overheid.nl, geldig op 01-07-2025 (`nl/law/mrb_g2025.txt`)",
              ["art. 23 lid 1: per period of three months, 20,86 EUR (500 kg or less), 28,30 (600), 35,96 (700), 46,94 (800), 62,43 at 900 kg plus 16,78 per 100 kg above 900 kg up to 3200 kg, 460,76 at 3300 kg plus 11,66 per 100 kg above",
               "art. 22 lid 1 b 1°: the eigen massa is rounded to the nearest 100 kg, 50 kg rounded down",
               "art. 23 lid 2: a brandstoftoeslag except for cars driven only by petrol, electricity, hydrogen or a combination: a. diesel 81,77 (500 kg) to 148,69 at 900 kg plus 16,10 per 100 kg; b. other fuels 95,93 to 167,23 plus 17,71; lid 3: CNG/LNG and factory LPG nil to 800 kg, then 18,51 plus 18,51 per 100 kg",
               "art. 23 lid 4, 5: diesel cars with particulate emissions above 5 mg/km pay 19 % more; without a registered value and a first admission before 1 September 2009 they are presumed above",
               "art. 23b lid 1: CO2 0 g/km pays a quarter, above 0 up to 50 g/km three quarters of the art. 23 tax",
               "the model books the hoofdsom (rijksdeel) for a year (four periods), rounded down to whole euros once; the provincial opcenten are not modelled"],
              [("g.vehicles.any (fun v => v.fuel == .diesel && 2009 ≤ v.firstRegYear)", "5200 Motorrijtuigenbelasting: a diesel car first admitted from 2009 is taken as emitting at most 5 mg/km of particulates (no fijnstoftoeslag, art. 23 lid 4); 2009 is read as from 1 September"),
               ("g.vehicles.any (fun v => v.fuel == .hybrid || v.fuel == .pluginHybrid)", "5200 Motorrijtuigenbelasting: a hybrid is taken as petrol-electric (no brandstoftoeslag, art. 23 lid 2)"),
               ("g.vehicles.any (fun v => v.fuel == .pluginHybrid && v.co2GKm < 0)", "5200 Motorrijtuigenbelasting: a plug-in hybrid without CO2 is booked at the full art. 23 tax (art. 23b lid 1 b not tested)"),
               ("!g.vehicles.isEmpty", "5200 Motorrijtuigenbelasting: provinciale opcenten (Provinciewet art. 222) not modelled (grade C)")],
              g, "LPG cars (art. 23 lid 2 b or 3 by installation type), bestelauto, motorrijwiel, vrachtauto, autobus")
    elif cc == "ES":
        _vstart(S, "IEDMT (new cars, national rates) and IVTM (art. 95.1 tariff) modelled; IVTM municipal coefficient, IEDMT on used cars and other classes not modelled",
                "the reference municipality's IVTM ordinance (coefficient, art. 95.4; bonificaciones, art. 95.6); the Orden HFP of average prices for used cars; autonomous IEDMT rates")
        _vfam(S, "Impuesto especial sobre determinados medios de transporte", _ES_IEDMT, "p10esIedmt",
              "Ley 38/1992 de Impuestos Especiales art. 65, 69 a), 70", "BOE texto consolidado, fetched 2026-11-21 (`es/law/iedmt_ley38_1992.txt`)", "A",
              "Ley 38/1992, de 28 de diciembre, de Impuestos Especiales, BOE-A-1992-28741, texto consolidado (`es/law/iedmt_ley38_1992.txt`); TRLRHL, BOE-A-2004-4214 (`es/law/trlrhl.txt`)",
              ["art. 69 a): for new means of transport the base is the VAT base of the acquisition",
               "art. 70.1: epígrafe 1.º a) CO2 not above 120 g/km, b) a single motor that is not of internal combustion; 2.º above 120 and below 160; 3.º from 160 to below 200; 4.º a) 200 or more, b) emissions required but not proven",
               "art. 70.2 b) (where the autonomous community has approved no rates), Península e Illes Balears: 0,00 / 4,75 / 9,75 / 14,75 por 100 (Canarias 0 / 3,75 / 8,75 / 13,75)",
               "TRLRHL art. 95.1 A) turismos: below 8 caballos fiscales 12,62 EUR, 8-11,99 34,08, 12-15,99 71,94, 16-19,99 89,61, 20 and more 112,00; art. 95.4: municipalities may raise the tariff by a coefficient up to 2"],
              [("g.vehicles.any (fun v => v.newReg)", "5200 IEDMT: the vehicle's value is taken as the VAT base of its acquisition (art. 69 a)); a used car first registered in Spain (art. 69 b), market value) is not distinguished; Península rates (no Canarias, no autonomous rates)")],
              ["(p10esIedmtR 120 159 475 \"\").amount 2025 { kind := \"car\", co2GKm := 140, value := 30000, firstRegYear := 2025 } == 1425",
               "((p10esIedmt.filter (·.computes 2025 { kind := \"car\", co2GKm := 120, value := 30000, fuel := .petrol, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 120, value := 30000, fuel := .petrol, firstRegYear := 2025 } == 0",
               "((p10esIedmt.filter (·.computes 2025 { kind := \"car\", co2GKm := 160, value := 30000, fuel := .petrol, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 160, value := 30000, fuel := .petrol, firstRegYear := 2025 } == 2925",
               "((p10esIedmt.filter (·.computes 2025 { kind := \"car\", co2GKm := 200, value := 30000, fuel := .diesel, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 200, value := 30000, fuel := .diesel, firstRegYear := 2025 } == 4425",
               "(p10esIedmt.filter (·.computes 2025 { kind := \"car\", co2GKm := 150, value := 30000, fuel := .petrol, firstRegYear := 2020 })).isEmpty"],
              "cars without CO2 (epígrafe 4.º b) applies only where the measurement is required and not proven), motorcycles, other vehicles", registration=True)
        _vfam(S, "Impuesto sobre vehículos de tracción mecánica", "", "p10esIvtm",
              "TRLRHL (RDLeg. 2/2004) art. 95.1 A)", "BOE texto consolidado, fetched 2026-11-21 (`es/law/trlrhl.txt`)", "A",
              "Texto refundido de la Ley Reguladora de las Haciendas Locales, BOE-A-2004-4214 (`es/law/trlrhl.txt`)",
              ["the IVTM is booked at the art. 95.1 tariff (the statutory minimum); the reference municipality's coefficient (art. 95.4, up to 2) and bonificaciones (art. 95.6) are not read"],
              [("!g.vehicles.isEmpty", "5200 IVTM: the municipal coefficient (TRLRHL art. 95.4) and bonificaciones (art. 95.6) are not applied: the art. 95.1 tariff is booked (grade C for the municipal part)"),
               ("g.vehicles.any (fun v => v.months < 12)", "5200 IVTM: part-year prorating is by quarters (art. 96.3), the model prorates by months")],
              ["p10esIvtmT.amount 7 == 1262", "p10esIvtmT.amount 11 == 3408", "p10esIvtmT.amount 12 == 7194", "p10esIvtmT.amount 20 == 11200",
               "(p10esIvtm.head!).amount 2025 { kind := \"car\", fiscalHp := 11, fuel := .petrol, firstRegYear := 2019 } == 34"],
              "vehicles other than turismos (autobuses, camiones, tractores, remolques, ciclomotores y motocicletas)")
    elif cc == "FR":
        tab, lean = _fr_malus_lean()
        _vstart(S, "malus CO2 (2025 barème, new cars) and taxe fixe modelled; taxe régionale, malus au poids and the annual taxes on company cars not modelled",
                "the regional tariff per cheval administratif (L. 421-41 ff., regional deliberations); CIBS L. 421-71 ff. (masse en ordre de marche) with the mass in running order; L. 421-93 ff. (company cars)")
        d = dict(tab)
        _vfam(S, "Taxe sur les émissions de CO2 des véhicules de tourisme (malus)", lean, "p10frVeh",
              "CIBS L. 421-58, L. 421-59, L. 421-62 (barème 2025), L. 421-67", "barème from 1 March 2025 (service-public.gouv.fr, vérifié le 21 février 2026); L. 421-59, L. 421-67 Légifrance via the Internet Archive (2024-02-23)", "B",
              "Barème from Service Public (DILA), page F35947 \"Taxe sur les émissions de CO2 des véhicules de tourisme (malus CO2)\", table for 1 March - 31 December 2025, WLTP (Légifrance answers 403 and the Internet Archive holds no capture of L. 421-62 in its 2025 wording); L. 421-58 to L. 421-67 read in `fr/law/cibs_wb/LEGISCTA000044599051.html` and `LEGISCTA000044599077.html`",
              ["L. 421-59: the tax is a tariff per vehicle set by its CO2 emissions in the barème of the year of first registration (WLTP: L. 421-62)",
               "barème 2025 (from 1 March 2025): below 113 g/km 0 EUR; 113 g/km 50; 130 g/km 540; 150 g/km 3 119; 170 g/km 14 325; 192 g/km 67 467; above 192 g/km 70 000 (every gram in the table)",
               "L. 421-67: a vehicle whose energy source is exclusively electricity, hydrogen or both is exempt",
               "L. 421-60: 10 % less per started period of twelve months since first registration (used vehicles first registered abroad); L. 421-61 bis cap at 50 % of the price including taxes; L. 421-68 E85 abatements; family abatements: not applied (listed)",
               "January and February 2025 used the 2024 barème (threshold 118 g/km, `cibs_wb/LEGISCTA000044599051.html`): not split"],
              [("g.vehicles.any (fun v => v.newReg && 0 ≤ v.value && 2 * p10frMalus.amount v.co2GKm > v.value)", "5200 malus: the cap at 50 % of the price including taxes (L. 421-61 bis) is not applied (grade C)"),
               ("g.vehicles.any (fun v => v.newReg && v.firstRegYear == 2025)", "5200 malus: the barème from 1 March 2025 is booked for the whole year; family, disability and E85 abatements (L. 421-65 ff., L. 421-68) are not applied")],
              ["p10frMalus.amount 112 == 0", f"p10frMalus.amount 113 == {d[113]}", f"p10frMalus.amount 130 == {d[130]}", f"p10frMalus.amount 192 == {d[192]}",
               "p10frMalus.amount 193 == 70000", "p10frMalus.amount 0 == 0",
               f"(p10frVeh[1]!).amount 2025 {{ kind := \"car\", co2GKm := 150, fuel := .petrol, firstRegYear := 2025 }} == {d[150]}",
               "(p10frVeh.filter (·.selects 2025 { kind := \"car\", co2GKm := 150, fuel := .petrol, firstRegYear := 2022, newReg := true })).isEmpty"],
              "vehicles first registered before 2025 and registered in France in 2025 (used imports: earlier barèmes, L. 421-60 décote), NEDC and non-EU-approved vehicles (L. 421-63, 421-64), vehicles other than cars", registration=True)
        _vfam(S, "Taxe fixe sur les certificats d'immatriculation", "", "p10frFixe",
              "CIBS L. 421-30 1°, L. 421-37, L. 421-38", "Légifrance via the Internet Archive (2025-01-24)", "A",
              "CIBS L. 421-37 to L. 421-40, Légifrance via the Internet Archive (`fr/law/cibs_wb/LEGISCTA000044598993.html`)",
              ["L. 421-38: \"Le montant de la taxe est égal à 11 €\"; L. 421-39, 421-40: exempt certificates (address update, corrections, storm replacements)",
               "booked once for each vehicle registered in the year; a change of holder of a used vehicle is not in the input"],
              [], ["(p10frFixe.head!).amount 2025 { kind := \"car\", firstRegYear := 2025 } == 11"],
              "none (every vehicle registered in the year)", registration=True)


# AT: motorbezogene Versicherungssteuer (VersStG 1953 § 6 (1) Z 2, monthly, booked x 12 in cents) and NoVA (NoVAG 1991 § 6 (2), (7))
_AT_DED = [(2021, 64, 112, 16), (2022, 63, 109, 15), (2023, 62, 106, 14), (2024, 61, 103, 13), (2025, 60, 100, 12)]


def _at_lean():
    rows = []
    for y, a, b, p in _AT_DED:
        rows.append(f"p10atC [.petrol, .diesel, .hybrid, .lpg, .cng, .other] {y} (p10atMin5 {a}) (p10atMin5 {b}) \"VersStG 1953 § 6 (1) Z 2 lit. c sublit. bb, cc: first registration {y}: 0,72 EUR per kW above {a} kW and per g CO2/km above {b} g (at least 5 each), a month\"")
        rows.append(f"p10atC [.pluginHybrid] {y} (p10atMin5 {a}) (p10atMin5 {p}) \"VersStG 1953 § 6 (1) Z 2 lit. c sublit. aa, cc: first registration {y}: 0,72 EUR per kW above {a} kW and per g weighted CO2/km above {p} g (at least 5 each), a month\"")
    body = ",\n   ".join(rows)
    return f"""
/-- VersStG 1953 § 6 (1) Z 2 lit. c: 0,72 EUR a month per unit above a deduction, at least 5 units: a year in cents -/
def p10atMin5 (d : Int) : QtyTable := {{ bands := [(0, 4320)], steps := [(d + 5, 864)] }}
def p10atC (fs : List VehicleFuel) (y : Nat) (kw co2 : QtyTable) (st : String) : VehicleTax :=
  {{ name := "Motorbezogene Versicherungssteuer", kinds := ["car"], fuels := fs, regFrom := y, regTo := y,
    parts := [(.engineKw, kw), (.co2GKm, co2)], multiplierBp := 100, statute := st }}
/-- § 6 (1) Z 2 lit. a: electric, per kW of the power less 45 kW (at least 10): 0,25 / 0,35 / 0,45 EUR; per kg of the
own weight less 900 kg (at least 200): 0,015 / 0,030 / 0,045 EUR, a month (a year in cents) -/
def p10atEvKw : QtyTable := {{ bands := [(0, 3000)], steps := [(55, 300), (80, 420), (105, 540)] }}
def p10atEvKg : QtyTable := {{ bands := [(0, 3600)], steps := [(1100, 18), (1400, 36), (2100, 54)] }}
/-- § 6 (1) Z 2 lit. b: first registered before 1 October 2020, per kW of the power less 24 kW: 0,62 (66 kW) / 0,66
(20 kW) / 0,75 EUR a month, at least 6,20 EUR (a year in cents) -/
def p10atOld : QtyTable := {{ steps := [(24, 744), (90, 792), (110, 900)] }}
def p10atVeh : List VehicleTax :=
  [{{ name := "Motorbezogene Versicherungssteuer", kinds := ["car"], fuels := [.electric], parts := [(.engineKw, p10atEvKw), (.massKg, p10atEvKg)],
     multiplierBp := 100, statute := "VersStG 1953 § 6 (1) Z 2 lit. a: rein elektrischer Antrieb, kW and own weight" }},
   {body},
   {{ name := "Motorbezogene Versicherungssteuer", kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .other],
     regTo := 2020, parts := [(.engineKw, p10atOld)], multiplierBp := 100, minAmount := 74,
     statute := "VersStG 1953 § 6 (1) Z 2 lit. b: first registered before 1 October 2020, kW less 24, at least 6,20 EUR a month" }}]
/-- NoVAG 1991 § 6 (2), (7) for 2025: rate (CO2 − 94) / 5 per cent, rounded to whole per cent (r % for CO2 from 92 + 5r
to 96 + 5r g/km; § 6 (7): the CO2 deduction falls by 3 from 1 January 2025, 97 − 3 = 94), at most 80 %; plus 80 EUR per g/km above 155; less 350 EUR; never below 0 -/
def p10atNovaR (r : Int) : VehicleTax :=
  {{ name := "Normverbrauchsabgabe", kinds := ["car"], occasion := .registration,
    when := [(.co2GKm, 91 + 5 * r, if r == 80 then 1000000 else 96 + 5 * r)],
    fixed := -350, parts := [(.value, QtyTable.perUnit r 100), (.co2GKm, {{ steps := [(155, 80)] }})],
    statute := s!"NoVAG 1991 § 6 (2), (7): {{r}} % of the net price, malus 80 EUR per g/km above 155, less 350 EUR" }}
def p10atNova : List VehicleTax :=
  {{ name := "Normverbrauchsabgabe", kinds := ["car"], occasion := .registration, when := [(.co2GKm, -1, 96)],
     fixed := -350, parts := [(.co2GKm, {{ steps := [(155, 80)] }})],
     statute := "NoVAG 1991 § 6 (2), (7): CO2 up to 96 g/km, 0 %; less 350 EUR; never below 0" }}
  :: (List.range 80).map (fun (i : Nat) => p10atNovaR ((i : Int) + 1))
"""


_SE_VEH = """
/-- Vägtrafikskattelag (2006:227) 2 kap. 8-10 §§ (öre a year; multiplierBp 100 gives kronor) -/
def p10seCar (fs : List VehicleFuel) (f t : Nat) (fixed : Int) (co2 : QtyTable) (st : String) : VehicleTax :=
  { name := "Fordonsskatt", kinds := ["car"], fuels := fs, regFrom := f, regTo := t, fixed := fixed,
    parts := [(.co2GKm, co2)], multiplierBp := 100, statute := st }
def p10seNonDiesel : List VehicleFuel := [.petrol, .hybrid, .pluginHybrid, .electric, .lpg, .hydrogen, .other]
def p10seVeh : List VehicleTax :=
  [p10seCar [.cng] 2006 0 36000 { steps := [(111, 1100)] } "2 kap. 7-9 §§: grundbelopp 360 kr, 11 kr per g CO2/km above 111 (gas other than LPG)",
   p10seCar p10seNonDiesel 2023 0 36000 { steps := [(75, 10700), (125, 13200)] } "2 kap. 7, 8, 9 a §§: first three years: 360 kr, 107 kr per g above 75 to 125, 132 kr per g above 125",
   p10seCar [.diesel] 2023 0 61000 { steps := [(0, 1352), (75, 12052), (125, 14552)] } "2 kap. 7, 8, 9 a, 10 §§: first three years, diesel: 360 kr + 107 / 132 kr per g + bränsletillägg 13,52 kr per g + miljötillägg 250 kr",
   p10seCar p10seNonDiesel 2006 2022 36000 { steps := [(111, 2200)] } "2 kap. 7-9 §§: grundbelopp 360 kr, 22 kr per g CO2/km above 111",
   p10seCar [.diesel] 2018 2022 61000 { steps := [(0, 1352), (111, 3552)] } "2 kap. 7 § tredje stycket, 8-10 §§: diesel of fordonsår 2018 or later: 360 kr + 22 kr per g above 111 + bränsletillägg 13,52 kr per g + miljötillägg 250 kr",
   p10seCar [.diesel] 2008 2017 110320 { steps := [(111, 5214)] } "2 kap. 7 § andra stycket, 8-10 §§: diesel: (360 kr + 22 kr per g above 111) x bränslefaktor 2,37 + miljötillägg 250 kr",
   p10seCar [.diesel] 2006 2007 135320 { steps := [(111, 5214)] } "2 kap. 7 § andra stycket, 8-10 §§: diesel: (360 kr + 22 kr per g above 111) x 2,37 + miljötillägg 500 kr (taxable before the end of 2007)"]
"""

_IE_VEH = """
/-- Finance (Excise Duties) (Vehicles) Act 1952, Schedule Part I para. 3 (o): M1 registered from 1 January 2021, WLTP CO2 -/
def p10ieO : QtyTable := QtyTable.ofCeilings [(0, 120), (50, 140), (80, 150), (90, 160), (100, 170), (110, 180), (120, 190),
  (130, 200), (140, 210), (150, 270), (160, 280), (170, 420), (190, 600), (200, 790), (225, 1250)] 2400
/-- para. 3 (d): M1 registered 1 July 2008 - 31 December 2020, CO2 (NEDC) -/
def p10ieD : QtyTable := QtyTable.ofCeilings [(0, 120), (80, 170), (100, 180), (110, 190), (120, 200), (130, 270), (140, 280),
  (155, 400), (170, 600), (190, 790), (225, 1250)] 2400
def p10ieVeh : List VehicleTax :=
  [{ name := "Motor tax", kinds := ["car"], regFrom := 2021, parts := [(.co2GKm, p10ieO)], level := .local,
     statute := "Finance (Excise Duties) (Vehicles) Act 1952, Sch. Part I para. 3 (o) (WLTP CO2 bands)" },
   { name := "Motor tax", kinds := ["car"], regFrom := 2008, regTo := 2020, parts := [(.co2GKm, p10ieD)], level := .local,
     statute := "Finance (Excise Duties) (Vehicles) Act 1952, Sch. Part I para. 3 (d) (CO2 bands)" }]
"""

_CZ_VEH = """
/-- Zákon o dani silniční 16/1993 Sb. § 2 (2) (od 1. 1. 2022): only N2, N3 and their trailers O3, O4 are taxable -/
def p10czVeh : List VehicleTax :=
  [{ name := "Daň silniční", kinds := ["car", "motorcycle", "van", "bus"],
     statute := "zákon 16/1993 Sb. § 2 odst. 2: zdanitelným vozidlem je silniční vozidlo kategorie N2 a N3 a přípojná vozidla O3, O4: cars, motorcycles, vans (N1) and buses are not taxable" }]
"""

_SK_VEH = """
/-- Zákon 361/2014 Z. z. príloha č. 1 (od 1. 1. 2025): M1 by cylinder capacity, EUR a year -/
def p10skCcm : QtyTable := QtyTable.ofCeilings [(150, 50), (900, 62), (1200, 80), (1500, 115), (2000, 148), (3000, 180)] 218
/-- § 7 (1): +10 % / 20 % / 30 % / 40 % / 50 % after 36 / 72 / 108 / 144 / 180 months (read by calendar years) -/
def p10skAge : List (Int × Int) := [(0, 10000), (3, 11000), (6, 12000), (9, 13000), (12, 14000), (15, 15000)]
def p10skVeh : List VehicleTax :=
  [{ name := "Daň z motorových vozidiel", kinds := ["car", "motorcycle"], fuels := [.electric],
     statute := "zákon 361/2014 Z. z. § 5 (1), príloha č. 1: a vehicle whose only energy source is electricity, 0 EUR" },
   { name := "Daň z motorových vozidiel", kinds := ["car", "motorcycle"], fuels := [.hybrid, .pluginHybrid, .cng, .hydrogen],
     parts := [(.engineCcm, p10skCcm)], ageFactors := p10skAge, multiplierBp := 5000,
     statute := "zákon 361/2014 Z. z. § 5 (2), § 6 (1), § 7 (1), (2), príloha č. 1: hybrid, CNG/LNG or hydrogen: 50 % less" },
   { name := "Daň z motorových vozidiel", kinds := ["car", "motorcycle"], fuels := [.petrol, .diesel, .lpg, .other],
     parts := [(.engineCcm, p10skCcm)], ageFactors := p10skAge,
     statute := "zákon 361/2014 Z. z. § 5 (2), § 6 (1), § 7 (1), príloha č. 1" }]
/-- § 2 (1): only a vehicle used for business is subject to the tax; a household's vehicle is not -/
def p10skHh : List VehicleTax :=
  [{ name := "Daň z motorových vozidiel", statute := "zákon 361/2014 Z. z. § 2 ods. 1: predmetom dane je vozidlo, ktoré sa používa na podnikanie: a household's vehicle is not subject" }]
"""


def _veh10b(S):
    cc = S["cc"]
    if S.get("fam") != "Other" or not any(str(t.get("oecd")) == "5200" and t.get("grade") == "C" and "rest" not in t.get("tax", "") for t in S["taxes"]):
        return
    if cc == "AT":
        _vstart(S, "motorbezogene Versicherungssteuer (cars) and NoVA (cars) modelled; motorcycles, vans, lorries (Kraftfahrzeugsteuer) not modelled",
                "VersStG § 6 (1) Z 1, 3 (motorcycles, N1); KfzStG 1992 (vehicles above 3,5 t); NoVAG § 6 (1) (motorcycles)")
        _vfam(S, "Motorbezogene Versicherungssteuer", _at_lean(), "p10atVeh",
              "Versicherungssteuergesetz 1953 § 6 (1) Z 2, (2)", "RIS, Fassung vom 1. Juli 2025 (`at/law/versstg_2025-07-01.txt`)", "A",
              "Versicherungssteuergesetz 1953, RIS Bundesrecht konsolidiert, Fassung vom 01.07.2025 (`at/law/versstg_2025-07-01.txt`)",
              ["§ 6 (1): the motorbezogene Versicherungssteuer is due \"für jeden Monat des Bestehens eines Versicherungsvertrages\" of the motor liability insurance; the model books twelve months",
               "Z 2 lit. a (electric): per kW of the power less 45 kW, 0,25 EUR for the first 35, 0,35 for the next 25, 0,45 above, at least 10 kW; plus per kg of the own weight less 900 kg, 0,015 / 0,030 / 0,045 EUR for 500 / 700 / above, at least 200 kg",
               "Z 2 lit. b (first registered before 1 October 2020): per kW of the power less 24 kW, 0,62 EUR for the first 66, 0,66 for the next 20, 0,75 above, at least 6,20 EUR",
               "Z 2 lit. c (first registered after 30 September 2020, WLTP): 0,72 EUR per kW of the power less a deduction and 0,72 EUR per g CO2/km less a deduction, at least 5 kW and 5 g; deductions by year of first registration: kW 65 (2020) to 60 (2025), CO2 115 to 100 (3 g a year), weighted CO2 of plug-in hybrids 17 to 12",
               "§ 6 (3): +6 / 8 / 10 % for half-yearly, quarterly or monthly payment of the premium: not applied (annual payment)"],
              [("g.vehicles.any (fun v => v.firstRegYear == 2020)", "5200 motorbezogene Versicherungssteuer: a car first registered in 2020 is taken under lit. b (before 1 October 2020)"),
               ("!g.vehicles.isEmpty", "5200 motorbezogene Versicherungssteuer: annual payment of the premium assumed (§ 6 (3) surcharges of 6-10 % not applied); the 6,20 EUR monthly minimum is booked as 74 EUR a year")],
              ["(p10atMin5 60).amount 110 == 43200", "(p10atMin5 100).amount 130 == 25920", "(p10atMin5 100).amount 90 == 4320",
               "p10atEvKw.amount 80 == 10500", "p10atEvKg.amount 2100 == 34200", "p10atEvKg.amount 1000 == 3600", "p10atOld.amount 100 == 57024",
               "((p10atVeh.filter (·.computes 2025 { kind := \"car\", engineKw := 110, co2GKm := 130, fuel := .petrol, firstRegYear := 2025 })).head!).amount 2025 { kind := \"car\", engineKw := 110, co2GKm := 130, fuel := .petrol, firstRegYear := 2025 } == 691",
               "((p10atVeh.filter (·.computes 2025 { kind := \"car\", engineKw := 85, fuel := .diesel, firstRegYear := 2015 })).head!).amount 2025 { kind := \"car\", engineKw := 85, fuel := .diesel, firstRegYear := 2015 } == 453"],
              "cars first registered after 2025, cars of 2021-2025 without WLTP CO2 (lit. d), motorcycles, vans, lorries")
        _vfam(S, "Normverbrauchsabgabe", "", "p10atNova",
              "Normverbrauchsabgabegesetz 1991 § 6 (2), (4), (7)", "RIS, Fassung vom 1. Juli 2025 (`at/law/novag_2025-07-01.txt`); § 6 (7) identical in the Fassung vom 31.12.2025 (`at/law/novag_2025-12-31.txt`)", "A",
              "Normverbrauchsabgabegesetz, RIS Bundesrecht konsolidiert, Fassung vom 01.07.2025 (`at/law/novag_2025-07-01.txt`)",
              ["§ 6 (2): rate in per cent = (CO2 g/km − 112) / 5, rounded to whole per cent, at most 50 %; above 200 g/km 50 EUR per g; less 350 EUR; no credit",
               "§ 6 (7): from 1 January 2022, for the last time on 1 January 2024, each year the CO2 deduction falls by 5, the malus threshold by 15, the malus amount rises by 10 and the top rate by 10 points (2024: 97 g/km, 155 g/km, 80 EUR, 80 %); the yearly fall of the CO2 deduction goes on from 1 January 2025 by 3: for 2025, 94 g/km, 155 g/km, 80 EUR, 80 % (pass 12: the model had 97, FT reviewer 6 R4-8)",
               "§ 6 (7) last sentence: a vehicle bought by an irrevocable written contract before 1 December 2024 and delivered before 1 April 2025 may keep the 2024 values (not modelled: the contract date is not an input)",
               "§ 6 (4): combined WLTP CO2 (weighted combined for plug-in hybrids)"],
              [("g.vehicles.any (fun v => v.newReg)", "5200 NoVA: the vehicle's value is taken as the net price (Bemessungsgrundlage, NoVAG § 5); a used car imported and first registered in Austria is taxed on the same table")],
              ["(p10atNovaR 7).amount 2025 { kind := \"car\", co2GKm := 130, value := 30000, firstRegYear := 2025, newReg := true } == 1750",
               "(p10atNovaR 13).amount 2025 { kind := \"car\", co2GKm := 160, value := 30000, firstRegYear := 2025, newReg := true } == 3950",
               "((p10atNova.filter (·.computes 2025 { kind := \"car\", co2GKm := 130, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 130, value := 30000, firstRegYear := 2025, newReg := true } == 1750",
               "((p10atNova.filter (·.computes 2025 { kind := \"car\", co2GKm := 99, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 99, value := 30000, firstRegYear := 2025, newReg := true } == 0",
               "((p10atNova.filter (·.computes 2025 { kind := \"car\", co2GKm := 100, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 100, value := 30000, firstRegYear := 2025, newReg := true } == 0",
               "((p10atNova.filter (·.computes 2025 { kind := \"car\", co2GKm := 105, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 105, value := 30000, firstRegYear := 2025, newReg := true } == 250",
               "((p10atNova.filter (·.computes 2025 { kind := \"car\", co2GKm := 96, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 96, value := 30000, firstRegYear := 2025, newReg := true } == 0",
               "((p10atNova.filter (·.computes 2025 { kind := \"car\", co2GKm := 117, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 117, value := 30000, firstRegYear := 2025, newReg := true } == 1150",
               "((p10atNova.filter (·.computes 2025 { kind := \"car\", co2GKm := 173, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := \"car\", co2GKm := 173, value := 30000, firstRegYear := 2025, newReg := true } == 5890"],
              "cars without CO2 (§ 6 (6) cylinder-capacity rule not modelled), motorcycles, vans", registration=True)
    elif cc == "SE":
        _vstart(S, "fordonsskatt on personbilar klass I modelled; other vehicle classes, the bonus and the 11 § reduction not modelled",
                "vägtrafikskattelag 2 kap. 12 § and bilaga 2 (heavy vehicles); bilaga 1 municipalities (11 §); cars before fordonsår 2006 (weight rates)")
        _vfam(S, "Fordonsskatt", _SE_VEH, "p10seVeh",
              "Vägtrafikskattelag (2006:227) 2 kap. 7, 8, 9, 9 a, 10 §§", "data.riksdagen.se, ändrad t.o.m. SFS 2025:1369; 9 a § as worded by Lag (2024:1134) (`se/law/vtsl2006_227.txt`)", "A",
              "Vägtrafikskattelag (2006:227), Riksdagen (`se/law/vtsl2006_227.txt`)",
              ["8 §: grundbelopp 360 kronor a year; 9 §: koldioxidbelopp 22 kronor per g CO2/km above 111 g (11 kronor for alcohol and gas other than LPG)",
               "9 a §: cars of fordonsår 2018 or later first taxable from 1 June 2022, for the first three years: 107 kronor per g above 75 up to 125 g and 132 kronor per g above 125 g (not for gas cars)",
               "7 §, 10 §: diesel cars: (grundbelopp + koldioxidbelopp) x bränslefaktor 2,37 + miljötillägg 250 kronor (500 if first taxable before the end of 2007); diesel of fordonsår 2018 first taxable from 1 July 2018: + bränsletillägg 13,52 kronor per g CO2/km + miljötillägg",
               "the first three years are read by calendar year: cars first registered 2023-2025 are inside them for all of 2025; the text is the consolidation to SFS 2025:1369 (amendments to bilaga 2 only after Lag 2024:1134)"],
              [("g.vehicles.any (fun v => v.firstRegYear == 2022)", "5200 fordonsskatt: a car first registered in 2022 is booked outside the three-year malus of 9 a § (it leaves it during 2025; not split)"),
               ("g.vehicles.any (fun v => v.fuel == .hybrid || v.fuel == .pluginHybrid)", "5200 fordonsskatt: a hybrid is taken as not driven by diesel"),
               ("!g.vehicles.isEmpty", "5200 fordonsskatt: the reduction of 2 kap. 11 § (cars at home in a municipality of bilaga 1) is not applied")],
              ["(p10seVeh[1]!).amount 2025 { kind := \"car\", co2GKm := 120, fuel := .petrol, firstRegYear := 2024 } == 5175",
               "(p10seVeh[1]!).amount 2025 { kind := \"car\", co2GKm := 150, fuel := .petrol, firstRegYear := 2024 } == 9010",
               "(p10seVeh[2]!).amount 2025 { kind := \"car\", co2GKm := 120, fuel := .diesel, firstRegYear := 2024 } == 7047",
               "(p10seVeh[3]!).amount 2025 { kind := \"car\", co2GKm := 150, fuel := .petrol, firstRegYear := 2015 } == 1218",
               "(p10seVeh[5]!).amount 2025 { kind := \"car\", co2GKm := 130, fuel := .diesel, firstRegYear := 2012 } == 2093",
               "(p10seVeh[1]!).amount 2025 { kind := \"car\", co2GKm := 0, fuel := .electric, firstRegYear := 2024 } == 360"],
              "cars of fordonsår before 2006, light buses and lorries, motorcycles (180 kr), heavy vehicles (bilaga 2)")
    elif cc == "IE":
        _vstart(S, "motor tax on M1 cars registered from July 2008 modelled; VRT, older cars and other classes not modelled",
                "Finance Act 1992 s. 132-133 (VRT on OMSP by CO2 and NOx); Sch. Part I para. 3 (e) (engine cc for cars before July 2008)")
        _vfam(S, "Motor tax", _IE_VEH, "p10ieVeh",
              "Finance (Excise Duties) (Vehicles) Act 1952 s. 1, Schedule Part I para. 3 (d), (o)", "Revised Acts, updated to 1 June 2026 (`ie/law/fedva1952_rev.txt`)", "A",
              "Finance (Excise Duties) (Vehicles) Act 1952, Law Reform Commission Revised Acts (`ie/law/fedva1952_rev.txt`)",
              ["para. 3 (o) (M1 registered on or after 1 January 2021, WLTP CO2): 0 g €120; to 50 €140; to 80 €150; to 90 €160; to 100 €170; to 110 €180; to 120 €190; to 130 €200; to 140 €210; to 150 €270; to 160 €280; to 170 €420; to 190 €600; to 200 €790; to 225 €1,250; above €2,400",
               "para. 3 (d) (M1 registered 1 July 2008 - 31 December 2020): 0 g €120; to 80 €170; to 100 €180; to 110 €190; to 120 €200; to 130 €270; to 140 €280; to 155 €400; to 170 €600; to 190 €790; to 225 €1,250; above €2,400",
               "the rates have stood since the Finance Act 2020 (para. 3 (o), annotation F39); the revised text is dated after 2025 and shows no later rate change"],
              [("g.vehicles.any (fun v => v.firstRegYear == 2008)", "5200 motor tax: a car of 2008 is taken as registered from 1 July 2008 (para. 3 (d)); earlier ones pay by engine size (para. 3 (e), not modelled)"),
               ("g.vehicles.any (fun v => v.firstRegYear < 2021 && v.co2GKm ≥ 0)", "5200 motor tax: CO2 of a car registered before 2021 is read as the NEDC value of para. 3 (d)")],
              ["p10ieO.amount 0 == 120", "p10ieO.amount 120 == 190", "p10ieO.amount 121 == 200", "p10ieO.amount 226 == 2400", "p10ieD.amount 140 == 280", "p10ieD.amount 141 == 400",
               "(p10ieVeh.head!).amount 2025 { kind := \"car\", co2GKm := 120, fuel := .petrol, firstRegYear := 2022 } == 190"],
              "cars registered before July 2008 (engine-size rates, para. 3 (e)), goods vehicles, motorcycles and other classes")
    elif cc == "CZ":
        _vstart(S, "daň silniční: cars, vans, motorcycles and buses cited as not taxable; N2/N3 lorries and O3/O4 trailers not modelled",
                "zákon 16/1993 Sb. § 6 (rates for N2, N3 by axles and weight)")
        _vfam(S, "Daň silniční", _CZ_VEH, "p10czVeh",
              "Zákon o dani silniční 16/1993 Sb. § 2 odst. 2", "zákony pro lidi, znění od 1. 1. 2025 (`cz/law/silnicni_zneni-20250101.txt`)", "A",
              "Zákon č. 16/1993 Sb., o dani silniční, znění účinné od 1. 1. 2025 (`cz/law/silnicni_zneni-20250101.txt`)",
              ["§ 2 odst. 2: \"Zdanitelným vozidlem se pro účely daně silniční rozumí silniční vozidlo kategorie N 2 a N 3 a jejich přípojná vozidla kategorie O 3 nebo O 4, pokud jsou registrovaná v registru silničních vozidel v České republice\"",
               "passenger cars (M1), vans (N1), motorcycles (L) and buses (M2, M3) are therefore outside the tax: booked as a cited 0"],
              [], ["(p10czVeh.head!).amount 2025 { kind := \"car\", engineCcm := 1600, fuel := .petrol, firstRegYear := 2020 } == 0",
                   "(p10czVeh.filter (·.selects 2025 { kind := \"truck\", fuel := .diesel, firstRegYear := 2020 })).isEmpty"],
              "lorries N2/N3 and trailers O3/O4 (taxable, rates not modelled), other kinds")
    elif cc == "SK":
        _vstart(S, "daň z motorových vozidiel: business cars and motorcycles modelled, households' vehicles cited as outside; lorries, buses, trailers not modelled",
                "zákon 361/2014 Z. z. prílohy č. 1a-1e (N1-N3, M2-M3, O) with weight and axles")
        ts = "(if g.entity == .company then p10skVeh else p10skHh)"
        _vfam(S, "Daň z motorových vozidiel", _SK_VEH, ts,
              "Zákon 361/2014 Z. z. o dani z motorových vozidiel § 2 ods. 1, § 5, § 6, § 7, príloha č. 1", "Slov-Lex, znenie od 1. 1. 2025 (`sk/law/dmv361_20250101.txt`)", "A",
              "Zákon č. 361/2014 Z. z. o dani z motorových vozidiel, Slov-Lex, znenie účinné od 1. 1. 2025 (`sk/law/dmv361_20250101.txt`)",
              ["§ 2 ods. 1: \"Predmetom dane je vozidlo, ktoré je evidované v Slovenskej republike a používa sa na podnikanie\": a company's vehicles are taxed, a household's vehicles are not (cited 0)",
               "§ 5 ods. 2: base for L and M1 = cylinder capacity in cm3; ods. 1: electric vehicles by kW, príloha č. 1: 0 EUR",
               "príloha č. 1 (from 2025): to 150 cm3 50 EUR; 150-900 62; 900-1200 80; 1200-1500 115; 1500-2000 148; 2000-3000 180; above 3000 218",
               "§ 7 ods. 1: the rate applies for the first 36 months from first registration, then +10 %, +20 %, +30 %, +40 % for each further 36 months, +50 % after 180 months; ods. 2: 50 % less for hybrids, CNG/LNG and hydrogen vehicles"],
              [("g.entity == .company && !g.vehicles.isEmpty", "5200 daň z motorových vozidiel: the 36-month periods of § 7 (1) are read by calendar years since first registration; a company's vehicles are taken as used for business all year")],
              ["p10skCcm.amount 1598 == 148", "p10skCcm.amount 1500 == 115", "p10skCcm.amount 3500 == 218",
               "(p10skVeh[2]!).amount 2025 { kind := \"car\", engineCcm := 1598, fuel := .diesel, firstRegYear := 2019 } == 177",
               "(p10skVeh[1]!).amount 2025 { kind := \"car\", engineCcm := 1798, fuel := .hybrid, firstRegYear := 2024 } == 74",
               "(p10skHh.head!).amount 2025 { kind := \"car\", engineCcm := 1598, fuel := .petrol, firstRegYear := 2019 } == 0"],
              "company vehicles other than L and M1 (N1-N3, M2-M3 by weight and axles, trailers)")


# ---------------------------------------------------------------- 2. conditional withholding (kernel 2.4.0 StateWht)
def _swrap(S, old, new, conds, dated, src, facts, missing_text, guards):
    """Wrap the existing Wht `old` as StateWht `new`: the conditional rules first, then `old`'s rules unchanged
    (StateWht.ofWht books the same charges), and point the families at it. conds = [(kind, rateBp, toCompany, statute,
    tests, minStakeBp)]; every conditional rule says ifUnknown := .general: an absent fact books the general rate and the
    model lists the payment (StateWht.notes) as an unsupported line."""
    import re as _re
    tcl = lambda tc: "none" if tc is None else ("some true" if tc else "some false")
    rl = ",\n     ".join(
        f"{{ rule := {{ kind := .{k}, toCompany := {tcl(tc)}, minStakeBp := {ms}, rateBp := {r}, statute := {_q(st)} }}, "
        f"tests := [{', '.join('.' + t for t in ts)}], ifUnknown := .general }}" for k, r, tc, st, ts, ms in conds)
    S["lean"] = (S.get("lean") or "") + (f"\n/-- {old} with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/\n"
                                         f"def {new} : StateWht :=\n  {{ name := {old}.name, rules := [\n     {rl}] ++ {old}.rules.map StateRule.plain, round := {old}.round }}\n")
    n = 0
    fams = []
    for f in S["families"]:
        e2, k = _re.subn(rf"(?<![\w.]){_re.escape(old)}\.charges g\.company", f"{new}.charges g", f[2])
        n += k
        fams.append((f[0], f[1], e2) + tuple(f[3:]))
    if n != 1:
        raise ValueError(f"{S['cc']}: {old}.charges g.company found {n} times in the families")
    S["families"] = fams
    S["imports"] = sorted(set(S.get("imports", []) + ["TaxKernel.Global2"]))
    S["unsupported"].append((f"!({new}.notes g).isEmpty", "1200 withholding: " + missing_text))
    S["guards"] += list(guards)
    for t in S["taxes"]:
        if str(t.get("oecd")) == "1200" and t.get("grade") in ("A", "B") and "WhtState" not in " ".join(t.get("kernel_parts", [])) \
                and any(x in t.get("kernel_parts", []) for x in ("Wht", "Wht rules")):
            t["kernel_parts"] = list(t.get("kernel_parts", [])) + ["StateWht (2.4.0, recipient state)"]
    S["notes"].append(f"{S['cc']} 1200 withholding by recipient state pass 10 ({old} -> {new}): {dated}")
    S["doc"] += (f"\n\n## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: {old} -> {new})\nSource: {src}.\n"
                 + "".join(f"* {x}\n" for x in facts)
                 + "* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate\n")


def _fixu(S, pairs):
    """Restate earlier unsupported lines that a pass-10 conditional rule now answers: (old, new) replaces the substring,
    (old, None) drops every line (model level and per tax) containing it."""
    def f(t):
        for o, n in pairs:
            if o in t:
                if n is None:
                    return None
                t = t.replace(o, n)
        return t
    S["unsupported"] = [(c, f(t)) for c, t in S["unsupported"] if f(t) is not None]
    for t in S["taxes"]:
        if t.get("unsupported"):
            t["unsupported"] = [f(u) for u in t["unsupported"] if f(u) is not None]


def _pg(new, kind, amt, tc, x, due):
    return f"({new}.chargeOf {{ kind := .{kind}, amount := {amt}, toCompany := {'true' if tc else 'false'}, stakeBp := 6000 }} {{ {x} }} 0).due == {due}"


def _sw10(S):
    cc = S["cc"]
    if S.get("fam") != "Corporate":
        return
    if cc == "ES":
        eu = "TRLIRNR (RDLeg. 5/2004)"
        _swrap(S, "wht", "p10esSw",
               [("interest", 0, None, f"{eu} art. 14.1 c): interest of residents of another EU/EEA state (EEA: with effective exchange of information) is exempt", ["euEea true"], 0),
                ("royalty", 1900, None, f"{eu} art. 25.1 a): 19 por ciento for residents of another EU/EEA state with effective exchange of information", ["euEea true"], 0)],
               "BOE texto consolidado (`es/law/trlirnr.txt`)", "TRLIRNR, BOE texto consolidado (`es/law/trlirnr.txt`)",
               ["art. 25.1 a): \"Con carácter general el 24 por 100. No obstante, el tipo de gravamen será el 19 por ciento cuando se trate de contribuyentes residentes en otro Estado miembro de la Unión Europea o del Espacio Económico Europeo con el que exista un efectivo intercambio de información tributaria\"",
                "art. 14.1 c): interest obtained without a permanent establishment by residents of another EU member state or EEA state (EEA: with effective exchange of information) is exempt",
                "the euEea flag of the payment is read as residence in such a state; art. 14.1 h) (parent-subsidiary) stays out of scope"],
               "a conditional rate of TRLIRNR art. 14.1 c) / 25.1 a) (EU/EEA resident) was not tested because euEea is not given: the general rate is booked",
               [_pg("p10esSw", "royalty", 100000, True, "euEea := some true", 19000), _pg("p10esSw", "royalty", 100000, True, "", 24000),
                _pg("p10esSw", "royalty", 100000, True, "euEea := some false", 24000), _pg("p10esSw", "interest", 100000, False, "euEea := some true", 0),
                _pg("p10esSw", "interest", 100000, False, "", 19000)])
        _swrap(S, "p8wht2", "p10esSw2",
               [("services", 1900, None, "TRLIRNR art. 13.1 b), 25.1 a): 19 por ciento for residents of another EU/EEA state with effective exchange of information", ["euEea true"], 0)],
               "BOE texto consolidado (`es/law/trlirnr.txt`)", "TRLIRNR, BOE texto consolidado (`es/law/trlirnr.txt`)",
               ["services fall under the general rate of art. 25.1 a): 24 %, 19 % for EU/EEA residents"],
               "the 19 % of TRLIRNR art. 25.1 a) on services (EU/EEA resident) was not tested because euEea is not given: 24 % is booked",
               [_pg("p10esSw2", "services", 100000, True, "euEea := some true", 19000), _pg("p10esSw2", "services", 100000, True, "", 24000)])
        _fixu(S, [("services are taken as provided or used in Spain and the recipient outside the EU/EEA (24 %); the art. 24.2 net base and the 19 % EU/EEA rate are not applied", "services are taken as provided or used in Spain; the art. 24.2 net base is not applied")])
    elif cc == "CZ":
        st = "zákon 586/1992 Sb. § 36 odst. 1 písm. c): 35 % for recipients not resident in an EU/EEA state or a state with an implemented double-tax treaty or tax-information agreement"
        _swrap(S, "wht", "p10czSw", [(k, 3500, None, st, ["euEea false", "treaty false"], 0) for k in ("dividend", "interest", "royalty")],
               "zákony pro lidi, znění od 1. 7. 2025 (`cz/law/zdp_zneni-20250701.txt`)", "Zákon o daních z příjmů 586/1992 Sb., znění od 1. 7. 2025 (`cz/law/zdp_zneni-20250701.txt`)",
               ["§ 36 odst. 1 písm. c): \"35 % z příjmů uvedených v písmenech a) a b), a to pro poplatníky, kteří nejsou daňovými rezidenty 1. jiného členského státu Evropské unie nebo dalšího státu tvořícího Evropský hospodářský prostor, nebo 2. třetího státu, se kterým má Česká republika uzavřenu mezinárodní smlouvu upravující zamezení dvojímu zdanění ... nebo ... výměnu informací\"",
                "the rule needs both facts: euEea false and treaty false (the treaty flag is read as a treaty or tax-information agreement in force)"],
               "the 35 % of ZDP § 36 odst. 1 písm. c) (recipient outside the EU/EEA and without a treaty) was not tested because euEea or treaty is not given: 15 % is booked",
               [_pg("p10czSw", "royalty", 100000, True, "euEea := some false, treaty := some false", 35000), _pg("p10czSw", "royalty", 100000, True, "euEea := some false", 15000),
                _pg("p10czSw", "dividend", 100000, True, "euEea := some true, treaty := some false", 15000), _pg("p10czSw", "interest", 100000, True, "", 15000)])
        _swrap(S, "p8wht2", "p10czSw2", [("services", 3500, None, st, ["euEea false", "treaty false"], 0)],
               "zákony pro lidi, znění od 1. 7. 2025 (`cz/law/zdp_zneni-20250701.txt`)", "ZDP (`cz/law/zdp_zneni-20250701.txt`)",
               ["services withheld under § 36 odst. 1 písm. a) bear 35 % under písm. c) for the same recipients"],
               "the 35 % of ZDP § 36 odst. 1 písm. c) on services was not tested because euEea or treaty is not given: 15 % is booked",
               [_pg("p10czSw2", "services", 100000, True, "euEea := some false, treaty := some false", 35000), _pg("p10czSw2", "services", 100000, True, "", 15000)])
        _fixu(S, [("; the 35 % rate for non-treaty, non-EU/EEA residents (§ 36 (1) c)) is not applied", ""), ("35 % for non-treaty, non-EEA residents (§ 36 (1)) not applied", None)])
    elif cc == "SK":
        st = "zákon 595/2003 Z. z. § 43 ods. 1 písm. c): 35 % of income paid to a taxpayer of a non-cooperative state (§ 2 písm. x))"
        _swrap(S, "p8wht", "p10skSw", [("interest", 3500, None, st, ["nonCooperative true"], 0), ("royalty", 3500, None, st, ["nonCooperative true"], 0),
                                       ("dividend", 3500, False, st, ["nonCooperative true"], 0)],
               "Slov-Lex, znenie od 1. 1. 2025 (`sk/law/dp_20250101.txt`)", "Zákon o dani z príjmov 595/2003 Z. z., Slov-Lex (`sk/law/dp_20250101.txt`)",
               ["§ 43 ods. 1 písm. c): \"35 % z príjmov podľa odsekov 2 a 3, ak sú tieto príjmy vyplatené, poukázané alebo pripísané daňovníkovi nespolupracujúceho štátu podľa § 2 písm. x)\"",
                "the nonCooperative flag of the payment is read as a non-cooperative state of § 2 písm. x)"],
               "the 35 % of § 43 ods. 1 písm. c) (non-cooperative state) was not tested because nonCooperative is not given: the general rate is booked",
               [_pg("p10skSw", "interest", 100000, True, "nonCooperative := some true", 35000), _pg("p10skSw", "interest", 100000, True, "", 19000),
                _pg("p10skSw", "dividend", 100000, False, "nonCooperative := some true", 35000), _pg("p10skSw", "dividend", 100000, False, "nonCooperative := some false", 7000)])
        _swrap(S, "p9wht2", "p10skSw2", [("services", 3500, None, st, ["nonCooperative true"], 0),
                                         ("dividend", 3500, True, "zákon 595/2003 Z. z. § 12 ods. 7 písm. c) (a profit share paid to a non-cooperative state is subject), § 43 ods. 1 písm. c): 35 %", ["nonCooperative true"], 0)],
               "Slov-Lex, znenie od 1. 1. 2025 (`sk/law/dp_20250101.txt`)", "ZDP SK (`sk/law/dp_20250101.txt`)",
               ["§ 12 ods. 7 písm. c): a dividend paid to a legal entity is not subject unless paid to a taxpayer of a non-cooperative state, where § 43 ods. 1 písm. c) takes 35 %"],
               "the 35 % on services and dividends to a non-cooperative state (§ 12 ods. 7 písm. c), § 43 ods. 1 písm. c)) was not tested because nonCooperative is not given: the general rate is booked",
               [_pg("p10skSw2", "services", 100000, True, "nonCooperative := some true", 35000), _pg("p10skSw2", "dividend", 100000, True, "nonCooperative := some true", 35000),
                _pg("p10skSw2", "dividend", 100000, True, "", 0)])
        _fixu(S, [("35 % for non-cooperative states and the EU exemption (§ 13 ods. 1 písm. e)) not applied", "the EU exemption (§ 13 ods. 1 písm. e)) not applied"),
                  ("; 35 % to non-cooperative states (§ 43 ods. 1 písm. c)) not applied", ""), ("35 % on dividends to legal entities of non-cooperative states not applied", None)])
    elif cc == "FR":
        _swrap(S, "p8wht", "p10frSw",
               [(k, 7500, None, "CGI art. 182 B III: 75 % where paid to persons whose domicile or establishment is in a state or territory listed as non-cooperative (art. 238-0 A, other than those of its 2 bis 2°), unless the payer shows the payments are not artificial", ["nonCooperative true"], 0) for k in ("royalty", "services")],
               "Légifrance via the Internet Archive (`fr/law/cgi_182B_wb.txt`)", "CGI art. 182 B (`fr/law/cgi_182B_wb.txt`)",
               ["art. 182 B III: \"Le taux de la retenue est porté à 75 % lorsque les sommes et produits, autres que les salaires, mentionnés au I sont payés à des personnes domiciliées ou établies dans un Etat ou territoire non coopératif au sens de l'article 238-0 A\" (except those of its 2 bis 2°), save where the payer proves the operations are real",
                "the nonCooperative flag is read as a state or territory on the art. 238-0 A list (other than 2 bis 2°); the safe-harbour proof is not in the input"],
               "the 75 % of CGI art. 182 B III (non-cooperative state or territory) was not tested because nonCooperative is not given: 25 % is booked",
               [_pg("p10frSw", "royalty", 100000, True, "nonCooperative := some true", 75000), _pg("p10frSw", "royalty", 100000, True, "", 25000)])
        _swrap(S, "p8wht2", "p10frSw2",
               [("interest", 7500, None, "CGI art. 125 A III: 75 % on interest paid outside France in a non-cooperative state or territory (art. 238-0 A)", ["nonCooperative true"], 0)],
               "Légifrance via the Internet Archive (`fr/law/cgi_125A_wb.txt`)", "CGI art. 125 A (`fr/law/cgi_125A_wb.txt`)",
               ["art. 125 A III: the prélèvement applies at 75 % to interest paid outside France in a non-cooperative state or territory; other interest paid to non-residents bears none",
                "dividends to non-cooperative states (CGI art. 119 bis 2, 75 %) are not modelled: the article's 2025 text is not on disk"],
               "the 75 % of CGI art. 125 A III on interest (non-cooperative state or territory) was not tested because nonCooperative is not given: none is booked",
               [_pg("p10frSw2", "interest", 100000, True, "nonCooperative := some true", 75000), _pg("p10frSw2", "interest", 100000, True, "", 0)])
    elif cc == "NL":
        st = "Wet bronbelasting 2021 art. 1.2 lid 1 (gelieerd, laagbelastende jurisdictie), 2.1 lid 1 a, 3.1, 4.1: 25,8 % (highest Vpb rate, art. 22 Wet Vpb 1969) on {k} to a related body established in a low-tax jurisdiction"
        _swrap(S, "p8wht", "p10nlSw", [(k, 2580, True, st.format(k=k + "s" if k == "royalty" else k), ["lowTax true"], 5000) for k in ("interest", "royalty")],
               "wetten.overheid.nl, geldend op 1 juli 2025 (`nl/law/wbb2021_g2025.txt`)", "Wet bronbelasting 2021 (BWBR0042952), wetten.overheid.nl, geldig op 01-07-2025 (`nl/law/wbb2021_g2025.txt`)",
               ["art. 2.1 lid 1 a: liable is a body entitled to interest or royalties (art. 3.1) that is established in a low-tax jurisdiction; art. 1.2: a related body is one in which the payer has a kwalificerend belang (or which has one in the payer); a low-tax jurisdiction taxes profits at less than 9 % or appears on the Union list of jurisdictions that do not cooperate",
                "art. 4.1: \"De belasting bedraagt het hoogste percentage, bedoeld in artikel 22 van de Wet op de vennootschapsbelasting 1969\": 25,8 % in 2025",
                "the kwalificerend belang is read as a stake of at least 50 % (minStakeBp 5000); the lowTax flag as a jurisdiction on the ministerial list; dividends (art. 3.1 c, with dividendbelasting set off) are not modelled"],
               "the 25,8 % of the Wet bronbelasting 2021 (related body in a low-tax jurisdiction) was not tested because lowTax is not given: none is booked",
               [_pg("p10nlSw", "interest", 100000, True, "lowTax := some true", 25800), _pg("p10nlSw", "interest", 100000, True, "", 0),
                _pg("p10nlSw", "royalty", 100000, True, "lowTax := some false", 0),
                "(p10nlSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 1000 } { lowTax := some true } 0).due == 0"])
        _fixu(S, [("the 25,8 % conditional withholding (related recipient in a low-tax or listed state) not applied: the input has no recipient state", None),
                  ("Wet bronbelasting 2021 (interest/royalties to low-tax jurisdictions) not modelled", None)])
    elif cc == "NO":
        _swrap(S, "p8wht", "p10noSw",
               [("interest", 1500, True, "skatteloven § 10-80, § 10-82, § 10-63; Stortingets skattevedtak 2025 § 3-5: 15 pst. on interest to a related (at least 50 %) company in a low-tax country", ["lowTax true"], 5000),
                ("royalty", 1500, True, "skatteloven § 10-81, § 10-82, § 10-63; Stortingets skattevedtak 2025 § 3-5: 15 pst. on royalties to a related (at least 50 %) company in a low-tax country", ["lowTax true"], 5000)],
               "Lovdata (`no/law/sktl_10-80.txt`, `sktl_10-82.txt`, `sktl_10-63.txt`); Stortingsvedtak 2024-12-13-3203 (`no/law/stv_skatt2025.txt`)",
               "Skatteloven §§ 10-63, 10-80 to 10-82, Lovdata (`no/law/sktl_10-*.txt`); Stortingets vedtak om skatt av inntekt og formue mv. for inntektsåret 2025 § 3-5 (`no/law/stv_skatt2025.txt`)",
               ["§ 10-80 (1): a company or entity resident in a low-tax country (§ 10-63) pays tax on interest received from a related company; § 10-81 likewise on royalties; § 10-82: related = at least 50 % owned or controlled, directly or indirectly, either way",
                "§ 10-63: a low-tax country taxes the company's total profit at less than two thirds of the Norwegian tax; § 10-80 (2) a: no tax where the recipient is genuinely established with real economic activity in an EEA state (not in the input: noted)",
                "Stortingets skattevedtak 2025 § 3-5: \"Av inntekt etter bestemmelsene i skatteloven § 10-80 og § 10-81 ... svare skatt til staten med 15 pst.\""],
               "the 15 % of skatteloven § 10-80 / 10-81 (related company in a low-tax country) was not tested because lowTax is not given: none is booked",
               [_pg("p10noSw", "interest", 100000, True, "lowTax := some true", 15000), _pg("p10noSw", "interest", 100000, True, "", 0),
                _pg("p10noSw", "royalty", 100000, False, "lowTax := some true", 0)])
        _fixu(S, [("15 pst. on interest and royalties to related companies in low-tax states (skatteloven § 10-82) not applied: the input has no recipient state", None)])
    elif cc == "RO":
        st = "Codul fiscal art. 224 alin. (4) lit. c^1): 10 % on income of art. 223 alin. (1) lit. b)-i), k)-p) of individuals resident in an EU member state or a state with a double-tax convention with Romania"
        _swrap(S, "p9wht", "p10roSw",
               [(k, 1000, False, st, [t], 0) for k in ("interest", "royalty", "services") for t in ("euEea true", "treaty true")],
               "Internet Archive 2025-05-02 (`ro/law/cf_wb20250502.txt`)", "Codul fiscal (Legea 227/2015), text via the Internet Archive 2025-05-02 (`ro/law/cf_wb20250502.txt`)",
               ["art. 224 alin. (4) lit. c^1): \"10% în cazul veniturilor impozabile enumerate la art. 223 alin. (1) lit. b)-i) și k)-p) obținute din România de persoane fizice rezidente într-un stat membru al Uniunii Europene sau într-un stat cu care România are încheiată o convenție de evitare a dublei impuneri\"",
                "either fact suffices (two rules: euEea true, treaty true); the euEea flag also covers the EEA states outside the EU, all of which are read as treaty states",
                "lit. c): 50 % on payments to a state without an information-exchange instrument applies only to transactions qualified as artificial (art. 11 alin. (3)): not in the input, not modelled"],
               "the 10 % of Codul fiscal art. 224 alin. (4) lit. c^1) (individual resident in the EU or a treaty state) was not tested because euEea and treaty are not given: 16 % is booked",
               [_pg("p10roSw", "interest", 100000, False, "euEea := some true", 10000), _pg("p10roSw", "interest", 100000, False, "euEea := some false, treaty := some true", 10000),
                _pg("p10roSw", "interest", 100000, False, "", 16000), _pg("p10roSw", "services", 100000, True, "euEea := some true", 16000)])


# ---------------------------------------------------------------- 3. remaining withholding gaps
def _w10(S, key, *a, **k):
    _wx(S, "p10", "pass 10", key, *a, **k)


def _wht10(S):
    cc = S["cc"]
    if S.get("fam") != "Corporate":
        return
    if cc == "SM":
        _w10(S, "whtr", "Ritenuta sui redditi di lavoro autonomo (royalty)",
             [("royalty", 2000, None, "Legge 166/2013 art. 27 c. 6 b), art. 102 c. 1: income from the economic use of trade marks, works, copyrights and inventions is lavoro autonomo income; ritenuta a titolo d'imposta del 20 per cento on payments to persons resident abroad")],
             "Legge 16 dicembre 2013 n. 166 art. 7 c. 2 b), art. 27 c. 6 b), art. 102 c. 1", "testo coordinato (`sm/law/igr_166_2013_coord_senzanote.txt`)", "A",
             "Legge 166/2013 (imposta generale sui redditi), testo coordinato (`sm/law/igr_166_2013_coord_senzanote.txt`)",
             ["art. 27 c. 6 b): income from the economic use of trade marks, works of the mind, copyrights, industrial inventions and the like is income from lavoro autonomo",
              "art. 102 c. 1: whoever pays compensation for lavoro autonomo or assimilated services as defined in art. 27 to persons resident abroad, also where performed as a business, withholds a final tax of 20 per cent",
              "art. 7 c. 2 b): such compensation paid by San Marino residents is produced in San Marino whatever the place of use"],
             uns=[(_pay8("royalty"), "royalties are taken as paid by a San Marino operator (art. 7 c. 2 b)); the 3 % rate of art. 102 c. 2 (artistic, cultural, sporting services) does not concern royalties")],
             remaining=[])
    elif cc == "BY":
        _w10(S, "whti", "Подоходный налог с физических лиц (налоговый агент: услуги нерезидентам)",
             [("services", 1300, False, "НК ст. 197 п. 1 пп. 1.6, ст. 214 п. 1, ст. 216 п. 1: remuneration for services received from a Belarusian organisation is Belarusian-source income; the organisation withholds 13 %")],
             "Налоговый кодекс, Особенная часть, гл. 17: ст. 197 п. 1 пп. 1.6, ст. 214 п. 1, ст. 216 п. 1", "pravo.by via Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`)", "A",
             "Налоговый кодекс Республики Беларусь, Особенная часть, pravo.by via Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`)",
             ["ст. 197 п. 1 пп. 1.6: remuneration for work performed or services rendered received from Belarusian organisations is income from Belarusian sources",
              "ст. 214 п. 1: \"Ставка подоходного налога с физических лиц устанавливается в размере тринадцать (13) процентов\", unless the article provides otherwise",
              "ст. 216 п. 1: Belarusian organisations are tax agents that compute and pay the tax on income they pay"],
             uns=[(_ind9("services"), "a non-resident individual is taken as acting outside an individual-entrepreneur registration in Belarus (13 %, not the 20 % of ст. 214 п. 3)")],
             remaining=[])
    elif cc == "NL":
        _w10(S, "whti", "Geen bronheffing op dienstvergoedingen (natuurlijke personen)",
             [("services", 0, False, "Wet IB 2001 art. 7.1, 7.2: a non-resident individual is assessed on Dutch income (profit of a Dutch enterprise, wages for work in the Netherlands, results from other work in the Netherlands); no tax is withheld on a fee for services")],
             "Wet inkomstenbelasting 2001 art. 7.1, 7.2", "wetten.overheid.nl, geldig op 1 juli 2025 (`nl/law/ib2001_g2025.txt`)", "A",
             "Wet inkomstenbelasting 2001 (BWBR0011353), wetten.overheid.nl, geldig op 01-07-2025 (`nl/law/ib2001_g2025.txt`)",
             ["art. 7.1: the income tax of a buitenlandse belastingplichtige is levied on taxable income from work and home in the Netherlands, from a substantial interest in a Dutch company and from savings and investments in the Netherlands",
              "art. 7.2 lid 2: income from work and home in the Netherlands is the profit of a Dutch enterprise (permanent establishment or representative), wages for work done in the Netherlands, results from other work in the Netherlands and the listed benefits: all assessed, none withheld by the payer of a fee",
              "art. 7.2 lid 3: a performing artist or athlete of a non-treaty state on a short engagement is deemed to have a permanent establishment (loonbelasting artiestenregeling): not modelled"],
             uns=[(_ind9("services"), "the recipient is taken as performing the services outside the Netherlands or without a Dutch enterprise; artists and athletes of non-treaty states (art. 7.2 lid 3; loonbelasting) are not separated")],
             remaining=[])


# ---------------------------------------------------------------- 6. P5/P6
def _p56_10(S):
    cc = S["cc"]
    if cc == "IE" and S.get("fam") == "Property" and any(str(t.get("oecd")) == "4400" and t.get("grade") == "C" for t in S["taxes"]):
        src = ("Revenue, Notes for Guidance, Stamp Duties Consolidation Act 1999 (2025 edition), Schedules & Appendices, head of charge "
               "\"CONVEYANCE or TRANSFER on sale\" (`ie/law/sdca_nfg2025_schedules.txt`; the revised Act is not on revisedacts.lawreform.ie)")
        dated = "Notes for Guidance 2025 (rates for instruments executed from 2 October 2024, Finance Act 2024 s. 90)"
        p6_transfer(S, "ieSdRes", "Stamp duty on conveyances (residential property)", [(0, 100), (1000000, 200), (1500000, 600)],
                    "SDCA 1999 Sch. 1, CONVEYANCE or TRANSFER on sale: residential property 1 % to EUR 1 000 000, 2 % to EUR 1 500 000, 6 % above",
                    dated, "B", src,
                    ["residential property: 1 % where the consideration does not exceed EUR 1 million, 2 % on the excess up to EUR 1,5 million, 6 % on the excess above EUR 1,5 million",
                     "3 or more units in an apartment block: 1 % to EUR 1 million, 2 % on the balance; relevant residential units of s. 31E (10 or more houses in 12 months): 15 %",
                     "non-residential property: 7,5 %",
                     "grade B: Revenue's official guide; the Act's Schedule 1 text itself is not on disk"],
                    kinds=("home", "realEstate"))
        p6_transfer(S, "ieSdNonRes", "Stamp duty on conveyances (non-residential property)", [(0, 750)],
                    "SDCA 1999 Sch. 1, CONVEYANCE or TRANSFER on sale: non-residential property 7,5 %", dated, "B", src,
                    ["land is taken as non-residential property (7,5 %)"], kinds=("land",),
                    uns=[("g.purchases.any (fun p => p.kind == .realEstate)", "stamp duty: other real estate is taken as residential property (1 / 2 / 6 %); commercial property bears 7,5 %"),
                         ("g.purchases.any (fun p => p.kind == .land)", "stamp duty: land is taken as non-residential (7,5 %); residential land follows the residential rates"),
                         ("g.purchases.any (fun p => p.kind == .home || p.kind == .realEstate)", "stamp duty: the apartment-block rates, the s. 31E 15 % rate, consanguinity relief and the aggregation of linked transactions are not applied")])


# ---------------------------------------------------------------- 7. kernel 2.5.0: gains stacked on the 1.x PIT
def _stackfam(S, key, rules_lean, names, entries, src, facts, uns):
    """Replace the grade-C 1100 gains entry by StackRules priced on the 1.x line (`base.pit` / `base.route` of Pit.lean)."""
    S.setdefault("families", []); S.setdefault("notes", []); S.setdefault("guards", []); S.setdefault("unsupported", [])
    S["families"] = list(S["families"] or [])
    S["imports"] = sorted(set(S.get("imports", []) + ["TaxKernel.Global2"]))
    S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == "1100" and t.get("grade") == "C" and "Gains of individuals" in t.get("tax", ""))]
    S["unsupported"] = [u for u in S["unsupported"] if not ("1100" in u[1][:6] and "ains" in u[1] and "grade C" in u[1])]
    S["lean"] = (S.get("lean") or "") + rules_lean + f"\ndef {key} : List StackRule := [{', '.join(names)}]\n"
    S["families"].append((f"1100 gains stacked on the 1.x income tax (pass 10)", [".pit"], f"stackCharges base.pit base.route {key} args g"))
    S["unsupported"].append((f"!(stackUnknown base.pit base.route {key} args g).isEmpty", "1100 gains: a stacked rule could not be priced on the 1.x line (grade C)"))
    S["unsupported"] += list(uns)
    S["guards"] += [f"{key}.length == {len(names)}"]
    for e in entries:
        S["taxes"].append(dict(e, kernel_parts=["StackRule (2.5.0)", "GainRule"]))
    S["notes"].append(f"{S['cc']} 1100 gains stacked on the 1.x PIT, pass 10 (kernel 2.5.0)")
    S["doc"] += f"\n\n## 1100 gains of individuals stacked on the 1.x income tax (pass 10, kernel 2.5.0 StackRule)\nSource: {src}.\n" + "".join(f"* {x}\n" for x in facts)


def _stack10(S):
    cc = S["cc"]
    if S.get("fam") != "Capital" or not any(str(t.get("oecd")) == "1100" and t.get("grade") == "C" and "Gains of individuals" in t.get("tax", "") for t in S["taxes"]):
        return
    if cc == "CZ":
        lean = """
/-- ZDP § 10 odst. 1 písm. b) bod 2, odst. 4; § 4 odst. 1 písm. u): securities, exempt when held more than 3 years -/
def p10czSec : StackRule :=
  { name := "Daň z příjmů fyzických osob: prodej cenných papírů (§ 10)",
    statute := "zákon 586/1992 Sb. § 10 odst. 1 písm. b), odst. 4; § 4 odst. 1 písm. u) (exempt after 3 years); rates § 16 (1.x model)",
    gainKinds := [.listedShares, .bonds], gainRule := { exemptAfterMonths := 37 }, into := .wages }
/-- ZDP § 10 odst. 1 písm. b) bod 1; § 4 odst. 1 písm. a) (2 years' residence), písm. b) (10 years) -/
def p10czRe : StackRule :=
  { name := "Daň z příjmů fyzických osob: prodej nemovitých věcí (§ 10)",
    statute := "zákon 586/1992 Sb. § 10 odst. 1 písm. b), odst. 4; § 4 odst. 1 písm. a) (main home, 2 years' residence), písm. b) (exempt after 10 years); rates § 16 (1.x model)",
    gainKinds := [.home, .realEstate, .land], gainRule := { exemptAfterMonths := 121, mainHomeExempt := true }, into := .wages }
"""
        _stackfam(S, "p10czStack", lean, ["p10czSec", "p10czRe"],
                  [{"oecd": "1100", "tax": "Příjmy z prodeje cenných papírů (§ 10), stacked", "statute": "ZDP § 10 odst. 1 písm. b), odst. 4; § 4 odst. 1 písm. u)", "dated": "znění od 1. 7. 2025", "grade": "A",
                    "unsupported": ["the CZK 100 000 annual proceeds exemption and the CZK 40 million cap on time-tested exemptions are not applied", "shares in an s.r.o. (not securities: 5 years, § 4 odst. 1 písm. r)) are not separated from unlisted shares"]},
                   {"oecd": "1100", "tax": "Příjmy z prodeje nemovitých věcí (§ 10), stacked", "statute": "ZDP § 10 odst. 1 písm. b), odst. 4; § 4 odst. 1 písm. a), b)", "dated": "znění od 1. 7. 2025", "grade": "A",
                    "unsupported": ["real estate acquired before 2021 is exempt after 5 years (transitional rule): the 10-year test is applied", "the 2 years' residence of a main home is taken as met"]}],
                  "Zákon o daních z příjmů 586/1992 Sb., znění od 1. 7. 2025 (`cz/law/zdp_zneni-20250701.txt`); kernel 2.5.0 StackRule",
                  ["§ 4 odst. 1 písm. a): the sale of a family house or flat in which the seller lived for at least 2 years immediately before the sale is exempt",
                   "§ 4 odst. 1 písm. b): other real estate is exempt where more than 10 years pass between acquisition and sale; písm. u): securities where more than 3 years pass",
                   "§ 10 odst. 1 písm. b), odst. 4: other gains are 'ostatní příjmy', proceeds less the acquisition price, in the general base taxed at 15 % / 23 % (§ 16)",
                   "the net gain enters the 1.x line as the seller's wage (`into := .wages`): the 1.x model taxes wages in full at the § 16 scale on the total base (employee contributions are not in its income tax); unlisted shares are left out (s.r.o. shares: 5-year test not separable)"],
                  [("g.disposals.any (fun d => d.kind == .unlistedShares)", "1100 gains: unlisted shares (an s.r.o. share is not a security: 5-year test of § 4 odst. 1 písm. r)) are not modelled (grade C)")])
    elif cc == "SK":
        lean = """
/-- ZDP § 8 ods. 1 písm. e); § 9 ods. 1 písm. k): listed securities, exempt after one year -/
def p10skSec : StackRule :=
  { name := "Daň z príjmov fyzickej osoby: predaj cenných papierov prijatých na regulovaný trh (§ 8)",
    statute := "zákon 595/2003 Z. z. § 8 ods. 1 písm. e), ods. 5; § 9 ods. 1 písm. k) (exempt after one year), písm. i) (500 EUR, 1.x model); rates § 15 (1.x model)",
    gainKinds := [.listedShares, .bonds], gainRule := { exemptAfterMonths := 13 }, into := .capitalGains }
/-- § 8 ods. 1 písm. e): other securities and shares, no holding-period exemption -/
def p10skOther : StackRule :=
  { name := "Daň z príjmov fyzickej osoby: predaj iných cenných papierov a podielov (§ 8)",
    statute := "zákon 595/2003 Z. z. § 8 ods. 1 písm. e), ods. 5; § 9 ods. 1 písm. i) (500 EUR, 1.x model)",
    gainKinds := [.unlistedShares], into := .capitalGains }
/-- § 8 ods. 1 písm. b); § 9 ods. 1 písm. a): real estate, exempt five years after acquisition -/
def p10skRe : StackRule :=
  { name := "Daň z príjmov fyzickej osoby: predaj nehnuteľnosti (§ 8)",
    statute := "zákon 595/2003 Z. z. § 8 ods. 1 písm. b), ods. 5; § 9 ods. 1 písm. a) (exempt after five years)",
    gainKinds := [.home, .realEstate, .land], gainRule := { exemptAfterMonths := 61 }, into := .capitalGains }
"""
        _stackfam(S, "p10skStack", lean, ["p10skSec", "p10skOther", "p10skRe"],
                  [{"oecd": "1100", "tax": "Príjmy z predaja cenných papierov a podielov (§ 8), stacked", "statute": "ZDP § 8 ods. 1 písm. e); § 9 ods. 1 písm. i), k)", "dated": "znenie od 1. 1. 2025", "grade": "A",
                    "unsupported": ["the 500 EUR exemption of § 9 ods. 1 písm. i) is the 1.x model's (shared with other § 8 income as it applies it)"]},
                   {"oecd": "1100", "tax": "Príjmy z predaja nehnuteľnosti (§ 8), stacked", "statute": "ZDP § 8 ods. 1 písm. b); § 9 ods. 1 písm. a)", "dated": "znenie od 1. 1. 2025", "grade": "A",
                    "unsupported": ["inherited real estate (§ 9 ods. 1 písm. b): the testator's holding counts) is not separated"]}],
                  "Zákon o dani z príjmov 595/2003 Z. z., Slov-Lex znenie od 1. 1. 2025 (`sk/law/dp_20250101.txt`); kernel 2.5.0 StackRule",
                  ["§ 9 ods. 1 písm. a): the sale of real estate is exempt after five years from acquisition; písm. k): securities admitted to a regulated market after one year from acquisition (and admission)",
                   "§ 9 ods. 1 písm. c): movable things are exempt (securities are not movable things for this purpose); písm. i): § 8 ods. 1 písm. d)-f) income up to 500 EUR in total is exempt",
                   "the net gain enters the 1.x line's `capitalGains` (§ 8 ods. 1 písm. e) income, which the 1.x model taxes at the § 15 rates after the 500 EUR exemption); there is no main-home exemption beyond the five years"],
                  [("g.disposals.any (fun d => d.kind == .other)", "1100 gains: movable things are exempt (§ 9 ods. 1 písm. c)); not booked")])
    elif cc == "LU":
        lean = """
/-- L.I.R. art. 99bis (1) 1. b), (3): speculative gains on movables held at most six months; Freigrenze 500 EUR -/
def p10luMov : StackRule :=
  { name := "Impôt sur le revenu: bénéfices de spéculation, biens meubles (art. 99bis)",
    statute := "L.I.R. art. 99bis (1) 1. b) (six months), art. 99bis Freigrenze (inférieur à 500 euros); barème art. 118 (1.x model)",
    gainKinds := [.listedShares, .unlistedShares, .bonds, .other], gainRule := { exemptAfterMonths := 7 },
    exclusion := { amount := 500, threshold := true }, into := .rentalIncome }
/-- art. 99bis (1) 1. a) with the 2025 derogation: real estate realised within two years -/
def p10luRe : StackRule :=
  { name := "Impôt sur le revenu: bénéfices de spéculation, immeubles (art. 99bis)",
    statute := "L.I.R. art. 99bis (1) 1. a) and the derogation for immeubles réalisés du 1er janvier au 30 juin 2025 (two years); barème art. 118 (1.x model)",
    gainKinds := [.home, .realEstate, .land], gainRule := { exemptAfterMonths := 25 }, into := .rentalIncome }
"""
        _stackfam(S, "p10luStack", lean, ["p10luMov", "p10luRe"],
                  [{"oecd": "1100", "tax": "Bénéfices de spéculation (art. 99bis), stacked", "statute": "L.I.R. art. 99bis", "dated": "texte coordonné (amendments to L. 27.06.25)", "grade": "A",
                    "unsupported": ["the 500 EUR Freigrenze is applied to each rule (movables, real estate) rather than to their total", "real estate sold from 1 July 2025 (five years, or two with a compromis registered by 30 June 2025) is read under the first-half rule (two years)"]},
                   {"oecd": "1100", "tax": "Plus-values de cession (art. 99ter, art. 100: demi-taux global)", "statute": "L.I.R. art. 99ter, 100, 131", "dated": "", "grade": "C", "status": "unsupported",
                    "tried": "pass 10: art. 99ter and 100 are taxed at half the global rate, which stacking at the full scale cannot express",
                    "unsupported": ["would unlock: a half-rate stacking rule (kernel request) or a hand form on the 1.x scale"]}],
                  "Loi modifiée du 4 décembre 1967 concernant l'impôt sur le revenu, texte coordonné (`lu/law/LIR_2025-01-01.txt`); kernel 2.5.0 StackRule",
                  ["art. 99bis (1) 1.: gains on property acquired for consideration are speculative when the interval between acquisition and realisation does not exceed five years for real estate and six months for other property; real estate realised between 1 January and 30 June 2025: two years (from 1 July to 30 September 2025: two years if the compromis was registered by 30 June 2025)",
                   "art. 99bis: speculative gains are exempt where their total for the calendar year is below 500 euros (Freigrenze)",
                   "speculative gains are revenus divers taxed at the progressive scale: the net gain enters the 1.x line's `rentalIncome`, which the 1.x model adds in full to the taxable income",
                   "long-held non-substantial shares are exempt; art. 99ter (real estate after the speculative period) and art. 100 (substantial participations) are taxed at half the global rate: grade C"],
                  [("g.disposals.any (fun d => (d.kind == .home || d.kind == .realEstate || d.kind == .land) && !d.mainHome && 25 ≤ d.heldMonths)", "1100 gains: real estate held beyond the speculative period (art. 99ter, half the global rate) is not modelled (grade C)"),
                   ("g.disposals.any (fun d => (d.kind == .unlistedShares || d.kind == .listedShares) && 7 ≤ d.heldMonths && 1000 < d.stakeBp)", "1100 gains: a substantial participation (more than 10 %, art. 100, half the global rate) is not modelled (grade C)")])


# ---------------------------------------------------------------- driver
def p10_rows(S):
    for f in (_veh10, _veh10b, _sw10, _wht10, _p56_10, _stack10):
        f(S)
