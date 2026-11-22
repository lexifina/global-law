S = {'cc': 'CO', 'fam': 'Transfers', 'doc': '# CO 2025: Transfers family: Bogotá predial (4100); registro and timbre grade C\n\nSources: Acuerdo 648 de 2016 art. 1 (Régimen Legal de Bogotá consolidation, Wayback 20250515): the impuesto predial unificado tariffs depend on the avalúo catastral; "A partir del año 2017, los rangos del avalúo catastral que determinan la tarifa ... se ajustarán cada año en el porcentaje correspondiente a la variación anual a junio del Índice Precios de Vivienda Nueva (IPVN)". Acuerdo 780 de 2020 art. 3 replaced the residential urban tariffs (5.5 to 12.3 per mil); par. 2 keeps the 1 and 3 per mil for estratos 1-3 up to 135 SMLMV. **Resolución SDH-000301 de 2024** (26 Dec 2024, in force 1 Jan 2025) art. 1 fixes the 2025 ranges (IPVN 10.91 %): to $176,611,000 5.5 per mil, ..., above $2,276,985,001 12.3 per mil; the rate of the range applies to the whole avalúo. Model: each real-estate asset as residential urban property in Bogotá at its statutory value; stratum, non-residential use and the thousand rounding not applied (flagged). Registro/timbre stay C.', 'families': '[predialF]', 'taxes': [{'oecd': '4100', 'tax': 'Impuesto predial unificado (Bogotá, residential urban)', 'statute': "Acuerdo Distrital 648 de 2016 art. 1 (tarifas por rangos de avalúo catastral; rangos ajustados cada año por el IPVN) with the residential urban tariffs of Acuerdo 780 de 2020 art. 3; Resolución SDH-000301 de 2024 art. 1: 2025 ranges, 5.5 per mil up to $176,611,000 ... 12.3 per mil above $2,276,985,001, the range's rate on the whole avalúo", 'dated': 'Régimen Legal de Bogotá (Secretaría Jurídica Distrital): Acuerdo 648 de 2016 consolidated (Wayback 20250515, archived co/law/sisjur_acuerdo648_2016_wb20250515.*); Acuerdo 780 de 2020 (bogota.gov.co PDF, co/law/acuerdo780_2020_bogota.*); Resolución SDH-000301 de 26 Dec 2024, in force 1 Jan 2025 (sisjur Norma1.jsp?i=172560, co/law/sisjur_res_sdh301_2024.*); pass 9, 2026-11-21', 'grade': 'A', 'status': 'modelled', 'package': 'P5', 'kernel_parts': ['charge'], 'unsupported': ['estratos 1-3 preferential tariffs not applied (stratum not an input)', 'non-residential tariffs', 'all real estate taken as residential urban in Bogotá', 'rounding to the thousand']}, {'oecd': '4400', 'tax': 'Impuesto de registro and stamp duties on real-estate transfers', 'statute': 'Ley 223 de 1995 (registro); Ley 2277 de 2022 (timbre on real estate)', 'grade': 'C', 'status': 'unsupported', 'package': 'P5', 'kernel_parts': [], 'tried': 'not read in pass 9 (Bogotá predial done first)', 'unsupported': ['would unlock: the departmental registro ordinance for Cundinamarca/Bogotá and Ley 223 arts. 226-236']}], 'unsupported': [['g.assets.any (·.kind.isRealEstate)', 'Bogotá predial on each real-estate asset at its statutory value (the avalúo catastral where `assessed` is given, else market value), every property taken as residential urban in Bogotá; the preferential 1 and 3 per mil of estratos 1-3 up to 135 SMLMV and the estrato 1-2 floor of 16 SMLMV not applied (stratum not an input: upper bound for them); non-residential tariffs not applied; rounding to the thousand not applied'], ['!g.purchases.isEmpty', 'impuesto de registro (Ley 223/1995) and departmental/district stamp on real-estate transfers not computed (grade C)']], 'lean': '/-- Res. SDH-000301 de 2024 art. 1 (año gravable 2025): the per-mil rate of the avalúo\'s range, in bp (5.5 per mil = 55 bp). -/\ndef predialBp (v : Int) : Int :=\n  if v ≤ 176611000 then 55 else if v ≤ 188204000 then 56 else if v ≤ 216665000 then 57 else if v ≤ 245128000 then 58 else if v ≤ 273591000 then 59 else if v ≤ 302052000 then 60 else if v ≤ 330514000 then 61 else if v ≤ 358977000 then 62 else if v ≤ 406413000 then 63 else if v ≤ 453854000 then 64 else if v ≤ 501289000 then 65 else if v ≤ 548727000 then 66 else if v ≤ 596163000 then 68 else if v ≤ 643601000 then 70 else if v ≤ 691037000 then 72 else if v ≤ 738475000 then 74 else if v ≤ 785912000 then 76 else if v ≤ 852324000 then 78 else if v ≤ 918737000 then 80 else if v ≤ 985147000 then 82 else if v ≤ 1051562000 then 84 else if v ≤ 1117971000 then 86 else if v ≤ 1184383000 then 88 else if v ≤ 1250796000 then 90 else if v ≤ 1317208000 then 92 else if v ≤ 1554392000 then 95 else if v ≤ 1791582000 then 101 else if v ≤ 2028768000 then 108 else if v ≤ 2276985000 then 115 else 123\n\n/-- Impuesto predial unificado: the range\'s rate on the whole avalúo (whole pesos, down). -/\ndef predial (v : Int) : Int := divR .down (predialBp (pos v) * pos v) BP\n\ndef predialF : Family :=\n  { name := "4100 impuesto predial unificado (Bogotá)", covers := [.propertyRecurrent],\n    run := fun _ g _ =>\n      (g.assets.zipIdx.filter fun (a, _) => a.kind.isRealEstate).map fun (a, i) =>\n        charge .propertyRecurrent "Impuesto predial unificado (Bogotá, residencial urbano)" a.statutoryValue (fun _ => pos a.statutoryValue)\n          (fun _ => predial a.statutoryValue) (event := s!"asset {i + 1}") (level := .local)\n          (statute := "Acuerdo Distrital 648 de 2016 art. 1 (tarifas por rangos de avalúo catastral; rangos ajustados cada año por el IPVN) with the residential urban tariffs of Acuerdo 780 de 2020 art. 3; Resolución SDH-000301 de 2024 art. 1: 2025 ranges, 5.5 per mil up to $176,611,000 ... 12.3 per mil above $2,276,985,001, the range\'s rate on the whole avalúo") }', 'guards': ['predial 100000000 == 550000', 'predial 176611000 == 971360', 'predial 176611001 == 989021', 'predial 3000000000 == 36900000', 'predialBp 1000000000 == 84']}

# ---- pass 14 (builder 14, 2026-11-21): impuesto sobre vehículos automotores (Ley 488 de 1998), new vehicles by the month ----
# Ley 488/1998 (DIAN normograma, Wayback 2025-07-09: co/law/ley_0488_1998_normograma_wb20250709.*): art. 141 (taxed: new and
# used vehicles; not: motorcycles up to 125 cc (a), public passenger and goods transport (e)); art. 143 (base: the Ministry of
# Transport's commercial value; first entry into circulation: the invoice total); art. 144 (accrues 1 January; new vehicles
# on the request for registration = the invoice date); art. 145 with the 2025 values of Decreto 1493 de 2024 art. 1: private
# vehicles up to $55.679.000 1,5 %, to $125.274.000 2,5 %, above 3,5 % (whole value at the bracket's rate); motorcycles over
# 125 cc 1,5 %; par. 2: first entry into circulation: in proportion to the months left in the year, a fraction of a month
# counted as a whole month; par. 5 (Ley 1964/2019) electric and par. 6 (Ley 2128/2021) gas-dedicated: at most 1 %.
# Bogotá: Acuerdo 780 de 2020 art. 25 discounts for new electric (60 %) and hybrid (40 %) vehicles registered in Bogotá
# ("for the 5 years following" registration): the years covered and later amendments not read -> electric and hybrid
# vehicles are not computed (grade C, listed as unmatched).
S["imports"] = ["TaxKernel.Global2"]
S["lean"] = S["lean"] + '''

/-- Ley 488/1998 art. 145 (2025 values, Decreto 1493 de 2024 art. 1): a whole-value rate by bracket, on the commercial value
(art. 143; for a vehicle first entering circulation, the invoice total). -/
def vehRule (nm : String) (kinds : List String) (fuels : List VehicleFuel) (w : List (VehicleAttr × Int × Int)) (rateBp : Int)
    (st : String) : VehicleTax :=
  { name := nm, kinds := kinds, fuels := fuels, «when» := w, parts := [(.value, QtyTable.perUnit rateBp 10000)], regTo := 2024,
    level := .local, statute := st }

def vehPriv : List String := ["car", "stationWagon", "van", "suv", "pickup", "pickupSingleCab", "truck"]
def vehComb : List VehicleFuel := [.petrol, .diesel, .other]
def vehSt : String := "Ley 488 de 1998 art. 145 (2025 values: Decreto 1493 de 2024 art. 1)"

/-- (rule for vehicles first registered up to 2024, its rate in bp) -/
def vehBase : List (VehicleTax × Int) :=
  [(vehRule "Impuesto sobre vehículos automotores (private, to $55.679.000)" vehPriv vehComb [(.value, -1, 55679000)] 150 (vehSt ++ " 1 a): 1,5 %"), 150),
   (vehRule "Impuesto sobre vehículos automotores (private, to $125.274.000)" vehPriv vehComb [(.value, 55679000, 125274000)] 250 (vehSt ++ " 1 b): 2,5 %"), 250),
   (vehRule "Impuesto sobre vehículos automotores (private, above $125.274.000)" vehPriv vehComb [(.value, 125274000, -1)] 350 (vehSt ++ " 1 c): 3,5 %"), 350),
   (vehRule "Impuesto sobre vehículos automotores (gas-dedicated, at most 1 %)" vehPriv [.lpg, .cng] [] 100 (vehSt ++ " and par. 6 (Ley 2128 de 2021 art. 17): at most 1 % (every bracket's rate is higher)"), 100),
   (vehRule "Impuesto sobre vehículos automotores (motorcycle over 125 cc)" ["motorcycle"] vehComb [(.engineCcm, 125, -1)] 150 (vehSt ++ " 2: motorcycles over 125 cc, 1,5 %"), 150),
   (vehRule "Impuesto sobre vehículos automotores (motorcycle up to 125 cc: not taxed)" ["motorcycle"] vehComb [(.engineCcm, -1, 125)] 0 "Ley 488 de 1998 art. 141 a): motorcycles up to 125 cc not taxed", 0)]

/-- art. 145 par. 2 and art. 144: a vehicle first entering circulation in month k + 1 of 2025 pays (12 - k) / 12 of the year. -/
def vehNew (tr : VehicleTax × Int) : List VehicleTax := (List.range 12).map fun (k : Nat) =>
  { tr.1 with
      name := s!"{tr.1.name} (first in circulation in month {k + 1} of 2025)", regTo := 0, occasion := .registration,
      proRata := false, «when» := tr.1.when ++ [(.firstRegMonth, (k : Int), (k : Int) + 1)],
      parts := [(.value, QtyTable.perUnit (tr.2 * (12 - (k : Int))) 120000)],
      statute := tr.1.statute ++ s!"; art. 145 par. 2, art. 143, 144: first entry into circulation, {12 - k}/12 of the year on the invoice total" }

def vehTs : List VehicleTax := vehBase.map (·.1) ++ vehBase.flatMap vehNew

def vehF : Family := vehicleTaxFamily "impuesto sobre vehículos automotores" vehTs
'''
S["families"] = "[predialF, vehF]"
_us = S.pop("unsupported")
import json as _json
S["unsupported_expr"] = " ++ ".join("(if %s then [%s] else [])" % (c, _json.dumps(t, ensure_ascii=False)) for c, t in _us) \
  + " ++ (if !g.vehicles.isEmpty then [\"impuesto sobre vehículos automotores: every vehicle taken as registered in Bogotá D.C. and in private use (public transport exempt, art. 141 e); value taken as the Ministry of Transport's commercial value (for a 2025 first registration: the invoice total); the pronto-pago discount not applied; electric and hybrid vehicles not computed (Bogotá Acuerdo 780 de 2020 art. 25 discounts: years covered and later amendments not read; grade C)\"] else [])" \
  + " ++ vehicleTaxUnknown \"impuesto sobre vehículos automotores\" vehTs g ++ vehicleTaxUnmatched \"impuesto sobre vehículos automotores\" vehTs g"
S["guards"] += [
    "-- car first registered 2020, commercial value 50.000.000: 1,5 % = 750.000; 100.000.000: 2,5 % = 2.500.000; 200.000.000: 3,5 % = 7.000.000",
    "((vehBase.getD 0 (default, 0)).1).amount 2025 { value := 50000000, fuel := .petrol, firstRegYear := 2020 } == 750000",
    "((vehBase.getD 1 (default, 0)).1).amount 2025 { value := 100000000, fuel := .petrol, firstRegYear := 2020 } == 2500000",
    "((vehBase.getD 2 (default, 0)).1).amount 2025 { value := 200000000, fuel := .diesel, firstRegYear := 2020 } == 7000000",
    "(vehTs.filter (·.computes 2025 { value := 100000000, fuel := .petrol, firstRegYear := 2020 })).length == 1",
    "-- new car first in circulation in April 2025, invoice 80.000.000: 2,5 % = 2.000.000; x 9/12 = 1.500.000",
    "((vehNew (vehBase.getD 1 (default, 0))).getD 3 default).amount 2025 { value := 80000000, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 4, newReg := true } == 1500000",
    "-- December, 50.000.000: 750.000 x 1/12 = 62.500",
    "((vehNew (vehBase.getD 0 (default, 0))).getD 11 default).amount 2025 { value := 50000000, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 12, newReg := true } == 62500",
    "(vehTs.filter (·.computes 2025 { value := 80000000, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 4, newReg := true })).length == 1",
    "(vehTs.filter (·.computes 2025 { value := 80000000, fuel := .petrol, firstRegYear := 2025, newReg := true })).isEmpty",
    "-- motorcycle 150 cc, 10.000.000: 150.000; 110 cc: 0",
    "((vehBase.getD 4 (default, 0)).1).amount 2025 { kind := \"motorcycle\", engineCcm := 150, value := 10000000, fuel := .petrol, firstRegYear := 2022 } == 150000",
    "(vehTs.filter (·.computes 2025 { kind := \"motorcycle\", engineCcm := 110, value := 10000000, fuel := .petrol, firstRegYear := 2022 })).map (·.amount 2025 { kind := \"motorcycle\", engineCcm := 110, value := 10000000, fuel := .petrol, firstRegYear := 2022 }) == [0]",
    "(vehTs.filter (·.selects 2025 { value := 100000000, fuel := .electric, firstRegYear := 2020 })).isEmpty"]
S["taxes"].append({"oecd": "5200", "tax": "Impuesto sobre vehículos automotores (Bogotá D.C.; Ley 488 de 1998)",
  "statute": "Ley 488 de 1998 arts. 141, 143, 144, 145 (2025 values: Decreto 1493 de 2024 art. 1: to $55.679.000 1,5 %, to $125.274.000 2,5 %, above 3,5 %; motorcycles over 125 cc 1,5 %), par. 2 (first entry into circulation: months left), par. 6 (gas: at most 1 %)",
  "dated": "DIAN normograma Ley 488/1998, Wayback 2025-07-09 (values in force from 1 Jan 2025), co/law/ley_0488_1998_normograma_wb20250709.*; pass 14, 2026-11-21",
  "grade": "A", "status": "modelled", "package": "P1", "kernel_parts": ["VehicleTax", "vehicleTaxFamily", "firstRegMonth"],
  "unsupported": ["electric and hybrid vehicles not computed (Bogotá Acuerdo 780/2020 art. 25 discounts)", "every vehicle taken as private and registered in Bogotá", "value taken as the Ministry's commercial value", "pronto-pago discount not applied"]})
S["doc"] += "\n\n**Pass 14 (kernel 2.6.0): impuesto sobre vehículos automotores (Bogotá).** Ley 488 de 1998 (DIAN normograma; the Wayback copy of 9 July 2025 gives art. 145 with the 2025 values of Decreto 1493 de 2024): private vehicles 1,5 % of the commercial value up to $55.679.000, 2,5 % up to $125.274.000, 3,5 % above (the whole value at its bracket's rate); motorcycles over 125 cc 1,5 %, up to 125 cc not taxed (art. 141 a); gas-dedicated vehicles at most 1 % (par. 6). A vehicle first entering circulation in 2025 pays on its invoice total (art. 143) the share of the months left, its month counted whole (art. 145 par. 2, art. 144): one rule per month on `firstRegMonth`. Electric and hybrid vehicles are not computed: Bogotá's Acuerdo 780 de 2020 art. 25 discounts (60 % / 40 %) were read only in the 2020 text.\n"
