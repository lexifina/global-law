import MnGlobal.Pit

/-!
# Mongolia 2025: no net wealth tax (4200, cited absence)

Source: Татварын ерөнхий хууль (General Tax Law, revised text of 2019), consolidated text on legalinfo.mn (`/mn/detail/14403`,
read 2026-11-21; `mn/law/mn_general_tax_law_legalinfo14403.html`). **Art. 7.1**: the taxes of Mongolia consist of the
taxes, payments and fees; **art. 7.2** lists their types, 7.2.1 to 7.2.30. No item is a tax on net wealth: the property
taxes listed are the immovable property tax (7.2.14), the livestock tax (7.2.15), the vehicle tax (7.2.16), the firearms
tax (7.2.19) and the dog and cat tax (7.2.21). The amendment notes inside art. 7 are of 2021-12-30 (7.2.30), 2023-12-08
(7.2.21) and 2024-06-05 (7.2.20): the list in force in 2025 is the one read. Item 7.2.22 names an inheritance and gift
tax. Gap-closing session: 4300 is a cited absence (lexifina/mongolia-law): art. 7.3 leaves each tax to its own law,
art. 8 delegates no rate for 7.2.22, and no such law is among the laws in force on legalinfo.mn (laws.csv, 951 laws); the
PIT law (2019) art. 7.1.3 taxes only an employer's gifts, as wages.
-/

namespace MnGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Net wealth tax: not levied in 2025. Татварын ерөнхий хууль (General Tax Law, revised 2019; legalinfo.mn /mn/detail/14403) art. 7.1-7.2: the taxes of Mongolia are the 30 types listed in 7.2 (7.2.1-7.2.30); none is a tax on net wealth (the property taxes listed are on immovable property 7.2.14, livestock 7.2.15, vehicles 7.2.16, firearms 7.2.19 and dogs and cats 7.2.21). Amendment notes in art. 7 end 2024-06-05 (7.2.20)" },
   { oecd := .estate, why := "Inheritance, estate and gift taxes: not levied in 2025. Татварын ерөнхий хууль (General Tax Law 2019; lexifina/mongolia-law law/2019/14403, official source legalinfo.mn lawId=14403) art. 7.2.22 names \"өв залгамжлал, бэлэглэлийн албан татвар\", but art. 7.3 leaves each tax to this law and the law on that tax, and art. 8.2-8.4 delegate rate-setting for other items only (7.2.22 is not among them): without its own law the tax is not imposed. No such law is among the 951 laws in force on legalinfo.mn (lexifina/mongolia-law laws.csv, read 2026-10-28); the PIT law (2019, law/2019/14410) taxes only gifts from an employer, as wages (art. 7.1.3). The register is of 2026: a law in force in 2025 and repealed by October 2026 would not show; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 2

end MnGlobal.Transfers
