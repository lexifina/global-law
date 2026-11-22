import TaxKernel.Global
import R5Common

/-!
# Bahrain 2025: employer social insurance contributions (2200)

LLOC consolidated texts (`law/`):
* Social Insurance Law, DL 24/1976: art. 17 maximum contribution wage "(4000 دينار)" a month; art. 33(1) as
  substituted by Law 14/2022: employer share for old age, disability and death "(17%)"; Law 14/2022 art. 4
  (transitional): "(11%) … عند نفاذ أحكام هذا القانون، وتزاد سنوياً بمعدل (1%) حتى تصل للحصة المحددة" (in force
  April 2022; the yearly steps fall on 1 January: 12 % 2023, 13 % 2024, 14 % 2025, as the SIO's January 2025
  circular reported a total employer rate of 17 %); art. 47(1) employment injury "3 بالمائة", employer alone, all
  nationalities (art. 2).
* Unemployment insurance, DL 78/2006 art. 6(2): employer 1 %, but "يتحمل صندوق العمل سداد حصة أصحاب العمل عن
  المؤمن عليهم العاملين في القطاع الأهلي": borne by the Labour Fund, not charged.
Bahraini (default `nationality` "national"): 14 % + 3 % = 17 %; others: 3 % (old-age branch for expatriates not
applied, as in the 1.x model).
-/

namespace BhGlobal
open TaxKernel TaxKernel.Global R5Common

def nationalityBh (g : CanonGlobal) : String := (g.str? "nationality").getD ((g.household.str? "nationality").getD "national")

def bhCap : Int := 4000 * 12

/-- Law 14/2022 art. 4: 11 % on entry into force (2022), +1 % on 1 January of each later year, up to 17 %. -/
def oldAgeEmployer (year : Nat) : Int := min 1700 (1100 + 100 * ((year : Int) - 2022))

def social : Family :=
  { name := "2200 SIO employer contributions", covers := [.sscEmployer],
    run := fun _ g _ =>
      (if nationalityBh g == "national" then
        employerOn "اشتراك تأمين الشيخوخة والعجز والوفاة (صاحب العمل)"
          "DL 24/1976 art. 33(1) (Law 14/2022) with Law 14/2022 art. 4: 14 % in 2025; art. 17 ceiling BHD 4,000 a month" (oldAgeEmployer 2025) bhCap g
      else [])
      ++ employerOn "اشتراك تأمين إصابات العمل" "DL 24/1976 art. 47(1): 3 % (employer alone); art. 17 ceiling" 300 bhCap g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer: unemployment 1 % (DL 78/2006 art. 6(2)) borne by the Labour Fund, not charged; art. 48 injury-rate reductions and art. 49 increases not applied; expatriates' old-age branch not applied"]

#guard oldAgeEmployer 2022 == 1100 && oldAgeEmployer 2025 == 1400 && oldAgeEmployer 2030 == 1700
#guard bhCap == 48000

end BhGlobal
