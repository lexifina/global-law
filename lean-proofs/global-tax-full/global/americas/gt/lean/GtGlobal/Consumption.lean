import GtGlobal.Pit

/-!
# Guatemala 2025: Impuesto al Valor Agregado (5111); fuel and drinks distribution taxes (5121)

Sources: Decreto 32-2001 del Congreso (Diario de Centro América, 2001), Congreso PDF via Wayback (capture 2025-08-12;
`gt/law/decreto_32_2001.pdf`, scanned: OCR `decreto_32_2001.ocr.txt`; ARCHIVE_INDEX.tsv); Decreto 10-2012 Libro III
(the 1.x builder's copy `world/B12-latin-america/gt/src/d10_2012.txt`), which reforms arts. 3, 8, 16, 23, 24, 29, 55-57
of the Ley del IVA but not art. 10 or art. 7. The consolidated Ley del IVA (Decreto 27-92) was not reached (SAT portal
403; the Congreso 27-92 capture holds one page): grade B.
* **Art. 10** as reformed by Decreto 32-2001 art. 1: taxpayers "pagarán el impuesto con una tarifa del doce por ciento
  (12%) sobre la base imponible. La tarifa del impuesto en todos los casos deberá estar incluida en el precio de venta"
  (single rate). In force from publication (art. 3).
* The art. 7 exemptions (education, interest, rent of dwellings, cooperatives and the like) and the pequeño contribuyente
  regime (Decreto 10-2012) are not held: every good is charged at 12 % (upper bound, flagged).

**Specific taxes (pass 12, grade A):**
* **Fuels: Decreto 38-92 art. 12 "A"**, added by **Decreto 11-2003 art. 5** (`gt/law/reforma_ley_alcoholes_scp.pdf`,
  scp.gob.gt copy of the decree): "tasas específicas, por galón americano de 3.785 litros: Gasolina superior Q. 4.70,
  Gasolina regular Q. 4.60 ... Diesel y gas oil Q. 1.30". Per litre: 4.60 / 3.785 and 1.30 / 3.785. Petrol is read as
  gasolina regular (superior Q 4.70 flagged). Later amendments of art. 12 "A" not identified (Decreto 10-2012 and 4-2012
  do not touch it: checked by grep); a temporary suspension decree for 2025 not found.
* **Drinks: Decreto 21-2004** (`gt/law/d21_2004_alcohol_scp.pdf`, scp.gob.gt): art. 9 base = "el precio de venta al
  consumidor final sugerido por el fabricante o el importador ... sin incluir en dicho precio, el Impuesto al Valor
  Agregado, ni el impuesto a la distribución" - the consumer amount net of both, as the kernel line reads it; art. 10
  cervezas 6 %, art. 11 vinos 7.5 %, art. 15 bebidas alcohólicas destiladas 8.5 %. The suggested price is taken equal to
  the price paid (flagged). Decreto 4-2012 Libro VII reforms only the tobacco law (61-77), not 21-2004.
* **Tobacco (Decreto 61-77 art. 27)**: only the Decreto 4-2012 art. 69 reform of the second paragraph is held (base not
  less than 75 % of the suggested price net of IVA and the specific tax); the rate paragraph is not held: grade C.
-/

namespace GtGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon GtGlobal

def vat : Vat :=
  { name := "Impuesto al Valor Agregado", standard := 1200,
    classOf := fun gd => match gd with
      | _ => .standard }

def vatStatute : String := "Ley del IVA (Decreto 27-92) art. 10 as reformed by Decreto 32-2001 art. 1: 12 %, included in the price"

def vatF : Family := vatFamily "Impuesto al Valor Agregado" vat vatStatute .vat .central

def lines : List ExLine :=
  [{ good := .petrol, name := "Impuesto a la distribución de combustibles (gasolina regular)", num := 460000, den := 378500, statute := "Decreto 38-92 art. 12 A (Decreto 11-2003 art. 5): Q 4.60 per US gallon of 3.785 litres" },
    { good := .diesel, name := "Impuesto a la distribución de combustibles (diésel)", num := 130000, den := 378500, statute := "Decreto 38-92 art. 12 A (Decreto 11-2003 art. 5): Q 1.30 per US gallon of 3.785 litres" },
    { good := .beer, name := "Impuesto a la distribución de cervezas", advBp := 600, vatBp := 1200, statute := "Decreto 21-2004 arts. 9, 10 (6 % of the suggested consumer price net of IVA and the tax)" },
    { good := .wine, name := "Impuesto a la distribución de vinos", advBp := 750, vatBp := 1200, statute := "Decreto 21-2004 arts. 9, 11 (7.5 %)" },
    { good := .spirits, name := "Impuesto a la distribución de bebidas alcohólicas destiladas", advBp := 850, vatBp := 1200, statute := "Decreto 21-2004 arts. 9, 15 (8.5 %)" }]

def exciseF : Family :=
  { name := "5121 excises", covers := [.excise],
    run := fun _ g _ => exciseCharges lines g.consumption }

def families : List Family := [vatF, exciseF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 239: \"Corresponde con exclusividad al Congreso de la República, decretar impuestos ordinarios y extraordinarios\" (`gt/law/const_art-239.md`). no law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (laws read include: Ley del IVA (Decreto 27-92) art. 10 (Decreto 32-2001 art. 1); Decreto 38-92 art. 12 A (Decreto 11-2003 art. 5); Decreto 21-2004 arts. 9-17; Decreto 10-2012 art. 36 (25 %); Decreto 10-2012 Libro I Título V arts. 97-99, 103-105 (art. 104 num. 1 d. repealed by Decreto 19-2013 art. 28); 1.x model (see its summary.json))." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .education || s.good == .financial || s.good == .rent || s.good == .health || s.good == .insurance || s.good == .transport || s.good == .medicines) "art. 7 exemptions of the Ley del IVA (Decreto 27-92) not held: charged at 12 % (upper bound)"
  ++ when (g.consumption.length > 0) "purchases from pequeños contribuyentes (simplified regime, Decreto 10-2012) carry no IVA invoice at 12 %: all spending charged at 12 % (upper bound)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther) "tobacco tax (Decreto 61-77 art. 27): rate paragraph not held, grade C"
  ++ when (g.consumption.any fun s => s.good == .petrol) "petrol read as gasolina regular (Q 4.60/gal; superior Q 4.70)"
  ++ when (g.consumption.any fun s => s.good == .beer || s.good == .wine || s.good == .spirits) "drinks: the suggested consumer price (art. 9) taken equal to the price paid; sparkling wine, vermouth, cider, mixed drinks (all 7.5 %) read as wine"

#guard vat.embedded { good := .clothing, amount := 1120 } == 120
#guard vat.embedded { good := .food, amount := 1120 } == 120
#guard vat.standard == 1200
-- 100 litres of regular petrol: 100 x 4.60 / 3.785 = 121.53
#guard (lines.find? (·.good == .petrol)).get!.duty { good := .petrol, amount := 3000, quantity := 100000 } == 121
-- 100 litres of diesel: 100 x 1.30 / 3.785 = 34.35
#guard (lines.find? (·.good == .diesel)).get!.duty { good := .diesel, amount := 2500, quantity := 100000 } == 34
-- beer Q 1,120 paid: net of IVA 1,000, net of the tax 1,000 / 1.06 = 943, 6 % = 56.6
#guard (lines.find? (·.good == .beer)).get!.duty { good := .beer, amount := 1120 } == 56

end GtGlobal.Consumption
