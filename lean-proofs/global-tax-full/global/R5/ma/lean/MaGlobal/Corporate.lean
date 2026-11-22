import TaxKernel.Global
import R5Common

/-!
# Morocco 2025: impôt sur les sociétés (1200), cotisation minimale, retenues à la source

Source: CGI 2025 (DGI edition; `law/cgi2025fr.txt`):
* art. 19-I (LF 50-22): A 20 %, B 35 % for net profit ≥ 100 000 000; art. 247-XXXVII-A transitional rates for the
  financial year opened from 1 January 2025: 1) profit ≤ 300 000: 17,50 %; 300 001-1 000 000: 20 %; 5) profit above
  1 000 000 and below 100 000 000: 22,75 %; profit ≥ 100 000 000: 34 %; 6) credit institutions and insurers 39,25 %.
  The rate is a proportional rate on the whole profit chosen by its size (not marginal bands).
* art. 144-D: cotisation minimale 0,25 % of turnover (a minimum: the higher of IS and the CM is due).
* art. 19-IV-B: 10 % on the gross products of non-residents listed in art. 15 (royalties, services, interest on loans
  from abroad); art. 247-XXXVII-C: dividends distributed from 1 January 2025: 12,50 %.
-/

namespace MaGlobal
open TaxKernel TaxKernel.Global R5Common

def isRate (co : Company) (taxable : Int) : Int :=
  if co.flags.contains "financial" then 3925
  else if taxable ≥ 100000000 then 3400
  else if taxable > 1000000 then 2275
  else if taxable > 300000 then 2000
  else 1750

def isRegime : CorpRegime := { name := "Impôt sur les sociétés", sched := Schedule.flat 0, minBp := 25 }

def isDue (co : Company) : Int :=
  let t := isRegime.taxableProfit co
  max (divR .down (isRate co t * t) BP) (isRegime.minimumTax co)

def ras : Wht :=
  { name := "Retenue à la source",
    rules := [{ kind := .dividend, rateBp := 1250, statute := "CGI art. 247-XXXVII-C (12,50 % from 1 January 2025)" }]
      ++ [.interest, .royalty, .services, .rent].map fun k =>
        { kind := k, rateBp := 1000, statute := "CGI art. 19-IV-B (10 % of non-residents' gross products, art. 15)" } }

def corporate : Family :=
  { name := "1200 impôt sur les sociétés", covers := [.cit, .incomeOther],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      [charge .cit "Impôt sur les sociétés" (isRegime.beforeLosses co) (fun _ => isRegime.taxableProfit co) (fun _ => isDue co)
        (statute := s!"CGI art. 19-I, 247-XXXVII-A ({isRate co (isRegime.taxableProfit co)} bp for 2025), art. 144-D (0,25 % minimum)")]
      ++ ras.charges co }

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true true false true

#guard isDue { profit := 200000, turnover := 1000000 } == 35000
#guard isDue { profit := 500000, turnover := 1000000 } == 100000
#guard isDue { profit := 5000000, turnover := 10000000 } == 1137500
#guard isDue { profit := 0, turnover := 10000000 } == 25000
#guard ras.amount { kind := .dividend, amount := 1000000 } == 125000

end MaGlobal
