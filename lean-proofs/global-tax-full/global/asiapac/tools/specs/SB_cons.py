S = dict(cc="SB", family_name="5112 Sales tax (Cap. 125)",
doc=r'''# Solomon Islands 2025: sales tax on prescribed services and fuel (5112); goods tax and excise not modelled

Source: Sales Tax Act (Cap. 125), Reprint "As in force at: 5 February 2024 … STATUS: CURRENT" (Legislation Act 2023),
published by the Inland Revenue Division (`ird.gov.sb/wp-content/uploads/2025/10/SALE-TAX-ACT-CAP-125.pdf`, fetched
2026-11-21; `sb/law/sb_sales_tax_cap125_2024.pdf`, sha256 in `SHA256SUMS`).
* **s. 3 (1)**: "Every purchaser of prescribed goods or services shall be charged a tax (to be known as "sales tax") …
  computed in such amount or at such percentage of the value thereof as may be prescribed".
* **Schedule One** items 1 "Local and Overseas Telecommunications: 10 cents in the dollar", 2 "Restaurant Services:
  10 cents in the dollar", 12 "Sale of petroleum … 10 cents per litre", 13 "Sale of diesoline … 10 cents per litre".
  Other goods and services are not prescribed (no sales tax).
The tax is charged on the purchaser on top of the price (10 % of the value): the basket amount is taken tax-inclusive.
Goods tax (Cap. 122, Reprint as in force 5 February 2024; Second Schedule as substituted by L.N. 73 of 2019: imported
goods 15 %, prescribed locally manufactured goods 10 %, rice 5 %) is levied on the wholesale sale value (s. 69), which the
basket does not carry: not modelled.''',
vat=dict(oecd="5112", name="Sales tax", standard=1000, statute="Sales Tax Act (Cap. 125) s. 3 (1), Schedule One items 1-2 (10 cents in the dollar)",
  classes={g:"exempt" for g in ["food","nonAlcoholic","beer","wine","spirits","cigarettes","tobaccoOther","clothing","rent","water","electricity","gas","petrol","diesel","heatingOil","medicines","health","transport","recreation","books","newspapers","education","hotels","financial","insurance","other"]}),
excise=[dict(good="petrol", name="Sales tax (petroleum)", num=10, den=100, statute="Sales Tax Act (Cap. 125) Schedule One item 12 (10 cents per litre)"),
  dict(good="diesel", name="Sales tax (diesoline)", num=10, den=100, statute="Sales Tax Act (Cap. 125) Schedule One item 13 (10 cents per litre)")],
notes=["SB 5112: Sales Tax Act (Cap. 125) reprint as in force 5 February 2024, Schedule One"],
unsupported=[["basket","goods tax (Goods Tax Act Cap. 122 s. 69, Second Schedule: imported goods 15 %, local manufactures 10 %, rice 5 %) is charged on the wholesale value, not in the basket: not modelled"],
 [["transport","recreation","other"],"Schedule One items charged per ticket or on particular services (air tickets $10, sea fares 10 %, movie tickets, professional, accounting, legal, real estate, vehicle hire) not modelled"],
 [["spirits","wine","beer","cigarettes","tobaccoOther"],"excise (Customs and Excise Act) not modelled"]],
guards=["vat.embedded { good := .restaurants, amount := 1100 } == 100","vat.embedded { good := .food, amount := 1100 } == 0",
  "excise.duty { good := .petrol, amount := 1500, quantity := 100000 } == 10"],
taxes=[{"oecd":"5112","tax":"Sales tax (Cap. 125) on telecommunications, restaurants and fuel","statute":"Sales Tax Act (Cap. 125) s. 3 (1), Schedule One items 1, 2, 12, 13","dated":"Reprint as in force at 5 February 2024 (IRD, STATUS: CURRENT)","grade":"B","kernel_parts":["Vat","Excise"],"unsupported":["per-ticket and professional-service items of Schedule One not modelled","no 2025-dated text: amendments after 5 February 2024 not checked"]},
 {"oecd":"5112","tax":"Goods tax (Cap. 122)","statute":"Goods Tax Act (Cap. 122) s. 69, Second Schedule (L.N. 73 of 2019): imported goods 15 %, prescribed local manufactures 10 %, rice 5 %","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["rates read in the Reprint as in force 5 February 2024; the base is the wholesale sale value (s. 69, 130 % of cost rules), which the canonical basket does not carry; would unlock: a wholesale-value field or a margin rule"]},
 {"oecd":"5121","tax":"Excise duty","statute":"Customs and Excise Act (Cap. 121) and its tariff","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: IRD legislation page (no excise tariff; Customs and Excise Amendment (No. 2) Act 2012 only), PacLII via Wayback (consolidation 1996); would unlock: the Customs and Excise tariff as in force 2025 (customs.gov.sb)"]}])
