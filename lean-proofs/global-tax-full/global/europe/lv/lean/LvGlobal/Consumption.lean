import LvGlobal.Pit

/-!
# Latvia 2025: pievienotās vērtības nodoklis (5111) and akcīzes nodoklis (5121)

Sources: likumi.lv (official publisher Latvijas Vēstnesis), "Redakcija uz" 01.07.2025 (`lv/law/pvn_2025-07-01.html`,
`lv/law/akcizes_2025-07-01.html`; the current versions `pvn.html`, `akcizes.html` saved beside them show the later
rates, e.g. spirits 2276 instead of 2115 euro; sha256 in `law/SHA256SUMS`).
* **PVN likums 41. pants (1)**: "1) nodokļa standartlikmi 21 procenta apmērā ... 2) nodokļa samazināto likmi saskaņā ar
  šā likuma 42. pantu: a) 12 procentu apmērā, b) piecu procentu apmērā"; **42. pants**: 12 % (1) medicines, (4)
  "pasažieru un to bagāžas regulāro pārvadājumu pakalpojumiem iekšzemē", (10) "izmitināšanas pakalpojumiem tūristu
  mītnēs"; 5 % (5) books, (7) press. **59. pants (1)**: no registration while supplies in the calendar year have "nav
  pārsniegusi 50 000" euro.
* **Likums "Par akcīzes nodokli" 12. pants (1)** (2025-07-01): "1) alum (par 100 litriem) — 11,3 euro par katru
  absolūtā spirta tilpumprocentu ..., bet ne mazāk kā 22,5 euro par 100 litriem alus"; "3) raudzētajiem dzērieniem (par
  100 litriem): a) ... līdz 6 tilpumprocentiem (ieskaitot) — 89 euro, b) ... virs 6 tilpumprocentiem — 155 euro";
  "5) pārējiem alkoholiskajiem dzērieniem (par 100 litriem absolūtā spirta) — 2115 euro". **13. pants**: cigarettes
  "a) 159,3 euro par 1000 cigaretēm, b) 15 procenti no maksimālās mazumtirdzniecības cenas"; (1¹) not less than "208
  euro par 1000 cigaretēm". **14. pants (1)**: "1) svinu nesaturošam benzīnam ... (par 1000 litriem) — 555 euro";
  "4) dīzeļdegvielai (gāzeļļai) ... (par 1000 litriem) — 467 euro".

## FT review (2026-11-21, second pass): fuel rates for 2025 (pārejas noteikumi)
Same likumi.lv version at 2025-07-01 (`lv/law/akcizes_2025-07-01.txt`). The 14. pants (1) rates the model used (555,
467 euro) apply from 2026-01-01; for 2025 the transitional provisions set lower rates:
* **p. 174**: unleaded petrol "no 2025. gada 1. janvāra līdz 2025. gada 31. decembrim apliek ar nodokli — 532 euro par
  1000 litriem" (p. 173: the 14. pants (1) 1) rate applies from 2026-01-01).
* **p. 180**: diesel (gāzeļļa) "no 2025. gada 1. janvāra līdz 2025. gada 31. decembrim apliek ar nodokli — 440,5 euro"
  per 1000 litres (p. 179: the 467 euro of 14. pants (1) 4) and 6) from 2026-01-01).
* **14. pants (2³)** marked (iezīmēti) oil products of (1) 3), 4), 6): 324 euro per 1000 litres, applied from 2026-01-01
  (p. 168); **p. 169 2)**: "no 2025. gada 1. janvāra līdz 2025. gada 31. decembrim — 236 euro par 1000 litriem". The
  household's `heatingOil` is read as marked gas oil under (2³).
-/

namespace LvGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Pievienotās vērtības nodoklis", standard := 2100, reduced := 1200, superReduced := 500, threshold := 50000,
    classOf := fun gd => match gd with
      | .medicines | .transport | .hotels => .reduced
      | .books | .newspapers => .superReduced
      | .health | .education | .insurance | .financial | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "PVN likums 41. pants (1) (21 %, 12 %, 5 %), 42. pants (1), (4), (5), (7), (10); 52. pants (exempt); 59. pants (1) (50 000 euro)"

def excise : Excise :=
  { rates := [
      { good := .petrol, name := "Akcīzes nodoklis (benzīns)", perUnitNum := 532, perUnitDen := 1000, statute := "Par akcīzes nodokli pārejas noteikumi 174. punkts (2025): 532 euro / 1000 l (14. pants (1) 1) 555 euro from 2026)" },
      { good := .diesel, name := "Akcīzes nodoklis (dīzeļdegviela)", perUnitNum := 4405, perUnitDen := 10000, statute := "Par akcīzes nodokli pārejas noteikumi 180. punkts (2025): 440,5 euro / 1000 l (14. pants (1) 4) 467 euro from 2026)" },
      { good := .cigarettes, name := "Akcīzes nodoklis (cigaretes)", perUnitNum := 1593, perUnitDen := 10000, adValoremBp := 1500, minNum := 208, minDen := 1000, statute := "Par akcīzes nodokli 13. pants (1) 2), (1¹): 159,3 euro / 1000 + 15 % of the maximum retail price, at least 208 euro / 1000" },
      { good := .beer, name := "Akcīzes nodoklis (alus)", perUnitNum := 113, perUnitDen := 10, onPureAlcohol := true, minNum := 225, minDen := 1000, statute := "Par akcīzes nodokli 12. pants (1) 1): 11,3 euro per % vol per 100 l, at least 22,5 euro / 100 l" },
      { good := .wine, name := "Akcīzes nodoklis (raudzētie dzērieni)", perUnitNum := 155, perUnitDen := 100, statute := "Par akcīzes nodokli 12. pants (1) 3) b): 155 euro / 100 l (over 6 % vol)" },
      { good := .spirits, name := "Akcīzes nodoklis (pārējie alkoholiskie dzērieni)", perUnitNum := 2115, perUnitDen := 100, onPureAlcohol := true, statute := "Par akcīzes nodokli 12. pants (1) 5): 2115 euro / 100 l absolūtā spirta" },
      { good := .heatingOil, name := "Akcīzes nodoklis (iezīmēta gāzeļļa apkurei)", perUnitNum := 236, perUnitDen := 1000, statute := "Par akcīzes nodokli 14. pants (2³); pārejas noteikumi 169. punkts 2) (2025): 236 euro / 1000 l" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 PVN, 5121 akcīzes nodoklis", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["LV 5111/5121: likumi.lv versions at 2025-07-01"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["food at 21 %; fresh fruit, berries and vegetables are 5 % (42. pants) and infant food 12 %: not separated"] else [])
  ++ (if g.consumption.any (fun s => s.good == .wine) then ["wine taken as a fermented beverage over 6 % vol (≤ 6 %: 89 euro / 100 l)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies (52. pants) taken from the act's structure, not quoted item by item"] else [])

#guard vat.embedded { good := .clothing, amount := 121 } == 21
#guard vat.embedded { good := .hotels, amount := 112 } == 12
#guard vat.embedded { good := .books, amount := 105 } == 5
#guard vat.net { turnover := 50000, sales := [{ good := .other, net := 50000 }] } == 0
#guard excise.duty { good := .cigarettes, amount := 200, quantity := 1000000 } == 208
#guard excise.duty { good := .cigarettes, amount := 400, quantity := 1000000 } == 159 + 60
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 56
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 100 } == 22
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 155
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 846
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 532
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 440
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 236

end LvGlobal.Consumption
