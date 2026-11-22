import R4Common
import R4Common.K21

/-!
# Madagascar 2025: VAT (5111) and excises (5121)

Source: Code général des impôts suivant la LFI 2025 (DGI): `cmp20/world/B08-central-africa-fr/mg/law/cdi_lfi2025.txt`.

* **TVA** art. 06.01.12: "Le taux normal de la Taxe sur la Valeur Ajoutée est fixé à 20p.100. Les importations et les
  ventes de gaz butanes … sont taxées au taux réduit de 10p.100." Exemptions art. 06.01.06: 1° "Les écolages …
  d'enseignement"; 4° a- bank interest; 6° domestic water and electricity up to 10 m³ and 100 kWh; 7° "Les
  prestations fournies dans le cadre de la profession de la santé"; 8° "L'importation et la vente des médicaments";
  9° newspapers and periodicals; 11° educational and school books; 20° "pétrole lampant"; 21° "La vente de maïs".
* **Droit d'accises** art. 03.01.01 and the annex 2 table "TAUX ET TARIF" (columns LOCAL / IMPORTE): beer 2203
  "12,5% 50%"; wines 2204.21 "12,5% 50%"; whiskies 2208.30 "10% 275%"; gin, vodka, liqueurs, others 2208 "10% 260%";
  rum 2208.40 "Ar 500/L 260%"; cigarettes 2402.20 "Ar 1440 325 %" ("Par paquet de 20"); sweetened waters 2202.10
  "2,5% 10%". Base art. 03.01.04: imports "la valeur CAF des marchandises majorée des droits de douanes"; local "le
  prix de vente pratiqué à la sortie de l'usine" (`R4.Exc`, VAT stripped).
-/

namespace MgGlobal
open TaxKernel TaxKernel.Global

def tva : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 2000, reduced := 1000,
    classOf := fun gd => match gd with
      | .gas => .reduced
      | .health | .medicines | .education | .financial | .newspapers => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily tva "CGI art. 06.01.12 (20 %; butane 10 %), art. 06.01.06 1°, 4°, 7°-9° (exemptions)"

def mk (gd : Good) (nm : String) (loc imp : Int) (st : String) (spLoc : Int := 0) (spDen : Int := 1) : List R4.Exc :=
  [{ good := gd, name := nm, advBp := loc, perUnitNum := spLoc, perUnitDen := spDen, vatBp := 2000, imported := some false,
     statute := s!"CGI art. 03.01.01, 03.01.04, annex 2 {st} (local)" },
   { good := gd, name := nm, advBp := imp, vatBp := 2000, imported := some true,
     statute := s!"CGI art. 03.01.01, 03.01.04, annex 2 {st} (imported)" }]

def accises : List R4.Exc :=
  mk .beer "Droit d'accises (bières)" 1250 5000 "2203 (12,5 % / 50 %)"
  ++ mk .wine "Droit d'accises (vins)" 1250 5000 "2204.21 (12,5 % / 50 %)"
  ++ mk .spirits "Droit d'accises (eaux-de-vie)" 1000 26000 "2208 (10 % / 260 %)"
  ++ mk .nonAlcoholic "Droit d'accises (boissons sucrées)" 250 1000 "2202.10 (2,5 % / 10 %)"
  ++ mk .cigarettes "Droit d'accises (cigarettes)" 0 32500 "2402.20 (Ar 1 440 per pack of 20 / 325 %)" (spLoc := 1440) (spDen := 20)

def excise : Family := exciseRuleFamily "droit d'accises (CGI art. 03.01.01-03.01.05)" (accises.map R4.Exc.toRule)

/-- kernel 2.1 `ExciseRule` (value before tax) gives the R4 figures on a mixed basket (local and imported). -/
def excT : CanonGlobal := { id := "x", household := { id := "x" }, consumption := [{ good := .beer, amount := 1180, quantity := 1000, abvBp := 500 }, { good := .wine, amount := 3540, quantity := 1000, abvBp := 1200 }, { good := .spirits, amount := 9000, quantity := 700, abvBp := 4000 }, { good := .cigarettes, amount := 1500, quantity := 20000 }, { good := .petrol, amount := 100000, quantity := 100000 }, { good := .nonAlcoholic, amount := 1180, quantity := 1000 }] }
#guard (exciseRuleCharges (accises.map R4.Exc.toRule) excT).map (·.due) == (R4.exciseCharges accises excT.consumption).map (·.due)

def consumptionNotes (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .water || s.good == .electricity) then
     ["CGI art. 06.01.06 6°: domestic water up to 10 m³ and electricity up to 100 kWh are exempt; the whole line is taxed at 20 %"] else [])
  ++ (if g.consumption.any (·.good == .books) then ["CGI art. 06.01.06 11°: only educational and school books are exempt"] else [])
  ++ (if g.consumption.any (·.good == .spirits) then ["annex 2: whiskies 275 % and local rum Ar 500/L not separated from spirits (10 % / 260 %)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then
     ["fuel: no droit d'accises line in the CGI table was read for petrol and gas oil; fuel taxes not modelled"] else [])

-- 1 200 Ar of local beer: net of VAT 1 000, base 1 000 / 1,125 = 888, 12,5 % = 111
#guard (R4.exciseCharges accises [{ good := .beer, amount := 1200, quantity := 1000 }]).map (·.due) == [111]
-- a pack of 20 local cigarettes: Ar 1 440 (specific only)
#guard (R4.exciseCharges accises [{ good := .cigarettes, amount := 0, quantity := 20000 }]).map (·.due) == [1440]
#guard tva.embedded { good := .gas, amount := 11000 } == 1000

end MgGlobal
