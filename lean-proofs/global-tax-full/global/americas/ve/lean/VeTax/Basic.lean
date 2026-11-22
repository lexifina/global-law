import TaxKernel.World

/-!
# Venezuela 2025: Impuesto sobre la Renta of a resident natural person (Decreto-Ley ISLR, G.O. 6.210 Ext., 30-12-2015)

Source: Gaceta Oficial No. 6.210 Extraordinario (Decreto con Rango, Valor y Fuerza de Ley de Impuesto sobre la Renta),
the copy hosted by SENIAT at `declaraciones.seniat.gob.ve/portal/page/portal/MANEJADOR_CONTENIDO_SENIAT/01NOTICIAS/00IMAGENES/Gaceta6210.pdf`
(seniat.gob.ve answers 403 to the build server and a second machine; Internet Archive capture 2024-04-11, 112 scanned pages, sha256
7caafd928ea1b480...; OCR checked against the page images): art. 50 Tarifa No. 1 in unidades tributarias (6 % to
1.000 U.T.; 9 % to 1.500; 12 % to 2.000; 16 % to 2.500; 20 % to 3.000; 24 % to 4.000; 29 % to 6.000; 34 % above;
page 13 image), art. 58 ("desgravamen unico equivalente a setecientas setenta y cuatro unidades tributarias
(774 U.T.)"), art. 59 (rebaja "de diez (10) unidades tributarias (U.T.) anuales", plus ten for the spouse "no separado
de bienes" and ten for each dependent ascendant or descendant).
The 2025 value of the unidad tributaria (a SENIAT providencia) was not reached: the model computes in U.T. and needs
the optional input `veUT` (bolivares per U.T.); without it the tax cannot be expressed in bolivares (access B).
-/

namespace VeTax
open TaxKernel

/-- Art. 50 Tarifa No. 1 (U.T.; rates in bp). -/
def tarifa1Units : List (Int × Int) :=
  [(0, 600), (1000, 900), (1500, 1200), (2000, 1600), (2500, 2000), (3000, 2400), (4000, 2900), (6000, 3400)]
/-- The tarifa on thousandths of a U.T. -/
def tarifa1 : Schedule := Schedule.ofList (tarifa1Units.map fun (u, r) => (u * 1000, r))
/-- Art. 58: "desgravamen unico ... (774 U.T.)". -/
def desgravamenUnicoUT : Int := 774
/-- Art. 59: rebaja personal 10 U.T.; 10 U.T. for the spouse; 10 U.T. per dependent ascendant/descendant. -/
def rebajaUT : Int := 10

/-- Tax in thousandths of a U.T. for a net income given in thousandths of a U.T. -/
def taxMilliUT (netMilli : Int) (cargas : Int) : Int :=
  let base := pos (netMilli - desgravamenUnicoUT * 1000)
  let t := divR .halfUp (tarifa1.ticks base) BP
  pos (t - rebajaUT * 1000 * (1 + cargas))

structure Person where
  netMilliUT : Int
  taxMilliUT : Int
  taxBs : Int
  deriving Repr

def person (wage se rent ut : Int) (cargas : Int) : Person :=
  let gross := pos wage + pos se + pos rent
  let netMilli := if ut > 0 then divR .down (gross * 1000) ut else 0
  let tm := taxMilliUT netMilli cargas
  { netMilliUT := netMilli, taxMilliUT := tm, taxBs := if ut > 0 then divR .halfUp (tm * ut) 1000 else 0 }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let ut := (c.int? "veUT").getD 0
  let kids : Int := c.childrenUnder 18
  -- the first adult claims the children and the spouse (art. 59 Paragrafo Primero: only one spouse claims family
  -- charges when they file separately; the spouse rebate is not available then)
  let ps := ((c.adults.zip (sh c.rentalIncome)).zipIdx).map fun ((a, r), k) =>
    person a.wages a.selfEmployment r ut (if k == 0 then kids else 0)
  let unsup :=
    (if ut ≤ 0 then ["veUT (2025 value of the unidad tributaria, SENIAT providencia) not supplied and not reached: tax cannot be expressed in bolivares; incomeTax = 0"] else []) ++
    ["employee contributions (Seguro Social Obligatorio, Regimen Prestacional de Empleo, FAOV) not reached; employeeSocial = 0",
     "desgravamen unico (art. 58) used; the itemised desgravamenes of art. 57 not modelled",
     "spouses file separately; the spouse rebate (art. 59 num. 1) is not available then (Paragrafo Primero)"] ++
    (if c.interest != 0 || c.dividends != 0 || c.capitalGains != 0 then ["capital income: proportional regimes (dividends 34 %, etc.) not read; ignored"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) || c.rentalIncome != 0 then ["selfEmployment/rent: gross taxed with wages; costs not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pensions: not modelled"] else [])
  Out.make c "VE" "VES" (sumInts (ps.map (·.taxBs)))
    (detail := [Out.d "taxableIncomeMilliUT" (sumInts (ps.map (·.netMilliUT))),
                Out.d "taxMilliUT" (sumInts (ps.map (·.taxMilliUT))), Out.d "veUT" ut])
    (unsupported := unsup)

def country : Country :=
  { code := "VE", name := "Venezuela (ISLR, persona natural residente; Tarifa No. 1 en U.T.)", currency := "VES",
    year := "2025", compute := out }

/- 1.774 U.T. of income: 1.000 U.T. taxable at 6 % = 60 U.T., less the 10 U.T. rebate = 50 U.T. -/
#guard taxMilliUT 1774000 0 == 50000
/- Up to 774 + 166,67 U.T. the rebate cancels the tax (10 U.T. / 6 %). -/
#guard taxMilliUT (774000 + 166666) 0 == 0

end VeTax
