import R4Common

/-!
# Congo 2025: VAT (5111) and excises (5121) (generated from `R4/specs/cg.json` by `R4/tools/gen_country.py`)

Code général des impôts tome 1 (local copy `cmp20/world/B08-central-africa-fr/cg/law/cgi_tome1.txt`, edition without post-2021 amendment notes); Journal officiel 2022-2025 issues held locally do not include the LF 2025. Pass 9: the Journal officiel special editions held under `world/B08-central-africa-fr/cg/law/jo/` were read for P1/P2: `jo-2024-15-sp.txt` = LF 2025 (Loi n° 47-2024: art. 122 IS 30 % restored, art. 8 of the excise text new rates, VAT art. 7 items 12 and 22 only), `congo-jo-2023-06-sp.raw.txt` = LF 2024 (Loi n° 39-2023, which modifies and completes loi n° 12-97 on VAT: art. 7 exemptions, art. 22 rates, art. 38 A centimes additionnels). Withholding from CGI tome 1 (`cgi_tome1.txt`) art. 185 ter. Thirteenth pass: CGI tome 2 (Wayback copy of finances.gouv.cg `CGI Tome II.pdf`, capture 2021-08-15, 171 pages), saved as `R4/fetch/p13/cg_cgi_tome2.pdf`.

LF 2024, art. 22: "2) Les taux de la TVA sont fixés de la manière suivante : a) Taux général : 18 % applicable à toutes les opérations taxables à l'exclusion des opérations soumises aux taux réduit et zéro ; ... c) Taux réduit : 5 % applicable : sur certains biens de consommations courantes, ci-après cités en Annexe V"; art. 38 A: "Les centimes additionnels sont applicables aux opérations soumises à la TVA. ... 3) La base d'imposition aux centimes additionnels est le montant de la TVA collectée. 4) Le taux applicable aux centimes additionnels est de 5 %." art. 7: "Sont exonérés de la TVA : 1) ... Les opérations bancaires et financières ... et les prestations d'assurance et de réassurance ; ... 2) ... Les locations d'immeubles nus à usage d'habitation et de terrains nus ... 4) Les examens, consultations, soins, hospitalisation ... 5) ... journaux et périodiques ... 6) Les frais de scolarité ... 10) Les produits pharmaceutiques". LF 2025 (Loi n° 47-2024): "Article 7 (nouveau) Sont exonérés de la TVA : 1) à 11) : Sans changement ; 12) L'eau minérale produite au Congo et le gaz butane ... 13) à 21) : Sans changement ; 22) l'importation des panneaux photovoltaïques ...".

LF 2025, point 23 "Revalorisation des taux des droits d'accises conformément à la directive CEMAC n° 03/19-UEAC-010A-CM-33 du 8 avril 2019 ... Article 8 (nouveau) : 1) Les taux des droits d'accises sont fixés comme suit : a) Tabacs : 30% ; b) Boissons alcoolisées : 25% ; c) Boissons sucrées : 12,5% ; d) produits alimentaires de luxe, parfums et produits cosmétiques, armes et munitions, bijoux : 25% ; e) Véhicules automobiles de tourisme ... : 15% ; f) Appareils servant aux jeux de hasard et de divertissements : 25%. g) Autres produits soumis aux droits d'accises : 25% 2) Les droits d'accises appliqués sur les produits ci-dessus énumérés est exclusif à d'autres taxes assimilées aux droits d'accises."
-/

namespace CgGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée (with centimes additionnels)", standard := 1890, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .financial | .insurance | .rent | .health | .newspapers | .education | .medicines => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Loi n° 12-97 (TVA) as modified by Loi n° 39-2023 (LF 2024) art. 22 2) a) (18 %) and art. 38 A 4) (centimes additionnels 5 % of the VAT: 18 % x 1,05 = 18,9 %); art. 7 exemptions (LF 2025 amends only items 12 and 22)"

-- the standard rate as printed: 18.9 % inside a tax-inclusive 11890
#guard vatX.embedded { good := .other, amount := 11890 } == 1890
#guard vatX.embedded { good := .financial, amount := 10000 } == 0
#guard vatX.embedded { good := .insurance, amount := 10000 } == 0
#guard vatX.embedded { good := .rent, amount := 10000 } == 0
def accises : List R4.Exc :=
  [ { good := .beer, name := "Droits d'accises boissons alcoolisées (bière)", advBp := 2500, vatBp := 1890, statute := "art. 8 1) b) (LF 2025): 25 %" },
    { good := .wine, name := "Droits d'accises boissons alcoolisées (vin)", advBp := 2500, vatBp := 1890, statute := "art. 8 1) b) (LF 2025): 25 %" },
    { good := .spirits, name := "Droits d'accises boissons alcoolisées (spiritueux)", advBp := 2500, vatBp := 1890, statute := "art. 8 1) b) (LF 2025): 25 %" },
    { good := .nonAlcoholic, name := "Droits d'accises boissons sucrées", advBp := 1250, vatBp := 1890, statute := "art. 8 1) c) (LF 2025): 12,5 %" },
    { good := .cigarettes, name := "Droits d'accises tabacs", advBp := 3000, vatBp := 1890, statute := "art. 8 1) a) (LF 2025): 30 %" } ]
def excise : Family := R4.exciseFamily "Droits d'accises" accises
-- art. 8 1) b) (LF 2025): 25 %: 10000 paid for 1 unit(s) at 5 % vol → 1682
#guard (R4.exciseCharges [{ good := .beer, name := "Droits d'accises boissons alcoolisées (bière)", advBp := 2500, vatBp := 1890, statute := "art. 8 1) b) (LF 2025): 25 %" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [1682]
-- art. 8 1) b) (LF 2025): 25 %: 10000 paid for 1 unit(s) at 12 % vol → 1682
#guard (R4.exciseCharges [{ good := .wine, name := "Droits d'accises boissons alcoolisées (vin)", advBp := 2500, vatBp := 1890, statute := "art. 8 1) b) (LF 2025): 25 %" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [1682]
-- art. 8 1) b) (LF 2025): 25 %: 10000 paid for 1 unit(s) at 40 % vol → 1682
#guard (R4.exciseCharges [{ good := .spirits, name := "Droits d'accises boissons alcoolisées (spiritueux)", advBp := 2500, vatBp := 1890, statute := "art. 8 1) b) (LF 2025): 25 %" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [1682]
-- art. 8 1) c) (LF 2025): 12,5 %: 10000 paid for 1 unit(s) at 0 % vol → 934
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Droits d'accises boissons sucrées", advBp := 1250, vatBp := 1890, statute := "art. 8 1) c) (LF 2025): 12,5 %" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [934]
-- art. 8 1) a) (LF 2025): 30 %: 10000 paid for 1 unit(s) at 0 % vol → 1940
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Droits d'accises tabacs", advBp := 3000, vatBp := 1890, statute := "art. 8 1) a) (LF 2025): 30 %" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1940]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["the centimes additionnels (5 % of the VAT, non-deductible, for local authorities) are folded into one 18,9 % rate", "the 5 % reduced rate (Annexe V staples, milk, bread, rice, flour) is not applied to the processed-food basket line; the art. 7 exemptions for water/butane produced in Congo (LF 2025) are not separated", "the base article of the excise text was not read: the region convention (value before excise and VAT, i.e. ex-factory price or customs value plus duties under the CEMAC directive) is used", "the non-alcoholic basket line is charged at the sugary-drinks rate (water is outside it); petroleum products are under the TSPP/TIPP regime (not modelled)"]

end CgGlobal
