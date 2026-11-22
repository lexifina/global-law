import GrGlobal.Pit

/-!
# GR 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (ν. 2961/2001 (φόρος κληρονομιών, δωρεών)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)


## 4300 Φόρος κληρονομιών και δωρεών (pass 6)
Source: PwC Worldwide Tax Summaries, Greece, Individual - Other taxes, accessed 2025-06-17 (Wayback capture; `law/pwc_indother_wb2025.txt`).
* category Α' (spouse, children, grandchildren, parents): the first EUR 150 000 free, then 1 % up to 300 000, 5 % up to 600 000 and 10 % above
* category Β' (siblings, nephews and nieces, uncles, grandparents, great-grandchildren, step-children, in-laws): EUR 30 000 free, then 5 % up to 100 000, 10 % up to 300 000 and 20 % above
* category Γ' (all other relatives and non-relatives): EUR 6 000 free, then 20 % up to 72 000, 30 % up to 267 000 and 40 % above
* each heir is taxed on the share received, by the heir's category; immovables abroad are outside the tax
* donations are taxed on the donee by the same scales; a parental grant has EUR 800 000 free (not computed: see the unsupported line)
* Hand check: a child inheriting EUR 1 000 000: 1 % x 150 000 + 5 % x 300 000 + 10 % x 400 000 = 1 500 + 15 000 + 40 000 = 56 500

* **4200 not levied (cited, gap pass, grade B)**: European Commission TEDB, GR: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 838, 210, 3561, 216, 6961, 215, 222, 223, 961, 1141, 6960): the TEDB lists Greece's taxes in force on 1.7.2025 (road tax, inheritance and gift tax, ΕΝ.Φ.Ι.Α., registration tax, digital transaction fee, insurance premium tax, stamp duties, real estate transfer tax, mobile services tax, luxury tax, climate crisis resilience fee); ΕΝ.Φ.Ι.Α. is a tax on immovable property (4100), and none is levied on net wealth (OECD Interpretative Guide § 51: 4200 covers taxes levied regularly on net wealth, i.e. on a wide range of assets net of debt) (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))

* **4200: absence withdrawn (gap pass 2)**: gap pass 2: the cited absence of the gap pass (TEDB list read against the guide) is withdrawn: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVGRC v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/GRC.csv`, SHA256SUMS; general government S13; 2025 not yet published) books revenue under heading 4200: heading 4200 total 1 157, 1 295, 1 308 million EUR in 2021-2023 (unnamed); the national taxes behind it not read
-/

namespace GrGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- ν. 2961/2001 (Κώδικας φορολογίας κληρονομιών, δωρεών, γονικών παροχών), scales of categories Α', Β', Γ' (art. 29 and 44, as stated by PwC; the act itself not read) -/
def p6grKlirClass : Relation → Nat
  | .spouse => 0
  | .child => 0
  | .grandchild => 0
  | .parent => 0
  | .sibling => 1
  | .nieceNephew => 1
  | _ => 2
def p6grKlir : InheritanceTax :=
  { name := "Φόρος κληρονομιών και δωρεών", classOf := p6grKlirClass,   classes := [{ allowance := 150000, sched := Schedule.ofList [(0, 100), (150000, 500), (450000, 1000)] },   { allowance := 30000, sched := Schedule.ofList [(0, 500), (70000, 1000), (270000, 2000)] },   { allowance := 6000, sched := Schedule.ofList [(0, 2000), (66000, 3000), (261000, 4000)] }],   exemptRelations := [], lookbackYears := 0,   exemptValue := fun t => if t.kind == .gift && t.relation == .child then pos t.statutoryValue else 0 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Φόρος κληρονομιών και δωρεών", covers := [.estate],
     run := fun args g prev =>
       p6grKlir.charges g.transfers "ν. 2961/2001 (Κώδικας φορολογίας κληρονομιών, δωρεών, γονικών παροχών), scales of categories Α', Β', Γ' (art. 29 and 44, as stated by PwC; the act itself not read)" }]

def absent : List Absent :=
  []

def notes : List String := ["GR 4300 Φόρος κληρονομιών και δωρεών: PwC Worldwide Tax Summaries, Greece, Individual - Other taxes, last reviewed 4 March 2025 (Internet Archive 2025-06-17) (grade B, pass 14)", "GR 4200 gap pass 2: cited absence withdrawn (OECD Revenue Statistics book revenue under 4200)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (fun t => t.kind == .gift && t.relation == .child) then ["4300 parental grant (γονική παροχή, parent to child): EUR 800 000 tax-free with the category A' rates above it; the scale above the 800 000 is not stated clearly enough to compute, so a gift to a child is charged 0 here (grade C)"] else [])
  ++ (if g.transfers.any (fun t => t.relation == .otherRelative || t.relation == .charity) then ["4300 an 'other relative' is taken as category Γ' (distant relatives); uncles and aunts, step-children, in-laws, grandparents and great-grandchildren are category Β'; legal entities and charities have their own rates (not read)"] else [])
  ++ (if !g.transfers.isEmpty then ["4300 earlier gifts and parental grants from the same person, which the act adds to the later acquisition, are not looked back on; real estate at its objective value is not in the input (the value given stands in); disability reliefs not applied"] else [])
  ++ (if true then ["4200 Taxes on net wealth (4200): not modelled (grade C: gap pass 2, OECD Revenue Statistics book revenue under 4200)"] else [])

#guard p6grKlir.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6grKlir.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 56500
#guard p6grKlir.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6grKlir.tax { kind := .inheritance, value := 1000000, relation := .child } == 56500
#guard p6grKlir.tax { kind := .inheritance, value := 100000, relation := .sibling } == 3500
#guard p6grKlir.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 163500
#guard p6grKlir.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 21600
#guard p6grKlir.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 364900
#guard p6grKlir.tax { kind := .inheritance, value := 300000, relation := .child } == 1500
#guard p6grKlir.tax { kind := .inheritance, value := 600000, relation := .parent } == 16500
#guard p6grKlir.tax { kind := .inheritance, value := 300000, relation := .nieceNephew } == 23500
#guard p6grKlir.tax { kind := .inheritance, value := 267000, relation := .otherRelative } == 71700
#guard p6grKlir.tax { kind := .gift, value := 500000, relation := .child } == 0
#guard p6grKlir.tax { kind := .gift, value := 100000, relation := .sibling } == 3500

end GrGlobal.Wealth
