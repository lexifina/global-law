import TaxKernel.Global
import R5Common

/-!
# Cyprus 2025: VAT (ΦΠΑ, 5111) and excise (ειδικός φόρος κατανάλωσης, 5121)

Sources: cylaw.org consolidated texts (archived copies fetched by the registry agent; `law/cy_vat.html.txt`,
`law/cy_exc.html.txt`, sha256 in `law/SHA256SUMS`). Year-in-force audit (pass 3q): `cy_vat.html.txt` is a 2026
consolidation (amending acts to ΚΔΠ 103/2026). Checked against the cylaw capture of 05/12/2024 (Wayback; amending acts
to 167(Ι)/2024) and the 2025 orders (ΚΔΠ 159/2025 Thirteenth, 205/2025 and 364/2025 Fifth, 278/2025 Seventh Schedule;
337/2025 Fifth Schedule zero rate from 1/1/2026; Law 104(Ι)/2025 art. 2 definitions, from 1/1/2025): the rates and the
schedule items used are the 2025 ones, except household electricity (below). Excise: amending acts end at 16(Ι)/2024
(cylaw capture of 22/01/2026), so the text governs all of 2025. Amounts in euros.
* VAT Law 95(Ι)/2000 art. 17: "δεκαεννέα τοις εκατό (19%) από 13 Ιανουαρίου 2014".
  art. 18 / Fifth Schedule (5 %): Part I 4 water, 7 food and drinks for human consumption except alcoholic drinks,
  8 liquefied gas; Part II 4 urban and rural buses, 9 medical and dental services not exempt.
  art. 18Α / Twelfth Schedule (9 %): (1) taxis, (2) restaurant and catering services, (3) hotel accommodation,
  Household electricity (item (6), domestic tariffs 01/02/08/56) is absent from the schedule on 05/12/2024 and no 2025
  order adds it; it returns only for meter readings from 1/4/2026 to 31/3/2027 (ΚΔΠ 82/2026): 19 % in 2025.
  art. 18Β / Fifteenth Schedule (3 %): Table A 1 books, newspapers and periodicals.
  Seventh Schedule (exempt): Part I 2-3 hospital and medical care, 9-10 education; Part II 1 insurance, 3 financial
  services; leasing of immovable property exempt unless the lessor opts to tax.
  First Schedule Part II: registration not required when annual turnover "δεν υπερβαίνει … (€15.600)".
* Excise Duties Law 91(Ι)/2004, Second Schedule: 1 ethyl alcohol €956,82 per 100 litres of anhydrous alcohol;
  2(β) beer €6,00 per 100 litres per degree of alcohol (brewery not small); 3-4 wine €0. Third Schedule: 1 cigarettes
  "€1,10 τα 20 τσιγάρα και 34% επί της ανώτερης τιμής λιανικής πώλησης", minimum "€2,43 τα 20 τσιγάρα".
  First Schedule (energy): unleaded petrol (2710 12 41/45/49) €429,00 per 1 000 litres; gas oil as motor fuel
  €400,00 per 1 000 litres (the temporary reductions of the provisos ended on 31 March 2024).
  FT review (2026-11-21, third pass): First Schedule item 7, gas oil "το οποίο χρησιμοποιείται ως καύσιμο θέρμανσης"
  (note (2): fuel for central heating or other heating of persons in dwellings ...) €74,73 per 1 000 litres (its
  €21,00 provisos ended on 31 March 2024). The household's `heatingOil` is read as such gas oil.
-/

namespace CyGlobal
open TaxKernel TaxKernel.Global R5Common

def fpa : Vat :=
  { name := "Φόρος Προστιθέμενης Αξίας (ΦΠΑ)", standard := 1900, reduced := 900, reduced2 := 500, superReduced := 300,
    threshold := 15600,
    classOf := fun g => match g with
      | .restaurants | .hotels => .reduced
      | .food | .nonAlcoholic | .water | .gas | .transport => .reduced2
      | .books | .newspapers => .superReduced
      | .health | .education | .insurance | .financial | .rent => .exempt
      | _ => .standard }

def efk : Excise :=
  { rates := [
      { good := .spirits, name := "Ειδικός φόρος κατανάλωσης", perUnitNum := 95682, perUnitDen := 10000, onPureAlcohol := true,
        statute := "Law 91(Ι)/2004 Second Schedule 1 (€956,82 per 100 l of anhydrous alcohol)" },
      { good := .beer, name := "Ειδικός φόρος κατανάλωσης", perUnitNum := 6, onPureAlcohol := true,
        statute := "Law 91(Ι)/2004 Second Schedule 2(β) (€6 per 100 l per degree = €6 per litre of alcohol)" },
      { good := .cigarettes, name := "Ειδικός φόρος κατανάλωσης", perUnitNum := 110, perUnitDen := 2000, adValoremBp := 3400,
        minNum := 243, minDen := 2000,
        statute := "Law 91(Ι)/2004 Third Schedule 1 (€1,10 per 20 + 34 % of the maximum retail price; minimum €2,43 per 20)" },
      { good := .petrol, name := "Ειδικός φόρος κατανάλωσης", perUnitNum := 429, perUnitDen := 1000,
        statute := "Law 91(Ι)/2004 First Schedule (unleaded petrol €429 per 1 000 l)" },
      { good := .diesel, name := "Ειδικός φόρος κατανάλωσης", perUnitNum := 400, perUnitDen := 1000,
        statute := "Law 91(Ι)/2004 First Schedule (gas oil as motor fuel €400 per 1 000 l)" },
      -- FT review (2026-11-21, third pass): First Schedule item 7 (heating gas oil)
      { good := .heatingOil, name := "Ειδικός φόρος κατανάλωσης", perUnitNum := 7473, perUnitDen := 100000,
        statute := "Law 91(Ι)/2004 First Schedule 7 (gas oil 2710 19 43-48, 2710 20 11-19 used as heating fuel, note (2): €74,73 per 1 000 l)" }] }

def consumption : Family :=
  { name := "5111 ΦΠΑ, 5121 ειδικοί φόροι κατανάλωσης", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [fpa.basketCharge g.consumption "VAT Law 95(Ι)/2000 art. 17 (19 %), 18 (5 %), 18Α (9 %), 18Β (3 %); Seventh Schedule"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [fpa.businessCharge g.company "VAT Law 95(Ι)/2000 art. 17, First Schedule (€15.600)"] else [])
      ++ efk.charges g.consumption }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .medicines) then ["medicines: no schedule entry found in the text read; taxed at 19 %"] else [])
  ++ (if g.consumption.any (·.good == .transport) then ["transport taken at 5 % (urban and rural buses); taxis are 9 %, other transport 19 %"] else [])
  ++ (if g.consumption.any (·.good == .tobaccoOther) then ["excise on cigars, fine-cut and heated tobacco (Third Schedule 2-5) is per kilogram: not computed"] else [])

#guard fpa.embedded { good := .other, amount := 11900 } == 1900
#guard fpa.embedded { good := .food, amount := 10500 } == 500
#guard fpa.embedded { good := .restaurants, amount := 10900 } == 900
#guard fpa.embedded { good := .books, amount := 10300 } == 300
#guard fpa.net { turnover := 15600, sales := [{ good := .other, net := 15600 }] } == 0
-- 1 litre of 40 % spirits: 0.4 l × 956.82/100 = 3.83 → 3
#guard efk.duty { good := .spirits, amount := 20, quantity := 1000, abvBp := 4000 } == 3
-- 20 packs of 20 at €5: fixed 22 + 34 % × 100 = 56 (minimum 48.6)
#guard efk.duty { good := .cigarettes, amount := 100, quantity := 400000 } == 56
-- cheap packs: 20 packs at €2.5: 22 + 17 = 39 < minimum 48
#guard efk.duty { good := .cigarettes, amount := 50, quantity := 400000 } == 48
#guard efk.duty { good := .petrol, amount := 1500, quantity := 1000000 } == 429
-- FT review (third pass): 1 000 l heating gas oil: €74,73 -> 74
#guard efk.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 74

end CyGlobal
