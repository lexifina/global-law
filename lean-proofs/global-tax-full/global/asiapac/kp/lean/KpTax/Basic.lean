import TaxKernel.World

/-!
# Democratic People's Republic of Korea: no tax on income, 2025

Access tier B (rescue pass 2): the only text reached is a secondary host's English translation of the Constitution.
* Constitution of the DPRK, 1972 as revised in 2016, English text on constituteproject.org ("Korea (Democratic People's
  Republic of) 1972 (rev. 2016)", page marked "Subsequently amended"; saved `kp/law/rescue2/cp_kp2016.html`/`.txt`),
  art. 25: "The increasing material wealth of society in our country, where taxes have been abolished, is used
  entirely to promote the well-being of the working people."
Doubts (written down, not resolved): the translation is not official; the page itself says the text was amended after
2016 (the 2019 and later revisions were not reached, so art. 25's 2025 wording is not verified); the 1974 law that
abolished taxes was not reached; state levies on enterprises and any social-insurance contribution withheld from wages
(not a tax in the Constitution's sense) are outside the text read.
Model: income tax 0 for every household (art. 25); employee contributions unsupported.
-/

namespace KpTax
open TaxKernel

def out (c : Canon) : Out :=
  Out.make c "KP" "KPW" 0 (employeeSocial := 0)
    (detail := [Out.dStr "note" "No tax on income: Constitution of the DPRK (1972, rev. 2016) art. 25 'where taxes have been abolished' (constituteproject.org translation; later revisions not checked)"])
    (unsupported := ["employee social-insurance contributions (if any are withheld from wages): no text reached; employeeSocial = 0"])

def country : Country :=
  { code := "KP", name := "Democratic People's Republic of Korea", currency := "KPW", year := "2025", compute := out }

-- The model never charges income tax.
#guard (out { id := "g", adults := [{ wages := 1000000 }] }).incomeTax = 0

end KpTax
