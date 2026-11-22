import CnGlobal.Pit

/-!
# China 2025: enterprise income tax and withholding on non-resident enterprises (1200)

Sources: flk.npc.gov.cn official docx (`cn/law/flk/cit_law_2018.*`, `cit_regs_2024.*`).
* **企业所得税法 (2018-12-29) art. 4**: "企业所得税的税率为25％"; non-resident enterprises' art. 3 (3) income 20 %.
* **art. 28**: small low-profit enterprises 20 %, high and new technology enterprises 15 % (`hnte`).
* **art. 26 (2)**: dividends between resident enterprises exempt (participation, any stake).
* **实施条例 (2024-12-06 version, in force 2025-01-20) art. 91**: art. 27 (5) income of non-resident enterprises "减按10%的税率".

FT review (2026-11-21): **财政部 税务总局公告2023年第12号** (2023-08-02; gov.cn 国务院部门文件,
`cn/law/mof/mof_sat_2023_12.html`, sha256 in `SOURCES.tsv`):
* **三**: "对小型微利企业减按25%计算应纳税所得额，按20%的税率缴纳企业所得税政策，延续执行至2027年12月31日" (2025: 5 % of
  the taxable income).
* **五**: "小型微利企业，是指从事国家非限制和禁止行业，且同时符合年度应纳税所得额不超过300万元、从业人数不超过300人、资产总额
  不超过5000万元等三个条件的企业" (replacing, for the notice, 实施条例 art. 92's 30万元 / 100 or 80 / 3000 or 1000万元).
The test is applied to the entity's own taxable profit, employees and assets (the quarterly averages taken as the
entity's values); flag `restrictedIndustry` excludes it, flag `smallLowProfit` forces it. A company that is both a high
and new technology enterprise (15 %) and a small low-profit enterprise pays the lower.
-/

namespace CnGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- The regime before the rate (taxable profit only; same fields as `cit`). -/
def base : CorpRegime := { name := "企业所得税 (enterprise income tax)", sched := Schedule.flat 2500, participationBp := 10000 }
/-- 公告2023年第12号 五: 年度应纳税所得额 ≤ 300万元, 从业人数 ≤ 300人, 资产总额 ≤ 5000万元, non-restricted industry. -/
def smallLowProfit (co : Company) : Bool :=
  co.flags.contains "smallLowProfit" ||
  (!co.flags.contains "restrictedIndustry" && decide (base.taxableProfit co ≤ 3000000) && decide (co.employees ≤ 300)
    && decide (co.assets ≤ 50000000))
/-- art. 4 25 %; art. 28 (2) high and new technology enterprise 15 %; 公告2023年第12号 三: 25 % of the income at 20 % = 5 %. -/
def rateOf (co : Company) : Int := if smallLowProfit co then 500 else if co.flags.contains "hnte" then 1500 else 2500

def cit (co : Company) : CorpRegime :=
  { name := "企业所得税 (enterprise income tax)",
    sched := Schedule.flat (rateOf co),
    participationBp := 10000 }

def citStatute : String := "企业所得税法 (2018) art. 4, art. 28; 财政部 税务总局公告2023年第12号 三, 五 (small low-profit enterprises, to 2027-12-31)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, toCompany := some false, rateBp := 2000, statute := "个人所得税法 art. 3 (3) (20 %); 实施条例 art. 3 (5) (China-source)" },
      { kind := .interest, toCompany := some false, rateBp := 2000, statute := "个人所得税法 art. 3 (3) (20 %); 实施条例 art. 3 (5)" },
      { kind := .services, toCompany := some false, rateBp := 0, statute := "个人所得税法实施条例 art. 3 (1): services performed outside China are not China-source" },
      { kind := .services, rateBp := 0, statute := "企业所得税法实施条例 art. 7 (2): services income is sourced where the services are performed; 企业所得税法 art. 3: a non-resident enterprise is taxed on China-source income only" },
      { kind := .dividend, toCompany := some true, rateBp := 1000, statute := "企业所得税法 3 (3), 27 (5); 实施条例 91" },
      { kind := .interest, toCompany := some true, rateBp := 1000, statute := "实施条例 91" },
      { kind := .royalty, toCompany := some true, rateBp := 1000, statute := "实施条例 91" }] }


/-- Non-resident individuals' royalties (个人所得税法 2018 art. 2 (1) 4, art. 6 (1) 2: 每次收入额; art. 6 para. 2: 收入额 =
收入 less 20 %; 附表一 注2: the 综合所得 table of art. 3 converted to a month: 3 000 / 12 000 / 25 000 / 35 000 / 55 000 /
80 000 yuan; art. 11 para. 3: withheld by the payer, no annual settlement). -/
def nrMonthly : Schedule := Schedule.ofList [(0, 300), (3000, 1000), (12000, 2000), (25000, 2500), (35000, 3000), (55000, 3500), (80000, 4500)]

def royaltyIndTax (amt : Int) : Int := nrMonthly.tax {} (pos amt * 8 / 10)

def royaltyIndCharges (co : Company) : List Charge :=
  co.paymentsAbroad.zipIdx.filterMap fun (p, i) =>
    if p.kind == .royalty && !p.toCompany then
      some (charge .pit "个人所得税 (非居民个人 特许权使用费所得)" p.amount (fun a => pos a * 8 / 10) (fun b => nrMonthly.tax {} b)
        (event := s!"payment {i + 1} ({p.kind.name})") (bearer := .withheld)
        (statute := "个人所得税法 (2018) art. 3, art. 6 (1) 2 and para. 2 (收入额 80 %), art. 11 para. 3; 附表一 注2 (按月换算)"))
    else none


def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [(cit g.company).citCharge g.company citStatute]
       ++ wht.charges g.company
       ++ royaltyIndCharges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["the art. 30 super deductions not modelled; small low-profit test on the entity's own year-end employees and assets (not the quarterly averages of 公告2023年第12号 五), industry taken as non-restricted unless flagged `restrictedIndustry`"] else [])

#guard (cit { profit := 1000000, employees := 301 }).citTax { profit := 1000000, employees := 301 } == 250000
#guard (cit { profit := 1000000, employees := 301, flags := ["hnte"] }).citTax { profit := 1000000, employees := 301, flags := ["hnte"] } == 150000
#guard wht.amount { kind := .dividend, amount := 1000, toCompany := true } == 100
#guard wht.amount { kind := .interest, amount := 1000, toCompany := true } == 100
#guard wht.amount { kind := .royalty, amount := 1000, toCompany := true } == 100
-- 公告2023年第12号 三, 五: 5 % up to 3,000,000 of taxable income, 300 employees, 50,000,000 of assets
#guard (cit { profit := 3000000, employees := 300, assets := 50000000 }).citTax { profit := 3000000, employees := 300, assets := 50000000 } == 150000
#guard (cit { profit := 3000001, employees := 300, assets := 50000000 }).citTax { profit := 3000001, employees := 300, assets := 50000000 } == 750000
#guard (cit { profit := 1000000, employees := 300, assets := 50000001 }).citTax { profit := 1000000, employees := 300, assets := 50000001 } == 250000
#guard (cit { profit := 1000000, flags := ["restrictedIndustry"] }).citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000, toCompany := false } == 200
#guard wht.amount { kind := .services, amount := 1000 } == 0
#guard royaltyIndTax 10000 == 590
#guard royaltyIndTax 0 == 0
#guard royaltyIndTax 200000 == 56840

end CnGlobal.Corporate
