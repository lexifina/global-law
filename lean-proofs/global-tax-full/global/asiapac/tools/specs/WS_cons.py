S = dict(cc="WS", family_name="5111 Value Added Goods and Services Tax",
doc=r'''# Samoa 2025: value added goods and services tax (5111); excise not modelled

Source: Value Added Goods and Services Tax Act 2015, "official version of this Act as at 31 December 2018" (revision
notes 2016-2018; Ministry for Revenue copy, Wayback 20251130151308 of
`revenue.gov.ws/wp-content/uploads/2022/08/Value-Added-Goods-and-Services-Tax-Act-2015.pdf`; `ws/law/ws_vagst2015.pdf`,
sha256 in `SHA256SUMS`).
* **s. 8 (3)**: "The rate of GST is: (a) for a taxable supply that is a zero-rated supply, zero percent; or (b) in any
  other case, 15%."
* **s. 9 (1) (b), (2)**: registration where taxable supplies in a 12 month period exceed the registration threshold;
  "The registration threshold is at least $130,000." (130 000 tala used).
* **Schedule 2 cl. 1** exempt: (a) financial services; (c) "the supply to passengers of transport services by buses and
  taxis"; (f) carriage of passengers by ships within Samoa.
* **Schedule 3 Part 1 cl. 1** zero-rated: (j) "a supply of educational services"; (k) "a supply of medical goods or
  services provided in hospitals"; (l) "a supply of water"; (o) electricity supplied under the Electric Power
  Corporation Act 1980.
The 2018 revised text is the latest official version reached; the 15 % rate is taken as in force in 2025 (grade B).''',
vat=dict(name="Value added goods and services tax", standard=1500, threshold=130000, statute="VAGST Act 2015 s. 8 (3) (15 %), s. 9 (2) ($130,000), Schedule 2 cl. 1, Schedule 3 Part 1 cl. 1",
  classes={"financial":"exempt","transport":"exempt","education":"zero","health":"zero","water":"zero","electricity":"zero"}),
notes=["WS 5111: VAGST Act 2015 (official version as at 31 December 2018)"],
unsupported=[[["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel","nonAlcoholic"],"excise (Excise Tax Rates Act 1984 Schedule, as amended to 2019 and later) not modelled: the 2025 schedule was not reached"],
 [["health","transport"],"zero-rating of medical supplies covers hospitals only (Schedule 3 cl. 1 (k)); transport exemption covers buses, taxis and domestic ships only; applied to the whole class"]],
guards=["vat.embedded { good := .clothing, amount := 1150 } == 150","vat.embedded { good := .water, amount := 1150 } == 0","vat.net { turnover := 130000, sales := [{ good := .other, net := 130000 }] } == 0"],
taxes=[{"oecd":"5111","tax":"Value added goods and services tax (15 %)","statute":"VAGST Act 2015 s. 8 (3), s. 9 (2), Schedule 2 cl. 1 (a), (c), (f), Schedule 3 Part 1 cl. 1 (j), (k), (l), (o)","dated":"official version as at 31 December 2018 (Ministry for Revenue, Wayback 2025-11-30); later amendments not read","grade":"B","kernel_parts":["Vat"],"unsupported":["amendments after 2018 not read"]},
 {"oecd":"5121","tax":"Excise tax","statute":"Excise Tax Rates Act 1984 Schedule (official version as at 31 December 2018), Excise Tax Rates Amendment Act 2019 (No. 28)","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: the 2018 official version (Wayback revenue.gov.ws) gives e.g. cigarettes $244.31 per 1000 sticks, rising to $256.52 from 1 July 2019 (Amendment Act (No. 3) 2018); the 2019 Amendment Act No. 28 is a scanned PDF (not OCRed) and later amendments were not found: rates for 2025 unknown; would unlock: the Excise Tax Rates Act revised to 2024/2025 (samoalaws.gov.ws, unreachable from a second machine and the build server)"]}])
