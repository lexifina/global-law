import TaxKernel.World

/-!
# Bolivia 2025: Regimen Complementario al Impuesto al Valor Agregado (RC-IVA), Ley 843 Titulo II

Sources (read 2026-11-20):
* Ley 843 (Texto Ordenado), SIN compilation "Ley N° 843 ... actualizado" `sac.impuestos.gob.bo/formularios/pdf/
  1.-LEY N° 843-09-23.pdf` (Internet Archive capture 2024-08-09; 576 pages; sha256 in src/NOTES.md): arts. 19 (objeto:
  wages e), rents a), interest c) excluding dividends and term deposits, independent professions g)), 25 (contributions
  excluded), 26 ("deducir, en concepto de minimo no imponible el monto equivalente a dos salarios minimos nacionales"),
  28 ("El periodo fiscal sera mensual"), 30 ("alicuota del 13%"), 31 (VAT in invoices "como pago a cuenta").
  Reglamento D.S. 21531 art. 8 (same compilation, as modified by D.S. 24050 and D.S. 3448): pago a cuenta of 1. the IVA
  in invoices presented and 2. "la alicuota ... del IVA aplicada sobre el monto de dos (2) Salarios Minimos Nacionales";
  a balance in the taxpayer's favour is carried forward to the following months.
* D.S. 5383 of 1 May 2025 art. 7: Salario Minimo Nacional "Bs2.750.-", Disposicion Final Primera I: "efecto retroactivo
  al 1 de enero de 2025" (impuestos.gob.bo/wp-content/uploads/2025/09/DS-5383.pdf).
* Ley 065 art. 66 (quoted in the same compilation under art. 19): pensions "no constituyen hecho generador de tributos".

Unit: the individual (art. 22). The year is twelve equal months; the monthly balances in favour carry forward
(mantenimiento de valor in UFV ignored), so the year's tax is max(0, sum of monthly taxes - sum of credits).

W5 pattern A (2026-11-20): when `boEmployeeContrib` is not given, each dependent worker's SIP contributions are
computed (APS copies on aps.gob.bo, `bo/law/w5/`): Ley 065 de Pensiones (text updated to Nov 2019) art. 88 (Cotización
10 % of Total Ganado), art. 87 b) (Aporte Solidario del Asegurado 0,5 %), art. 151 a) (Comisión 0,5 %), art. 83 b)
(Prima por Riesgo Común, deducted from Total Ganado, paid until 65), art. 87 f) (Aporte Nacional Solidario: 1 % of
Total Solidario over Bs 13.000, 5 % over 25.000, 10 % over 35.000, each on the difference), glossary "Total Ganado":
"El máximo Total Ganado a efecto de la Contribución es de sesenta (60) veces el Salario Mínimo Nacional"; D.S. 778
(Reglamento de contribuciones, 2011) annex table: Riesgo Común 1,71 % (under 65 only), Comisión 0,50 %, and art.
(II-III) the ANS on the Total Ganado without the 60-SMN cap. So 12,71 % (11 % from 65) of the monthly wage up to
60 x 2.750 = Bs 165.000, plus the ANS; deducted under Ley 843 art. 25 as before. A given `boEmployeeContrib` still wins;
`"w5Contrib": false` restores the earlier default (0). Updates of the ANS thresholds after 2019 were not checked.
-/

namespace BoTax
open TaxKernel

/-- D.S. 5383 art. 7: Salario Minimo Nacional 2025 = Bs 2.750 (retroactive to 1 January 2025). -/
def smn : Int := 2750
/-- Ley 843 art. 30: "la alicuota del 13% (trece por ciento)". -/
def rcivaRate : Int := 1300
/-- Ley 843 art. 26 I: minimo no imponible of two SMN a month for employees. -/
def mniSMN : Int := 2

structure Person where
  baseYear : Int
  taxBeforeCredits : Int
  creditSMN : Int
  creditInvoices : Int
  wageTax : Int
  indepTax : Int
  deriving Repr

/-- One person. `contrib` = annual employee social-security contributions (Ley 843 art. 25: excluded from the base);
`invoices` = annual value of invoices presented (VAT credit at 13 %, D.S. 21531 art. 8 c) 1). -/
def person (wage se rent contrib invoices : Int) : Person :=
  let monthlyWage := pos wage / 12
  let monthlyContrib := pos contrib / 12
  let isEmployee := wage > 0
  let monthlyBase := if isEmployee then pos (monthlyWage - monthlyContrib - mniSMN * smn) else 0
  let baseYear := 12 * monthlyBase
  let taxBefore := divR .halfUp (baseYear * rcivaRate) BP
  let creditSMN := if isEmployee then 12 * divR .halfUp (mniSMN * smn * rcivaRate) BP else 0
  let creditInv := divR .halfUp (pos invoices * rcivaRate) BP
  let wageTax := pos (taxBefore - creditSMN - creditInv)
  let indepTax := divR .halfUp ((pos se + pos rent) * rcivaRate) BP
  { baseYear, taxBeforeCredits := taxBefore, creditSMN, creditInvoices := creditInv, wageTax, indepTax }

/-- W5 pattern A: monthly employee SIP contributions on a monthly Total Ganado `m` (Bs), by age. -/
def sipMonthly (m : Int) (age : Nat) : Int :=
  let tg := min (pos m) (60 * smn)
  let rate : Int := if age ≥ 65 then 1100 else 1271
  let ans := divR .halfUp (100 * pos (m - 13000) + 500 * pos (m - 25000) + 1000 * pos (m - 35000)) BP
  divR .halfUp (rate * tg) BP + ans

#guard sipMonthly 10000 40 = 1271 ∧ sipMonthly 30000 40 = 3813 + 170 + 250 ∧ sipMonthly 200000 40 = 20972 + 1870 + 8750 + 16500
#guard sipMonthly 10000 70 = 1100

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
  let given := c.int? "boEmployeeContrib"
  let statC : List Int := c.adults.map fun a => if a.wages > 0 then 12 * sipMonthly (pos a.wages / 12) a.age else 0
  let contrib := match given with
    | some x => x
    | none => if w5 then sumInts statC else 0
  let contribBy : List Int := match given with
    | some x => shW x
    | none => if w5 then statC else shW 0
  let inv := (c.int? "boInvoices").getD 0
  let rows := (((c.adults.zip (sh c.rentalIncome)).zip contribBy).zip (sh inv))
  let ps := rows.map fun (((a, r), k), i) => person a.wages a.selfEmployment r k i
  let unsup :=
    (if given.isNone && w5 then ["SIP contributions computed (Ley 065, D.S. 778): monthly wage = annual / 12; ANS thresholds as printed in 2019"] else
     ["employee contributions to the Sistema Integral de Pensiones (Ley 065) not reached: pass boEmployeeContrib (annual household total) or the base is overstated; employeeSocial = that input"]) ++ [
     "invoice credit (D.S. 21531 art. 8 c) 1, plus the 20 % extra for Bolivian-made goods of D.S. 5503 from December 2025) needs boInvoices; taken as 0",
     "balance in favour at the year end carries to the next year (not refunded); UFV maintenance of value ignored"] ++
    (if c.interest != 0 then ["interest: art. 19 c) excludes term deposits over 30 days (national currency) and others; not taxed"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: RC-IVA 13 % on gross fees (art. 19 g); IVA and IT on the fees and the invoice credit not modelled"] else []) ++
    (if c.rentalIncome != 0 then ["rent: RC-IVA 13 % on gross rent (art. 19 a), quarterly filing; IVA/IT not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: not modelled"] else [])
  Out.make c "BO" "BOB" (sumInts (ps.map fun p => p.wageTax + p.indepTax))
    (employeeSocial := pos contrib)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.baseYear))),
                Out.d "taxBeforeCredits" (sumInts (ps.map (·.taxBeforeCredits))),
                Out.d "credit13pct2SMN" (sumInts (ps.map (·.creditSMN))),
                Out.d "creditInvoices" (sumInts (ps.map (·.creditInvoices))),
                Out.dStr "dividends" "not object of the RC-IVA (Ley 843 art. 19 c: 'No estan incluidos los dividendos')",
                Out.dStr "pensions" "not taxed (Ley 065 art. 66)", Out.d "smn" smn])
    (unsupported := unsup)

def country : Country :=
  { code := "BO", name := "Bolivia (RC-IVA, Ley 843 Titulo II)", currency := "BOB", year := "2025", compute := out }

/- With no invoices and no contributions, a monthly wage of four SMN (Bs 11.000) pays nothing: 13 % of 2 SMN of base
is cancelled by the 13 % of 2 SMN credit. -/
#guard (person (12 * 11000) 0 0 0 0).wageTax == 0
#guard (person (12 * 11100) 0 0 0 0).wageTax == 12 * 13

end BoTax
