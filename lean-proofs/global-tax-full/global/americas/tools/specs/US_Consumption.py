S = dict(cc="US", fam="Consumption",
doc=r'''# United States 2025 (California, City of Los Angeles): sales tax (5112), federal and California excises (5121)

Sources (`us/law/`): 26 U.S.C. §§ 4081, 5001, 5041, 5051, 5701 (Cornell LII, current US Code; the rates quoted are
unchanged since 2018 or earlier per each section's amendment notes); CDTFA "California City & County Sales & Use Tax
Rates (effective July 1, 2025)" (archived 2025-07-03) and CDTFA "Tax Rates - Special Taxes and Fees" (archived
2024-07-17), official secondary sources for the state rates (grade B).
* **No federal VAT or general sales tax**: Subtitle D of the Internal Revenue Code levies only specific excises.
* **Sales tax, City of Los Angeles 9.750 %** (CDTFA table: state, county, city and district parts together). Food for
  home consumption, prescription medicines, utilities and services are outside or exempt (R&TC §§ 6359, 6369, 6353:
  not read; categories from the structure of the tax on tangible personal property, flagged).
* **Federal**: § 4081 (a) (2) (A) gasoline "18.3 cents per gallon", diesel "24.3 cents per gallon", (B) + 0.1 cent
  (LUST); § 5701 (b) (1) cigarettes "$50.33 per thousand"; § 5001 (a) (1) "$13.50 on each proof gallon" (a proof gallon
  is half a gallon of pure alcohol); § 5041 (b) (1) still wine up to 16 % "$1.07 per wine gallon"; § 5051 (a) (1) beer
  "$18 on any barrels … to which clause (i) does not apply" ($16 on a brewer's first 6 million barrels: flagged).
* **California** (CDTFA): motor vehicle fuel $0.596 per gallon from July 1, 2024, diesel $0.454 (the July 1, 2025
  adjustment is after the capture: the first half of 2025, flagged); cigarettes "$0.1435/cigarette ($2.87/pack of
  20s)"; beer and wine $0.20, distilled spirits (100 proof or less) $3.30 per wine gallon.
* One US gallon = 3.785411784 litres; a barrel = 31 gallons.''',
vat=dict(name="Sales tax (Los Angeles)", standard=975, statute="CDTFA rate table eff. 2025-07-01: City of Los Angeles 9.750 %", oecd="5112", level="state", family="5112 California sales and use tax",
  classes={"food":"exempt","medicines":"exempt","health":"exempt","education":"exempt","transport":"exempt","financial":"exempt","insurance":"exempt",
           "rent":"exempt","water":"exempt","electricity":"exempt","gas":"exempt","communication":"exempt","newspapers":"exempt","hotels":"exempt","heatingOil":"exempt"}),
lean=r'''
/-- litres per US gallon × 10^9 -/
def galL : Int := 3785411784

def federal : List ExLine :=
  [{ good := .petrol, name := "Federal excise (gasoline)", num := 184000000, den := galL, statute := "26 U.S.C. § 4081 (a) (2) (A) (i), (B): 18.3 + 0.1 cents per gallon" },
   { good := .diesel, name := "Federal excise (diesel)", num := 244000000, den := galL, statute := "26 U.S.C. § 4081 (a) (2) (A) (iii), (B): 24.3 + 0.1 cents per gallon" },
   { good := .cigarettes, name := "Federal excise (cigarettes)", num := 5033, den := 100000, statute := "26 U.S.C. § 5701 (b) (1): $50.33 per thousand" },
   { good := .spirits, name := "Federal excise (distilled spirits)", num := 1350000000, den := galL / 2, pure := true, statute := "26 U.S.C. § 5001 (a) (1): $13.50 per proof gallon" },
   { good := .wine, name := "Federal excise (wine)", num := 1070000000, den := galL, statute := "26 U.S.C. § 5041 (b) (1): $1.07 per wine gallon (up to 16 %)" },
   { good := .beer, name := "Federal excise (beer)", num := 18000000000, den := 31 * galL, statute := "26 U.S.C. § 5051 (a) (1) (A) (ii): $18 per barrel" }]

def california : List ExLine :=
  [{ good := .petrol, name := "California motor vehicle fuel tax", num := 596000000, den := galL, statute := "CDTFA: $0.596 per gallon from July 1, 2024" },
   { good := .diesel, name := "California diesel fuel tax", num := 454000000, den := galL, statute := "CDTFA: $0.454 per gallon from July 1, 2024" },
   { good := .cigarettes, name := "California cigarette tax", num := 1435, den := 10000, statute := "CDTFA: $0.1435 per cigarette" },
   { good := .spirits, name := "California alcoholic beverage tax (spirits)", num := 3300000000, den := galL, statute := "CDTFA: $3.30 per wine gallon (100 proof or less)" },
   { good := .wine, name := "California alcoholic beverage tax (wine)", num := 200000000, den := galL, statute := "CDTFA: $0.20 per wine gallon" },
   { good := .beer, name := "California alcoholic beverage tax (beer)", num := 200000000, den := galL, statute := "CDTFA: $0.20 per wine gallon" }]

def exciseF : Family :=
  { name := "5121 federal and California excises", covers := [.excise],
    run := fun _ g _ => exciseCharges federal g.consumption
      ++ (exciseCharges california g.consumption).map fun c => { c with level := .state } }
''',
families="[vatF, exciseF]",
absent=[["vat", "no federal value added or general sales tax: 26 U.S.C. Subtitle D (miscellaneous excise taxes) levies only specific excises; general sales taxes are state and local (5112)"]],
unsupported=[["g.consumption.any fun s => s.good == .petrol || s.good == .diesel", "California fuel: the July 1, 2025 adjustment is not in the capture (2024-25 rate used); the sales tax on fuel (partial exemption R&TC 6357.7, diesel rate) is taken at the general rate"],
 ["g.consumption.any fun s => s.good == .tobaccoOther", "federal and California tax on other tobacco products not modelled"],
 ["g.consumption.any (·.good == .beer)", "federal beer: $18 per barrel taken; the first 6 million barrels of each brewer pay $16 (5051 (a) (1) (A) (i))"],
 ["!g.consumption.isEmpty", "sales tax categories (food, medicines, utilities, services exempt or outside) from the structure of the tax, not from R&TC 6353-6369 read; hotels' transient occupancy tax (city) not modelled"],
 ["g.entity == .company", "a company's sales and use tax on its retail sales is modelled as the basket rule on its supplies"]],
guards=["vat.embedded { good := .clothing, amount := 10975 } == 975", "vat.embedded { good := .food, amount := 10975 } == 0",
        "-- 100 gallons of gasoline: federal 18.40 dollars, California 59.60",
        "(federal.head!).duty { good := .petrol, amount := 500, quantity := 378541 } == 18",
        "(california.head!).duty { good := .petrol, amount := 500, quantity := 378541 } == 59",
        "-- 1,000 cigarettes: federal 50.33, California 143.50",
        "(federal.find? (·.good == .cigarettes)).get!.duty { good := .cigarettes, amount := 900, quantity := 1000000 } == 50",
        "(california.find? (·.good == .cigarettes)).get!.duty { good := .cigarettes, amount := 900, quantity := 1000000 } == 143"],
taxes=[dict(oecd="5112", tax="California sales and use tax (City of Los Angeles)", statute="R&TC Part 1 (Sales and Use Tax Law), Bradley-Burns and district taxes; CDTFA rate table", dated="CDTFA table effective 2025-07-01 (archived 2025-07-03)", grade="B", package="P1", kernel_parts=["Vat"], unsupported=["exemption sections not read item by item"]),
 dict(oecd="5111", tax="VAT", statute="26 U.S.C. Subtitle D", grade="A", status="not levied", package="P1"),
 dict(oecd="5121", tax="Federal excises (fuel, tobacco, alcohol)", statute="26 U.S.C. 4081, 5001, 5041, 5051, 5701", dated="current US Code; rates unchanged in 2025", grade="A", package="P1", kernel_parts=["ExLine"], unsupported=["other tobacco", "small-producer rates"]),
 dict(oecd="5121", tax="California excises (fuel, cigarettes, alcohol)", statute="R&TC 7360, 60050, 30101 ff., 32151 ff. (via CDTFA)", dated="CDTFA special-tax table archived 2024-07-17 (rates from 2024-07-01)", grade="B", package="P1", kernel_parts=["ExLine"], unsupported=["July 2025 fuel adjustment"])])

# ---- gap pass 2026-11-21 (approach 1): customs import duties, OECD 5123, kernel 2.8.0 TariffRule ----
import json as _gj
S['imports'] = sorted(set((S.get('imports') or []) + ['TaxKernel.Global2']))
S['lean'] = (S.get('lean') or '') + '\n\n' + "/-! ## 5123 customs import duties (kernel 2.8.0 `TariffRule`; gap pass 2026-11-21) -/\n\ndef tariff : TariffRule :=\n  { name := \"customs duty\", country := \"US\", vatOf := some vat,\n    lines := [{ hs := \"0207.14\", perKgNum := 176, perKgDen := 1000, statute := \"0207.14.00 17.6 cents/kg\" },\n      { hs := \"1006.30.10\", adValoremBp := 1120, statute := \"1006.30.10 11.2 %\" },\n      { hs := \"1006.30.90\", perKgNum := 14, perKgDen := 1000, statute := \"1006.30.90 1.4 cents/kg\" },\n      { hs := \"2202.10\", perUnitNum := 2, perUnitDen := 1000, statute := \"2202.10.00 0.2 cents/liter\" },\n      { hs := \"2203.00\", statute := \"2203.00.00 Free\" },\n      { hs := \"2204.21.50\", perUnitNum := 63, perUnitDen := 1000, statute := \"2204.21.50 6.3 cents/liter\" },\n      { hs := \"2204.21.80\", perUnitNum := 169, perUnitDen := 1000, statute := \"2204.21.80 16.9 cents/liter\" },\n      { hs := \"2208.30\", statute := \"2208.30.30/.60 Free\" },\n      { hs := \"2402.20.80\", adValoremBp := 230, perKgNum := 105, perKgDen := 100, statute := \"2402.20.80 $1.05/kg + 2.3 %\" },\n      { hs := \"2402.20.90\", adValoremBp := 320, perKgNum := 150, perKgDen := 100, statute := \"2402.20.90 $1.50/kg + 3.2 %\" },\n      { hs := \"2710.12.15\", perUnitNum := 525, perUnitDen := 158987, statute := \"2710.12.15 52.5 cents/bbl (158.987 l)\" },\n      { hs := \"2710.19.11\", perUnitNum := 105, perUnitDen := 158987, statute := \"2710.19.11 10.5 cents/bbl (158.987 l)\" },\n      { hs := \"3004.90\", statute := \"3004.90.10/.92 Free\" },\n      { hs := \"4901.99\", statute := \"4901.99.00 Free\" },\n      { hs := \"6109.10\", adValoremBp := 1650, statute := \"6109.10.00 16.5 %\" },\n      { hs := \"8471.30\", statute := \"8471.30.01 Free\" },\n      { hs := \"8517.13\", statute := \"8517.13.00 Free\" },\n      { hs := \"8703.23\", adValoremBp := 250, statute := \"8703.23.01 2.5 %\" },\n      { hs := \"8703.80\", adValoremBp := 250, statute := \"8703.80.00 2.5 %\" }],\n    otherBp := -1,\n    preferences := [{ name := \"USMCA, CAFTA-DR and the bilateral FTAs (special program indicators S, P, AU, BH, CL, CO, IL, KR, MA, OM, PA, PE, SG)\", partners := [\"CA\", \"MX\", \"AU\", \"BH\", \"CL\", \"CO\", \"IL\", \"KR\", \"MA\", \"OM\", \"PA\", \"PE\", \"SG\", \"CR\", \"DO\", \"GT\", \"HN\", \"NI\", \"SV\"], statute := \"HTSUS column 1 Special: Free\" },\n      { name := \"US-Jordan FTA (JO)\", partners := [\"JO\"], hsExcept := [\"2204.21\", \"2402.20\"], statute := \"HTSUS column 1 Special: Free (JO)\" }],\n    mfnIfOriginUnknown := true,\n    statute := \"Harmonized Tariff Schedule of the United States (19 U.S.C. 1202), 2025 Basic Edition to Revision 32, column 1 General and Special\" }\n\ndef customsF : Family := customsFamily [tariff] \"5123 customs import duties (HTSUS)\"\n\n/-- Imported lines whose duty this model cannot settle (grade C lines; the MFN or preferential duty is still shown). -/\ndef customsFlags (g : CanonGlobal) : List String :=\n  (consumptionC g).zipIdx.flatMap fun ((s, x, c), i) =>\n    let hs := (hsNormalize c.hsRaw).getD \"\"\n    if !(x.imported || c.origin != \"\") || tariff.isDomestic c || !tariff.takesGood s.good then [] else\n    let o := if c.origin == \"\" then \"not given\" else c.origin\n    let pre := s!\"5120 customs duty: line {i + 1} ({s.good.name}), origin {o}, hs {hs}: \"\n    (if true then [pre ++ \"2025 additional duties under HTSUS Chapter 99 (IEEPA: EO 14195 China from 4 Feb 2025, EO 14193/14194 Canada and Mexico from 4 Mar 2025, EO 14257 reciprocal tariffs from 5 Apr 2025; s. 232 automobiles from 3 Apr 2025) depend on the entry date, the origin and the good, and are not computed (grade C)\"] else []) ++\n    (if [\"AG\", \"AW\", \"BS\", \"BB\", \"BZ\", \"VG\", \"CW\", \"DM\", \"GD\", \"GY\", \"HT\", \"JM\", \"MS\", \"KN\", \"LC\", \"VC\", \"TT\"].contains c.origin then [pre ++ \"a CBERA beneficiary (special indicator E/R) may enter some goods Free; not modelled, MFN booked (grade C)\"] else [])\n\ndef customsUnknown (g : CanonGlobal) : List String := tariff.unknown g ++ customsFlags g\n\n/-- A one-household line with the given consumption lines (for the guards). -/\ndef custLine (lines : String) : CanonGlobal :=\n  match Lean.Json.parse (\"{\\\"id\\\":\\\"h\\\",\\\"schema\\\":\\\"global/2.0\\\",\\\"household\\\":{\\\"id\\\":\\\"h\\\",\\\"adults\\\":[{\\\"age\\\":40}]},\\\"consumption\\\":[\" ++ lines ++ \"]}\") with\n  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default\n  | .error _ => default\n"
_gf = S.get('families') or '[' + ', '.join(n for n, ok in (('vatF', S.get('vat')), ('exciseF', S.get('ex') or S.get('retail')), ('citF', S.get('cit'))) if ok) + ']'
S['families'] = (_gf.rstrip()[:-1].rstrip() + (', ' if _gf.strip() != '[]' else '') + 'customsF]')
_gu = S.get('unsupported_expr') or (' ++ '.join(f'when ({c}) {_gj.dumps(t, ensure_ascii=False)}' for c, t in S.get('unsupported', [])) or '[]')
S['unsupported_expr'] = '(' + _gu + ') ++ customsUnknown g'
S['taxes'] = S['taxes'] + [{"oecd": "5120", "tax": "Customs duties (HTSUS column 1)", "statute": "HTSUS (19 U.S.C. 1202) 2025: 0207.14.00 17.6 c/kg; 1006.30.10 11.2 %, .90 1.4 c/kg; 2202.10.00 0.2 c/l; 2203.00 Free; 2204.21.50 6.3 c/l, .80 16.9 c/l; 2208.30 Free; 2402.20.80 $1.05/kg + 2.3 %, .90 $1.50/kg + 3.2 %; 2710.12.15 52.5 c/bbl; 2710.19.11 10.5 c/bbl; 3004.90, 4901.99, 8471.30, 8517.13 Free; 6109.10.00 16.5 %; 8703.23.01, 8703.80.00 2.5 %; Special column Free for USMCA (S), CAFTA-DR (P) and the bilateral FTAs", "dated": "USITC HTS REST export (hts.usitc.gov/reststop/exportList, release=2025HTSBasic and 2025HTSRev32: every line used identical in both, so unchanged through 2025), us/law/hts_2025HTS{Basic,Rev32}_NNNN.json; gap pass 2026-11-21", "grade": "B", "status": "modelled", "package": "P7", "kernel_parts": ["TariffRule", "customsFamily", "consumptionC"], "unsupported": ["2025 Chapter 99 additional duties (IEEPA, reciprocal, s. 232, s. 301) not computed: every foreign-origin line is flagged grade C", "only the listed HS lines are modelled; any other code is grade C (no tariff line)", "GSP (A, A+, A*) expired on 31 Dec 2020 and is not applied; CBERA/AGOA not modelled", "specific duties need the line's quantity (litres) or mass (\"massG\")"], "gap_pass": "2026-11-21 approach 1 (customs, kernel 2.8.0)"}]
S['guards'] = (S.get('guards') or []) + ["-- T-shirts from Viet Nam: 10 975 / 1,0975 = 10 000; / 1,165 = 8 583; 16.5 % = 1 416", "(tariff.charges (custLine \"{\\\"good\\\":\\\"clothing\\\",\\\"amount\\\":10975,\\\"hs\\\":\\\"6109.10\\\",\\\"origin\\\":\\\"VN\\\"}\")).map (·.due) == [1416]", "-- from Mexico (USMCA, S): Free", "(tariff.charges (custLine \"{\\\"good\\\":\\\"clothing\\\",\\\"amount\\\":10975,\\\"hs\\\":\\\"6109.10\\\",\\\"origin\\\":\\\"MX\\\"}\")).map (·.due) == [0]", "-- Chapter 99 flag on every foreign line", "(customsUnknown (custLine \"{\\\"good\\\":\\\"clothing\\\",\\\"amount\\\":10975,\\\"hs\\\":\\\"6109.10\\\",\\\"origin\\\":\\\"VN\\\"}\")).length == 1"]
S['doc'] = S['doc'] + '\n\n' + "**Customs (gap pass, kernel 2.8.0 `TariffRule`)**: HTSUS column 1 General rates of the representative goods (USITC 2025 Basic Edition, the same in Revision 32), specific duties per litre / kg / barrel (158.987 l), the Special column's Free treatment for USMCA, CAFTA-DR and the bilateral FTAs. The 2025 Chapter 99 duties (IEEPA, reciprocal, s. 232) depend on the entry date: every foreign-origin line carries a grade-C line."
