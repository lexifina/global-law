import ITTax.Household

/-!
# Official worked examples and OECD lines, checked at build time

* Agenzia delle Entrate, circolare 16 maggio 2025 n. 4/E, § 1.2, esempi 1-3 (the 2025 cuneo sum, L. 207/2024 c. 4,
  for part-year and impatriati workers; `refs/circ4E_2025.txt` lines 390-560). The rate is chosen on the income
  "rapportato all'intero anno" (c. 5) and applied to the income actually received; esempio 3 chooses it on the
  income including the exempt impatriati share (c. 9) and applies it to the taxable share.
* OECD Taxing Wages 2025 lines for Italy at the OECD's own wages (not rounded to the euro): the imposta lorda and
  the detrazioni of S100, S67 and M100_0 (`cmp20/continental/data/oecd/summary_2025.txt`).
-/

namespace ITTax
open TaxKernel

/-- The c. 4 sum for a part-year worker: rate chosen on `annual` (c. 5), applied to `paid`. -/
def cuneoSommaGen (r annual paid : Int) : Int :=
  if paid ≤ 0 ∨ r > cuneoLimit then 0 else divR .halfUp (cuneoRate annual * paid) BP

/-- Esempio 1: "Il reddito annuale teorico è pari a 11.744,19 euro [(2.000:62) x 365]. La somma spettante è pari a
106 euro". -/
theorem circ4E_es1 : cuneoSommaGen (eur 6000) 1174419 (eur 2000) = eur 106 := by decide
/-- Esempio 2: "(2.000 + 1.000):(62 + 30) x 365" = 11.902,17; "La somma spettante è pari a 159 euro". -/
theorem circ4E_es2 : cuneoSommaGen (eur 6000) 1190217 (eur 3000) = eur 159 := by decide
/-- Esempio 3: "reddito complessivo ... pari a 15.000 euro"; "La somma spettante è pari a 238,50 euro". -/
theorem circ4E_es3 : cuneoSommaGen (eur 15000) (eur 15000) (eur 4500) = 23850 := by decide

/-- OECD S100: CGTC 33.121,17, CGITLETC 8.232,41 (art. 11). -/
theorem oecd_s100_lorda : lorda 3312117 = 823241 := by decide
/-- OECD S67: CGTC 22.191,18, CGITLETC 5.103,97. -/
theorem oecd_s67_lorda : lorda 2219118 = 510397 := by decide
/-- OECD S67: BTC 3.441,73 = art. 13 c. 1 b) + L. 207/2024 c. 6 (OECD: exact ratio; statute: four decimals). -/
def s67Statute : Int := detrDip 2219118 + ulteriore 2219118
theorem oecd_s67_btc_statute : s67Statute = 344169 := by decide
/-- OECD S100: BTC 2.390,24 = art. 13 c. 1 c) + c. 1.1 + L. 207/2024 c. 6 b). The statute (four decimals)
gives 2.390,20. -/
theorem oecd_s100_btc_statute : detrDip 3312117 + ulteriore 3312117 = 239020 := by decide
/-- OECD M100_0: HFTC 710 = art. 12 c. 1 a) 2) 690 + b) 2) 20 (reddito 33.121,17). -/
theorem oecd_m100_0_coniuge : detrConiuge 3312117 = eur 710 := by decide

end ITTax
