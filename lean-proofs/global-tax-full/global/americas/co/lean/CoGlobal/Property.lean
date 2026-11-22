import CoGlobal.Pit

/-!
# Colombia 2025: impuesto al patrimonio (4200); inheritances grade C

Source: Estatuto Tributario (Secretaría del Senado consolidation updated 15 Nov 2026, local copy
`co/law/et/estatuto_tributario_pr012.txt`), Libro I Título II-A as added by Ley 2277 de 2022 arts. 35-39:
* **Art. 292-3 (1)**: subject: "Las personas naturales y las sucesiones ilíquidas, contribuyentes del impuesto sobre la
  renta" (numeral 6, companies, applies "Para la vigencia 2026" only: no company charge in 2025).
* **Art. 294-3**: the tax arises on wealth held on 1 January "cuyo valor sea igual o superior a setenta y dos mil
  (72.000) UVT"; patrimonio = patrimonio líquido (gross wealth less debts).
* **Art. 295-3**: base = gross wealth less debts on 1 January; "En el caso de las personas naturales, se excluyen las
  primeras doce mil (12.000) UVT del valor patrimonial de su casa o apartamento de habitación".
* **Art. 296-3**: table: 0 % to 72.000 UVT; 0,5 % to 122.000; 1,0 % to 239.000 (+250 UVT); 1,5 % above (+1.420 UVT);
  "La tarifa del uno coma cinco por ciento (1,5%) sólo aplicará de manera temporal durante los años 2023, 2024, 2025 y
  2026".
UVT 2025 = 49.799 (the 1.x model's `CoTax.uvt`). The entry test reads the net wealth before the home exclusion, the
table the base after it. Assets at the given (statutory where given) values; the special valuation rules of art. 295-3
par. 3 (unlisted shares, trusts) are not applied. The household's wealth is taxed as one person's (no split between
spouses: each spouse is a separate taxpayer; flagged).
-/

namespace CoGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon CoGlobal

def uvt : Int := CoTax.uvt

def wtScale : Schedule := Schedule.ofList [(0, 0), (72000 * uvt, 50), (122000 * uvt, 100), (239000 * uvt, 150)]

/-- patrimonio líquido (art. 294-3) and the base after the home exclusion (art. 295-3). -/
def liquid : WealthTax := { name := "Impuesto al patrimonio", sched := wtScale }
def wt : WealthTax := { name := "Impuesto al patrimonio", homeExempt := 12000 * uvt, sched := wtScale }

def wtDue (as : List Asset) : Int := if liquid.netWealth as < 72000 * uvt then 0 else wt.gross as

def wealthF : Family :=
  { name := "4200 impuesto al patrimonio", covers := [.wealth],
    run := fun _ g _ =>
      if g.entity == .company || g.assets.isEmpty then [] else
      [charge .wealth wt.name (liquid.netWealth g.assets) (fun _ => wt.base g.assets) (fun _ => wtDue g.assets)
        (event := "1 January 2025") (statute := "ET arts. 292-3, 294-3 (72.000 UVT), 295-3 (home 12.000 UVT), 296-3 (0.5/1/1.5 %)")] }

def families : List Family := [wealthF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (!g.assets.isEmpty && g.entity != .company) "impuesto al patrimonio on the household's assets as one taxpayer's (spouses not split); special valuation rules of ET art. 295-3 par. 3 not applied"

#guard uvt == 49799
#guard wtDue [{ kind := .home, value := 1000000000 }] == 0
#guard wtDue [{ kind := .deposits, value := 10000000000 }] == wtScale.tax {} 10000000000
#guard wtScale.tax {} (122000 * uvt) == 250 * uvt
#guard wtScale.tax {} (239000 * uvt) == 1420 * uvt

end CoGlobal.Property
