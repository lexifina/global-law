import TaxKernel.Global
import R5Common

/-!
# Sudan 2025: business profits tax of companies (1200)

The Income Tax Act, 1986, Ministry of Justice English consolidation (amendment footnotes up to Act No 34 of 2015;
`law/sd_income_tax_act_1986_moj_en.txt`, copied from the SSA build's folder), s. 29(1): business profits are taxed at the rates of Schedule III, Sector (A). Schedule III Sector (A)(c):
(1) agricultural companies (animals and plants, poultry, dairy) zero; (2) private and public companies (banks, insurers,
fund-investment and mining companies, and sellers of petrol and gas direct to consumers) 15 % of net income; (3) industrial companies
10 %; (4) oil and gas exploration, production and distribution companies and petroleum service sub-contractors 35 %;
(5) cigarettes and tobacco companies 30 %; (6) communication companies (rate printed "2.5%", Act 25/2013: not computed);
(7) banks 30 % (Act 4/2012, Act 34/2015).
Flags: `agriculture` 0 %, `industrial` 10 %, `oil` 35 %, `tobacco` 30 %, `bank` 30 %, otherwise 15 %.
**Grade B**: the consolidation stops at 2015; the Finance Acts since (2016-2025) were not read.
-/

namespace SdGlobal
open TaxKernel TaxKernel.Global R5Common

def bptRate (co : Company) : Int :=
  let f := fun s => co.flags.contains s
  if f "agriculture" then 0 else if f "oil" then 3500 else if f "tobacco" || f "bank" then 3000
  else if f "industrial" then 1000 else 1500

def bpt (co : Company) : Int := divR .down (pos (co.profit + co.addBacks - co.exemptIncome) * bptRate co) 10000

def corporate : Family :=
  { name := "1200 Business profits tax", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company || g.company.flags.contains "telecom" then [] else
      let co := g.company
      [charge .cit "Business profits tax" (pos (co.profit + co.addBacks - co.exemptIncome)) id (fun _ => bpt co)
        (statute := s!"Income Tax Act 1986 s. 29(1), Schedule III Sector (A)(c) ({bptRate co / 100} %)")] }

def corporateUnsupported (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  corpInputsUnread g true true true true
  ++ (if g.company.flags.contains "telecom" then ["communication companies (Schedule III (A)(c)(6), printed 2.5 %): not computed"] else [])
  ++ ["business profits tax: Finance Acts after 2015 not read (rates as consolidated to Act 34/2015)"]

#guard bpt { profit := 1000000 } == 150000
#guard bpt { profit := 1000000, flags := ["industrial"] } == 100000
#guard bpt { profit := 1000000, flags := ["oil"] } == 350000

end SdGlobal
