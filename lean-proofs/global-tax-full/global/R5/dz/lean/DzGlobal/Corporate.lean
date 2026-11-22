import TaxKernel.Global
import R5Common

/-!
# Algeria 2025: impôt sur les bénéfices des sociétés (1200)

Code des impôts directs et taxes assimilées, art. 150-1, DGI 2025 Arabic edition (mfdgi.gov.dz dropfiles category 776,
file 2523, Wayback 2025-02-22, `law/dgi_cidta_2025_ar.pdf`, p. 46 read on the page image; the edition already carries
LF 2025 amendments, e.g. art. 149 bis by LF 2025 art. 12) and the 2023 French edition (`law/dgi_cidta_2023_fr.pdf`,
art. 150): "يحدد معدل الضريبة على أرباح الشركات كما يأتي: 19% بالنسبة لأنشطة إنتاج السلع؛ 23% بالنسبة لأنشطة البناء
والأشغال العمومية والري، وكذا الأنشطة السياحية والحمامات، باستثناء وكالات الأسفار؛ 26% بالنسبة للأنشطة الأخرى".
Footnote: last amended by LF 2022 art. 46. Mixed activities are split by turnover share (not computed: one rate).
Flags: `production` (19 %; extraction, manufacture, processing, not packaging for resale, not mining/hydrocarbons),
`construction` or `tourism` (23 %); otherwise 26 %. **Grade A**. Not computed: losses (art. 147), reinvested-profit
relief, art. 150 bis tobacco surtax, withholding on non-residents.
-/

namespace DzGlobal
open TaxKernel TaxKernel.Global R5Common

def ibsRate (co : Company) : Int :=
  if co.flags.contains "production" then 1900
  else if co.flags.contains "construction" || co.flags.contains "tourism" then 2300 else 2600

def ibsBase (co : Company) : Int := pos (co.profit + co.addBacks - co.exemptIncome)

def ibs (co : Company) : Int := divR .down (ibsBase co * ibsRate co) 10000

/-- Withholding on payments to non-residents (CIDTA 2025 Arabic edition pp. 31-32 and 47, page images checked; French
2023 edition identical): companies without a permanent establishment art. 150-2, 156; individuals domiciled abroad
art. 33, 104-II-4 and 104-III. -/
def dzWht : Wht :=
  { name := "الاقتطاع من المصدر (غير المقيمين)",
    rules := [{ kind := .dividend, toCompany := some true, rateBp := 1500, statute := "CIDTA art. 150-2 (15 %, final)" },
              { kind := .interest, toCompany := some true, rateBp := 1000, statute := "CIDTA art. 150-2, 155 (10 %)" },
              { kind := .royalty, toCompany := some true, rateBp := 3000, statute := "CIDTA art. 150-2, 156-1 (30 %)" },
              { kind := .services, toCompany := some true, rateBp := 3000, statute := "CIDTA art. 150-2, 156-1 services of any kind (30 %)" },
              { kind := .dividend, toCompany := some false, rateBp := 1500, statute := "CIDTA art. 104-III (15 %)" },
              { kind := .interest, toCompany := some false, rateBp := 1000, statute := "CIDTA art. 104-II-4-b (10 %)" },
              { kind := .royalty, toCompany := some false, rateBp := 2400, statute := "CIDTA art. 33-2°, 104-III (24 %)" },
              { kind := .services, toCompany := some false, rateBp := 2400, statute := "CIDTA art. 33-1°/3°, 104-III (24 %)" }] }

def corporate : Family :=
  { name := "1200 الضريبة على أرباح الشركات", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      [charge .cit "الضريبة على أرباح الشركات (IBS)" (ibsBase co) id (fun _ => ibs co)
        (statute := s!"CIDTA art. 150-1 ({ibsRate co / 100} %)")] ++ dzWht.charges co }

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true true true true
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && p.toCompany) then ["withholding: management contracts (20 %, art. 150-2) not distinguished from other services (30 %)"] else [])
  ++ (if g.entity == .company then ["IBS: one rate from the company flags (production / construction / tourism); mixed activities are split by turnover share (art. 150-1)"] else [])

#guard ibs { profit := 1000000 } == 260000
#guard dzWht.amount { kind := .services, amount := 100000 } == 30000
#guard dzWht.amount { kind := .services, amount := 100000, toCompany := false } == 24000
#guard ibs { profit := 1000000, flags := ["production"] } == 190000
#guard ibs { profit := 1000000, flags := ["tourism"] } == 230000

end DzGlobal
