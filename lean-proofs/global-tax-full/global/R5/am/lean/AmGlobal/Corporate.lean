import TaxKernel.Global
import R5Common

/-!
# Armenia 2025: profit tax (շահութահարկ, 1200) and withholding on non-residents

Source: Tax Code ՀՕ-165-Ն as in force on 2025-07-01 (Global law, `law/gl_cit_2025-07-01.txt`).
* art. 125(1): residents and permanent establishments: "շահութահարկը հաշվարկվում է 18 տոկոս դրույքաչափով".
* art. 125(4), non-residents without a permanent establishment: 1) insurance, reinsurance and freight 5 %;
  2) passive income (interest, royalties, rent) 10 %; 3.1) dividends 5 %; 5) other Armenian-source income 20 %.
* art. 114: interest deductible only on borrowings up to "սեփական կապիտալի դրական մեծության կրկնապատիկը" (twice the
  positive equity; nine times for banks): thin capitalisation at 200 %.
* art. 254-258: the turnover tax regime (elective, turnover up to 115 million) is not modelled.
-/

namespace AmGlobal
open TaxKernel TaxKernel.Global R5Common

def profitTax : CorpRegime := { name := "Շահութահարկ", sched := Schedule.flat 1800, thinCapPct := 200 }

def whtNonResident : Wht :=
  { name := "Շահութահարկ (ոչ ռեզիդենտ, աղբյուրից)",
    rules := [{ kind := .dividend, rateBp := 500, statute := "Tax Code art. 125(4)(3.1) (5 %)" },
              { kind := .interest, rateBp := 1000, statute := "Tax Code art. 125(4)(2) passive income (10 %)" },
              { kind := .royalty, rateBp := 1000, statute := "Tax Code art. 125(4)(2) passive income (10 %)" },
              { kind := .rent, rateBp := 1000, statute := "Tax Code art. 125(4)(2) passive income (10 %)" },
              { kind := .services, rateBp := 2000, statute := "Tax Code art. 125(4)(5) other income (20 %)" },
              { kind := .other, rateBp := 2000, statute := "Tax Code art. 125(4)(5) other income (20 %)" }] }

def corporate : Family :=
  corpFamily "1200 շահութահարկ" (fun _ => profitTax) (fun _ => "Tax Code art. 125(1) (18 %), art. 114 (thin cap 2 × equity)") whtNonResident

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true false false true
  ++ (if g.entity == .company && g.company.flags.contains "turnoverTax" then ["turnover tax regime (art. 254-263) not modelled"] else [])

#guard profitTax.citTax { profit := 1000000 } == 180000
-- thin cap: debt 300, equity 100: interest on the 100 above 2 × equity is not deductible (1/3 of 30)
#guard profitTax.interestDisallowed { profit := 0, interestExpense := 30, debt := 300, equity := 100 } == 10
#guard whtNonResident.amount { kind := .dividend, amount := 1000000 } == 50000
#guard whtNonResident.amount { kind := .royalty, amount := 1000000 } == 100000

end AmGlobal
