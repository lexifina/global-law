import R4Common

/-!
# Côte d'Ivoire 2025: VAT (5111) and excises (5121) (generated from `R4/specs/ci.json` by `R4/tools/gen_country.py`)

CGI 2025, DGI online edition (`https://cgici.com/V2025/page-N.html`, 711 pages fetched 2026-11-21 at 2 req/s; the dgi.gouv.ci menu entry 'Le code général des Impôts' points to cgici.com), concatenated text `cmp20/global/R4/fetch/ci8/cgi2025_cgici.txt` (+ v2025.tgz, SHA256SUMS). The online pages also show superseded versions of some articles; the version headed by the latest year marker is used.

art. 359: "Pour la détermination de la taxe sur la valeur ajoutée, telle que prévue par le présent Livre, il est fait application du taux de 18 % sur une base hors taxe. Le taux prévu au paragraphe ci-dessus est réduit à 9% pour : - le lait à l'exclusion des yaourts et de tout autre produit laitier ; - le lait infantile ... - les pâtes alimentaires à base de semoule de blé dur à 100 %; ... - les produits pétroliers; - la viande de luxe (Loi n° 2024-1109, an. fiscale, art. 1er-4); - le riz de luxe".

art. 418 Section IV - Bases d'imposition et tarifs: "I. - Boissons alcoolisées 1- Champagnes : 40 %. 2- Vins ordinaires : 35 %. 3- Vins mousseux et vins AC et assimilés : 40 %. 4- Bières et cidres : 17 %. 5- Autres boissons alcoolisées titrant moins de 35° d'alcool : 40 %. 6- Autres boissons alcoolisées titrant 35° d'alcool et plus : 45 %. ... II. - Boissons non alcoolisées à l'exclusion de l'eau : 1- Boissons énergétiques : 14 % 2- Autres boissons non alcoolisées : 14 %. III. - Tabacs Cigares, cigarillos, cigarettes, tabac à fumer, ... 57 %"; art. 419: "d'après le prix de vente sortie-usine, à l'exclusion de la taxe sur la valeur ajoutée ... En ce qui concerne les tabacs, ce prix de vente ne peut être inférieur à 20 000 francs les 1 000 cigarettes".
-/

namespace CiGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1800, reduced := 900, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .petrol | .diesel => .reduced
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "CGI 2025 art. 359 (18 % on a base excluding tax; 9 % for milk, infant milk, durum-wheat pasta, petroleum products, luxury meat (LF 2025 art. 1-4) and luxury rice)"

-- the standard rate as printed: 18 % inside a tax-inclusive 11800
#guard vatX.embedded { good := .other, amount := 11800 } == 1800
#guard vatX.embedded { good := .petrol, amount := 10900 } == 900
#guard vatX.embedded { good := .diesel, amount := 10900 } == 900
def accises : List R4.Exc :=
  [ { good := .beer, name := "Taxe spécifique bières", advBp := 1700, vatBp := 1800, statute := "CGI art. 418 I 4 (17 %)" },
    { good := .wine, name := "Taxe spécifique vins ordinaires", advBp := 3500, vatBp := 1800, statute := "CGI art. 418 I 2 (35 %)" },
    { good := .spirits, name := "Taxe spécifique boissons < 35°", advBp := 4000, vatBp := 1800, maxAbvBp := 3499, statute := "CGI art. 418 I 5 (40 %)" },
    { good := .spirits, name := "Taxe spécifique boissons >= 35°", advBp := 4500, vatBp := 1800, minAbvBp := 3499, statute := "CGI art. 418 I 6 (45 %)" },
    { good := .nonAlcoholic, name := "Taxe spécifique boissons non alcoolisées", advBp := 1400, vatBp := 1800, statute := "CGI art. 418 II (14 %)" },
    { good := .cigarettes, name := "Taxe spécifique tabacs", advBp := 5700, vatBp := 1800, statute := "CGI art. 418 III (57 %)" } ]
def excise : Family := R4.exciseFamily "Taxe spécifique sur les boissons et les tabacs" accises
-- CGI art. 418 I 4 (17 %): 10000 paid for 1 unit(s) at 5 % vol → 1231
#guard (R4.exciseCharges [{ good := .beer, name := "Taxe spécifique bières", advBp := 1700, vatBp := 1800, statute := "CGI art. 418 I 4 (17 %)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [1231]
-- CGI art. 418 I 2 (35 %): 10000 paid for 1 unit(s) at 12 % vol → 2196
#guard (R4.exciseCharges [{ good := .wine, name := "Taxe spécifique vins ordinaires", advBp := 3500, vatBp := 1800, statute := "CGI art. 418 I 2 (35 %)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [2196]
-- CGI art. 418 I 5 (40 %): 10000 paid for 1 unit(s) at 0.99 % vol → 2420
#guard (R4.exciseCharges [{ good := .spirits, name := "Taxe spécifique boissons < 35°", advBp := 4000, vatBp := 1800, maxAbvBp := 3499, statute := "CGI art. 418 I 5 (40 %)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 99 }] []).map (·.due) == [2420]
-- CGI art. 418 I 6 (45 %): 10000 paid for 1 unit(s) at 40 % vol → 2629
#guard (R4.exciseCharges [{ good := .spirits, name := "Taxe spécifique boissons >= 35°", advBp := 4500, vatBp := 1800, minAbvBp := 3499, statute := "CGI art. 418 I 6 (45 %)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [2629]
-- CGI art. 418 II (14 %): 10000 paid for 1 unit(s) at 0 % vol → 1040
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Taxe spécifique boissons non alcoolisées", advBp := 1400, vatBp := 1800, statute := "CGI art. 418 II (14 %)" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1040]
-- CGI art. 418 III (57 %): 10000 paid for 1 unit(s) at 0 % vol → 3076
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Taxe spécifique tabacs", advBp := 5700, vatBp := 1800, statute := "CGI art. 418 III (57 %)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [3076]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["art. 355 exemptions (financial operations under the taxe sur les opérations bancaires, medicines, education, unprocessed staples, ...) are not applied; the 9 % food items are not separable from the processed-food basket line", "water is excluded from the non-alcoholic rate (art. 418 II): the whole non-alcoholic basket line is charged", "the minimum tobacco base (20 000 F per 1 000 cigarettes) and the taxe spécifique unique on petroleum products (per-litre tariff set by ordinance, reproduced in the online edition) are not modelled; the annex taxes on alcoholic drinks (taxe additionnelle) not located"]

end CiGlobal
