import TaxKernel.Global
import R5Common

/-!
# Israel 2025: companies tax (מס חברות, 1200)

Source: Income Tax Ordinance [New Version], Hebrew Wikisource (`law/il_ito.txt`; grade B):
s. 126(a): "יוטל מס שייקרא מס חברות, בשיעור 23%"; s. 126(b): dividends from income produced in Israel received
directly from another company are not included (participation exemption, no stake test).
-/

namespace IlGlobal
open TaxKernel TaxKernel.Global R5Common

def mh : CorpRegime := { name := "מס חברות", sched := Schedule.flat 2300, participationBp := 10000 }

/-- Ordinance s. 170(a) (Wikisource consolidation, `law/il_ito.txt`): whoever pays a non-resident taxable income from
which tax was not deducted under s. 161 or 164 deducts "25 אגורות לכל לירה" for an individual, and the s. 126 rate
(23 %) for a body of persons. Dividends and interest (pass 3k): Income Tax (Deduction from Interest, Dividend and Certain Profits) Regulations 2005
(s. 164, 243; Hebrew Wikisource, `law/il_wht_regs2005.txt`): reg. 2(b) an Israeli body paying a dividend to a non-resident
deducts 30 % if the recipient was a substantial shareholder (s. 88: 10 % of any means of control) at the payment or in the
preceding 12 months, else 25 %; reg. 7(a) interest to a body of persons: the maximum rate, reg. 1(2) = s. 126(a) (23 %).
Interest to an individual: reg. 5(a) 25 %, 15 % on a non-index-linked asset, reg. 6 the maximum rate for a substantial
shareholder: the linkage is not an input (grade C). -/
def ilWht : Wht :=
  { name := "ניכוי במקור לתושב חוץ",
    rules := [{ kind := .royalty, toCompany := some true, rateBp := 2300, statute := "Ordinance s. 170(a), 126(a) (23 %)" },
              { kind := .services, toCompany := some true, rateBp := 2300, statute := "Ordinance s. 170(a), 126(a) (23 %)" },
              { kind := .royalty, toCompany := some false, rateBp := 2500, statute := "Ordinance s. 170(a) (25 agorot per lira)" },
              { kind := .dividend, minStakeBp := 1000, rateBp := 3000, statute := "Income Tax (Deduction from Interest, Dividend and Certain Profits) Regulations 2005 reg. 2(b)(1) (non-resident substantial shareholder, Ordinance s. 88: 10 %): 30 %" },
              { kind := .dividend, rateBp := 2500, statute := "Income Tax (Deduction from Interest, Dividend and Certain Profits) Regulations 2005 reg. 2(b)(2) (non-resident): 25 %" },
              { kind := .interest, toCompany := some true, rateBp := 2300, statute := "Income Tax (Deduction from Interest, Dividend and Certain Profits) Regulations 2005 reg. 7(a), 1 (body of persons: the maximum rate = s. 126(a) 23 %)" },
              { kind := .services, toCompany := some false, rateBp := 2500, statute := "Ordinance s. 170(a) (25 agorot per lira)" }] }

def corporate : Family := corpFamily "1200 מס חברות" (fun _ => mh) (fun _ => "Income Tax Ordinance s. 126(a) (23 %), 126(b)") ilWht

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true true false false
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .royalty || p.kind == .services) then ["withholding (s. 170(a)): taken at the full rate; an assessing officer's reduced-rate certificate and Israeli-source test not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .dividend) then ["dividend withholding (reg. 2(b)): stake at the payment taken for the 12-month substantial-shareholder test; treaty rates need a certificate (not applied)"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest && !p.toCompany) then ["interest to an individual abroad: reg. 5(a) 25 % or 15 % by index linkage, reg. 6 maximum rate for a substantial shareholder; linkage not an input (grade C)"] else [])

#guard mh.citTax { profit := 1000000, dividendsReceived := 100000 } == 207000
#guard ilWht.amount { kind := .services, amount := 100000, toCompany := false } == 25000
#guard ilWht.amount { kind := .dividend, amount := 100000, stakeBp := 1000 } == 30000
#guard ilWht.amount { kind := .dividend, amount := 100000, stakeBp := 500, toCompany := false } == 25000
#guard ilWht.amount { kind := .interest, amount := 100000 } == 23000

end IlGlobal
