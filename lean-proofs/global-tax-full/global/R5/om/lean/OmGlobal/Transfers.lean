import TaxKernel.Global
import R5Common

/-!
# Oman 2025: registration fee on sales of real property (4400)

Ministerial Decision 570/2025 (Ministry of Housing and Urban Planning) issuing the regulation of values, fees and
prices the Ministry collects (Official Gazette 1581 of 26/01/2025; in force the day after publication: art. 3; repeals
MD 43/2012 and 92/2016: art. 2). Text from qanoon.om (`qanoon.om/p/2025/mhup20250570/`, Gazette scan
`data.qanoon.om/ar/md/mhup/2025-0570.pdf`; `law/om_md570_2025.txt`):
* Annex 7 (registration and documentation of dispositions), item 1: registration of contracts of sale and of gift from
  third parties and from relatives other than the first degree **3 %** of the value of the property; item 2: an
  individual transferring to a company wholly or 50 %-owned by him 1 %; item 3: investment funds 1 %; item 4: sale by
  an Islamic bank to the buyer 0,5 % of the first sale contract.
* The regulation does not name the party who pays; the fee is a condition of registering the transfer in the
  acquirer's name, so it is charged to the buyer (agreements between the parties not modelled).
MD 92/2016 (in force until 26/01/2025) printed 5 % for item 1; the reduction to 3 % before 2025 was not read, so the
3 % is applied to the whole year. **Grade B** (pass 3n, FT reviewer 6 Y-7: MD 570/2025 governs from
27/01/2025 only; 1-26 January 2025 fell under MD 92/2016, printed 5 %, whose reduction to 3 % was not read; purchases carry no
date) (Arabic text read; dated note above).
-/

namespace OmGlobal
open TaxKernel TaxKernel.Global R5Common

def registration : TransferDuty := { name := "رسم تسجيل عقد البيع", sched := Schedule.flat 300 }

def transfers : Family :=
  { name := "4400 رسوم تسجيل التصرفات العقارية", covers := [.transactions],
    run := fun _ g _ => registration.charges g.purchases "MD 570/2025 regulation, Annex 7 item 1 (3 % of the value of the property)" }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (fun p => p.kind.isRealEstate) then
    ["registration fee charged to the buyer (the regulation names no payer); 1-26 January 2025 under MD 92/2016 as amended (not read): 3 % applied to the whole year; transfers to own companies, funds and Islamic-bank sales (1 % / 0,5 %) not distinguished"] else []

#guard registration.amount { kind := .home, price := 100000 } == 3000

end OmGlobal
