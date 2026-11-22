import R4Common

/-!
# Comoros 2025: corporate income tax (1200) and withholding (generated from `R4/specs/km.json`)

Sources: Code général des impôts 2022 (`cmp20/world/B08-central-africa-fr/km/law/cgi2022.txt`), LF 2024 OCR pages 1-60.

art. 33: "Le taux de l'impôt sur les sociétés est fixé à 35 %"; art. 35: "un minimum forfaitaire égal à 1,5 % du chiffre d'affaires" (art. 36: 3 % of the turnover realised in the Comoros for a second category, not applied).

art. 128: "Il est institué une taxe sur les rémunérations extérieures au taux global de 10 % sur les revenus servis aux personnes morales ou physiques domiciliées hors des Comores, par des entreprises ou établissements situés aux Comores, l'État ou les collectivités territoriales décentralisées au titre : des droits d'auteurs ; de la vente ou de la location de licence d'exploitation de brevets, marques de fabrique, procédés et formules secrets ; ... des rémunérations pour études, consultations, assistance technique, ou comptable ; ... et plus généralement, des rémunérations payées au titre d'un service quelconque à l'exception des rémunérations d'emprunts contractés à l'étranger"; art. 130: base = gross amount. Twelfth pass (kernel 2.3.0 grade-C withholding): dividend 10 %: CGI 2022 art. 109 1) (impôt sur le revenu au titre des valeurs mobilières retenu à la source au taux de 10 %; two-column print read across the columns, flag) Thirteenth pass (kernel 2.3.0 grade-C withholding): interest 10 %: CGI 2022 art. 61 c), 72 1° (revenus des créances are revenus de valeurs mobilières), art. 109 1) (IRVM retenu à la source au taux de 10 %; two-column print read across the columns, flag)
-/

namespace KmGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 3500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 150, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3500349
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 15000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 300000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 6000000
def whtR : Wht :=
  { name := "Taxe sur les rémunérations extérieures (TRE)",
    rules := [{ kind := .services, rateBp := 1000, statute := "CGI art. 128 (TRE 10 %)" },
              { kind := .royalty, rateBp := 1000, statute := "CGI art. 128 (TRE 10 %: copyrights, patents, trademarks)" },
              { kind := .dividend, rateBp := 1000, statute := "CGI 2022 art. 109 1) (impôt sur le revenu au titre des valeurs mobilières retenu à la source au taux de 10 %; two-column print read across the columns, flag)" },
              { kind := .interest, rateBp := 1000, statute := "CGI 2022 art. 61 c), 72 1° (revenus des créances are revenus de valeurs mobilières), art. 109 1) (IRVM retenu à la source au taux de 10 %; two-column print read across the columns, flag)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 100000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 100000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 100000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 100000
def corporate : Family :=
  { name := "1200 Impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "CGI 2022 art. 33 (35 %), art. 35 (minimum forfaitaire 1,5 % of turnover)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CGI 2022 edition (LF 2025 not held)", "CGI art. 36 minimum 3 % for the category it names: not applied", "art. 128 excludes interest on loans contracted abroad; dividends: art. 109 1) withholds the IRVM at 10 % 'en ce qui concerne les personnes morales' (two-column extraction, scope for non-residents not established): not applied"]

end KmGlobal
