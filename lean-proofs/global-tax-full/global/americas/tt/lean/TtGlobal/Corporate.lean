import TtGlobal.Pit

/-!
# Trinidad and Tobago 2025: corporation tax (1200)

Source: Board of Inland Revenue page "Corporations" (ird.gov.tt, `tt/law/ird_corporations.txt`, fetched 2026-11-21; facts paraphrased): 25 % to the end of 2016; for 2017,
25 % on the first $1,000,000 and 30 % on the excess; 30 % from income year 2018; 35 % for petrochemical companies. The official consolidation of Chap. 75:02 (`tt/law/cta_75.02.txt`)
is updated only to 31 Dec 2016 (25 %), so the rate is taken from the IRD page: grade B.
Withholding: Income Tax Act Chap. 75:01, Third Schedule Part II (ss. 48, 50; RGD PDF updated to 31 Dec 2016, and the
laws.gov.tt consolidation in force 2025-06-03 held by the 1.x builder): 15 % on payments to a company or other person
(interest, royalties, fees): both texts agree, grade A. Distributions: the 2016 PDF reads 10 % (5 % to a parent
company), the 2025 consolidation 8 % (3 %): the texts disagree and the amending Act was not read: not modelled.
Business levy (0.6 % of gross sales, a minimum against corporation tax) and Green Fund Levy (0.3 % of gross sales) are
on the same IRD page: not modelled.

**Pass 7 (2026-11-21):** distributions to non-residents: the laws.gov.tt Recent Update of Chap. 75:01 (PDF of 3 June 2025; world/B13-caribbean/tt/law/ita_75-01_2025-06-03.txt) Third Sched. Part II (i): 8 %, 3 % to a parent company (the 2016 RGD text read 10 %/5 %; the amending Act was not identified: grade B). "Parent company" is not defined in the Act: the 3 % is not modelled.
-/

namespace TtGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon TtGlobal

def regime : CorpRegime :=
  { name := "Corporation tax", sched := Schedule.flat 3000 }

def citStatute : String := "Corporation Tax Act Chap. 75:02 s. 3 as amended (Finance Act 2017); IRD 'Corporations': 30 % from income year 2018"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 1500, statute := "ITA Chap. 75:01 Third Sched. Part II (iii) (15 %)" }, { kind := .royalty, rateBp := 1500, statute := "ITA Chap. 75:01 Third Sched. Part II (iii) (15 %)" }, { kind := .services, rateBp := 1500, statute := "ITA Chap. 75:01 Third Sched. Part II (iii) (15 %)" }, { kind := .dividend, rateBp := 800, statute := "ITA Chap. 75:01 s. 50 (1) (a), Third Sched. Part II (i) (laws.gov.tt Recent Update, in force by 2025-06-03): distributions 8 %" }] }

def citF : Family := corpFamily "1200 Corporation tax" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "business levy 0.6 % of gross sales (minimum against corporation tax), Green Fund Levy 0.3 %, petrochemical 35 % and the 35 % rate for banks not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "distributions to a parent company (3 %, ITA Third Sched. Part II (i)) not modelled: 8 % applied"

#guard regime.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 150000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 80000

end TtGlobal.Corporate
