import TaxKernel.Global
import R5Common

/-!
# Algeria 2025: droit de mutation à titre onéreux d'immeubles (4400)

Code de l'enregistrement, DGI edition 2023 in French (`law/dgi_cenr_2023_fr.pdf`, Wayback 2023-02-02 of
`mfdgi.gov.dz/images/pdf/codes_fiscaux/CENR_2023_fr.pdf`; the 2025 Arabic edition `law/dgi_cenr_2025_ar.pdf`, Wayback
2025-02-24, dropfiles catid 776 id 2520):
* art. 252: sales and all acts transferring the ownership or usufruct of immovable property for consideration "sont
  assujettis à un droit de 5%" (last amended by LF 1999 art. 32); art. 255: property abroad 3 %.
* art. 258: exemptions (young entrepreneurs' schemes, public land bodies, savings-scheme flats sold by the OPGI, …) not
  applied.
The duty is on the price stated in the deed (art. 256 lets the administration correct it). Taxe de publicité foncière
not computed. **Grade A** (statute read).
-/

namespace DzGlobal
open TaxKernel TaxKernel.Global R5Common

def mutation : TransferDuty := { name := "droit de mutation (رسم نقل الملكية)", sched := Schedule.flat 500 }

def transfers : Family :=
  { name := "4400 droits d'enregistrement (mutations immobilières)", covers := [.transactions],
    run := fun _ g _ => mutation.charges g.purchases "Code de l'enregistrement art. 252 (5 %)" }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (fun p => p.kind.isRealEstate) then
    ["registration duty: art. 258 exemptions and the taxe de publicité foncière not applied"] else []

#guard mutation.amount { kind := .home, price := 10000000 } == 500000

end DzGlobal
