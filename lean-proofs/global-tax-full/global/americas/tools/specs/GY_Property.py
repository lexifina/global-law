S = dict(cc="GY", fam="Property",
doc=r'''# Guyana 2025: property (net wealth) tax not levied on individuals (4200); companies and inheritance grade C

Sources:
* Fiscal Enactments (Amendment) Act 2026 (No. 3 of 2026, Official Gazette Legal Supplement A of 17 Feb 2026; copy and
  OCR held by the 1.x builder `world/B13-caribbean/gy/law/acts/fiscalenactmentsamendmentact3of2026.ocr.txt`):
  **s. 1 (4)** "The amendments to the Property Tax Act shall come into operation with respect to and from the year of
  income commencing the 1st January, 2025"; **s. 5**: Property Tax Act (Cap. 81:21) s. 6 renumbered 6 (1), and after
  paragraph (x) "(y) notwithstanding any other provision of this Act, an individual." (s. 6 lists the persons exempt).
  So no individual pays property tax for 2025: cited not levied, grade A.
* Before that Act the GRA page "Rates and Calculation" (`gy/law/gra_property_tax_rates.html`) gave the individual rates
  (nil on the first $40 million of net property, 0.5 % on the next $20 million, 0.75 % above).
Not modelled (C rows): the property tax on companies' net property (company rates not read) and inheritance and gift
taxes (no text held).''',
families="[]",
absent=[["wealth", "individuals are exempt from the Property Tax Act from the year of income 2025 (Fiscal Enactments (Amendment) Act 2026 ss. 1 (4), 5: Cap. 81:21 s. 6 (1) (y)); the tax on companies' net property is not modelled"]],
unsupported=[["g.entity == .company", "property tax on a company's net property (Cap. 81:21) not modelled: company rates not read"],
 ["!g.transfers.isEmpty", "inheritance and gift taxes: no text held (grade C)"]],
taxes=[dict(oecd="4200", tax="Property tax on net property (individuals)", statute="Property Tax Act Cap. 81:21 s. 6 (1) (y) inserted by the Fiscal Enactments (Amendment) Act 2026 s. 5, in operation from the year of income 2025 (s. 1 (4))", dated="Act No. 3 of 2026, Official Gazette 17 Feb 2026", grade="A", status="not levied", package="P6", kernel_parts=["Absent"]),
 dict(oecd="4200", tax="Property tax on net property (companies)", statute="Property Tax Act Cap. 81:21 First Schedule", grade="C", status="unsupported", package="P6", kernel_parts=[], tried="the GRA rate page read gives the individual rates only", unsupported=["would unlock: the First Schedule company rates as in force 2025"]),
 dict(oecd="4300", tax="Inheritance and gift taxes", statute="registry: none levied (not cited from a text)", grade="C", status="unsupported", package="P6", kernel_parts=[], tried="no statute read", unsupported=["would unlock: a text showing the abolition or absence"])])
