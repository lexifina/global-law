import TaxKernel.Global
import R5Common

/-!
# Tunisia 2025: impôt sur les sociétés (1200)

Source: Code de l'IRPP et de l'IS, DGELF edition 2025 (`law/code2025fr.txt`, the 1.x model's source):
* art. 49-I (LF 2020-46, LF 2024-48): "Le taux de l'impôt sur les sociétés … est fixé à 20%" (profits from 1 January
  2024); art. 49-I 4: 40 % for the listed financial and other sectors (flag `rate40`); 10 % for the listed
  activities (flag `rate10`).
* minimum tax: 0,2 % of turnover (code, minimum d'impôt; the floor amount is not modelled).
* non-residents: withholding at 15 % of gross amounts (royalties and fees).
-/

namespace TnGlobal
open TaxKernel TaxKernel.Global R5Common

def isRate (co : Company) : Int := if co.flags.contains "rate40" then 4000 else if co.flags.contains "rate10" then 1000 else 2000

def is (co : Company) : CorpRegime := { name := "Impôt sur les sociétés", sched := Schedule.flat (isRate co), minBp := 20 }

def ras : Wht :=
  { name := "Retenue à la source (non-résidents)",
    rules := [.royalty, .services].map (fun k => { kind := k, rateBp := 1500, statute := "Code IRPP-IS art. 52-I-b (15 % of gross amounts to non-residents)" })
      ++ [{ kind := .dividend, rateBp := 1000, statute := "Code IRPP-IS art. 52-I-c bis (10 %, distributed income, art. 29), 52-II (final)" },
          { kind := .interest, rateBp := 2000, statute := "Code IRPP-IS art. 52-I-c (20 %, revenus de capitaux mobiliers), 52-II (final)" }] }

def corporate : Family := corpFamily "1200 impôt sur les sociétés" is (fun co => s!"Code IRPP-IS art. 49-I ({isRate co / 100} %), minimum 0,2 % of turnover") ras

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true true false true
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest) then ["withholding on interest: 20 % (art. 52-I-c); loans from banks not established in Tunisia 10 % (52-I-e) and currency deposits exempt not distinguished"] else [])

#guard (is {}).citTax { profit := 1000000, turnover := 2000000 } == 200000
#guard (is {}).citTax { profit := 0, turnover := 2000000 } == 4000

end TnGlobal
