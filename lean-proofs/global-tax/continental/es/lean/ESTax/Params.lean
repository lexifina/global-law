import ESTax.Basic

/-!
# Parameters for ejercicio 2025, each with its provision

Sources (texts saved under `law/`; official consolidated texts on boe.es):
* LIRPF = Ley 35/2006 (BOE-A-2006-20764), as in force on 31-12-2025, https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764
* Madrid = Decreto Legislativo 1/2010 (texto refundido tributos cedidos), as in force on 31-12-2025,
  https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/BOCM-m-2010-90068
* Orden PJC/178/2025 (cotización 2025), BOE-A-2025-3780, https://www.boe.es/buscar/doc.php?id=BOE-A-2025-3780
* Ley 49/2002 art. 19 (mecenazgo), BOE-A-2002-25039, as amended by RDL 6/2023 (from 1-1-2024)
* Ley 5/2025 disp. final 3.ª (adds LIRPF disp. adicional 61.ª, effects 1-1-2025), BOE-A-2025-15424
-/

namespace ESTax
open TaxKernel

/-! ## Scales -/

/-- LIRPF art. 63.1 1.º (Ley 11/2020, from 2021): escala general estatal.
"0,00 | 0,00 | 12.450,00 | 9,50 / 12.450,00 | 1.182,75 | 7.750,00 | 12,00 / 20.200,00 | 2.112,75 | 15.000,00 | 15,00 /
35.200,00 | 4.362,75 | 24.800,00 | 18,50 / 60.000,00 | 8.950,75 | 240.000,00 | 22,50 / 300.000,00 | 62.950,75 |
En adelante | 24,50". -/
def escalaEstatal : List Row :=
  [⟨0, 0, 950⟩, ⟨1245000, 118275, 1200⟩, ⟨2020000, 211275, 1500⟩, ⟨3520000, 436275, 1850⟩,
   ⟨6000000, 895075, 2250⟩, ⟨30000000, 6295075, 2450⟩]

/-- DLeg 1/2010 (Madrid) art. 1 (Ley 13/2023, periods from 1-1-2023): escala autonómica.
"0 | 0 | 13.362,22 | 8,50 / 13.362,22 | 1.135,79 | 5.642,41 | 10,70 / 19.004,63 | 1.739,53 | 16.421,05 | 12,80 /
35.425,68 | 3.841,42 | 21.894,72 | 17,40 / 57.320,40 | 7.651,10 | en adelante | 20,50". -/
def escalaMadrid : List Row :=
  [⟨0, 0, 850⟩, ⟨1336222, 113579, 1070⟩, ⟨1900463, 173953, 1280⟩, ⟨3542568, 384142, 1740⟩,
   ⟨5732040, 765110, 2050⟩]

/-- LIRPF art. 66.1 1.º (Ley 7/2024 disp. final 7.ª, from 1-1-2025): escala del ahorro, parte estatal.
"0 | 0 | 6.000 | 9,5 / 6.000,00 | 570 | 44.000 | 10,5 / 50.000,00 | 5.190 | 150.000 | 11,5 / 200.000,00 | 22.440 |
100.000 | 13,5 / 300.000,00 | 35.940 | En adelante | 15". -/
def escalaAhorroEstatal : List Row :=
  [⟨0, 0, 950⟩, ⟨600000, 57000, 1050⟩, ⟨5000000, 519000, 1150⟩, ⟨20000000, 2244000, 1350⟩,
   ⟨30000000, 3594000, 1500⟩]

/-- LIRPF art. 76 1.º (Ley 7/2024, from 1-1-2025): tipo de gravamen del ahorro, parte autonómica; the same table. -/
def escalaAhorroAutonomica : List Row := escalaAhorroEstatal

/-! ## Mínimo personal y familiar -/

/-- LIRPF art. 57.1: "El mínimo del contribuyente será, con carácter general, de 5.550 euros anuales." -/
def minContribuyente : Int := eur 5550
/-- art. 57.2: "edad superior a 65 años, el mínimo se aumentará en 1.150 euros ... superior a 75 años ...
adicionalmente en 1.400 euros". -/
def minMas65 : Int := eur 1150
def minMas75 : Int := eur 1400
/-- art. 58.1: "2.400 euros anuales por el primero. 2.700 ... por el segundo. 4.000 ... por el tercero. 4.500 ... por el
cuarto y siguientes." -/
def minDesc : List Int := [eur 2400, eur 2700, eur 4000, eur 4500]
/-- art. 58.2: "Cuando el descendiente sea menor de tres años, ... se aumentará en 2.800 euros anuales." -/
def minDescMenor3 : Int := eur 2800

/-- Madrid art. 2 a): "El mínimo del contribuyente será, con carácter general, de 5.956,65 euros anuales." -/
def minContribuyenteMad : Int := 595665
/-- Madrid art. 2 b): "superior a 65 años ... 1.234,26 euros ... superior a 75 años ... 1.502,58 euros". -/
def minMas65Mad : Int := 123426
def minMas75Mad : Int := 150258
/-- Madrid art. 2 bis: "2.575,85 ... primer descendiente ... 2.897,83 ... segundo ... 4.400 ... tercero ... 4.950 ...
cuarto y siguientes"; "menor de tres años ... se aumentará en 3.005,16 euros anuales". -/
def minDescMad : List Int := [257585, 289783, eur 4400, eur 4950]
def minDescMenor3Mad : Int := 300516

/-- The mínimo for the `i`-th descendant (0-based), the last amount repeating ("cuarto y siguientes"). -/
def ordinal (amts : List Int) (i : Nat) : Int :=
  match amts[i]? with
  | some a => a
  | none => amts.getLastD 0

/-! ## Rendimientos del trabajo -/

/-- LIRPF art. 19.2 f): "En concepto de otros gastos distintos de los anteriores, 2.000 euros anuales." -/
def otrosGastos : Int := eur 2000

/-- LIRPF art. 20 (RDL 4/2024, from 1-1-2024): thresholds and amounts. -/
def r20Limite : Int := 1974750     -- "inferiores a 19.747,5 euros"
def r20Otras : Int := eur 6500      -- "rentas ... distintas de las del trabajo superiores a 6.500 euros"
def r20T1 : Int := eur 14852        -- a) "iguales o inferiores a 14.852 euros: 7.302 euros"
def r20Max : Int := eur 7302
def r20T2 : Int := 1767352          -- b) "... 17.673,52 euros: 7.302 euros menos ... 1,75"
def r20Mid : Int := 236434          -- c) "2.364,34 euros menos ... 1,14"
def r20K1 : Int := 175              -- 1,75 in hundredths
def r20K2 : Int := 114              -- 1,14 in hundredths

/-! ## Seguridad Social, employee share (Régimen General, contrato indefinido), 2025 -/

/-- Orden PJC/178/2025 arts. 1-2 (tope máximo "4.909,50 euros mensuales"), annual: 12 × 4.909,50 = 58.914 €. -/
def baseMaxima : Int := 12 * 490950
/-- Contingencias comunes "el 4,70 por ciento a cargo de la persona trabajadora". -/
def ssCC : Int := 470
/-- Desempleo, contratación indefinida: "el 1,55 por ciento, a cargo del empleado". -/
def ssDesempleo : Int := 155
/-- Formación profesional: "el 0,10 por ciento, a cargo de la persona trabajadora". -/
def ssFP : Int := 10
/-- Mecanismo de equidad intergeneracional (art. 17 bis Orden numbering a1-8): "0,13 por ciento, a cargo de la persona
trabajadora". -/
def ssMEI : Int := 13
/-- Employer shares (for the art. 81 bis limit "cotizaciones y cuotas totales"): CC 23,60 %, desempleo 5,50 %, FP 0,60 %,
MEI 0,67 % (same Orden). Accidentes de trabajo (tarifa by activity) and FOGASA are left out: the limit used is a lower
bound. -/
def ssEmployer : Int := 2360 + 550 + 60 + 67

/-- Orden PJC/178/2025 art. 17 (cotización adicional de solidaridad), worker shares, monthly bands × 12:
"0,15 por ciento ... entre 4.909,51 euros y 5.400,45 euros"; "0,17 por ciento ... entre 5.400,46 euros y 7.364,25";
"0,19 por ciento ... que supere los 7.364,25 euros". -/
def solT1 : Int := 12 * 540045
def solT2 : Int := 12 * 736425
def solR1 : Int := 15
def solR2 : Int := 17
def solR3 : Int := 19

/-! ## Reductions, deductions -/

/-- LIRPF art. 52.1: "a) El 30 por 100 de la suma de los rendimientos netos del trabajo y de actividades económicas
... b) 1.500 euros anuales." -/
def ppLimitePct : Int := 3000
def ppLimite : Int := eur 1500

/-- LIRPF art. 84.2 3.º and 4.º: joint taxation reductions "3.400 euros anuales" (first modality) and "2.150 euros
anuales" (second modality, not when living with the other parent). -/
def redConjunta : Int := eur 3400
def redMonoparental : Int := eur 2150

/-- Ley 49/2002 art. 19.1 (RDL 6/2023): "250 euros. | 80 / Resto base de deducción. | 40"; LIRPF art. 69.1 base
limit "10 por ciento de la base liquidable"; arts. 67.1 b) / 77.1 a): 50 % of the deduction on each cuota. -/
def donTramo : Int := eur 250
def donR1 : Int := 8000
def donR2 : Int := 4000

/-- LIRPF disp. adicional 61.ª (Ley 5/2025): "inferiores a 18.276 euros"; "iguales o inferiores a 16.576 euros
anuales: 340 euros"; "340 euros menos el resultado de multiplicar por 0,2 la diferencia". -/
def smiLimite : Int := eur 18276
def smiT1 : Int := eur 16576
def smiMax : Int := eur 340

/-- LIRPF art. 81.1: "hasta en 1.200 euros anuales por cada hijo menor de tres años". -/
def maternidad : Int := eur 1200
/-- LIRPF art. 81 bis.1 c): "hasta 1.200 euros anuales"; "incrementará en un 100 por ciento" (categoría especial);
"hasta en 600 euros anuales por cada uno de los hijos ... que exceda del número mínimo". -/
def famNum : Int := eur 1200
def famNumHijoExtra : Int := eur 600

/-- Madrid art. 4.1: "721,70 euros por cada hijo nacido o adoptado" (year of birth and the two following);
art. 18.1 limits "30.930 euros en tributación individual o a 37.322,20 euros en tributación conjunta"; unit
"61.860 euros". -/
def madNacimiento : Int := 72170
def madLimInd : Int := eur 30930
def madLimConj : Int := 3732220
def madLimUnidad : Int := eur 61860
/-- Madrid art. 14: "dos o más descendientes ... suma de bases imponibles no sea superior a 24.744 euros ...
deducción del 10 por 100". -/
def madFam2Lim : Int := eur 24744
def madFam2Pct : Int := 1000



/-! ## Earlier years (improvement round 5, 2026-11-19): one parameter record per ejercicio

Every amount below is read from the dated version of the provision, through the BOE consolidated-text API (blocks with
all their versions, copies in `~/cmp20/improve-central/refs/es/`):
* LIRPF blocks `a20`, `a57`, `a58`, `a63`, `a66`, `a76`, `a81`, `a81bis`
  (https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/BOE-A-2006-20764/texto/bloque/<a>);
* Madrid DLeg 1/2010 blocks `a1`, `a2`, `a2-3` (art. 2 bis), `a4`, `a14`, `a18`
  (…/id/BOCM-m-2010-90068/texto/bloque/<a>);
* Órdenes de cotización: Orden PCM/244/2022 (BOE-A-2022-5063), Orden PCM/74/2023 (BOE-A-2023-2472), Orden PJC/51/2024
  (BOE-A-2024-1691), https://www.boe.es/buscar/doc.php?id=<id>.
Unchanged in every year 2022-2025 (no version of the block in force from 2021 to 2025 differs): the escala general
estatal (art. 63, version of 1-1-2021, Ley 11/2020), the mínimos estatales (arts. 57, 58: last versions before 2020),
art. 81 bis (no version after 2018), the SS rates for contingencias comunes 4,70 %, desempleo (indefinido) 1,55 % and
formación profesional 0,10 % (each Orden, articles on "Contingencias comunes", "Desempleo: 1.º Contratación
indefinida", "Formación profesional"). -/

/-- The amounts that differ between ejercicios. -/
structure YP where
  year : Nat
  /-- Madrid art. 1 scale -/
  escalaMadrid : List Row
  /-- LIRPF art. 66.1 1.º (state) = art. 76 1.º (autonómica): the ahorro scale -/
  escalaAhorro : List Row
  /-- Madrid arts. 2 a)-b), 2 bis -/
  minContribuyenteMad : Int
  minMas65Mad : Int
  minMas75Mad : Int
  minDescMad : List Int
  minDescMenor3Mad : Int
  /-- LIRPF art. 20 (cents; k in hundredths). Two-band versions set `r20T2 = r20Limite`. -/
  r20Limite : Int
  r20T1 : Int
  r20Max : Int
  r20T2 : Int
  r20Mid : Int
  r20K1 : Int
  r20K2 : Int
  /-- Orden de cotización: tope máximo (annual), MEI worker share, employer total used by art. 81 bis.2 -/
  baseMaxima : Int
  ssMEI : Int
  ssEmployer : Int
  /-- LGSS art. 19 bis cotización de solidaridad (from 2025) -/
  solidaridad : Bool
  /-- LIRPF DA 61.ª (Ley 5/2025, from 2025) -/
  da61 : Bool
  /-- Madrid art. 4 amount and art. 18.1 limits; art. 14 limit -/
  madNacimiento : Int
  madLimInd : Int
  madLimConj : Int
  madLimUnidad : Int
  madFam2Lim : Int
  deriving Repr, Inhabited, DecidableEq

/-- 2025: exactly the constants above. -/
def yp2025 : YP :=
  { year := 2025, escalaMadrid, escalaAhorro := escalaAhorroEstatal, minContribuyenteMad, minMas65Mad, minMas75Mad,
    minDescMad, minDescMenor3Mad, r20Limite, r20T1, r20Max, r20T2, r20Mid, r20K1, r20K2, baseMaxima, ssMEI,
    ssEmployer, solidaridad := true, da61 := true, madNacimiento, madLimInd, madLimConj, madLimUnidad, madFam2Lim }

/-- LIRPF art. 66.1 1.º / 76 1.º, version in force 1-1-2023 (Ley 31/2022 art. 59): "... 200.000,00 | 22.440 | 100.000 |
13,5 / 300.000,00 | 35.940 | En adelante | 14" (2023 and 2024; the 15 % top rate is Ley 7/2024, from 2025). -/
def escalaAhorro2023 : List Row :=
  [⟨0, 0, 950⟩, ⟨600000, 57000, 1050⟩, ⟨5000000, 519000, 1150⟩, ⟨20000000, 2244000, 1350⟩,
   ⟨30000000, 3594000, 1400⟩]

/-- Same articles, version of 1-1-2021 (Ley 11/2020), in force for 2022: "... 200.000,00 | 22.440 | En adelante | 13,00". -/
def escalaAhorro2022 : List Row :=
  [⟨0, 0, 950⟩, ⟨600000, 57000, 1050⟩, ⟨5000000, 519000, 1150⟩, ⟨20000000, 2244000, 1300⟩]

/-- Madrid art. 1 as set by Ley 8/2022 art. único.2 ("aplicación a todos los períodos impositivos que se inicien a
partir del 1 de enero de 2022"): "0 | 0 | 12.960,45 | 8,50 / 12.960,45 | 1.101,64 | 5.472,75 | 10,70 / 18.433,20 |
1.687,22 | 15.927,30 | 12,80 / 34.360,50 | 3.725,91 | 21.236,40 | 17,40 / 55.596,90 | 7.421,04 | En adelante | 20,50". -/
def escalaMadrid2022 : List Row :=
  [⟨0, 0, 850⟩, ⟨1296045, 110164, 1070⟩, ⟨1843320, 168722, 1280⟩, ⟨3436050, 372591, 1740⟩,
   ⟨5559690, 742104, 2050⟩]

/-- 2024. LIRPF art. 20 as set by RDL 4/2024 (the 2025 values); ahorro top rate 14 %; Madrid as in 2025 (Ley 13/2023,
periods from 1-1-2023); Orden PJC/51/2024: "tope máximo ... desde el 1 de enero de 2024, de 4.720,50 euros mensuales";
MEI "el 0,70 por ciento ... del que el 0,58 por ciento será a cargo de la empresa y el 0,12 por ciento, a cargo del
trabajador"; no cotización de solidaridad (LGSS art. 19 bis applies from 2025); no DA 61.ª. -/
def yp2024 : YP :=
  { yp2025 with
    year := 2024, escalaAhorro := escalaAhorro2023, baseMaxima := 12 * 472050, ssMEI := 12,
    ssEmployer := 2360 + 550 + 60 + 58, solidaridad := false, da61 := false }

/-- 2023. LIRPF art. 20 as set by Ley 31/2022 art. 59.1 (version in force 1-1-2023): "inferiores a 19.747,5 euros ...
a) iguales o inferiores a 14.047,5 euros: 6.498 euros anuales. b) ... entre 14.047,5 y 19.747,5 euros: 6.498 euros
menos el resultado de multiplicar por 1,14 la diferencia"; Orden PCM/74/2023: "4.495,50 euros mensuales", MEI "0,6 por
ciento ... 0,5 ... a cargo de la empresa y el 0,1 por ciento, a cargo del trabajador". Madrid: Ley 13/2023 (periods
from 1-1-2023): the 2025 scale, mínimos, art. 4 721,70 €, art. 14 24.744 €, art. 18.1 30.930 / 37.322,20 / 61.860 €. -/
def yp2023 : YP :=
  { yp2024 with
    year := 2023, r20Limite := 1974750, r20T1 := 1404750, r20Max := eur 6498, r20T2 := 1974750,
    r20Mid := 0, r20K1 := 114, r20K2 := 0, baseMaxima := 12 * 449550, ssMEI := 10, ssEmployer := 2360 + 550 + 60 + 50 }

/-- 2022. LIRPF art. 20 version of 5-7-2018 (Ley 6/2018): "inferiores a 16.825 euros ... a) iguales o inferiores a
13.115 euros: 5.565 euros anuales. b) ... entre 13.115 y 16.825 euros: 5.565 euros menos el resultado de multiplicar por
1,5 la diferencia"; ahorro scale with 13 % above 200.000 € (Ley 11/2020); Orden PCM/244/2022: "4.139,40 euros
mensuales", no MEI (Ley 21/2021 DF 4.ª: from 2023). Madrid as set by Ley 8/2022 (periods from 1-1-2022): art. 1
`escalaMadrid2022`; art. 2 "5.777,55 ... 1.197,15 ... 1.457,40"; art. 2 bis "2.498,40 ... 2.810,70 ... 4.400 ...
4.950", under three "2.914,80"; art. 4 (Ley 12/2017 version) "600 euros"; art. 14 (original text) "24.000 euros";
art. 18.1 (version in force 1-1-2022): art. 4 limits "30.000 euros en tributación individual o a 36.200 euros en
tributación conjunta", unit "60.000 euros". -/
def yp2022 : YP :=
  { yp2023 with
    year := 2022, escalaMadrid := escalaMadrid2022, escalaAhorro := escalaAhorro2022,
    minContribuyenteMad := 577755, minMas65Mad := 119715, minMas75Mad := 145740,
    minDescMad := [249840, 281070, eur 4400, eur 4950], minDescMenor3Mad := 291480,
    r20Limite := eur 16825, r20T1 := eur 13115, r20Max := eur 5565, r20T2 := eur 16825, r20Mid := 0, r20K1 := 150,
    r20K2 := 0, baseMaxima := 12 * 413940, ssMEI := 0, ssEmployer := 2360 + 550 + 60,
    madNacimiento := eur 600, madLimInd := eur 30000, madLimConj := eur 36200, madLimUnidad := eur 60000,
    madFam2Lim := eur 24000 }

/-- The record for an ejercicio: 2022-2024 their own; 2025 and anything else the 2025 record (`years.json` declares
2022-2025 only). -/
def ypFor (y : Nat) : YP :=
  if y = 2022 then yp2022 else if y = 2023 then yp2023 else if y = 2024 then yp2024 else yp2025

theorem ypFor_2025 : ypFor 2025 = yp2025 := rfl

/-- Madrid 2022 (Ley 8/2022) prints its cuota column as a running sum of each band's tax rounded to the cent, not as
the rounded band sum: at 34.360,50 € it prints 3.725,91 where 8,5 % × 12.960,45 + 10,7 % × 5.472,75 + 12,8 % × 15.927,30
= 3.725,916 (1.101,64 + 585,58 + 2.038,69 = 3.725,91). So `cuotasConsistent` fails by one cent; every printed cuota is
within one cent of the band sum, and the model uses the printed column (the statute's table). -/
def cuotasWithinCent (t : List Row) : Bool :=
  t.all fun r => (r.cuota - tc ((toSched t).ticks r.lo)).natAbs ≤ 1
theorem madrid2022_not_rounded_sum : cuotasConsistent escalaMadrid2022 = false := by decide
theorem madrid2022_cuotas : cuotasWithinCent escalaMadrid2022 = true := by decide
/-- The ahorro tables of 2022 and 2023-24 agree with their band sums, as the 2025 tables do. -/
theorem ahorro2023_cuotas : cuotasConsistent escalaAhorro2023 = true := by decide
theorem ahorro2022_cuotas : cuotasConsistent escalaAhorro2022 = true := by decide

end ESTax
