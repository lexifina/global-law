import TaxKernel.Global
import R5Common

/-!
# Georgia 2025: profit tax (1200), distribution model

Tax Code of Georgia (Law No 3591 of 17 September 2010), official English translation on matsne.gov.ge
(document 1043717, consolidated version of 28/10/2026 fetched 2026-11-21, extract `law/matsne_1043717_en_art97-98.txt`):
* art. 97(1): the object of profit taxation of a resident enterprise is (a) the distributed profit, (b) expenses or
  other payments not related to the economic activity, (c) free supplies and transfers, (d) representation expenses
  above the limit; art. 97(10): "the amount subject to profit taxation shall be calculated by dividing the sum of a
  disbursement made/expense paid ... by 0.85". Art. 97 was last amended by Law No 4364 (website 11.7.2024): the
  wording applies to the whole of 2025.
* art. 98(1): "The profit tax rate shall be 15%", except (2) pre-1998 oil and gas agreements 10 %, (4) banking
  institutions, credit unions, microfinance organisations and loan providers 20 % on taxable profit, (5)-(6) gambling.
  Last amendment Law No 134 of 13 December 2024 (website 29.12.2024): in force for 2025.
* art. 98¹(1): distributed profit is a profit distributed to a partner as a dividend, in money or in kind.

Inputs: `dividendsPaid` (art. 97(1)(a)) and `addBacks`, read as art. 97(1)(b)-(d) payments (expenses unrelated to
the economic activity, free supplies, representation expenses above the limit). Tax = 15 % × (amount / 0.85),
each step rounded down. The financial-sector (art. 98(4): taxable profit at 20 %, flag `bank`) and gambling regimes
are not computed. **Grade A** (statute text read; consolidated official translation, amendment notes checked).
-/

namespace GeGlobal
open TaxKernel TaxKernel.Global R5Common

/-- art. 97(10): the amount subject to profit tax, the disbursement divided by 0.85. -/
def grossUp (x : Int) : Int := divR .down (pos x * 100) 85

def profitTax (amount : Int) : Int := divR .down (grossUp amount * 1500) 10000

/-- Withholding at source on a non-resident's Georgian-source income (Tax Code art. 134(1); matsne English
consolidation, Wayback 2025-12-21, `law/matsne_1043717_en_full_cap20251221.txt`). -/
def geWht : Wht :=
  { name := "გადასახადი გადახდის წყაროსთან (withholding)",
    rules := [{ kind := .dividend, rateBp := 500, statute := "Tax Code art. 134(1)(a), 130(1) (5 %)" },
              { kind := .interest, rateBp := 500, statute := "Tax Code art. 134(1)(b), 131(1) (5 %)" },
              { kind := .royalty, rateBp := 500, statute := "Tax Code art. 134(1)(b1) (5 %)" },
              { kind := .services, rateBp := 1000, statute := "Tax Code art. 134(1)(e) other Georgian-source amounts (10 %)" }] }

def corporate : Family :=
  { name := "1200 მოგების გადასახადი", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      (if g.company.flags.contains "bank" then [] else
      [charge .cit "მოგების გადასახადი (profit tax)" (g.company.dividendsPaid + g.company.addBacks) grossUp profitTax
        (statute := "Tax Code art. 97(1), 97(10) (÷ 0.85), 98(1) (15 %), 98¹")])
      ++ geWht.charges g.company }

def corporateUnsupported (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.flags.contains "bank" then
    ["profit tax: art. 98(4) financial institutions (20 % on taxable profit, art. 97(9¹)) not computed"] else [])
  ++ (if g.company.paymentsAbroad.isEmpty then [] else
    ["withholding: art. 134(1¹) 15 % to persons in preferential-tax countries and the art. 130/131 exemptions (e.g. interest of licensed financial institutions) not applied"])

-- a dividend of 850 000: 850 000 / 0.85 = 1 000 000, tax 150 000
#guard profitTax 850000 == 150000
#guard grossUp 85 == 100
#guard profitTax 0 == 0
#guard geWht.amount { kind := .services, amount := 100000 } == 10000
#guard geWht.amount { kind := .dividend, amount := 100000 } == 5000

end GeGlobal
