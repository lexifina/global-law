S = dict(cc="TV", family_name="none",
doc=r'''# Tuvalu 2025: consumption taxes (P1) not modelled (grade C)

Read (PacLII sessional texts via the Wayback Machine; `tv/law/`, sha256 in `SHA256SUMS`):
* Consumption Tax Act 2008 **s. 5 (3)**: "The rate of Consumption Tax shall be an amount determined by the Minister by
  Regulation, but shall be an amount within the range from 3% to 10%"; **s. 7 (1)**: registration at "$100,000 or more".
* Consumption Tax Regulations 2009 **reg. 3**: 3 % from 1 July 2009; Consumption Tax (Amendment) Regulations 2011:
  "Replace the reference to "3%" … with "4%"".
* Consumption Tax (Amendment) Act 2020 (No. 10 of 2020): s. 6 (1) (e)-(h) zero-rated supplies moved to a regulation.
The regulation fixing the rate in force in 2025 (after 2011) was not reached, so the tax is not modelled.''',
notes=["TV P1: Consumption Tax Act 2008 read; the 2025 rate regulation not reached (grade C)"],
unsupported=[["basket","consumption tax (Consumption Tax Act 2008; rate set by regulation within 3-10 %, 4 % from the 2011 regulation, later regulations not reached) and import levies not modelled"]],
guards=["absent.length == 0"],
taxes=[{"oecd":"5111","tax":"Tuvalu consumption tax","statute":"Consumption Tax Act 2008 s. 5 (3) (rate by regulation within 3 %-10 %), s. 7 (1); Consumption Tax Regulations 2009 reg. 3 (3 %), Amendment Regulations 2011 (4 %); Consumption Tax (Amendment) Act 2020","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: PacLII via Wayback (Act 2008, Regulations 2009 and 2011, Amendment Act 2020 read); tuvalu-legislation.tv answers 502 and its Wayback captures have no later consumption tax regulation; would unlock: the regulation fixing the rate in force in 2025"]},
 {"oecd":"5121","tax":"Import levies and excise","statute":"Import Levy (Imposition of Levy) Order 1997; Customs Revenue and Border Protection Act 2014","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: tuvalu-legislation.tv (502) and its Wayback captures (Import Levy Order 1997, Customs Tariff Order 2009 only); would unlock: the import levy / excise schedule in force 2025"]}])
