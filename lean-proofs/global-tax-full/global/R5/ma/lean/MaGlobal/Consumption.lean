import TaxKernel.Global2
import R5Common

/-!
# Morocco 2025: TVA (5111); TIC on cigarettes (5121)

Source: Code général des impôts, DGI edition 2025 (with LF n° 60-24 for 2025; `world/B06-mena/ma/law/cgi2025fr.pdf`,
linked as `law/cgi2025fr.txt`):
* art. 99 (LF 55-23): "A.- 20 %"; "B.- 10 %" 1° with deduction: hotels and restaurants, cafés; refined petroleum oils
  ("les huiles de pétrole … brutes ou raffinées"); petroleum gas; banking and credit operations; water for public
  networks (applicable from 1 January 2024, art. 247-XXXXI-A).
* art. 247-XXXXI transitional rates for 2025: B electricity 18 % "à compter du 1er janvier 2025"; G urban transport
  and road transport of passengers 12 % "à compter du 1er janvier 2025".
* art. 91 exemptions without deduction used: I-A 1° bread, flour, 2° milk, 6° meat (the basket's `food` is taken as
  exempt and flagged); journals, publications and books; private education services.
* Taxes intérieures de consommation, Dahir portant loi 1-77-340 art. 9, tableau G (cigarettes) as scheduled by LF 76-21
  (2022) for its fourth year, 1 January 2025; restated in Annex V of the customs circular 6619/210 of 26/12/2024 on
  LF 60-24 (`law/adii_circ6619-210_20241226_lf2025.pdf`, douane.gov.ma copy archived 2024-12-27): "Cigarettes … 400
  dirhams les 1000 cigarettes | 61% [du prix de vente public hors TVA et TIC spécifique] | 900,9 dirhams les 1000
  cigarettes [minimum de perception]". With `P` the retail price net of TVA (20 %) and `q` sticks:
  TIC = max (0,4 q + 0,61 (P − 0,4 q), 0,9009 q) = max (0,156 q + 0,61 P, 0,9009 q): the kernel rule carries the
  identity (specific 156 per 1000 on top of 61 % of the price net of TVA; guard below checks it against the statute's
  form). Other TIC tables (beverages other than tableau L, alcohol, fuels) not read for 2025: not computed.
* **Tableau L (pass 3r)**, same circular, section VIII.2 and Annex V (pp. 42-43): LF 55-23 set a TIC on products
  containing added sugar in two yearly steps from 1/1/2024; the second step "à compter du 1er Janvier 2025" restates
  tableau L by "teneur en sucre ajouté en grammes (pour 100 g ou 100 ml)", quotité per 100 kg. Drinks modelled (line
  `sub` and `sugarMg100ml`; the unit is 100 kg, **one litre taken as one kg**, the density is not in the text): item 6
  "Boissons préparées à base d'eau contenant 10% ou plus de jus de fruits" plus de 7 g: **37,5 DH** (`sub`
  `"juiceDrinks"`); item 4 "Boissons au lait" plus de 8 g: **120 DH** (`"milkDrinks"`), "Lait aromatisé" plus de 8,5 g:
  **120 DH** (`"flavouredMilk"`); item 11 "Sirops" plus de 49 g: **450 DH** (`"syrups"`). "Plus de" = strictly more
  (bands from 7 001, 8 001, 8 501, 49 001 mg). Foods of tableau L (biscuits, confectionery, chocolate, dairy desserts,
  jam, cereals, ...) are not basket goods: not computed. Sodas without juice are not in tableau L (their own TIC not read).
-/

namespace MaGlobal
open TaxKernel TaxKernel.Global R5Common

def tva : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 2000, reduced := 1000, reduced2 := 1800, superReduced := 1200,
    classOf := fun g => match g with
      | .restaurants | .hotels | .petrol | .diesel | .heatingOil | .gas | .financial | .water => .reduced
      | .electricity => .reduced2
      | .transport => .superReduced
      | .food | .books | .newspapers | .education => .exempt
      | _ => .standard }

/-- Tableau G, cigarettes: `0,4 q + 0,61 (P − 0,4 q)` written as `0,156 q + 0,61 P` (`P` net of TVA), minimum 0,9009 q. -/
def ticCigarettes : ExciseRule :=
  { good := .cigarettes, name := "Taxe intérieure de consommation (tabacs manufacturés)", perUnitNum := 156, perUnitDen := 1000,
    adValoremBp := 6100, valueBase := .netOfVat, vatBp := 2000, minNum := 9009, minDen := 10000,
    statute := "Dahir 1-77-340 art. 9 tableau G (LF 76-21, 4th year, 1/1/2025): 400 DH/1000 + 61 % of the price net of TVA and specific TIC, minimum 900,9 DH/1000" }

/-- Tableau L (circular 6619/210 Annex V, 1/1/2025): DH per 100 kg read as per 100 l: `(from mg/100 ml, num, den)` per litre. -/
def ticSucre : List ExciseRule :=
  [ { good := .nonAlcoholic, sub := "juiceDrinks", name := "TIC produits contenant du sucre (boissons à base de jus)", sugarBands := [(7001, 3, 8)],
      statute := "Dahir 1-77-340 art. 9 tableau L (LF 55-23, 2nd step 1/1/2025; circular 6619/210 Annex V item 6): plus de 7 g/100 ml, 37,5 DH/100 kg" },
    { good := .nonAlcoholic, sub := "milkDrinks", name := "TIC produits contenant du sucre (boissons au lait)", sugarBands := [(8001, 6, 5)],
      statute := "Dahir 1-77-340 art. 9 tableau L (circular 6619/210 Annex V item 4): boissons au lait plus de 8 g/100 ml, 120 DH/100 kg" },
    { good := .nonAlcoholic, sub := "flavouredMilk", name := "TIC produits contenant du sucre (lait aromatisé)", sugarBands := [(8501, 6, 5)],
      statute := "Dahir 1-77-340 art. 9 tableau L (circular 6619/210 Annex V item 4): lait aromatisé plus de 8,5 g/100 ml, 120 DH/100 kg" },
    { good := .nonAlcoholic, sub := "syrups", name := "TIC produits contenant du sucre (sirops)", sugarBands := [(49001, 9, 2)],
      statute := "Dahir 1-77-340 art. 9 tableau L (circular 6619/210 Annex V item 11): sirops plus de 49 g/100 ml, 450 DH/100 kg" } ]

def ticSucreSubs : List String := ["juiceDrinks", "milkDrinks", "flavouredMilk", "syrups"]

/-- The statute's form, for the guard. -/
def ticStatute (netPrice q : Int) : Int := max (divR .down (400 * q) 1000 + divR .down (6100 * (netPrice - divR .down (400 * q) 1000)) BP) (divR .down (9009 * q) 10000)

def consumption : Family :=
  { name := "5111 TVA, 5121 TIC", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [tva.basketCharge g.consumption "CGI art. 99 A (20 %), B (10 %); art. 247-XXXXI B (18 %), G (12 %) for 2025; art. 91"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then [tva.businessCharge g.company "CGI art. 99, 101-104 (deduction, prorata)"] else [])
      ++ exciseRuleCharges [ticCigarettes] g
      ++ exciseRuleCharges ticSucre g }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then ["TVA: food taken as exempt (bread, flour, milk, meat: art. 91); oils, rice, pasta are 10 %, processed foods 20 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .medicines || s.good == .health) then ["TVA on medicines and health services (art. 91, 99) not read: taxed at 20 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel || s.good == .tobaccoOther) then
    ["taxes intérieures de consommation other than on cigarettes and tableau L drinks (Dahir 1-77-340 art. 9 tables for alcohol, fuels, other tobacco): 2025 quotités not read; not computed"] else [])
  ++ (if (consumptionX g).any (fun (s, x) => s.good == .nonAlcoholic && !(ticSucreSubs.contains x.sub)) then
    ["TIC on non-alcoholic drinks: only tableau L drinks (sub juiceDrinks, milkDrinks, flavouredMilk, syrups) are computed; sodas and other drinks (their own TIC table not read) are not"] else [])
  ++ (if (consumptionX g).any (fun (s, x) => s.good == .nonAlcoholic && ticSucreSubs.contains x.sub && (x.sugarMg100ml ≤ 0 || s.quantity ≤ 0)) then
    ["TIC tableau L: a drink line without sugarMg100ml or quantity (litres) is not taxed"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes && s.quantity <= 0) then
    ["TIC cigarettes: line without quantity (sticks): specific part and minimum not applied"] else [])

#guard tva.embedded { good := .clothing, amount := 12000 } == 2000
-- 2,000 cigarettes (quantity in thousandths: 2,000,000) sold 6,000 DH: net of TVA 5,000; statute 800 + 0,61 × 4,200
#guard ticCigarettes.dutyOn { good := .cigarettes, amount := 6000, quantity := 2000000 } {} == ticStatute 5000 2000
#guard ticStatute 5000 2000 == 3362
-- sold 2,000 DH: 312 + 1,016 < the minimum 0,9009 × 2,000 = 1,801
#guard ticCigarettes.dutyOn { good := .cigarettes, amount := 2000, quantity := 2000000 } {} == 1801
#guard tva.embedded { good := .restaurants, amount := 11000 } == 1000
#guard tva.embedded { good := .electricity, amount := 11800 } == 1800
#guard tva.embedded { good := .transport, amount := 11200 } == 1200

-- tableau L: 2 l of a juice drink with 9 g/100 ml: 2 x 0,375 = 0,75 -> 0 (down); 100 l: 37
#guard (ticSucre.getD 0 default).dutyOn { good := .nonAlcoholic, amount := 1000, quantity := 100000 } { sub := "juiceDrinks", sugarMg100ml := 9000 } == 37
#guard (ticSucre.getD 0 default).dutyOn { good := .nonAlcoholic, amount := 1000, quantity := 100000 } { sub := "juiceDrinks", sugarMg100ml := 7000 } == 0
#guard (ticSucre.getD 3 default).dutyOn { good := .nonAlcoholic, amount := 1000, quantity := 10000 } { sub := "syrups", sugarMg100ml := 60000 } == 45

end MaGlobal
