import TaxKernel.World

/-!
# Chile 2025 (año comercial 2025, año tributario 2026): parameters with their dated sources

Statute (Global law, corpus `chile/national/acts`, publisher Biblioteca del Congreso Nacional, LeyChile; texts as in
force on 2025-07-01 saved in `../src/`):
* LIR = DL 824, Ley sobre Impuesto a la Renta (https://www.bcn.cl/leychile/navegar?idNorma=6368). Art. 42, 43, 47,
  50, 52, 54, 55 bis, 56, 57, 75 as in force on 2025-07-01 (last changed by Ley 21.210, in force 2020-02-24; art. 56
  next changed only on 2027-01-01 by Ley 21.850).
* DL 3.500 art. 16, 17, 84, 85 (pensions, health); Ley 19.728 art. 5, 6 (seguro de cesantía).
Official secondary (amounts the statute delegates; flagged `"source": "official secondary"` in summary.json):
* UTM / UTA and IPC 2025: Servicio de Impuestos Internos, https://www.sii.cl/valores_y_fechas/utm/utm2025.htm (and
  utm2024.htm for the December 2024 IPC), fetched 2026-11-20.
* UF daily values: SII, https://www.sii.cl/valores_y_fechas/uf/uf2025.htm and uf2024.htm.
* Topes imponibles 2025: Superintendencia de Pensiones, Resolución exenta N° 48 de 2025 (87,8 UF, AFP and health)
  and N° 47 de 2025 (131,8 UF, seguro de cesantía), Diario Oficial N° 44.051, 17-01-2025, CVE 2596352 / 2596353.
-/

namespace ClTax
open TaxKernel

/-- UTM of each month of 2025 (pesos), SII utm2025.htm: Enero 67.429 … Diciembre 69.542. -/
def utm : List Int := [67429, 67294, 68034, 68306, 68648, 68785, 68923, 68647, 69265, 69265, 69542, 69542]

/-- UTA at the close of 2025 = UTM of December × 12 (SII: "UTA = Unidad Tributaria Anual (UTM x 12)"; LIR art. 47
and 52 use the December unit): 834.504. -/
def utaDec : Int := 69542 * 12

/-- UF on the last day of the month before each month of 2025 (centavos): 31-12-2024 … 30-11-2025 (SII uf2024/uf2025).
Ley 19.728 art. 6: "unidades de fomento consideradas al último día del mes anterior al pago"; DL 3.500 art. 84: "valor
de la unidad de fomento al último día del mes anterior al pago de la cotización". -/
def ufPrev : List Int := [3841669, 3838441, 3864794, 3889411, 3907541, 3918945, 3926707, 3917901, 3938307, 3948565,
  3959767, 3964359]

/-- IPC points (base 2023 = 100, hundredths) at the end of the month before each month of 2025 (Dec 2024 … Nov 2025),
SII utm2024.htm / utm2025.htm, and November 2025 (109,47). -/
def ipcPrev : List Int := [10562, 10674, 10716, 10770, 10791, 10812, 10768, 10862, 10866, 10914, 10919, 10947]
def ipcNov : Int := 10947

/-! ## LIR art. 43 N° 1 and art. 52: one scale, in UTM (monthly) or UTA (annual) -/

/-- LIR art. 43 N° 1 (and art. 52 in UTA): exempt to 13,5 units; "Sobre la parte que exceda de 13,5 y no sobrepase las
30 ..., 4%; ... 30 y ... 50, 8%; ... 50 y ... 70, 13,5%; ... 70 y ... 90, 23%; ... 90 y ... 120, 30,4%; ... 120 y ...
310, 35%; y ... de 310 ..., 40%". Thresholds in tenths of a unit. -/
def scaleTenths : List (Int × Int) :=
  [(0, 0), (135, 400), (300, 800), (500, 1350), (700, 2300), (900, 3040), (1200, 3500), (3100, 4000)]

/-- The scale in pesos for a unit value (`Schedule.ofUnits`, thresholds in tenths of a unit, rounded half-up to the
peso: reading, the statute gives no rounding). -/
def scale (unitValue : Int) : Schedule := Schedule.ofUnits scaleTenths .halfUp 10 unitValue

/-! ## Contributions (employee) -/

/-- DL 3.500 art. 17: "el 10 por ciento de sus remuneraciones y rentas imponibles". -/
def rateAFP : Int := 1000
/-- DL 3.500 art. 84: "una cotización del siete por ciento de sus remuneraciones imponibles". -/
def rateHealth : Int := 700
/-- Ley 19.728 art. 5 a): "Un 0,6% de las remuneraciones imponibles, de cargo del trabajador con contrato de duración
indefinida". -/
def rateAFC : Int := 60
/-- DL 3.500 art. 85: pensions "afectas a una cotización uniforme del siete por ciento en la parte que no exceda de
sesenta Unidades de Fomento". -/
def ratePensionHealth : Int := 700
def pensionCapUFTenths : Int := 600

/-- Res. ex. SP N° 48 de 2025: "desde el 1 de enero de 2025, el límite máximo imponible ... será de 87,8 Unidades de
Fomento" (tenths of a UF). Check: Res. N° 224/2024 84,3 UF × (1 + 4,1 %) = 87,76 → 87,8 (`tope_check`). -/
def topeUFTenths : Int := 878
/-- Res. ex. SP N° 47 de 2025: seguro de cesantía "131,8 Unidades de Fomento" from 1 January 2025 (126,6 × 1,041 =
131,79, provisional INE index); Res. ex. SP N° 253 de 2025 (Diario Oficial N° 44.078, 18-02-2025, CVE 2610237):
"desde el 1 de febrero de 2025, el límite máximo imponible reajustado ... será de 131,9 Unidades de Fomento" (INE
oficio N° 161: 4,2 %, definitive; 126,6 × 1,042 = 131,92). Res. ex. N° 254 de 2025 (CVE 2610238) keeps the AFP/health
tope at 87,8 UF from 1 February (84,3 × 1,042 = 87,84). -/
def topeAFCUFTenths : Int := 1318
def topeAFCUFTenthsFeb : Int := 1319
def topeAFCOfMonth (i : Nat) : Int := if i == 0 then topeAFCUFTenths else topeAFCUFTenthsFeb

/-! ## Annual items -/

/-- LIR art. 50: presumed expenses "un 30% de los ingresos brutos anuales ... no podrá exceder de la cantidad de 15
unidades tributarias anuales". -/
def presumedRate : Int := 3000
def presumedCapUTA : Int := 15
/-- LIR art. 57: interest (art. 20 N° 2) exempt from global complementario when "no exceda en conjunto de veinte
unidades tributarias mensuales vigentes en el mes de diciembre" and the other income is only art. 22 / 42 N° 1. -/
def interestExemptUTM : Int := 20

end ClTax
