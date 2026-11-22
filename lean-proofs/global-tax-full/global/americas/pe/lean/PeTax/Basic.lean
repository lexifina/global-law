import TaxKernel.World

/-!
# Peru 2025: Impuesto a la Renta of a domiciled individual (rentas del trabajo + rentas del capital)

Sources (all read 2026-11-20):
* TUO de la Ley del Impuesto a la Renta (D.S. 179-2004-EF), SUNAT's official consolidated text
  `https://www.sunat.gob.pe/legislacion/renta/ley/capvi.pdf` (arts. 36, 45, 46; file dated 2025-11-03),
  `capvii.pdf` (arts. 52-A, 53), `capiv.pdf` (art. 19 i), `capv.pdf` (art. 34).
* D.S. 260-2024-EF art. 1 (El Peruano 17-12-2024 p. 19): "Durante el año 2025, el valor de la Unidad Impositiva
  Tributaria (UIT) ... será de Cinco Mil Trescientos Cincuenta Soles" (S/ 5 350).
* Ley 26504 (1995), Segunda Disposición Transitoria: SNP contributions "no serán menores a 13% de la remuneración
  asegurable" (gob.pe copy of the law as published).

Unit: the individual (art. 53 "personas naturales"); capital income of a couple split equally (no sociedad conyugal
election modelled). Everything annual, in soles; tax rounded half-up to the sol.
-/

namespace PeTax
open TaxKernel

/-- D.S. 260-2024-EF art. 1: UIT 2025 = S/ 5 350. -/
def uit : Int := 5350

/-- LIR art. 53 (Ley 30296, from 2015): "Hasta 5 UIT 8% / Más de 5 UIT hasta 20 UIT 14% / Más de 20 UIT hasta 35 UIT 17%
/ Más de 35 UIT hasta 45 UIT 20% / Más de 45 UIT 30%" on the sum of the renta neta del trabajo and foreign income. -/
def art53Units : List (Int × Int) := [(0, 800), (5, 1400), (20, 1700), (35, 2000), (45, 3000)]
def art53 : Schedule := Schedule.ofUnits art53Units .halfUp 1 uit

/-- LIR art. 46 first paragraph: "un monto fijo equivalente a siete (7) Unidades Impositivas Tributarias". -/
def fixedDeductionUIT : Int := 7
/-- LIR art. 46 fourth-last paragraph: the additional gastos "no podrán exceder en conjunto de tres (3) UIT". -/
def extraDeductionCapUIT : Int := 3
/-- LIR art. 45: cuarta categoría "el veinte por ciento (20%) ... hasta el límite de 24 UIT". -/
def cuartaRate : Int := 2000
def cuartaCapUIT : Int := 24
/-- LIR art. 52-A first paragraph: "seis coma veinticinco por ciento (6,25%) sobre sus rentas netas del capital". -/
def capitalRate : Int := 625
/-- LIR art. 52-A last paragraph (D.Leg. 1261): dividends "gravados con la tasa de cinco por ciento (5%)". -/
def dividendRate : Int := 500
/-- LIR art. 36: primera categoría net = gross less "el veinte por ciento (20%) del total de la renta bruta". -/
def rentDeductionRate : Int := 2000
/-- Ley 26504, 2ª Disp. Transitoria: SNP "no serán menores a 13% de la remuneración asegurable". -/
def snpRate : Int := 1300

structure Person where
  quinta : Int
  cuartaNet : Int
  fixedDed : Int
  extraDed : Int
  netWork : Int
  workTax : Int
  capitalBase : Int
  capitalTax : Int
  dividendTax : Int
  snp : Int
  deriving Repr

/-- One person: wages and pensions are quinta categoría (art. 34 a, b); self-employment is cuarta (art. 33) with the
art. 45 20 % deduction; art. 46 7 UIT once on cuarta + quinta plus up to 3 UIT of qualifying paid expenses. -/
def person (wage pension se rent divs extraClaim : Int) : Person :=
  let quinta := pos wage + pos pension
  let cuartaGross := pos se
  let cuartaNet := cuartaGross - min (divR .down (cuartaGross * cuartaRate) BP) (cuartaCapUIT * uit)
  let gross := quinta + cuartaNet
  let fixedDed := min gross (fixedDeductionUIT * uit)
  let extraDed := min (pos (gross - fixedDed)) (min (pos extraClaim) (extraDeductionCapUIT * uit))
  let netWork := pos (gross - fixedDed - extraDed)
  let workTax := art53.tax { mode := .halfUp, step := 1 } netWork
  let rentNet := pos rent - divR .down (pos rent * rentDeductionRate) BP
  let capitalTax := divR .halfUp (rentNet * capitalRate) BP
  let dividendTax := divR .halfUp (pos divs * dividendRate) BP
  let snp := divR .halfUp (pos wage * snpRate) BP
  { quinta, cuartaNet, fixedDed, extraDed, netWork, workTax, capitalBase := rentNet, capitalTax, dividendTax, snp }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let extra := (c.int? "peDeductibleExpenses").getD 0
  let rows := ((c.adults.zip (sh c.rentalIncome)).zip (sh c.dividends))
  let ps := (rows.zipIdx).map fun (((a, r), d), k) =>
    person a.wages a.pension a.selfEmployment r d (if k == 0 then extra else 0)
  let work := sumInts (ps.map (·.workTax))
  let cap := sumInts (ps.map (·.capitalTax))
  let div := sumInts (ps.map (·.dividendTax))
  let afp := c.str? "pePension" == some "afp"
  let unsup :=
    ["SNP 13 % applied to all wages: Ley 30334 (gratificaciones not subject to contributions) and the SNP floor/AFP premium and commission not reached"] ++
    (if afp then ["pePension=afp: AFP contribution not modelled (TUO SPP art. 30 not reached); employeeSocial = 0"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: LIR arts. 2, 21, 52-A (6,25 %) and the 5 UIT exemption for listed securities not modelled; ignored"] else []) ++
    (if c.charitable != 0 || c.pensionContributions != 0 then ["charitable/pensionContributions: LIR art. 49 donations not modelled"] else []) ++
    (if extra == 0 then ["art. 46 additional deduction (30 % of rent, medical and professional fees; 3 UIT cap) taken as 0: pass peDeductibleExpenses (the qualifying amount) to use it"] else [])
  Out.make c "PE" "PEN" (work + cap) (surtaxes := [("dividendos_art52A", div)])
    (employeeSocial := if afp then 0 else sumInts (ps.map (·.snp)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.netWork))),
                Out.d "rentaNetaTrabajo" (sumInts (ps.map (·.netWork))),
                Out.d "deduccion7UIT" (sumInts (ps.map (·.fixedDed))),
                Out.d "deduccionGastos3UIT" (sumInts (ps.map (·.extraDed))),
                Out.d "impuestoTrabajo" work, Out.d "impuestoCapital" cap, Out.d "uit" uit,
                Out.dStr "interest" "deposit interest exempt to 31-12-2026 (LIR art. 19 i, D.Leg. 1549 art. 2): not taxed"])
    (unsupported := unsup)

def country : Country :=
  { code := "PE", name := "Peru (Impuesto a la Renta, persona natural domiciliada)", currency := "PEN", year := "2025",
    compute := out }

/- Statute-visible checks (LIR art. 53 bands at UIT 5 350). -/
#guard art53.ticks (5 * uit) == 5 * uit * 800
#guard art53.tax { mode := .halfUp, step := 1 } (20 * uit) == 2140 + 11235
#guard (person 100000 0 0 0 0 0).netWork == 100000 - 37450

end PeTax
