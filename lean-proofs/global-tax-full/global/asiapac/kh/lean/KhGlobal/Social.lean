import KhGlobal.Pit

/-!
# Cambodia 2025: employer contributions to the National Social Security Fund (2200)
Secondary-source sweep, grade B (two guides agree; the Law on Social Security Schemes and the NSSF Prakas not read):
PwC Worldwide Tax Summaries, Cambodia, Individual - Other taxes, last reviewed 8 September 2025 (Wayback capture 2025-12-15, asiapac/kh/law/pwc_kh_indother_wb20251215.txt); Deloitte Cambodia Highlights 2025 (updated August 2025), 'Social security contributions' (asiapac/kh/law/deloitte_kh_2025.txt).
* Occupational risks 0.8 % of the average monthly wage (employer only).
* Health care 2.6 % (the employer has borne the whole 1.3 % + 1.3 % since 1 January 2018).
* Old-age pension, first five-year stage from October 2022 (so all of 2025): 4 % of the contributory wage, 2 % from the employer.
* Ceiling: Deloitte gives a contributory wage cap of KHR 1.2 million a month for the pension and gives monthly maxima of
  USD 7.80 (health) and USD 2.40 (occupational risks) for the other two, i.e. the same base of about USD 300: modelled as one base of KHR 1,200,000 a month
  (KHR 14,400,000 a year) for all three parts.
Not modelled: the pension's minimum contributory wage (KHR 400,000 a month), the size threshold of the occupational-risk
registration (eight employees, PwC), public-sector employees (separate guidance).
-/

namespace KhGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "NSSF occupational risks (employer 0.8 %)" a.wages (fun w => min (pos w) 14400000) (fun b => divR .down (80 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "NSSF occupational risk scheme (not read); PwC Worldwide Tax Summaries, Cambodia, Individual - Other taxes, last reviewed 8 September 2025 (Wayback capture 2025-12-15, asiapac/kh/law/pwc_kh_indother_wb20251215.txt); Deloitte Cambodia Highlights 2025 (updated August 2025), 'Social security contributions' (asiapac/kh/law/deloitte_kh_2025.txt)"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "NSSF health care (employer 2.6 %)" a.wages (fun w => min (pos w) 14400000) (fun b => divR .down (260 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "NSSF health care scheme (not read); PwC Worldwide Tax Summaries, Cambodia, Individual - Other taxes, last reviewed 8 September 2025 (Wayback capture 2025-12-15, asiapac/kh/law/pwc_kh_indother_wb20251215.txt); Deloitte Cambodia Highlights 2025 (updated August 2025), 'Social security contributions' (asiapac/kh/law/deloitte_kh_2025.txt)"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "NSSF old-age pension (employer 2 %, first stage)" a.wages (fun w => min (pos w) 14400000) (fun b => divR .down (200 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Law on Social Security Schemes 2019 and the pension Prakas (not read); PwC Worldwide Tax Summaries, Cambodia, Individual - Other taxes, last reviewed 8 September 2025 (Wayback capture 2025-12-15, asiapac/kh/law/pwc_kh_indother_wb20251215.txt); Deloitte Cambodia Highlights 2025 (updated August 2025), 'Social security contributions' (asiapac/kh/law/deloitte_kh_2025.txt)")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => a.wages > 0 && a.wages < 4800000) then ["2200 Cambodia NSSF pension: a monthly wage below the KHR 400,000 minimum contributory wage is charged on the actual wage (the minimum is not applied)"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ age := 40, wages := 12000000 }] } } []).map (·.due) == [96000, 312000, 240000]
#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ age := 40, wages := 30000000 }] } } []).map (·.due) == [115200, 374400, 288000]

end KhGlobal.Social
