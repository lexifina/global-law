import SiGlobal.Pit

/-!
# SI 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Zakon o davku na dediščine in darila): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, gap pass, grade B)**: European Commission TEDB, SI: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 812, 6880, 536, 537, 543, 545, 714, 811, 813, 814, 3741): the TEDB lists Slovenia's taxes in force on 1.7.2025 (motor vehicle fee and tax, bank balance-sheet tax, insurance and financial services taxes, gaming taxes, real property transaction tax, CO2 tax, charge for the use of building land, environmental charges); none is levied on an individual's net wealth (OECD Interpretative Guide § 51) (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))

* **4200: absence withdrawn (gap pass 2)**: gap pass 2: the cited absence of the gap pass (TEDB list read against the guide) is withdrawn: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVSVN v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/SVN.csv`, SHA256SUMS; general government S13; 2025 not yet published) books revenue under heading 4200: 4220 tax on balance wealth paid by banks 93,8 million EUR (2024; the bank balance-sheet tax, in force in 2025); the national taxes behind it not read
-/

namespace SiGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := ["SI 4200 gap pass 2: cited absence withdrawn (OECD Revenue Statistics book revenue under 4200)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)"] else [])
  ++ (if true then ["4200 Taxes on net wealth (4200): not modelled (grade C: gap pass 2, OECD Revenue Statistics book revenue under 4200)"] else [])


end SiGlobal.Wealth
