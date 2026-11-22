import TaxKernel.Global2
import R5Common

/-!
# Israel 2025: ארנונה כללית, municipal property tax on dwellings (4100), at the municipality's declared rate

Framework: חוק הסדרים במשק המדינה (תיקוני חקיקה להשגת יעדי התקציב), התשנ״ג–1992 (he.wikisource revision 2869205
of 18/07/2024, the text in force through 2025; revision 2969718 of 24/12/2025 has the same ss. 7-9, amendment 20 only
adds s. 12(ז) on discounts; extract `law/il_arn_ws_rev2869205_s7_9.txt`):
* s. 8(א): every financial year the council imposes the general arnona on the property in its area other than building
  land, computed per unit of area by the property's type, use and location, **paid by the holder** (המחזיק);
* s. 8(ב1)(1)-(2): area in square metres (part of a m² rounded to the nearest metre, half down); the arnona is the
  number of m² times the amount per m²;
* s. 9: the amount per m² is the council's amount of the previous year plus the update rate, never below the minimum
  or above the maximum the ministers set by regulation.
The amount per m² is the municipality's (its yearly arnona order). It is read from the entity's declared rate
(kernel 2.8 `LocalRate`: `"localRates": {"propertyTax": {"rate": <NIS per m²>, "source": …, "date": …,
"municipality": …}}`, at the top of the line, in the household, or on the home's asset record) and the home's
`"areaM2"`. No default municipality: the 2025 order of a reference city was not reached (Tel Aviv-Yafo's 2025 booklet
has only a 404 capture), and the 2025 national minimum and maximum were not reached, so a declared rate is not
range-checked. Without a rate or an area: no charge, grade C. Grade A for the framework (statute text read).
-/

namespace IlGlobal
open TaxKernel TaxKernel.Global R5Common

def arnona : LocalTax :=
  { key := "propertyTax", name := "ארנונה כללית (מגורים)", base := .area [.home], unit := .perUnit,
    statute := "חוק הסדרים במשק המדינה, התשנ״ג–1992, s. 8(א), 8(ב1)(1) (m² × the council's 2025 amount per m², paid by the holder), s. 9" }

def property : Family := arnona.family

def propertyUnsupported (g : CanonGlobal) : List String :=
  arnona.unknown g ++
  (if g.assets.any (·.kind == .home) then
    ["4100 arnona: the declared amount per m² is not checked against the 2025 national minimum and maximum (s. 9; regulations not read); discounts (s. 12 and its regulations) not modelled; a tenant household without a home record is not charged"] else [])

#guard taxAt .perUnit 80 10350 100 == 8280

end IlGlobal
