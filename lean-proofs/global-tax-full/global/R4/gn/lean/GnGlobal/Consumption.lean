import R4Common

/-!
# Guinea 2025: VAT (5111) and excises (5121) (generated from `R4/specs/gn.json` by `R4/tools/gen_country.py`)

Sources: CGI 2021 (`cmp20/world/B07-west-africa-fr-pt/gn/src/cgi2021.txt`), Loi 2024-23 (LF) OCR.

art. 373: "Le taux de droit commun de la Taxe sur la Valeur Ajoutée est de dix-huit pourcent (18%). II. Toutefois … sont imposables au taux de zéro pourcent (0%)" (exports). Exemptions not read.

art. 435 I (layout extraction): "a. Produits du tabac et produits du vapotage 35% b. Bières et boissons maltées (Malta) 12% c. Vins 12% d. Spiritueux 15% e. Boissons alcoolisées autres que les bières, boissons maltées, vins et spiritueux 30% f. jus de fruit ... 0% g. eau ... et autres boissons non alcooliques ... 0% h. Boissons énergisantes 0%"; II: "Les tarifs des droits d'accises sur les produits imposables importés sont fixés dans le TARIF DES DOUANES" (not held). Art. 436 III: "La base d'imposition des produits fabriqués en Guinée soumis à un droit d'accise ad valorem est le prix de vente ex-usine hors TVA".
-/

namespace GnGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1800, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "CGI art. 373 (18 %)"

-- the standard rate as printed: 18 % inside a tax-inclusive 11800
#guard vatX.embedded { good := .other, amount := 11800 } == 1800
def accises : List R4.Exc :=
  [ { good := .beer, name := "Droit d'accise bières", advBp := 1200, vatBp := 1800, imported := some false, statute := "CGI art. 435 I b (12 %)" },
    { good := .wine, name := "Droit d'accise vins", advBp := 1200, vatBp := 1800, imported := some false, statute := "CGI art. 435 I c (12 %)" },
    { good := .spirits, name := "Droit d'accise spiritueux", advBp := 1500, vatBp := 1800, imported := some false, statute := "CGI art. 435 I d (15 %)" },
    { good := .cigarettes, name := "Droit d'accise produits du tabac", advBp := 3500, vatBp := 1800, imported := some false, statute := "CGI art. 435 I a (35 %)" } ]
def excise : Family := R4.exciseFamily "Droits d'accises (produits fabriqués en Guinée)" accises
-- CGI art. 435 I b (12 %): 10000 paid for 1 unit(s) at 5 % vol → 907
#guard (R4.exciseCharges [{ good := .beer, name := "Droit d'accise bières", advBp := 1200, vatBp := 1800, imported := some false, statute := "CGI art. 435 I b (12 %)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [907]
-- CGI art. 435 I c (12 %): 10000 paid for 1 unit(s) at 12 % vol → 907
#guard (R4.exciseCharges [{ good := .wine, name := "Droit d'accise vins", advBp := 1200, vatBp := 1800, imported := some false, statute := "CGI art. 435 I c (12 %)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [907]
-- CGI art. 435 I d (15 %): 10000 paid for 1 unit(s) at 40 % vol → 1105
#guard (R4.exciseCharges [{ good := .spirits, name := "Droit d'accise spiritueux", advBp := 1500, vatBp := 1800, imported := some false, statute := "CGI art. 435 I d (15 %)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [1105]
-- CGI art. 435 I a (35 %): 10000 paid for 1 unit(s) at 0 % vol → 2196
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Droit d'accise produits du tabac", advBp := 3500, vatBp := 1800, imported := some false, statute := "CGI art. 435 I a (35 %)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [2196]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["Guinea: CGI 2021 (LF 2025 not held); VAT exemptions not read", "CGI art. 435 II: imported goods bear the customs tariff's excise rates (not held): only locally made goods are charged here; soft drinks, water and juices are at 0 % (art. 435 I f-h)"]

end GnGlobal
