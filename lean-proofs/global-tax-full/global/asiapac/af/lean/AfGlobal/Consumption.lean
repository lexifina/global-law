import AfGlobal.Pit

/-!
# Afghanistan 2025: business receipts tax (5112); no VAT; excise not modelled

Source: Income Tax Law 2009, MoF consolidated English version "Version: December 2016" (`cmp20/world/B11-south-asia/af/law/
itl2009_consol2016.pdf`, text `itl.txt`; sha256 in `law/SOURCES.tsv`). Whether every 2016 provision was applied unchanged in
2025 could not be checked (grade B).
* **art. 64 (1)**: "A legal person who provides goods or services in exchange for consideration shall be required to pay
  business receipts tax"; (2) natural persons from "Afs. 750,000 or more per quarter"; (3) imports 4 % on cost incl. duty.
* **art. 66**: (1) "Four percent of income received (before any deductions)" (Presidential Decree No. 149 of 13.02.2016);
  (3) "Five percent … from hotels or guest houses and restaurants" above the threshold; (5) "Ten percent … from
  telecommunication, hotels and restaurants providing superior services".
* **art. 65**: exempt 1- interest. In the basket the tax is taken inside the final seller's price (rate × price);
  restaurants and hotels at 5 %, communication at 10 %, interest-bearing financial services exempt; its cascade through
  earlier stages is not modelled.
-/

namespace AfGlobal.Consumption
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .vat, why := "no VAT in force: the business receipts tax of Income Tax Law 2009 ch. 10 (arts. 64-67) is the general tax on sales (a VAT law was never brought into force)" }]

def notes : List String := ["AF 5112: Income Tax Law 2009 ch. 10, consolidated version December 2016"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if true then ["session 11 year-in-force audit: the only text is the MoF consolidation 'Version: December 2016' of the Income Tax Law 2009; no 2025 version, amendment list or 2025 official source reached (the 2025 application of the 2016 text is not established): grade C"] else [])


end AfGlobal.Consumption
