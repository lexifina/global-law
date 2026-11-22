import R4Common

/-!
# Burkina Faso 2025: VAT (5111) and excises (5121) (generated from `R4/specs/bf.json` by `R4/tools/gen_country.py`)

Sources: CGI updated to the LF 2023 (`cmp20/world/B07-west-africa-fr-pt/bf/src/CGI-LF2023-b.txt`), LF 2024 and LFR 2024 OCR.

art. 317: "Le taux de la TVA est fixé à 18 %. Ce taux est réduit à 10% pour les prestations d'hébergement et de restauration fournies par les hôtels, les restaurants et organismes assimilés". Exemptions not read; LF 2025 not held.

LF 2024 art. 29, art. 359: "Il est fait application des taux suivants quelle que soit l'origine des produits : I. Boissons alcoolisées 1. Bières titrant moins de 8° d'alcool : 30% 2. Bières titrant 8° d'alcool et plus : 40% 3. Vins : 70% 4. Autres boissons alcoolisées titrant moins de 35° d'alcool : 50% 5. Autres boissons alcoolisées titrant 35° d'alcool et plus : 70% Le reste sans changement" (CGI 2023: "II. Boissons non alcoolisées 1. Boissons non alcoolisées énergisantes : 50% 2. Autres boissons non alcoolisées : 15%"). Art. 358: local products taxed on turnover excluding VAT; imports on customs value plus duties except VAT. Art. 365: "Le taux de la taxe est fixé à 55 %"; art. 364: ex-factory price excluding VAT, at least 300 FCFA per 20 cigarettes. Grade B: LF 2025 not held.
-/

namespace BfGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1800, reduced := 1000, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .hotels | .restaurants => .reduced
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "CGI art. 317 (18 %; 10 % hotel and restaurant services)"

-- the standard rate as printed: 18 % inside a tax-inclusive 11800
#guard vatX.embedded { good := .other, amount := 11800 } == 1800
#guard vatX.embedded { good := .hotels, amount := 11000 } == 1000
#guard vatX.embedded { good := .restaurants, amount := 11000 } == 1000
def accises : List R4.Exc :=
  [ { good := .beer, name := "TSB bières < 8°", advBp := 3000, vatBp := 1800, maxAbvBp := 799, statute := "CGI art. 359 I 1 (LF 2024 art. 29): 30 %" },
    { good := .beer, name := "TSB bières >= 8°", advBp := 4000, vatBp := 1800, minAbvBp := 799, statute := "CGI art. 359 I 2 (LF 2024 art. 29): 40 %" },
    { good := .wine, name := "TSB vins", advBp := 7000, vatBp := 1800, statute := "CGI art. 359 I 3 (LF 2024 art. 29): 70 %" },
    { good := .spirits, name := "TSB autres boissons alcoolisées < 35°", advBp := 5000, vatBp := 1800, maxAbvBp := 3499, statute := "CGI art. 359 I 4 (LF 2024 art. 29): 50 %" },
    { good := .spirits, name := "TSB autres boissons alcoolisées >= 35°", advBp := 7000, vatBp := 1800, minAbvBp := 3499, statute := "CGI art. 359 I 5 (LF 2024 art. 29): 70 %" },
    { good := .nonAlcoholic, name := "TSB autres boissons non alcoolisées", advBp := 1500, vatBp := 1800, statute := "CGI art. 359 II 2: 15 %" },
    { good := .cigarettes, name := "Taxe sur les tabacs, cigares et cigarettes", advBp := 5500, vatBp := 1800, statute := "CGI art. 365 (loi n° 029-2022/ALT art. 53): 55 %" } ]
def excise : Family := R4.exciseFamily "Taxe sur les boissons et taxe sur les tabacs" accises
-- CGI art. 359 I 1 (LF 2024 art. 29): 30 %: 10000 paid for 1 unit(s) at 5 % vol → 1955
#guard (R4.exciseCharges [{ good := .beer, name := "TSB bières < 8°", advBp := 3000, vatBp := 1800, maxAbvBp := 799, statute := "CGI art. 359 I 1 (LF 2024 art. 29): 30 %" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [1955]
-- CGI art. 359 I 2 (LF 2024 art. 29): 40 %: 10000 paid for 1 unit(s) at 8.99 % vol → 2420
#guard (R4.exciseCharges [{ good := .beer, name := "TSB bières >= 8°", advBp := 4000, vatBp := 1800, minAbvBp := 799, statute := "CGI art. 359 I 2 (LF 2024 art. 29): 40 %" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 899 }] []).map (·.due) == [2420]
-- CGI art. 359 I 3 (LF 2024 art. 29): 70 %: 10000 paid for 1 unit(s) at 12 % vol → 3488
#guard (R4.exciseCharges [{ good := .wine, name := "TSB vins", advBp := 7000, vatBp := 1800, statute := "CGI art. 359 I 3 (LF 2024 art. 29): 70 %" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [3488]
-- CGI art. 359 I 4 (LF 2024 art. 29): 50 %: 10000 paid for 1 unit(s) at 0.99 % vol → 2824
#guard (R4.exciseCharges [{ good := .spirits, name := "TSB autres boissons alcoolisées < 35°", advBp := 5000, vatBp := 1800, maxAbvBp := 3499, statute := "CGI art. 359 I 4 (LF 2024 art. 29): 50 %" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 99 }] []).map (·.due) == [2824]
-- CGI art. 359 I 5 (LF 2024 art. 29): 70 %: 10000 paid for 1 unit(s) at 40 % vol → 3488
#guard (R4.exciseCharges [{ good := .spirits, name := "TSB autres boissons alcoolisées >= 35°", advBp := 7000, vatBp := 1800, minAbvBp := 3499, statute := "CGI art. 359 I 5 (LF 2024 art. 29): 70 %" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [3488]
-- CGI art. 359 II 2: 15 %: 10000 paid for 1 unit(s) at 0 % vol → 1105
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "TSB autres boissons non alcoolisées", advBp := 1500, vatBp := 1800, statute := "CGI art. 359 II 2: 15 %" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1105]
-- CGI art. 365 (loi n° 029-2022/ALT art. 53): 55 %: 10000 paid for 1 unit(s) at 0 % vol → 3006
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Taxe sur les tabacs, cigares et cigarettes", advBp := 5500, vatBp := 1800, statute := "CGI art. 365 (loi n° 029-2022/ALT art. 53): 55 %" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [3006]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["Burkina Faso: CGI as of LF 2023/2024 (LF 2025 not held); VAT exemptions not read", "CGI art. 356: water without sugar or flavouring, local fruit juices from local raw materials and traditional local drinks are exempt (not separable from the basket line); energy drinks 50 % (art. 359 II 1) not separable", "art. 364: the minimum base of 300 FCFA per 20 cigarettes is not applied", "taxe sur les produits pétroliers, café/thé, colas and cosmetics (15 %) not modelled"]

end BfGlobal
