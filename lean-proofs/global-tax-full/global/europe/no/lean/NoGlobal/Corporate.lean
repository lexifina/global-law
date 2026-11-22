import NoGlobal.Pit
import TaxKernel.Global2

/-!
# NO 2025: Inntektsskatt for selskaper (skatt til staten) (1200) and withholding on payments abroad

Source: Stortingsvedtak om skatt av inntekt og formue mv. for inntektsåret 2025 (lovdata `STV/forskrift/2024-12-13-3203`, `no/law/stv_skatt2025.html`); sha256 in `law/SHA256SUMS`.
* § 3-3: "Selskaper og innretninger som nevnt i skatteloven § 2-36 annet ledd , svarer skatt til staten med 22 pst. av inntekten."
* § 3-3 annet ledd: 25 pst. for companies paying finansskatt på lønn


## 1200 Kildeskatt: dividend, interest, royalty, services (pass 8, grade A)
Source: Stortingets vedtak om skatt av inntekt og formue mv. for inntektsåret 2025, Lovdata (`no/law/stv_skatt2025.txt`); skatteloven (TOC, `no/law/skatteloven.txt`).
* § 3-5: "Av aksjeutbytte som utdeles til aksjonær som er hjemmehørende i utlandet, svares skatt til staten med 25 pst."; income under skatteloven §§ 10-80 and 10-81 of taxpayers in § 2-3 (1) i and j: 15 pst.
* § 3-6: 15 pst. on fees to foreign artists


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: p8wht -> p10noSw)
Source: Skatteloven §§ 10-63, 10-80 to 10-82, Lovdata (`no/law/sktl_10-*.txt`); Stortingets vedtak om skatt av inntekt og formue mv. for inntektsåret 2025 § 3-5 (`no/law/stv_skatt2025.txt`).
* § 10-80 (1): a company or entity resident in a low-tax country (§ 10-63) pays tax on interest received from a related company; § 10-81 likewise on royalties; § 10-82: related = at least 50 % owned or controlled, directly or indirectly, either way
* § 10-63: a low-tax country taxes the company's total profit at less than two thirds of the Norwegian tax; § 10-80 (2) a: no tax where the recipient is genuinely established with real economic activity in an EEA state (not in the input: noted)
* Stortingets skattevedtak 2025 § 3-5: "Av inntekt etter bestemmelsene i skatteloven § 10-80 og § 10-81 ... svare skatt til staten med 15 pst."
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate
-/

namespace NoGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Inntektsskatt for selskaper (skatt til staten)",   sched := Schedule.flat 2200 }

def citStatute : String := "Stortingets skattevedtak for inntektsåret 2025 (FOR-2024-12-13-3203) § 3-3 første ledd (22 pst.)"

/-- Stortingets skattevedtak for 2025 §§ 3-5, 3-6; skatteloven § 2-3 (1) i, j, §§ 10-80, 10-81 -/
def p8wht : Wht :=
  { name := "Kildeskatt", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 2500, statute := "Stortingets skattevedtak 2025 § 3-5 (2): 25 pst. on dividends to shareholders resident abroad" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "skattevedtak 2025 § 3-5 (5), skatteloven § 2-3 (1) i: interest bears source tax only when paid to a related company in a low-tax state: none otherwise" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "skattevedtak 2025 § 3-5 (5), skatteloven § 2-3 (1) j: royalties bear source tax only when paid to a related company in a low-tax state: none otherwise" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "skattevedtak 2025 §§ 3-5, 3-6: the source taxes are on dividends, interest and royalties to related low-tax companies and foreign artists' fees: none on service fees" }] }

/-- p8wht with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10noSw : StateWht :=
  { name := p8wht.name, rules := [
     { rule := { kind := .interest, toCompany := some true, minStakeBp := 5000, rateBp := 1500, statute := "skatteloven § 10-80, § 10-82, § 10-63; Stortingets skattevedtak 2025 § 3-5: 15 pst. on interest to a related (at least 50 %) company in a low-tax country" }, tests := [.lowTax true], ifUnknown := .general },    { rule := { kind := .royalty, toCompany := some true, minStakeBp := 5000, rateBp := 1500, statute := "skatteloven § 10-81, § 10-82, § 10-63; Stortingets skattevedtak 2025 § 3-5: 15 pst. on royalties to a related (at least 50 %) company in a low-tax country" }, tests := [.lowTax true], ifUnknown := .general }] ++ p8wht.rules.map StateRule.plain, round := p8wht.round }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Inntektsskatt for selskaper (skatt til staten)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Kildeskatt (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10noSw.charges g else []) }]

def absent : List Absent :=
  []

def notes : List String := ["NO 1200: Stortingets skattevedtak, ikrafttredelse inntektsåret 2025", "NO 1200 withholding pass 8 (dividend, interest, royalty, services): Lovdata, FOR-2024-12-13-3203 (`no/law/stv_skatt2025.txt`) (grade A)", "NO 1200 withholding by recipient state pass 10 (p8wht -> p10noSw): Lovdata (`no/law/sktl_10-80.txt`, `sktl_10-82.txt`, `sktl_10-63.txt`); Stortingsvedtak 2024-12-13-3203 (`no/law/stv_skatt2025.txt`)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .dividend) then ["1200 withholding: the exemption for EEA companies (skatteloven § 2-38) not applied"] else [])
  ++ (if !(p10noSw.notes g).isEmpty then ["1200 withholding: the 15 % of skatteloven § 10-80 / 10-81 (related company in a low-tax country) was not tested because lowTax is not given: none is booked"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 22000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 220000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard (p10noSw.chargeOf { kind := .interest, amount := 100000, toCompany := true, stakeBp := 6000 } { lowTax := some true } 0).due == 15000
#guard (p10noSw.chargeOf { kind := .interest, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 0
#guard (p10noSw.chargeOf { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 6000 } { lowTax := some true } 0).due == 0

end NoGlobal.Corporate
