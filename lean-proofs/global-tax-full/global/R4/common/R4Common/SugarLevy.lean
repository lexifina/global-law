import R4Common.ProfitLevy
import TaxKernel.Global2.Basket

/-! # R4Common: a levy per gram of sugar above a threshold content (thirteenth pass, P7 "high" item).

ZA Health Promotion Levy on sugary beverages (Customs and Excise Act Schedule 1 Part 7 Section A, Rates and Monetary
Amounts Act 14 of 2017): 2,1 cents a gram on sugar above 4 g per 100 ml; nothing on the first
4 g per 100 ml. Charged per basket line of the good that carries `"sugarMg100ml"` (kernel 2.1 `SpendX`, mg per 100 ml)
and a `quantity` (thousandths of a litre):

    grams above the threshold = quantity / 1000 (litres) × (sugarMg100ml − thrMg) / 100 (g per litre)
    levy (whole currency units) = grams × num / den cents / 100, rounded down once
                                = quantity × (sugarMg100ml − thrMg) × num / (10^7 × den)

A line without a sugar content (`sugarMg100ml` absent or 0) gets no charge (not computed; the statute's deemed 20 g per
100 ml applies to imports and products without a certified test report, which the input cannot tell). The levy is
borne in the price like an excise (bearer: the entity); `covers` is empty so the heading 5121 keeps its own coverage. -/

namespace R4
open TaxKernel TaxKernel.Global

def sugarLevyAmount (quantity sugarMg thrMg num den : Int) : Int :=
  divR .down (pos quantity * pos (sugarMg - thrMg) * num) (10000000 * den)

def sugarLevyFamily (name : String) (good : Good) (thrMg num den : Int) (statute : String)
    (oecd : Oecd := .excise) : Family :=
  { name := s!"{oecd.code} {name}", covers := [],
    run := fun _ g _ =>
      ((consumptionX g).zipIdx.filter (fun (sx, _) => sx.1.good == good && decide (sx.2.sugarMg100ml > 0))).map
        fun (sx, i) =>
          charge oecd name sx.1.quantity id (fun q => sugarLevyAmount q sx.2.sugarMg100ml thrMg num den)
            (event := s!"consumption {i + 1}") (statute := statute) }

-- 100 litres at 10 g / 100 ml: 6 000 g above 4 g / 100 ml, 2,1 c per gram = R126
#guard sugarLevyAmount 100000 10000 4000 21 10 == 126
#guard sugarLevyAmount 100000 4000 4000 21 10 == 0
#guard sugarLevyAmount 100000 3000 4000 21 10 == 0

def tSL : CanonGlobal :=
  { id := "h", household := { id := "h" },
    consumption := [{ good := .nonAlcoholic, amount := 2000, quantity := 100000 }, { good := .food, amount := 500 },
                    { good := .nonAlcoholic, amount := 900, quantity := 50000 }],
    raw := (Lean.Json.parse "{\"consumption\": [{\"sugarMg100ml\": 10000}, {}, {}]}").toOption.getD Lean.Json.null }
#guard ((sugarLevyFamily "t" .nonAlcoholic 4000 21 10 "s").run [] tSL []).map (·.due) == [126]
#guard ((sugarLevyFamily "t" .nonAlcoholic 4000 21 10 "s").run [] tSL []).map (·.event) == ["consumption 1"]

end R4
