import DoGlobal.Pit

/-!
# DO 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (Ley 2569 (sucesiones y donaciones)): tried not read in this pass; would unlock: the act's 2025 text.

**Pass 15 (2026-11-21), net wealth (4200): not levied (A).** Not levied (convention R5-3k-G, pass 15): Constitución art. 93 num. 1 a): "Establecer los impuestos, tributos o contribuciones generales" (`do/law/const_articulo-093.md`); art. 243: "El régimen tributario está basado en los principios de legalidad" (`do/law/const_articulo-243.md`). The Impuesto sobre los Activos (Código Tributario Título V, arts. 401-407, added by Ley 557-05 of 13 Dec 2005; DGII consolidation `do/law/ct_titulo5_wb2020.pdf`, Wayback 2020-11-26; the DGII income-tax page of 22 Jun 2025, `world/B13-caribbean/do/law/dgii_impuestoSobreRenta_wayback_20250622.html`, describes the same tax at 1 % in 2025) falls on companies and sole-proprietor businesses (art. 401) and is measured on the balance-sheet assets after depreciation, not net of debts (art. 402); art. 407 makes the amount a credit against the income tax of the same year, and the asset tax is extinguished when the income tax is equal or higher (párrafo I): a minimum income tax on businesses (heading 1200), not a tax on net wealth. Ley 253-12 art. 48 (note in the consolidation) planned its reduction and removal subject to a revenue target; DGII still lists it in 2025. No law read in this build levies a recurrent tax on net wealth (laws read include: Código Tributario (Ley 11-92) Título III arts. 335, 343, 344, 345 (Ley 253-12); Código Tributario (Ley 11-92) art. 375 (Ley 253-12) Párrafos I, II, VII, VIII; Código Tributario art. 297 (27 %); Código Tributario arts. 305, 306, 308 (Ley 253-12); 1.x model (see its summary.json); Código Tributario arts. 283, 289, 296, 299 m)).
-/

namespace DoGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon DoGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 15): Constitución art. 93 num. 1 a): \"Establecer los impuestos, tributos o contribuciones generales\" (`do/law/const_articulo-093.md`); art. 243: \"El régimen tributario está basado en los principios de legalidad\" (`do/law/const_articulo-243.md`). The Impuesto sobre los Activos (Código Tributario Título V, arts. 401-407, added by Ley 557-05 of 13 Dec 2005; DGII consolidation `do/law/ct_titulo5_wb2020.pdf`, Wayback 2020-11-26; the DGII income-tax page of 22 Jun 2025, `world/B13-caribbean/do/law/dgii_impuestoSobreRenta_wayback_20250622.html`, describes the same tax at 1 % in 2025) falls on companies and sole-proprietor businesses (art. 401) and is measured on the balance-sheet assets after depreciation, not net of debts (art. 402); art. 407 makes the amount a credit against the income tax of the same year, and the asset tax is extinguished when the income tax is equal or higher (párrafo I): a minimum income tax on businesses (heading 1200), not a tax on net wealth. Ley 253-12 art. 48 (note in the consolidation) planned its reduction and removal subject to a revenue target; DGII still lists it in 2025. No law read in this build levies a recurrent tax on net wealth (laws read include: Código Tributario (Ley 11-92) Título III arts. 335, 343, 344, 345 (Ley 253-12); Código Tributario (Ley 11-92) art. 375 (Ley 253-12) Párrafos I, II, VII, VIII; Código Tributario art. 297 (27 %); Código Tributario arts. 305, 306, 308 (Ley 253-12); 1.x model (see its summary.json); Código Tributario arts. 283, 289, 296, 299 m))." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end DoGlobal.Property
