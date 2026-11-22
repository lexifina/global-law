import TaxKernel.Global2
import R5Common

/-!
# Saudi Arabia 2025: income tax on companies (1200) and withholding on payments to non-residents

Source: Income Tax Law (Royal Decree M/1, 15/1/1425H), laws.boe.gov.sa as archived on 2025-05-07 (`law/itl_2025.html`):
* art. 7(a): "سعر الضريبة على الوعاء الضريبي هو عشرون بالمائة (20%)" for resident capital companies (on the
  non-Saudi/non-GCC share: the Saudi share pays zakat instead, P7), non-Saudi resident individuals in business, and
  non-residents through a permanent establishment; art. 7(b) natural gas 30 %; 7(c) oil and hydrocarbons 85 % (flags).
  The share of the company's profit owned by Saudi/GCC holders is the input field `zakatShareBp` (bp, default 0:
  the whole profit is taxed).
* art. 21(a): net operating losses carried forward until recovered; the annual cap is set by the Implementing
  Regulations (not read: losses offset in full, flagged).
* art. 68(a): withholding on payments from a Saudi source to non-residents: rent 5 %, royalties ("إتاوة أو ريع") 15 %,
  management fees 20 %, air tickets and freight 5 %, international telecom 5 %; other payments as the Regulations set
  (dividends and interest: in the Regulations).
* Implementing Regulations (Ministerial Resolution 1535, 1425H, as amended to Resolution 2568, 1440H; ZATCA Arabic
  consolidation archived 2025-11-18, `law/zatca/Regulations_of_Income_Tax.pdf`) art. 63(1): management fees 20 %;
  royalties and technical services to the head office or a related company 15 %; other technical or consulting
  services, rent, air tickets and freight, dividends, loan returns, insurance premiums 5 %; any other payments 15 %.
-/

namespace SaGlobal
open TaxKernel TaxKernel.Global R5Common

def citRate (co : Company) : Int :=
  if co.flags.contains "hydrocarbons" then 8500 else if co.flags.contains "naturalGas" then 3000 else 2000

/-- The Saudi/GCC share, bp: the complement of the kernel 2.1 taxable share. -/
def zakatShareBp (g : CanonGlobal) : Int :=
  BP - ({ regime := { name := "", sched := Schedule.flat 0 }, shareKey := "zakatShareBp", shareComplement := true } : CorpRule).shareOf g

def incomeTax (co : Company) : CorpRegime := { name := "ضريبة الدخل", sched := Schedule.flat (citRate co) }

def whtNonResident : Wht :=
  { name := "ضريبة الاستقطاع",
    rules := [{ kind := .rent, rateBp := 500, statute := "ITL art. 68(a)(1) (5 %)" },
              { kind := .royalty, rateBp := 1500, statute := "ITL art. 68(a)(2) (15 %)" },
              { kind := .services, rateBp := 2000, statute := "ITL art. 68(a)(3) management fees (20 %)" },
              { kind := .dividend, rateBp := 500, statute := "Implementing Regulations art. 63(1) dividends (5 %)" },
              { kind := .interest, rateBp := 500, statute := "Implementing Regulations art. 63(1) loan returns (5 %)" },
              { kind := .other, rateBp := 1500, statute := "Implementing Regulations art. 63(1) any other payments (15 %)" }] }

/-- Kernel 2.1 `CorpRule`: CIT on the non-Saudi/non-GCC share (`zakatShareBp` read as the complement). -/
def saRule (co : Company) : CorpRule := { regime := incomeTax co, shareKey := "zakatShareBp", shareComplement := true }

def corporate : Family :=
  { name := "1200 ضريبة الدخل", covers := [.cit, .incomeOther],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      [(saRule co).citCharge g s!"ITL art. 7 ({citRate co / 100} %) on the non-Saudi share ({(saRule co).shareOf g} bp), art. 21 (losses)"]
      ++ whtNonResident.charges co }

def corporateUnsupported (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.lossesForward ≠ 0 then ["losses: annual cap of the Implementing Regulations not read; offset in full"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services) then
    ["withholding on services: taken as management fees (20 %); technical or consulting services are 5 % (15 % to a related party) under Regulations art. 63(1)"] else [])
  ++ corpInputsUnread g false true false true

#guard (incomeTax {}).citTax { profit := 1000000 } == 200000
#guard whtNonResident.amount { kind := .royalty, amount := 100000 } == 15000
#guard whtNonResident.amount { kind := .dividend, amount := 100000 } == 5000

end SaGlobal
