import CoGlobal.Pit
import TaxKernel.Global2

/-!
# Colombia 2025: IVA (5111); impuesto nacional al consumo and excises (5121) unsupported

Source: Estatuto Tributario, Secretaría del Senado consolidation (`co/law/et/estatuto_tributario_pr0NN.html`, fetched
2026-11-21; every article carries its amendment notes: the 2025 wording is the one after Ley 2277 de 2022).
* **art. 468**: "La tarifa general del impuesto sobre las ventas es del diecinueve por ciento (19%)" (art. 184 Ley
  1819 de 2016).
* Excluded goods (art. 424: basic foods, medicines), exempt goods with refund (art. 477: meat, fish, eggs, milk) and
  excluded services (art. 476: health, education, public passenger transport, rent of housing, residential public
  utilities, interest): the basket's food line is read as these basic foods (0 %), flagged.
* Impuesto nacional al consumo (art. 512-1: restaurants, mobile telephony, some goods), the departmental taxes on
  tobacco and liquor (Ley 223 de 1995, Ley 1816 de 2016; amounts indexed every year), the national gasoline and ACPM
  tax and the carbon tax (amounts indexed every year by DIAN resolution): not read in a dated form: unsupported.

**Pass 12 (2026-11-21), beer (A):** Ley 223 de 1995 (lexifina/colombia-law `act/1995/reforma-tributaria`, Secretaría
del Senado text) art. 189: "La base gravable ... está constituida por el precio de venta al detallista", the sum of a)
the price invoiced to retailers "excluido el impuesto al consumo" and b) "El valor del impuesto al consumo"; art. 190:
"Cervezas y sifones: 48%" (8 points to health). The base includes the tax; the model takes it as the consumer price net
of IVA (19 %), so the retail margin is in the base (upper bound). Departmental tobacco and liquor taxes (indexed),
gasoline/ACPM and carbon (2025 DIAN amounts) remain C.

**Pass 10 (2026-11-21), 5121 (held ET, Secretaría del Senado consolidation, `co/law/et/`):** art. 426 (Ley 2010 de 2019): prepared food and drinks in restaurants, cafeterías, etc. are a service excluded from IVA and subject to the impuesto nacional al consumo of art. 512-1; art. 512-9: base the precio total de consumo, rate 8 %, included in the list price. Art. 513-4 (Ley 2277 de 2022): bebidas ultraprocesadas azucaradas, 2025: below 5 g added sugar per 100 ml $0, 5 g to below 9 g $38, 9 g or more $65 per 100 ml (IMP = Vol/100 × tarifa). Both A. The INC restaurants is OECD 5126 (specific services), booked under the excise heading (the kernel has no 5126).

**Pass 13 (2026-11-21): national gasoline/ACPM tax and carbon tax (A).** Ley 1607 art. 168 (Ley 1819 art. 219): $490 corriente /
$469 ACPM per gallon, "se ajustará cada primero de febrero con la inflación del año anterior"; Ley 1819 art. 222 (Ley 2277 art. 48):
$20.500 per t CO2eq, gasolina $169, ACPM $191 per gallon, adjusted each 1 February by CPI + 1 point (gasolina, ACPM, gas natural
from 2024). DIAN normograma (fetched from the build server): **Resolución 000007 de 2024** (from 1 Feb 2024): corriente $724,70, ACPM $693,65;
carbon gasolina $186,37, ACPM $210,63; **Resolución 000008 de 2025** ("rige a partir del primero (1) de febrero de 2025"): corriente
$762,39, extra $1.446,98, ACPM $729,71; carbon gasolina $197,93, ACPM $223,69 ($27.399,14 per t). Per US gallon of 3.785411784 l;
rules dated with `validTo/validFrom` 2025-02-01 (undated line: 31/365 and 334/365). Pure-fuel rates: the E10/biodiesel blend
shares are not distinguished (upper bound). The sobretasa (Ley 488/1998) and the departmental taxes stay C.
-/

namespace CoGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon CoGlobal

def vat : Vat :=
  { name := "Impuesto sobre las Ventas (IVA)", standard := 1900,
    classOf := fun gd => match gd with
      | .food => .zero
      | .medicines | .education | .health | .transport | .rent | .water | .electricity | .financial | .restaurants => .exempt
      | _ => .standard }

def vatStatute : String := "Estatuto Tributario art. 468 (19 %), arts. 424, 476, 477; art. 426 (restaurants: excluded, under the impuesto nacional al consumo)"

def vatF : Family := vatFamily "Impuesto sobre las Ventas (IVA)" vat vatStatute .vat .central

/-- ET art. 512-9: 8 % of the total consumption price, the tax included in the list price: amount × 8/108. -/
def incRest (s : Spend) : Int := divR .down (800 * pos s.amount) 10800

/-- ET art. 513-4, 2025: pesos per 100 ml by added sugar per 100 ml -> per litre: $380 from 5 g, $650 from 9 g. -/
def bebidas : ExciseRule :=
  { good := .nonAlcoholic, name := "Impuesto a las bebidas ultraprocesadas azucaradas",
    sugarBands := [(0, 0, 1), (5000, 380, 1), (9000, 650, 1)], statute := "ET art. 513-1, 513-3, 513-4 (Ley 2277 de 2022 art. 54): 2025 per 100 ml: under 5 g added sugar $0; 5 g to under 9 g $38; 9 g or more $65" }

/-- Ley 223 de 1995 arts. 189-190: impuesto al consumo de cervezas, 48 % of the precio de venta al detallista, which
includes the tax itself (art. 189 a) + b)); read from the consumer price net of IVA (19 %): the retail margin stays in
the base (upper bound, flagged). -/
def cerveza (s : Spend) : Int := divR .down (4800 * divR .down (pos s.amount * BP) 11900) BP

/-! Pass 13: impuesto nacional a la gasolina y al ACPM (Ley 1607 art. 168 as replaced by Ley 1819 art. 219; par. 1:
indexed each 1 February) and impuesto nacional al carbono (Ley 1819 art. 222 as replaced by Ley 2277 art. 48; par. 1:
CPI + 1 point each 1 February). Pesos per US gallon (3.785411784 l): DIAN Resolucion 000007 de 2024 (from 1 Feb 2024,
in force to 31 Jan 2025) and Resolucion 000008 de 2025 (from 1 Feb 2025). An undated line is split 31/365 + 334/365. -/
/-- centavos per US gallon -> `perUnitNum / perUnitDen` pesos per litre -/
def galNum (c : Int) : Int := c * 1000000000
def galDen : Int := 100 * 3785411784
def fuelRule (good : Good) (name : String) (c : Int) (fr to : String) (st : String) : ExciseRule :=
  { good, name, perUnitNum := galNum c, perUnitDen := galDen, validFrom := fr, validTo := to, statute := st }
def r24 : String := "DIAN Res. 000007 de 2024 art. "
def r25 : String := "DIAN Res. 000008 de 2025 art. "
def ingNac : String := "Impuesto nacional a la gasolina y al ACPM"
def carbono : String := "Impuesto nacional al carbono"
def gas24 : ExciseRule := fuelRule .petrol ingNac 72470 "" "2025-02-01" (r24 ++ "1 num. 1 (Ley 1607 art. 168, Ley 1819 art. 219): gasolina corriente $724,70 per gallon, to 31 Jan 2025")
def gas25 : ExciseRule := fuelRule .petrol ingNac 76239 "2025-02-01" "" (r25 ++ "1 num. 1 (Ley 1607 art. 168, Ley 1819 art. 219): gasolina corriente $762,39 per gallon from 1 Feb 2025")
def acpm24 : ExciseRule := fuelRule .diesel ingNac 69365 "" "2025-02-01" (r24 ++ "1 num. 1: ACPM $693,65 per gallon, to 31 Jan 2025")
def acpm25 : ExciseRule := fuelRule .diesel ingNac 72971 "2025-02-01" "" (r25 ++ "1 num. 1: ACPM $729,71 per gallon from 1 Feb 2025")
def cGas24 : ExciseRule := fuelRule .petrol carbono 18637 "" "2025-02-01" (r24 ++ "2 (Ley 1819 art. 222, Ley 2277 art. 48): gasolina $186,37 per gallon, to 31 Jan 2025")
def cGas25 : ExciseRule := fuelRule .petrol carbono 19793 "2025-02-01" "" (r25 ++ "2 (Ley 1819 art. 222, Ley 2277 art. 48): gasolina $197,93 per gallon from 1 Feb 2025")
def cAcpm24 : ExciseRule := fuelRule .diesel carbono 21063 "" "2025-02-01" (r24 ++ "2: ACPM $210,63 per gallon, to 31 Jan 2025")
def cAcpm25 : ExciseRule := fuelRule .diesel carbono 22369 "2025-02-01" "" (r25 ++ "2: ACPM $223,69 per gallon from 1 Feb 2025")
def fuelRules : List ExciseRule := [gas24, gas25, acpm24, acpm25, cGas24, cGas25, cAcpm24, cAcpm25]

def exciseF : Family :=
  { name := "5121 impuesto nacional al consumo (restaurantes), bebidas ultraprocesadas azucaradas, cervezas, gasolina y ACPM, carbono", covers := [.excise],
    run := fun _ g _ =>
      (g.consumption.filterMap fun s => if s.good == .restaurants then
        some (charge .excise "Impuesto nacional al consumo (restaurantes)" s.amount id (fun _ => incRest s) (event := s.good.name)
          (bearer := .consumer) (statute := "ET art. 512-1 num. 3, art. 512-9 (8 % of the precio total de consumo, included in the list price), art. 426 (excluded from IVA)")) else none)
      ++ exciseRuleCharges [bebidas] g
      ++ exciseRuleCharges fuelRules g
      ++ (g.consumption.filterMap fun s => if s.good == .beer then
        some (charge .excise "Impuesto al consumo de cervezas" s.amount id (fun _ => cerveza s) (event := s.good.name)
          (bearer := .consumer) (statute := "Ley 223 de 1995 arts. 189 (base: precio de venta al detallista, tax included), 190 (cervezas 48 %)")) else none) }

def families : List Family := [vatF, exciseF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .electricity || s.good == .water) "residential utilities taken as excluded (art. 476); the exclusion depends on the household's stratum and consumption"
  ++ when (!g.consumption.isEmpty) "food read as the excluded/exempt basic foods of arts. 424, 477; processed food is at 19 % (or 5 % under art. 468-1)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .wine || s.good == .spirits || s.good == .communication) "departmental tobacco and liquor taxes (Ley 1816/2016; Ley 1819/2016 art. 347; 2025 indexed amounts not read) and INC on mobile services (art. 512-2): not charged"
  ++ when (g.consumption.any fun s => s.good == .restaurants) "INC restaurantes: every restaurant amount taken as charged by a responsible (art. 512-13 small natural-person establishments are not responsible); IVA excluded under art. 426"
  ++ when (g.consumption.any fun s => s.good == .nonAlcoholic || s.good == .food) "bebidas ultraprocesadas: the line's sugar per 100 ml is read as the added sugar (a line without it pays nothing); exempt drinks of art. 513-1 (milk drinks, juices without added sugar, etc.) not distinguished; the 20 % tax on ultra-processed foods (art. 513-6 to 513-9) is not charged (the food line has no tariff heading)"
  ++ when (g.consumption.any fun s => s.good == .beer) "beer (Ley 223/1995 art. 189): the precio de venta al detallista read as the consumer price net of IVA (retail margin inside: upper bound); mezclas y refajos 20 % not distinguished"
  ++ when (g.consumption.any fun s => s.good == .petrol || s.good == .diesel) "gasolina/ACPM national tax and carbon tax at the pure-fuel rates per US gallon: the ethanol share of E10 gasoline and the biodiesel share of the ACPM blend (Res. 000008 art. 1 num. 2: 98/2 to 90/10 lower rates) are not distinguished (upper bound); San Andres rates, frontier-zone exemption (Ley 1819 art. 220) and the sobretasa a la gasolina/ACPM (Ley 488/1998) not modelled"

#guard vat.embedded { good := .clothing, amount := 1190 } == 190
#guard vat.embedded { good := .food, amount := 1190 } == 0
#guard vat.embedded { good := .restaurants, amount := 10800 } == 0
#guard incRest { good := .restaurants, amount := 10800 } == 800
-- 2 litres at 10 g added sugar per 100 ml: $65 × 20; at 6 g: $38 × 20; at 4 g: nothing
#guard bebidas.dutyOn { good := .nonAlcoholic, amount := 9000, quantity := 2000 } { sugarMg100ml := 10000 } == 1300
#guard bebidas.dutyOn { good := .nonAlcoholic, amount := 9000, quantity := 2000 } { sugarMg100ml := 6000 } == 760
#guard bebidas.dutyOn { good := .nonAlcoholic, amount := 9000, quantity := 2000 } { sugarMg100ml := 4000 } == 0
-- beer $11,900 paid: 10,000 net of IVA, 48 % = 4,800
#guard cerveza { good := .beer, amount := 11900 } == 4800
-- 31 l in January / 334 l from February (the window shares of an undated 365 l): pesos per gallon / 3.785411784
#guard gas24.dutyOn { good := .petrol, amount := 0, quantity := 31000 } {} == 5934
#guard gas25.dutyOn { good := .petrol, amount := 0, quantity := 334000 } {} == 67268
#guard acpm24.dutyOn { good := .diesel, amount := 0, quantity := 31000 } {} == 5680
#guard acpm25.dutyOn { good := .diesel, amount := 0, quantity := 334000 } {} == 64384
#guard cGas24.dutyOn { good := .petrol, amount := 0, quantity := 31000 } {} == 1526
#guard cGas25.dutyOn { good := .petrol, amount := 0, quantity := 334000 } {} == 17464
#guard cAcpm24.dutyOn { good := .diesel, amount := 0, quantity := 31000 } {} == 1724
#guard cAcpm25.dutyOn { good := .diesel, amount := 0, quantity := 334000 } {} == 19736

end CoGlobal.Consumption
