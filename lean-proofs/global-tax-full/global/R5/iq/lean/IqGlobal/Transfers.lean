import TaxKernel.Global
import R5Common

/-!
# Iraq 2025: tax on the transfer of ownership of real estate (ضريبة نقل ملكية العقار, 4400)

Decision of the (dissolved) Revolutionary Command Council No. 120 of 27/06/2002 (Iraqi Gazette 3938 of 08/07/2002, in
force 07/08/2002), as compiled by the legal section of the General Commission for Taxes (2011)
(`tax.mof.gov.iq/قرار-120-لسنة-2002-ضريبة-نقل-ملكية-العقار/`, Wayback 2023-09-27; `law/iq_rcc120_2002.{html,txt}`):
* item Second: a lump-sum tax at progressive rates on the value of the property assessed under Law 85/1978 **or the
  consideration, whichever is higher**, **on the owner** (the transferor) on any transfer of ownership or of the right
  of disposal (sale, exchange, settlement, waiver, gift, partition, …);
  (1) the first **IQD 20 000 000** is exempt; (2) the excess is taxed at **3 %** up to 30 000 000, **4 %** above
  30 000 000 to 60 000 000, **5 %** above 60 000 000 to 90 000 000, **6 %** above 90 000 000;
* item Fifth: gifts between parents and children or between spouses are exempt.
Reading: the band limits apply to the amount subject to tax (the excess over the exemption). Model: each real-estate
disposal, on the seller, base = proceeds (a disposal carries no assessed value). **Grade A** (decision text read).
-/

namespace IqGlobal
open TaxKernel TaxKernel.Global R5Common

/-- item Second (2): progressive rates (basis points) on the taxable excess, band limits on that excess. -/
def transferBands (x : Int) : Int :=
  let x := pos x
  divR .down (min x 30000000 * 300 + pos (min x 60000000 - 30000000) * 400
    + pos (min x 90000000 - 60000000) * 500 + pos (x - 90000000) * 600) BP

def transfers : Family :=
  { name := "4400 ضريبة نقل ملكية العقار", covers := [.transactions],
    run := fun _ g _ =>
      (g.disposals.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>
        charge .transactions "ضريبة نقل ملكية العقار (المالك الناقل)" d.proceeds (fun b => pos (b - 20000000)) transferBands
          (event := s!"disposal {i + 1}")
          (statute := "RCC decision 120/2002 item Second (owner; first IQD 20 000 000 exempt; 3/4/5/6 % bands at 30/60/90 million)") }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.disposals.any (fun d => d.kind.isRealEstate) then
    ["4400 real estate transfer tax: base = proceeds (the Law 85/1978 assessed value, if higher, is not an input of a disposal); band limits read as applying to the taxable excess; gifts within the family (exempt) not distinguished"] else []

#guard transferBands 80000000 == 3100000
#guard transferBands 10000000 == 300000

end IqGlobal
