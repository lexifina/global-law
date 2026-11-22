import PlGlobal.Pit

/-!
# PL 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (ustawa o podatku od spadków i darowizn (grupy I-III)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)


## 4300 Podatek od spadków i darowizn (pass 6)
Source: ustawa z dnia 28 lipca 1983 r. o podatku od spadków i darowizn, tekst jednolity Dz.U. 2024 poz. 1837 (Sejm ELI API, `pl/law/spadki_tj2024_1837.pdf`); amending act Dz.U. 2025 poz. 1064 read (`pl/law/spadki_zm2025_1064.pdf`: arts. 4a, 6, 12, 13, 18-19, procedure and valuation only).
* art. 4a ust. 1: "Zwalnia się od podatku nabycie własności rzeczy lub praw majątkowych przez małżonka, zstępnych, wstępnych, pasierba, rodzeństwo, ojczyma i macochę, jeżeli" reported within 6 months
* art. 9 ust. 1: tax-free amounts "36 120 zł" (grupa I), "27 090 zł" (II), "5733 zł" (III); ust. 2: acquisitions from the same person in the year and the 5 preceding years are added, less the tax on the earlier ones
* art. 14 ust. 3: grupa I spouse, descendants, ascendants, stepchild, children-in-law, siblings, step-parents, parents-in-law; II descendants of siblings, siblings of parents, ...; III others
* art. 15 ust. 1: I 3 % to 10 278 zł, 308,30 zł + 5 % to 20 556 zł, 822,20 zł + 7 % above; II 7 % / 719,50 + 9 % / 1644,50 + 12 %; III 12 % / 1233,40 + 16 % / 2877,90 + 20 %

* **4200 not levied (cited, gap pass, grade B)**: European Commission TEDB, PL: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 461, 687, 458, 460, 2983, 6060, 4090, 452, 878, 879): the TEDB lists Poland's taxes in force on 1.7.2025 (real estate tax, tax on civil law transactions, transport vehicles tax, stamp duty, agricultural tax, retail sales tax, tax on assets of financial institutions, excise duty, payments to the disabled persons fund, tax on games); none is levied on an individual's net wealth (OECD Interpretative Guide § 51: 4200 covers taxes levied regularly on net wealth, i.e. on a wide range of assets net of debt) (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))
-/

namespace PlGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- ustawa o podatku od spadków i darowizn art. 4a ust. 1, art. 9 ust. 1-2, art. 14 ust. 3, art. 15 ust. 1 -/
def p6sdClass : Relation → Nat
  | .nieceNephew => 1
  | .otherRelative => 1
  | _ => 2
def p6sd : InheritanceTax :=
  { name := "Podatek od spadków i darowizn", classOf := p6sdClass,   classes := [{ allowance := 36120, sched := Schedule.ofList [(0, 300), (10278, 500), (20556, 700)] },   { allowance := 27090, sched := Schedule.ofList [(0, 700), (10278, 900), (20556, 1200)] },   { allowance := 5733, sched := Schedule.ofList [(0, 1200), (10278, 1600), (20556, 2000)] }],   exemptRelations := [.spouse, .child, .grandchild, .parent, .sibling], lookbackYears := 6 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Podatek od spadków i darowizn", covers := [.estate],
     run := fun args g prev =>
       p6sd.charges g.transfers "ustawa o podatku od spadków i darowizn art. 4a ust. 1, art. 9 ust. 1-2, art. 14 ust. 3, art. 15 ust. 1" }]

def absent : List Absent :=
  [{ oecd := .wealth, why := "the TEDB lists Poland's taxes in force on 1.7.2025 (real estate tax, tax on civil law transactions, transport vehicles tax, stamp duty, agricultural tax, retail sales tax, tax on assets of financial institutions, excise duty, payments to the disabled persons fund, tax on games); none is levied on an individual's net wealth (OECD Interpretative Guide § 51: 4200 covers taxes levied regularly on net wealth, i.e. on a wide range of assets net of debt)" }]

def notes : List String := ["PL 4300 Podatek od spadków i darowizn: t.j. Dz.U. 2024 poz. 1837 (amended by Dz.U. 2025 poz. 769, 1064: not the rates or allowances) (grade A)", "PL 4200 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty then ["4300 art. 4a exemption assumes the 6-month report is made; otherwise grupa I; otherRelative taken as grupa II (in-laws are I, cousins III); the scale's fixed amounts are rounded (308,30 zł vs 3 % of 10 278 = 308,34); look-back taken as 6 years"] else [])

#guard p6sd.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6sd.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 0
#guard p6sd.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6sd.tax { kind := .inheritance, value := 1000000, relation := .child } == 0
#guard p6sd.tax { kind := .inheritance, value := 100000, relation := .sibling } == 0
#guard p6sd.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 0
#guard p6sd.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 17620
#guard p6sd.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 197620

end PlGlobal.Wealth
