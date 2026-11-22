import TaxKernel.Global
import R5Common
import TrTax

/-!
# Türkiye 2025: employer social security premiums (2200)

Sosyal Sigortalar ve Genel Sağlık Sigortası Kanunu No. 5510 (`law/tr_5510.pdf`) art. 81: (a) long-term (MYÖ) premium
"%20'sidir … %11'i işveren hissesidir" (the consolidated text prints 21 % / 12 % as changed by Law 7566 of 4/12/2025,
in force from 2026: footnote 141); GSS premium "%12,5'idir. Bu primin %5'i sigortalı, %7,5'i ise işveren hissesidir".
Base: the earnings subject to premium, capped at the 1.x ceiling `TrTax.ssCeiling` (7,5 × the monthly minimum wage, in
kuruş) × 12. Not modelled: the 5-point Treasury incentive (art. 81(ı)), unemployment insurance (Law 4447, 2 %), short-
term branches (risk-rated).
-/

namespace TrGlobal
open TaxKernel TaxKernel.Global R5Common

def annualCeiling : Int := 12 * TrTax.ssCeiling / TrTax.KR

def social : Family :=
  { name := "2200 SGK işveren primleri", covers := [.sscEmployer],
    run := fun _ g _ =>
      employerOn "MYÖ primi (işveren)" "5510 art. 81(a) (11 % employer, 2025 wording)" 1100 annualCeiling g
      ++ employerOn "GSS primi (işveren)" "5510 art. 81 GSS (7,5 % employer)" 750 annualCeiling g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.household.adults.any (·.wages > 0) then ["employer: unemployment insurance (Law 4447), short-term branches and the 5-point incentive not modelled"] else []

#guard annualCeiling == 12 * (2600550 * 15 / 2) / 100

end TrGlobal
