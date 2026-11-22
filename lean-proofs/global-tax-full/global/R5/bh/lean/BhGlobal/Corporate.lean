import TaxKernel.Global
import R5Common

/-!
# Bahrain 2025: income tax on oil companies (1200)

Legislative Decree No 22 of 1979 (Income Tax Law, replacing Decree 80/1955), Legislation & Legal Opinion Commission
English text published May 2024 (`lloc.gov.bh/FullEn/L2279.docx`, saved `law/lloc_FullEn_L2279.txt`): art. 2: income tax at "forty-six per cent (46%)" of each
taxable year's income of a company, wherever established, that directly explores for or produces crude oil (art. 1:
petroleum incl. condensate). Computed for a company flagged `oil`; other companies
bear no income tax under this law (no general corporate income tax).
Legislative Decree No 11 of 2024 (LLOC English June 2025, `law/lloc_FullEn_L1124.txt`): a domestic minimum top-up tax at
the "Minimum Rate ... fifteen percent (15%)" on constituent entities of multinational groups within its scope, from
fiscal years starting 1/1/2025: not computed (GloBE base and group revenue test).
**Grade B** (official commission's English translation; the Arabic Gazette text not read).
-/

namespace BhGlobal
open TaxKernel TaxKernel.Global R5Common

def it : CorpRegime := { name := "Income tax (oil companies)", sched := Schedule.flat 4600 }

/-- LD 22/1979 art. 1(d), 2 (LLOC English text, May 2024): the income tax is levied only on bodies directly engaged in
hydrocarbon exploration or production, on their income from hydrocarbon sales; the Decree-Law has no tax on payments
to non-residents, and the DMTT Decree-Law 11/2024 charges only a group top-up tax (no withholding provision). -/
def bhWht : Wht :=
  { name := "Withholding tax", rules := Wht.zeroOn [.dividend, .interest, .royalty, .services]
      "LD 22/1979 art. 1(d), 2: income tax only on hydrocarbon producers' income; no tax on payments abroad (LD 11/2024: top-up tax only)" }

def corporate : Family :=
  { name := "1200 Income tax (Legislative Decree 22/1979)", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      (if !g.company.flags.contains "oil" then [] else
      [it.citCharge g.company "Legislative Decree 22/1979 art. 2 (46 %, crude oil exploration and production)"])
      ++ bhWht.charges g.company }

def corporateUnsupported (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.flags.contains "oil" then corpInputsUnread g false true true true else [])
  ++ ["domestic minimum top-up tax on multinational groups (Legislative Decree 11/2024, 15 %) not computed"]

#guard it.citTax { profit := 1000000 } == 460000

end BhGlobal
