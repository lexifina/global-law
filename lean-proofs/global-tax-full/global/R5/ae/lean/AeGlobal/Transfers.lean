import TaxKernel.Global
import R5Common

/-!
# United Arab Emirates 2025 (model emirate: Dubai): Land Department fee on property sales (4400)

Executive Council Resolution No. (30) of 2013 Approving Fees of the Land Department (Dubai), English text of the Dubai
Legislation Portal (`dlp.dubai.gov.ae/Legislation Reference/2013/ECR 30 of 2013.pdf`; `law/ae_ecr30_2013.pdf` + `.txt`),
issued under Law No. (7) of 2006 Concerning Real Property Registration:
* art. 2 and Schedule item 1: registering a real property sale contract **4 %** of the value of the sale contract
  (item 2: warehouses AED 10 per m² of plot, at least AED 10 000; not computed).
* art. 3(1): "unless agreed otherwise, the Fee for the sale of Real Property will be shared equally by the seller and
  purchaser": **2 % from the buyer** (purchases) and **2 % from the seller** (disposals of real estate).
The UAE has no federal transfer tax; the fee is the emirate's. Dubai is the model's emirate (Abu Dhabi, Sharjah and the
others have their own fee laws, not read). **Grade B** (English text of the Dubai Legislation Portal, not the Arabic
Official Gazette text; no later amendment of item 1 found).
**2025 (pass 3r re-cite).** DLD service page "Request for sale registration" (dubailand.gov.ae/en/eservices/
request-for-sale-registration/, "Site was last updated on 05 March 2025", Wayback 17/03/2025;
`law/ae_dld_sale_registration_2025.html`): "Service Fees: The seller: 2% of the sale value; The purchaser: 2% of the sale
value", plus fixed fees (AED 250 a unit or villa, plot maps, AED 10 + 10 per drawing) and the registration trustee's
service charge (AED 4,000 / 2,000 + VAT, a private partner's fee): the 2 % + 2 % rule is the one in force in 2025 (the
fixed fees are not computed). Grade B (official guide).
-/

namespace AeGlobal
open TaxKernel TaxKernel.Global R5Common

def dldBuyer : TransferDuty := { name := "Dubai Land Department sale registration fee (purchaser's half)", sched := Schedule.flat 200 }

def transfers : Family :=
  { name := "4400 Dubai Land Department fee", covers := [.transactions],
    run := fun _ g _ =>
      dldBuyer.charges g.purchases "Dubai ECR 30/2013 Schedule item 1 (4 % of the sale contract), art. 3(1) (shared equally: purchaser 2 %)"
      ++ ((g.disposals.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>
          charge .transactions "Dubai Land Department sale registration fee (seller's half)" d.proceeds pos
            (fun x => divR .down (200 * x) BP) (event := s!"disposal {i + 1}")
            (statute := "Dubai ECR 30/2013 Schedule item 1 (4 %), art. 3(1) (shared equally: seller 2 %)")) }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (fun p => p.kind.isRealEstate) || g.disposals.any (fun d => d.kind.isRealEstate) then
    ["property registration fee: Dubai's (4 % shared equally unless agreed otherwise) applied to every property; other emirates' fees and warehouses (AED 10/m²) not read"] else []

#guard dldBuyer.amount { kind := .home, price := 2000000 } == 40000



end AeGlobal
