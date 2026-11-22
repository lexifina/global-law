import TaxKernel.Global
import R5Common

/-!
# Jordan 2025: income tax on juristic persons and the national contribution (1200)

Source: Income Tax Law No. 34 of 2014 as amended by Law No. 38 of 2018, ISTD consolidated text (`law/itl_p2.txt`):
* art. 11(b): "(20%) … لجميع الأشخاص الاعتباريين" except (2) "(24%)" basic telecom, electricity distribution and
  generation, mining of basic materials, insurance and reinsurance, financial intermediation, financial companies and
  leasing; (3) "(35%) … للبنوك".
* art. 11(و): national contribution on taxable income: 3 % banks and electricity; 7 % basic mining; 4 % financial
  intermediation and leasing; 2 % basic telecom and insurance; "1% … لباقي الأشخاص الاعتباريين".
Sector flags on the company: `bank`, `telecomEnergy`, `mining`, `financial`, `insurance`.
-/

namespace JoGlobal
open TaxKernel TaxKernel.Global R5Common

def has (co : Company) (f : String) : Bool := co.flags.contains f

def citRate (co : Company) : Int :=
  if has co "bank" then 3500
  else if has co "telecomEnergy" || has co "mining" || has co "financial" || has co "insurance" then 2400 else 2000

def ncRate (co : Company) : Int :=
  if has co "bank" then 300 else if has co "mining" then 700 else if has co "financial" then 400
  else if has co "telecomEnergy" || has co "insurance" then 200 else 100

def it (co : Company) : CorpRegime := { name := "ضريبة الدخل", sched := Schedule.flat (citRate co) }

/-- art. 12(B)(1): "Any person who owed or paid a taxable income to a non-resident person … shall withhold … (10%)"
(Arabic text of art. 12 in `law/itl_p2.txt`); taxable Jordanian-source income includes interest (art. 3(A)(2)),
royalties (3(A)(3)) and services used in the Kingdom (3(A)(12)); dividends of resident companies are exempt
(art. 4(A)(8); ISTD unofficial English consolidation, Wayback 2023-10-10, `law/jo_itl_34_2014_en_consol2018.pdf`). -/
def joWht : Wht :=
  { name := "اقتطاع الضريبة (غير المقيم)",
    rules := [{ kind := .interest, rateBp := 1000, statute := "ITL 34/2014 art. 12(B)(1), 3(A)(2) (10 %)" },
              { kind := .royalty, rateBp := 1000, statute := "ITL 34/2014 art. 12(B)(1), 3(A)(3) (10 %)" },
              { kind := .services, rateBp := 1000, statute := "ITL 34/2014 art. 12(B)(1), 3(A)(12) (10 %)" },
              WhtRule.zero .dividend "ITL 34/2014 art. 4(A)(8): dividends of resident companies exempt"] }

def corporate : Family :=
  { name := "1200 ضريبة الدخل والمساهمة الوطنية", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      [(it co).citCharge co s!"ITL 34/2014 art. 11(b) ({citRate co / 100} %)",
       charge .cit "المساهمة الوطنية" ((it co).taxableProfit co) id (fun t => divR .down (ncRate co * pos t) BP)
         (statute := s!"ITL 34/2014 art. 11(و) ({ncRate co} bp)")] ++ joWht.charges co }

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true true false true
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest) then ["withholding on interest: 10 % (art. 12(B)(1)); bank-deposit interest (5 % / 7 %, art. 12(A)(2)) not distinguished"] else [])

#guard (it {}).citTax { profit := 1000000 } == 200000
#guard joWht.amount { kind := .royalty, amount := 100000 } == 10000
#guard (it { flags := ["bank"] }).citTax { profit := 1000000 } == 350000

end JoGlobal
