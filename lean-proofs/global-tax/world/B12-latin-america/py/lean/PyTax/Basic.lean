import TaxKernel.World

/-!
# Paraguay 2025: Impuesto a la Renta Personal (IRP), rentas de servicios personales and rentas del capital; IPS

Sources (read 2026-11-20):
* Ley 6380/2019 "De modernizacion y simplificacion del sistema tributario nacional", text served by the DNIT
  (`https://www.dnit.gov.py/web/portal-institucional/w/d-ley-n-6380-19`): arts. 43 (IDU), 60 (capital 8 %),
  62-69 (servicios personales), 139 (amounts in arts. 62 and 69 "podran ser actualizados por el Poder Ejecutivo").
  The DNIT decree list (`/web/portal-institucional/decretos`) shows no decree updating the art. 62/69 amounts, and its
  law list no amendment of arts. 62-69 (only Ley 7067/2023 on art. 100): the printed amounts are taken as in force.
* IPS employee contribution 9 %: IPS "Tabla de bases minimas imponibles y porcentajes de aportes al IPS"
  (portal.ips.gov.py contenido.php?c=372, image 1786135176.jpg, sha256 914b8c6a...): "TRABAJADOR 9%" (official
  secondary; the table is headed Resolucion MTESS 670/2026, so the rate is confirmed for 2026 and assumed for 2025).

Unit: the individual (art. 62 "Toda persona fisica"). Amounts in guaranies.
-/

namespace PyTax
open TaxKernel

/-- Art. 62 and art. 69 last paragraph: a person is liable once gross income from personal services "sea superior a
G. 80.000.000"; at or below that amount "no estara obligado al pago del impuesto". -/
def threshold : Int := 80000000
/-- Art. 69: "Hasta G 50.000.000 8%; Desde G 50.000.001 hasta G 150.000.000 9%; Igual o mayor a G 150.000.001 10%",
applied band by band ("a la porcion de renta neta comprendida en cada tramo"). -/
def art69 : Schedule := Schedule.ofList [(0, 800), (50000000, 900), (150000000, 1000)]
/-- Art. 60: "La tasa aplicable para las rentas y ganancias del capital sera del 8% (ocho por ciento)". -/
def capitalRate : Int := 800
/-- Art. 43 num. 1: IDU "8% (ocho por ciento) cuando el perceptor de los dividendos ... sea una persona fisica ...
residente en el pais". -/
def iduRate : Int := 800
/-- IPS table (official secondary): employee 9 %. -/
def ipsRate : Int := 900

structure Person where
  gross : Int
  ips : Int
  rentaBruta : Int
  rentaNeta : Int
  liable : Bool
  tax : Int
  deriving Repr

/-- Servicios personales of one person. `expenses` = documented deductible expenditure of art. 64 (personal and
family spending on food, clothing, housing, health, education ...), an optional input (default 0). -/
def person (wage se expenses : Int) : Person :=
  let gross := pos wage + pos se
  let ips := divR .halfUp (pos wage * ipsRate) BP
  -- art. 63: the worker's social-security contributions are excluded from the renta bruta
  let rentaBruta := pos (gross - ips)
  let rentaNeta := pos (rentaBruta - pos expenses)
  let liable := decide (gross > threshold)
  let tax := if liable then art69.tax { mode := .halfUp, step := 1 } rentaNeta else 0
  { gross, ips, rentaBruta, rentaNeta, liable, tax }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let exps := (c.int? "pyDeductibleExpenses").getD 0
  let ps := ((c.adults.zip (sh exps))).map fun (a, e) => person a.wages a.selfEmployment e
  let labour := sumInts (ps.map (·.tax))
  let idu := divR .halfUp (pos c.dividends * iduRate) BP
  let capital := divR .halfUp ((pos c.rentalIncome + pos c.capitalGains) * capitalRate) BP
  let unsup :=
    ["art. 64 deductible personal and family expenses taken as 0 (pass pyDeductibleExpenses, household total, split equally): with documented spending the IRP falls towards a tax on saving",
     "IPS 9 % applied to all wages (the IPS base excludes the aguinaldo; minimum base 'base minima imponible' not applied); rate from the 2026 IPS table (official secondary)",
     "first year of liability (art. 62: expenses only from the day after the threshold is passed) not modelled: steady state"] ++
    (if c.interest != 0 then ["interest: arts. 57-60 exemptions not checked; not taxed"] else []) ++
    (if c.rentalIncome != 0 || c.capitalGains != 0 then ["rent and capital gains: 8 % (art. 60) on the gross amount; art. 58-59 net-income rules not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pensions: not modelled"] else [])
  Out.make c "PY" "PYG" (labour + capital) (surtaxes := [("IDU_dividendos", idu)])
    (employeeSocial := sumInts (ps.map (·.ips)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.rentaNeta))),
                Out.d "rentaBruta" (sumInts (ps.map (·.rentaBruta))),
                Out.d "irpServicios" labour, Out.d "irpCapital" capital,
                Out.d "liablePersons" (ps.filter (·.liable)).length])
    (unsupported := unsup)

def country : Country :=
  { code := "PY", name := "Paraguay (IRP servicios personales y capital; IDU; IPS)", currency := "PYG", year := "2025",
    compute := out }

/- At exactly G 80.000.000 nothing is due; one guarani more and the whole renta neta is taxed. -/
#guard (person 80000000 0 0).tax == 0
#guard (person 80000001 0 0).tax == 4000000 + 2052000

end PyTax
