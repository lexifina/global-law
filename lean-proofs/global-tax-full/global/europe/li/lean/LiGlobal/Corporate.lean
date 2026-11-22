import LiGlobal.Pit

/-!
# LI 2025: Ertragssteuer (1200) and withholding on payments abroad

Source: Steuergesetz, gesetze.li (Lilex, Rechtsdienst der Regierung, official) consolidated PDF "Fassung: 01.07.2026" (`li/law/steg_konso.pdf`): Art. 61 carries no amendment footnote since 2010; Art. 62 last amended by LGBl. 2016 Nr. 344 and 524, so the wording read applies in 2025; sha256 in `law/SHA256SUMS`.
* Art. 61 Steuersatz: "Die Ertragssteuer beträgt 12,5 % des steuerpflichtigen Reinertrags."
* Art. 62 (1): juristische Personen "unterliegen einer Mindestertragssteuer, welche unabhängig von der Dauer der Steuerpflicht im jeweiligen Steuerjahr geschuldet ist. Diese ist in vollem Umfang auf die Ertragssteuer anrechenbar." (2): "Die Mindestertragssteuer beträgt 1 800 Franken."
* Art. 62 (3): not levied where the purpose is exclusively a commercial trade and the Bilanzsumme "im Durchschnitt der letzten drei Geschäftsjahre 500 000 Franken nicht überschritten hat"


## 1200 Withholding on payments abroad (none levied): dividend, interest, royalty, services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Liechtenstein, Corporate - Withholding taxes, accessed 2025-06-17 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* no withholding taxes are levied
-/

namespace LiGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Ertragssteuer",   sched := Schedule.flat 1250,   minFixed := 1800 }

def citStatute : String := "Steuergesetz (SteG, LGBl. 2010 Nr. 340) Art. 61 (12,5 %), Art. 62 Abs. 1-2 (Mindestertragssteuer 1 800 Franken, anrechenbar)"

/-- SteG (no withholding tax) -/
def p8wht : Wht :=
  { name := "Withholding on payments abroad (none levied)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Liechtenstein levies no withholding tax on dividend paid abroad (Couponsteuer abolished from 2011)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Liechtenstein levies no withholding tax on interest paid abroad (Couponsteuer abolished from 2011)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Liechtenstein levies no withholding tax on royalty paid abroad (Couponsteuer abolished from 2011)" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Liechtenstein levies no withholding tax on services paid abroad (Couponsteuer abolished from 2011)" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Ertragssteuer", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Withholding on payments abroad (none levied) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["LI 1200: SteG Fassung 01.07.2026; Art. 61-62 unchanged since 2010 / 2016", "LI 1200 withholding pass 8 (dividend, interest, royalty, services): 2025-06-17 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 12500
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 125000
#guard cit.citTax { profit := 0, turnover := 10000000 } == 1800
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end LiGlobal.Corporate
