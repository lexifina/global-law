import TaxKernel.Global
import R5Common

/-!
# Iraq 2025: sales tax on hotel and restaurant services (5126, booked under 5120)

* RCC (dissolved) decision No. 36 of 4/5/1997 (in force 1/6/1997), text reproduced by the General Commission for Taxes
  (`tax.mof.gov.iq/قرار-رقم36-لسنة-1997-ضريبة-المبيعات/`, Wayback 2023-09-25; `law/iq_rcc36_1997_gct.txt`), item First:
  "تفرض ضريبة تسمى ضريبة المبيعات بنسبة (10%) ... على اقيام جميع الخدمات التي تقدمها فنادق ومطاعم الدرجتين الممتازة
  والأولى"; item Second: the management of the establishment collects it (on the bill: Instructions 7/1997 art. 3).
* Federal General Budget Law No. 13 of 2023 for 2023-2025 (Al-Waqai Al-Iraqiya 4726, page image p. 40), art. 20 First:
  the sales tax of decision 36/1997 applies to the services of restaurants and hotels **up to the second class** in
  addition to the excellent and first classes.
Model: household spending on restaurants and hotels carries 10 % (tax-inclusive amounts: 10/110 embedded); the
class of the establishment is not an input (third-class and popular establishments are outside: not distinguished).
Not a general sales tax or VAT (5111): the decision taxes these services only. Other sales taxes set by budget laws
(mobile and internet services, travel tickets, cars, tobacco and alcohol) not read. **Grade A** (decision text from the
tax authority; budget article read on the gazette page image).
-/

namespace IqGlobal
open TaxKernel TaxKernel.Global R5Common

def salesTax : Vat :=
  { name := "ضريبة المبيعات (الفنادق والمطاعم)", standard := 1000,
    classOf := fun g => match g with
      | .restaurants | .hotels => .standard
      | _ => .exempt }

def consumption : Family :=
  { name := "5126 ضريبة المبيعات", covers := [.goodsOther],
    run := fun _ g _ =>
      let xs := g.consumption.filter fun s => s.good == .restaurants || s.good == .hotels
      if xs.isEmpty then [] else
        [charge .goodsOther salesTax.name (isum (xs.map (·.amount))) id (fun _ => salesTax.basket xs)
          (event := "basket") (bearer := .consumer)
          (statute := "RCC decision 36/1997 item First (10 % on hotel and restaurant services); Budget Law 13/2023 art. 20 First (to the second class)")] }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .restaurants || s.good == .hotels) then
    ["sales tax: establishment class not an input (below the second class untaxed): all restaurant and hotel spending taxed"] else [])
  ++ (if g.consumption.any (fun s => s.good == .communication || s.good == .cigarettes || s.good == .spirits || s.good == .beer || s.good == .wine) then
    ["sales taxes of Finance Ministry Instructions 5/2015 (Federal Budget Law 2015 art. 33: mobile and internet 20 %, air tickets 15 %, imported or local cigarettes and alcohol 300 % of the customs value; car imports 15 %, collection stopped by GCT circular of 13/4/2016): in force in 2025 not established (annual budget-law basis; no continuation found in Budget Law 13/2023): not computed (grade C)"] else [])

#guard salesTax.basket [{ good := .restaurants, amount := 110000 }] == 10000

end IqGlobal
