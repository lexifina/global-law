import HnGlobal.Pit

/-!
# HN 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (none read): tried not read in this pass; would unlock: the act's 2025 text.

**Pass 15 (2026-11-21), net wealth (4200): not levied (A).** Not levied (convention R5-3k-G, pass 15): Constitución art. 205 num. 35: "Establecer impuestos y contribuciones así como las cargas públicas" (`hn/law/const_art-205.md`). The Impuesto al Activo Total Neto (Ley de Equidad Tributaria, Decreto 51-2003, La Gaceta 30,059, arts. 5-16; SAR copy `hn/law/sar_decreto51-2003_equidad.*`, OCR) is 1 % of the balance-sheet assets of merchant companies less reserves, depreciation and fixed-asset financing, above L 3,000,000 (arts. 5-7, 14 num. 1); art. 15 makes the amount paid a credit against the income tax, the obligation being met when the income tax paid is equal or higher: a minimum income tax on companies (heading 1200), not a tax on net wealth. Decreto 17-2010 (La Gaceta 32,193) art. 86 num. 6 derogates 'el capitulo II del Impuesto del Activo Neto' of Decreto 51-2003 (`hn/law/sar_decreto17-2010.*`), while Decreto 278-2013 art. 9 (new LISR art. 22-A, `hn/law/sar_decreto278-2013.*`) still refers to declaring the 'Impuesto Sobre el Activo Neto': whichever reading holds in 2025, no tax on net wealth is levied. No law read in this build levies a recurrent tax on net wealth (laws read include: Decreto-Ley 24 de 1963 arts. 6, 15 (texto consolidado al Decreto 59-2022); LISR art. 22 (25 %); LISR (Decreto-Ley 25, SAR consolidation to Acuerdo SAR 07-2025) art. 5 num. 3), 5), 6), 7); 1.x model (see its summary.json); LISR art. 10; Reglamento de Aplicación de la Ley del Seguro Social (Acuerdo 193/1971) art. 28).
-/

namespace HnGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon HnGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 15): Constitución art. 205 num. 35: \"Establecer impuestos y contribuciones así como las cargas públicas\" (`hn/law/const_art-205.md`). The Impuesto al Activo Total Neto (Ley de Equidad Tributaria, Decreto 51-2003, La Gaceta 30,059, arts. 5-16; SAR copy `hn/law/sar_decreto51-2003_equidad.*`, OCR) is 1 % of the balance-sheet assets of merchant companies less reserves, depreciation and fixed-asset financing, above L 3,000,000 (arts. 5-7, 14 num. 1); art. 15 makes the amount paid a credit against the income tax, the obligation being met when the income tax paid is equal or higher: a minimum income tax on companies (heading 1200), not a tax on net wealth. Decreto 17-2010 (La Gaceta 32,193) art. 86 num. 6 derogates 'el capitulo II del Impuesto del Activo Neto' of Decreto 51-2003 (`hn/law/sar_decreto17-2010.*`), while Decreto 278-2013 art. 9 (new LISR art. 22-A, `hn/law/sar_decreto278-2013.*`) still refers to declaring the 'Impuesto Sobre el Activo Neto': whichever reading holds in 2025, no tax on net wealth is levied. No law read in this build levies a recurrent tax on net wealth (laws read include: Decreto-Ley 24 de 1963 arts. 6, 15 (texto consolidado al Decreto 59-2022); LISR art. 22 (25 %); LISR (Decreto-Ley 25, SAR consolidation to Acuerdo SAR 07-2025) art. 5 num. 3), 5), 6), 7); 1.x model (see its summary.json); LISR art. 10; Reglamento de Aplicación de la Ley del Seguro Social (Acuerdo 193/1971) art. 28)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end HnGlobal.Property
