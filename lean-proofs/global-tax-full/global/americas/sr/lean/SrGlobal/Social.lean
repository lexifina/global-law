import SrGlobal.Pit

/-!
# Suriname 2025: employer contributions (2200)

Source: Wet Algemeen Pensioen 2014 (S.B. 2014 no. 113, DNA copy, archived `sr/law/wet_algemeen_pensioen_2014_dna.*`) art. 8: "De maandelijkse premie bedraagt drie procent van de bijdragegrondslag" (lid 1), "zal ingaande 1 januari 2016, jaarlijks met een half procent (0.5/100) worden verhoogd tot en met een maximum van achtentwintig procent" (lid 2): 8 % in 2025; maximum bijdragegrondslag SRD 5,000 a month (lid 3), no premium above it (lid 5); employer share 50/100 (lid 7 b). Grade B: the staatsbesluiten that may have changed the base limits (lid 6) were not read and the steps are taken as applied. The Wet AOV premium is the resident's (no employer share). The basiszorg premium stays C.
-/

namespace SrGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon SrGlobal

/-- Wet Algemeen Pensioen 2014 (S.B. 2014 no. 113) art. 8: premium 3 % from entry into force, + 0.5 point each 1 January
    from 2016 (lid 2): 8 % in 2025; employer half (lid 7 b); maximum bijdragegrondslag SRD 5,000 a month (lid 3, lid 5). -/
def maxGrondslag : Int := 60000
def ap : Contribution := Contribution.flatCapped "Algemeen Pensioen premie (werkgeversaandeel)" 400 maxGrondslag
def fam1 : Family := employerFamily "2200 Algemeen Pensioen (werkgever)" [ap] "Wet Algemeen Pensioen 2014 art. 8 leden 1-3, 5, 7: employer half of 8 % (2025) up to SRD 5,000 a month" (inBp := 10000) (oecd := .sscEmployer) (level := .social)

def families : List Family := [fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "Algemeen Pensioen employer 4 % (half of 8 %) up to SRD 60,000 a year: the yearly 0.5-point steps of art. 8 lid 2 taken as applied and the 2014 bijdragegrondslag limits as unchanged (staatsbesluiten under art. 8 lid 6 not read); minimum base SRD 500 not applied; health insurance (Wet Nationale Basiszorgverzekering) premium not modelled"

#guard ap.amount 50000 == 2000
#guard ap.amount 1000000 == ap.amount maxGrondslag

end SrGlobal.Social
