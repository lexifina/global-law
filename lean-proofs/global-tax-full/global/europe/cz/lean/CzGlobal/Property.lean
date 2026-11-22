import CzGlobal.Pit
import TaxKernel.Global2

/-!
# CZ 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (daň z nabytí nemovitých věcí (abolished from 2020: absence not yet cited)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (zákon 338/1992 Sb. o dani z nemovitých věcí (Praha)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4400 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Czech Republic, Individual - Other taxes, accessed 2025-04-20 (Wayback capture; `law/pwc_indother_wb2025.txt`): real estate acquisition / transfer tax: none (PwC WWTS Individual - Other taxes, 2025-04-20 (Wayback capture))

* **4100 Recurrent property tax (pass 6 note, grade C)**: zákon 338/1992 Sb. o dani z nemovitých věcí (Praha): zákon 338/1992 Sb. sets per-m2 rates by type, multiplied by coefficients each municipality sets; area inputs are not in the model (pass 6 note (PwC WWTS 2025 captures on disk))


## 4100 Daň ze staveb (obytná budova, Praha 1) (gap pass, grade B)
Source: zákon č. 338/1992 Sb. (e-Sbírka) and Obecně závazná vyhláška hl. m. Prahy č. 11/2024 (sbirkapp.gov.cz SPPGSHO2FHERZ7TG), read from lexifina/czechia-law `sb/1992/338.md` and `local/praha/hlavni-mesto-praha/2024/11.md`.
* § 11 odst. 1 písm. a): residential buildings 3,50 Kč per m² of built-up area; odst. 2: 1,40 Kč for each further above-ground floor (not modelled)
* OZV 11/2024 § 2 and příloha 1: coefficient 5 for residential buildings in Praha 1, 3, 5, 6, 7, 8, 14, 18, 19 and 4,5 elsewhere; § 4 odst. 1: "místní koeficient pro obec ve výši 1,5"; § 5 and příloha 2: 2 in Praha 3, 6, 7 (and four small districts), 1,7 in Praha 8, used instead of the city's 1,5
* § 11f: the inflation coefficient (May CPI ratio rounded down to one decimal) is announced by the Ministry of Finance only when it rises; no 2025 announcement was found: taken as 1,0 (grade B)
* Model: a home or other residential building in Praha 1: area ("areaM2", taken as the built-up area) x 26,25 Kč
* Hand check: 120 m² built-up, one floor: 120 x 26,25 = 3 150 Kč
-/

namespace CzGlobal.Property
open TaxKernel TaxKernel.Global

/-- Daň ze staveb (obytná budova, Praha 1) (kernel 2.8.0 `LocalTax`, gap pass). -/
def gxLocal0 : LocalTax :=
  { key := "propertyTax",   name := "Daň ze staveb (obytná budova, Praha 1)",   base := .area [.home, .realEstate],   unit := .perUnit,   default := some { municipality := "Praha 1", num := 2625, den := 100, source := "OZV hl. m. Prahy č. 11/2024 (Sbírka právních předpisů ÚSC 24.6.2024) § 2 a příloha č. 1 (koeficient 5 pro Prahu 1), § 4 odst. 1 (místní koeficient 1,5); zákon 338/1992 Sb. § 11 odst. 1 (3,50 Kč/m²): 3,50 x 5 x 1,5 = 26,25 Kč/m²", date := "2025-01-01" },   statute := "zákon č. 338/1992 Sb. o dani z nemovitých věcí § 10, § 11 odst. 1 písm. a), odst. 4-5, § 11f, § 12 (znění 1.1.-30.9.2025)" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4100 Daň ze staveb (obytná budova, Praha 1) (local rate, gap pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       gxLocal0.charges g }]

def absent : List Absent :=
  [{ oecd := .transactions, why := "real estate acquisition / transfer tax: none" }]

def notes : List String := ["CZ 4100 gap pass: Daň ze staveb (obytná budova, Praha 1) (LocalTax, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  gxLocal0.unknown g

#guard (gxLocal0.default.map (·.num)) == some 2625
#guard (gxLocal0.default.map (·.den)) == some 100
#guard 120 * 2625 / 100 == 3150

end CzGlobal.Property
