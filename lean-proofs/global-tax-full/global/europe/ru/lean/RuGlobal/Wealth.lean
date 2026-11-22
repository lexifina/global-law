import RuGlobal.Pit

/-!
# RU 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (НК РФ ст. 217 п. 18 (inheritance exempt from НДФЛ)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Russian Federation, Individual - Other taxes, accessed 2021-11-19 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (2022 capture, the newest archived) (PwC WWTS Individual - Other taxes, 2021-11-19 (Wayback capture))

* **4300 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Russian Federation, Individual - Other taxes, accessed 2021-11-19 (Wayback capture; `law/pwc_indother_wb2025.txt`): inheritance / gift tax: abolished from 1.1.2006; some gifts are PIT income (close relatives exempt; the 1.x PIT) (PwC WWTS Individual - Other taxes, 2021-11-19 (Wayback capture))


## 4200 / 4300 provenance: the stale 2021 PwC date replaced by the 2025 tax-code redactions already cited (gap pass, grade C)
Source: the entries' own statute fields (pass 17 / 18 readings of the Russian tax code); audit of B entries whose provenance named a pre-2025 secondary source.
* error found: both entries still gave a PwC capture of 19.11.2021 as their date, although their statute fields had been re-cited from the 2025 redactions
-/

namespace RuGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "inheritance / gift tax: none in 2025 (НК ст. 217 п. 18, 18.1: inheritances exempt from НДФЛ; gifts exempt except real estate, vehicles, shares from non-family donors, which are НДФЛ income)" },
   { oecd := .wealth, why := "net wealth tax: none in 2025 (НК РФ ст. 13-15 list every federal, regional and local tax; none on net wealth)" }]

def notes : List String := ["RU 4300 Inheritance and gift tax (not levied): back to B (pass 17, 2025 text read)", "RU 4200 Net wealth tax (not levied): back to B (pass 18, 2025 text read)", "RU gap pass: 4200 / 4300 provenance: the stale 2021 PwC date replaced by the 2025 tax-code redactions already cited"]

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end RuGlobal.Wealth
