import TaxKernel.Global
import R5Common

/-!
# Morocco 2025: IR on rents, dividends and real-estate profits (1100, final rates)

The 1.x model taxes salaries only (it reads none of the household's rents, dividends, interest or gains).
Source: CGI 2025 (`law/cgi2025fr.txt`):
* art. 73-II-B-5° (LF 60-24): 10 % on gross taxable rents (art. 61-I) below 120 000 dirhams; art. 73-II-C-4°: 15 % on
  gross rents of 120 000 dirhams or more (the rate is chosen by the size of the whole amount).
* art. 247-XXXVII-C: dividends ("produits des actions") distributed from 1 January 2025: 12,50 %.
* art. 73-II-F-6°: 20 % on net real-estate profits (art. 61-II), subject to the minimum of art. 144-II-1° (not read:
  not applied).
Not modelled (flagged): gains on shares (art. 73-II-C, F), interest (fixed-income products), main-home exemptions
(art. 63-II).
-/

namespace MaGlobal
open TaxKernel TaxKernel.Global R5Common

def incomesOf (g : CanonGlobal) (k : IncomeKind) : Int := isum ((g.incomes.filter (·.kind == k)).map (·.amount))

def rentTax (gross : Int) : Int := if gross < 120000 then divR .down (1000 * pos gross) BP else divR .down (1500 * gross) BP

def capital : Family :=
  { name := "1100 IR revenus fonciers, dividendes, profits fonciers", covers := [],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      let rent := g.household.rentalIncome + incomesOf g .rent
      let div := g.household.dividends + incomesOf g .dividend
      let props := g.disposals.filter (·.kind.isRealEstate)
      (if rent ≠ 0 then [charge .pit "IR revenus fonciers" rent id rentTax (event := "rents")
          (statute := "CGI art. 73-II-B-5° (10 % below 120 000), 73-II-C-4° (15 %)")] else [])
      ++ (if div ≠ 0 then [charge .pit "IR produits des actions" div pos (fun x => divR .down (1250 * x) BP) (event := "dividends")
          (statute := "CGI art. 247-XXXVII-C (12,50 % from 1 January 2025)")] else [])
      ++ (props.zipIdx.map fun (d, i) =>
          charge .pit "IR profits fonciers" (d.proceeds - d.cost - d.costs) pos (fun x => divR .down (2000 * x) BP)
            (event := s!"disposal {i + 1}") (statute := "CGI art. 73-II-F-6° (20 %); art. 144-II-1° minimum not applied")) }

def capitalUnsupported (g : CanonGlobal) : List String :=
  (if g.disposals.any (·.kind.isShares) then ["gains on shares (art. 73-II-C, F) not modelled"] else [])
  ++ (if g.household.interest ≠ 0 then ["interest (fixed-income products) withholding not modelled"] else [])
  ++ (if g.disposals.any (fun d => d.kind.isRealEstate && d.mainHome) then ["main-home exemption (art. 63-II) not applied"] else [])

#guard rentTax 119999 == 11999
#guard rentTax 120000 == 18000

end MaGlobal
