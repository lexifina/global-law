import TaxKernel.Global
import R5Common

/-!
# Lebanon 2025: employer contributions to the National Social Security Fund (2200)

Social Security Code (Decree 13955 of 26/09/1963; NSSF edition `law/nssf_ssc_2012ed.pdf`): art. 71 rates "بمرسوم";
art. 73(1) family allowances and end-of-service on the employer alone; art. 73(2) sickness/maternity shared;
art. 68(2) ceilings by decree; art. 68(3) no ceiling for end-of-service. Rate decrees (Lebanese University
legiliban.ul.edu.lb text, `law/legiliban_*.html`):
* Decree 5101 of 24/03/2001 art. 2: sickness and maternity "بنسبة 9% ... 7% (سبعة بالمئة) على عاتق صاحب العمل.
  2% ... على عاتق المضمون" (the NSSF drivers' tables of memos 754 and 801 still apply 9 % in 2024-2025);
* Decree 5102 of 24/03/2001 art. 2: family and educational allowances "بنسبة 6% (ستة بالمائة)", employer;
* Decree 2951 of 20/10/1965 art. 1: end-of-service "بثمانية ونصف بالماية (8،5%)" (art. 2: 8 % for some
  establishments, not applied). Law 319/2023 (pension system) art. 12 keeps the end-of-service branch in force until
  its decrees are adopted (none in 2025: memo 795 of 4/7/2025 still amends the end-of-service regulation).
Monthly ceilings in 2025:
* sickness/maternity: 5 x the minimum monthly wage (Decree 12962 of 12/02/2024) = LBP 90,000,000 from 1/4/2024 (memo
  754: minimum wage 18 m, Decree 13164/2024), LBP 120,000,000 from 1/8/2025 (Decree 887 of 14/08/2025, memo 805;
  memo 801's 140 m withdrawn by memo 805 art. 2);
* family allowances: LBP 12,000,000 from 1/1/2024 (Decree 12772 of 20/12/2023, memo 734), LBP 18,000,000 from 1/7/2025
  (Decree 422 of 10/06/2025, memo 793).
Yearly caps for an even monthly wage: sickness 7 x 90 m + 5 x 120 m = 1,230 m; family 6 x 12 m + 6 x 18 m = 180 m.
-/

namespace LbGlobal
open TaxKernel TaxKernel.Global R5Common

def sickCap : Int := 7 * 90000000 + 5 * 120000000
def famCap : Int := 6 * 12000000 + 6 * 18000000

def social : Family :=
  { name := "2200 NSSF employer contributions", covers := [.sscEmployer],
    run := fun _ g _ =>
      employerOn "اشتراك ضمان المرض والأمومة (صاحب العمل)"
        "Decree 5101/2001 art. 2: 7 %; ceilings Decree 12962/2024 (LBP 90 m a month) and Decree 887/2025 (120 m from 1/8/2025)" 700 sickCap g
      ++ employerOn "اشتراك التقديمات العائلية والتعليمية"
        "Decree 5102/2001 art. 2: 6 %; ceilings Decree 12772/2023 (LBP 12 m a month) and Decree 422/2025 (18 m from 1/7/2025)" 600 famCap g
      ++ employerOn "اشتراك تعويض نهاية الخدمة"
        "Decree 2951/1965 art. 1: 8.5 %; no ceiling (SSC art. 68(3)); Law 319/2023 art. 12" 850 (-1) g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["NSSF employer: monthly ceilings applied as yearly caps for an even monthly wage; work-injury branch not in force; Decree 2951/1965 art. 2 reduced 8 % end-of-service rate and art. 72 flat-rate categories not applied; the employee's 2 % is not an employer charge"]

#guard sickCap == 1230000000
#guard famCap == 180000000
#guard divR .down (700 * sickCap) BP + divR .down (600 * famCap) BP == 86100000 + 10800000

end LbGlobal
