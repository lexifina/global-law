import GyGlobal.Pit

/-!
# Guyana 2025: property (net wealth) tax not levied on individuals (4200); companies and inheritance grade C

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
taxes (no text held).
-/

namespace GyGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon GyGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "individuals are exempt from the Property Tax Act from the year of income 2025 (Fiscal Enactments (Amendment) Act 2026 ss. 1 (4), 5: Cap. 81:21 s. 6 (1) (y)); the tax on companies' net property is not modelled" }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "property tax on a company's net property (Cap. 81:21) not modelled: company rates not read"
  ++ when (!g.transfers.isEmpty) "inheritance and gift taxes: no text held (grade C)"


end GyGlobal.Property
