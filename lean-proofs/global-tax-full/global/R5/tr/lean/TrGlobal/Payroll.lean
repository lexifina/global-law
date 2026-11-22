import TaxKernel.Global
import R5Common

/-! # Türkiye 2025: work-permit fee (çalışma izni harcı) per foreign worker (OECD 3000)

* Harçlar Kanunu 492, tariff (6) part IV (added by Law 4817 art. 34, in force 6/9/2003; as changed by Law 6735 art. 27,
  in force 13/8/2016): 1. fixed-term work permit and work-permit exemption certificate, up to one year (one year
  included); "extensions are charged the same amount for each year". Amount for 2025: **TL 10.571,60**, Harçlar Kanunu
  Genel Tebliği (Seri No: 96), Resmî Gazete 32768 (2. mükerrer) of 30/12/2024, annex (tariff 6, IV-1; the 2024 amounts
  raised by the revaluation rate 43,93 %, art. 3), in force 1/1/2025 (art. 4) and until the next revaluation on
  1/1/2026 (`law/tr_rg_20241230M2-10_harc_seri96.htm`, annex PDF `law/tr_rg_20241230M2-10-1_harc_seri96_ek.pdf`, page 6
  read on the image). Indefinite and independent work permits (TL 105.760,60 once) are not per-worker yearly charges.
* International Labour Force Law 6735 art. 10(1)-(2) (text from the team's git history of mevzuat.gov.tr,
  lexifina/turkey-law, act 6735): the permit is for work at a given employer's workplace, at most one year at first,
  then up to two and three years; art. 22: employers of foreigners report and pay social security.
Classification: a fixed amount for each foreign worker employed and for each year of the permit (Guide §47: "a fixed
amount per person employed"); pass 3l coordinator decision: a per-worker fee levied by law belongs to 3000.
Model (company line with `company.expatWorkers`): TL 10.571,60 per foreign worker for the year, rounded to the lira.
The payer is read as the employer, who applies for the permit of the worker it employs (the application rules of the
implementing regulation are not read). Grade A (tariff and Tebliğ text read).
-/

namespace TrGlobal
open TaxKernel TaxKernel.Global R5Common

/-- an optional integer field of the company object (-1 when absent) -/
def trCoInt (g : CanonGlobal) (k : String) : Int :=
  match g.raw.getObjVal? "company" with
  | .ok cj => intField cj k (-1)
  | _ => -1

/-- tariff (6) IV-1, 2025 (Seri No: 96), in kuruş -/
def permitKurus : Int := 1057160

def permitFee (n : Int) : Int := (n * permitKurus + 50) / 100

def payroll : Family :=
  { name := "3000 çalışma izni harcı", covers := [.payroll],
    run := fun _ g _ =>
      if g.entity == .company && 0 ≤ trCoInt g "expatWorkers" then
        [charge .payroll "çalışma izni harcı (yabancı çalışan başına, yıllık)" (trCoInt g "expatWorkers") pos permitFee
          (statute := "Harçlar Kanunu 492 tariff (6) IV-1 (Law 6735 art. 27), TL 10.571,60 a year per foreign worker for 2025 (Harçlar Kanunu Genel Tebliği Seri No: 96, RG 30/12/2024); Law 6735 art. 10")]
      else [] }

def payrollUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company && trCoInt g "expatWorkers" < 0 then
    ["3000 work-permit fee (TL 10.571,60 a year per foreign worker): company.expatWorkers not given (grade C); no payroll tax in the laws read (KVK 5520, 5510, KDV 3065)"]
  else []

#guard permitFee 1 == 10572
#guard permitFee 10 == 105716

end TrGlobal
