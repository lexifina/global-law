import TaxKernel.Global
import R5Common

/-!
# Saudi Arabia 2025: Real Estate Transaction Tax (4400)

Real Estate Transaction Tax Law (issued 1446/03/19 H = 22/09/2024), laws.boe.gov.sa as archived on 2025-05-13
(`law/rett_2025.html`, ARCHIVE_INDEX.tsv):
* art. 2: "تفرض الضريبة بنسبة قدرها (5%) خمسة بالمائة على التصرف العقاري" on the agreed value when it is within the fair
  market value (else on that value: the purchase's `assessed` is read as the fair market value, higher of the two).
* art. 3(a): total exemptions (estate divisions, gifts to the spouse and relatives to the third degree, waqf, public
  bodies, …): not purchases for consideration; not modelled as purchases.
The state's payment of the tax on a first home (a decision outside the Law) is not modelled.
-/

namespace SaGlobal
open TaxKernel TaxKernel.Global R5Common

def rett : TransferDuty := { name := "ضريبة التصرفات العقارية", sched := Schedule.flat 500, higherOfAssessed := true }

def transfers : Family :=
  { name := "4400 ضريبة التصرفات العقارية", covers := [.transactions],
    run := fun _ g _ => rett.charges g.purchases "RETT Law (1446H) art. 2 (5 %)" }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (·.firstHome) then ["first-home relief (state-borne tax, outside the Law) not modelled"] else []

#guard rett.amount { kind := .home, price := 1000000 } == 50000
#guard rett.amount { kind := .home, price := 1000000, assessed := 1200000 } == 60000

end SaGlobal
