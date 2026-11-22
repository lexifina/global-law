import TaxKernel.Global2
import R5Common

/-!
# Azerbaijan 2025: road tax (yol vergisi) and vehicles (5200 / 5121)

Tax Code (Vergi Məcəlləsi), e-qanun.az framework 46948, Wayback captures of 04/12/2024 (`law/eqanun_46948_20241204.txt`,
windows-1251) and 24/08/2026 (`law/eqanun_46948_20260824.txt`), with the consolidation's amendment footnotes:
* **No recurrent tax on vehicles registered in Azerbaijan.** Art. 197.1.1 still prints "rezident fiziki şəxslərə məxsus
  avtomobil və özüyeriyən təkərli texnika" among the property-tax objects, but its footnote records that Law
  792-IIQD of 03/12/2004 **removed** those words (the consolidation kept them by mistake: the same footnote's
  second change, "vasitələrinin dəyəri" → "vasitələri", is applied); art. 198.1 (Law 406-VIQD of 03/12/2021) gives
  natural persons' rates for buildings, water and air vehicles only. The road tax on persons owning or using cars in
  Azerbaijan (art. 209 as amended in 2004) was removed by Law 1167-IVQD of 30/12/2014 (art. 209 new wording).
* **Road tax, art. 209-211** (in force 2025): payers are owners or drivers of vehicles registered abroad entering,
  crossing or leaving Azerbaijan (art. 211.1.1: USD by engine size, seats, axles and days: not inputs), and producers
  and importers of motor petrol, diesel and LPG: **art. 211.1.2** as worded by Law 98-VIIQD of 16/12/2024 (published
  27-28/12/2024): 0,02 manat for each litre, added to the wholesale price (domestic) or the customs value (imports);
  the 2026 consolidation prints 0,07, but its footnote records that **Law 297-VIIQD of 09/12/2025** (published
  29-30/12/2025) replaced "0,02" by "0,07" in the first and second sentences: 0,07 is the 2026 rate, not 2025's
  (pass 3p year-in-force fix; Dec-2025 Tax Code changes taken from 1/1/2026, entry clause not read). Before Law 98-VIIQD
  (04/12/2024 capture): also 0,02 manat a litre added to the wholesale price.
Model: the fuel road tax is a per-litre charge on the household's petrol and diesel (`quantity` in thousandths of a litre), borne by
the consumer through the price, heading 5121 (a tax on a product, like the excise); LPG has no basket good. **Grade B**
(statute read through the consolidation and its amendment footnotes; the amending laws' own texts not read).
-/

namespace AzGlobal
open TaxKernel TaxKernel.Global R5Common

def yolVergisi : Excise :=
  { rates := [
      perUnit .petrol "Yol vergisi (road tax on motor fuel)" 2 100 "Tax Code art. 209, 210, 211.1.2 as worded by Law 98-VIIQD of 16/12/2024: 0,02 manat per litre (0,07 only from Law 297-VIIQD of 09/12/2025)",
      perUnit .diesel "Yol vergisi (road tax on motor fuel)" 2 100 "Tax Code art. 209, 210, 211.1.2 as worded by Law 98-VIIQD of 16/12/2024: 0,02 manat per litre (0,07 only from Law 297-VIIQD of 09/12/2025)"] }

def vehicles : Family :=
  { name := "5200 yol vergisi (road tax)", covers := [.excise],
    run := fun _ g _ => yolVergisi.charges g.consumption }

def vehiclesUnsupported (g : CanonGlobal) : List String :=
  (if g.vehicles.isEmpty then [] else
    ["vehicles registered in Azerbaijan: no recurrent tax (art. 197.1.1 car words removed by Law 792-IIQD of 2004; art. 198.1 rates for buildings, water and air vehicles only; art. 209 since Law 1167-IVQD of 2014); road tax on foreign-registered vehicles (art. 211.1.1) not an input"])
  ++ (if g.consumption.any (fun s => (s.good == .petrol || s.good == .diesel) && s.quantity ≤ 0) then
    ["road tax on motor fuel (art. 211.1.2): petrol/diesel without litres (quantity) not computed"] else [])

#guard yolVergisi.duty { good := .petrol, amount := 1500, quantity := 1000000 } == 20
#guard yolVergisi.duty { good := .diesel, amount := 600, quantity := 500000 } == 10

end AzGlobal
