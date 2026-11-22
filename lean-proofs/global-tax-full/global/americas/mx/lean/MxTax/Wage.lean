import MxTax.Params

/-!
# Wage income: the exempt aguinaldo and prima vacacional, previsión social, the monthly withholding with the
subsidio para el empleo, and the employee's IMSS quotas

How an annual wage `W` divides (an input convention, not statute; the OECD's, see `oecd_map.py`): the daily wage is
`W / 365`; the *aguinaldo* is `aguinaldoDays` of it (LFT art. 87: "equivalente a quince días de salario, por lo
menos", default 15), the *prima vacacional* is `primaPct` of `vacationDays` of it (LFT art. 80: "no menor de
veinticinco por ciento"; LFT art. 76 as amended DOF 27-12-2022: 12 days in the first year; defaults 25 % and 12),
and both are part of `W`. The aguinaldo is paid in December (LFT art. 87: "antes del día veinte de diciembre"), the
prima vacacional (convention) in July; the rest is paid in 12 equal months.
-/

namespace MxTax
open TaxKernel

structure WageIn where
  /-- annual wages, pesos (aguinaldo and prima vacacional included) -/
  wages : Int := 0
  aguinaldoDays : Int := 15
  vacationDays : Int := 12
  /-- bp -/
  primaPct : Int := 2500
  /-- pesos of `wages` paid as previsión social (art. 93 fr. VIII: vales, despensa, ...) -/
  prevision : Int := 0
  /-- IMSS with the OECD's convention (annual 2025 UMA for the whole year) instead of the calendar -/
  imssOecd : Bool := false
  /-- paid as *asimilados a salarios* (LISR art. 94 fr. II-VII, e.g. honorarios asimilados): taxed like wages but
  outside the IMSS (no employment relationship) and outside the subsidy (SE-2024 art. Primero covers only "el
  artículo 94, primer párrafo y fracción I") -/
  asimilado : Bool := false
  /-- tax year (2024 or 2025; tests round 2): `mxYear` -/
  yr : Int := 2025
  deriving Repr, Inhabited

/-- The aguinaldo, centavos: `aguinaldoDays × W / 365`. -/
def WageIn.aguinaldo (w : WageIn) : Int := mulDivHU (cts w.wages) w.aguinaldoDays 365
/-- The prima vacacional, centavos: `primaPct × vacationDays × W / 365`. -/
def WageIn.prima (w : WageIn) : Int := mulDivHU (cts w.wages) (w.vacationDays * w.primaPct) (365 * BP)

/-- LISR art. 93 fr. XIV: exempt aguinaldo, at most 30 UMA (the December UMA, 113.14). -/
def WageIn.exAguinaldo (w : WageIn) : Int := min (pos w.aguinaldo) (aguinaldoExemptDays * (mxYearAll w.yr).umaDaily)
/-- LISR art. 93 fr. XIV: exempt prima vacacional, at most 15 UMA. -/
def WageIn.exPrima (w : WageIn) : Int := min (pos w.prima) (primaExemptDays * (mxYearAll w.yr).umaDaily)

/-- LISR art. 93 penúltimo párrafo: the previsión social exemption. If salary `y` plus the previsión `ps` exceed 7
annual UMA, only up to 1 annual UMA is exempt, "Esta limitación en ningún caso deberá dar como resultado que la suma
... sea inferior a siete veces". Centavos. -/
def psExempt (y ps : Int) (ua : Int := umaAnnual) : Int :=
  if y + ps ≤ psLimitUma * ua then ps
  else min ps (max ua (psLimitUma * ua - y))

def WageIn.exPrevision (w : WageIn) : Int :=
  psExempt (cts (w.wages - w.prevision)) (cts (pos w.prevision)) (mxYearAll w.yr).umaAnnual

/-- Total exempt wage income (the OECD's "BTA" for these households), centavos. -/
def WageIn.exempt (w : WageIn) : Int := w.exAguinaldo + w.exPrima + w.exPrevision

/-- Taxable wage income (LISR art. 94 less art. 93 exemptions), centavos. -/
def WageIn.taxable (w : WageIn) : Int := pos (cts w.wages - w.exempt)

/-! ## Monthly withholding (art. 96) and the subsidio para el empleo -/

/-- Ordinary monthly taxable wage, centavos: the wage less aguinaldo, prima and the exempt previsión, over 12. -/
def WageIn.ordinaryMonth (w : WageIn) : Int :=
  mulDivHU (cts w.wages - w.aguinaldo - w.prima - w.exPrevision) 1 12

/-- The base of month `m` (1..12): "la totalidad de los ingresos obtenidos en un mes de calendario" (art. 96) less
exempt income; July carries the taxable prima, December the taxable aguinaldo. -/
def WageIn.monthBase (w : WageIn) (m : Nat) : Int :=
  w.ordinaryMonth
    + (if m = 7 then pos (w.prima - w.exPrima) else 0)
    + (if m = 12 then pos (w.aguinaldo - w.exAguinaldo) else 0)

/-- SE-2025 art. Segundo: a month qualifies when its base does not exceed $10,171.00. -/
def WageIn.subsidyEligible (w : WageIn) (m : Nat) : Bool :=
  !w.asimilado && decide (0 < w.wages) &&
    (if w.yr = 2024 ∨ w.yr = 2023 ∨ w.yr = 2022 then decide (subsidyYear w.yr m (w.monthBase m) > 0) else decide (w.monthBase m ≤ subsidyCap))

/-- The subsidy that "le correspondió" in month `m` (the entitlement). -/
def WageIn.subsidyOf (w : WageIn) (m : Nat) : Int :=
  if w.subsidyEligible m then (if w.yr = 2024 ∨ w.yr = 2023 ∨ w.yr = 2022 then subsidyYear w.yr m (w.monthBase m) else subsidyMonth m) else 0

/-- Art. 96 ISR of month `m` before the subsidy, centavos. -/
def WageIn.isrMonth (w : WageIn) (m : Nat) : Int := ticksToCentavos (tarifaTicks (tarifa96Y w.yr) (w.monthBase m))

/-- Withheld in month `m`: ISR less the subsidy; SE-2024 art. Segundo: "En los casos en que el impuesto a cargo del
trabajador sea menor que el subsidio ... la diferencia no podrá aplicarse ... ni se entregará cantidad alguna". -/
def WageIn.withheld (w : WageIn) (m : Nat) : Int := pos (w.isrMonth m - w.subsidyOf m)

def months : List Nat := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

/-- Σ of the monthly subsidies that corresponded (reading R1 of SE-2024 art. Tercero: the entitlement). -/
def WageIn.subsidyTotal (w : WageIn) : Int := sumInts (months.map w.subsidyOf)
/-- Σ of the subsidies actually applied against the monthly ISR (reading R2). -/
def WageIn.subsidyApplied (w : WageIn) : Int := sumInts (months.map fun m => min (w.subsidyOf m) (w.isrMonth m))
def WageIn.subsidyMonths (w : WageIn) : Int := sumInts (months.map fun m => if w.subsidyEligible m then 1 else 0)
/-- Total withheld over the year (art. 96 provisional payments), centavos. -/
def WageIn.withheldTotal (w : WageIn) : Int := sumInts (months.map w.withheld)

/-! ## IMSS employee quotas (LSS) -/

structure Imss where
  excess : Int := 0
  dinero : Int := 0
  pensionados : Int := 0
  invalidez : Int := 0
  cesantia : Int := 0
  deriving Repr, Inhabited

def Imss.total (i : Imss) : Int := i.excess + i.dinero + i.pensionados + i.invalidez + i.cesantia
/-- The quotas the OECD books as SSC (it treats retiro/cesantía/vejez, paid into individual AFORE accounts, as a
non-tax compulsory payment). -/
def Imss.oecdSsc (i : Imss) : Int := i.excess + i.dinero + i.pensionados + i.invalidez

/-- One branch over `n` days at UMA `u`, in units of 1/(365 × 100,000) centavo: `n × rate × base`, where the base
is the SBC (W/365 per day, capped at 25 UMA, LSS art. 28) or its excess over 3 UMA (art. 106 fr. II). Working
with `365 × SBC = W` keeps it exact. -/
def branch365 (wC n u rate : Int) (excessOnly : Bool) : Int :=
  let base := min wC (sbcCapUma * u * 365)
  let b := if excessOnly then pos (base - excessUma * u * 365) else base
  n * rate * b

/-- The employee's quotas for wage `W` pesos. LSS art. 36: when the worker's daily wage is the minimum wage the
employer pays the worker's quota ("Corresponde al patrón pagar íntegramente la cuota señalada para los trabajadores,
en los casos en que éstos perciban como cuota diaria el salario mínimo"); we read "el salario mínimo" as a daily
wage not above it. Calendar convention: 31 days at the 2024 UMA, 334 at the 2025 UMA, each branch rounded to the
centavo on the year. OECD convention: the annual 2025 UMA (3 × 41,273.52) for the year. -/
def imssOf (w : WageIn) : Imss :=
  let wC := cts (pos w.wages)
  let Y := mxYearAll w.yr
  if w.asimilado || wC ≤ Y.salMin * 365 then {}
  else if w.imssOecd then
    let base := min wC (sbcCapUma * Y.umaAnnual)
    let ex := pos (base - excessUma * Y.umaAnnual)
    { excess := mulDivHU ex rExcess 100000, dinero := mulDivHU base rDinero 100000,
      pensionados := mulDivHU base rPensionados 100000, invalidez := mulDivHU base rInvalidez 100000,
      cesantia := mulDivHU base rCesantia 100000 }
  else
    let d := 365 * 100000
    let f (rate : Int) (ex : Bool) : Int :=
      divR .halfUp (branch365 wC daysJan Y.umaDailyPrev rate ex + branch365 wC daysFebDec Y.umaDaily rate ex) d
    { excess := f rExcess true, dinero := f rDinero false, pensionados := f rPensionados false,
      invalidez := f rInvalidez false, cesantia := f rCesantia false }

end MxTax
