import TaxKernel.World

/-!
# Colombia 2025 (año gravable 2025): parameters with their dated sources

Statute: Estatuto Tributario (ET, Decreto 624 de 1989). Text as in force on 2025-07-01 from Global law (corpus
`colombia/national/acts`, publisher Secretaría General del Senado, basedoc), checked against the Senate's official
compilation http://www.secretariasenado.gov.co/senado/basedoc/estatuto_tributario.html (pages pr008, pr010, pr014,
pr015; the art. 241 table is the image `graficas/estatuto_tributario_obj_20.gif`, read as an image). Ley 100 de 1993
(art. 18, 20, 204) from the same corpus.
Official secondary: UVT 2025 = DIAN Resolución 000193 de 2024 art. 1 (normograma.dian.gov.co, compilación,
`resolucion_dian_0193_2024.htm`).
Not reached: the 2025 minimum wage decree (SMMLV), and the 2008 decree that used Ley 100 art. 20 inc. 4's authority to
add one point to the pension rate (see `pensionRateEmployee`).
-/

namespace CoTax
open TaxKernel

/-- DIAN Res. 000193 de 2024 art. 1: "Fijar en cuarenta y nueve mil setecientos noventa y nueve pesos ($49.799) el
valor de la Unidad de Valor Tributario (UVT) que regirá durante el año 2025". -/
def uvt : Int := 49799

/-- ET art. 241 (Ley 2010 de 2019 art. 34), table as printed: "Rangos en UVT ... >1090 1700 19% (Base Gravable en UVT
menos 1090 UVT) x 19%; >1700 4100 28% (...) x 28% + 116 UVT; >4100 8670 33% ... + 788 UVT; >8670 18970 35% ... +
2296 UVT; >18970 31000 37% ... + 5901 UVT; >31000 En adelante 39% ... + 10352 UVT". In UVT. -/
def art241 : List CumRow :=
  [⟨0, 0, 0⟩, ⟨1090, 0, 1900⟩, ⟨1700, 116, 2800⟩, ⟨4100, 788, 3300⟩, ⟨8670, 2296, 3500⟩, ⟨18970, 5901, 3700⟩,
   ⟨31000, 10352, 3900⟩]

/-- The bands the table is built from (same thresholds and rates). -/
def art241Bands : Schedule :=
  Schedule.ofList [(0, 0), (1090, 1900), (1700, 2800), (4100, 3300), (8670, 3500), (18970, 3700), (31000, 3900)]

/-- ET art. 206 num. 10 (Ley 2277 de 2022 art. 2): "El veinticinco por ciento (25%) del valor total de los pagos
laborales limitada anualmente a setecientos noventa (790) UVT", computed after INCR, deductions and other exempt income. -/
def exempt25Rate : Int := 2500
def exempt25CapUVT : Int := 790

/-- ET art. 336 num. 3 (Ley 2277 de 2022 art. 7): exempt income and deductions "siempre que no excedan el cuarenta
(40%) del resultado del numeral anterior, que en todo caso no puede exceder de mil trescientas cuarenta (1.340) UVT
anuales"; "en adición al límite ..., setenta y dos (72) UVT por dependiente hasta un máximo de cuatro (4)". -/
def limitRate : Int := 4000
def limitCapUVT : Int := 1340
def depExtraUVT : Int := 72
def depExtraMax : Nat := 4

/-- ET art. 387 inc. 2 (Ley 2411 de 2024): dependants "hasta el 10% del total de los ingresos brutos provenientes de la
relación laboral ... hasta un máximo de treinta y dos (32) UVT mensuales"; par. 2 num. 1: "Los hijos del contribuyente
que tengan hasta 18 años de edad". -/
def depRate : Int := 1000
def depCapUVTMonth : Int := 32
def depChildMaxAge : Nat := 18

/-- ET art. 206 num. 5: pensions "gravadas sólo en la parte del pago mensual que exceda de 1.000 UVT". -/
def pensionExemptUVTMonth : Int := 1000

/-- ET art. 254-1 (Ley 2277 art. 5): dividend discount "(Renta líquida cedular de dividendos y participaciones en UVT
menos 1.090 UVT) x 19%". -/
def divDiscountFromUVT : Int := 1090
def divDiscountRate : Int := 1900

/-- Ley 100 art. 20 (Ley 797 de 2003 art. 7): rate 13,5 % "+1 % 2004, +0,5 % 2005, +0,5 % 2006" = 15,5 %; inc. 4 lets
the Government add one more point from 2008 by decree (not reached). "Los empleadores pagarán el 75% de la cotización
total y los trabajadores el 25% restante": employee 25 % × 15,5 % = 3,875 % (387,5 bp: kept in tenths of a bp). -/
def pensionRateEmployeeTenthBp : Int := 3875
/-- Ley 100 art. 204 (Ley 2294 de 2023): "La cotización a cargo del empleador será del 8.5% y a cargo del empleado del
4%". Pensioners: "La cotización mensual al régimen contributivo de salud de los pensionados será del 12%". -/
def healthRateEmployee : Int := 400
def healthRatePensioner : Int := 1200

end CoTax
