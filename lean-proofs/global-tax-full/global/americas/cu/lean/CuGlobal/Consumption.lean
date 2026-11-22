import CuGlobal.Pit

/-!
# Cuba 2025: impuestos sobre las Ventas y los Servicios (5112); Impuesto Especial a Productos y Servicios (5121)

Sources: Ley 113 "Del Sistema Tributario" (2012) as modified to 2021 (`world/B13-caribbean/cu/law/l113.txt`) and the
2025 budget law, **Ley 174** de 2024 (Gaceta Oficial GOC-2024-O127, 30/12/2024; `ley174_presupuesto2025.pdf`), which
sets the year's rates (grade A).
* Ley 113 art. 132, 135: the sales tax on goods for use and consumption, base "el importe total de las ventas";
  art. 146-150 the services tax, base "el total de los ingresos".
* **Ley 174 art. 74**: "Se grava en el año 2025 con los impuestos sobre las Ventas y los Servicios a las personas
  jurídicas, por la comercialización minorista de bienes y la prestación de servicios a la población, aplicando un tipo
  impositivo del diez por ciento (10 %)"; art. 76-78 the same 10 % for MSMEs, cooperatives, natural persons and
  associations; **art. 80** telecommunications by ETECSA 5 %; **art. 81** books, newspapers, educational materials not
  taxed; **art. 82** electricity transmission not taxed; **art. 83.1** exonerated: a) the rationed family basket, b)
  liquefied gas, d) medicines in community pharmacies, j) state passenger transport.
* The tax is a share of the sales value the household pays: 10 % (5 %) of the amount.
* **Impuesto Especial** (Ley 113 art. 140-145; Ley 174 art. 85): rates per product set by the Minister of Finance and
  Prices: unsupported.
-/

namespace CuGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon CuGlobal

/-- Ley 174 art. 74-83: the 2025 rate on the retail value, bp (0 = not taxed or exonerated). -/
def rateOf (g : Good) : Int :=
  match g with
  | .books | .newspapers | .education | .electricity | .medicines | .transport | .gas | .health => 0
  | .rent | .financial | .insurance => 0
  | .communication => 500
  | _ => 1000

def salesF : Family :=
  { name := "5112 impuestos sobre las Ventas y los Servicios", covers := [.salesTax],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [charge .salesTax "Impuestos sobre las Ventas y los Servicios" (isum (g.consumption.map (·.amount))) id
          (fun _ => isum (g.consumption.map fun s => divR .down (rateOf s.good * pos s.amount) BP)) (event := "basket")
          (bearer := .consumer) (statute := "Ley 113 art. 132-150; Ley 174 (2025) art. 74, 76-78 (10 %), 80 (5 %), 81-83")])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
        [charge .salesTax "Impuestos sobre las Ventas y los Servicios" (isum (g.company.sales.map (·.net))) id
          (fun _ => isum (g.company.sales.map fun s => if s.exported then 0 else divR .down (rateOf s.good * pos s.net) BP))
          (event := "supplies") (bearer := .consumer) (statute := "Ley 174 (2025) art. 74, 76 (10 % of sales; no input credit)")] else []) }

def families : List Family := [salesF]

def absent : List Absent :=
  [{ oecd := .vat, why := "Cuba levies no value added tax: Ley 113 art. 132-150 tax retail sales and services on their gross value (Ley 174 (2025) art. 61 lists the year's taxes; none is a VAT)" }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) "Impuesto Especial a Productos y Servicios (Ley 113 art. 140-145; Ley 174 art. 85): rates per product by the Minister of Finance and Prices, not read: not charged"
  ++ when (g.consumption.any (·.good == .food)) "food: the rationed family basket is exonerated (Ley 174 art. 83.1 a)); the model taxes the whole food line at 10 % (market purchases)"
  ++ when (g.consumption.any fun s => s.good == .rent || s.good == .financial || s.good == .insurance || s.good == .health) "housing rent, financial services, insurance and health services taken as outside the services tax (state provision; not read)"

#guard rateOf .clothing == 1000
#guard rateOf .books == 0
#guard rateOf .communication == 500

end CuGlobal.Consumption
