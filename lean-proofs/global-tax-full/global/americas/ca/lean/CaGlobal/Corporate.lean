import CaGlobal.Pit

/-!
# Canada 2025 (Ontario): federal and Ontario corporate income tax, Part XIII withholding (1200)

Sources: Income Tax Act (Justice Laws, current to 2026-10-29; `ca/law/I-3.3.txt`) and Ontario Taxation Act, 2007
(e-Laws, `ca/law/on_07t11.txt`).
* **ITA s. 123 (1) (a)** "38% of its amount taxable"; **s. 124 (1)** abatement "10% of the corporation's taxable
  income earned in the year in a province"; **s. 123.4** general rate reduction 13 % (from 2012): 15 %.
* **s. 125 (1), (1.1) (c)** small business deduction rate "19%" for a Canadian-controlled private corporation on its
  business limit ($500,000, s. 125 (2)): 9 %. The company flag `ccpc` selects it (all profit taken as active business
  income).
* **Ontario Taxation Act, 2007**: general rate "11.5 per cent" (from 1 July 2011); small business deduction "8.3 per
  cent" (2020 - June 2026): 3.2 % on the first $500,000 (grade B: the business-limit link to the federal one not read).
* **ITA s. 212 (1)**: "an income tax of 25%" on dividends, rents, royalties and non-arm's-length interest paid to
  non-residents (arm's-length interest is exempt: flagged).

**Pass 7 (2026-11-21):** services: ITA s. 212 (1) (a) (Part XIII, `ca/law/I-3.3.txt`): 25 % on a management or administration fee or charge; s. 212 (4): not on a service performed in the ordinary course of the non-resident's business when dealing at arm's length, nor on specific expense reimbursements. As for interest, the payment is taken as non-arm's length: 25 % (flagged).
-/

namespace CaGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon CaGlobal

def isCcpc (co : Company) : Bool := co.flags.contains "ccpc"

def federal (co : Company) : CorpRegime :=
  { name := "Federal corporate income tax",
    sched := if isCcpc co then Schedule.ofList [(0, 900), (500000, 1500)] else Schedule.flat 1500 }

def ontario (co : Company) : CorpRegime :=
  { name := "Ontario corporate income tax",
    sched := if isCcpc co then Schedule.ofList [(0, 320), (500000, 1150)] else Schedule.flat 1150 }

def wht : Wht :=
  { name := "Part XIII tax", rules := [
    { kind := .dividend, rateBp := 2500, statute := "ITA s. 212 (2): 25 %" },
    { kind := .royalty, rateBp := 2500, statute := "ITA s. 212 (1) (d): 25 %" },
    { kind := .interest, rateBp := 2500, statute := "ITA s. 212 (1) (b): 25 % (non-arm's-length interest only)" },
    { kind := .services, rateBp := 2500, statute := "ITA s. 212 (1) (a): 25 % on a management or administration fee or charge (non-arm's-length; s. 212 (4))" }] }

def citF : Family :=
  { name := "1200 federal and Ontario CIT, Part XIII", covers := [.cit, .incomeOther],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      [(federal co).citCharge co "ITA s. 123 (1) (a) 38 %, s. 124 (1) 10 %, s. 123.4 13 %, s. 125 small business 19 %",
       { (ontario co).citCharge co "Taxation Act, 2007 (Ont.): 11.5 %; small business 8.3 % reduction" with level := .state }]
      ++ wht.charges co }

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "Ontario small-business limit taken as $500,000 (link to ITA s. 125 (2) not read); active business income = profit; arm's-length interest to non-residents is exempt (ITA s. 212 (1) (b)): not distinguished"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "services: taken as a management or administration fee to a non-arm's-length recipient (ITA s. 212 (1) (a)); arm's-length services in the ordinary course of business (s. 212 (4)) are not taxed"

#guard (federal {}).citTax { profit := 1000000 } == 150000
#guard (federal { flags := ["ccpc"] }).citTax { profit := 1000000 } == 45000 + 75000
#guard (ontario {}).citTax { profit := 1000000 } == 115000
#guard wht.amount { kind := .dividend, amount := 1000 } == 250
#guard wht.amount { kind := .services, amount := 1000000 } == 250000

end CaGlobal.Corporate
