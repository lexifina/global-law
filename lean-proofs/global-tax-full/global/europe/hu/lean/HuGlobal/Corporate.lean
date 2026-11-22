import HuGlobal.Pit

/-!
# HU 2025: Társasági adó (1200) and withholding on payments abroad

Source: 1996. évi LXXXI. törvény, net.jogtar.hu (Wolters Kluwer, private publisher of the consolidated text), `hu/law/tao.html`; sha256 in `law/SHA256SUMS`.
* III. Fejezet A társasági adó mértéke, 19. §: "A társasági adó mértéke 9 százalék. A társasági adó a pozitív adóalap ..."

* **Withholding on payments to non-resident companies not levied (cited, pass 6, grade B)**: Tao. (no withholding on payments to non-individuals); PwC Worldwide Tax Summaries, Hungary, Corporate - Withholding taxes, accessed 2025-06-24 (Wayback capture; `law/pwc_wht_wb2025.txt`): domestic WHT on dividends / interest / royalties to non-individuals: none (PwC WWTS Corporate - Withholding taxes, 2025-06-24 (Wayback capture))


## 1200 Forrásadó (társaságok): dividend, interest, royalty, services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Hungary, Corporate - Withholding taxes, accessed 2025-06-24 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* dividends, interest and royalties paid to a company bear no withholding under domestic law


## 1200 Személyi jövedelemadó (külföldi magánszemély: osztalék, kamat): dividend, interest (pass 9, grade A)
Source: 1995. évi CXVII. törvény a személyi jövedelemadóról, net.jogtar.hu (`hu/law/szja.txt`).
* 8. § (1): "Az e törvény hatálya alá tartozó jövedelem után az adó mértéke – ha e törvény másként nem rendelkezik – az adóalap 15 százaléka"; the payer (kifizető) withholds on interest (65. §) and dividends (66. §)
* the text read is the version in force from 1 October 2026; the 15 % rate is the one in force in 2025


## 1200 withholding still grade C (pass 12)
* Szja (`hu/law/szja.txt`, consolidated text with the 2025. évi LIV. törvény amendments) 46.-47. §: on self-employed and royalty income the Hungarian payer deducts a tax advance (adóelőleg) and the tax is settled by return; the advance base for a non-resident individual and the treaty relief path were not read clause by clause (the jogtar text interleaves amendment notes)
* would unlock: a clean 2025 text of Szja 46.-49. § and 7. § (cost ratio) or NAV's guide for payments to foreign individuals
-/

namespace HuGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Társasági adó",   sched := Schedule.flat 900 }

def citStatute : String := "1996. évi LXXXI. törvény a társasági adóról és az osztalékadóról 19. § (9 százalék)"

/-- 1996. évi LXXXI. törvény (Tao.): no withholding on payments to foreign companies -/
def p8wht : Wht :=
  { name := "Forrásadó (társaságok)", rules := [
    { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "Tao. tv.: no withholding on dividends paid to non-individuals" },   { kind := .interest, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "Tao. tv.: no withholding on interest paid to non-individuals" },   { kind := .royalty, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "Tao. tv.: no withholding on royalties paid to non-individuals" },   { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "Tao. tv.: no withholding on service fees paid to non-individuals" }] }

/-- 1995. évi CXVII. törvény (Szja tv.) 8. § (1), 65. §, 66. § -/
def p9whti : Wht :=
  { name := "Személyi jövedelemadó (külföldi magánszemély: osztalék, kamat)", rules := [
    { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 1500, statute := "Szja tv. 8. § (1), 66. §: 15 % on dividend income" },   { kind := .interest, toCompany := some false, minStakeBp := 0, rateBp := 1500, statute := "Szja tv. 8. § (1), 65. §: 15 % on interest income" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Társasági adó", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Forrásadó (társaságok) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) },
   { name := "1200 Személyi jövedelemadó (külföldi magánszemély: osztalék, kamat) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9whti.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["HU 1200: consolidated text (jogtar), current at fetch (2026-11)", "HU 1200 withholding pass 8 (dividend, interest, royalty, services): 2025-06-24 (grade B)", "HU 1200 withholding pass 9 (dividend, interest; individuals): Nemzeti Jogtár, hatályos 2026.X.1. (rate unchanged since 2016) (`hu/law/szja.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest && !p.toCompany) then ["1200 withholding: interest is taken as kamatjövedelem (65. §); interest on a private loan is other income, also 15 % (social contribution tax not applied)"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => !p.toCompany) then ["1200 withholding: royalties and service fees paid to non-resident individuals (önálló tevékenység: base and source rules) not read (grade C)"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 9000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 90000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p9whti.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 15000
#guard p9whti.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 15000

end HuGlobal.Corporate
