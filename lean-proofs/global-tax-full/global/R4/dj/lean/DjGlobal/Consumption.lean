import R4Common

/-!
# Djibouti 2025: VAT (5111) and excises (5121) (generated from `R4/specs/dj.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: only finance laws (2017-2025) are held, not the CGI; rates not consolidated. Second pass: Finance laws 2017-2025 (Loi n°203/AN/25 for 2025); the CGI itself not held. Pass 9: the Code général des impôts as recast by Loi n° 42/AN/08/6ème L, full text on the Journal officiel site (https://www.journalofficiel.dj/texte-juridique/loi-n42-an-08-6emel-portant-refonte-du-code-generale-des-impots/, found with the site's WordPress search `/wp-json/wp/v2/search?search=impôts`), saved with SHA256SUMS in `R4/fetch/dj9/` (cgi2008.html / .txt). The finance laws 2017-2025 held were searched for amendments of art. 56, 57-61, 70-75 (LF 2024, Loi n° 64/AN/23: art. 58 al. 2 added, art. 62 al. 3 repealed, new art. 90F-90L IRVM 5 %); the finance laws 2009-2016 and the CGI amending laws of 2009, 2017 and 2018 listed on the same site were not read: graded B and flagged.

LF 2025: "Il est perçu au profit du budget de l'État, une taxe intérieure de consommation de 10% et une taxe sur la valeur ajoutée de 10% sur les véhicules électriques importés ou produits sur le territoire national"; Loi n°111/AN/20 art. 28: "une taxe intérieure de consommation (TIC) de 10% et une taxe sur la valeur ajoutée de 10% sur les couches et lange pour bébés"; Loi n°142/AN/21: "en plus de la taxe intérieure de consommation de 23% une taxe sur la valeur ajoutée de 10%". The general rate article of the CGI is not held: grade B (rate from the finance laws' own charging lines).


-/

namespace DjGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1000, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "TVA 10 % as imposed by the finance laws (LF 2025 art. on electric vehicles; Loi n°111/AN/20 art. 28; Loi n°142/AN/21); the CGI rate article not held"

-- the standard rate as printed: 10 % inside a tax-inclusive 11000
#guard vatX.embedded { good := .other, amount := 11000 } == 1000

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["VAT 10 % taken from the finance laws' charging lines (the CGI rate article not held)", "excises not modelled: only finance laws (2017-2025) are held, not the CGI; rates not consolidated"]

end DjGlobal
