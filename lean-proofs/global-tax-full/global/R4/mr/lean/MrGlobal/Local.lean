import R4Common
import TaxKernel.Global2

/-! # MR 2025: contribution foncière sur les propriétés bâties (local, OECD 4100), the commune's rate a declared input
(gap pass; kernel 2.8.0 `LocalTax`)

CGI (version officielle janvier 2023; the LF 2025 is held in Arabic only and was not read: grade B as the other MR entries),
Titre 8 'Impôts locaux', chapitre 1 (world/B06-mena/mr/law/cgi2023fr.txt):
* art. 159 (1): "Les propriétés bâties sont soumises à une contribution annuelle"; art. 161: due for the whole year by the
  owner;
* art. 162: "imposables à raison de leur valeur locative au 1er janvier de l'année d'imposition après déduction d'un
  abattement forfaitaire de 20 %";
* art. 163: the rental value is the rent obtained, or for an owner-occupier what the property would let for;
* art. 164: the base is rounded down to the ten ouguiya;
* art. 165: "calculée par application à la base d'imposition d'un taux voté par le Conseil Municipal qui doit être compris
  entre 3 % et 10 %".
The rate is the commune's: read from `localRates.contributionFonciere` (kernel 2.8.0), checked against 3 %-10 %; no
Nouakchott deliberation was reached, so the model declares no default rate (no rate given: grade C, never guessed).
Not modelled: art. 160 exemptions (state, worship, schools, straw huts…), art. 163 (1) fallback of 14 % of cost or price
when no rent is known (an asset without `annualValue` is grade C), art. 137 (2) withholding of 8 % of rent by corporate
tenants (a collection mechanism of the same tax), the art. 164 rounding of the base (the tax is rounded down).
-/

namespace MrGlobal
open Lean TaxKernel TaxKernel.Global

def mrFonciere : LocalTax :=
  { key := "contributionFonciere", name := "Contribution foncière sur les propriétés bâties",
    base := .annualValue [.home, .realEstate], unit := .percent,
    ratioNum := 80, ratioDen := 100,
    minNum := 3, maxNum := 10,
    statute := "CGI art. 159, 161, 162 (rental value less 20 %), 165 (rate voted by the Conseil Municipal, 3 %-10 %) [text version: CGI version officielle janvier 2023]" }

def mrT (s : String) : CanonGlobal :=
  match Json.parse s with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default

-- a let flat with a rental value of 1 200 000 MRU at a commune rate of 5 %: 1 200 000 × 80 % × 5 % = 48 000
#guard (mrFonciere.charges (mrT "{\"id\":\"h\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"localRates\":{\"contributionFonciere\":5},\"assets\":[{\"kind\":\"realEstate\",\"value\":10000000,\"annualValue\":1200000}]}")).map (fun c => (c.base, c.relieved, c.due)) == [(1200000, 960000, 48000)]
-- 10 % (the ceiling) is accepted; 12 % is outside the range: no charge, a grade-C line
#guard (mrFonciere.charges (mrT "{\"id\":\"h\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"localRates\":{\"contributionFonciere\":10},\"assets\":[{\"kind\":\"home\",\"value\":1,\"annualValue\":600000}]}")).map (·.due) == [48000]
#guard (mrFonciere.charges (mrT "{\"id\":\"h\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"localRates\":{\"contributionFonciere\":12},\"assets\":[{\"kind\":\"home\",\"value\":1,\"annualValue\":600000}]}")).isEmpty
-- no rate given: no charge, grade C (the commune's rate is never guessed)
#guard (mrFonciere.charges (mrT "{\"id\":\"h\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":1,\"annualValue\":600000}]}")).isEmpty
#guard (mrFonciere.unknown (mrT "{\"id\":\"h\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":1,\"annualValue\":600000}]}")).length == 1
-- land without buildings is outside the contribution on built property
#guard (mrFonciere.charges (mrT "{\"id\":\"h\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"localRates\":{\"contributionFonciere\":5},\"assets\":[{\"kind\":\"land\",\"value\":1,\"annualValue\":600000}]}")).isEmpty

end MrGlobal
