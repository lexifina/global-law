import VeGlobal.Pit

/-!
# Venezuela 2025: impuesto sobre la renta of companies (1200)

Sources:
* Decreto con Rango, Valor y Fuerza de Ley de Reforma de la Ley de Impuesto sobre la Renta, G.O. 6.210 Ext. of 30 Dec
  2015 (reprinted law; OCR held by the 1.x builder `world/B12-latin-america/ve/src/ocr/page013.txt`) **art. 52**: the
  enriquecimiento global neto of companies "se gravará ... con base en la siguiente Tarifa expresada en unidades
  tributarias (U.T.): Tarifa N° 2: Por la fracción comprendida hasta 2.000,00 15% | Por la fracción que exceda de
  2.000,00 hasta 3.000,00 22% | Por la fracción que exceda de 3.000,00 34%"; Parágrafo Primero: banking, financial and
  insurance income 40 % (not modelled: the sector is not an input).
* Unit: Código Orgánico Tributario (G.O. 6.507 Ext., 29 Jan 2020) art. 3: "En los casos de tributos que se liquiden por
  períodos anuales, la unidad tributaria aplicable será la que esté vigente al cierre del ejercicio fiscal respectivo";
  SENIAT Providencia in G.O. 43.140 of 2 Jun 2025 "reajusta el valor de la Unidad Tributaria de nueve bolívares (Bs.
  9,00) a cuarenta y tres bolívares (Bs. 43,00)" (gazette index page; the Providencia's own page is an image): for a
  calendar 2025 year U.T. = Bs. 43, so the bands end at Bs. 86,000 and Bs. 129,000.
Grade A. Withholding on payments abroad (Decreto 1.808 de retenciones) and the 34 % dividend tax of the ISLR were not
modelled.
-/

namespace VeGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon VeGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre la renta (compañías)", sched := Schedule.ofList [(0, 1500), (86000, 2200), (129000, 3400)] }

def citStatute : String := "Ley de ISLR (Decreto de reforma, G.O. 6.210 Ext., 30 Dec 2015) art. 52 Tarifa N° 2 (15 % to 2,000 U.T., 22 % to 3,000 U.T., 34 % above); U.T. Bs. 43 (G.O. 43.140, in force at the close of 2025: COT art. 3)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [] }

def citF : Family := corpFamily "1200 Impuesto sobre la renta (compañías)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "banking, financial and insurance income 40 % (ISLR art. 52 Par. 1) not modelled; withholding (Decreto 1.808) and dividend tax not modelled"

#guard regime.citTax { profit := 1000000 } == 318500
#guard regime.citTax { profit := 50000 } == 7500

end VeGlobal.Corporate
