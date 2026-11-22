S = dict(cc="PG", family_name="5111 Goods and Services Tax",
doc=r'''# Papua New Guinea 2025: goods and services tax (5111); excise not modelled

Source: Goods and Services Tax Act 2003 (No. 38 of 2003), certified text as amended by No. 20 of 2004 and No. 13 of 2005
(PacLII consolidation, Wayback capture 20250103080229 of `paclii.org/pg/legis/consol_act/gasta2003226.pdf`;
`pg/law/pg_gst2003.pdf`, sha256 in `SHA256SUMS`).
* **s. 8**: "a tax, to be known as Goods and Services Tax, shall be charged … at the rate of 10% on the supply (but not
  including an exempt supply) in Papua New Guinea of goods and services, by a registered person".
* **s. 25 (1)** financial services exempt; **(4)** "medical and related services by a hospital, a registered medical
  practitioner … is exempt"; **(5)** educational services by an educational institution, including text books;
  **(7) (a)** "public road transport to passengers by a registered Public Motor Vehicle (PMV) or Taxi"; **(7) (b)** the
  retail supply of newspapers.
* **s. 21 (1) (a)** medical supplies supplied by or on behalf of a hospital, doctor, … pharmacist: zero-rated.
* **s. 43 (1) (a)**: liability to register where taxable supplies over 12 months exceed an amount printed "K1000,000.00"
  (sic) "or such larger amounts as may … be prescribed": the figure is ambiguous in the certified text and no threshold
  is applied (flagged for company entities).
* **s. 24 (1)** "financial services" (exempt under s. 25 (1)) include **(i)** life insurance; other insurance is taxable.
  Letting of dwellings is not in s. 24 or s. 25: residential rent is standard-rated.
Later amendments (after 2005) were not read; the 10 % rate in s. 8 is the rate in force in 2025 as far as the texts
reached show (grade B).''',
vat=dict(name="Goods and Services Tax", standard=1000, statute="Goods and Services Tax Act 2003 s. 8 (10 %), s. 21 (1) (a), s. 25 (1), (4), (5), (7)",
  classes={"financial":"exempt","health":"exempt","education":"exempt","books":"exempt","transport":"exempt","newspapers":"exempt","medicines":"zero"}),
notes=["PG 5111: GST Act 2003 s. 8 (10 %), ss. 21, 25 (PacLII certified text as amended to 2005)"],
unsupported=[[["insurance"],"life insurance is exempt (GST Act 2003 s. 24 (1) (i), s. 25 (1)); insurance is modelled as taxable (non-life)"],
 [["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"excise (Excise Tariff Act 1956 Schedule 1) not modelled: the 2025 schedule was not reached"],
 [["books","newspapers","transport","health","education"],"exemptions of s. 25 (5) and (7) apply only to supplies by the listed suppliers (educational institutions, PMVs and taxis, newspaper vendors); applied to the whole class"]],
extra_run=[],
guards=["vat.embedded { good := .clothing, amount := 1100 } == 100","vat.embedded { good := .education, amount := 1100 } == 0","vat.embedded { good := .medicines, amount := 1100 } == 0"],
taxes=[{"oecd":"5111","tax":"Goods and Services Tax (10 %)","statute":"Goods and Services Tax Act 2003 s. 8, s. 21 (1) (a), s. 25 (1), (4), (5), (7)","dated":"PacLII certified text as amended by No. 20 of 2004 and No. 13 of 2005 (Wayback 2025-01-03); later amendments not read","grade":"B","kernel_parts":["Vat"],"unsupported":["registration threshold s. 43 (1) (a) printed 'K1000,000.00' (ambiguous): not applied"]},
 {"oecd":"5121","tax":"Excise duty","statute":"Excise Tariff Act 1956 (Ch. 107) s. 4, Schedule 1","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: PacLII consolidation (Wayback 20250130102407) prints Schedule 1 with the note 'the updated schedules to this Act were not available at time of going to press' (pre-2000 rates); would unlock: the Excise Tariff schedule as amended by the 2025 Budget (parliament.gov.pg / IRC)"]}])
