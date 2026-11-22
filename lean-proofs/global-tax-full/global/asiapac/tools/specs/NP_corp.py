S = {'cc': 'NP', 'doc': '# Nepal FY 2082/83: income tax on entities (1200)\n\nIncome Tax Act 2058 as amended by the Finance Act 2082 (`cmp20/world/B11-south-asia/np/law/ita2058_fa2082.pdf`): Schedule 1\nrates as read by the registry (B).\n* **Schedule 1 s. 2**: entities 25 %; banks, financial institutions, telecom, tobacco and alcohol 30 % (flag `bank`);\n  special industries 20 %. Withholding (s. 88-89): not reached (C).', 'regimeName': 'Income tax on entities', 'unsupported': [], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on entities', 'statute': 'ITA 2058 Schedule 1 s. 2', 'dated': 'FY 2082/83', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'ITA 2058 ss. 88-89', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['rates not located in the text']}], 'sched': [(0, 2500)], 'citStatute': 'ITA 2058 Schedule 1 s. 2', 'guards': ['(cit { profit := 1000000 }).citTax { profit := 1000000 } == 250000'], 'rateByFlag': [('bank', 3000), ('specialIndustry', 2000)]}

# ---- FT review (2026-11-21): withholding on payments (ITA 2058 s. 88 (1), (2) (क)) read in the FA 2082 consolidation ----
S["doc"] = S["doc"].replace(" Withholding (s. 88-89): not reached (C).", "") + '''

FT review (2026-11-21): **ITA 2058 s. 88** in the consolidation as amended by the Finance Act 2082
(`cmp20/world/B11-south-asia/np/law/ita2058_fa2082.pdf`, sha256 8a1ca760... in that folder's SHA256SUMS; text layer
`ita2058.txt` lines 4645-4800, Devanagari with ligature damage, the rates legible):
* **s. 88 (1)**: a resident person paying "नेपालमा स्रोत भएको ब्याज, ... रोयल्टी, सेवा शुल्क, ... भुक्तानी गर्दा कुल भुक्तानी रकमको
  पन्ध्र प्रतिशतका दरले कर कट्टी गर्नु पर्नेछ" (interest, royalties, service fees with a source in Nepal: 15 % of the gross
  payment); the provisos' lower rates (5 % commission paid by a resident employment company to a non-resident,
  10 % aircraft lease, 5 % interest on foreign-currency loans of banks and of hydropower projects, ...) are not modelled.
* **s. 88 (2) (क)**: "लाभांश भुक्तानी गरेकोमा भुक्तानी रकमको पाँच प्रतिशत" (dividends: 5 %).
Recipient type does not change the rate; tax withheld on a payment to an individual is booked under 1100.'''
S["wht"] = [{"kind": "dividend", "rate": 500, "statute": "ITA 2058 s. 88 (2) (क) (5 %)"},
            {"kind": "interest", "rate": 1500, "statute": "ITA 2058 s. 88 (1) (15 %)"},
            {"kind": "royalty", "rate": 1500, "statute": "ITA 2058 s. 88 (1) (15 %)"},
            {"kind": "services", "rate": 1500, "statute": "ITA 2058 s. 88 (1) (सेवा शुल्क, 15 %)"}]
S["whtName"] = "Withholding tax on payments (ITA 2058 s. 88)"
S["guards"] = S["guards"] + [
  "-- s. 88 (2) (क) 5 %; s. 88 (1) 15 %",
  "wht.amount { kind := .dividend, amount := 1000 } == 50",
  "wht.amount { kind := .interest, amount := 1000 } == 150",
  "wht.amount { kind := .royalty, amount := 1000 } == 150",
  "wht.amount { kind := .services, amount := 1000, toCompany := false } == 150"]
S["unsupported"] = S["unsupported"] + [["company.paymentsAbroad", "ITA 2058 s. 88 (1) provisos (5 % / 10 % special payments) and treaty rates not modelled"]]
for _t in S["taxes"]:
    if _t["oecd"] == "1200/1100":
        _t.update({"statute": "ITA 2058 s. 88 (1), (2) (क)", "dated": "consolidation as amended by the Finance Act 2082", "grade": "A",
                   "kernel_parts": ["Wht"], "unsupported": ["s. 88 (1) provisos (special lower rates)"]})
S["unsupported"] = [["abroad" if c == "company.paymentsAbroad" else c, t] for c, t in S["unsupported"]]
