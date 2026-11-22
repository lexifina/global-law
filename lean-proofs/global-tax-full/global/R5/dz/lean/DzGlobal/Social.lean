import TaxKernel.Global
import R5Common

/-!
# Algeria 2025: employer social security contribution (2200)

Décret exécutif n° 06-339 du 25 septembre 2006 (JORADP n° 60 of 27 Sep 2006, `law/dz_jo_F2006060.pdf`) amending
décret 94-187, art. 1: of the 34,5 % rate (décret législatif 94-12 art. 1), from 1 October 2006 "25% de l'assiette de
cotisation de sécurité sociale à la charge de l'employeur" (assurances sociales 12,5 %, accidents du travail 1,25 %,
retraite 10 %, assurance-chômage 1 %, retraite anticipée 0,25 %) and "0,5% … au titre de la quote-part du Fonds des
œuvres sociales" (paid out of the employer's social-works funding, décret 82-179): 25,5 % charged. No ceiling in the
decree (base: ordonnance 95-01, not read). Later amendments of décret 94-187 not checked (as in the 1.x model).
-/

namespace DzGlobal
open TaxKernel TaxKernel.Global R5Common

def socialPre3q : Family :=
  { name := "2200 CNAS employer contribution", covers := [.sscEmployer],
    run := fun _ g _ =>
      employerOn "Cotisation de sécurité sociale (employeur)"
        "Décret exécutif 06-339 art. 1 (décret 94-187 art. 1-2): 25 % employer + 0,5 % fonds des œuvres sociales" 2550 (-1) g }

def socialUnsupportedPre3q (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer CNAS: base rules (ordonnance 95-01) and later amendments of décret 94-187 not read; employment-support rate reductions not applied"]

#guard divR .down (2550 * 100000) BP == 25500


/-- Pass 3q year-in-force audit: grade C. 2200 CNAS employer contribution grade C (year-in-force audit, pass 3q): Décret exécutif 06-339 (JORADP 2006) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`socialPre3q`) for a later re-cite;
it is not in the model. -/
def socialUnsupported (g : CanonGlobal) : List String :=
  (if (socialPre3q.run [] g []).isEmpty then [] else ["2200 CNAS employer contribution grade C (year-in-force audit, pass 3q): Décret exécutif 06-339 (JORADP 2006) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ socialUnsupportedPre3q g

end DzGlobal
