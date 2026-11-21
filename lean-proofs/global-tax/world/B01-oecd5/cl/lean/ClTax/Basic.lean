import ClTax.Params

/-!
# Chile 2025: impuesto único de segunda categoría (monthly) with the global complementario overlay (annual)

Unit: the individual (LIR art. 52: the tax falls on "toda persona natural"; no joint assessment).

Per person and month m (wages paid in 12 equal instalments; pensions likewise, from a second payer):
1. contributions (employee): AFP 10 % and health 7 % on the wage up to 87,8 UF, seguro de cesantía 0,6 % up to
   131,8 UF in January and 131,9 UF from February (indefinite contract assumed), at the UF of the last day of the previous month;
2. the base of art. 43 N° 1 is the wage less those contributions (art. 42 N° 1: "exceptuadas las imposiciones
   obligatorias ... y las cotizaciones ... de salud, calculadas sobre el límite máximo imponible ... Asimismo, se
   exceptúa la cotización para el seguro de desempleo");
3. impuesto único = the art. 43 scale at the month's UTM.
Annual (art. 47, 52, 54, 56): when a person has income other than art. 42 N° 1 from one payer (a second payer,
interest, rent, fees), the art. 52 scale at the December UTA is applied to all income, art. 42 N° 1 income and the
withheld impuesto único are adjusted by the IPC (art. 54 N° 3 penúltimo inciso, art. 75: from the end of the month
before receipt to the end of November), and the adjusted impuesto único is credited (art. 54 N° 3 inc. 3; art. 56:
the excess is not refunded) — kernel `overlayTax` with credit. A single-payer wage earner may also reliquidate
(art. 47 inc. 3) for a refund: option `--reliquidar` (election, cheapest first).
-/

namespace ClTax
open TaxKernel

def months : List Nat := [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

def at! (l : List Int) (i : Nat) : Int := l.getD i 0

/-- Month `i` (0..11) of an annual amount: equal instalments, the remainder to later months. -/
def monthOf (annual : Int) (i : Nat) : Int := annual * ((i : Int) + 1) / 12 - annual * (i : Int) / 12

/-- A cap in tenths of a UF in pesos at a UF value in centavos (half-up to the peso: reading). -/
def ufCap (tenths ufCent : Int) : Int := divR .halfUp (tenths * ufCent) 1000

/-- Employee contributions on a monthly wage in month `i`: (AFP incl. the AFP's commission `cm` in basis points of the
capped wage, health, cesantía), half-up to the peso. The commission (DL 3.500 art. 17 inc. 2: "cotización adicional",
fixed by each AFP) is part of the deductible compulsory contributions (LIR art. 42 N° 1 "imposiciones obligatorias");
its rate is the AFP's, not the statute's: input `clAfpCommission` (basis points), default 0 (round D2). -/
def wageContrib (cm : Int) (g : Int) (i : Nat) : Int × Int × Int :=
  let uf := at! ufPrev i
  let b := min g (ufCap topeUFTenths uf)
  let bc := min g (ufCap (topeAFCOfMonth i) uf)
  (divR .halfUp (b * (rateAFP + cm)) BP, divR .halfUp (b * rateHealth) BP, divR .halfUp (bc * rateAFC) BP)

/-- The health part (7 %) of a year's wage contributions (for the OECD convention below). -/
def wageHealthYear (annual : Int) : Int :=
  if annual ≤ 0 then 0 else
  months.foldl (fun acc i => let (_, h, _) := wageContrib 0 (monthOf annual i) i; acc + h) 0

/-- Pensioner's health contribution (DL 3.500 art. 85, cap 60 UF; UF of the previous month-end used: reading). -/
def pensionContrib (p : Int) (i : Nat) : Int :=
  divR .halfUp (min p (ufCap pensionCapUFTenths (at! ufPrev i)) * ratePensionHealth) BP

/-- Impuesto único on a monthly base in month `i` (pesos, half-up: reading). -/
def iu (base : Int) (i : Nat) : Int := (scale (at! utm i)).tax Rule.unitHalfUp base

/-- IPC adjustment factor of month `i` in tenths of a percent, rounded half-up, negative variations taken as 0
(SII: "cuando el porcentaje de reajuste da como resultado un valor negativo, dicho valor no debe considerarse"). -/
def reajTenths (i : Nat) : Int := pos (divR .halfUp ((ipcNov - at! ipcPrev i) * 1000) (at! ipcPrev i))

def reaj (x : Int) (i : Nat) : Int := x + divR .halfUp (x * reajTenths i) 1000

/-- One payer's year of art. 42 N° 1 income: monthly bases, impuesto único, contributions, adjusted figures. -/
structure Payer where
  contrib : Int := 0
  base : Int := 0
  tax : Int := 0
  baseAdj : Int := 0
  taxAdj : Int := 0
  deriving Repr

def payerYear (perMonth : Int → Nat → Int × Int) (annual : Int) : Payer :=
  if annual ≤ 0 then {} else
  months.foldl (fun acc i =>
    let g := monthOf annual i
    let (ct, b) := perMonth g i
    let t := iu b i
    { contrib := acc.contrib + ct, base := acc.base + b, tax := acc.tax + t,
      baseAdj := acc.baseAdj + reaj b i, taxAdj := acc.taxAdj + reaj t i }) {}

def wageMonth (cm : Int) (g : Int) (i : Nat) : Int × Int :=
  let (a, h, c) := wageContrib cm g i
  (a + h + c, g - a - h - c)

def pensionMonth (p : Int) (i : Nat) : Int × Int :=
  let h := pensionContrib p i
  (h, p - h)

/-- The annual scale of art. 52 at the December UTA. -/
def gcTax (x : Int) : Int := (scale utaDec).tax Rule.unitHalfUp x

/-- One person's year. -/
structure Person where
  wage : Payer
  pension : Payer
  fees : Int            -- art. 42 N° 2 income after the art. 50 presumed expenses
  interest : Int        -- art. 20 N° 2 interest after the art. 57 exemption
  rent : Int
  overlay : Bool
  gc : Int              -- art. 52 tax on all income
  credit : Int          -- adjusted impuesto único
  extra : Int           -- global complementario (or art. 47 reliquidation) payable
  deriving Repr

def person (reliquidar : Bool) (cm : Int) (wage pension fees interest rent : Int) : Person :=
  let w := payerYear (wageMonth cm) wage
  let p := payerYear pensionMonth pension
  let feesNet := if fees ≤ 0 then 0 else fees - min (divR .down (fees * presumedRate) BP) (presumedCapUTA * utaDec)
  let onlyDependent := fees ≤ 0 && rent ≤ 0
  let intTaxable := if interest ≤ 0 then 0 else
    if onlyDependent && interest ≤ interestExemptUTM * 69542 then 0 else interest
  let other := feesNet + intTaxable + pos rent
  let twoPayers := wage > 0 && pension > 0
  let overlay := other > 0 || twoPayers || reliquidar
  let total := w.baseAdj + p.baseAdj + other
  let credit := w.taxAdj + p.taxAdj
  let gc := if overlay then gcTax total else 0
  let extra :=
    if other > 0 then pos (gc - credit)                     -- art. 54 N° 3, 56: excess credit not refunded
    else if twoPayers then (if reliquidar then gc - credit else pos (gc - credit))  -- art. 47 inc. 1 / inc. 3
    else if reliquidar then min 0 (gc - credit)             -- art. 47 inc. 3: optional, for a refund only
    else 0
  { wage := w, pension := p, fees := feesNet, interest := intTaxable, rent := pos rent, overlay, gc, credit, extra }

/-- OECD Taxing Wages convention (`--oecd`; Taxing Wages 2025, Part II, Chile chapter, the methodology the OECD publishes
for its Chile tables): (1) "Employee social security contributions in respect of pensions and unemployment are not
classified as taxes in this report; though they are included in modelling as deductions for income tax": employeeSocial
= the 7 % health contribution only; (2) the AFP commission is deducted at the OECD's average, note 5 "Average cost in
2024 was 1.15% of gross income" (the latest published; used for 2025 unless `clAfpCommission` is given); (3) "In order
to estimate taxes, tax rates are applied on an annual basis, on the annual average income", the scale in UTA, the UTM
being the "Value up to 18 June" (note 1; 2024 table: UTM 65 967, UTA 791 604, first threshold 13,5 x 791 604): the art.
43 scale at 12 x the June UTM (68.785 in 2025) on the year's base. -/
def oecdCommission : Int := 115
def julyUTA : Int := 12 * at! utm 5

def out (args : List String) (c : Canon) : Out :=
  let reliq := args.contains "--reliquidar" || (c.bool? "reliquidar").getD false
  let oecd := args.contains "--oecd"
  let cm := (c.int? "clAfpCommission").getD (if oecd then oecdCommission else 0)
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let ps := ((c.adults.zip (sh c.interest)).zip (sh c.rentalIncome)).map fun ((a, i), r) =>
    person reliq cm a.wages a.pension a.selfEmployment i r
  let wageTax (p : Person) : Int := if oecd then (scale julyUTA).tax Rule.unitHalfUp p.wage.base else p.wage.tax
  let iuTot := sumInts (ps.map fun p => wageTax p + p.pension.tax)
  let extra := sumInts (ps.map (·.extra))
  let social := if oecd then sumInts (c.adults.map fun a => wageHealthYear a.wages) + sumInts (ps.map (·.pension.contrib))
    else sumInts (ps.map fun p => p.wage.contrib + p.pension.contrib)
  let unsup :=
    (if c.dividends != 0 then ["dividends: global complementario with the art. 56 N° 3 first-category credit depends on the company's regime and registers (LIR art. 14); not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: listed shares (LIR art. 107 / art. 17 N° 8) not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: honorarios under LIR art. 42 N° 2 with art. 50 presumed expenses; the independent worker's contributions (DL 3.500 art. 89-92) are not modelled"] else []) ++
    (if c.rentalIncome != 0 then ["rentalIncome: taken as net renta efectiva in global complementario; DFL 2 exemptions and expenses not modelled"] else []) ++
    (if c.charitable != 0 || c.pensionContributions != 0 then ["charitable/pensionContributions: LIR art. 42 bis (APV) and donation credits not modelled"] else []) ++
    (if (c.int? "clAfpCommission").isNone && !oecd then ["AFP commission (DL 3.500 art. 17 inc. 2, fixed by each AFP, not by statute): pass clAfpCommission (basis points) to deduct it"] else []) ++
    ["asignación familiar, aporte familiar permanente, bolsillo familiar electrónico and the education credit of LIR art. 55 ter not modelled"] ++
    (if oecd then ["--oecd: OECD Taxing Wages conventions (employeeSocial = health only; AFP commission 1,15 %; annual scale at 12 x the June UTM)"] else [])
  Out.make c "CL" "CLP" (iuTot + extra) (employeeSocial := social)
    (detail := [Out.d "impuestoUnico" iuTot, Out.d "globalComplementario" extra,
                Out.d "taxableIncome" (sumInts (ps.map fun p => p.wage.base + p.pension.base + p.fees + p.interest + p.rent)),
                Out.d "afpHealthCesantia" social,
                Out.dBool "annualOverlay" (ps.any (·.overlay))])
    (unsupported := unsup)

def country : Country :=
  { code := "CL", name := "Chile (impuesto único de segunda categoría + global complementario)", currency := "CLP",
    year := "2025", compute := out [], computeWith := out }

end ClTax
