import LiGlobal.Pit

/-!
# LI 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (no inheritance tax since 2011 (SteG): absence not cited): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (Steuergesetz Art. 9-12 (Vermögenssteuer via Sollertrag 4 %)): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4300 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Liechtenstein, Individual - Other taxes, accessed 2025-07-15 (Wayback capture; `law/pwc_indother_wb2025.txt`): inheritance / estate / gift tax: none (PwC WWTS Individual - Other taxes, 2025-07-15 (Wayback capture))

* **4200 Vermögenssteuer (Sollertrag) (pass 6 note, grade C)**: Steuergesetz Art. 5 Abs. 1 (Sollertrag 4 %), Art. 14 Abs. 2 Bst. l (the Sollertrag of the taxable wealth is Erwerb), Art. 6 Abs. 1: the wealth tax is a 4 % notional return (Sollertrag) on the taxable net wealth, added to the Erwerb and taxed with the Erwerbssteuer tariff (no separate wealth rate); the 1.x PIT line carries no wealth, so it is not computed. To model: PIT(Erwerb + 4 % x net wealth) - PIT(Erwerb) (SteG, Lilex consolidated PDF Fassung 01.07.2026 (`li/law/steg_konso.txt`; Art. 5 unchanged in 2025 not checked))
-/

namespace LiGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "inheritance / estate / gift tax: none" }]

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)"] else [])


end LiGlobal.Wealth
