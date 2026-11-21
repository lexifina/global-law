import TaxKernel.World

/-!
# Bahrain 2025: no personal income tax; employee social insurance (old-age branch) and unemployment insurance

Sources (Legislation and Legal Opinion Commission, lloc.gov.bh, read 2026-11-20; copies in `bh/law/`):
* Social Insurance Law, Decree-Law No. 24 of 1976, consolidated text "with amendments" (`/FullAr/L2476.docx`,
  `lloc_full_L2476.txt`), and the amending acts' list (`/Legislation/Amendments/L2476`):
  - art. 2: applies compulsorily "على جميع العاملين دون أي تمييز في الجنس، أو الجنسية، أو السن" (private sector
    workers of any nationality); art. 3 exclusions (civil servants under the pension law, etc.);
  - art. 17: contributions on monthly wages, "ويكون الحد الأقصى للأجر الشهري الخاضع للاشتراك (4000 دينار)";
  - art. 33(2) as substituted by Law No. 14 of 2022 (`lloc_K1422.txt`, in force the day after publication):
    "الحصة التي يلتزم بها المؤمن عليه وتقع على عاتقه بواقع (7%) من أجره شهرياً" (old-age, disability and death).
  - The 2026 amendments (Decree-Law No. 44 of 2026: a minimum contribution wage for persons first registered after
    it; Law No. 19 of 2026: art. 144) do not touch art. 17 or art. 33, so the consolidated wording is the 2025 one.
* Unemployment Insurance, Decree-Law No. 78 of 2006, consolidated (`/FullAr/L7806.docx`): art. 2 covers private
  sector workers insured for employment injury under the Social Insurance Law (art. 2 of that law: any
  nationality) and civil servants; art. 6(1) "1% من الأجر يدفعها المؤمن عليه شهرياً"; art. 1(17) the wage is the
  wage on which social insurance contributions are computed (so the 4,000 ceiling applies).
* No personal income tax: no Bahraini act levies a tax on individuals' income (the LLOC classification "التشريعات
  المالية والاقتصادية" holds no income tax act for individuals; not established from a text that says so: see
  FINDINGS F1).

Scope of the old-age branch for non-Bahrainis: art. 1 applies the branches "على مراحل" by Council of Ministers
decisions, which were not read; expatriates are therefore modelled with the unemployment contribution only and the
old-age branch flagged `unsupported`. Default `"nationality": "national"` (a Bahraini private-sector employee).
Amounts in whole dinars (the statute's fils are not modelled).
-/

namespace BhTax
open TaxKernel

def pct (rate base : Int) : Int := divR .down (rate * pos base) 10000
def nationality (c : Canon) : String := (c.str? "nationality").getD "national"

/-- art. 17: 4,000 dinars a month. -/
def ceiling : Int := 4000 * 12
/-- art. 33(2) (Law 14/2022): 7 %. -/
def oldAgeRate : Int := 700
/-- DL 78/2006 art. 6(1): 1 %. -/
def unemploymentRate : Int := 100

def oldAge : Contribution := Contribution.flatCapped "oldAge" oldAgeRate ceiling
def unemployment : Contribution := Contribution.flatCapped "unemployment" unemploymentRate ceiling

def out (c : Canon) : Out :=
  let nat := nationality c
  let oa := if nat = "national" then sumInts (c.adults.map fun a => oldAge.amount a.wages) else 0
  let un := sumInts (c.adults.map fun a => unemployment.amount a.wages)
  let uns :=
    (if nat ≠ "national" ∧ c.adults.any (fun a => a.wages > 0) then
      ["old-age branch for non-Bahraini workers: phased application (DL 24/1976 art. 1) by decisions not read; only the 1 % unemployment contribution is modelled"] else [])
    ++ (if nat = "gcc" then ["GCC national: pension contributions follow the home state's law (GCC unified insurance extension), not modelled"] else [])
  Out.make c "BH" "BHD" 0 (employeeSocial := oa + un)
    (detail := [Out.d "oldAgeContribution" oa, Out.d "unemploymentContribution" un, Out.dStr "nationality" nat,
      Out.dStr "note" "no personal income tax (no act levies one); DL 24/1976 art. 17, 33 (Law 14/2022); DL 78/2006 art. 6"])
    (unsupported := uns)

def country : Country :=
  { code := "BH", name := "Bahrain (private-sector employee)", currency := "BHD", year := "2025", compute := out }

end BhTax
