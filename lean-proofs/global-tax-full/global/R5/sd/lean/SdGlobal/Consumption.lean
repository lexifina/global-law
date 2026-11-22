import TaxKernel.Global
import R5Common

/-!
# Sudan 2025: value added tax (5111)

Value Added Tax Act 2000 (قانون الضريبة على القيمة المضافة لسنة 2000) as consolidated by the Taxation Chamber to Act 35 of
2015 (`tax.gov.sd/documents/VAT law.pdf`, created 24/07/2016, Wayback 2017-01-02; `law/sd_vat_act2000_tc2016.pdf`, Arabic
OCR `law/sd_vat_act2000_tc2016.ocr.txt`, art. 14 read on the page image p. 12):
* art. 14(1): 15 % on goods, services and works, exports at zero; footnote: Council of Ministers order of 19/06/2012
  sets the rate at **17 %** (art. 15 lets the Council amend the rate by order); a Council order of 07/05/2015 sets the
  tax on cigarettes at **30 %**;
* art. 14(2): telecommunication services **30 %**;
* art. 36(1) exemptions: (a) goods: agricultural products sold in their natural state, livestock, meat, poultry, fish,
  dairy and their products, fertilisers, seeds, pesticides, medicines, locally produced flour, bread; (b) services:
  financial services, insurance, education, medical services, renting and sale of residential real estate.
Basket classes: food, medicines, health, education, financial, insurance, rent exempt; communication and cigarettes
30 %; every other good 17 %. **Grade B**: the 17 % and the cigarette rate are the Council orders as footnoted in the
Chamber's consolidation (orders not read); Finance Acts after 2015 not read.
-/

namespace SdGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "الضريبة على القيمة المضافة", standard := 1700, reduced := 3000,
    classOf := fun g => match g with
      | .food | .medicines | .health | .education | .financial | .insurance | .rent => .exempt
      | .communication | .cigarettes => .reduced
      | _ => .standard }

def consumptionPre3q : Family :=
  { name := "5111 الضريبة على القيمة المضافة", covers := [.vat],
    run := fun _ g _ =>
      if g.consumption.isEmpty then [] else
        [vat.basketCharge g.consumption "VAT Act 2000 art. 14(1) (17 % by Council of Ministers order of 19/06/2012), 14(2) (telecommunications 30 %), Council order of 07/05/2015 (cigarettes 30 %), art. 36(1) exemptions"] }

def consumptionUnsupportedPre3q (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
    ["VAT: food taken as exempt (art. 36(1)(a): natural agricultural products, meat, fish, dairy, flour, bread; processed food not separated); excise duties not read; Finance Acts after 2015 not read"]

#guard vat.basket [{ good := .clothing, amount := 11700 }] == 1700
#guard vat.basket [{ good := .communication, amount := 13000 }] == 3000


/-- Pass 3q year-in-force audit: grade C. 5111 VAT grade C (year-in-force audit, pass 3q): the VAT Act 2000 consolidation to Act 35/2015 (Taxation Chamber, 2016) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`consumptionPre3q`) for a later re-cite;
it is not in the model. -/
def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if (consumptionPre3q.run [] g []).isEmpty then [] else ["5111 VAT grade C (year-in-force audit, pass 3q): the VAT Act 2000 consolidation to Act 35/2015 (Taxation Chamber, 2016) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ consumptionUnsupportedPre3q g

end SdGlobal
