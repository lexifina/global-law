# pass 11 rows (R1 Europe, 2026-11-21): vehicle taxes (kernel 2.4.0/2.5.0 VehicleTax), carry-overs, P5/P6, withholding.
# exec'd by the spec after p6lib.py, p8_rows.py, p9_rows.py and p10_rows.py (helpers _q, _wx, _first8, _pay8, _ind9, _co9,
# _swrap, _fixu). Every function is keyed by country and family (lesson of pass 10: the block re-runs at every build).
# Statute rows quote or cite the act read (grade A); official guides are grade B.


# ---------------------------------------------------------------- 1. vehicle taxes (5200)
def _veh_c(S):
    """True for the Other family of a country whose 5200 entry is still the grade-C stub."""
    return S.get("fam") == "Other" and any(str(t.get("oecd")) == "5200" and t.get("grade") == "C" and "rest" not in t.get("tax", "")
                                          for t in S["taxes"])


def _vstart11(S, rest_tax, rest_unlock):
    """First vehicle family of a country in pass 11: as p10 `_vstart`, plus the guard helper `p11amt` (the amount of the
    first tax that computes the vehicle in 2025; -1 when none does)."""
    S.setdefault("families", []); S.setdefault("notes", []); S.setdefault("guards", []); S.setdefault("unsupported", [])
    S["families"] = list(S["families"] or [])
    S["imports"] = sorted(set(S.get("imports", []) + ["TaxKernel.Global2"]))
    S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == "5200" and t.get("grade") == "C")]
    S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("5200")]
    S["taxes"].append({"oecd": "5200", "tax": "Other taxes on use of goods (rest)", "statute": "", "dated": "", "grade": "C",
                       "status": "unsupported", "kernel_parts": [], "tried": "pass 11: " + rest_tax,
                       "unsupported": ["would unlock: " + rest_unlock]})
    S["lean"] = (S.get("lean") or "") + """
/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1
"""


def _vfam11(S, name, lean, ts, statute, dated, grade, src, facts, uns, guards, rest_veh, registration=False):
    """One VehicleTax family (first rule that computes, per vehicle), as p10 `_vfam` with the pass-11 label."""
    S["lean"] = (S.get("lean") or "") + lean
    S["families"].append((f"5200 {name} (pass 11)", [".useOfGoods"], f"vehicleTaxCharges {ts} g (firstOnly := true)"))
    um = (f"g.vehicles.any (fun v => v.newReg && !({ts}.any (·.selects g.year v)))" if registration
          else f"!(vehicleTaxUnmatched {_q(name)} {ts} g).isEmpty")
    S["unsupported"] += [(f"!(vehicleTaxUnknown {_q(name)} {ts} g).isEmpty", f"5200 {name}: a vehicle lacks an attribute the rate needs (grade C)"),
                         (um, f"5200 {name}: a vehicle no rule reaches: {rest_veh} (grade C)")] + list(uns)
    S["guards"] += list(guards)
    S["notes"].append(f"{S['cc']} 5200 {name} pass 11: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "5200", "tax": name, "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["VehicleTax (2.4.0)", "QtyTable"], "unsupported": [rest_veh] + [t for _, t in uns]})
    S["doc"] += f"\n\n## 5200 {name} (pass 11, kernel 2.4.0, grade {grade})\nSource: {src}.\n" + "".join(f"* {x}\n" for x in facts)


def _vg(ts, fields, want):
    """A guard: p11amt ts { fields } == want."""
    return f"p11amt {ts} {{ {fields} }} == {want}"


# RO: Codul fiscal (Legea 227/2015) art. 469 (1) n), art. 470 (2), (3)
_RO_VEH = """
/-- Codul fiscal art. 470 alin. (2): lei for each group of 200 cmc or fraction of it, at the rate of the vehicle's row -/
def p11roCcm (r : Int) : QtyTable := QtyTable.perUnit r 200 (step := 200)
def p11roRow (k : String) (fs : List VehicleFuel) (lo hi r bp : Int) (st : String) : VehicleTax :=
  { name := "Impozitul pe mijloacele de transport", kinds := [k], fuels := fs, «when» := [(.engineCcm, lo, hi)],
    parts := [(.engineCcm, p11roCcm r)], multiplierBp := bp, level := .local, statute := st }
def p11roIce : List VehicleFuel := [.petrol, .diesel, .lpg, .cng, .other]
def p11roHyb : List VehicleFuel := [.hybrid, .pluginHybrid]
def p11roCars (fs : List VehicleFuel) (bp : Int) (sfx : String) : List VehicleTax :=
  [p11roRow "car" fs (-1) 1600 8 bp s!"Codul fiscal art. 470 alin. (2) pct. I.1: autoturisme până la 1.600 cmc, 8 lei/200 cmc{sfx}",
   p11roRow "car" fs 1600 2000 18 bp s!"Codul fiscal art. 470 alin. (2) pct. I.3: autoturisme 1.601-2.000 cmc, 18 lei/200 cmc{sfx}",
   p11roRow "car" fs 2000 2600 72 bp s!"Codul fiscal art. 470 alin. (2) pct. I.4: autoturisme 2.001-2.600 cmc, 72 lei/200 cmc{sfx}",
   p11roRow "car" fs 2600 3000 144 bp s!"Codul fiscal art. 470 alin. (2) pct. I.5: autoturisme 2.601-3.000 cmc, 144 lei/200 cmc{sfx}",
   p11roRow "car" fs 3000 VehicleTax.noBound 290 bp s!"Codul fiscal art. 470 alin. (2) pct. I.6: autoturisme peste 3.000 cmc, 290 lei/200 cmc{sfx}"]
def p11roVeh : List VehicleTax :=
  [{ name := "Impozitul pe mijloacele de transport", kinds := ["car", "motorcycle"], fuels := [.electric, .hydrogen], level := .local,
     statute := "Codul fiscal art. 469 alin. (1) lit. n): autovehiculele acționate electric are not taxed" }]
  ++ p11roCars p11roIce 10000 ""
  ++ p11roCars p11roHyb 5000 "; art. 470 alin. (3): hibride, reduced by 50 % (the statutory minimum reduction)"
  ++ [p11roRow "motorcycle" (p11roIce ++ p11roHyb) (-1) 1600 8 10000 "Codul fiscal art. 470 alin. (2) pct. I.1: motociclete până la 1.600 cmc, 8 lei/200 cmc",
      p11roRow "motorcycle" (p11roIce ++ p11roHyb) 1600 VehicleTax.noBound 9 10000 "Codul fiscal art. 470 alin. (2) pct. I.2: motociclete peste 1.600 cmc, 9 lei/200 cmc"]
"""


def _veh11(S):
    cc = S["cc"]
    if not _veh_c(S):
        return
    if cc == "RO":
        _vstart11(S, "impozitul pe mijloacele de transport on cars and motorcycles modelled at the statutory amounts; local indexation and additional quotas, buses, lorries (art. 470 (5)-(7)) and trailers not modelled",
                  "the 2025 decision of the Bucharest general council (art. 491 indexation, art. 489 additional quotas, art. 470 (3) hybrid reduction); art. 470 (5)-(7) for heavy vehicles")
        car = 'kind := "car", fuel := .{f}, engineCcm := {c}, firstRegYear := 2019'
        g = [_vg("p11roVeh", car.format(f="petrol", c=1598), 64), _vg("p11roVeh", car.format(f="diesel", c=1968), 180),
             _vg("p11roVeh", car.format(f="petrol", c=1600), 64), _vg("p11roVeh", car.format(f="petrol", c=1601), 162),
             _vg("p11roVeh", car.format(f="petrol", c=2001), 792), _vg("p11roVeh", car.format(f="diesel", c=3000), 2160),
             _vg("p11roVeh", car.format(f="petrol", c=3001), 4640), _vg("p11roVeh", car.format(f="hybrid", c=1798), 81),
             _vg("p11roVeh", 'kind := "car", fuel := .electric, firstRegYear := 2023', 0),
             _vg("p11roVeh", 'kind := "motorcycle", fuel := .petrol, engineCcm := 1800, firstRegYear := 2020', 81),
             _vg("p11roVeh", 'kind := "truck", fuel := .diesel, engineCcm := 7000, firstRegYear := 2020', -1)]
        _vfam11(S, "Impozitul pe mijloacele de transport", _RO_VEH, "p11roVeh",
                "Codul fiscal (Legea 227/2015) art. 469 alin. (1) lit. n), art. 470 alin. (2), (3)",
                "legislatie.just.ro via the Internet Archive, 2025-05-02 (`ro/law/cf_wb20250502.txt`; unchanged in the 2025-11-25 capture)", "A",
                "Codul fiscal, Legea nr. 227/2015, forma consolidată, legislatie.just.ro DetaliiDocument/171282 via the Internet Archive 2025-05-02 (`ro/law/cf_wb20250502.txt`)",
                ["art. 470 (2): for motorcycles, cars, buses and other motor vehicles up to 12 t the tax is each group of 200 cmc or fraction of it times the row's amount: cars up to 1.600 cmc 8 lei, 1.601-2.000 cmc 18, 2.001-2.600 cmc 72, 2.601-3.000 cmc 144, above 3.000 cmc 290; motorcycles up to 1.600 cmc 8, above 9",
                 "art. 470 (3): for hybrids the tax is reduced by at least 50 %, by decision of the local council: the model applies 50 %",
                 "art. 469 (1) n): electrically driven motor vehicles are not taxed (a fuel-cell car is read as electrically driven)",
                 "art. 491 (1): every amount in lei is indexed yearly by the local council for the previous year's inflation; art. 489: the council may add quotas: neither is applied (the statute's amounts are booked)"],
                [("!g.vehicles.isEmpty", "5200 impozitul pe mijloacele de transport: the statute's amounts of art. 470 (2) are booked without the Bucharest council's 2025 indexation (art. 491) and additional quotas (art. 489) (grade C for the local part)"),
                 ("g.vehicles.any (fun v => v.months < 12)", "5200 impozitul pe mijloacele de transport: the tax is owed for the whole year by the owner at 31 December of the previous year (a vehicle acquired in the year from the next 1 January); the model prorates by months held")],
                g, "buses, lorries (art. 470 (2) I.7-I.9, (5)-(7) by axles and mass), trailers, other kinds")


# PL: ustawa o podatku akcyzowym art. 100, 104, 105, 109a, 163a (excise on passenger cars: OECD 5121) and ustawa o
# podatkach i opłatach lokalnych art. 8 (podatek od środków transportowych: cars not taxable, 5200)
_PL_VEH = """
def p11plAkc (fs : List VehicleFuel) (lo hi bp : Int) (st : String) : VehicleTax :=
  { name := "Akcyza od samochodów osobowych", oecd := .excise, kinds := ["car"], fuels := fs, occasion := .registration,
    «when» := [(.engineCcm, lo, hi)], parts := [(.value, QtyTable.perUnit bp 10000)], statute := st }
def p11plIce : List VehicleFuel := [.petrol, .diesel, .lpg, .cng, .other]
def p11plAkcyza : List VehicleTax :=
  [{ name := "Akcyza od samochodów osobowych", oecd := .excise, kinds := ["car"], fuels := [.electric, .hydrogen], occasion := .registration,
     statute := "ustawa o podatku akcyzowym art. 109a ust. 1: a passenger car that is an electric vehicle or a hydrogen-driven vehicle is exempt" },
   { name := "Akcyza od samochodów osobowych", oecd := .excise, kinds := ["car"], fuels := [.pluginHybrid], occasion := .registration,
     «when» := [(.engineCcm, -1, 2000)],
     statute := "ustawa o podatku akcyzowym art. 163a ust. 1: to 31 December 2029 a plug-in hybrid (art. 2 pkt 13 ustawy o elektromobilności) with an engine of 2000 cm3 or less is exempt" },
   p11plAkc [.hybrid, .pluginHybrid] 2000 3500 930 "ustawa o podatku akcyzowym art. 104, art. 105 pkt 1a: hybrid with an engine above 2000 and not above 3500 cm3, 9,3 % of the base",
   p11plAkc [.hybrid] (-1) 2000 155 "ustawa o podatku akcyzowym art. 104, art. 105 pkt 1b: hybrid not charged from an external source, engine of 2000 cm3 or less, 1,55 % of the base",
   p11plAkc (p11plIce ++ [.hybrid, .pluginHybrid]) 2000 VehicleTax.noBound 1860 "ustawa o podatku akcyzowym art. 104, art. 105 pkt 1: engine above 2000 cm3, 18,6 % of the base",
   p11plAkc p11plIce (-1) 2000 310 "ustawa o podatku akcyzowym art. 104, art. 105 pkt 2: other passenger cars, 3,1 % of the base"]
def p11plSt : List VehicleTax :=
  [{ name := "Podatek od środków transportowych", kinds := ["car", "motorcycle", "van"], level := .local,
     statute := "ustawa o podatkach i opłatach lokalnych art. 8: only lorries above 3,5 t, tractor units, trailers from 7 t and buses are taxable: cars, motorcycles and vans are not" }]
"""

# HU: 1991. évi LXXXII. törvény a gépjárműadóról 5. § g), 6. § (1), 7. § (1), 7/A. §; NAV 2025 table
_HU_VEH = """
def p11huRow (lo hi r : Int) (st : String) : VehicleTax :=
  { name := "Gépjárműadó", kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .other],
    «when» := [(.age, lo, hi)], parts := [(.engineKw, QtyTable.perUnit r 1)], statute := st }
def p11huVeh : List VehicleTax :=
  [{ name := "Gépjárműadó", kinds := ["car"], fuels := [.electric, .hydrogen],
     statute := "Gjt. 5. § g): a környezetkímélő gépkocsi (KöHÉM 2. § (6): purely electric and other zero-emission cars) is exempt" },
   p11huRow (-1) 3 360 "Gjt. 6. § (1), 7. § (1), 7/A. §: year of manufacture and the 3 following calendar years, 360 Ft/kW (2025, NAV)",
   p11huRow 3 7 310 "Gjt. 6. § (1), 7. § (1), 7/A. §: 4th-7th calendar year after the year of manufacture, 310 Ft/kW (2025, NAV)",
   p11huRow 7 11 240 "Gjt. 6. § (1), 7. § (1), 7/A. §: 8th-11th calendar year, 240 Ft/kW (2025, NAV)",
   p11huRow 11 15 195 "Gjt. 6. § (1), 7. § (1), 7/A. §: 12th-15th calendar year, 195 Ft/kW (2025, NAV)",
   p11huRow 15 VehicleTax.noBound 145 "Gjt. 6. § (1), 7. § (1), 7/A. §: 16th calendar year and later, 145 Ft/kW (2025, NAV)"]
"""

# BY: Налоговый кодекс, Особенная часть, гл. 31-1 (ст. 307-1 ... 307-7), приложение 27
_BY_VEH = """
def p11byInd : QtyTable := QtyTable.ofCeilings [(1500, 70), (1750, 92), (2000, 116), (2250, 138), (2500, 161), (3000, 183)] 253
def p11byOrg : QtyTable := QtyTable.ofCeilings [(1000, 183), (2000, 237), (3000, 289)] 368
def p11byZero : List VehicleTax :=
  [{ name := "Транспортный налог", kinds := ["car"], fuels := [.electric],
     statute := "НК ст. 307-2 п. 2: M1 cars driven only by an electric motor are not an object of the tax to 31 December 2025" },
   { name := "Транспортный налог", kinds := ["car"], regTo := 1991,
     statute := "НК ст. 307-2 п. 2: vehicles made no later than 1991 are not an object of the tax" }]
def p11byVeh (company : Bool) : List VehicleTax :=
  p11byZero ++ [{ name := "Транспортный налог", kinds := ["car"], parts := [(.massKg, if company then p11byOrg else p11byInd)],
    statute := if company then "НК ст. 307-5 п. 1, ст. 307-7 п. 1, приложение 27 п. 1.1: organisation, passenger car by permitted maximum mass (BYN a year)"
               else "НК ст. 307-5 п. 1, ст. 307-7 п. 1, приложение 27 п. 2.1: individual, passenger car by permitted maximum mass (BYN a year)" }]
"""

# UA: Податковий кодекс ст. 267; Закон про Державний бюджет на 2025 рік ст. 8 (мінімальна заробітна плата 8 000 грн)
_UA_VEH = """
def p11uaVeh : List VehicleTax :=
  [{ name := "Транспортний податок", kinds := ["car"], «when» := [(.age, 5, VehicleTax.noBound)], level := .local,
     statute := "ПКУ п. 267.2.1: only cars of which no more than five years have passed since the year of manufacture are taxable" },
   { name := "Транспортний податок", kinds := ["car"], «when» := [(.value, -1, 3000000)], level := .local,
     statute := "ПКУ п. 267.2.1: only cars whose average market value exceeds 375 minimum wages (375 x 8 000 = 3 000 000 UAH on 1 January 2025) are taxable" },
   { name := "Транспортний податок", kinds := ["car"], «when» := [(.age, -1, 5), (.value, 3000000, VehicleTax.noBound)], fixed := 25000, level := .local,
     statute := "ПКУ п. 267.2.1, 267.4: 25 000 UAH a year for each car of at most five years with an average market value above 375 minimum wages" }]
"""


def _veh11b(S):
    cc = S["cc"]
    if not _veh_c(S):
        return
    if cc == "PL":
        _vstart11(S, "akcyza on passenger cars (5121, new registrations) and podatek od środków transportowych (cars, motorcycles, vans cited as not taxable) modelled; lorries, buses and trailers not modelled",
                  "ustawa o podatkach i opłatach lokalnych art. 10 with the reference municipality's 2025 resolution (rates within the ministerial maxima)")
        nw = 'kind := "car", fuel := .{f}, engineCcm := {c}, value := {v}, firstRegYear := 2025, newReg := true'
        g = [_vg("p11plAkcyza", nw.format(f="petrol", c=1498, v=100000), 3100), _vg("p11plAkcyza", nw.format(f="diesel", c=2500, v=200000), 37200),
             _vg("p11plAkcyza", nw.format(f="hybrid", c=1800, v=120000), 1860), _vg("p11plAkcyza", nw.format(f="hybrid", c=2500, v=200000), 18600),
             _vg("p11plAkcyza", nw.format(f="pluginHybrid", c=1500, v=150000), 0), _vg("p11plAkcyza", nw.format(f="pluginHybrid", c=2500, v=200000), 18600),
             _vg("p11plAkcyza", nw.format(f="hybrid", c=3600, v=200000), 37200), _vg("p11plAkcyza", nw.format(f="electric", c=0, v=200000), 0),
             _vg("p11plAkcyza", nw.format(f="petrol", c=2000, v=100000), 3100), _vg("p11plAkcyza", nw.format(f="petrol", c=2001, v=100000), 18600),
             _vg("p11plAkcyza", 'kind := "car", fuel := .petrol, engineCcm := 1498, value := 100000, firstRegYear := 2020', -1),
             _vg("p11plSt", 'kind := "car", fuel := .petrol, engineCcm := 1498, firstRegYear := 2020', 0),
             _vg("p11plSt", 'kind := "truck", fuel := .diesel, firstRegYear := 2020', -1)]
        _vfam11(S, "Akcyza od samochodów osobowych", _PL_VEH, "p11plAkcyza",
                "Ustawa o podatku akcyzowym art. 100 ust. 1, 104 ust. 1, 105, 109a ust. 1, 163a ust. 1", "tekst jednolity Dz. U. 2025 poz. 126 (`pl/law/akcyza_tj2025.txt`)", "A",
                "Ustawa z dnia 6 grudnia 2008 r. o podatku akcyzowym, tekst jednolity Dz. U. 2025 poz. 126, api.sejm.gov.pl (`pl/law/akcyza_tj2025.txt`)",
                ["art. 100 ust. 1: the excise on passenger cars falls on the import, the intra-Community acquisition and the first sale in Poland of a car not yet registered in Poland",
                 "art. 104 ust. 1: the base is the price of the sale net of VAT and excise, the amount paid on an intra-Community acquisition, or the customs value plus duty on import",
                 "art. 105: 18,6 % for an engine above 2000 cm3; 9,3 % for hybrids (charged or not from an external source) above 2000 and not above 3500 cm3; 1,55 % for hybrids not charged externally of 2000 cm3 or less; 3,1 % for other cars",
                 "art. 109a ust. 1: electric and hydrogen cars are exempt; art. 163a ust. 1: plug-in hybrids of 2000 cm3 or less are exempt to 31 December 2029",
                 "OECD classification: an excise on a good (5121), booked in the vehicle family because the event is the car's first registration in Poland"],
                [("g.vehicles.any (fun v => v.newReg)", "5121 akcyza: the vehicle's value is taken as the art. 104 base (price net of VAT and excise, or the amount paid abroad); a car first registered in Poland in the year is taken as not yet registered there (art. 100 ust. 1)")],
                g, "vehicles other than passenger cars, cars without engine size (an electric car needs none)", registration=True)
        S["taxes"][-1]["oecd"] = "5121"
        S["families"][-1] = (S["families"][-1][0].replace("5200", "5121"), [".excise"], S["families"][-1][2])
        _vfam11(S, "Podatek od środków transportowych", "", "p11plSt",
                "Ustawa o podatkach i opłatach lokalnych art. 8", "tekst jednolity Dz. U. 2025 poz. 707 (`pl/law/upol_tj2025_707.txt`)", "A",
                "Ustawa z dnia 12 stycznia 1991 r. o podatkach i opłatach lokalnych, tekst jednolity Dz. U. 2025 poz. 707, api.sejm.gov.pl (`pl/law/upol_tj2025_707.txt`)",
                ["art. 8: the tax falls on lorries above 3,5 t, tractor units, trailers and semi-trailers from 7 t with the vehicle, and buses: passenger cars, motorcycles and vans are outside it (cited 0)"],
                [], [], "lorries, tractor units, trailers and buses (taxable at the municipality's rates, not modelled)")
    elif cc == "HU":
        _vstart11(S, "gépjárműadó on cars modelled (2025 indexed rates); cégautóadó (company cars), buses, lorries and motorcycles not modelled",
                  "Gjt. 17/A-17/G. § and 1. melléklet (cégautóadó by kW and environmental class); 7. § (2) heavy vehicles with mass")
        car = 'kind := "car", fuel := .{f}, engineKw := {k}, firstRegYear := {y}'
        g = [_vg("p11huVeh", car.format(f="petrol", k=110, y=2019), 34100), _vg("p11huVeh", car.format(f="diesel", k=85, y=2022), 30600),
             _vg("p11huVeh", car.format(f="petrol", k=100, y=2021), 31000), _vg("p11huVeh", car.format(f="petrol", k=100, y=2017), 24000),
             _vg("p11huVeh", car.format(f="petrol", k=100, y=2010), 19500), _vg("p11huVeh", car.format(f="petrol", k=100, y=2009), 14500),
             _vg("p11huVeh", car.format(f="electric", k=150, y=2024), 0)]
        _vfam11(S, "Gépjárműadó", _HU_VEH, "p11huVeh",
                "1991. évi LXXXII. törvény a gépjárműadóról (Gjt.) 5. § g), 6. § (1), 7. § (1), 7/A. §", "Gjt. via the Internet Archive 2025-06-17 (`hu/law/gjt1991_wb2025.txt`); 2025 rates as published by NAV under 7/A. § (`hu/law/nav_gjt_valorizalt_2025.txt`)", "A",
                "1991. évi LXXXII. törvény a gépjárműadóról, net.jogtar.hu via the Internet Archive 2025-06-17 (`hu/law/gjt1991_wb2025.txt`); NAV, \"Belföldi gépjárműadó 2025. évre valorizált adómértéke\" (`hu/law/nav_gjt_valorizalt_2025.txt`)",
                ["6. § (1): the base of a passenger vehicle is its registered power in kW (horsepower / 1,36 where only hp is registered)",
                 "7. § (1): per kW, by calendar years after the year of manufacture: in that year and the 3 following 345 Ft, 4th-7th 300, 8th-11th 230, 12th-15th 185, from the 16th 140 (the 2024 amounts)",
                 "7/A. §: after 2024 each rate is the previous year's rate indexed by the July CPI change and rounded; NAV publishes the rates by 31 October: for 2025, 360 / 310 / 240 / 195 / 145 Ft/kW",
                 "5. § g): the környezetkímélő gépkocsi is exempt (electric and hydrogen cars read as such)"],
                [("!g.vehicles.isEmpty", "5200 gépjárműadó: the year of first registration is read as the year of manufacture (7. § (1) counts from the year of manufacture)"),
                 ("g.vehicles.any (fun v => v.fuel == .pluginHybrid)", "5200 gépjárműadó: a plug-in hybrid is taxed by kW; it is exempt only if classed környezetkímélő (KöHÉM 2. § (6)), which the input does not give"),
                 ("g.entity == .company && !g.vehicles.isEmpty", "5200 cégautóadó (Gjt. 17/A-17/G. §, company cars, gépjárműadó deductible under 17/F. §) not modelled (grade C)")],
                g, "motorcycles, buses, lorries (7. § (2) per 100 kg), trailers")
    elif cc == "BY":
        _vstart11(S, "транспортный налог on passenger cars modelled; lorries, buses, trailers, motorcycles and the high-comfort list (ст. 307-7 п. 11) not modelled",
                  "приложение 27 п. 1.2-1.8, 2.2-2.8 (other kinds); the Council of Ministers' list of high-comfort vehicles")
        ts = "(p11byVeh (g.entity == .company))"
        car = 'kind := "car", fuel := .{f}, massKg := {m}, firstRegYear := {y}'
        g = [_vg("(p11byVeh false)", car.format(f="petrol", m=1850, y=2018), 116), _vg("(p11byVeh false)", car.format(f="petrol", m=1500, y=2018), 70),
             _vg("(p11byVeh false)", car.format(f="diesel", m=3100, y=2018), 253), _vg("(p11byVeh true)", car.format(f="diesel", m=1850, y=2018), 237),
             _vg("(p11byVeh true)", car.format(f="diesel", m=3100, y=2018), 368), _vg("(p11byVeh false)", car.format(f="electric", m=2100, y=2023), 0),
             _vg("(p11byVeh false)", car.format(f="petrol", m=1300, y=1990), 0)]
        _vfam11(S, "Транспортный налог", _BY_VEH, ts,
                "Налоговый кодекс, Особенная часть, гл. 31-1: ст. 307-1, 307-2, 307-4, 307-5, 307-7, приложение 27", "pravo.by via the Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`)", "A",
                "Налоговый кодекс Республики Беларусь, Особенная часть, pravo.by via the Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`)",
                ["ст. 307-2: the object is a vehicle registered with the State Automobile Inspection; not objects: vehicles made no later than 1991, and M1 cars driven only by an electric motor to 31 December 2025",
                 "ст. 307-4: the base is the number of vehicles; ст. 307-5 п. 1, приложение 27: annual rates in roubles by permitted maximum mass",
                 "приложение 27 п. 2.1 (individuals): up to 1,5 t 70, to 1,75 t 92, to 2 t 116, to 2,25 t 138, to 2,5 t 161, to 3 t 183, above 3 t 253; п. 1.1 (organisations): up to 1 t 183, to 2 t 237, to 3 t 289, above 3 t 368",
                 "ст. 307-7 п. 4: a vehicle registered in the year is taxed from the month after registration (the model prorates by months held); п. 11: the high-comfort list multiplies the rate (not modelled)"],
                [("!g.vehicles.isEmpty", "5200 транспортный налог: massKg is read as the permitted maximum mass (разрешенная максимальная масса); the 50 % / 75 % rates for veterans and disabled persons (ст. 307-5 п. 2, 3) are not applied"),
                 ("!g.vehicles.isEmpty", "5200 транспортный налог: a vehicle on the Council of Ministers' high-comfort list (ст. 307-7 п. 11) is taxed at the plain rate (grade C for the increase)")],
                g, "motorcycles, lorries, buses, trailers (приложение 27 other points)")
    elif cc == "UA":
        _vstart11(S, "транспортний податок (ПКУ ст. 267) modelled; no other annual vehicle tax on households",
                  "the ministry's 2025 list of cars with an average market value above 375 minimum wages (the input's value stands for it)")
        car = 'kind := "car", fuel := .petrol, value := {v}, firstRegYear := {y}'
        g = [_vg("p11uaVeh", car.format(v=3500000, y=2022), 25000), _vg("p11uaVeh", car.format(v=3500000, y=2020), 25000),
             _vg("p11uaVeh", car.format(v=3500000, y=2019), 0), _vg("p11uaVeh", car.format(v=3000000, y=2023), 0),
             _vg("p11uaVeh", car.format(v=3000001, y=2023), 25000)]
        _vfam11(S, "Транспортний податок", _UA_VEH, "p11uaVeh",
                "Податковий кодекс України ст. 267 (п. 267.2.1, 267.4); Закон про Державний бюджет України на 2025 рік ст. 8",
                "ПКУ via the Internet Archive 2025-06-20 (`ua/law/ptk_wb20250620.txt`); budget law via the Internet Archive 2025-05-31 (`ua/law/budget2025_4059.txt`)", "A",
                "Податковий кодекс України, zakon.rada.gov.ua via the Internet Archive 2025-06-20 (`ua/law/ptk_wb20250620.txt`); Закон України № 4059-IX \"Про Державний бюджет України на 2025 рік\" via the Internet Archive 2025-05-31 (`ua/law/budget2025_4059.txt`)",
                ["п. 267.2.1: the object is a car of which no more than five years (inclusive) have passed since the year of manufacture and whose average market value exceeds 375 minimum wages set by law on 1 January of the year",
                 "budget law 2025 ст. 8: minimum wage from 1 January 2025, 8 000 UAH a month: threshold 3 000 000 UAH",
                 "п. 267.4: 25 000 UAH a year for each such car; п. 267.6.2: a car acquired in the year is taxed from the month of acquisition (the model prorates by months held)"],
                [("!g.vehicles.isEmpty", "5200 транспортний податок: the vehicle's value stands for the ministry's average market value and its first-registration year for the year of manufacture")],
                g, "vehicles other than passenger cars (not objects of the tax)")

# IT: tassa automobilistica regionale, Regione Lazio (Roma), tariffario 2025 (DD G16786 of 11.12.2024)
_IT_VEH = """
/-- euro cents per kW up to 100 kW, and per kW above 100 kW (den 100: whole euros, rounded down) -/
def p11itKw (a b : Int) : QtyTable := { steps := [(0, a), (100, b)], den := 100 }
def p11itBollo : String := "Tassa automobilistica regionale (bollo)"
def p11itRow (lo hi a b : Int) (st : String) : VehicleTax :=
  { name := p11itBollo, kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .pluginHybrid], «when» := [(.euroClass, lo, hi)],
    parts := [(.engineKw, p11itKw a b)], minAmount := 21, level := .local, statute := st }
def p11itVeh : List VehicleTax :=
  [{ name := p11itBollo, kinds := ["car"], «when» := [(.age, 29, VehicleTax.noBound)], level := .local,
     statute := "Regione Lazio, tariffario 2025, esenzioni 2): cars from the 30th year after construction are exempt" },
   { name := p11itBollo, kinds := ["car"], fuels := [.electric], «when» := [(.age, -1, 4)], level := .local,
     statute := "Regione Lazio, tariffario 2025, esenzioni 4) (D.P.R. 39/1953): electric cars, five years from first registration" },
   { name := p11itBollo, kinds := ["car"], fuels := [.electric, .lpg, .cng, .hydrogen], parts := [(.engineKw, QtyTable.perUnit 284 100)],
     minAmount := 21, level := .local,
     statute := "Regione Lazio, tariffario 2025, esenzioni 5): cars running only or also on electricity, methane, LPG or hydrogen, 2,84 EUR per kW whatever the Euro class" },
   p11itRow (-1) 0 330 495 "Regione Lazio, tariffario 2025: Euro 0, 3,30 EUR per kW up to 100 kW, 4,95 EUR per kW above",
   p11itRow 0 1 319 479 "Regione Lazio, tariffario 2025: Euro 1, 3,19 EUR per kW up to 100 kW, 4,79 EUR per kW above",
   p11itRow 1 2 308 462 "Regione Lazio, tariffario 2025: Euro 2, 3,08 EUR per kW up to 100 kW, 4,62 EUR per kW above",
   p11itRow 2 3 297 446 "Regione Lazio, tariffario 2025: Euro 3, 2,97 EUR per kW up to 100 kW, 4,46 EUR per kW above",
   p11itRow 3 VehicleTax.noBound 284 426 "Regione Lazio, tariffario 2025: Euro 4, 5, 6, 2,84 EUR per kW up to 100 kW, 4,26 EUR per kW above"]
"""


def _veh11c(S):
    cc = S["cc"]
    if not _veh_c(S):
        return
    if cc == "IT":
        _vstart11(S, "tassa automobilistica (bollo) on cars for Regione Lazio modelled; superbollo, IPT (provincial registration tax), motorcycles and other classes not modelled",
                  "D.L. 98/2011 art. 23 c. 21 (superbollo 20 EUR per kW above 185 kW, by age); D.Lgs. 446/1997 art. 56 and the Città metropolitana di Roma's IPT tariff; the motorcycle rows of the tariffario")
        car = 'kind := "car", fuel := .{f}, engineKw := {k}, euroClass := {e}, firstRegYear := {y}'
        g = [_vg("p11itVeh", car.format(f="petrol", k=110, e=6, y=2019), 326), _vg("p11itVeh", car.format(f="diesel", k=90, e=3, y=2004), 267),
             _vg("p11itVeh", car.format(f="petrol", k=120, e=0, y=1998), 429), _vg("p11itVeh", car.format(f="petrol", k=100, e=1, y=1996), 319),
             _vg("p11itVeh", car.format(f="petrol", k=101, e=2, y=2000), 312), _vg("p11itVeh", car.format(f="petrol", k=5, e=6, y=2020), 21),
             _vg("p11itVeh", car.format(f="lpg", k=110, e=6, y=2020), 312), _vg("p11itVeh", car.format(f="electric", k=150, e=6, y=2023), 0),
             _vg("p11itVeh", car.format(f="electric", k=150, e=6, y=2018), 426), _vg("p11itVeh", car.format(f="petrol", k=150, e=0, y=1990), 0),
             _vg("p11itVeh", 'kind := "car", fuel := .petrol, engineKw := 110, firstRegYear := 2019', -1)]
        _vfam11(S, "Tassa automobilistica regionale (bollo)", _IT_VEH, "p11itVeh",
                "D.P.R. 39/1953; D.Lgs. 504/1992 art. 23-24; L. 296/2006 art. 1 c. 321; Regione Lazio, Determinazione G16786 dell'11.12.2024 (tariffario 2025)",
                "tariffario 2025, valid from 1 January 2025 (`it/law/lazio_dd_g16786.txt`, `it/law/lazio_tariffario2025_g16786.pdf`; the table is an image, read by OCR: `lazio_tariffario2025_g16786_ocr.txt`)", "B",
                "Regione Lazio, Determinazione n. G16786 dell'11/12/2024 \"Tariffario Anno 2025 delle Tasse Automobilistiche della Regione Lazio\" and its allegato, regione.lazio.it (`it/law/lazio_dd_g16786.txt`, `it/law/lazio_tariffario2025_g16786.pdf`)",
                ["the tax is based on the engine's maximum power in kW from the registration certificate and on its Euro class: Euro 0 3,30 / 4,95; Euro 1 3,19 / 4,79; Euro 2 3,08 / 4,62; Euro 3 2,97 / 4,46; Euro 4, 5, 6 2,84 / 4,26 EUR per kW up to 100 kW / per kW above (the national L. 296/2006 tariff raised by 10 % under D.Lgs. 504/1992 art. 24)",
                 "minimum 21,02 EUR; amounts are rounded to the cent (the model books whole euros, rounded down, and a 21 EUR minimum)",
                 "exempt: electric cars for five years from first registration, cars from the 30th year after construction; cars running only or also on electricity, methane, LPG or hydrogen pay 2,84 EUR per kW whatever the class",
                 "grade B: the region's official tariff table, read by OCR from the published PDF; the regional law text is not on disk"],
                [("!g.vehicles.isEmpty", "5200 bollo: the region of Roma (Lazio) is taken; the year of first registration stands for the year of construction (30-year exemption); amounts in whole euros (rounded down)"),
                 ("g.vehicles.any (fun v => (v.fuel == .hybrid || v.fuel == .pluginHybrid) && v.firstRegYear == 2022)", "5200 bollo: a hybrid first registered in 2022 may still be in Lazio's three-year exemption (tariffario, esenzioni 5)): taxed at the Euro-class tariff"),
                 ("g.vehicles.any (fun v => 185 < v.engineKw)", "5200 superbollo (D.L. 98/2011 art. 23 c. 21, 20 EUR per kW above 185 kW) not modelled (grade C)")],
                g, "motorcycles, mopeds, lorries, buses and other classes (other rows of the tariffario)")

# DK: brændstofforbrugsafgiftsloven (LBK nr. 1050 af 12/08/2025) § 3 c (cars first registered from 1 July 2021, CO2 WLTP)
_DK_CEIL = [58, 65, 73, 80, 87, 102, 116, 131, 145, 160, 174, 189, 203, 218, 232, 246, 262, 277, 290, 319, 350, 377, 409, 433, 461, 492, 519, 548, 581, 605, 645]
_DK_A = [390, 440, 460, 480, 510, 540, 590, 640, 680, 1040, 1390, 1770, 2130, 2480, 2840, 3190, 3560, 3920, 4280, 4980, 5730, 6440, 7150, 7870, 8600, 9310, 10030, 10770, 11490, 12200, 12910, 13650]
_DK_U = [160] * 6 + [740, 1320, 1420, 1570, 1690, 1820, 1960, 2100, 2260, 2400, 2560, 2680, 2810, 3110, 3370, 3630, 3950, 4180, 4440, 4770, 5020, 5290, 5600, 5880, 6240, 6530]


def _up10(x):
    return -(-x // 10) * 10


def _dk_lean():
    a = [2 * _up10(-(-a0 * 1065 // 1000)) for a0 in _DK_A]
    u = [2 * _up10(-(-u0 * 70 // 100)) for u0 in _DK_U]
    tab = lambda xs: "QtyTable.ofCeilings [" + ", ".join(f"({c}, {x})" for c, x in zip(_DK_CEIL, xs[:-1])) + f"] {xs[-1]}"
    return a, u, f"""
/-- brændstofforbrugsafgiftsloven § 3 c stk. 1 A, stk. 3: CO2-baseret afgift for 2025 (half-year amounts + 6,5 %, rounded up to
10 kr, two periods), kroner a year by g CO2/km -/
def p11dkA : QtyTable := {tab(a)}
/-- § 3 c stk. 1 A, stk. 4: udligningsafgift for diesel cars, 2025 (half-year amounts − 30 %, rounded up to 10 kr), a year -/
def p11dkU : QtyTable := {tab(u)}
def p11dkVeh : List VehicleTax :=
  [{{ name := "Brændstofforbrugsafgift (grøn ejerafgift)", kinds := ["car"], fuels := [.diesel], regFrom := 2021, parts := [(.co2GKm, p11dkA), (.co2GKm, p11dkU)],
     statute := "brændstofforbrugsafgiftsloven § 3 c stk. 1 A, stk. 3, 4: CO2-baseret afgift and udligningsafgift (diesel), cars first registered from 1 July 2021, 2025 amounts" }},
   {{ name := "Brændstofforbrugsafgift (grøn ejerafgift)", kinds := ["car"], fuels := [.petrol, .electric, .hybrid, .pluginHybrid, .lpg, .cng, .hydrogen, .other], regFrom := 2021,
     parts := [(.co2GKm, p11dkA)],
     statute := "brændstofforbrugsafgiftsloven § 3 c stk. 1 A, stk. 3: CO2-baseret afgift, cars first registered from 1 July 2021, 2025 amounts" }}]
"""


def _veh11d(S):
    cc = S["cc"]
    if not _veh_c(S):
        return
    if cc == "DK":
        a, u, lean = _dk_lean()
        amt = lambda xs, c: next((x for cl, x in zip(_DK_CEIL, xs) if c <= cl), xs[-1])
        _vstart11(S, "grøn ejerafgift (§ 3 c, CO2) on cars first registered from July 2021 modelled; older cars (km/l, § 3), registreringsafgift, vægtafgift and vans not modelled",
                  "brændstofforbrugsafgiftsloven § 3 with the car's km/l (an input attribute the kernel lacks); registreringsafgiftsloven (LBK) § 4-5 with the taxable value; vægtafgiftsloven")
        car = 'kind := "car", fuel := .{f}, co2GKm := {c}, firstRegYear := {y}'
        g = [f"p11dkA.amount 120 == {amt(a, 120)}", f"p11dkA.amount 58 == {a[0]}", f"p11dkA.amount 646 == {a[-1]}", f"p11dkU.amount 100 == {u[0]}", f"p11dkU.amount 140 == {amt(u, 140)}",
             _vg("p11dkVeh", car.format(f="petrol", c=120, y=2023), amt(a, 120)), _vg("p11dkVeh", car.format(f="diesel", c=140, y=2022), amt(a, 140) + amt(u, 140)),
             _vg("p11dkVeh", car.format(f="electric", c=0, y=2024), a[0]), _vg("p11dkVeh", car.format(f="petrol", c=120, y=2019), -1)]
        _vfam11(S, "Brændstofforbrugsafgift (grøn ejerafgift)", lean, "p11dkVeh",
                "Brændstofforbrugsafgiftsloven (LBK nr. 1050 af 12. august 2025) § 1, § 3 c, § 4", "retsinformation.dk, LBK nr. 1050 af 12/08/2025 (`dk/law/bfa_lbk2025_1050.txt`)", "A",
                "Bekendtgørelse af lov om afgift efter brændstofforbrug m.v. for visse person- og varebiler (brændstofforbrugsafgiftsloven), LBK nr. 1050 af 12/08/2025, retsinformation.dk (`dk/law/bfa_lbk2025_1050.txt`)",
                ["§ 3 c stk. 1: cars first registered on 1 July 2021 or later pay by WLTP CO2 g/km: per six months 390 kr up to 58 g, rising by bands to 13 650 kr above 645 g; diesel cars also pay udligningsafgift (160 kr to 6 530 kr)",
                 "§ 3 c stk. 3: for 2025 the CO2 amounts rise by 6,5 %; stk. 4: for 2025 and 2026 the udligningsafgift falls by 30 %; both rounded up to whole kroner divisible by ten",
                 "§ 4: six-month periods, paid from the day of registration: the model books two periods for a car held all year (prorated by months otherwise)",
                 "§ 3 b: diesel cars without a measured particle emission of at most 5 mg/km pay 1 000 kr a year more (not in the input)"],
                [("g.vehicles.any (fun v => v.firstRegYear == 2021)", "5200 grøn ejerafgift: a car first registered in 2021 is taken as registered from 1 July 2021 (§ 3 c)"),
                 ("g.vehicles.any (fun v => v.fuel == .diesel)", "5200 grøn ejerafgift: a diesel car is taken as having a measured particle emission of at most 5 mg/km (no § 3 b surcharge of 1 000 kr)"),
                 ("g.vehicles.any (fun v => v.newReg)", "5200 registreringsafgift (registreringsafgiftsloven) on a car registered in the year not modelled (grade C)")],
                g, "cars first registered before July 2021 (km/l tables of § 3, not an input attribute), vans, other kinds")


# PT: Código do IUC (Lei 22-A/2007, anexo II) art. 2 n.º 1 b), 5 n.º 1 e), 10 (redação da Lei 82/2023; unchanged by Lei 45-A/2024)
_PT_VEH = """
/-- Código do IUC art. 10 n.º 1: cilindrada component (cents) -/
def p11ptCc : QtyTable := QtyTable.ofCeilings [(1250, 3177), (1750, 6374), (2500, 12735)] 43584
/-- art. 10 n.º 1: CO2 component, NEDC and WLTP columns (cents) -/
def p11ptCo2N : QtyTable := QtyTable.ofCeilings [(120, 6515), (180, 9763), (250, 21204)] 36325
def p11ptCo2W : QtyTable := QtyTable.ofCeilings [(140, 6515), (205, 9763), (260, 21204)] 36325
/-- art. 10 n.º 2: taxas adicionais for a first registration after 1 January 2017 (cents) -/
def p11ptAddN : QtyTable := QtyTable.ofCeilings [(180, 0), (250, 3177)] 6374
def p11ptAddW : QtyTable := QtyTable.ofCeilings [(205, 0), (260, 3177)] 6374
def p11ptIuc : String := "Imposto único de circulação (categoria B)"
/-- multiplierBp = the art. 10 n.º 3 coefficient (1,00 / 1,05 / 1,10 / 1,15) in hundredths, which also turns cents into euros -/
def p11ptB (f t : Nat) (ps : List (VehicleAttr × QtyTable)) (bp : Int) (st : String) : VehicleTax :=
  { name := p11ptIuc, kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .hydrogen, .other],
    regFrom := f, regTo := t, parts := ps, multiplierBp := bp, statute := st }
def p11ptVeh : List VehicleTax :=
  [{ name := p11ptIuc, kinds := ["car"], fuels := [.electric], regFrom := 2007,
     statute := "Código do IUC art. 5.º n.º 1 e): exclusively electric vehicles are exempt" },
   p11ptB 2020 0 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2W), (.co2GKm, p11ptAddW)] 115 "Código do IUC art. 10.º n.º 1, 2 (WLTP columns), n.º 3 (coefficient 1,15)",
   p11ptB 2017 2019 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N), (.co2GKm, p11ptAddN)] 115 "Código do IUC art. 10.º n.º 1, 2 (NEDC columns), n.º 3 (coefficient 1,15)",
   p11ptB 2010 2016 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N)] 115 "Código do IUC art. 10.º n.º 1 (NEDC), n.º 3 (coefficient 1,15)",
   p11ptB 2009 2009 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N)] 110 "Código do IUC art. 10.º n.º 1 (NEDC), n.º 3 (coefficient 1,10)",
   p11ptB 2008 2008 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N)] 105 "Código do IUC art. 10.º n.º 1 (NEDC), n.º 3 (coefficient 1,05)",
   p11ptB 2007 2007 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N)] 100 "Código do IUC art. 10.º n.º 1 (NEDC), n.º 3 (coefficient 1,00)"]
"""


def _veh11e(S):
    cc = S["cc"]
    if not _veh_c(S):
        return
    if cc == "PT":
        _vstart11(S, "IUC category B (cars first registered from July 2007) modelled; category A (older cars), the diesel adicional de IUC, ISV (registration) and other categories not modelled",
                  "Código do IUC art. 9 (category A table, an image on the portal); Lei 82-B/2014 art. 216 (adicional de IUC, diesel); Código do ISV art. 7 tables (images) with the cilindrada and CO2 of a new car")
        car = 'kind := "car", fuel := .{f}, engineCcm := {c}, co2GKm := {e}, firstRegYear := {y}'
        g = [_vg("p11ptVeh", car.format(f="petrol", c=1499, e=130, y=2021), 148), _vg("p11ptVeh", car.format(f="diesel", c=1998, e=150, y=2021), 258),
             _vg("p11ptVeh", car.format(f="petrol", c=2998, e=210, y=2018), 781), _vg("p11ptVeh", car.format(f="petrol", c=1600, e=150, y=2008), 169),
             _vg("p11ptVeh", car.format(f="petrol", c=3000, e=270, y=2024), 992), _vg("p11ptVeh", car.format(f="electric", c=0, e=0, y=2022), 0),
             _vg("p11ptVeh", car.format(f="petrol", c=1499, e=130, y=2005), -1)]
        _vfam11(S, "Imposto único de circulação (categoria B)", _PT_VEH, "p11ptVeh",
                "Código do Imposto Único de Circulação (Lei 22-A/2007, anexo II) art. 2.º n.º 1 b), 5.º n.º 1 e), 10.º (redação da Lei 82/2023)",
                "Portal das Finanças, codigos tributarios, read 2026-11-21 (`pt/law/iuc2_portal.txt`, `iuc5_portal.txt`, `iuc10_portal.txt`; the art. 10 n.º 1 and 2 tables are images: `iuc10_oe2024_01.png`, `iuc10_oe2024_02.png`, read by OCR); OE 2025 (Lei 45-A/2024, `pt/law/Lei_45_A_2024.txt`) changes no IUC rate", "A",
                "Código do IUC, info.portaldasfinancas.gov.pt (art. 2, 5, 10 and the table images of art. 10, redação da Lei n.º 82/2023)",
                ["art. 2.º n.º 1 b): category B = passenger cars first registered in Portugal or in the EU/EEA after the code entered into force (1 July 2007)",
                 "art. 10.º n.º 1: cilindrada component up to 1 250 cm3 31,77 EUR, to 1 750 63,74, to 2 500 127,35, above 435,84; CO2 component NEDC up to 120 g/km (WLTP 140) 65,15, to 180 (205) 97,63, to 250 (260) 212,04, above 363,25",
                 "art. 10.º n.º 2: first registration after 1 January 2017: an additional 31,77 EUR for NEDC 180-250 g/km (WLTP 205-260) and 63,74 EUR above",
                 "art. 10.º n.º 3: the sum is multiplied by 1,00 (first registration 2007), 1,05 (2008), 1,10 (2009), 1,15 (2010 and later)",
                 "art. 5.º n.º 1 e): exclusively electric vehicles are exempt"],
                [("!g.vehicles.isEmpty", "5200 IUC: CO2 of a car first registered from 2020 is read in the WLTP column, earlier ones in the NEDC column (Lei 119/2019 note); a car of 2007 is taken as registered after 1 July 2007; amounts rounded down to whole euros"),
                 ("g.vehicles.any (fun v => v.fuel == .diesel)", "5200 adicional de IUC (Lei 82-B/2014 art. 216, kept by Lei 45-A/2024 art. 113) on diesel cars not modelled (grade C)"),
                 ("g.vehicles.any (fun v => v.newReg)", "5200 ISV (Código do ISV) on a car registered in the year not modelled (grade C)")],
                g, "cars first registered before July 2007 (category A, art. 9), motorcycles, goods vehicles and other categories")


# NO: Stortingsvedtak om avgift på trafikkforsikringer for 2025 (LTI 2024-12-13-3212); om engangsavgift på motorvogner mv. for 2025 (3211)
_NO_VEH = """
/-- daily rates in øre x 365 (multiplierBp 100: kroner) -/
def p11noT (ks : List String) (fs : List VehicleFuel) (w : List (VehicleAttr × Int × Int)) (perDay : Int) (st : String) : VehicleTax :=
  { name := "Trafikkforsikringsavgift", kinds := ks, fuels := fs, «when» := w, fixed := perDay * 365, multiplierBp := 100, statute := st }
def p11noTfa : List VehicleTax :=
  [p11noT ["car", "van", "motorcycle"] [] [(.age, 29, VehicleTax.noBound)] 37 "Stortingsvedtak om avgift på trafikkforsikringer 2025 § 2, avgiftsgruppe e nr. 10 (30 years or older): 0,37 kr per day",
   p11noT ["car", "van"] [.electric, .hydrogen] [] 870 "Stortingsvedtak om avgift på trafikkforsikringer 2025 § 2, avgiftsgruppe f (electricity only, incl. fuel cells): 8,70 kr per day (contract with hovedforfall from 1 March 2024 to February 2025)",
   p11noT ["car", "van"] [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .other] [] 760 "Stortingsvedtak om avgift på trafikkforsikringer 2025 § 2, avgiftsgruppe a: 7,60 kr per day (contract with hovedforfall from 1 March 2024 to February 2025)",
   p11noT ["motorcycle"] [] [] 523 "Stortingsvedtak om avgift på trafikkforsikringer 2025 § 2, avgiftsgruppe d: 5,23 kr per day (contract with hovedforfall from 1 March 2024 to February 2025)"]
/-- engangsavgift § 2: 12,44 kr per kg of egenvekt above 500 kg (den 100: kroner); § 5: vrakpantavgift 2 400 kr -/
def p11noEng : List VehicleTax :=
  [{ name := "Engangsavgift på motorvogner", kinds := ["car"], fuels := [.electric, .hydrogen], occasion := .registration, fixed := 2400,
     parts := [(.massKg, { steps := [(500, 1244)], den := 100 })],
     statute := "Stortingsvedtak om engangsavgift på motorvogner mv. 2025 § 2 (12,44 kr per kg of egenvekt above 500 kg; § 3 applies only to piston combustion engines), § 5 (vrakpantavgift 2 400 kr)" }]
"""


def _veh11f(S):
    cc = S["cc"]
    if not _veh_c(S):
        return
    if cc == "NO":
        _vstart11(S, "trafikkforsikringsavgift (cars, vans, motorcycles) and engangsavgift on new electric cars modelled; engangsavgift on combustion-engine cars (NOx is not an input attribute), vektårsavgift and omregistreringsavgift not modelled",
                  "the car's NOx mg/km (engangsavgift § 3 a 2) and a rule for negative CO2 deductions below 70 g/km; Stortingsvedtak om vektårsavgift and om omregistreringsavgift 2025")
        car = 'kind := "car", fuel := .{f}, firstRegYear := {y}'
        g = [_vg("p11noTfa", car.format(f="petrol", y=2020), 2774), _vg("p11noTfa", car.format(f="electric", y=2023), 3175),
             _vg("p11noTfa", car.format(f="petrol", y=1990), 135), _vg("p11noTfa", 'kind := "motorcycle", fuel := .petrol, firstRegYear := 2015', 1908),
             _vg("p11noEng", 'kind := "car", fuel := .electric, massKg := 2100, firstRegYear := 2025, newReg := true', 22304),
             _vg("p11noEng", 'kind := "car", fuel := .petrol, massKg := 1400, firstRegYear := 2025, newReg := true', -1)]
        _vfam11(S, "Trafikkforsikringsavgift", _NO_VEH, "p11noTfa",
                "Stortingsvedtak om avgift på trafikkforsikringer for 2025 (FOR-2024-12-13-3212) § 1, § 2", "Lovdata (`no/law/stv_tfa2025.txt`)", "A",
                "Stortingsvedtak om avgift på trafikkforsikringer for 2025, Lovdata LTI/forskrift/2024-12-13-3212 (`no/law/stv_tfa2025.txt`)",
                ["§ 1: the tax is due on the compulsory motor liability insurance of Norwegian-registered vehicles; § 2: kroner per day by group and by the date of the contract's main renewal (before 1 March 2024 / 1 March 2024 to February 2025 / from 1 March 2025)",
                 "group a (cars, vans and other vehicles listed): 8,38 / 7,60 / 6,38; group b (diesel without a factory particle filter): 9,84 / 9,11 / 7,93; group d (motorcycles): 6,10 / 5,23 / 5,39; group e (incl. vehicles of 30 years or more): 1,42 / 0,37 / 0,38; group f (electricity only, incl. fuel cells): 8,38 / 8,70 / 8,96",
                 "the model takes a contract renewed on 1 January 2025 (the middle column for the whole year, x 365 days)"],
                [("!g.vehicles.isEmpty", "5200 trafikkforsikringsavgift: the insurance contract is taken as renewed on 1 January 2025 (column 'fra 1. mars 2024 t.o.m. februar 2025' all year); a renewal from March 2025 gives the lower last column (grade C for the split)"),
                 ("g.vehicles.any (fun v => v.fuel == .diesel)", "5200 trafikkforsikringsavgift: a diesel vehicle is taken as having a factory-fitted particle filter (group a, not b)")],
                g, "tractors, mopeds, motor equipment and other groups")
        _vfam11(S, "Engangsavgift på motorvogner", "", "p11noEng",
                "Stortingsvedtak om engangsavgift på motorvogner mv. for 2025 (FOR-2024-12-13-3211) § 2, § 3, § 5", "Lovdata (`no/law/stv_engangs2025.txt`)", "A",
                "Stortingsvedtak om engangsavgift på motorvogner mv. for 2025, Lovdata LTI/forskrift/2024-12-13-3211 (`no/law/stv_engangs2025.txt`)",
                ["§ 2: for passenger cars (group a) 12,44 kr per kg of the egenvekt above 500 kg, in addition to § 3",
                 "§ 3: for piston combustion engines also egenvekt bands, NOx (85,88 kr per mg/km) and CO2 bands with deductions below 70 g/km: not modelled (NOx is not an input attribute)",
                 "§ 5: vrakpantavgift 2 400 kr per car of group a (booked with the registration)"],
                [("g.vehicles.any (fun v => v.newReg)", "5200 engangsavgift: massKg is read as the egenvekt; the bruksfradrag for a used import (§ 4) is not applied")],
                g[:0], "new cars with a combustion engine (§ 3 needs NOx), other groups", registration=True)


# HR: Zakon o lokalnim porezima (NN 115/16 ... 152/24) čl. 11-12 (porez na cestovna motorna vozila, a county tax)
_HR_VEH = """
def p11hrCar (a b c d e : Int) : QtyTable := QtyTable.ofCeilings [(55, a), (70, b), (100, c), (130, d)] e
def p11hrMoto (a b c d : Int) : QtyTable := QtyTable.ofCeilings [(20, a), (50, b), (80, c)] d
def p11hrPcmv : String := "Porez na cestovna motorna vozila"
def p11hrRow (k : String) (lo hi : Int) (t : QtyTable) (st : String) : VehicleTax :=
  { name := p11hrPcmv, kinds := [k], «when» := [(.age, lo, hi)], parts := [(.engineKw, t)], level := .local, statute := st }
def p11hrVeh : List VehicleTax :=
  [{ name := p11hrPcmv, kinds := ["car", "motorcycle"], «when» := [(.age, 10, VehicleTax.noBound)], level := .local,
     statute := "Zakon o lokalnim porezima čl. 11 st. 3: the tables stop at 10 years of age: older cars and motorcycles pay none" },
   p11hrRow "car" (-1) 2 (p11hrCar 40 53 80 119 199) "Zakon o lokalnim porezima čl. 11 st. 3 t. 1: osobni automobili up to 2 years of age, EUR by kW",
   p11hrRow "car" 2 5 (p11hrCar 33 46 66 93 159) "Zakon o lokalnim porezima čl. 11 st. 3 t. 1: osobni automobili 2 to 5 years of age, EUR by kW",
   p11hrRow "car" 5 10 (p11hrCar 27 33 53 80 133) "Zakon o lokalnim porezima čl. 11 st. 3 t. 1: osobni automobili 5 to 10 years of age, EUR by kW",
   p11hrRow "motorcycle" (-1) 2 (p11hrMoto 13 27 66 159) "Zakon o lokalnim porezima čl. 11 st. 3 t. 2: motocikli up to 2 years of age",
   p11hrRow "motorcycle" 2 5 (p11hrMoto 11 20 53 133) "Zakon o lokalnim porezima čl. 11 st. 3 t. 2: motocikli 2 to 5 years of age",
   p11hrRow "motorcycle" 5 10 (p11hrMoto 7 13 40 106) "Zakon o lokalnim porezima čl. 11 st. 3 t. 2: motocikli 5 to 10 years of age"]
"""


def _veh11g(S):
    cc = S["cc"]
    if not _veh_c(S):
        return
    if cc == "HR":
        _vstart11(S, "porez na cestovna motorna vozila (cars, motorcycles) modelled; posebni porez na motorna vozila (registration) and the annual road-use fee not modelled",
                  "Zakon o posebnom porezu na motorna vozila (CO2 table and price) with the price of a new car; the Pravilnik on the godišnja naknada za uporabu javnih cesta")
        car = 'kind := "car", fuel := .petrol, engineKw := {k}, firstRegYear := {y}'
        g = [_vg("p11hrVeh", car.format(k=85, y=2021), 66), _vg("p11hrVeh", car.format(k=55, y=2024), 40), _vg("p11hrVeh", car.format(k=56, y=2023), 53),
             _vg("p11hrVeh", car.format(k=140, y=2018), 133), _vg("p11hrVeh", car.format(k=140, y=2014), 0),
             _vg("p11hrVeh", 'kind := "motorcycle", fuel := .petrol, engineKw := 60, firstRegYear := 2022', 53)]
        _vfam11(S, "Porez na cestovna motorna vozila", _HR_VEH, "p11hrVeh",
                "Zakon o lokalnim porezima (NN 115/16, 101/17, 114/22, 114/23, 152/24) čl. 11, 12", "consolidated text in force from 1 January 2024 (zakon.hr via the Internet Archive 2025-06-15, `hr/law/zlp_zakonhr_wb20250615.txt`); original NN 115/2016 (`hr/law/nn2016_115_2524_zlp.txt`)", "B",
                "Zakon o lokalnim porezima, pročišćeni tekst (NN 115/16 to 152/24), zakon.hr via the Internet Archive 2025-06-15 (`hr/law/zlp_zakonhr_wb20250615.txt`); NN 115/2016 (`hr/law/nn2016_115_2524_zlp.txt`)",
                ["čl. 11 st. 1: owners of passenger cars, motorcycles and quadricycles pay the tax once a year, on registration or extension of the registration",
                 "čl. 11 st. 3 t. 1 (cars, EUR): up to 55 kW 40 / 33 / 27; 55-70 kW 53 / 46 / 33; 70-100 kW 80 / 66 / 53; 100-130 kW 119 / 93 / 80; above 130 kW 199 / 159 / 133, for up to 2, 2 to 5 and 5 to 10 years of age; the table has no row for older vehicles",
                 "čl. 12 st. 3: a vehicle acquired during the year and not registered before pays the annual tax less the part of the year before the purchase (the model prorates by months held)",
                 "grade B: the euro amounts (NN 114/22) are read in an unofficial consolidated text; the 2016 Narodne novine text (kuna) agrees in structure"],
                [("!g.vehicles.isEmpty", "5200 porez na cestovna motorna vozila: the age is read in calendar years since first registration (2 / 5 / 10-year boundaries fall in the lower column)")],
                g, "quadricycles, vehicles other than cars and motorcycles")


# ---------------------------------------------------------------- driver
def p11_rows(S):
    for f in (_veh11, _veh11b, _veh11c, _veh11d, _veh11e, _veh11f, _veh11g):
        f(S)
