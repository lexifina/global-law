import PTTax.Household

/-!
# Official worked examples, checked in Lean

* AT leaflet "Deduções, benefícios fiscais e taxas — IRS 2025" (`refs/IRS_deducoes_2025.pdf`, p. 17,
  https://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/Folhetos_informativos/Documents/IRS_deducoes_2025.pdf):
  five "Exemplos de dedução total por dependente" (art. 78-A), ages at 31 December 2025.
* OECD Taxing Wages 2025, Portugal, S100: rendimento coletável 19 791,83 €, OECD tax 3 378,58 € (band sum);
  the statute's art. 68 n.º 2 gives 3 378,53 €.
-/

namespace PTTax
open TaxKernel

/-- Caso 1 (1 dependente, 2 anos): 600 + 126 = 726 €. -/
theorem at_caso1 : dependentsDeduction [2] = 72600 := by decide
/-- Caso 2 (5 e 2 anos): 600 + 600 + 300 = 1 500 €. -/
theorem at_caso2 : dependentsDeduction [5, 2] = 150000 := by decide
/-- Caso 3 (6, 2, 1 ano): 1 800 + 300 + 300 = 2 400 €. -/
theorem at_caso3 : dependentsDeduction [6, 2, 1] = 240000 := by decide
/-- Caso 4 (3, 2 e 1 ano): 1 800 + 126 + 300 + 300 = 2 526 €. -/
theorem at_caso4 : dependentsDeduction [3, 2, 1] = 252600 := by decide
/-- Caso 5 (10, 7 e 3 anos): 1 800 + 300 = 2 100 €. -/
theorem at_caso5 : dependentsDeduction [10, 7, 3] = 210000 := by decide

/-- OECD S100: statute 3 378,53 € ... -/
theorem oecd_s100_statute : art68Coleta 1 1979183 = 337853 := by decide
/-- ... the OECD's band sum 3 378,58 €. -/
theorem oecd_s100_bands : divR .halfUp (bandsScaledN 1 1979183) 100000 = 337858 := by decide

/-- OECD SP67 abono: 2.º escalão, two children over 72 months, monoparental: 2 × 73,51 × 1,5 × 12 = 2 646,36 €
(annual rounding, the OECD's) and 2 646,48 € paid monthly (110,27 € per child-month). -/
theorem oecd_sp67_abono_annual : (abono 1625017 [6, 11] true true).1 = 264636 := by decide
theorem oecd_sp67_abono_monthly : (abono 1625017 [6, 11] true false).1 = 264648 := by decide
/-- OECD M100_0: 3.º escalão, 2 × 53,18 × 12 = 1 276,32 €. -/
theorem oecd_m100_abono : (abono 2425398 [6, 11] false).1 = 127632 := by decide

end PTTax
