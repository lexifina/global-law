import TaxKernel.Global
import R5Common

/-!
# Bahrain 2025: property registration fee on sales (4400)

Law No. 13 of 2013 promulgating the Property Registration Law, English text of the Survey and Land Registration
Bureau (`slrb.gov.bh/uploads/K1313.pdf`, "unofficial translation"; `law/bh_K1313.pdf` + `.txt`):
* art. 50 First: sale agreement registration fee **2 %** of the property's value; 15 % of the fee is deducted if the
  registration takes place within 60 days of the sale agreement (art. 34: within two months of notarization), i.e.
  **1,7 %**. Second: swaps 2 % of the larger value, "jointly paid by the parties". Third: gifts 5 dinars (royal gifts,
  spouses and relatives to the fourth degree, value up to BD 50 000), else 2 %.
* art. 51: fees are charged in advance, before the action (registration in the buyer's name); art. 53-54: on the value
  at notarization / the price in the instrument, re-estimated where the true value is higher.
Model: the fee is charged to the buyer, the applicant for registration of the transfer (the law names joint payment
only for swaps); registration within 60 days assumed (1,7 %); base = max(price, assessed value) (art. 54).
**Grade B** (English non-official translation; the SLRB fee schedule shows the same 2 % / 1,7 %).
-/

namespace BhGlobal
open TaxKernel TaxKernel.Global R5Common

def registration : TransferDuty := { name := "Sale agreement registration fee", sched := Schedule.flat 170, higherOfAssessed := true }

def transfers : Family :=
  { name := "4400 property registration fee", covers := [.transactions],
    run := fun _ g _ => registration.charges g.purchases "Property Registration Law (Law 13/2013) art. 50 First (2 %, less 15 % when registered within 60 days), art. 51, 54" }

def transfersUnsupported (g : CanonGlobal) : List String :=
  (if g.purchases.any (fun p => p.kind.isRealEstate) then ["registration fee: registration within 60 days assumed (1,7 %; 2 % after)"] else [])
  ++ (if g.transfers.any (·.kind == .gift) then ["gift registration fee (art. 50 Third: 5 dinars, or 2 % above BD 50 000 to non-relatives) not computed"] else [])

#guard registration.amount { kind := .home, price := 100000 } == 1700
#guard registration.amount { kind := .home, price := 100000, assessed := 120000 } == 2040

end BhGlobal
