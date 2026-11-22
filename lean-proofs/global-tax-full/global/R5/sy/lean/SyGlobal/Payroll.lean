import TaxKernel.Global

/-! # Sy: taxes on payroll and workforce (OECD 3000), grade C (pass 3l)

3000 taxes on payroll and workforce: fees for work permits of foreign workers (Labour Law 17/2010; not read); no payroll tax in the laws read (ITL 24/2003 as amended by LD 30/2023). Coordinator decision of pass 3l: OECD 3000 covers taxes paid by employers as a fixed amount per person employed, so a per-worker fee levied by law on employers belongs here and the heading is not cited absent until the fee text is read; a one-off permit issuance charge that does not scale with the workforce is not a tax (note only). No company input carries the workforce by nationality. Grade C (pass 3l).
-/

namespace SyGlobal
open TaxKernel TaxKernel.Global

def payrollNote : String := "3000 taxes on payroll and workforce: fees for work permits of foreign workers (Labour Law 17/2010; not read); no payroll tax in the laws read (ITL 24/2003 as amended by LD 30/2023). Coordinator decision of pass 3l: OECD 3000 covers taxes paid by employers as a fixed amount per person employed, so a per-worker fee levied by law on employers belongs here and the heading is not cited absent until the fee text is read; a one-off permit issuance charge that does not scale with the workforce is not a tax (note only). No company input carries the workforce by nationality. Grade C (pass 3l)."

def payrollUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then [payrollNote] else []

end SyGlobal
