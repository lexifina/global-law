import TaxKernel.Global
import R5Common

/-!
# Egypt 2025: tax on built real estate (الضريبة على العقارات المبنية, 4100)

Law No. 196 of 2008 issuing the Built Real Estate Tax Law (ETA PDF `2024-10/law-196-2008.pdf`, Wayback 2025-09-16,
Arabic OCR `mena3j_dl/ocr/eg196.ocr.txt`), as amended by Decree-Law No. 117 of 2014 (text as published by the Real
Estate Tax Authority, `rta.gov.eg/sites/default/files/2022-03/تعديلات قانون 117 لسنة 2014.pdf`, `law/eg_rta_117_2014.*`):
* art. 12: the rate is **10 %** of the annual rental value of the taxable property, after excluding **30 %** of that
  value for premises used for dwelling and **32 %** for other premises (all costs, maintenance included);
* art. 18(1)(د) as replaced by Law 117/2014: the unit the taxpayer uses as his main private dwelling (and his family's)
  is exempt where its **net annual rental value is under EGP 24 000; the excess is taxed**; (هـ) a commercial,
  industrial, administrative or professional unit under EGP 1 200 net, the excess taxed.
Law No. 3 of 2026 (main-dwelling exemption EGP 100 000) was ratified in 2026 and does not govern 2025.
Model (owner): `home` = the main dwelling: 10 % × (70 % of `annualValue` − 24 000)⁺; `realEstate` = another dwelling:
10 % × 70 % of `annualValue` (no exemption). **Grade A** (statute texts read; the OCR of art. 12 garbles the digits of
10/30/32 %, which the article's structure and the 2014 amendment confirm).
-/

namespace EgGlobal
open TaxKernel TaxKernel.Global R5Common

/-- art. 12: net annual rental value (dwelling: less 30 %; other premises: less 32 %). -/
def netRental (dwelling : Bool) (v : Int) : Int := divR .down (pos v * (if dwelling then 7000 else 6800)) BP

/-- art. 12 + 18(1)(د) (Law 117/2014): 10 % of the net value above the exempt amount. -/
def builtTax (exempt : Int) (net : Int) : Int := divR .down (pos (net - exempt) * 1000) BP

def property : Family :=
  { name := "4100 الضريبة على العقارات المبنية", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      g.assets.zipIdx.filterMap fun (a, i) =>
        if a.kind == .home && a.annualValue ≥ 0 then
          some (charge .propertyRecurrent "الضريبة على العقارات المبنية (سكن خاص رئيسي)" a.annualValue (netRental true)
            (builtTax 24000) (event := s!"property {i + 1}") (level := .central)
            (statute := "Law 196/2008 art. 12 (10 % after excluding 30 %), art. 18(1)(د) as replaced by Law 117/2014 (main dwelling: net annual rental value up to EGP 24 000 exempt, excess taxed)"))
        else if a.kind == .realEstate && a.annualValue ≥ 0 then
          some (charge .propertyRecurrent "الضريبة على العقارات المبنية" a.annualValue (netRental true)
            (builtTax 0) (event := s!"property {i + 1}") (level := .central)
            (statute := "Law 196/2008 art. 12 (10 % of the annual rental value after excluding 30 % for dwellings)"))
        else none }

def propertyUnsupported (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => (a.kind == .home || a.kind == .realEstate) && a.annualValue < 0) then
    ["4100 built real estate tax: a building without `annualValue` (the committees' annual rental value) is not computed (grade C)"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate) then
    ["4100 built real estate tax: `realEstate` taken as a dwelling (30 % exclusion); premises for other uses (32 % exclusion, EGP 1 200 exemption per unit, art. 18(1)(هـ)) not distinguished"] else [])

#guard netRental true 60000 == 42000
#guard builtTax 24000 42000 == 1800
#guard builtTax 24000 20000 == 0
#guard builtTax 24000 30000 == 600
#guard builtTax 0 (netRental true 20000) == 1400

end EgGlobal
