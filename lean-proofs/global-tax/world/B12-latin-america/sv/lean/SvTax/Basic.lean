import TaxKernel.World

/-!
# El Salvador 2025: Impuesto sobre la Renta of a domiciled natural person (Ley de Impuesto sobre la Renta, D.L. 134/1991)

Sources (mh.gob.sv and transparenciafiscal.gob.sv answer a Cloudflare challenge to scripts; Internet Archive copies
of the Ministry's own files were used; not bypassed):
* Decreto Ejecutivo No. 10 of 30 April 2025 "Tablas de retencion del Impuesto sobre la Renta"
  (`transparenciafiscal.gob.sv/downloads/pdf/700-DGII-DC-2025-01.pdf`, capture 2025-05-22, 8 scanned pages, OCR checked
  against the page images), Considerando I: "mediante Decreto Legislativo No. 293, de fecha 30 de abril de 2025, se
  introdujo reforma al articulo 37 ... modificacion de los Tramos I y II de la Tabla para el Calculo del Impuesto de
  Personas Naturales ... se amplio la base exenta ... hasta ... ($6,600.00) de ingresos anuales"; art. 1 f) 2) annual
  recalculation table (December), "guardando consonancia con lo dispuesto en el articulo 37": I 0,01-6.600,00 sin
  retencion; II 6.600,01-10.742,86 10 % sobre el exceso de 6.600,00 mas 212,12; III 10.742,87-24.457,14 20 % sobre el
  exceso de 10.742,86 mas 720,00; IV 24.457,15 en adelante 30 % sobre el exceso de 24.457,14 mas 3.462,86;
  art. 1 e): the deduction of US$1.600 of LISR art. 29 num. 7 for "personas naturales asalariadas cuyo monto anual sea
  igual o inferior a nueve mil cien dolares (US$9,100.00)"; d): labour social-security contributions and pension
  contributions are not taxable remuneration.
* LISR (MH consolidated text DC5101, capture 2024-07-24, reforms to 2007, in colones) for the structure of art. 37.
The text of D.L. 293/2025 itself was not reached: the 2025 amounts are official secondary (access B).
Amounts in cents.
-/

namespace SvTax
open TaxKernel

/-- Art. 37 as reformed by D.L. 293/2025, from the Decreto Ejecutivo No. 10 annual table (cents): "sobre el exceso de"
+ "mas cuota fija de". -/
def art37 : List CumRow :=
  [⟨0, 0, 0⟩, ⟨660000, 21212, 1000⟩, ⟨1074286, 72000, 2000⟩, ⟨2445714, 346286, 3000⟩]
/-- LISR art. 29 num. 7 (as quoted by D.E. 10 art. 1 e): US$ 1.600 for salaried persons with annual pay at most
US$ 9.100. -/
def wageDeduction : Int := 160000
def wageDeductionLimit : Int := 910000

/-- The table with its "Desde ... Hasta" bounds: each tramo starts one cent above the previous "Hasta", so at exactly
US$ 10.742,86 tramo II still applies (cents; the fixed 212,12 is due from the first cent above US$ 6.600,00). -/
def tax37 (b : Int) : Int :=
  let ticks :=
    if b ≤ 660000 then 0
    else if b ≤ 1074286 then 21212 * BP + 1000 * (b - 660000)
    else if b ≤ 2445714 then 72000 * BP + 2000 * (b - 1074286)
    else 346286 * BP + 3000 * (b - 2445714)
  divR .halfUp ticks BP

structure Person where
  base : Int
  tax : Int
  deriving Repr

/-- `contrib` = the person's labour social-security and pension contributions (annual, dollars). -/
def person (wage contrib : Int) : Person :=
  let w := pos wage * 100
  let afterContrib := pos (w - pos contrib * 100)
  let ded := if wage > 0 && w ≤ wageDeductionLimit then wageDeduction else 0
  let base := pos (afterContrib - ded)
  { base, tax := divR .halfUp (tax37 base) 100 }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  /- W5 review pass 2 (sweep P2-6): the household-total employee contribution is allotted to the adults in
  proportion to their wages (each person's own contribution is deducted from that person's income); it was halved, which
  gave a one-earner couple half its deduction. Halves only when nobody has wages. -/
  let socW : List Int := c.adults.map (fun a => pos a.wages)
  let wsumS := sumInts socW
  let socBy (x : Int) (i : Nat) : Int :=
    if n ≤ 1 then x else if wsumS = 0 then (if i = 0 then half1 x else half2 x)
    else if i = 0 then x - divR .down (x * socW.getD 1 0) wsumS else divR .down (x * socW.getD 1 0) wsumS
  let shW := fun (x : Int) => if n == 2 then [socBy x 0, socBy x 1] else [x]
  let contrib := (c.int? "svEmployeeContrib").getD 0
  let ps := (c.adults.zip (shW contrib)).map fun (a, k) => person a.wages k
  let unsup :=
    ["employee ISSS and AFP contributions (not taxable, D.E. 10 art. 1 d) not reached: pass svEmployeeContrib (annual household total) or the base is overstated; employeeSocial = that input",
     "2025 art. 37 amounts from the executive withholding decree's annual table (official secondary); D.L. 293/2025 not reached; whether the 1991 cap of 25 % of renta imponible (art. 37 last paragraph in the 2007 consolidation) survives was not verified: not applied",
     "D.E. 10 applies from May 2025; the model applies the reformed table to the whole year",
     "medical and school-fee deductions (LISR art. 33) for incomes above US$ 9.100 not modelled"] ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: not modelled; ignored"] else []) ++
    (if c.interest != 0 || c.dividends != 0 || c.rentalIncome != 0 || c.capitalGains != 0 then ["capital income: final withholdings not read; ignored"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pensions: not modelled"] else [])
  Out.make c "SV" "USD" (sumInts (ps.map (·.tax))) (employeeSocial := pos contrib)
    (detail := [Out.d "taxableIncome" (divR .down (sumInts (ps.map (·.base))) 100)])
    (unsupported := unsup)

def country : Country :=
  { code := "SV", name := "El Salvador (Impuesto sobre la Renta, personas naturales asalariadas)", currency := "USD",
    year := "2025", compute := out }

#guard tax37 660000 == 0
#guard tax37 660001 == 21212
#guard tax37 2445714 == 346286

end SvTax
