import TaxKernel.World

/-!
# Honduras 2025: Impuesto Sobre la Renta of a resident individual (Decreto-Ley 25 de 1963)

Sources (read 2026-11-20, sar.gob.hn "Impuesto Sobre Renta (ISR)" document list):
* Acuerdo SAR-07-2025 (La Gaceta No. 36,735, 9 January 2025), PRIMERO: "Ajustar la escala de tasas progresivas para
  el pago del Impuesto Sobre la Renta para las personas naturales, a partir del ejercicio fiscal 2025, en un 3.88 %":
  TABLA PROGRESIVA 2025 "Exentos L 0.01 - L 217,493.16; 15% L 217,493.17 - L 331,638.50; 20% L 331,638.51 -
  L 771,252.38; 25% L 771,252.39 en adelante" (page image read at 110 dpi).
* SAR "Texto consolidado Decreto-Ley numero 25 Ley del Impuesto sobre la Renta hasta el Acuerdo SAR-07-2025"
  (PDF of 2025-02-05): art. 22 b) (the same table; "sera ajustada automaticamente de forma anual ... (IPC)"),
  art. 13 a) (deduction "hasta de CUARENTA MIL LEMPIRAS (L.40,000.00) por gastos educativos y por honorarios ...
  sin necesidad de presentar comprobante alguno"; "mayores de sesenta y cinco (65) anos ... OCHENTA MIL LEMPIRAS").

Unit: the individual. The tax is computed in centavos (the table is printed to the centavo) and rounded half-up to the
lempira.
-/

namespace HnTax
open TaxKernel

/-- Acuerdo SAR-07-2025 / LISR art. 22 b): marginal bands in centavos ("Desde" of each taxed band less one centavo). -/
def tabla2025 : Schedule := Schedule.ofList [(0, 0), (21749316, 1500), (33163850, 2000), (77125238, 2500)]
/-- LISR art. 13 a): L 40,000 without receipts; L 80,000 for persons over 65. -/
def art13Deduction : Int := 40000
def art13DeductionOver65 : Int := 80000

structure Person where
  base : Int
  tax : Int
  deriving Repr

def person (wage se rent : Int) (age : Nat) : Person :=
  let gross := pos wage + pos se + pos rent
  let ded := if age > 65 then art13DeductionOver65 else art13Deduction
  let base := pos (gross - ded)
  { base, tax := divR .halfUp (tabla2025.ticks (base * 100)) (BP * 100) }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let ps := (c.adults.zip (sh c.rentalIncome)).map fun (a, r) => person a.wages a.selfEmployment r a.age
  let unsup :=
    ["employee contributions (IHSS, RAP): the laws were not reached; employeeSocial = 0",
     "the 13th and 14th month salaries are taxed with the rest of the wage (their exemptions, Codigo del Trabajo / LISR art. 10, not modelled)"] ++
    (if c.interest != 0 || c.dividends != 0 || c.capitalGains != 0 then ["interest, dividends and capital gains: final withholding regimes (10 %) not read; ignored"] else []) ++
    (if c.rentalIncome != 0 then ["rent: taxed in the global base; the cedular tax on residential rent (Codigo 106) not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: gross taxed; art. 13 b) expenses not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pensions: not modelled"] else [])
  Out.make c "HN" "HNL" (sumInts (ps.map (·.tax)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.base)))])
    (unsupported := unsup)

def country : Country :=
  { code := "HN", name := "Honduras (Impuesto Sobre la Renta, personas naturales)", currency := "HNL", year := "2025",
    compute := out }

/- The exempt band ends at L 217,493.16: a wage of L 257,493 (base 217,493) pays nothing. -/
#guard (person 257493 0 0 40).tax == 0
/- At base L 331,638.50 the 15 % band is full: 15 % of 114,145.34 = 17,121.80 -> L 17,122. -/
#guard divR .halfUp (tabla2025.ticks 33163850) (BP * 100) == 17122

end HnTax
