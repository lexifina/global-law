import MtGlobal.Pit

/-!
# MT 2025: Income tax (companies) (1200) and withholding on payments abroad

Source: Income Tax Act, Cap. 123, legislation.mt consolidated PDF (official; consolidation later than 2025, read through an unchanged rate), `mt/law/cap123.pdf`; sha256 in `law/SHA256SUMS`.
* art. 56 (6): "The tax shall be charged at the rate of thirty-five cents (0.35) on every euro of the chargeable income of every - (a) company; (b) body corporate established by law; ..."

* **Withholding on payments to non-resident companies not levied (cited, pass 6, grade B)**: Income Tax Act Cap. 123 (no withholding on dividends; interest and royalties to non-residents exempt subject to conditions); PwC Worldwide Tax Summaries, Malta, Corporate - Withholding taxes, accessed 2025-05-27 (Wayback capture; `law/pwc_wht_wb2025.txt`): non-treaty WHT to non-resident companies: 0 % on dividends, interest, royalties (interest / royalties exempt unless connected with a Maltese PE) (PwC WWTS Corporate - Withholding taxes, 2025-05-27 (Wayback capture))


## 1200 Withholding on payments abroad (interest, royalties): interest, royalty (pass 8, grade A)
Source: Income Tax Act, Cap. 123, legislation.mt (`mt/law/cap123.txt`).
* art. 12 (1): "There shall be exempt from the tax - ... (c) (i) any interest, discount, premium or royalties accruing to or derived by any person not resident in Malta" (provisos: PE in Malta, resident owners)


## 1200 Withholding on dividends (none): dividend (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Malta, Corporate - Withholding taxes, accessed 2025-05-27 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* dividends carry no withholding: the company's tax is imputed to the shareholder


## 1200 withholding still grade C (pass 9)
* Cap. 123 read for withholding on payments to non-residents: only investment income (art. 41) and the art. 12 (1) (c) exemptions; a non-resident's Malta-source service income is taxed by return (art. 4), no deduction at source found
* would unlock: the Final Settlement System rules (S.L. 123.13) on payments to non-residents, to confirm that no deduction applies


## 1200 withholding still grade C (pass 12)
* Cap. 123 (`mt/law/cap123.txt`) re-read: the only deduction at source on a non-resident's fees for services is art. 23 (5) (a), petroleum Contractors paying non-resident sub-contractors at the art. 56 (13) (b) rate; any other non-resident's Malta-source service income is charged by return (art. 4), so a generic company deducts nothing
* would unlock: a Commissioner for Tax and Customs guide or the FSS rules (S.L. 123.13) stating that no other deduction applies, to cite the 0 as A


## 1200 income tax (companies) and withholding on interest and royalties: 2025 text read, A (gap pass, grade C)
Source: Laws of Malta (legislation.mt consolidations) read from lexifina/malta-law: Income Tax Act Cap. 123 art. 56(6) and 12(1)(c)(i) (version of 17.4.2025, commit cdc104a5; e96cb3ae).
* art. 56(6): "thirty-five cents (0.35) on every euro of the chargeable income of every - (a) company"
* art. 12(1)(c)(i): interest, discount, premium or royalties accruing to a person not resident in Malta are exempt
-/

namespace MtGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax (companies)",   sched := Schedule.flat 3500 }

def citStatute : String := "Income Tax Act (Cap. 123) art. 56 (6) (a) (thirty-five cents on every euro)"

/-- Income Tax Act (Cap. 123) art. 12 (1) (c) (i) -/
def p8wht : Wht :=
  { name := "Withholding on payments abroad (interest, royalties)", rules := [
    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Income Tax Act (Cap. 123) art. 12 (1) (c) (i): interest accruing to a person not resident in Malta is exempt" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Cap. 123 art. 12 (1) (c) (i): royalties accruing to a person not resident in Malta are exempt" }] }

/-- Income Tax Act (Cap. 123): full imputation, no tax on distributions -/
def p8wht2 : Wht :=
  { name := "Withholding on dividends (none)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "full imputation system: no withholding on dividends paid to non-residents" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Income tax (companies)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Withholding on payments abroad (interest, royalties) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) },
   { name := "1200 Withholding on dividends (none) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["MT 1200: legislation.mt consolidation (after 2025)", "MT 1200 withholding pass 8 (interest, royalty): legislation.mt consolidated text (`mt/law/cap123.txt`) (grade A)", "MT 1200 withholding pass 8 (dividend): 2025-05-27 (grade B)", "MT 1200 Income tax (companies): back to B (pass 17, 2025 text read)", "MT 1200 Withholding on payments abroad (interest, royalties) (interest, royalty): back to B (pass 17, 2025 text read)", "MT gap pass: 1200 income tax (companies) and withholding on interest and royalties: 2025 text read, A"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 35000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 350000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end MtGlobal.Corporate
