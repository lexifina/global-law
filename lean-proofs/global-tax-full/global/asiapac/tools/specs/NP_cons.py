S = dict(cc="NP", family_name="5111 Value added tax",
doc=r'''# Nepal 2025: value added tax (5111); excise duty not modelled

Source: Value Added Tax Act, 2052 (1996), English text on nepallaws.com (secondary host; per-section pages and
Schedule 1 "List of VAT exempt goods and services", read 2026-11-21; `np/law/np_vat_*_nepallaws.txt`, sha256 in
`SHA256SUMS`). The Finance Acts 2081 and 2082 that set the rate and amend Schedule 1 were not read (ird.gov.np pages are
script-driven; the IRD PDF of the Act answers 404): grade B.
* **s. 7 (1)**: the tax is levied "in a single rate as prescribed in the Financial Act made for that fiscal year":
  13 % (rate in the Finance Acts 2081/2082, not read). **s. 7 (2)**: Schedule 2 zero-rated (exports).
* **s. 9**: small vendors under "a prescribed annual taxable transaction threshold" are exempt from registration; the
  threshold is in the VAT Rules (not read): not applied.
* **Schedule 1** (s. 5 (3)): Group 1 basic agricultural products (rice, cereals, flours, vegetables, fruit; not when
  supplied by hotels or restaurants); Group 2 goods of basic needs (salt, kerosene 2710.19.10, electrical energy
  2716.00.00, fuel wood, tap water); Group 3 live animals and animal products; Group 5 medicines (Chapter 30) and
  health services; Group 6 education by schools and universities; Group 7 books and newspapers; Group 9 air transport
  and public transportation; Group 11 (B) 4 financial services and life, accident, medical and agricultural insurance;
  Group 12 purchase, sale and rental of buildings and land (not hotels, guesthouses, apartments).''',
vat=dict(name="Value added tax", standard=1300, statute="VAT Act 2052 s. 7 (13 % by the Finance Act), Schedule 1 Groups 1-3, 5-7, 9, 11, 12",
  classes={"food":"exempt","electricity":"exempt","water":"exempt","heatingOil":"exempt","medicines":"exempt","health":"exempt","education":"exempt","books":"exempt","newspapers":"exempt","transport":"exempt","financial":"exempt","rent":"exempt"}),
notes=["NP 5111: VAT Act 2052 (nepallaws.com English text, Schedule 1); 13 % from the Finance Act (not read); grade B"],
unsupported=[[["food"],"basic food (Schedule 1 Groups 1 and 3: cereals, flours, vegetables, fruit, meat, fish, milk) is exempt; processed food is taxable at 13 %: food modelled as exempt"],
 [["insurance"],"only life, accident, medical and agricultural insurance are exempt (Schedule 1 Group 11 (B) 4); insurance is modelled as taxable"],
 [["transport"],"air transport and public transportation are exempt (Schedule 1 Group 9); applied to the whole class"],
 ["*","registration threshold (VAT Act s. 9, amount in the VAT Rules) not applied"],
 [["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"excise duty (Excise Duty Act 2058 and the Finance Act schedule) not modelled"]],
extra_run=[],
guards=["vat.embedded { good := .clothing, amount := 1130 } == 130","vat.embedded { good := .rent, amount := 1130 } == 0","vat.embedded { good := .hotels, amount := 1130 } == 130"],
taxes=[{"oecd":"5111","tax":"Value added tax (13 %)","statute":"Value Added Tax Act, 2052 s. 5, s. 7, Schedule 1; Finance Act 2081/2082 (rate)","dated":"nepallaws.com English text read 2026-11-21 (amendment state not dated); Finance Acts not read","grade":"B","kernel_parts":["Vat"],"unsupported":["registration threshold (VAT Rules) not applied","partial exemptions applied by whole class (food, transport, insurance)"]},
 {"oecd":"5121","tax":"Excise duty","statute":"Excise Duty Act 2058 and the Finance Act 2082 schedule","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: ird.gov.np (category pages script-driven, no PDF links in the HTML); would unlock: the Finance Act 2081 and 2082 excise schedules (per litre / per 1,000 sticks)"]}])
