import TaxKernel.Global
import R5Common

/-!
# Saudi Arabia 2025: employer social insurance contributions (2200) (pass 3r: re-cited to the 2024 law)

Two laws apply in 2025, by the worker's history (Royal Decree M/273 of 26/12/1445H, approving the **Social Insurance
Law 1445H**; text as published by GOSI, `cmsapi.gosi.gov.sa ... siteUrl=newSystem` captured by Wayback on 24/10/2025,
`law/sa_gosi_si1445_2025.txt`; the law is "يعمل به من اليوم التالي لتاريخ صدوره": in force 3/7/2024):
* **Existing contributors** (decree item ثانياً(1): "المشتركون الذين لديهم مدد اشتراك سابقة على نفاذ النظام لم يعوضوا
  عنها") stay under the **Social Insurance Law 1421H (M/33)** and the Unemployment Insurance Law (M/18, 1435H)
  (item رابعاً). Law 1421H read in the laws.boe.gov.sa capture of 07/08/2025 (status "ساري", no amendment of art. 18-19;
  `law/sa_boe_si1421_2025.txt`): art. 18(1) occupational hazards 2 % on the employer (every worker); art. 18(2)(a)
  annuities 18 %, employer 9 % (Saudi workers); art. 19(1)(b) ceiling SAR 45,000 a month.
* **New entrants** (first insured from 3/7/2024; input `"gosiScheme": "1445"`, top level or household): Law 1445H
  art. 15(1) sets the annuities branch at 22 % (11 % employer), phased in by decree item ثالثاً(1): 18 % "خلال الإثني عشر
  شهراً من تاريخ نفاذ النظام", 19 % "من الشهر التالي لانقضاء إثني عشر شهراً", employer 50 % (item ثالثاً(2)). The twelve
  contribution months are July 2024 - June 2025 (contributions are monthly and July 2024 is the first month of the law),
  so 2025 is split: **January-June 9 %, July-December 9,5 %** (employer), each on half the year's wages. Art. 29(1)
  occupational hazards 2 % on the employer (every worker); art. 8(2) ceiling SAR 45,000 a month; unemployment branch
  (art. 43-44) set at **1,5 %, half on the employer (0,75 %)** "في تاريخ نفاذ النظام" by Council of Ministers decision
  1022 of 26/12/1445H item ثالثاً(6) (same GOSI page).
* **Unemployment (SANED) of existing contributors**: M/18 sets the rate by decision (not read); GOSI's SANED guide as
  served on 16/07/2025 (`GOSIOnline/SANED`, Wayback; `law/sa_gosi_saned_guide_2025.pdf`, page 4) gives 0,75 % for the
  employer and 0,75 % for the worker: applied, **grade B** for this part (the entry is graded B).
Saudi workers only for annuities and SANED (the household's `nationality`: `national` default, `expatriate`, `gcc`).
The 45,000 ceiling is applied to SANED too (art. 8(2) of the 1445H law covers every branch; the M/18 ceiling not read).
-/

namespace SaGlobal
open TaxKernel TaxKernel.Global R5Common

def nationalitySa (g : CanonGlobal) : String := (g.str? "nationality").getD ((g.household.str? "nationality").getD "national")

/-- "1421" (default: an existing contributor, decree M/273 item 2(1)) or "1445" (first insured from 3/7/2024) -/
def gosiScheme (g : CanonGlobal) : String := (g.str? "gosiScheme").getD ((g.household.str? "gosiScheme").getD "1421")

def gosiCap : Int := 45000 * 12

/-- employer charge on `num/den` of each earner's capped yearly wages -/
def employerPart (name statute : String) (rateBp num den : Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
    charge .sscEmployer name a.wages (fun w => divR .down (min (pos w) gosiCap * num) den) (fun b => divR .down (rateBp * b) BP)
      (event := s!"adult {i + 1}") (level := .social) (bearer := .employer) (statute := statute)

def sanedStatute1445 : String :=
  "Council of Ministers decision 1022 (26/12/1445H) item 3(6): unemployment branch 1.5 %, employer half (0.75 %); Law 1445H art. 8(2) ceiling"

def social : Family :=
  { name := "2200 GOSI employer contributions", covers := [.sscEmployer],
    run := fun _ g _ =>
      let nat := nationalitySa g
      if nat == "gcc" then [] else
      if gosiScheme g == "1445" then
        employerPart "GOSI occupational hazards (employer, Law 1445H)" "Social Insurance Law 1445H art. 29(1) (2 %), 8(2) (SAR 45,000 a month)" 200 1 1 g
        ++ (if nat == "national" then
          employerPart "GOSI annuities Jan-Jun 2025 (employer, Law 1445H)" "Royal Decree M/273 item 3(1)(a), 3(2): 18 % for the first twelve months, employer half (9 %)" 900 1 2 g
          ++ employerPart "GOSI annuities Jul-Dec 2025 (employer, Law 1445H)" "Royal Decree M/273 item 3(1)(b), 3(2): 19 % from the month after twelve months, employer half (9.5 %)" 950 1 2 g
          ++ employerPart "SANED unemployment insurance (employer, Law 1445H)" sanedStatute1445 75 1 1 g
          else [])
      else if nat == "national" then
        employerOn "GOSI annuities + occupational hazards (employer, Law 1421H)" "Social Insurance Law 1421H art. 18(1) (2 %), 18(2)(a) (9 %), 19(1)(b) (SAR 45,000 a month); Royal Decree M/273 items 2(1), 4" 1100 gosiCap g
        ++ employerPart "SANED unemployment insurance (employer)" "Unemployment Insurance Law M/18 (1435H); GOSI SANED guide served 2025: employer 0.75 % (grade B)" 75 1 1 g
      else
        employerOn "GOSI occupational hazards (employer, Law 1421H)" "Social Insurance Law 1421H art. 18(1) (2 %), 19(1)(b)" 200 gosiCap g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  (if (g.str? "gosiScheme").isNone && (g.household.str? "gosiScheme").isNone then
    ["GOSI: every worker taken as an existing contributor (Law 1421H); a worker first insured from 3/7/2024 needs gosiScheme \"1445\" (annuities 9 % / 9.5 % in 2025)"] else [])
  ++ ["wage base = basic wage + housing per the Regulations: wages used"]
  ++ (if nationalitySa g == "gcc" then ["GCC national: home state's scheme (unified GCC insurance protection; not modelled)"] else [])

#guard gosiCap == 540000
#guard divR .down (min (pos 600000) gosiCap * 1) 2 == 270000

end SaGlobal
