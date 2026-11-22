import TaxKernel.Global
import R5Common

/-!
# Cyprus 2025: corporate income tax (1200) and withholding on royalties

Source: Income Tax Law 118(Ι)/2002, cylaw consolidation as of 2025-11-09 (`law/itl_118_2002_as_of_2025-11-09.txt`;
Law 244(Ι)/2025, `law/2025_1_244.txt`, raises the rate to 15 % only from 1 January 2026):
* s. 29(2): "Οι Εταιρείες, υπόκεινται σε εταιρικό φόρο με συντελεστή δώδεκα και μισό τοις εκατόν (12,5%)".
* s. 8(20): dividend income exempt (dividends received by a company: participation exemption with no stake test).
* s. 21: royalties and similar income from Cyprus sources of a non-resident: tax "με συντελεστή δέκα σεντ κατά λίρα"
  (10 %). The Law levies no withholding on dividends or interest paid to non-resident companies.
-/

namespace CyGlobal
open TaxKernel TaxKernel.Global R5Common

def eft : CorpRegime := { name := "Εταιρικός φόρος", sched := Schedule.flat 1250, participationBp := 10000 }

def whtNonResident : Wht :=
  { name := "Φόρος παρακράτησης (μη κάτοικοι)",
    rules := [{ kind := .royalty, rateBp := 1000, statute := "ITL s. 21 (10 cents per pound: 10 %)" },
              { kind := .services, rateBp := 1000, statute := "ITL s. 21 consideration for technical assistance (10 %); s. 24 (withholding)" },
              WhtRule.zero .dividend "ITL s. 8(20) dividends exempt; SDC Law 117(I)/2002 s. 3(2)(a) charges residents only ((a1): 17 % to affiliated low-tax/non-cooperative companies, not applied)",
              WhtRule.zero .interest "ITL s. 8(19) interest exempt; SDC Law s. 3(2)(b) charges residents only ((b1): 17 % to affiliated non-cooperative companies, not applied)"] }

def corporate : Family :=
  corpFamily "1200 εταιρικός φόρος" (fun _ => eft) (fun _ => "ITL 118(Ι)/2002 s. 29(2) (12,5 %), s. 8(20) (dividends exempt)") whtNonResident

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true true false false
  ++ (if g.entity == .company && g.company.dividendsReceived ≠ 0 then ["Special Defence Contribution on dividends received from abroad (Law 117(Ι)/2002) not modelled"] else [])

#guard eft.citTax { profit := 1000000 } == 125000
#guard eft.citTax { profit := 1000000, dividendsReceived := 200000 } == 100000
#guard whtNonResident.amount { kind := .royalty, amount := 1000 } == 100
#guard whtNonResident.amount { kind := .dividend, amount := 1000 } == 0
#guard whtNonResident.amount { kind := .services, amount := 1000 } == 100
#guard (whtNonResident.ruleFor { kind := .interest, amount := 1 }).isSome

end CyGlobal
