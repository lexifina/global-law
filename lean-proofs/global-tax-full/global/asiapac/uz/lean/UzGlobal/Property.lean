import UzGlobal.Pit

/-!
# Uzbekistan 2025: property tax of individuals (4100)

Source: Tax Code of 30 December 2019 No. ZRU-599, lex.uz Russian text as on 1 January 2025, copied by the 1.x UZ
builder (`cmp20/world/B05-former-ussr/uz/law/lex_tc_ru_on20250101.txt`, sha256 in `uz/law/SOURCES.tsv`), ch. 60.
* **art. 419**: dwellings, flats, dacha buildings; non-residential property for business or income; unfinished
  non-residential construction; parking places and other structures.
* **art. 420**: base = the cadastral value set by the registration authority (the asset's assessed value, else its market
  value); for dwellings it "cannot be lower than forty-two million soums" (floor not applied: flagged).
* **art. 422** (Law ZRU-1014 of 24 Dec 2024, in force 1 Jan 2025): dwellings, flats, dachas up to 200 m² 0.34 %; urban
  dwellings 200-500 m² 0.45 %, above 500 m² 0.6 %; other settlements above 200 m² 0.45 %; objects used for business or
  let to a legal person or entrepreneur, and non-residential property for business or income, 1.5 %. Regions may apply
  coefficients of 0.7 to 1.3 (not applied). Homes are taken at 0.34 % (floor area not in the canonical asset).
* **art. 421** exemptions (heroes, war invalids, families of fallen servicemen; 60 m² for pensioners, families with ten
  children, group I-II disability) not applied.
-/

namespace UzGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "Property tax of individuals (Tax Code art. 422)", sched := Schedule.flat 150, homeSched := some (Schedule.flat 34), ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.home, .realEstate] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "Tax Code arts. 419, 420, 422 (Law ZRU-1014, from 1 Jan 2025)" (level := .local) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .home) then ["homes taken at 0.34 % (up to 200 m²): 0.45 %/0.6 % for larger homes (art. 422 items 2-3), the 42 million soum floor on the base (art. 420), regional coefficients 0.7-1.3 and the art. 421 exemptions not applied"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate) then ["other real estate taken as non-residential or let property at 1.5 % (art. 422 item 4)"] else [])
  ++ (if g.assets.any (fun a => a.kind == .land) then ["land tax (Tax Code ch. 61) not modelled"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 100000000 }] } []).map (·.due) == [340000]
#guard (fam0.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .realEstate, value := 100000000 }] } []).map (·.due) == [1500000]

end UzGlobal.Property
