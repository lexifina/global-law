import ClGlobal.Pit

/-!
# Chile 2025: 5111 IVA (pilot) and 5121 excises (R2)

Sources (BCN LeyChile `get_norma_json`, version 2025-07-01, saved in `cl/law/` with SHA256SUMS):
* **IVA, DL 825** (idNorma 6369): art. 14 "una tasa de 19% sobre la base imponible"; exempt or outside: art. 13 N° 3,
  4, 5, 7, art. 12 E N° 10 (interest), N° 11 with art. 8 g) (unfurnished housing rent). (Pilot.)
* **DL 825 art. 42** (impuesto adicional, "sobre la misma base imponible que la del impuesto al valor agregado"):
  a) non-alcoholic drinks "tasa del 10%" (18 % above 15 g of sugar per 240 ml); b) "Licores, piscos, whisky,
  aguardientes y destilados … tasa del 31,5%"; c) "Vinos … cervezas y otras bebidas alcohólicas … tasa del 20,5%".
  Art. 43: due on the sales of importers, producers and distributors, not on the retailer's sale: the model takes the
  consumer price net of IVA as the base (it includes the retail margin: an upper bound, flagged).
* **DL 828** (tabaco, idNorma 6372; last note D.O. 29.09.2014, Ley 20.780): art. 4 cigarettes "un impuesto específico
  equivalente a 0,0010304240 unidades tributarias mensuales por cada cigarrillo …; y, además, un impuesto de 30%, que se
  aplicará sobre el precio de venta al consumidor, incluido impuestos"; art. 5 tabaco elaborado "un impuesto de 59,7%
  sobre el precio de venta al consumidor, incluido impuestos".
* **Ley 18.502** (combustibles, idLey 18502): art. 6 "para las gasolinas automotrices será de 6 UTM/m3"; "Los impuestos
  específicos … no serán base imponible del Impuesto al Valor Agregado" (so the IVA in a petrol amount is on the amount
  less the specific tax). The diesel component is "el menor valor entre 2 UTM/m3 y el vigente al 31 de diciembre de
  1989": the 1989 figure is not in the text. Pass 10: the SII guide "Impuestos indirectos" (sii.cl, fetched
  2026-11-21, `cl/law/sii_impuestos_indirectos.*`): "La tasa del impuesto es de 1,5 UTM por m3 para el petróleo diesel y
  de 6 UTM por m3 para la gasolina automotriz (tasas denominadas componente base)" -> diesel 1,5 UTM/m3 (B; within the
  statutory 2 UTM ceiling). The variable component (Ley 20.765) is set by weekly decree (unsupported).
* **UTM (pass 13, year in force)**: Ley 18.502 art. 6 ("se expresarán en Unidades Tributarias Mensuales, según su valor
  vigente al momento de la determinación del impuesto") and DL 828 art. 4 ("la unidad tributaria mensual vigente al
  momento de la determinación del impuesto"): each sale is taxed at the UTM of its month. An undated annual quantity is
  spread over 2025 by days (the kernel's convention for undated lines), so the specific taxes use the day-weighted UTM
  of 2025: Σ days × UTM / 365 = 25.056.300 / 365 (= 68.647,40), from the SII table `cl/law/sii_utm2025.*` (Jan 67.429,
  Feb 67.294, Mar 68.034, Apr 68.306, May 68.648, Jun 68.785, Jul 68.923, Aug 68.647, Sep 69.265, Oct 69.265, Nov 69.542,
  Dec 69.542). Until pass 12 the December UTM (69.542) priced the whole year.
-/

namespace ClGlobal.Consumption
open TaxKernel TaxKernel.Global ClGlobal AmerCommon

def utm : Int := uta / 12
#guard utm == 69542

/-- 2025 monthly UTM (SII utm2025.htm) and days per month: Σ days × UTM (UTM-days of 2025). -/
def utmMonths : List (Int × Int) :=
  [(31, 67429), (28, 67294), (31, 68034), (30, 68306), (31, 68648), (30, 68785),
   (31, 68923), (31, 68647), (30, 69265), (31, 69265), (30, 69542), (31, 69542)]
def utmDays : Int := isum (utmMonths.map fun (d, u) => d * u)
#guard utmDays == 25056300
#guard isum (utmMonths.map (·.1)) == 365

def iva : Vat :=
  { name := "Impuesto al Valor Agregado", standard := 1900,
    classOf := fun gd => match gd with
      | .education | .transport | .health | .rent | .financial => .exempt
      | _ => .standard }

def ivaStatute : String := "DL 825 art. 14 (19 %); art. 13 N° 3, 4, 5, 7, art. 12 E N° 10, art. 8 g)"

/-- Ley 18.502 art. 6: 6 UTM per m³ of gasoline (per litre: 6 × UTM / 1000). -/
def gasolina : ExLine :=
  { good := .petrol, name := "Impuesto específico a las gasolinas automotrices", num := 6 * utmDays, den := 1000 * 365,
    statute := "Ley 18.502 art. 6 (6 UTM/m3 at the UTM of the month of sale; undated: 2025 day-weighted UTM; fixed component only)" }

/-- Ley 18.502 art. 6 inc. 5 (the lower of 2 UTM/m³ and the 31.12.1989 rate) = 1,5 UTM per m³ (SII guide). -/
def diesel : ExLine :=
  { good := .diesel, name := "Impuesto específico al petróleo diesel", num := 15 * utmDays, den := 10000 * 365,
    statute := "Ley 18.502 art. 6 (lower of 2 UTM/m3 and the 31.12.1989 rate; 1,5 UTM/m3 per the SII guide; UTM of the month of sale, undated: 2025 day-weighted; fixed component only)" }

def adicional (good : Good) (bp : Int) (lit : String) : ExLine :=
  { good, name := "Impuesto adicional art. 42 DL 825", advBp := bp, vatBp := 1900,
    statute := s!"DL 825 art. 42 {lit} (on the IVA base)" }

def lines : List ExLine :=
  [gasolina, diesel, adicional .spirits 3150 "b) 31,5 %", adicional .wine 2050 "c) 20,5 %", adicional .beer 2050 "c) 20,5 %",
   adicional .nonAlcoholic 1000 "a) 10 %"]

/-- DL 828 art. 4 and 5 (retail price including taxes is the base of the ad valorem part). -/
def tabaco : Excise :=
  { rates := [{ good := .cigarettes, name := "Impuesto al tabaco (cigarrillos)", perUnitNum := utmDays * 10304240,
                perUnitDen := 365 * 10000000000, adValoremBp := 3000, statute := "DL 828 art. 4 (0,0010304240 UTM per cigarette at the UTM of the month, undated: 2025 day-weighted + 30 % of the retail price)" },
              { good := .tobaccoOther, name := "Impuesto al tabaco elaborado", adValoremBp := 5970,
                statute := "DL 828 art. 5 (59,7 % of the retail price)" }] }

/-- The IVA basket: a petrol amount carries the specific tax outside the IVA base. -/
def ivaBasket (sp : List Spend) : List Spend :=
  sp.map fun s => if s.good == .petrol then { s with amount := s.amount - gasolina.specific s }
    else if s.good == .diesel then { s with amount := s.amount - diesel.specific s } else s

def vatF : Family :=
  { name := "5111 IVA", covers := [.vat],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [{ iva.basketCharge (ivaBasket g.consumption) ivaStatute with base := isum (g.consumption.map (·.amount)) }])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then [iva.businessCharge g.company "DL 825 art. 14, 20, 23"] else []) }

def exciseF : Family :=
  { name := "5121 impuestos específicos y adicionales", covers := [.excise],
    run := fun _ g _ => exciseCharges lines g.consumption ++ tabaco.charges g.consumption }

def families : List Family := [vatF, exciseF]
def absent : List Absent := []
def notes : List String := []
def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any (·.good == .diesel)) "diesel: Ley 18.502 art. 6 fixed component 1,5 UTM/m3 (the 31.12.1989 rate as stated by the SII guide); variable component (Ley 20.765, weekly decrees) not modelled"
  ++ when (g.consumption.any fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .nonAlcoholic)
       "DL 825 art. 42: base taken as the consumer price net of IVA (the statute's base is the wholesale price: upper bound); IVA computed on the full price; non-alcoholic drinks at 10 % (18 % if high in sugar)"
  ++ when (g.consumption.any fun s => s.good == .gas || s.good == .heatingOil) "Ley 18.502 GNC/GLP vehicular taxes (art. 1) not modelled"

-- IVA: 11.900 of food holds 1.900; education is exempt
#guard iva.embedded { good := .food, amount := 11900 } == 1900
#guard iva.embedded { good := .education, amount := 11900 } == 0
-- 1.000 litres of petrol: 6 × 25.056.300 / 365 = 411.884,38 -> 411.884
#guard gasolina.specific { good := .petrol, amount := 1500000, quantity := 1000000 } == 411884
-- 1.000 litres of diesel: 1,5 × 25.056.300 / 365 = 102.971,10 -> 102.971
#guard diesel.specific { good := .diesel, amount := 1000000, quantity := 1000000 } == 102971
-- a pack of 20 at 5.000: 20 × 0,0010304240 × 68.647,40 = 1.414,72 -> 1.414 + 30 % (1.500)
#guard tabaco.duty { good := .cigarettes, amount := 5000, quantity := 20000 } == 1414 + 1500
-- spirits: 11.900 × 31,5 % / (1,19 × 1,315)
#guard (adicional .spirits 3150 "").duty { good := .spirits, amount := 15649 } == 3150

end ClGlobal.Consumption
