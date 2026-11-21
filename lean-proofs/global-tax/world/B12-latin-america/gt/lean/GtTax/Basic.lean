import TaxKernel.World

/-!
# Guatemala 2025: Impuesto Sobre la Renta, rentas del trabajo en relacion de dependencia (Decreto 10-2012, Libro I)

Source: Decreto Numero 10-2012, Ley de Actualizacion Tributaria, SAT's annotated text (reform notes up to Decreto
19-2013) `portal.sat.gob.gt/portal/descarga/1899/legislacion-tributaria/18261/decreto-numero-10-2012-ley-de-actualizacion-tributaria.pdf`,
Internet Archive capture of 2022-07-02 (SAT's portal answers a Cloudflare challenge to scripts; not bypassed;
sha256 5433ea7389e70091...). Arts. 72 (base imponible: Q 48.000 personal expenses without proof + up to Q 12.000 of
VAT paid, IGSS contributions, donations up to 5 % of renta bruta, life insurance), 73 (5 % up to Q 300.000; Q 15.000
+ 7 % above), 92 (capital income 10 %), 93 (dividends 5 %). No reform note on arts. 72-73 in that text; reforms after
2022 were not checked (access B).
W5 review pass 2: art. 70 "Rentas exentas. Están exentas del impuesto: ... 5. El aguinaldo hasta el cien por ciento
(100%) del sueldo o salario ordinario mensual. 6. La bonificación anual ... (bono 14) ... hasta el cien por ciento (100%)
del sueldo o salario ordinario mensual" (src/d10_2012.txt, sha256 4610b593…). The annual wage does not say whether it
holds them: input `gtFourteenPays` (default false: none in `wages`); true = `wages` is fourteen equal payments (twelve
monthly salaries, the aguinaldo and Bono 14 of one monthly salary each), and two monthly salaries (2 x wages / 14) are
exempt.
W5 pattern A (2026-11-20): when `gtIgss` is not given, each adult's employee IGSS contribution is computed from the
Junta Directiva agreements (IGSS's own consolidated copies on igssgt.org, `gt/law/w5/`): Acuerdo 410 (Enfermedad y
Maternidad, rev. 2018) art. 62 b) "Los trabajadores, el 2 % de su salario"; Acuerdo 1002 (Accidentes) art. 46 b) "Los
trabajadores afiliados, el 1% de su salario" (on "los salarios mensuales totales, cualesquiera que sean sus
denominaciones"); Acuerdo 1124 (Invalidez, Vejez y Sobrevivencia, rev. 13 Sep 2021) art. 40 b) "Los trabajadores
afiliados, el 1.83% de sus salarios": 4.83 % of all wages, no ceiling, deducted under art. 72 as before. A given
`gtIgss` still wins; `"w5Contrib": false` restores the earlier default (0).
-/

namespace GtTax
open TaxKernel

/-- Art. 73: "Q.0.01 a Q 300,000.00 ... 5% sobre la renta imponible; Q.300,000.01 en adelante Q.15,000.00 + 7% sobre
el excedente de Q.300,000.00". -/
def art73 : List CumRow := [⟨0, 0, 500⟩, ⟨300000, 15000, 700⟩]
def art73Bands : Schedule := Schedule.ofList [(0, 500), (300000, 700)]
/-- Art. 72 a): "Hasta sesenta mil Quetzales (Q.60,000.00), de los cuales cuarenta y ocho mil Quetzales (Q.48,000.00)
corresponden a gastos personales sin necesidad de comprobacion alguna; y, doce mil Quetzales (Q.12,000.00) que podra
acreditar por el Impuesto al Valor Agregado pagado". -/
def personalExpenses : Int := 48000
def vatCreditCap : Int := 12000
/-- Art. 92: capital income (mobiliarias e inmobiliarias) and capital gains "diez por ciento (10%)". -/
def capitalRate : Int := 1000
/-- Art. 93: dividends "cinco por ciento (5%)". -/
def dividendRate : Int := 500

structure Person where
  base : Int
  tax : Int
  deriving Repr

/-- W5 pattern A: employee IGSS 2 % + 1 % + 1.83 % = 4.83 % of wages (Acuerdos 410 art. 62, 1002 art. 46, 1124 art. 40). -/
def igssEmployee (w : Int) : Int := divR .halfUp (483 * pos w) BP

#guard igssEmployee 100000 = 4830

def person (wage igss vat : Int) : Person :=
  let base := pos (pos wage - personalExpenses - min (pos vat) vatCreditCap - pos igss)
  { base, tax := divR .halfUp (cumTicks art73 base) BP }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  /- W5 review pass 2 (sweep P2-6): the household-total employee contribution is allotted to the adults in
  proportion to their wages (each person's own contribution is deducted from that person's income); it was halved, which
  gave a one-earner couple half its deduction. Halves only when nobody has wages. -/
  let socW : List Int := c.adults.map (fun a => pos a.wages)
  let wsumS := sumInts socW
  let socBy (x : Int) (i : Nat) : Int :=
    if n ≤ 1 then x else if wsumS = 0 then (if i = 0 then half1 x else half2 x)
    else if i = 0 then x - divR .down (x * socW.getD 1 0) wsumS else divR .down (x * socW.getD 1 0) wsumS
  let shW := fun (x : Int) => if n == 2 then [socBy x 0, socBy x 1] else [x]
  let w5 := (c.bool? "w5Contrib").getD true
  let statIgss : List Int := c.adults.map fun a => igssEmployee a.wages
  let given := c.int? "gtIgss"
  let igss := match given with
    | some x => x
    | none => if w5 then sumInts statIgss else 0
  let igssBy : List Int := match given with
    | some x => shW x
    | none => if w5 then statIgss else shW 0
  let vat := (c.int? "gtVatPaid").getD 0
  let fourteen := (c.bool? "gtFourteenPays").getD false
  let taxableWage (w : Int) : Int := if fourteen then w - divR .down (2 * w) 14 else w
  let ps := ((c.adults.zip igssBy).zip (sh vat)).map fun ((a, g), v) => person (if a.wages > 0 then taxableWage a.wages else 0) g v
  let capital := divR .halfUp ((pos c.interest + pos c.rentalIncome + pos c.capitalGains) * capitalRate) BP
  let divs := divR .halfUp (pos c.dividends * dividendRate) BP
  let unsup :=
    (if given.isNone && w5 then ["IGSS 4.83 % computed on all wages (with gtFourteenPays, on all fourteen payments: whether the aguinaldo and Bono 14 are contribution wages was not read)"] else
     ["IGSS employee contribution (rate set by IGSS Junta Directiva agreements, not reached): pass gtIgss (annual household total) or the base is overstated; employeeSocial = gtIgss"]) ++ [
     "VAT-paid deduction (art. 72 a, up to Q 12.000) needs gtVatPaid; taken as 0",
     "aguinaldo and Bono 14 (art. 70 num. 5, 6) exempt only with gtFourteenPays (wages = 14 equal payments); default: none in wages",
     "reforms after the 2022 SAT text not checked"] ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: Regimen sobre utilidades (25 %) or Regimen opcional simplificado (5 % / 7 % of income) not modelled; ignored"] else []) ++
    (if c.rentalIncome != 0 || c.interest != 0 || c.capitalGains != 0 then ["capital income: art. 92 10 % on the gross amount; art. 88-90 base rules (rent 30 % deduction etc.) not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pensions: not modelled"] else [])
  Out.make c "GT" "GTQ" (sumInts (ps.map (·.tax)) + capital) (surtaxes := [("ISR_dividendos_art93", divs)])
    (employeeSocial := pos igss)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.base))), Out.d "capitalTax" capital])
    (unsupported := unsup)

def country : Country :=
  { code := "GT", name := "Guatemala (ISR rentas del trabajo, Decreto 10-2012)", currency := "GTQ", year := "2025",
    compute := out }

#guard (person 48000 0 0).tax == 0
#guard (person 348000 0 0).tax == 15000

end GtTax

/- W5 review pass 2: wages 140,000 in fourteen payments: 20,000 exempt (art. 70 num. 5, 6); base 120,000 - 48,000 =
72,000; tax 5 % = 3,600 (without the input: 92,000, 4,600). -/
#guard (GtTax.person (140000 - 2 * 140000 / 14) 0 0).tax = 3600 ∧ (GtTax.person 140000 0 0).tax = 4600

