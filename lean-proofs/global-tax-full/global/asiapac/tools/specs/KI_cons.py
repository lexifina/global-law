S = dict(cc="KI", family_name="5111 Value Added Tax",
doc=r'''# Kiribati 2025: value added tax (5111); excise not modelled

Source: Value Added Tax Act 2013 (Kiribati sessional legislation, PacLII; Wayback capture 20250130161400 of
`paclii.org/ki/legis/num_act/vata2013132/`; `ki/law/ki_vat2013_paclii.html`, sha256 in `SHA256SUMS`).
* **s. 7 (3)**: "The rate of VAT is — (a) in the case of a taxable supply that is a zero-rated supply, zero percent; or
  (b) in any other case, 12.5%."
* **s. 8 (2)**: "The registration threshold is $100,000." (registration when taxable supplies in a 12 month period exceed
  it).
* **Second Schedule cl. 1** exempt: (a) financial services; (d), (e) sale or lease of residential premises (other than new
  premises and leases under 2 months); (h) education services; (i) medical, dental or nursing services by a person
  registered under the Medical Services Act 1996; (j) "a supply of medicine".
* Third Schedule: zero-rating of exports and international transport only (no basket good).
The Act as enacted (sessional text) is the latest reached; the rate is taken as in force in 2025 (grade B).''',
vat=dict(name="Value added tax", standard=1250, threshold=100000, statute="Value Added Tax Act 2013 s. 7 (3) (12.5 %), s. 8 (2) ($100,000), Second Schedule cl. 1 (a), (d), (e), (h), (i), (j)",
  classes={"financial":"exempt","rent":"exempt","education":"exempt","health":"exempt","medicines":"exempt"}),
notes=["KI 5111: VAT Act 2013 ss. 7-8, Second Schedule (PacLII sessional text)"],
unsupported=[[["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel","nonAlcoholic"],"excise (Excise Tax Act) not modelled: its 2025 schedule was not reached"],
 [["insurance"],"insurance modelled as taxable (the Second Schedule definition of financial services was not read in full)"]],
guards=["vat.embedded { good := .clothing, amount := 1125 } == 125","vat.embedded { good := .medicines, amount := 1125 } == 0","vat.net { turnover := 100000, sales := [{ good := .other, net := 100000 }] } == 0"],
taxes=[{"oecd":"5111","tax":"Value added tax (12.5 %)","statute":"Value Added Tax Act 2013 s. 7 (3), s. 8 (2), Second Schedule cl. 1","dated":"Act as enacted (PacLII sessional, Wayback 2025-01-30); amendments after 2013 not read","grade":"B","kernel_parts":["Vat"],"unsupported":["amendments after 2013 not read"]},
 {"oecd":"5121","tax":"Excise tax","statute":"excise legislation of Kiribati (text not reached)","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: Wayback CDX of paclii.org/ki/legis (2 762 URLs: only the VAT Act 2013 among tax acts); kiribatilaws.gov.ki and mof.gov.ki unreachable from a second machine; would unlock: the excise act and its 2025 schedule"]}])
