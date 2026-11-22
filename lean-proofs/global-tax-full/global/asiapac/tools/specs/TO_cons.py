S = dict(cc="TO", family_name="5111 Consumption Tax",
doc=r'''# Tonga 2025: consumption tax (5111); excise not modelled

Source: Consumption Tax Act 2003 (Act 29 of 2003), bilingual text published by the Ministry of Revenue and Customs
(`revenue.gov.to/sites/default/files/inline-files/ConsumptionTaxAct2003.pdf`, fetched 2026-11-21;
`to/law/to_consumption_tax_act2003.pdf`, sha256 in `SHA256SUMS`).
* **s. 5 (3) (a)**: "The rate of Consumption Tax shall be 15% provided that Chief Commissioner with the consent of Privy
  Council may by Order direct what shall be an exempt import, exempt supply or a zero rated supply".
* **s. 6 (1)**: registration where taxable supplies in a 12 month period "will be $100,000 or more" / "is $100,000 or
  more" (liable from 100 000 pa'anga: kernel threshold 99 999, "at or below which a business is not liable").
* The Ministry's page "Consumption Tax Overview" (fetched 2026-11-21): CT "at the rate of 15% with effect from 1st April
  2005".
Exempt and zero-rated supplies are fixed by Orders under s. 5 (3) (a), which were not read: every basket good is taxed at
15 % (flagged). Grade B: the Act text is not a dated 2025 consolidation.''',
vat=dict(name="Consumption Tax", standard=1500, threshold=99999, statute="Consumption Tax Act 2003 s. 5 (3) (a) (15 %), s. 6 (1) ($100,000 or more)", classes={}),
notes=["TO 5111: Consumption Tax Act 2003 s. 5 (3) (a), s. 6 (1)"],
unsupported=[["basket","Consumption Tax exempt and zero-rated supplies are set by Orders under s. 5 (3) (a) (not read): every good taxed at 15 %"],
 [["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"excise (Excise Tax Act 2008 and amendment orders to 2017) not modelled: later orders not reached"]],
guards=["vat.embedded { good := .food, amount := 1150 } == 150","vat.net { turnover := 99999, sales := [{ good := .other, net := 99999 }] } == 0","vat.net { turnover := 100000, sales := [{ good := .other, net := 100000 }] } == 15000"],
taxes=[{"oecd":"5111","tax":"Consumption tax (15 %)","statute":"Consumption Tax Act 2003 s. 5 (3) (a), s. 6 (1)","dated":"Act text published by the Ministry of Revenue and Customs (fetched 2026-11-21); 15 % from 1 April 2005 (Ministry overview)","grade":"B","kernel_parts":["Vat"],"unsupported":["exempt / zero-rated supplies Orders under s. 5 (3) (a) not read"]},
 {"oecd":"5121","tax":"Excise tax","statute":"Excise Tax Act 2008 and Excise Tax (Amendment) Orders 2010, 2013, 2015, 2016, 2017","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: revenue.gov.to Tax-Legislations lists the Act and amendment orders up to 2017 only; the rates in force in 2025 (later orders) not established; would unlock: the Excise Tax schedule as amended to 2025 (Crown Law, crownlaw.gov.to)"]}])
