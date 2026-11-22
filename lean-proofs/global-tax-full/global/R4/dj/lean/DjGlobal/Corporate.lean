import R4Common

/-!
# Djibouti 2025: corporate income tax (1200) and withholding (generated from `R4/specs/dj.json`)

No usable 2025 text for these headings: only finance laws (2017-2025) are held, not the CGI; rates not consolidated. Second pass: Finance laws 2017-2025 (Loi n°203/AN/25 for 2025); the CGI itself not held. Pass 9: the Code général des impôts as recast by Loi n° 42/AN/08/6ème L, full text on the Journal officiel site (https://www.journalofficiel.dj/texte-juridique/loi-n42-an-08-6emel-portant-refonte-du-code-generale-des-impots/, found with the site's WordPress search `/wp-json/wp/v2/search?search=impôts`), saved with SHA256SUMS in `R4/fetch/dj9/` (cgi2008.html / .txt). The finance laws 2017-2025 held were searched for amendments of art. 56, 57-61, 70-75 (LF 2024, Loi n° 64/AN/23: art. 58 al. 2 added, art. 62 al. 3 repealed, new art. 90F-90L IRVM 5 %); the finance laws 2009-2016 and the CGI amending laws of 2009, 2017 and 2018 listed on the same site were not read: graded B and flagged.

art. 56: "1) Pour le calcul de l'impôt, toute fraction de bénéfice inférieur à 1.000 FD est négligée. 2) Le taux de l'impôt sur les bénéfices professionnels est fixé à 25 % du bénéfice net imposable." art. 60: "Le taux d'imposition applicable est fixé à 1 % du chiffre d'affaire réalisé hors TVA. En aucun cas le montant de l'impôt ne peut être inférieur à 120.000 FD." art. 61: "1) L'Impôt minimum forfaitaire est dû s'il est supérieur au montant de l'impôt sur les bénéfices ou dans l'hypothèse d'un résultat déficitaire." LF 2024 art. 6: "Art.58 al.2 : Est imposable le chiffre d'affaires issus des ventes et des prestations à l'exportation".

art. 70: "Il est institué un impôt perçu par la voie de retenue à la source, sur les rémunérations versées à des personnes physiques ou morales non domiciliées à Djibouti"; art. 72: "1) Les rémunérations imposables sont constituées par : les sommes versées en rémunération de prestations de service de toute nature fournies ou utilisées sur le territoire de la République de Djibouti ; les sommes perçues à titre de droit d'auteur, les produits tirés de la propriété industrielle, commerciale ou assimilée." art. 75: "2) Le taux d'imposition applicable sur la base ci-dessus est fixé à 10 %." LF 2024 art. 12: "Art. 90G ... Sont exonérées les dividendes distribués inférieurs à 10 millions FDJ"; art. 17: "Art. 90L CGI : Le taux d'imposition applicable est fixé à 5%". Thirteenth pass (kernel 2.3.0 grade-C withholding): interest 0 %: CGI (Loi 42/AN/08) art. 70-72 (non-domiciled tax: services and royalties only), art. 80 (impôt d'incitation sociale: placements of public institutions only), art. 90F-90I (LF 2024: IRVM on distributed income only): no schedular tax reaches interest paid to a non-resident lender (cited 0; LF 2017-2025 held searched, LF 2009-2016 not held: flagged)
-/

namespace DjGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les bénéfices professionnels (sociétés)", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 100, fixed := 0, floor := 120000, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 2500000
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 10000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 200000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 4000000
def whtR : Wht :=
  { name := "Impôt sur les rémunérations versées à des personnes non domiciliées et IRVM",
    rules := [{ kind := .services, rateBp := 1000, statute := "CGI art. 72, 75 (10 %)" },
              { kind := .royalty, rateBp := 1000, statute := "CGI art. 72, 75 (10 %)" },
              { kind := .dividend, rateBp := 500, statute := "CGI art. 90L (LF 2024): 5 %" },
              { kind := .interest, rateBp := 0, statute := "CGI (Loi 42/AN/08) art. 70-72 (non-domiciled tax: services and royalties only), art. 80 (impôt d'incitation sociale: placements of public institutions only), art. 90F-90I (LF 2024: IRVM on distributed income only): no schedular tax reaches interest paid to a non-resident lender (cited 0; LF 2017-2025 held searched, LF 2009-2016 not held: flagged)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 100000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 100000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 50000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 0
def corporate : Family :=
  { name := "1200 Impôt sur les bénéfices professionnels (sociétés)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "CGI (Loi n° 42/AN/08) art. 56 (25 %; fractions below 1 000 FD disregarded) and art. 57-61 impôt minimum forfaitaire (1 % of turnover excluding VAT, at least 120 000 FD, due when higher than the profit tax or with a loss); LF 2024 art. 6 adds export turnover to the IMF base — 2008 text, amendments 2009-2016 not read, flagged" (step := 1000)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["2008 recast: the finance laws 2009-2016 and the CGI amending laws of 2009, 2017 and 2018 were not read (flagged)", "the IMF base is the previous year's turnover (art. 59); the current turnover is used", "the 10 million FD exemption of distributions (art. 90G) is not applied per payment; interest paid abroad is outside art. 72 (no withholding modelled); international transport services are excluded by art. 72 3)"]

end DjGlobal
