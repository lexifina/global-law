import BgGlobal.Pit

/-!
# BG 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (ЗМДТ чл. 36-37 (данък върху наследствата, 0,4-6,6 %), чл. 44 (дарения)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Bulgaria, Individual - Other taxes, accessed 2025-05-31 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes, 2025-05-31 (Wayback capture))

* **4300 Данък върху наследствата и даренията (pass 6 note, grade C)**: Закон за местните данъци и такси (ЗМДТ) чл. 29-38 (данък върху наследствата) and чл. 44-48 (данък при придобиване на имущества по дарение): ЗМДТ read in the Ministry of Finance's English text (minfin.bg, as amended to SG 8/2022; Internet Archive 2024-09-12): the surviving spouse and lineal heirs pay no inheritance tax (чл. 31 ал. 2); siblings and their children pay 0,4 to 0,8 % and all others 3,3 to 6,6 % of each share above BGN 250 000 (чл. 36); gifts: 0,4 to 0,8 % between siblings and their children and 3,3 to 6,6 % otherwise, on the assessed value (чл. 47 ал. 1), none between spouses or lineal relatives (чл. 44 ал. 6). The rate inside each range is fixed by the municipal council's ordinance (чл. 1 ал. 2): the Sofia ordinance (Наредба за определянето и администрирането на местните данъци на територията на Столична община) was not reached: sofia.bg and council.sofia.bg answer 403 to a non-browser client and no Internet Archive copy was found. Amendments after SG 8/2022 to чл. 31, 36, 44 and 47 not checked (minfin.bg English text of the ЗМДТ, upload 51250 (Internet Archive 2024-09-12, `bg/law/zmdt_en_minfin_wb20240912.pdf`))
-/

namespace BgGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none" }]

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4300 inheritance and gift tax not computed (grade C): spouse and lineal heirs and gifts between spouses or lineal relatives owe none (ЗМДТ чл. 31 ал. 2, чл. 44 ал. 6); the other rates lie in the ranges of чл. 36 and 47 and are fixed by the Sofia ordinance, which was not reached"] else [])


end BgGlobal.Wealth
