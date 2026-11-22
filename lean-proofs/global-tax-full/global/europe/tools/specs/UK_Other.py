S = {'cc': 'UK', 'fam': 'Other', 'families': [], 'doc': "# UK 2025: Other family not reached (grade C)\n\n* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)\n* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025\n", 'notes': [], 'unsupported': [('true', '5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)'), ('true', '6000 Other taxes: not modelled (grade C: registry row: no other notable tax; no provision read)')], 'guards': [], 'taxes': [{'oecd': '5200', 'tax': 'Taxes on use of goods (motor vehicle taxes)', 'statute': "the country's motor-vehicle tax act", 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P7 pass', 'unsupported': ['would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)']}, {'oecd': '6000', 'tax': 'Other taxes', 'statute': 'none recorded by the registry', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'registry row: no other notable tax; no provision read', 'unsupported': ["would unlock: a statement in the statute or the tax authority's list of taxes for 2025"]}]}

# ---- pass 7 (R1 Europe, 2026-11-21): P5/P6 gaps, carry-overs (tools/p6lib.py helpers, tools/p7_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p7_rows.py")).read())
p7_rows(S)
p6_finish(S)

# ---- pass 9 (R1 Europe, 2026-11-21): remaining withholding, carry-overs, B -> A, P5/P6 (tools/p9_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
p9_rows(S)
p6_finish(S)

# ---- FT review, sixth pass (FT reviewer 6, 2026-11-21): VED para. 1GE on the list price (Dataset round 4, R4-1) ----
# VERA 1994 Sch. 1 para. 1GE (1) (a) "the price of the vehicle exceeds £40,000"; para. 1GF (1) (a): the price is the list
# price (+ non-standard accessories), (b) the notional price where there is none (uk/law/vera1994_sch1_20250601.txt
# l. 461-487). Kernel 2.5.0 `.listPrice` (never `value`). 1GD £195 for a car first registered from 2020 only where the list
# price is £40,000 or less, or where 1GE (1) (c) (ii) excludes it (CO2 0 g, registered before 1 April 2025); a car of 2020
# or later without a list price is now grade C (vehicleTaxUnknown), not £195.
_ft6_new = '''{ name := "Vehicle excise duty", kinds := ["car"], regFrom := 2020, fixed := 620, when := [(.listPrice, 40000, VehicleTax.noBound), (.co2GKm, 0, VehicleTax.noBound)], statute := "VERA 1994 Sch. 1 para. 1GE (1) (a)-(c), (2): £620 where the price (para. 1GF (1): the list price) exceeds £40,000 and the car is under six years old" },
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2017, regTo := 2019, fixed := 195, statute := "VERA 1994 Sch. 1 para. 1GD (1): £195" },
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2020, fixed := 195, when := [(.listPrice, -1, 40000)], statute := "VERA 1994 Sch. 1 para. 1GD (1): £195 (list price £40,000 or less, para. 1GE (1) (a), 1GF)" },
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2020, regTo := 2024, fixed := 195, when := [(.co2GKm, -1, 0)], statute := "VERA 1994 Sch. 1 para. 1GD (1): £195 (CO2 0 g/km, registered before 1 April 2025: para. 1GE (1) (c) (ii) excludes 1GE)" },'''
_a = S["lean"].index('{ name := "Vehicle excise duty", kinds := ["car"], regFrom := 2020, fixed := 620')
_b = S["lean"].index('para. 1GD (1): £195" },', _a) + len('para. 1GD (1): £195" },')
S["lean"] = S["lean"][:_a] + _ft6_new + S["lean"][_b:]
S["unsupported"] = [(c, t) for (c, t) in S["unsupported"] if "the vehicle's value is taken as its list price" not in t and "has no price: the £40,000 supplement" not in t]
S["unsupported"] += [("g.vehicles.any (fun v => v.firstRegYear ≥ 2020)", "5200 Vehicle excise duty: the £40,000 supplement (para. 1GE) is tested on the list price (para. 1GF; non-standard accessories not added) for cars first registered from 2020 (six years read by calendar year)")]
S["guards"] += ['(p9ukVed[1]!).amount 2025 { kind := "car", co2GKm := 120, fuel := .diesel, firstRegYear := 2022, value := 30842, listPrice := 50221 } == 620',
                '(p9ukVed[3]!).amount 2025 { kind := "car", co2GKm := 120, fuel := .petrol, firstRegYear := 2022, value := 45000, listPrice := 39000 } == 195',
                '(p9ukVed[1]!).computes 2025 { kind := "car", co2GKm := 120, fuel := .petrol, firstRegYear := 2022, value := 45000 } == false',
                '(p9ukVed[3]!).computes 2025 { kind := "car", co2GKm := 120, fuel := .petrol, firstRegYear := 2022, value := 45000 } == false']
S["doc"] += "\n* FT review (sixth pass): para. 1GE (1) (a) tests the price, para. 1GF (1) the list price (kernel `.listPrice`), not the vehicle's value; without a list price a car first registered from 2020 is grade C.\n"
for t in S["taxes"]:
    if str(t.get("oecd")) == "5200" and t.get("tax") == "Vehicle excise duty":
        t["statute"] = "Vehicle Excise and Registration Act 1994 Sch. 1 paras. 1B, 1GC, 1GD, 1GE, 1GF (price = list price)"
        t["unsupported"] = [u for u in t.get("unsupported", []) if "value is taken as its list price" not in u and "has no price" not in u] + ["a car first registered from 2020 without a list price (para. 1GF): grade C"]
p6_finish(S)

# ---- FT review, seventh pass (FT reviewer 7, 2026-11-21): cars first registered before March 2001 (Dataset round 4, R4-2) ----
# VERA 1994 Sch. 1 para. 1 (1): a vehicle with no other annual rate in the Schedule pays the general rate; (2) "Except in the
# case of an electrically propelled, or zero-emission, vehicle or a vehicle having an engine with a cylinder capacity not
# exceeding 1,549 cubic centimetres, the general rate is £360"; (2A) for those "the general rate is £220" (sums substituted by
# FA 2025 s. 66 (2) for licences taken out on or after 1.4.2025; uk/law/vera1994_sch1_20250601.txt l. 111-113). Para. 1B
# reaches only cars first registered on or after 1 March 2001, so a car first registered earlier pays para. 1 (the model's
# calendar-year boundary: 2001 and later stay under 1B). Cars first registered before 1985 are left unmatched (historic
# vehicles, VERA Sch. 2 para. 1A, not held).
_ft7_rows = '''
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 1985, regTo := 2000, fuels := [.electric], fixed := 220, statute := "VERA 1994 Sch. 1 para. 1 (2A): general rate £220, electrically propelled vehicle (first registered before 1 March 2001)" },
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 1985, regTo := 2000, fixed := 220, when := [(.engineCcm, -1, 1549)], statute := "VERA 1994 Sch. 1 para. 1 (2A): general rate £220, cylinder capacity not exceeding 1,549 cc (first registered before 1 March 2001)" },
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 1985, regTo := 2000, fixed := 360, when := [(.engineCcm, 1549, VehicleTax.noBound)], statute := "VERA 1994 Sch. 1 para. 1 (2): general rate £360 (first registered before 1 March 2001)" }]'''
_a = S["lean"].index('def p9ukVed : List VehicleTax :=')
_b = S["lean"].index('statute := "VERA 1994 Sch. 1 para. 1B" }]', _a) + len('statute := "VERA 1994 Sch. 1 para. 1B" }')
assert S["lean"][_b] == ']'
S["lean"] = S["lean"][:_b] + ',' + _ft7_rows + S["lean"][_b + 1:]
S["unsupported"] = [(c, t.replace("cars first registered before March 2001 (engine-size rates, para. 1), ", "cars first registered before 1985 (historic vehicles, Sch. 2 para. 1A, not held), ")) for (c, t) in S["unsupported"]]
S["unsupported"] += [("g.vehicles.any (fun v => v.firstRegYear ≥ 1985 && v.firstRegYear ≤ 2000)", "5200 Vehicle excise duty: a car first registered 1985-2000 pays the para. 1 general rate (£220 / £360 by cylinder capacity, licences from 1.4.2025); one constructed before 1985 would be a historic vehicle (Sch. 2 para. 1A, not held)")]
S["guards"] += ['(p9ukVed[7]!).amount 2025 { kind := "car", fuel := .electric, firstRegYear := 1998 } == 220',
                '(p9ukVed[8]!).amount 2025 { kind := "car", engineCcm := 1549, fuel := .petrol, firstRegYear := 1999 } == 220',
                '(p9ukVed[9]!).amount 2025 { kind := "car", engineCcm := 1550, fuel := .diesel, firstRegYear := 1999 } == 360',
                '(p9ukVed[9]!).computes 2025 { kind := "car", engineCcm := 1550, fuel := .diesel, firstRegYear := 2001 } == false',
                '(p9ukVed[8]!).computes 2025 { kind := "car", fuel := .petrol, firstRegYear := 1999 } == false',
                '(p9ukVed[8]!).computes 2025 { kind := "car", engineCcm := 1200, fuel := .petrol, firstRegYear := 1984 } == false']
S["doc"] += "\n* FT review (seventh pass): cars first registered before March 2001 (1985-2000 by calendar year) pay the para. 1 general rate: £220 up to 1,549 cc or electrically propelled (para. 1 (2A)), £360 otherwise (para. 1 (2)); before 1985: grade C (historic vehicles).\n"
for t in S["taxes"]:
    if str(t.get("oecd")) == "5200" and t.get("tax") == "Vehicle excise duty":
        t["statute"] = "Vehicle Excise and Registration Act 1994 Sch. 1 paras. 1, 1B, 1GC, 1GD, 1GE, 1GF (price = list price)"
        t["unsupported"] = [u.replace("cars first registered before March 2001 (engine-size rates, para. 1), ", "cars first registered before 1985 (historic vehicles), ") for u in t.get("unsupported", [])]
p6_finish(S)

# ---- pass 15 (R1 Europe, 2026-11-21): publication requests, ENFIA, vehicles, transfers, withholding notes (tools/p15_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
p15_rows(S)
p6_finish(S)

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
