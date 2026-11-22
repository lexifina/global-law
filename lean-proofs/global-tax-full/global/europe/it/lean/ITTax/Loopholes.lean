import ITTax.Household

/-!
# Loopholes and cliffs, each a proved statement about the model (cents)

`taxesOf p` = INPS + IRPEF netta − trattamento integrativo − cuneo sum + addizionali, for one taxpayer: what the
person hands over (negative = net cash received). A deductible pension contribution stays the taxpayer's own
savings, so the gain from contributing `c` is `taxesOf p − taxesOf {p with pensionContrib := c}`: the tax saved,
while the contribution itself is still his. When that saving exceeds `c`, the state pays more than the whole
contribution.

The known regimes (forfettario, impatriati, art. 24-bis, cedolare secca, premi di risultato) are below as small
functions of their own statutes, with the comparisons that make them loopholes.
-/

namespace ITTax
open TaxKernel

def taxesOf (p : Person) : Int :=
  let t := p.irpef
  p.inps + t.netta - t.ti - t.cuneo + t.regionale + t.comunale

def employee (wagesEur : Int) : Person := { wages := eur wagesEur, inps := inps (eur wagesEur) }
def employeeC (wagesEur contribCents : Int) : Person := { employee wagesEur with pensionContrib := contribCents }

/-! ## N1. The stacked cliff at 8.500 (new in 2025): cuneo band edge + addizionali "dovuta" threshold
For an employee, reddito complessivo = employment income R. At R = 8.500 both (a) the c. 4 percentage falls from
7,1 % to 5,3 % of the whole income and (b) the imposta lorda 23 % × 8.500 = 1.955 equals the art. 13 detrazione,
so above it IRPEF netta becomes positive and both addizionali become due on the whole base. Gross 9.391 -> 9.392
(R 8.499,79 -> 8.500,70): one more euro of pay costs 300,26 euro (`taxesOf` goes from −912,28, a net payment
to the worker, to −612,02). -/
theorem cliff_8500 : taxesOf (employee 9392) - taxesOf (employee 9391) = 30026 := by decide

/-! ## N2. A deductible pension contribution that buys back the addizionali (all thresholds tested on the
imponibile, while the detrazioni and the cuneo test the reddito complessivo, before the deduction) -/
/-- Employee on 9.500 gross: R = 8.598,45, IRPEF netta 22,64, Lazio 148,75. Paying 99 euro into a pension fund
(deductible, D.Lgs. 252/2005 art. 8 c. 4) brings the imposta lorda under the detrazione: IRPEF and the addizionale
regionale vanish; the trattamento integrativo and cuneo sum (tested before deductions) are unchanged. Taxes fall
by 171,39 euro and the 99 euro remain his pension savings. -/
theorem contrib_8500 : taxesOf (employee 9500) - taxesOf (employeeC 9500 9900) = 17139 := by decide
/-- Lazio's 28.000 threshold: employee on 31.050 gross (imponibile 28.103,35). Deducting 103,36 euro of pension
contributions saves the 1,60 % on 13.000 (208) less the lost 60-euro detrazione, plus 35 % IRPEF and 0,9 %
comunale on 103,36 (imponibile 27.999,99): 188,54 euro saved for 103,36 put aside. -/
theorem contrib_lazio_28000 : taxesOf (employee 31050) - taxesOf (employeeC 31050 10336) = 18854 := by decide
/-- Roma's 14.000 exemption: employee on 15.500 gross (imponibile 14.029,05). Deducting 29,06 euro saves the whole
0,9 % (126,26) and 23 % IRPEF on 29,06 (imponibile 13.999,99): 133,44 euro saved. -/
theorem contrib_roma_14000 : taxesOf (employee 15500) - taxesOf (employeeC 15500 2906) = 13344 := by decide

/-! ## N3. The 35.000 double edge: art. 13 c. 1.1 (+65, reddito complessivo) and Lazio's 60-euro detrazione
(imponibile) both stop at 35.000. Gross 38.669 -> 38.670. -/
theorem cliff_35000 : taxesOf (employee 38670) - taxesOf (employee 38669) = 12557 := by decide

/-! ## N4. The addizionali switch on, off and on again (one-earner couple with a dependent spouse and a child aged
21-29, art. 12 c. 1 a), c)). IRPEF netta first becomes positive at R 18.438,70 (gross 20.372): addizionali on the
whole base, 485,31 for one euro. At R 20.000 the cuneo cash sum (960) ends but the 1.000 c. 6 detrazione wipes out
the IRPEF netta, so the addizionali are no longer due: taxes FALL by 83,77 for one more euro. At R 21.455,40
(gross 23.705) the netta is positive again and the addizionali return: 564,66 for one euro. -/
def famEarner (w : Int) : Person :=
  { employee w with spouseDependent := true, kids2129 := 1, kids2129Share := 100, kidsDependent := 1 }
theorem family_on_off_on : taxesOf (famEarner 20372) - taxesOf (famEarner 20371) = 48531 ∧
    taxesOf (famEarner 22098) - taxesOf (famEarner 22097) = -8377 ∧
    taxesOf (famEarner 23705) - taxesOf (famEarner 23704) = 56466 := by decide

/-! ## K1. Dependent-spouse limit 2.840,51 (art. 12 c. 2), a known notch: the spouse earning one euro more costs
the household the 690-710 euro detrazione. Earner at the OECD average wage (36.594); spouse 3.138 -> 3.139 gross. -/
def coupleTaxes (w1 w2 : Int) : Int :=
  let p := employee w1
  let q := employee w2
  let qDep := (q.irpef).redditoRif ≤ caricoLimit
  taxesOf { p with spouseDependent := qDep } + taxesOf q
theorem spouse_limit : coupleTaxes 36594 3139 - coupleTaxes 36594 3138 = 71002 := by decide

/-! ## K2. Regime forfettario (L. 190/2014 cc. 54-89): 15 % (5 % for a start-up's first five years) on revenue ×
the allegato 4 coefficient, replacing IRPEF and both addizionali (c. 64); entry requires revenue ≤ 85.000 in the
previous year (c. 54 a)); exit in the same year above 100.000 (c. 71). Compared with ordinary IRPEF on the same
taxable income (INPS left out of both). `coeffBp`: the allegato 4 coefficient in bp (e.g. 7800 for professions). -/
def forfettarioTax (revenue coeffBp rateBp : Int) : Int := divR .halfUp (divR .halfUp (revenue * coeffBp) BP * rateBp) BP
def ordinaryTax (income : Int) : Int := taxesOf { selfEmp := income }
/-- A professional with 85.000 of fees and 78 % coefficient: taxable 66.300. Forfettario 9.945; ordinary IRPEF +
addizionali on the same 66.300: 23.713,49. -/
theorem forfettario_85000 : forfettarioTax (eur 85000) 7800 1500 = 994500 ∧ ordinaryTax (eur 66300) = 2371349 := by
  decide
/-- The c. 71 cliff: above 100.000 of fees the regime ends in the same year, so the whole income is taxed
ordinarily. At 100.000: 11.700 forfettario; just above, ordinary tax on about 78.000: 29.239,40. -/
theorem forfettario_exit_cliff : forfettarioTax (eur 100000) 7800 1500 = eur 11700 ∧
    ordinaryTax (eur 78000) = 2923940 := by decide

/-! ## K3. Cedolare secca vs IRPEF on rent (D.Lgs. 23/2011 art. 3): a top-rate landlord pays 21 % instead of
43 % + 3,33 % + 0,9 % on 95 % of the rent; a low-income landlord is better off under IRPEF. -/
/-- Employee at 80.000 gross with 10.000 of rent: cedolare 2.100; IRPEF + addizionali on 9.500 at the margin: 4.486,85. -/
theorem cedolare_top : taxesOf { employee 80000 with rentIrpef := eur 9500 } - taxesOf (employee 80000) = 448685 :=
  by decide

/-! ## K4. Impatriati (D.Lgs. 209/2023 art. 5): 50 % of employment income exempt (60 % with a minor child), up to
600.000; K5. art. 24-bis TUIR: 200.000 a year flat on all foreign income for a new resident. Shown as the
statutory amounts; the model's taxpayer is Italian-source only. -/
/-- An impatriate employee on 100.000 gross pays IRPEF etc. on half his income: compare. -/
def impatriato (wagesEur : Int) (exemptBp : Int) : Person :=
  let w := eur wagesEur
  let i := inps w
  -- art. 5 c. 1: "concorrono alla formazione del reddito complessivo limitatamente al 50 per cento"
  { wages := w - divR .halfUp ((w - i) * exemptBp) BP, inps := i }
theorem impatriati_100000 : taxesOf (employee 100000) - taxesOf (impatriato 100000 5000) = 2130260 := by decide

/-! ## K6. Premi di risultato (L. 208/2015 c. 182, 5 % for 2025-2027 by L. 207/2024 c. 385): up to 3.000 of
productivity pay taxed at 5 % instead of IRPEF and addizionali. Employee at 40.000 gross: -/
def premioTaxes (wagesEur premioEur : Int) : Int :=
  let p := employee wagesEur
  -- the premio is outside IRPEF; INPS is still due on it
  taxesOf p + inps (eur (wagesEur + premioEur)) - p.inps + divR .halfUp (eur premioEur * 500) BP
theorem premio_3000 : taxesOf (employee 43000) - premioTaxes 40000 3000 = 149031 := by decide

/-! ## K12. Impresa familiare (TUIR art. 5 c. 4: up to 49 % of the income attributed to family collaborators):
with individual taxation, splitting 100.000 of business income 51/49 with a spouse uses the second person's
23 % band, detrazioni and the addizionali thresholds twice (INPS left out). -/
theorem impresa_familiare_split :
    ordinaryTax (eur 100000) - (ordinaryTax (eur 51000) + ordinaryTax (eur 49000)) = 754270 := by decide

end ITTax
