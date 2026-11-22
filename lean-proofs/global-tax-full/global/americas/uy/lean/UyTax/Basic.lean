import TaxKernel.World

/-!
# Uruguay 2025: IRPF (Titulo 7, Texto Ordenado 1996) Categoria II (trabajo) and Categoria I (capital); BPS, FONASA

Dual income tax: labour income on the progressive art. 37 scale in BPC, capital income at proportional rates
(art. 26). Sources (read 2026-11-20):
* TO 1996 (DGI) Titulo 7 as kept up to date by IMPO, `https://www.impo.com.uy/bases/todgi1996/338-1996`
  (arts. 26, 27, 33, 34, 35, 36, 37, 38; art. 37 wording of Ley 19.438 art. 168, art. 38 of Ley 20.124 art. 1).
* BPC 2025 = $ 6.576 (Decreto No. 05/025 de 10.01.025, vigencia 01.01.025): DGI table "Base de Prestaciones y
  Contribuciones (BPC)", gub.uy/direccion-general-impositiva/comunicacion/publicaciones/base-prestaciones-contribuciones-bpc
  (official secondary: the decree itself is behind IMPO's login).
* Ley 16.713 art. 181 (personal montepio 15 %), Ley 18.211 art. 61 (FONASA 3 / 4,5 / 6 %): Global law
  uruguay/national/acts (in force 2025-06-30), official text IMPO.

* D9 review (2026-11-20): Ley 19.689 (D.O. 08/11/2018) art. 17: "La tasa de aportacion al Fondo de Reconversion
  Laboral, a partir del 1 de enero de 2019, se establece para empleadores, trabajadores y Estado en un 0,10% ...
  calculado sobre las asignaciones computables gravadas por contribuciones especiales de seguridad social" (IMPO,
  `law/d9/impo_ley19689_art17.html`); deductible for the IRPF: Titulo 7 art. 38 B) "Los aportes ... al Fondo de
  Reconversion Laboral" (`src/to1996.txt`). Input `"uyFrl": false` restores the pre-review model (no FRL).

Unit: the individual (art. 37 A); the nucleo familiar elections (art. 37 B, C) are not modelled.
-/

namespace UyTax
open TaxKernel

/-- Decreto 05/025 (DGI table, official secondary): BPC from 01.01.2025 = $ 6.576. -/
def bpc : Int := 6576

/-- Art. 37 A (Ley 19.438 art. 168): "Hasta el MNIG de 84 BPC Exento; Mas del MNIG y hasta 120 BPC 10%; Mas de 120 BPC
y hasta 180 BPC 15%; ... 180-360 24%; 360-600 25%; 600-900 27%; 900-1.380 31%; Mas de 1.380 BPC 36%". -/
def art37AUnits : List (Int × Int) :=
  [(0, 0), (84, 1000), (120, 1500), (180, 2400), (360, 2500), (600, 2700), (900, 3100), (1380, 3600)]
def scaleA : Schedule := Schedule.ofUnits art37AUnits .halfUp 1 bpc

/-- Art. 38 D: "20 BPC (veinte Bases de Prestaciones y Contribuciones) anuales por hijo" (minor children). -/
def childDeductionBPC : Int := 20
/-- Art. 38 penultimate paragraph: "la tasa del 14% ... si sus ingresos nominales anuales son iguales o inferiores a
180 BPC ... y la tasa de 8% (ocho por ciento) para los restantes casos". -/
def deductionRateLow : Int := 1400
def deductionRateHigh : Int := 800
def deductionRateLimitBPC : Int := 180
/-- Art. 34: "se deducira del monto total de los ingresos un 30% (treinta por ciento) en concepto de gastos". -/
def selfEmployedExpenseRate : Int := 3000
/-- Ley 16.713 art. 181: "la tasa de aportacion personal jubilatoria (montepio) ... sera del 15% (quince por ciento)". -/
def montepioRate : Int := 1500
/-- Ley 18.211 art. 61: 6 % above 2,5 BPC a month with children under 18, 4,5 % above without, 3 % at or below. -/
def fonasaChildren : Int := 600
def fonasaNoChildren : Int := 450
def fonasaLow : Int := 300
/-- 2,5 BPC a month, in tenths of a BPC. -/
def fonasaLimitTenthsBPC : Int := 25
/-- Ley 19.689 art. 17: FRL 0,10 % of the wage (workers' share), from 1 January 2019. -/
def frlRate : Int := 10
/-- Art. 26 B: dividends of IRAE taxpayers 7 %; "Restantes rentas 12%" (used for interest and rent: see notes). -/
def dividendRate : Int := 700
def otherCapitalRate : Int := 1200

def fonasaRate (monthlyWage : Int) (children : Bool) : Int :=
  if monthlyWage * 10 ≤ fonasaLimitTenthsBPC * bpc then fonasaLow
  else if children then fonasaChildren else fonasaNoChildren

structure Person where
  labour : Int
  taxBefore : Int
  montepio : Int
  fonasa : Int
  frl : Int
  childDed : Int
  deductions : Int
  deductionRate : Int
  credit : Int
  irpf : Int
  deriving Repr

/-- Categoria II for one person; `childShareTenths` = this person's share of the art. 38 D deduction (10 = whole). -/
def person (wage se : Int) (nKids : Nat) (childShareTenths : Int) (useFrl : Bool := true) : Person :=
  let labour := pos wage + (pos se - divR .down (pos se * selfEmployedExpenseRate) BP)
  let taxBefore := scaleA.tax { mode := .halfUp, step := 1 } labour
  let montepio := divR .halfUp (pos wage * montepioRate) BP
  let fonasa := if wage > 0 then divR .halfUp (pos wage * fonasaRate (wage / 12) (nKids > 0)) BP else 0
  let frl := if useFrl then divR .halfUp (pos wage * frlRate) BP else 0       -- art. 38 B): deductible
  let childDed := divR .down (childDeductionBPC * bpc * (nKids : Int) * childShareTenths) 10
  let deductions := montepio + fonasa + frl + childDed
  let rate := if labour ≤ deductionRateLimitBPC * bpc then deductionRateLow else deductionRateHigh
  let credit := divR .halfUp (deductions * rate) BP
  { labour, taxBefore, montepio, fonasa, frl, childDed, deductions, deductionRate := rate, credit,
    irpf := pos (taxBefore - credit) }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let kids := c.childrenUnder 18
  let share : Int := if n == 2 then 5 else 10
  let useFrl := (c.bool? "uyFrl").getD true
  let ps := c.adults.map fun a => person a.wages a.selfEmployment kids share useFrl
  let labourTax := sumInts (ps.map (·.irpf))
  let divTax := divR .halfUp (pos c.dividends * dividendRate) BP
  let intTax := divR .halfUp (pos c.interest * otherCapitalRate) BP
  let rentTax := divR .halfUp (pos c.rentalIncome * otherCapitalRate) BP
  let unsup :=
    ["aguinaldo (SAC) and salario vacacional taxed at a proportional rate (art. 36 inc. 2, 37 last inc.) not separated: all wages enter the scale",
     "montepio 15 % applied without the cap of Ley 20.130 art. 22 ($ 215.179 at the law's base date, indexed: 2025 value not reached); FONASA spouse surcharge not modelled",
     "nucleo familiar elections (art. 37 B/C) not modelled; child deduction shared equally between two parents (art. 38: shared in equal parts when the parents agree)"] ++
    (if c.adults.any (·.pension != 0) then ["pensions: taxed by the IASS (Ley 18.314), not by the IRPF: not modelled"] else []) ++
    (if c.interest != 0 then ["interest: art. 26 A rates depend on currency and term (0,5 % to 12 %); 12 % ('restantes rentas') applied"] else []) ++
    (if c.rentalIncome != 0 then ["rent: art. 26 B 12 % on gross rent (deductible costs and the art. 27 J exemption below 40 BPC not modelled)"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: incrementos patrimoniales (arts. 20-24, 12 %) not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: art. 34 30 % deduction applied; IRAE option and BPS contributions of non-dependents not modelled"] else [])
  Out.make c "UY" "UYU" labourTax
    (surtaxes := [("IRPF_CatI_dividendos", divTax), ("IRPF_CatI_intereses", intTax), ("IRPF_CatI_arrendamientos", rentTax)])
    (employeeSocial := sumInts (ps.map fun p => p.montepio + p.fonasa + p.frl))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.labour))),
                Out.d "taxBeforeCredits" (sumInts (ps.map (·.taxBefore))),
                Out.d "deductionsBase" (sumInts (ps.map (·.deductions))),
                Out.d "deductionCredit" (sumInts (ps.map (·.credit))),
                Out.d "montepio" (sumInts (ps.map (·.montepio))), Out.d "fonasa" (sumInts (ps.map (·.fonasa))),
                Out.d "frl" (sumInts (ps.map (·.frl))),
                Out.d "bpc" bpc])
    (unsupported := unsup)

def country : Country :=
  { code := "UY", name := "Uruguay (IRPF Categorias I y II; BPS montepio, FONASA)", currency := "UYU", year := "2025",
    compute := out }

/- Art. 37 A at BPC 6.576: 84 BPC = 552.384 exempt; the next 36 BPC at 10 %. -/
#guard scaleA.tax { mode := .halfUp, step := 1 } (84 * bpc) == 0
#guard scaleA.tax { mode := .halfUp, step := 1 } (120 * bpc) == 23674

/- D9 review: FRL 0,10 % of 1.000.000 = 1.000; deducted at the art. 38 rate; `uyFrl := false` gives the old person. -/
#guard (person 1000000 0 0 10).frl == 1000 ∧ (person 1000000 0 0 10 false).frl == 0
#guard (person 1000000 0 0 10).deductions == (person 1000000 0 0 10 false).deductions + 1000

end UyTax
