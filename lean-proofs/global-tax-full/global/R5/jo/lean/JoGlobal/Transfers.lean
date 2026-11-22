import TaxKernel.Global
import R5Common

/-!
# Jordan 2025: land registration fee and real-estate sale tax (4400)

Texts of the Department of Lands and Survey (dls.gov.jo, consolidated by the Department; Wayback captures of 20/04/2025;
`law/jo_fees_law26_1958.*`, `law/jo_fees_table_2023.*`, `law/jo_salestax_law21_1974.*`):
* Land Registration Fees Law No. 26 of 1958 as amended to Law 7/2023 (OG 5847 of 01/03/2023, in force 31/03/2023):
  art. 3(1) the fees of the annexed table, by the value of the immovable property; **art. 3(6) the fees are paid by
  the party in whose favour the transaction is made unless the parties agree otherwise** (the buyer); art. 4(و) the
  fee is levied on the value assessed by the committees where the declared price differs.
  Table (2023) item 1(ج) sale: **3 %** of the assessed value, minimum 20 dinars per buyer; 1(أ) between ascendants
  and descendants to the third degree, spouses, brothers and sisters 0,5 %; 1(ب) between co-owners 0,5 %.
* Real Estate Sale Tax Law No. 21 of 1974 as amended to Law 25/2023 (OG 5903 of 31/12/2023, in force 30/01/2024):
  art. 3 on the sale of any property the land registries collect **from the seller** (or donor) a tax of **3 %** of the
  amount on which the registration fee is levied; art. 4(أ) exempts sales and gifts between ascendants and descendants
  to the third degree, brothers and sisters and spouses.
Model: buyer 3 % of the assessed value (the price where no assessed value is given), at least 20 dinars; seller 3 % of
the proceeds (a disposal carries no assessed value). **Grade A** (statute texts read).
-/

namespace JoGlobal
open TaxKernel TaxKernel.Global R5Common

def joBase (p : Purchase) : Int := if p.assessed ≥ 0 then p.assessed else p.price

def regFee (b : Int) : Int := max 20 (divR .up (300 * pos b) BP)

def transfers : Family :=
  { name := "4400 رسوم تسجيل الأراضي وضريبة بيع العقار", covers := [.transactions],
    run := fun _ g _ =>
      ((g.purchases.zipIdx.filter fun (p, _) => p.kind.isRealEstate).map fun (p, i) =>
          charge .transactions "رسم تسجيل البيع (المشتري)" (joBase p) pos regFee (event := s!"purchase {i + 1}")
            (statute := "Land Registration Fees Law 26/1958 art. 3(1), 3(6), 4(و); Table 2023 item 1(ج) (3 % of the assessed value, min 20 dinars)"))
      ++ ((g.disposals.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>
          charge .transactions "ضريبة بيع العقار (البائع)" d.proceeds pos (fun x => divR .up (300 * x) BP) (event := s!"disposal {i + 1}")
            (statute := "Real Estate Sale Tax Law 21/1974 art. 3 (3 % from the seller)")) }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (fun p => p.kind.isRealEstate) || g.disposals.any (fun d => d.kind.isRealEstate) then
    ["registration fee and sale tax: sales between relatives (0,5 % fee, tax exempt) not distinguished; Council of Ministers exemptions for apartments (by area) not read; seller's tax on the proceeds (the assessed value is not an input of a disposal)"] else []

#guard regFee 100000 == 3000
#guard regFee 100 == 20

end JoGlobal
