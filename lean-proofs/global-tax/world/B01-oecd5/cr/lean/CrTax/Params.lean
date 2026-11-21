import TaxKernel.World

/-!
# Costa Rica 2025: parameters with their dated sources

Global law holds no Costa Rican text (corpus "metadata-only"). Source: the official publisher SINALEVI / SCIJ
(Procuraduría General de la República, https://sinalevi.go.cr, reached from http://www.pgrweb.go.cr/scij/), texts
fetched 2026-11-20 through its own search and full-text endpoint (`tools/sinalevi.py`), saved in `../src/sinalevi/`:
* Ley 7092 del Impuesto sobre la Renta (IdFichaNorma 10969, version 83 of 83): structure of art. 1, 15, 29, 29 bis,
  31 ter, 32-35; the amounts printed there are the 2026 ones (Decreto 45333-H), so the 2025 amounts come from
* Decreto Ejecutivo 44772-H (IdFichaNorma 103391, version 148976), "Actualización de los tramos ... a partir del 01
  de enero del 2025", art. 1 (salary scale), 2 (credits), 4 (personas físicas con actividades lucrativas), 5, 7
  ("Rige a partir del primero de enero de dos mil veinticinco").
* Ley 2412 (aguinaldo, IdFichaNorma 35148): art. 1-2, one month's average salary a year, paid in December.
* CCSS: Reglamento del Seguro de Salud art. 62 (IdFichaNorma 43463, v. 32); Reglamento del Seguro de Invalidez, Vejez
  y Muerte art. 33 and Transitorio XI table (image, IdFichaNorma 26485, v. 51); Ley 4351 Orgánica del Banco Popular
  art. 5 (IdFichaNorma 35582).
-/

namespace CrTax
open TaxKernel

/-- Decreto 44772-H art. 1 (Ley 7092 art. 33): monthly salary scale 2025: "hasta ¢ 922.000,00 ... no estarán
sujetas"; "exceso de ¢ 922.000,00 ... y hasta ¢1.352.000,00 ... diez por ciento"; "... hasta ¢ 2.373.000,00 ...
quince por ciento"; "... hasta ¢ 4.745.000,00 ... veinte por ciento"; "exceso de ¢ 4.745.000,00 ... veinticinco". -/
def salaryScale : Schedule :=
  Schedule.ofList [(0, 0), (922000, 1000), (1352000, 1500), (2373000, 2000), (4745000, 2500)]

/-- Decreto 44772-H art. 2 (Ley 7092 art. 34): monthly credits "Por cada hijo, la suma de mil setecientos veinte
colones (¢ 1 720,00)"; "Por el cónyuge, la suma de dos mil seiscientos colones (¢ 2.600,00)". -/
def creditChildMonth : Int := 1720
def creditSpouseMonth : Int := 2600

/-- Decreto 44772-H art. 4 (Ley 7092 art. 15 c): annual scale for personas físicas con actividades lucrativas:
4.094.000 exempt; 10 % to 6.115.000; 15 % to 10.200.000; 20 % to 20.442.000; 25 % above. -/
def profitScale : Schedule :=
  Schedule.ofList [(0, 0), (4094000, 1000), (6115000, 1500), (10200000, 2000), (20442000, 2500)]
/-- Decreto 44772-H art. 5: annual credits "Por cada hijo ... ¢20.640,00 anuales"; "Por el cónyuge ... ¢ 31.200,00". -/
def creditChildYear : Int := 20640
def creditSpouseYear : Int := 31200

/-- Ley 7092 art. 31 ter: "La tarifa aplicable a la renta imponible de las rentas de capital y a la de las ganancias
de capital será del quince por ciento (15%)"; art. 29.3: real-estate income "reducción del quince por ciento (15%) del
ingreso bruto, sin necesidad de prueba alguna"; art. 29 bis: movable capital "sin posibilidad de deducción". -/
def capitalRate : Int := 1500
def rentLumpRate : Int := 1500

/-- Reglamento del Seguro de Salud art. 62: "Trabajadores: 5.50% de sus salarios"; "Pensionados: 5.00% del monto de
sus pensiones". -/
def rateSEM : Int := 550
def rateSEMPension : Int := 500
/-- Reglamento IVM Transitorio XI (table, image): "Del 1º de enero del 2023 al 31 de diciembre del 2025 ... 11,16%
... Trabajadores: 4,17%". In hundredths of a bp. -/
def rateIVMcBp : Int := 41700
/-- Ley 4351 art. 5 b): "Un aporte del 1% mensual sobre las remuneraciones, sean salarios o sueldos que deben pagar los
trabajadores". -/
def rateBP : Int := 100

/-- Ley 7092 art. 35 b): the aguinaldo is not taxed "hasta por la suma que no exceda de la doceava parte de los
salarios devengados en el año"; Ley 2412 art. 1-2: "un beneficio económico anual equivalente a un mes de salario",
the average of the twelve months. So a year's pay is 13 monthly salaries, the 13th exempt. -/
def paymentsWithAguinaldo : Int := 13

end CrTax
