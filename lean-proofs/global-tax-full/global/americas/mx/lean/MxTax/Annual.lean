import MxTax.Wage

/-!
# One person's annual ISR (LISR Título IV): art. 152 on the accumulated income less art. 151 deductions, the
subsidy and dividend credits, the definitive 10 % taxes, RESICO and the own-company option

Mexico taxes each individual separately (there is no joint return), so a household is the sum of its adults.
Amounts are centavos; taxes before rounding are ticks (centavos × 10,000).
-/

namespace MxTax
open TaxKernel

structure PersonIn where
  wage : WageIn := {}
  /-- pesos: jubilaciones / pensiones (art. 93 fr. IV, Cap. I) -/
  pension : Int := 0
  /-- pesos: net profit of an actividad empresarial / profesional (Cap. II Sección I, arts. 100-110) -/
  se : Int := 0
  /-- pesos: gross revenue of that activity (RESICO is a tax on revenue); default = `se` -/
  seRevenue : Int := 0
  /-- "general" (statutory default), "resico" (art. 113-E option), "company" (activity run through an own company
  paying the 30 % CIT and distributing the rest as dividends) -/
  regime : String := "general"
  interest : Int := 0
  dividends : Int := 0
  capitalGains : Int := 0
  rental : Int := 0
  charitable : Int := 0
  ppr : Int := 0
  rentBlind : Bool := true
  /-- "best" (the taxpayer takes the art. 140 gross-up and credit when it lowers the tax), "credit", "none" -/
  divCredit : String := "best"
  deriving Repr, Inhabited

structure PersonOut where
  exemptWages : Int := 0
  taxableWages : Int := 0
  pensionTaxable : Int := 0
  seAccumulated : Int := 0
  rentalAccumulated : Int := 0
  dividendsAccumulated : Int := 0
  acumulables : Int := 0
  totalIncome : Int := 0
  donations : Int := 0
  ppr : Int := 0
  base : Int := 0
  tax152 : Int := 0
  subsidy : Int := 0
  subsidyApplied : Int := 0
  subsidyMonths : Int := 0
  dividendCredit : Int := 0
  isr : Int := 0
  usedDividendCredit : Bool := false
  divAdditional : Int := 0
  cgTax : Int := 0
  resicoTax : Int := 0
  resicoApplies : Bool := false
  resicoMonths : Int := 0
  companyCit : Int := 0
  withheld : Int := 0
  imss : Imss := {}
  deriving Repr, Inhabited

/-- Art. 113-F "TABLA ANUAL": the single rate on the whole revenue (not a marginal rate). -/
def resicoRate (revC : Int) : Int :=
  match resicoAnnual.find? (fun p => revC ≤ p.1) with
  | some p => p.2
  | none => 0

/-- RESICO annual tax on revenue `revC` centavos, ticks: "Tasa aplicable" × the whole revenue. -/
def resicoTicks (revC : Int) : Int := resicoRate revC * pos revC

/-- Art. 93 fr. IV: the exempt part of a pension, 15 UMA a day for 365 days, centavos. -/
def pensionExempt (Y : MxYear := mxY2025) : Int := pensionExemptDays * Y.umaDaily * 365

/-- The art. 152 tax of one variant (with or without the art. 140 gross-up), ticks, and its pieces. -/
structure Variant where
  acum : Int
  don : Int
  ppr : Int
  base : Int
  tax152 : Int
  credit : Int
  isr : Int
  divAcc : Int

def variant (p : PersonIn) (other totalIncome divC : Int) (gross : Bool) : Variant :=
  let divAcc := if gross then mulDivHU divC grossUpNum grossUpDen else divC
  let credit := if gross then mulDivHU divAcc citRate BP else 0
  let acum := other + divAcc
  -- art. 151 fr. III: donativos up to 7 % of ingresos acumulables (of the previous year: taken as this year's)
  let don0 := min (cts (pos p.charitable)) (mulDivHU (pos acum) donPct BP)
  -- art. 151 último párrafo: the overall cap (fr. V excluded)
  let don := min don0 (min (dedCapUma * (mxYearAll p.wage.yr).umaAnnual) (mulDivHU (pos totalIncome) dedCapPct BP))
  -- art. 151 fr. V: 10 % of ingresos acumulables, at most 5 annual UMA
  let ppr := min (cts (pos p.ppr)) (min (mulDivHU (pos acum) pprPct BP) (pprCapUma * (mxYearAll p.wage.yr).umaAnnual))
  let base := pos (acum - don - ppr)
  let t := tarifaTicks (tarifa152Y p.wage.yr) base
  let sub := p.wage.subsidyTotal
  -- SE-2024 art. Tercero fr. III: no tax and nothing paid when the subsidies exceed the tax; art. 152: the
  -- company's tax credited under art. 140 is not refunded ("únicamente se podrá solicitar la devolución ... del
  -- impuesto efectivamente pagado o que le hubiera sido retenido")
  let isr := pos (t - sub * BP - credit * BP)
  { acum, don, ppr, base, tax152 := t, credit, isr, divAcc }

/-- Leaving RESICO during the year (art. 113-E tercer párrafo: "a partir del mes siguiente a la fecha en que tales
ingresos excedan la referida cantidad"; RMF 2025 regla 3.13.5 fr. I: the RESICO payments of the earlier months
stay definitive and the general regime covers "únicamente ... los meses que restan"). With revenue earned evenly,
the months in RESICO are those up to and including the month in which cumulative revenue first exceeds
3,500,000: `min 12 (⌊42,000,000 / R⌋ + 1)`. -/
def resicoMonths (revC : Int) : Int :=
  if revC ≤ resicoLimit then 12 else min 12 (resicoLimit * 12 / revC + 1)

/-- RESICO tax, ticks. Up to 3,500,000 the annual table (art. 113-F). Above, the months spent in RESICO paid the
monthly table (art. 113-E) on revenue above 291,666.67 a month, i.e. 2.50 %; when the excess comes only in
December the whole year stays in RESICO and the annual table has no row for it (reading: its last rate, 2.50 %). -/
def resicoTax (revC : Int) : Int :=
  if revC ≤ resicoLimit then resicoTicks revC
  else divR .halfUp (250 * revC * resicoMonths revC) 12

def personTax (p : PersonIn) : PersonOut :=
  let w := p.wage
  let revenue := if p.seRevenue = 0 then p.se else p.seRevenue
  let resicoApplies := p.regime == "resico"
  let rm := if resicoApplies then resicoMonths (cts revenue) else 0
  let company := p.regime == "company"
  let cit := if company then mulDivHU (cts (pos p.se)) citRate BP else 0
  let companyDiv := if company then cts (pos p.se) - cit else 0
  let seAcc := if company then 0 else if resicoApplies then mulDivHU (cts p.se) (12 - rm) 12 else cts p.se
  let pensionTaxable := pos (cts p.pension - pensionExempt (mxYearAll p.wage.yr))
  let rentAcc := if p.rentBlind then cts p.rental - mulDivHU (cts p.rental) rentBlindPct BP else cts p.rental
  let divC := cts (pos p.dividends) + companyDiv
  let other := w.taxable + pensionTaxable + seAcc + rentAcc + cts p.interest
  let totalIncome := cts (pos w.wages + pos p.pension + pos p.rental + pos p.interest + pos p.dividends
    + pos p.capitalGains) + (if resicoApplies then cts revenue else if company then companyDiv else cts p.se)
  let vNo := variant p other totalIncome divC false
  let vYes := variant p other totalIncome divC true
  let useCredit := if p.divCredit == "credit" then true else if p.divCredit == "none" then false
    else decide (0 < divC) && decide (vYes.isr < vNo.isr)
  let v := if useCredit then vYes else vNo
  { exemptWages := w.exempt, taxableWages := w.taxable, pensionTaxable, seAccumulated := seAcc,
    rentalAccumulated := rentAcc, dividendsAccumulated := v.divAcc, acumulables := v.acum, totalIncome,
    donations := v.don, ppr := v.ppr, base := v.base, tax152 := v.tax152, subsidy := w.subsidyTotal,
    subsidyApplied := w.subsidyApplied, subsidyMonths := w.subsidyMonths, dividendCredit := v.credit,
    isr := v.isr, usedDividendCredit := useCredit,
    divAdditional := divC * divAddRate, cgTax := cts (pos p.capitalGains) * cgRate,
    resicoTax := if resicoApplies then resicoTax (cts revenue) else 0, resicoApplies, resicoMonths := rm,
    companyCit := cit, withheld := w.withheldTotal, imss := imssOf w }

/-- The person's federal ISR in pesos: the annual tax and the definitive 10 % taxes and RESICO, each paid
separately and rounded by CFF art. 20. -/
def PersonOut.isrPesos (o : PersonOut) : Int :=
  cffPesos (ticksToCentavos o.isr) + cffPesos (ticksToCentavos o.divAdditional)
    + cffPesos (ticksToCentavos o.cgTax) + cffPesos (ticksToCentavos o.resicoTax)

end MxTax
