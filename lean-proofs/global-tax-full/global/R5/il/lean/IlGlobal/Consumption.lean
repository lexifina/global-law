import TaxKernel.Global
import R5Common

/-!
# Israel 2025: VAT (מס ערך מוסף, 5111); purchase tax and fuel excise not computed (5121)

Source: Value Added Tax Law 5736-1975, Hebrew Wikisource consolidation (`law/il_vat.txt`; verbatim but not the
official publisher: **grade B** for every value):
* s. 2: VAT "בשיעור אחד ממחיר העסקה … כפי שקבע שר האוצר בצו"; the Wikisource note to s. 2 gives the order (VAT
  Order (Rate of Tax on a Transaction and on Import of Goods) 5765-2005 as amended): "שיעור המס על עסקה בישראל … יהיה
  18% ממחיר העסקה" (from 1 January 2025).
* s. 1 "עוסק פטור": turnover "אינו עולה על 120,000 שקלים חדשים לשנה (מתואם לשנת 2025)": no VAT below it.
* s. 31(1) exempt: residential leases up to 25 years ("השכרה למגורים"). s. 30(a)(13) zero rate: unprocessed fruit and
  vegetables of the kinds the Minister sets (not applied to the basket's `food`: flagged).
* s. 4: non-profit bodies and financial institutions pay wage (and profit) tax instead of VAT on their outputs: the
  basket's `financial` is exempt here; the wage tax is OECD 3000 (P4).
* Purchase Tax (Goods and Services) Law 5712-1952 and Fuel Excise Law 5718-1958 (`law/il_pt.txt`, `law/il_fuel.txt`):
  the amounts are set by orders not in these texts: not computed.
-/

namespace IlGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "מס ערך מוסף", standard := 1800, threshold := 120000,
    classOf := fun g => match g with
      | .rent | .financial => .exempt
      | _ => .standard }

def consumption : Family :=
  { name := "5111 מס ערך מוסף", covers := [.vat],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [vat.basketCharge g.consumption "VAT Law s. 2 and the 2005 rate order (18 %); s. 31(1); s. 4"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [vat.businessCharge g.company "VAT Law s. 1 (exempt dealer, 120,000 ₪ for 2025), s. 2"] else []) }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then ["VAT: zero rate on unprocessed fruit and vegetables (s. 30(a)(13)) not applied to food"] else [])
  ++ (if g.consumption.any (fun s => s.good == .education || s.good == .health) then ["education and health from non-profit bodies bear no VAT (s. 4); taxed at 18 % here"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) then
    ["purchase tax and fuel excise: amounts in orders not read; not computed"] else [])

#guard vat.embedded { good := .food, amount := 11800 } == 1800
#guard vat.embedded { good := .rent, amount := 11800 } == 0
#guard vat.net { turnover := 120000, sales := [{ good := .other, net := 120000 }] } == 0

end IlGlobal
