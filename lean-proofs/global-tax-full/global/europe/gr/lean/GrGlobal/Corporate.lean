import GrGlobal.Pit

/-!
# GR 2025: Φόρος εισοδήματος νομικών προσώπων (1200) and withholding on payments abroad

Source: ΦΕΚ Α' 78/18.05.2021 (ν. 4799/2021), Εθνικό Τυπογραφείο et.gr DownloadFeksApi fek_pdf=20210100078 (`gr/law/fek_a78_2021_n4799.pdf`); sha256 in `law/SHA256SUMS`.
* άρθρο 120: "Η περ. α' της παρ. 1 του άρθρου 58 του Κ.Φ.Ε. (ν. 4172/2013, Α' 167) τροποποιείται ως προς τον φορολογικό συντελεστή"
* "1. α) Τα κέρδη από επιχειρηματική δραστηριότητα που αποκτούν τα νομικά πρόσωπα και οι νομικές οντότητες ... φορολογικού έτους 2021 και εφεξής ο συντελεστής του προηγούμενου εδαφίου μειώνεται σε είκοσι δύο τοις εκατό (22%)."
* "β) Τα πιστωτικά ιδρύματα ... του άρθρου 27Α, φορολογούνται με συντελεστή είκοσι εννέα τοις εκατό (29%)."


## 1200 Παρακράτηση φόρου (ΚΦΕ άρθρο 64): dividend, interest, royalty, services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Greece, Corporate - Withholding taxes, accessed 2025-06-23 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* rates: 5 % on dividends; 15 % on interest; 20 % on royalties; 20 % on technical, management and consulting fees; non-resident legal entities without a Greek PE are outside the withholding on those fees
-/

namespace GrGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Φόρος εισοδήματος νομικών προσώπων",   sched := Schedule.flat 2200 }

def citStatute : String := "ΚΦΕ (ν. 4172/2013) άρθρο 58 παρ. 1 α) (22 % from tax year 2021), as replaced by ν. 4799/2021 άρθρο 120"

/-- ν. 4172/2013 (ΚΦΕ) άρθρο 64 -/
def p8wht : Wht :=
  { name := "Παρακράτηση φόρου (ΚΦΕ άρθρο 64)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 500, statute := "ν. 4172/2013 (ΚΦΕ) άρθρο 64: dividends 5 %" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ΚΦΕ άρθρο 64: interest 15 %" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "ΚΦΕ άρθρο 64: royalties 20 %" },   { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "ΚΦΕ άρθρο 64: legal entities without a PE in Greece bear no withholding on technical, consulting and management fees" },   { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 2000, statute := "ΚΦΕ άρθρο 64: 20 % on fees for technical, management and consulting services" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Φόρος εισοδήματος νομικών προσώπων", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Παρακράτηση φόρου (ΚΦΕ άρθρο 64) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["GR 1200: amending act ν. 4799/2021 read (22 % for tax year 2021 onwards); the consolidated ΚΦΕ as in force in 2025 not reached (later amendments of άρθρο 58 not checked)", "GR 1200 withholding pass 8 (dividend, interest, royalty, services): 2025-06-23 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 22000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 220000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 5000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 5000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 15000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 20000

end GrGlobal.Corporate
