import json
def C(oecd, tax, statute, tried, unlock):
    return {"oecd": oecd, "tax": tax, "statute": statute, "grade": "C", "status": "unsupported", "kernel_parts": [],
            "unsupported": ["tried: " + tried + "; would unlock: " + unlock]}
D = {}
def put(cc, name, vat, exc, absent=None, note=None):
    taxes = [vat, exc]
    D[cc] = {"name": name,
             "doc": "First pass (R3, 2026-11-21): " + "; ".join(t["tax"] + " (grade " + t["grade"] + ")" for t in taxes)
                    + ". Statutes, what was tried and what would unlock each are in results/taxes/Consumption.json.",
             "absent": absent or [], "unsupported": "consumption taxes of " + name + " not modelled in the first pass (see results/taxes/Consumption.json)",
             "taxes": taxes, "note": note}
LN = "the build server law folders (1.x builder: PIT texts only)"
put("MY", "Malaysia",
    C("5112", "Sales tax (Act 806) and service tax (Act 807)", "Sales Tax Act 2018; Service Tax Act 2018; Sales Tax (Rates of Tax) Order 2025; Service Tax Regulations 2018 First Schedule (scope widened 1 July 2025)", LN + "; lom.agc.gov.my did not answer from the build server", "the Acts and the 2025 Orders from lom.agc.gov.my or mysst.customs.gov.my via a second machine route"),
    C("5121", "Excise duty", "Excise Act 1976; Excise Duties Order 2022", LN, "Excise Duties Order as amended to 2025"))
put("IN", "India",
    C("5111", "Goods and services tax (CGST + SGST/IGST)", "CGST Act 2017 s. 9; Notification 1/2017-Central Tax (Rate) to 21 Sep 2025, Notification 9/2025-Central Tax (Rate) from 22 Sep 2025; Maharashtra GST Act", LN + "; the cbic-gst.gov.in rate page has no notification PDFs", "the two rate notifications (egazette.gov.in) and their Maharashtra SGST twins"),
    C("5121", "Central excise on petrol and diesel; Maharashtra VAT on fuel and liquor", "Central Excise Tariff Act 1985 Eighth Schedule; Maharashtra VAT Act 2002 Schedules", LN, "the 2025 Eighth Schedule rates and the MVAT fuel schedule"))
put("PK", "Pakistan",
    C("5111", "Sales tax on goods (federal) and on services (Punjab)", "Sales Tax Act 1990 s. 3 as amended by Finance Act 2025; Punjab Sales Tax on Services Act 2012", "the Finance Act 2025 gazette PDF on the build server is scanned (no text layer, 320 pages not OCR'd)", "OCR of the Finance Act 2025 Sales Tax part, or the FBR consolidated Sales Tax Act 2025"),
    C("5121", "Federal excise duty", "Federal Excise Act 2005 First Schedule as amended by Finance Act 2025", "as above", "the FBR consolidated First Schedule 2025"))
put("BD", "Bangladesh",
    C("5111", "Value added tax and supplementary duty", "VAT and SD Act 2012 (15 %), Finance Ordinance 2025", LN + " (ITA 2023 only)", "the VAT and SD Act 2012 as amended (nbr.gov.bd) and the 2025 SROs"),
    C("5121", "Supplementary duty", "VAT and SD Act 2012 schedules", LN, "as above"))
put("LK", "Sri Lanka",
    C("5111", "Value added tax; Social Security Contribution Levy (turnover 2.5 %)", "VAT Act No. 14 of 2002 as amended (18 %); SSCL Act No. 25 of 2022", LN + " (IRA amendments and EPF only)", "the VAT (Amendment) Acts of 2023-2024 and the SSCL Act (documents.gov.lk, parliament.lk)"),
    C("5121", "Excise duty", "Excise (Special Provisions) Act No. 13 of 1989 and gazette rate notices", LN, "the 2025 gazette rate notices"))
put("NP", "Nepal",
    C("5111", "Value added tax", "Value Added Tax Act 2052 (13 %)", LN + " (Income Tax Act and Finance Act pages)", "VAT Act 2052 as amended (ird.gov.np, lawcommission.gov.np)"),
    C("5121", "Excise duty", "Excise Duty Act 2058 and the Finance Act 2082 schedule", LN, "Finance Act 2082 excise schedule"))
put("BT", "Bhutan",
    C("5112", "Sales tax (to 31 Dec 2025)", "Sales Tax, Customs and Excise Act of the Kingdom of Bhutan 2000 and its schedules (the GST Act 2020 applies from 1 January 2026, not to 2025)", "the build server (ITA, rules, TDS; the registry's GST consolidation is the 2026 law)", "the Sales Tax, Customs and Excise Act 2000 and the 2025 sales tax and excise schedules (mof.gov.bt)"),
    C("5121", "Excise and green tax", "Sales Tax, Customs and Excise Act 2000", LN, "as above"))
put("MV", "Maldives",
    C("5111", "Goods and services tax (general 8 %, tourism 17 % from 1 July 2025)", "Goods and Services Tax Act (Law 10/2011) as amended", LN + " (Income Tax Act, Pension Act)", "the GST Act consolidation 2025 (mira.gov.mv), two periods for the tourism rate"),
    C("5121", "Import duty on tobacco and alcohol", "Import-Export Act tariff", LN, "customs tariff 2025"))
put("IR", "Iran",
    C("5111", "Value added tax (10 % in 1404)", "VAT Law 1400; Budget Law 1404", LN + " (PIT rescue folders)", "the permanent VAT Law and Budget Law 1404 (rc.majlis.ir) via a second machine route"),
    C("5121", "Taxes on cigarettes, fuel and soft drinks under the VAT Law", "VAT Law 1400", LN, "as above"))
put("MN", "Mongolia",
    C("5111", "Value added tax (10 %)", "Law on Value Added Tax (2015) as amended", LN + " (PIT, health and social insurance laws)", "the VAT law from legalinfo.mn"),
    C("5121", "Excise tax", "Law on Excise Tax (2006) as amended", LN, "legalinfo.mn excise law"))
put("LA", "Laos",
    C("5111", "Value added tax (10 %)", "Law on VAT No. 48/NA (2018); Presidential Decree 003/PS (2024)", LN + " (PIT rescue folder)", "the VAT law and decree from laoofficialgazette.gov.la"),
    C("5121", "Excise tax", "Law on Excise Tax (2019)", LN, "as above"))
put("MM", "Myanmar",
    C("5112", "Commercial tax (5 % general)", "Union Taxation Law 2025; Commercial Tax Law 1990", LN + " (IRD PIT page)", "Union Taxation Law 2025 (ird.gov.mm, mlis.gov.mm)"),
    C("5121", "Specific goods tax", "Specific Goods Tax Law 2016; Union Taxation Law 2025 schedules", LN, "as above"))
put("KH", "Cambodia",
    C("5111", "Value added tax (10 %)", "Law on Taxation 2023, VAT chapter", "the Khmer OCR of the Law on Taxation 2023 on the build server (473 kB) not yet searched", "grep the OCR for the VAT and specific tax chapters (Khmer numerals)"),
    C("5121", "Specific tax on certain goods and services", "Law on Taxation 2023", LN, "as above"))
put("PG", "Papua New Guinea",
    C("5111", "Goods and services tax (10 %)", "Goods and Services Tax Act 2003", "PacLII answers 403 to scripts; the build server has only the Income Tax Act", "the GST Act from parliament.gov.pg or an archived PacLII copy"),
    C("5121", "Excise duty", "Excise Tariff Act 1990 as amended", LN, "the Excise Tariff 2025"))
put("SB", "Solomon Islands",
    C("5112", "Goods tax (Cap. 122, 10 %) and sales tax (Cap. 125)", "Goods Tax Act Cap. 122; Sales Tax Act Cap. 125 (no VAT in 2025: the VAT Bill was introduced in 2025)", "PacLII 403; the build server has the Income Tax Act and NPF Acts", "the two Acts from the Ministry of Finance or an archived PacLII copy"),
    C("5121", "Excise duty", "Excise Act Cap. 123", LN, "as above"))
put("WS", "Samoa",
    C("5111", "Value added goods and services tax (15 %)", "Value Added Goods and Services Tax Act 2015", "not on the build server (Income Tax Act 2012, NPF and ACC Acts, MJCA legislation list)", "the VAGST Act 2015 consolidation from samoalaws.gov.ws"),
    C("5121", "Excise tax", "Excise Tax Rates Act 1984", LN, "as above"))
put("TO", "Tonga",
    C("5111", "Consumption tax (15 %)", "Consumption Tax Act 2003", "not on the build server (Income Tax Act, Regulations and gazettes)", "the Consumption Tax Act consolidation from ago.gov.to"),
    C("5121", "Excise tax", "Excise Tax Act 2007", LN, "as above"))
put("TV", "Tuvalu",
    C("5111", "Tuvalu consumption tax", "Tuvalu Consumption Tax Act 2008", "not on the build server (income tax acts and regulations)", "the TCT Act from tuvalu-legislation.tv"),
    C("5121", "Import levies and excise", "Customs Revenue and Border Protection Act; Import Levy Act", LN, "as above"))
put("KI", "Kiribati",
    C("5111", "Value added tax (12.5 %)", "Value Added Tax Act 2013", "not on the build server (Income Tax Act only)", "the VAT Act 2013 from the Kiribati legislation site"),
    C("5121", "Excise tax", "Excise Tax Act 2013", LN, "as above"))
put("MH", "Marshall Islands",
    C("5112", "Import duties; consumption tax", "Import Duties Act (48 MIRC Ch. 2); Consumption Tax Act 2025 (commencement not read)", "the build server has the Income Tax Act 1989 with its 2024-2025 amendments and the Net Profit Tax Act 2025", "the Consumption Tax Act 2025 and its commencement clause (rmiparliament.org)"),
    C("5121", "Import duties on tobacco, alcohol, fuel", "Import Duties Act", LN, "as above"))
put("FM", "Micronesia (Federated States)",
    C("5112", "State sales taxes (no national VAT)", "state revenue codes (e.g. Pohnpei, Chuuk)", "the build server has FSM Code Titles 53-54 (national income and gross revenue taxes)", "the state revenue codes"),
    C("5121", "National import taxes on tobacco, alcohol, fuel", "FSM Code Title 54", "Title 54 on the build server not yet searched for the import tax", "grep T54_Ch01_SubChpII_2014.txt for the import tax rates"))
put("NR", "Nauru",
    {"oecd": "5111", "tax": "VAT/GST (not levied)", "statute": "no VAT or GST statute among the Laws of Nauru (registry 2026-11-21)", "grade": "B", "kernel_parts": ["Absent"], "unsupported": ["no provision states the absence; to cite: the revenue laws index of ronlaw.gov.nr"]},
    C("5121", "Import duties and excise on tobacco, alcohol, sugar", "Customs Act 2014 and tariff", "the build server has the Employment and Services Tax Act and NSA laws only", "the Customs tariff 2025 (ronlaw.gov.nr)"),
    absent=[["vat", "no VAT or GST statute among the Laws of Nauru (registry 2026-11-21); revenue comes from the Employment and Services Tax Act 2014 and customs duties"]])
put("BN", "Brunei",
    {"oecd": "5111", "tax": "VAT/GST (not levied)", "statute": "no GST or VAT Act in the Laws of Brunei (AGC laws index on the build server: agc_brulaw.html)", "grade": "B", "kernel_parts": ["Absent"], "unsupported": ["absence inferred from the AGC laws index, not from a provision"]},
    C("5121", "Excise duties", "Excise Duties Order and Customs Import Duties Order as amended", "not on the build server (Income Tax Act Cap. 35 and Employee Trust Act)", "the Excise Duties Order schedule from agc.gov.bn"),
    absent=[["vat", "no GST or VAT Act in the Laws of Brunei (AGC laws index, cmp20/world/B15-no-pit/bn/law/agc_brulaw.html)"]])
put("KP", "North Korea (DPRK)",
    {"oecd": "5111", "tax": "Taxes on goods and services (not levied)", "statute": "taxes abolished by the decision of the Supreme People Assembly of 21 March 1974 (complete abolition of taxes, from 1 April 1974); turnover levies of state enterprises are not taxes in DPRK law", "grade": "B", "kernel_parts": ["Absent"], "unsupported": ["the 1974 text is not on the build server"]},
    {"oecd": "5121", "tax": "Excises (not levied)", "statute": "as above", "grade": "B", "kernel_parts": ["Absent"], "unsupported": []},
    absent=[["vat", "taxes abolished from 1 April 1974 (Supreme People Assembly decision of 21 March 1974 on the complete abolition of taxes)"], ["excise", "no taxes on goods are levied (1974 abolition)"], ["salesTax", "no taxes on goods are levied (1974 abolition)"]])
put("CN-HK", "Hong Kong SAR",
    {"oecd": "5111", "tax": "VAT/GST/sales tax (not levied)", "statute": "no sales or value added tax ordinance in the Laws of Hong Kong; Basic Law art. 108 (low tax policy)", "grade": "B", "kernel_parts": ["Absent"], "unsupported": ["no provision states the absence"]},
    C("5121", "Duties on liquor above 30 %, tobacco, hydrocarbon oil, methyl alcohol", "Dutiable Commodities Ordinance (Cap. 109) Schedule 1", "elegislation.gov.hk needs a browser check (script and laptop curl were redirected); no Wayback copy of the PDF", "the 2025 version of Cap. 109 Schedule 1 through a browser session"),
    absent=[["vat", "no VAT, GST or general sales tax ordinance in Hong Kong (only the Dutiable Commodities Ordinance Cap. 109 taxes goods)"]])
put("CN-MO", "Macao SAR",
    {"oecd": "5111", "tax": "VAT/GST/sales tax (not levied)", "statute": "no VAT or general sales tax in Macao; the consumption tax regulation (Lei n.o 4/99/M) taxes tobacco and alcohol only", "grade": "B", "kernel_parts": ["Absent"], "unsupported": ["Imprensa Oficial bo.io.gov.mo did not answer"]},
    C("5121", "Imposto de consumo (tobacco, alcohol above 30 %)", "Regulamento do Imposto de Consumo (Lei n.o 4/99/M) and its tables", "bo.io.gov.mo gave no answer from the build server or a second machine", "the table of the Regulamento from bo.io.gov.mo"),
    absent=[["vat", "no VAT or general sales tax in Macao; the Regulamento do Imposto de Consumo taxes tobacco and alcohol only"]])
json.dump(D, open("specs/bulk_cons_c.json", "w"), indent=1, ensure_ascii=False)
print(len(D))
