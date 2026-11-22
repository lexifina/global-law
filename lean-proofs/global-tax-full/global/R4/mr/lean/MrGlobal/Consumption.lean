import R4Common

/-!
# Mauritania 2025: VAT (5111) and excises (5121) (generated from `R4/specs/mr.json` by `R4/tools/gen_country.py`)

Sources: CGI 2023 French (`cmp20/world/B06-mena/mr/law/cgi2023fr.txt`).

art. 230: "Les taux de la taxe sur la valeur ajoutée sont les suivants : 1) Taux normal : 16 %. 2) Taux zéro (0 %) : exportations de biens et services". Exemptions not read; the Arabic LF 2025 not read.

art. 258: production and import of petroleum products, alcohols, tobacco, mineral water, dairy products, ... are subject to a taxe de consommation; art. 262: base = customs value plus import duties, or the ex-factory selling price for local products, VAT and the tax itself excluded; art. 263: "1) Produits pétroliers : essence auto ordinaire : 5,7 Ouguiya/l; super carburant : 5,8 Ouguiya/l; gazole (gas-oil) : 3,67 Ouguiya/l ... 2) Alcools : a) bière : 195 % b) vins ordinaires : 209 % c) vins mousseux et champagne : 229 % d) whisky, vodka, rhum, gin, eau de vie : 294 % 3) Tabac : 29 % 4) Eaux minérales importées : 80 %".
-/

namespace MrGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1600, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "CGI art. 230 (16 %; 0 % exports)"

-- the standard rate as printed: 16 % inside a tax-inclusive 11600
#guard vatX.embedded { good := .other, amount := 11600 } == 1600
def accises : List R4.Exc :=
  [ { good := .beer, name := "Taxe de consommation bière", advBp := 19500, vatBp := 1600, statute := "CGI art. 263 2) a (195 %)" },
    { good := .wine, name := "Taxe de consommation vins ordinaires", advBp := 20900, vatBp := 1600, statute := "CGI art. 263 2) b (209 %)" },
    { good := .spirits, name := "Taxe de consommation whisky, vodka, rhum, gin, eau de vie", advBp := 29400, vatBp := 1600, statute := "CGI art. 263 2) d (294 %)" },
    { good := .cigarettes, name := "Taxe de consommation tabac", advBp := 2900, vatBp := 1600, statute := "CGI art. 263 3) (29 %)" },
    { good := .petrol, name := "Taxe de consommation super carburant", perUnitNum := 5800, perUnitDen := 1000, vatBp := 1600, statute := "CGI art. 263 1) (5,8 MRU per litre)" },
    { good := .diesel, name := "Taxe de consommation gazole", perUnitNum := 3670, perUnitDen := 1000, vatBp := 1600, statute := "CGI art. 263 1) (3,67 MRU per litre)" } ]
def excise : Family := R4.exciseFamily "Taxe de consommation" accises
-- CGI art. 263 2) a (195 %): 10000 paid for 1 unit(s) at 5 % vol → 5697
#guard (R4.exciseCharges [{ good := .beer, name := "Taxe de consommation bière", advBp := 19500, vatBp := 1600, statute := "CGI art. 263 2) a (195 %)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [5697]
-- CGI art. 263 2) b (209 %): 10000 paid for 1 unit(s) at 12 % vol → 5829
#guard (R4.exciseCharges [{ good := .wine, name := "Taxe de consommation vins ordinaires", advBp := 20900, vatBp := 1600, statute := "CGI art. 263 2) b (209 %)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [5829]
-- CGI art. 263 2) d (294 %): 10000 paid for 1 unit(s) at 40 % vol → 6429
#guard (R4.exciseCharges [{ good := .spirits, name := "Taxe de consommation whisky, vodka, rhum, gin, eau de vie", advBp := 29400, vatBp := 1600, statute := "CGI art. 263 2) d (294 %)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [6429]
-- CGI art. 263 3) (29 %): 10000 paid for 1 unit(s) at 0 % vol → 1937
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Taxe de consommation tabac", advBp := 2900, vatBp := 1600, statute := "CGI art. 263 3) (29 %)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1937]
-- CGI art. 263 1) (5,8 MRU per litre): 10000 paid for 1 unit(s) at 0 % vol → 5
#guard (R4.exciseCharges [{ good := .petrol, name := "Taxe de consommation super carburant", perUnitNum := 5800, perUnitDen := 1000, vatBp := 1600, statute := "CGI art. 263 1) (5,8 MRU per litre)" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [5]
-- CGI art. 263 1) (3,67 MRU per litre): 10000 paid for 1 unit(s) at 0 % vol → 3
#guard (R4.exciseCharges [{ good := .diesel, name := "Taxe de consommation gazole", perUnitNum := 3670, perUnitDen := 1000, vatBp := 1600, statute := "CGI art. 263 1) (3,67 MRU per litre)" }] [{ good := .diesel, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [3]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["Mauritania: CGI 2023 French text (LF 2025 Arabic not read); VAT exemptions not read", "CGI art. 263: sparkling wine 229 %, ordinary petrol 5,7 MRU/l, imported mineral water 80 % and dairy products not separable from the basket lines (still wine, premium petrol taken)"]

end MrGlobal
