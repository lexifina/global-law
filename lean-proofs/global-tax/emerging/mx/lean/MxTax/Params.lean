import MxTax.Basic

/-!
# Parameters for 2025 (ejercicio fiscal = calendar year 2025), each with its source

Sources (official):
* LISR = Ley del Impuesto sobre la Renta (DOF 11-12-2013, last amended for these articles DOF 12-11-2021), text from
  Cámara de Diputados, LeyesBiblio (http://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf) via the Global law record
  `mexico/national/acts/ley/2013/ley-del-impuesto-sobre-la-renta/` (the record drops the printed tables).
* A8-2025 = Anexo 8 de la Resolución Miscelánea Fiscal para 2025 (DOF 30-12-2024; signed 20-12-2024),
  https://sidof.segob.gob.mx/notas/5746354 (getDoc/5746354). A8-2026 = Anexo 8 RMF 2026 (DOF 28-12-2025),
  https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rmf/anexos/Anexo-8-RMF-2026_DOF-28122025.pdf,
  whose section C.I repeats the 2025 annual tarifa identically.
* SE-2024 = "Decreto que otorga el subsidio para el empleo", DOF 01-05-2024,
  https://dof.gob.mx/nota_detalle.php?codigo=5725287&fecha=01/05/2024 ; SE-2025 = "Decreto por el que se modifica el
  diverso que otorga el subsidio para el empleo", DOF 31-12-2024,
  https://dof.gob.mx/nota_detalle.php?codigo=5746529&fecha=31/12/2024 .
* UMA: INEGI notice DOF 10-01-2025 (daily 113.14, monthly 3,439.46, annual 41,273.52, in force 1-02-2025), method
  (monthly = daily × 30.4, annual = monthly × 12) restated in INEGI's notice DOF 09-01-2026,
  https://sc.inegi.org.mx/repositorioNormateca/UMA.pdf . January 2025 uses the 2024 UMA (108.57 daily, 3,300.53
  monthly): Ley para Determinar el Valor de la UMA art. 5 (annual value "entrará en vigor a partir del 1 de febrero"),
  as SE-2025's considerandos and transitorio segundo say.
* LSS = Ley del Seguro Social (DOF 21-12-1995), arts. 25, 28, 36, 106, 107, 147, 168, transitorio décimo noveno.
* CFF = Código Fiscal de la Federación art. 20.
Convention notes (not statute): sub-centavo amounts are rounded half up; the statute's "salario mínimo general ...
elevado al año / veces" used as a unit of account is read as the UMA (Decreto de desindexación del salario mínimo,
DOF 27-01-2016, transitorios tercero y cuarto).
-/

namespace MxTax
open TaxKernel

/-! ## UMA -/

/-- UMA daily 2025 (INEGI, DOF 10-01-2025), in force 1-02-2025 to 31-01-2026: 113.14. -/
def umaDaily : Int := 11314
/-- UMA monthly 2025 = 113.14 × 30.4 = 3,439.46 (INEGI). -/
def umaMonthly : Int := 343946
/-- UMA annual 2025 = 3,439.46 × 12 = 41,273.52 (INEGI). -/
def umaAnnual : Int := 4127352
/-- UMA daily 2024 (in force in January 2025): 108.57. -/
def umaDaily2024 : Int := 10857
/-- UMA monthly 2024 = 108.57 × 30.4 = 3,300.53 (SE-2025 considerandos: 11.82% of it "representó un monto mensual
de $390.00"). -/
def umaMonthly2024 : Int := 330053
/-- Days of 2025 on the 2024 UMA (January) and on the 2025 UMA. -/
def daysJan : Int := 31
def daysFebDec : Int := 334

/-- Salario mínimo general 2025 (outside the northern border zone): 278.80 daily (SE-2025 considerandos, citing
CONASAMI Boletín 056/2024). -/
def salarioMinimo : Int := 27880

/-! ## LISR art. 152 annual tarifa 2025 (A8-2025 C.II = A8-2026 C.I) -/

/-- "Tarifa para el cálculo del impuesto correspondiente al ejercicio de 2025 a que se refieren los artículos 97 y
152 de la Ley del ISR" (límite inferior, cuota fija, %): 0.01 / 0.00 / 1.92 … 4,511,707.38 / 1,414,947.85 / 35.00. -/
def tarifa152 : List Row := [
  ⟨1, 0, 192⟩, ⟨895250, 17188, 640⟩, ⟨7598456, 446194, 1088⟩, ⟨13353608, 1072355, 1600⟩,
  ⟨15522981, 1419454, 1792⟩, ⟨18585258, 1968213, 2136⟩, ⟨37483789, 6004940, 2352⟩,
  ⟨59079600, 11084274, 3000⟩, ⟨112792685, 27198199, 3200⟩, ⟨150390247, 39229417, 3400⟩,
  ⟨451170738, 141494785, 3500⟩]

/-! ## LISR art. 96 monthly tarifa 2025 (A8-2025 B.V) -/

/-- "Tarifa aplicable durante 2025 para el cálculo de los pagos provisionales mensuales a que se refieren los
artículos 96 de la Ley del ISR y 175 de su Reglamento": 0.01 / 0.00 / 1.92 … 375,975.62 / 117,912.32 / 35.00. -/
def tarifa96 : List Row := [
  ⟨1, 0, 192⟩, ⟨74605, 1432, 640⟩, ⟨633206, 37183, 1088⟩, ⟨1112802, 89363, 1600⟩,
  ⟨1293583, 118288, 1792⟩, ⟨1548772, 164018, 2136⟩, ⟨3123650, 500412, 2352⟩,
  ⟨4923301, 923689, 3000⟩, ⟨9399391, 2266517, 3200⟩, ⟨12532521, 3269118, 3400⟩,
  ⟨37597562, 11791232, 3500⟩]

/-! ## Subsidio para el empleo 2025 (SE-2024 as amended by SE-2025) -/

/-- SE-2025 art. Segundo: monthly income "que sirvan de base para calcular el impuesto ... no excedan de
$10,171.00". -/
def subsidyCap : Int := 1017100
/-- SE-2025: "multiplicar el valor mensual de la Unidad de Medida y Actualización por 13.8%" (bp). -/
def subsidyRate : Int := 1380
/-- SE-2025 transitorio segundo: January 2025 uses 14.39% of the (2024) monthly UMA. -/
def subsidyRateJan : Int := 1439
/-- The monthly subsidy, centavos: Feb–Dec 13.8% × 3,439.46 = 474.65; January 14.39% × 3,300.53 = 474.95. -/
def subsidyMonth (m : Nat) : Int :=
  if m = 1 then mulDivHU umaMonthly2024 subsidyRateJan BP else mulDivHU umaMonthly subsidyRate BP

/-! ## LISR art. 93: exemptions of wage income -/

/-- Art. 93 fr. XIV: gratificación anual "hasta el equivalente del salario mínimo general ... elevado a 30 días";
primas vacacionales and PTU "hasta por el equivalente a 15 días de salario mínimo" each (read as UMA). Days. -/
def aguinaldoExemptDays : Int := 30
def primaExemptDays : Int := 15
/-- Art. 93 fr. IV: pensions exempt while "su monto diario no exceda de quince veces el salario mínimo". -/
def pensionExemptDays : Int := 15
/-- Art. 93 penúltimo párrafo: previsión social limited when salary + exemption exceed "siete veces el salario mínimo
general ... elevado al año", then exempt "hasta de un salario mínimo general ... elevado al año". -/
def psLimitUma : Int := 7

/-! ## LISR art. 151: deducciones personales -/

/-- Art. 151 último párrafo: total "no podrá exceder de la cantidad que resulte menor entre cinco veces el valor anual
de la Unidad de Medida y Actualización, o del 15% del total de los ingresos del contribuyente". -/
def dedCapUma : Int := 5
def dedCapPct : Int := 1500
/-- Art. 151 fr. III: donativos up to "7% de los ingresos acumulables ... del ejercicio inmediato anterior". -/
def donPct : Int := 700
/-- Art. 151 fr. V: aportaciones complementarias de retiro "hasta el 10% de los ingresos acumulables ... sin que
dichas aportaciones excedan del equivalente a cinco salarios mínimos generales ... elevados al año". -/
def pprPct : Int := 1000
def pprCapUma : Int := 5

/-! ## Investment income (LISR Título IV caps. III, VI, VIII, IX; art. 129) -/

/-- Art. 140: "tasa adicional del 10% sobre los dividendos ... El pago realizado conforme a este párrafo será
definitivo"; credit of the company's tax "aplicando la tasa del artículo 9 ... al resultado de multiplicar el
dividendo ... por el factor de 1.4286". -/
def divAddRate : Int := 1000
def grossUpNum : Int := 14286
def grossUpDen : Int := 10000
/-- LISR art. 9: "la tasa del 30%". -/
def citRate : Int := 3000
/-- Art. 129: "aplicando la tasa del 10% a las ganancias obtenidas en el ejercicio" (listed shares). -/
def cgRate : Int := 1000
/-- Art. 115 (arrendamiento): optional deduction of 35% of income instead of actual expenses (deducción ciega). -/
def rentBlindPct : Int := 3500

/-! ## RESICO personas físicas (LISR arts. 113-E, 113-F) -/

/-- Art. 113-F "TABLA ANUAL": Hasta 300,000.00 1.00% … Hasta 3,500,000.00 2.50% (upper limit in centavos, bp). -/
def resicoAnnual : List (Int × Int) :=
  [(30000000, 100), (60000000, 110), (100000000, 150), (250000000, 200), (350000000, 250)]
/-- Art. 113-E: the section stops applying when income "excedan de tres millones quinientos mil pesos". -/
def resicoLimit : Int := 350000000

/-! ## IMSS employee quotas (LSS), rates per 100,000 -/

/-- LSS art. 106 fr. II: "otra adicional obrera del dos por ciento" on SBC above three times the minimum (UMA),
reduced by "dieciséis centésimas de punto porcentual" each 1 July 1998–2007 (transitorio décimo noveno): 0.40%. -/
def rExcess : Int := 400
/-- LSS art. 107 fr. II: prestaciones en dinero "veinticinco por ciento" of 1% = 0.25%. -/
def rDinero : Int := 250
/-- LSS art. 25: gastos médicos de pensionados, "a los trabajadores el cero punto trescientos setenta y cinco por
ciento". -/
def rPensionados : Int := 375
/-- LSS art. 147: invalidez y vida, trabajadores "cero punto seiscientos veinticinco por ciento". -/
def rInvalidez : Int := 625
/-- LSS art. 168 fr. II b): cesantía en edad avanzada y vejez, "uno punto ciento veinticinco por ciento". -/
def rCesantia : Int := 1125
/-- LSS art. 28: SBC "límite superior el equivalente a veinticinco veces" (UMA); art. 106 fr. II: "tres veces". -/
def sbcCapUma : Int := 25
def excessUma : Int := 3

/-! ## Tax year 2024 (tests round 2, `~/cmp20/improve-emerging/IMPROVE.md`)

* Tarifas: A8-2024 = Anexo 8 RMF 2024 (DOF 29-12-2023, `refs/Anexo_8_RMF2024-29122023.pdf`, text `refs/a24.txt`): C.II
  "Tarifa para el cálculo del impuesto correspondiente al ejercicio de 2024 a que se refieren los artículos 97 y 152"
  and B.V (monthly, art. 96) have exactly the rows of the 2025 tables above (0.01 / 0.00 / 1.92; 8,952.50 / 171.88 /
  6.40; …; 4,511,707.38 / 1,414,947.85 / 35.00 and 746.05 / 14.32 / 6.40; …), so `tarifa152` and `tarifa96` serve 2024.
* UMA: 2024 daily 108.57, monthly 3,300.53 (SE-2025 considerandos, as above; annual 3,300.53 × 12 = 39,606.36, INEGI's
  method), in force from 1-02-2024; January 2024 uses the 2023 UMA: INEGI, DOF 10-01-2023
  (dof.gob.mx/nota_detalle.php?codigo=5676670, `refs/years/dof_uma_2023.html`): "el valor diario … es de $103.74 …, el
  mensual es de $3,153.70 … y el valor anual $37,844.40".
* Subsidio para el empleo: January–April 2024 the table of the 2013 decree (DOF 11-12-2013, art. Décimo transitorio), as
  printed in A8-2024 ("Tabla del subsidio para el empleo aplicable a la tarifa de la fracción V del apartado B":
  0.01–1,768.96 → 407.02 … 7,113.91–7,382.33 → 217.61; above → 0.00); from 1 May 2024 SE-2024 (DOF 01-05-2024, art.
  Segundo: monthly base "no excedan de $9,081.00", subsidy "valor mensual de la Unidad de Medida y Actualización por
  11.82%", Transitorio Primero "entra en vigor el 1 de mayo de 2024"); art. Tercero (annual: subtract the sum of the
  monthly subsidies, nothing paid out) applied to the whole year. NOT modelled: the 2013 decree's payment in cash of a
  January–April subsidy larger than the month's tax (the output says so when it can matter).
* Salario mínimo general 2024 (LSS art. 36 only): 248.93 a day — CONASAMI resolution, DOF 12-12-2023, codigo 5711066
  (`refs/years/dof_conasami_2024.txt`: "para el Resto del País el salario mínimo general será de 248.93 pesos diarios", round 7); it only decides whether a minimum-wage worker's quota is paid by the
  employer.
* Not changed for 2024: IMSS rates (LSS), the art. 93 and 151 rules, LFT art. 76 (12 days since DOF 27-12-2022). The
  model keeps its 365-day year (2024 had 366 days: W/365 a day, 31 days at the January UMA and 334 at the new one). -/

structure MxYear where
  year : Int
  umaDaily : Int
  umaMonthly : Int
  umaAnnual : Int
  umaDailyPrev : Int
  umaMonthlyPrev : Int
  salMin : Int
  deriving Repr

def mxY2025 : MxYear :=
  { year := 2025, umaDaily := umaDaily, umaMonthly := umaMonthly, umaAnnual := umaAnnual,
    umaDailyPrev := umaDaily2024, umaMonthlyPrev := umaMonthly2024, salMin := salarioMinimo }

def mxY2024 : MxYear :=
  { year := 2024, umaDaily := 10857, umaMonthly := 330053, umaAnnual := 3960636,
    umaDailyPrev := 10374, umaMonthlyPrev := 315370, salMin := 24893 }


/-- A8-2024: the monthly subsidy table of the 2013 decree (upper limit of the monthly base, subsidy), centavos. -/
def oldSubsidyTable : List (Int × Int) :=
  [(176896, 40702), (265338, 40683), (347284, 40662), (353787, 39277), (444615, 38246), (471718, 35423),
   (533542, 32487), (622467, 29463), (711390, 25354), (738233, 21761)]

def oldSubsidy (base : Int) : Int :=
  match oldSubsidyTable.find? (fun r => decide (base ≤ r.1)) with
  | some r => r.2
  | none => 0

/-- SE-2024 art. Segundo: "no excedan de $9,081.00". -/
def subsidyCap2024 : Int := 908100
def subsidyRate2024 : Int := 1182

/-- The subsidy that corresponded in month `m` of 2024 for a month's base `base` (centavos). -/
def subsidy2024 (m : Nat) (base : Int) : Int :=
  if m ≤ 4 then oldSubsidy base
  else if base ≤ subsidyCap2024 then mulDivHU mxY2024.umaMonthly subsidyRate2024 BP else 0

theorem uma_annual_2024 : mxY2024.umaMonthly * 12 = mxY2024.umaAnnual := by decide
theorem subsidy2024_may : subsidy2024 5 908100 = 39012 ∧ subsidy2024 5 908101 = 0 ∧ subsidy2024 1 738233 = 21761 ∧
    subsidy2024 1 738234 = 0 := by decide

/-! ## Tax year 2023 (tests round 2)

* Tarifa: A8-2024 section C ("Tarifa para el cálculo del impuesto correspondiente a los ejercicios 2023 y 2024", C.I for
  2023) prints the same rows as 2024 and 2025 (the art. 152 último párrafo update of 2023); the monthly B tarifa of 2023 is
  the same as 2024's: Anexo 8 RMF 2023 (DOF 27-12-2022, codigo 5675764, PDF `dof.gob.mx/2022/SHCP/SHCP_271222_01.pdf`,
  text in `~/cmp20/emerging/mx/refs/dof/rmf2023.txt`, round 10), B.5 "Tarifa aplicable durante 2023 para el cálculo de
  los pagos provisionales mensuales": 0.01 / 0.00 / 1.92; 746.05 / 14.32 / 6.40; 6,332.06 / 371.83 / 10.88; 11,128.02 /
  893.63 / 16.00; 12,935.83 / 1,182.88 / 17.92; 15,487.72 / 1,640.18 / 21.36; 31,236.50 / 5,004.12 / 23.52; 49,233.01 /
  9,236.89 / 30.00; 93,993.91 / 22,665.17 / 32.00; 125,325.21 / 32,691.18 / 34.00; 375,975.62 / 117,912.32 / 35.00 (=
  `tarifa96`), and its subsidy table (0.01–1,768.96: 407.02 … 7,382.34 en adelante: 0.00) is the 2013 table
  (`oldSubsidyTable`).
* UMA: 103.74 / 3,153.70 / 37,844.40 from 1-02-2023 (INEGI, DOF 10-01-2023, `refs/years/dof_uma_2023.html`); January
  2023: 96.22 / 2,925.09 / 35,101.08 (INEGI, boletín UMA 2022, "entran en vigor a partir del 1° de febrero de 2022",
  `refs/years/inegi_uma2022.pdf`).
* Subsidio para el empleo: the 2013 decree's monthly table all year (as printed in A8-2024; unchanged until SE-2024).
* Salario mínimo 2023 (LSS art. 36 only): 207.44 — CONASAMI resolution, DOF 07-12-2022, codigo 5673550
  (`refs/years/dof_conasami_2023.txt`): "para el Resto del país el salario mínimo general será de 207.44 pesos diarios"
  (round 4).
* LFT art. 76 (12 vacation days) as amended DOF 27-12-2022, in force from 2023. -/

def mxY2023 : MxYear :=
  { year := 2023, umaDaily := 10374, umaMonthly := 315370, umaAnnual := 3784440,
    umaDailyPrev := 9622, umaMonthlyPrev := 292509, salMin := 20744 }

/-- The subsidy that corresponded in month `m` of year `y` (2023 or 2024) for a month's base. -/
def subsidyYear (y : Int) (m : Nat) (base : Int) : Int :=
  if y = 2024 then subsidy2024 m base else oldSubsidy base

/-- The parameters of year `y` (2023, 2024 or 2025; any other year: 2025's). -/
def mxYear (y : Int) : MxYear := if y = 2024 then mxY2024 else if y = 2023 then mxY2023 else mxY2025

theorem uma_annual_2023 : mxY2023.umaMonthly * 12 = mxY2023.umaAnnual := by decide


/-! ## Tax year 2022 (tests round 3)

* Tarifas: Anexo 8 RMF 2022 (DOF 12-01-2022, "Anexos 8, 11, 14 y 17 de la Resolución Miscelánea Fiscal para 2022",
  dof.gob.mx/nota_detalle.php?codigo=5640505, `refs/years/dof_a8_2022.txt`): C.2 "Tarifa para el cálculo del impuesto
  correspondiente al ejercicio 2022" (0.01 / 0.00 / 1.92; 7,735.01 / 148.51 / 6.40; … 3,898,140.13 / 1,222,522.76 /
  35.00) and B.5 "Tarifa aplicable durante 2022 para el cálculo de los pagos provisionales mensuales" (0.01 / 0.00 / 1.92;
  644.59 / 12.38 / 6.40; … 324,845.02 / 101,876.90 / 35.00); its subsidy table (the 2013 decree's) is the one above.
* UMA 2022 from 1-02-2022: 96.22 / 2,925.09 / 35,101.08 (INEGI boletín UMA 2022, `refs/years/inegi_uma2022.pdf`; and the
  DOF notice itself, 10-01-2022, codigo 5640427, `refs/years/dof_uma_2022.txt`: "el valor diario … es de $96.22 …, el mensual
  es de $2,925.09 … y el valor anual $35,101.08", round 4).
  January 2022: the 2021 UMA, 89.62 / 2,724.45 — INEGI notice, DOF 08-01-2021, codigo 5609633 (`refs/years/dof_uma_2021.txt`:
  "el valor diario … es de $89.62 …, el mensual es de $2,724.45 … y el valor anual $32,693.40 … vigentes a partir del 1o. de
  febrero de 2021", round 7; it agrees with the derivation 89.62 × 1.0736 = 96.22 used before).
* Salario mínimo 2022 (LSS art. 36): 172.87 (CONASAMI resolution, DOF 08-12-2021, codigo 5637615,
  `refs/years/dof_conasami_2022.txt`: "para el Resto del país el salario mínimo general será de 172.87 pesos diarios").
* Vacation days (LFT art. 76): 6 in 2022 — the decree raising them to 12 (DOF 27-12-2022, codigo 5675889,
  `refs/years/dof_lft_vacaciones_2022.txt`) "entrará en vigor el 1.° de enero de 2023". The pre-reform text, from the Ley Federal del Trabajo as published
  in the DOF of 1 April 1970 (page 8, scanned image through the DOF daily index of 01-04-1970, codnota 4670446,
  `~/cmp20/emerging/mx/refs/dof/lft1970/p8.bin`, round 9): "Artículo 76. Los trabajadores que tengan más de un año de
  servicios disfrutarán de un período anual de vacaciones pagadas, que en ningún caso podrá ser inferior a seis días
  laborables, y que aumentará en dos días laborables, hasta llegar a doce, por cada año subsecuente de servicios";
  art. 80 "una prima no menor de veinticinco por ciento". Amendments between 1970 and 2022 were not checked
  (diputados.gob.mx is unreachable), but the 2022 decree replaced exactly this wording. Used as the default of
  `mxVacationDays` for 2022. -/

def tarifa152_2022 : List Row := [
  ⟨1, 0, 192⟩, ⟨773501, 14851, 640⟩, ⟨6565108, 385514, 1088⟩, ⟨11537591, 926520, 1600⟩,
  ⟨13411942, 1226416, 1792⟩, ⟨16057766, 1700547, 2136⟩, ⟨32386201, 5188301, 2352⟩,
  ⟨51045101, 9576874, 3000⟩, ⟨97453504, 23499395, 3200⟩, ⟨129938005, 33894434, 3400⟩,
  ⟨389814013, 122252276, 3500⟩]

def tarifa96_2022 : List Row := [
  ⟨1, 0, 192⟩, ⟨64459, 1238, 640⟩, ⟨547093, 32126, 1088⟩, ⟨961467, 77210, 1600⟩,
  ⟨1117663, 102201, 1792⟩, ⟨1338148, 141712, 2136⟩, ⟨2698851, 432358, 2352⟩,
  ⟨4253759, 798073, 3000⟩, ⟨8121126, 1958283, 3200⟩, ⟨10828168, 2824536, 3400⟩,
  ⟨32484502, 10187690, 3500⟩]

def mxY2022 : MxYear :=
  { year := 2022, umaDaily := 9622, umaMonthly := 292509, umaAnnual := 3510108,
    umaDailyPrev := 8962, umaMonthlyPrev := 272445, salMin := 17287 }

def tarifa152Y (y : Int) : List Row := if y = 2022 then tarifa152_2022 else tarifa152
def tarifa96Y (y : Int) : List Row := if y = 2022 then tarifa96_2022 else tarifa96

/-- The parameters of year `y` (2022–2025; any other year: 2025's). -/
def mxYearAll (y : Int) : MxYear := if y = 2022 then mxY2022 else mxYear y

theorem uma_2022 : mxY2022.umaMonthly * 12 = mxY2022.umaAnnual ∧ (8962 * 10736 + 5000) / 10000 / 100 = 96 := by decide

end MxTax
