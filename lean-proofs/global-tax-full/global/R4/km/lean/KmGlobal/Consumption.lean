import R4Common

/-!
# Comoros 2025: VAT (5111) and excises (5121) (generated from `R4/specs/km.json` by `R4/tools/gen_country.py`)

Sources: Code général des impôts 2022 (`cmp20/world/B08-central-africa-fr/km/law/cgi2022.txt`), LF 2024 OCR pages 1-60.

art. 152 (layout extraction): "Le taux de la taxe sur la consommation est fixé à 10 %. Par exception, la taxe sur la consommation est prélevée au taux de : 0 % à l'importation et à l'intérieur pour les produits de première nécessité défini par arrêté du Ministre des Finances et du Budget ; 3 % pour la fourniture d'eau et d'électricité ainsi que pour la vente des titres de transport inter-îles ; 5 % pour la restauration, les activités bancaires et le téléphone fixe ; 7,5 % pour la fourniture des recharges mobile en voix et en Data ; 5 % pour les titres de transport à l'international ; 25 % pour les activités des casinos". The Comoros levy this tax instead of a VAT. Grade B: CGI 2022 edition; LF 2024 pages 1-60 held (no change to art. 152 found); LF 2025 not held.

art. 157: "La taxe intérieure sur les alcools et tabacs est fixée à 10 % du prix de vente appliqué par le fabricant ou l'importateur"; art. 153: "La taxe intérieure sur les produits pétroliers (TIPP) est fixée comme suit : taux normal : 230 FC par litre d'essence ; 115 FC par litre de Gas-oil. taux réduit : 211 FC ... 95 FC ..."; LF 2018 art. 19: "un Droit d'Accise de 25 FC le litre sur les boissons sucrées". The LF 2016 cigarette surtax (12 300 FC per 1 000) applies "dès la création du fonds de couverture maladie universelle" (date not established): not applied.
-/

namespace KmGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la consommation", standard := 1000, reduced := 500, reduced2 := 300,
    threshold := 0,
    classOf := fun gd => match gd with
      | .restaurants | .financial => .reduced
      | .water | .electricity => .reduced2
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "CGI 2022 art. 152 (L.F. 2018, 2019, 2020, L.F.R. 2020): 10 %; 5 % restaurants and banking; 3 % water and electricity"

-- the standard rate as printed: 10 % inside a tax-inclusive 11000
#guard vatX.embedded { good := .other, amount := 11000 } == 1000
#guard vatX.embedded { good := .restaurants, amount := 10500 } == 500
#guard vatX.embedded { good := .financial, amount := 10500 } == 500
#guard vatX.embedded { good := .water, amount := 10300 } == 300
def accises : List R4.Exc :=
  [ { good := .beer, name := "Taxe intérieure sur les alcools (bière)", advBp := 1000, vatBp := 1000, statute := "CGI art. 157 (10 %)" },
    { good := .wine, name := "Taxe intérieure sur les alcools (vin)", advBp := 1000, vatBp := 1000, statute := "CGI art. 157 (10 %)" },
    { good := .spirits, name := "Taxe intérieure sur les alcools (spiritueux)", advBp := 1000, vatBp := 1000, statute := "CGI art. 157 (10 %)" },
    { good := .cigarettes, name := "Taxe intérieure sur les tabacs", advBp := 1000, vatBp := 1000, statute := "CGI art. 157 (10 %)" },
    { good := .petrol, name := "TIPP essence", perUnitNum := 230000, perUnitDen := 1000, vatBp := 1000, statute := "CGI art. 153 (230 FC per litre, taux normal)" },
    { good := .diesel, name := "TIPP gas-oil", perUnitNum := 115000, perUnitDen := 1000, vatBp := 1000, statute := "CGI art. 153 (115 FC per litre, taux normal)" },
    { good := .nonAlcoholic, name := "Droit d'accise sur les boissons sucrées", perUnitNum := 25000, perUnitDen := 1000, vatBp := 1000, statute := "LF 2018 art. 19 (25 FC per litre)" } ]
def excise : Family := R4.exciseFamily "Taxes intérieures (alcools, tabacs, produits pétroliers, boissons sucrées)" accises
-- CGI art. 157 (10 %): 10000 paid for 1 unit(s) at 5 % vol → 826
#guard (R4.exciseCharges [{ good := .beer, name := "Taxe intérieure sur les alcools (bière)", advBp := 1000, vatBp := 1000, statute := "CGI art. 157 (10 %)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [826]
-- CGI art. 157 (10 %): 10000 paid for 1 unit(s) at 12 % vol → 826
#guard (R4.exciseCharges [{ good := .wine, name := "Taxe intérieure sur les alcools (vin)", advBp := 1000, vatBp := 1000, statute := "CGI art. 157 (10 %)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [826]
-- CGI art. 157 (10 %): 10000 paid for 1 unit(s) at 40 % vol → 826
#guard (R4.exciseCharges [{ good := .spirits, name := "Taxe intérieure sur les alcools (spiritueux)", advBp := 1000, vatBp := 1000, statute := "CGI art. 157 (10 %)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [826]
-- CGI art. 157 (10 %): 10000 paid for 1 unit(s) at 0 % vol → 826
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Taxe intérieure sur les tabacs", advBp := 1000, vatBp := 1000, statute := "CGI art. 157 (10 %)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [826]
-- CGI art. 153 (230 FC per litre, taux normal): 10000 paid for 1 unit(s) at 0 % vol → 230
#guard (R4.exciseCharges [{ good := .petrol, name := "TIPP essence", perUnitNum := 230000, perUnitDen := 1000, vatBp := 1000, statute := "CGI art. 153 (230 FC per litre, taux normal)" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [230]
-- CGI art. 153 (115 FC per litre, taux normal): 10000 paid for 1 unit(s) at 0 % vol → 115
#guard (R4.exciseCharges [{ good := .diesel, name := "TIPP gas-oil", perUnitNum := 115000, perUnitDen := 1000, vatBp := 1000, statute := "CGI art. 153 (115 FC per litre, taux normal)" }] [{ good := .diesel, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [115]
-- LF 2018 art. 19 (25 FC per litre): 10000 paid for 1 unit(s) at 0 % vol → 25
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Droit d'accise sur les boissons sucrées", perUnitNum := 25000, perUnitDen := 1000, vatBp := 1000, statute := "LF 2018 art. 19 (25 FC per litre)" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [25]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["art. 152: 0 % on basic necessities listed by order (not held), 3 % inter-island and 5 % international transport tickets, 5 % fixed phone and 7,5 % mobile recharges are not separable from the basket lines (standard rate)", "art. 140: businesses with turnover below 20 000 000 FC are not liable (not applied)", "LF 2016 cigarette surtax 12 300 FC per 1 000 not applied (effective on creation of the CMU fund, date not established); TIPP reduced rates for beneficiaries set by regulation not applied; the sugary-drinks duty is applied to the whole non-alcoholic line (plain water not separable)"]

end KmGlobal
