import TaxKernel.Global
import R5Common

/-!
# Oman 2025: employer social protection contributions (2200)

Social Protection Law (Royal Decree 52/2023, 1 Muharram 1445H), Qanoon.om consolidated text (1.x
`law/qanoon_l2023052.txt`); RD art. 6: in force 1 January 2024, except the injury branch for non-Omanis (after five
years), Part III chapter 6 (sickness leave: after three years, i.e. from July 2026) and chapter 7 (maternity leave:
after one year, i.e. from July 2024). For an Omani employee in 2025:
* art. 70(1): old age, disability and death, employer "(١١٪) أحد عشر في المائة من الأجر الشهري … وفقا لحكم المادة (٥٢)";
* art. 90: work injuries and occupational diseases, employer (١٪);
* art. 52: contribution wage ceiling for those two branches (٣٠٠٠) OMR a month (36 000 a year);
* art. 116(1): job security, employer (٠٫٥٪) of the wage (no ceiling);
* art. 128: maternity leave, employer (١٪) of the wage (no ceiling).
Non-Omanis: no branch in force for them in 2025 except the savings scheme of art. 139(1) (9 %), which starts on a
date set by the Fund's board (RD art. 6(5), not read): not computed.
-/

namespace OmGlobal
open TaxKernel TaxKernel.Global R5Common

def nationalityOm (g : CanonGlobal) : String := (g.str? "nationality").getD ((g.household.str? "nationality").getD "national")

def omCap : Int := 3000 * 12

def social : Family :=
  { name := "2200 Social Protection Fund (employer)", covers := [.sscEmployer],
    run := fun _ g _ =>
      if nationalityOm g != "national" then [] else
      employerOn "old age, disability, death + work injury (employer)" "Social Protection Law art. 70(1) (11 %), 90 (1 %), 52 (OMR 3,000 a month)" 1200 omCap g
      ++ employerOn "job security + maternity leave (employer)" "Social Protection Law art. 116(1) (0.5 %), 128 (1 %)" 150 (-1) g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) || nationalityOm g == "national" then [] else
  ["non-Omani employee: savings scheme 9 % (art. 139(1)) starts on a board date (not read): not computed"]

#guard omCap == 36000

end OmGlobal
