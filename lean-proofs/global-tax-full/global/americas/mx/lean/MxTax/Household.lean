import MxTax.Annual

/-!
# The canonical household (`cmp/shared/CONTRACT.md`) → Mexico

Each adult is taxed alone (LISR Título IV has no joint return; `married` changes nothing; a *sociedad conyugal*
is read through `mxInvestmentOwner`). Investment income is split equally between two adults by default (the
contract's suggestion; LISR art. 140: "el ingreso lo percibe el propietario del título valor"), `charitable` and
`pensionContributions` are deducted by the adult with the higher wages + self-employment (art. 151: the deduction
belongs to whoever pays; the highest earner gains most). Children change nothing: there is no federal child tax
credit or universal child benefit.

Mexico-only optional input fields (all optional; defaults in brackets):
* per adult: `mxAguinaldoDays` [15], `mxVacationDays` [12], `mxPrimaPct` (percent) [25], `mxPrevisionSocial`
  (pesos of the wage paid as exempt-eligible previsión social, e.g. vales de despensa) [0], `mxAsimilado`
  (wages paid as asimilados a salarios: no IMSS, no subsidy) [false], `mxRegime`
  ("general" | "resico" | "company") ["general"], `mxSelfEmploymentRevenue` (pesos, gross revenue) [= selfEmployment].
* household: `mxInvestmentOwner` ("split" | "adult1" | "adult2") ["split"], `mxRealInterest` (pesos of real
  interest, art. 134) [= interest], `mxImss` ("calendar" | "oecd") ["calendar"], `mxDividendCredit`
  ("best" | "credit" | "none") ["best"], `mxRentalDeduction` ("blind" | "actual") ["blind"].
-/

namespace MxTax
open TaxKernel Lean

def adultRaw (c : Canon) (i : Nat) : Json := (arrField c.raw "adults").getD i Json.null

def jStrD (j : Json) (k : String) (d : String) : String :=
  match j.getObjVal? k with
  | .ok (.str s) => s
  | _ => d

def personsOf (c : Canon) : List PersonIn :=
  let n := c.adults.length
  let owner := (c.str? "mxInvestmentOwner").getD "split"
  let share (x : Int) (i : Nat) : Int :=
    if n ≤ 1 then x
    else if owner == "adult1" then (if i = 0 then x else 0)
    else if owner == "adult2" then (if i = 1 then x else 0)
    else if i = 0 then half1 x else half2 x
  let interest := (c.int? "mxRealInterest").getD c.interest
  let earn := c.adults.map Adult.earnings
  let top : Nat := if n ≥ 2 && earn.getD 1 0 > earn.getD 0 0 then 1 else 0
  let imssOecd := (c.str? "mxImss").getD "calendar" == "oecd"
  let divCredit := (c.str? "mxDividendCredit").getD "best"
  let rentBlind := (c.str? "mxRentalDeduction").getD "blind" != "actual"
  (List.range n).map fun i =>
    let a := c.adults.getD i {}
    let r := adultRaw c i
    { wage := { wages := a.wages, aguinaldoDays := intField r "mxAguinaldoDays" 15,
                vacationDays := intField r "mxVacationDays" (if c.year = 2022 then 6 else 12), primaPct := 100 * intField r "mxPrimaPct" 25,
                prevision := intField r "mxPrevisionSocial" 0, imssOecd,
                asimilado := boolField r "mxAsimilado" false, yr := c.year },
      pension := a.pension, se := a.selfEmployment,
      seRevenue := intField r "mxSelfEmploymentRevenue" a.selfEmployment,
      regime := jStrD r "mxRegime" "general",
      interest := share interest i, dividends := share c.dividends i, capitalGains := share c.capitalGains i,
      rental := share c.rentalIncome i,
      charitable := if i = top then c.charitable else 0,
      ppr := if i = top then c.pensionContributions else 0,
      rentBlind, divCredit }

def j (x : Int) : Json := toJson x
def pesos (centavos : Int) : Json := toJson (cffPesos centavos)
def pesosT (ticks : Int) : Json := toJson (cffPesos (ticksToCentavos ticks))

def personJson (p : PersonIn) (o : PersonOut) : Json :=
  Json.mkObj [
    ("wages", j p.wage.wages), ("regime", Json.str p.regime),
    ("aguinaldo", pesos p.wage.aguinaldo), ("primaVacacional", pesos p.wage.prima),
    ("exemptAguinaldo_art93XIV", pesos p.wage.exAguinaldo), ("exemptPrima_art93XIV", pesos p.wage.exPrima),
    ("exemptPrevisionSocial_art93", pesos p.wage.exPrevision),
    ("exemptWages", pesos o.exemptWages), ("taxableWages", pesos o.taxableWages),
    ("pensionTaxable", pesos o.pensionTaxable), ("selfEmploymentAccumulated", pesos o.seAccumulated),
    ("rentalAccumulated", pesos o.rentalAccumulated), ("dividendsAccumulated", pesos o.dividendsAccumulated),
    ("ingresosAcumulables", pesos o.acumulables), ("totalIncomeForCaps", pesos o.totalIncome),
    ("deduccionesPersonales", Json.mkObj [("donativos_151III", pesos o.donations),
      ("aportacionesRetiro_151V", pesos o.ppr)]),
    ("taxableIncome_art152", pesos o.base), ("tax152", pesosT o.tax152),
    ("subsidioEmpleo", Json.mkObj [("months", j o.subsidyMonths), ("entitlement", pesos o.subsidy),
      ("appliedMonthly", pesos o.subsidyApplied)]),
    ("dividendCredit_art140", pesos o.dividendCredit), ("usedDividendGrossUp", Json.bool o.usedDividendCredit),
    ("isrAnnual", pesosT o.isr), ("dividendAdditional10_art140", pesosT o.divAdditional),
    ("capitalGains10_art129", pesosT o.cgTax),
    ("resico", Json.mkObj [("applies", Json.bool o.resicoApplies), ("months", j o.resicoMonths),
      ("tax", pesosT o.resicoTax)]),
    ("ownCompanyCit30", pesos o.companyCit),
    ("withheldMonthly_art96", pesos o.withheld),
    ("annualMinusWithheld", toJson (cffPesos (ticksToCentavos o.isr) - cffPesos o.withheld)),
    ("imss", Json.mkObj [("enfermedadExcedente_106II", pesos o.imss.excess),
      ("prestacionesDinero_107", pesos o.imss.dinero), ("gastosMedicosPensionados_25", pesos o.imss.pensionados),
      ("invalidezVida_147", pesos o.imss.invalidez), ("cesantiaVejez_168II", pesos o.imss.cesantia),
      ("oecdSsc", pesos o.imss.oecdSsc)])]

def out (c : Canon) : Out :=
  let ps := personsOf c
  let os := ps.map personTax
  let it := sumInts (os.map PersonOut.isrPesos)
  let ss := sumInts (os.map fun o => cffPesos o.imss.total)
  let oecdSsc := sumInts (os.map fun o => cffPesos o.imss.oecdSsc)
  let cit := sumInts (os.map fun o => cffPesos o.companyCit)
  let base := sumInts (os.map fun o => cffPesos o.base)
  let t152 := sumInts (os.map fun o => cffPesos (ticksToCentavos o.tax152))
  let surt : List (String × Int) := if cit = 0 then [] else [("ownCompanyCIT_art9", cit)]
  let uns : List String :=
    ["interest: accumulated as given; the art. 134 inflation adjustment needs the principal (use mxRealInterest)",
     "donativos: the 7% cap uses this year's ingresos acumulables (the statute uses the previous year's)",
     "aguinaldo/prima vacacional: inside wages, W/365 a day (OECD convention); PTU, overtime, primas dominicales not modelled",
     "salario mínimo rule of art. 96 (no withholding) not modelled; LSS art. 36 (employer pays the quota) is",
     "state taxes on income (cedular taxes on professional income or rent in some states) not modelled",
     "selfEmployment: net profit (general regime); IMSS for the self-employed is voluntary (not modelled)"]
    ++ (if c.year = 2022 then ["2022: Anexo 8 RMF 2022 tarifas, the 2013 subsidy table (its cash payment of excess subsidy not modelled), 6 vacation days (LFT art. 76 before the DOF 27-12-2022 reform), January UMA 89.62 (INEGI, DOF 08-01-2021)"] else if c.year = 2023 then ["2023: the 2013 subsidy table all year; its cash payment of a subsidy larger than the month's tax (monthly bases up to 7,382.33) is not modelled; the 2023 monthly withholding tarifa taken equal to 2024's; salario mínimo 207.44 (CONASAMI, DOF 07-12-2022)"] else if c.year = 2024 then ["2024: January-April under the 2013 subsidy table (A8-2024), May-December SE-2024; the 2013 decree's cash payment of a subsidy larger than the month's tax (monthly bases up to 7,382.33) is not modelled; salario mínimo 248.93 (CONASAMI, DOF 12-12-2023)"]
        else if c.year ≠ 2025 then [s!"tax year {c.year} not modelled: the 2025 law was applied"] else [])
  Out.make c "MX" "MXN" it (surtaxes := surt) (employeeSocial := ss)
    (detail := [Out.dStr "taxYear" (if c.year = 2024 ∨ c.year = 2023 ∨ c.year = 2022 then s!"ejercicio fiscal {c.year} (calendar year); federal ISR + IMSS employee quotas" else "ejercicio fiscal 2025 (calendar year); federal ISR + IMSS employee quotas"),
      Out.d "taxableIncome" base, Out.d "taxBeforeCredits" t152, Out.d "imssOecdSsc" oecdSsc,
      ("persons", Json.arr ((ps.zip os).map fun (p, o) => personJson p o).toArray)])
    (unsupported := uns)

/-- **`mxtax --oecd` (convention mode of the tests, never the default):** the OECD's IMSS arithmetic, i.e. the input
field `mxImss: "oecd"` (FINDINGS F2: the annual 2025 UMA, 113.14 × 30.4 × 12, for the whole year; the statute uses the
daily UMA, 2024 value in January, the UMA being updated each 1 February, Ley para Determinar el Valor de la UMA art. 5;
LSS art. 106 fr. II "tres veces el salario mínimo general diario"). Tests round 1. -/
def oecdCanon (c : Canon) : Canon := { c with raw := c.raw.setObjVal! "mxImss" (Lean.Json.str "oecd") }

def country : Country :=
  { code := "MX", name := "Mexico (federal ISR + IMSS)", currency := "MXN", year := "2025", compute := out,
    computeWith := fun args c => if args.contains "--oecd" then out (oecdCanon c) else out c }

end MxTax
