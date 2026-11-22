import TaxKernel.Global

/-! # Lb: taxes on payroll and workforce (OECD 3000), grade C (pass 3l)

3000 taxes on payroll and workforce: work-permit fees for foreign workers (Ministry of Labour; amounts by decree and budget laws, not read); no payroll tax in the laws read (DL 144/1959, Social Security Code). Coordinator decision of pass 3l: OECD 3000 covers taxes paid by employers as a fixed amount per person employed, so a per-worker fee levied by law on employers belongs here and the heading is not cited absent until the fee text is read; a one-off permit issuance charge that does not scale with the workforce is not a tax (note only). No company input carries the workforce by nationality. Grade C (pass 3l).
-/

namespace LbGlobal
open TaxKernel TaxKernel.Global

def payrollNote : String := "3000 taxes on payroll and workforce: work-permit fees for foreign workers (Ministry of Labour; amounts by decree and budget laws, not read); no payroll tax in the laws read (DL 144/1959, Social Security Code). Coordinator decision of pass 3l: OECD 3000 covers taxes paid by employers as a fixed amount per person employed, so a per-worker fee levied by law on employers belongs here and the heading is not cited absent until the fee text is read; a one-off permit issuance charge that does not scale with the workforce is not a tax (note only). No company input carries the workforce by nationality. Grade C (pass 3l)."

def payrollUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then [payrollNote] else []

end LbGlobal
