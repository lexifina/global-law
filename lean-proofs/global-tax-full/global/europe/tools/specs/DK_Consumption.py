S = {'cc': 'DK', 'fam': 'Consumption', 'family_name': '5111 Merværdiafgift (moms)', 'doc': '# DK 2025: Merværdiafgift (moms) (5111); excises not modelled in this pass\n\nSource: Bekendtgørelse af lov om merværdiafgift (momsloven), LBK nr 209 af 27/02/2024, retsinformation.dk ELI XML (official; status Valid through 2025), `dk/law/momsl_lbk2024_209.xml`; sha256 in `law/SHA256SUMS`.\n* § 33: "Afgiften udgør 25 pct. af afgiftsgrundlaget."\n* § 48, stk. 1: registration not required "når de samlede afgiftspligtige leverancer ikke overstiger 50.000 kr. årligt"\n', 'vat': {'name': 'Merværdiafgift (moms)', 'standard': 2500, 'threshold': 50000, 'statute': 'Momsloven (LBK nr 209 af 27/02/2024) § 33 (25 pct.); § 13 (fritagelser); § 48, stk. 1 (50.000 kr.)', 'classes': {'health': 'exempt', 'education': 'exempt', 'financial': 'exempt', 'insurance': 'exempt', 'rent': 'exempt'}}, 'notes': ['DK 5111: LBK nr 209 af 27/02/2024 (in force 2024-03-04, Valid at fetch)'], 'unsupported': [('g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance)', "exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"), ('g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)', 'excise (Mineralolieafgiftsloven, tobaksafgiftsloven, øl- og vinafgiftsloven, spiritusafgiftsloven) not modelled in this pass')], 'guards': ['vat.embedded { good := .clothing, amount := 12500 } == 2500', 'vat.net { turnover := 50000, sales := [{ good := .other, net := 50000 }] } == 0'], 'taxes': [{'oecd': '5111', 'tax': 'Merværdiafgift (moms)', 'statute': 'Momsloven (LBK nr 209 af 27/02/2024) § 33 (25 pct.); § 13 (fritagelser); § 48, stk. 1 (50.000 kr.)', 'dated': 'LBK nr 209 af 27/02/2024 (in force 2024-03-04, Valid at fetch)', 'grade': 'A', 'kernel_parts': ['Vat'], 'unsupported': ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"]}, {'oecd': '5121', 'tax': 'Excise duties', 'statute': 'Mineralolieafgiftsloven, tobaksafgiftsloven, øl- og vinafgiftsloven, spiritusafgiftsloven', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'unsupported': ["not read in the P1 pass: would unlock with the act's 2025 rate articles"]}]}


# ---- FT review (2026-11-21, third pass): passenger transport exempt (ftd_ec_tedb_vat_2025 dev; IMPROVE_FT D3-7) ----
S["doc"] += """
## FT review (2026-11-21, third pass): passenger transport
Same LBK nr 209 af 27/02/2024 (`dk/law/momsl_lbk2024_209.txt`). **§ 13, stk. 1**: "Følgende varer og ydelser er
fritaget for afgift: ... 15) Personbefordring. Fritagelsen omfatter dog ikke anden erhvervsmæssig passagerkørsel med bus
end rutekørsel." The household's `transport` is read as exempt passenger transport (non-scheduled commercial bus
excepted, listed).
"""
S["vat"]["classes"]["transport"] = "exempt"
S["unsupported"] = S["unsupported"] + [("g.consumption.any (fun s => s.good == .transport)", "transport exempt (§ 13, stk. 1, nr. 15); non-scheduled commercial bus travel is taxable at 25 % (not separated)")]
S["guards"] = S["guards"] + ["vat.embedded { good := .transport, amount := 125 } == 0"]

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
