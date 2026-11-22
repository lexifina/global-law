import TaxKernel.Global
import R5Common

/-!
# Azerbaijan 2025: profit tax of enterprises (1200)

Tax Code of the Republic of Azerbaijan (Vergi Məcəlləsi), State Tax Service consolidated PDF
`taxes.gov.az/files/2/vergi-mecellesi/VM_new2019.pdf` (PDF dated 27/11/2019; Wayback 2025-12-07, `law/az_vm_2019.pdf`):
* art. 105.1: "Müəssisələrin mənfəətindən 20 faiz dərəcəsi ilə vergi tutulur" (20 % of the profit of enterprises);
  105.2: non-residents without a permanent establishment at the art. 125 source rates (not computed);
* art. 121.1: losses carried forward up to five years, offset without yearly limit (input `lossesForward` taken as
  within the five years).
Dating: the official consolidated text of the Ministry of Justice's legal database (e-qanun.az, framework id 46948,
`api.e-qanun.az/framework/46948` names it; HTML `e-qanun.az/frameworks/46/f_46948.html` read from Wayback captures of
4/12/2024 and 24/8/2026, extract `law/eqanun_46948_art105_121.txt`): art. 105.1 and 121.1 read the same in both
(amendment notes [757]/[800], [821]/[877] renumbered only), so the wording governs all of 2025. The 2019 STS PDF and
the STS 2025 Q&A booklet on Law 98-VIIQD agree. **Grade A** (official consolidated text dated on both sides of 2025).
Exemptions of art. 106 are not computed.
-/

namespace AzGlobal
open TaxKernel TaxKernel.Global R5Common

def azRegime (_ : Company) : CorpRegime := { name := "Mənfəət vergisi", sched := Schedule.flat 2000 }

/-- Tax at source on a non-resident's Azerbaijani-source income (art. 125.1; e-qanun Wayback captures 2024-12-04 and
2026-08-24, identical for these articles: `law/eqanun_46948_art122-125.txt`). -/
def azWht : Wht :=
  { name := "Ödəmə mənbəyində vergi",
    rules := [{ kind := .dividend, rateBp := 500, statute := "Vergi Məcəlləsi 125.1.1, 122.1 (5 %)" },
              { kind := .interest, rateBp := 1000, statute := "Vergi Məcəlləsi 125.1.2, 123.1 (10 %)" },
              { kind := .royalty, rateBp := 1400, statute := "Vergi Məcəlləsi 125.1.7, 124.1 (14 %)" },
              { kind := .rent, rateBp := 1400, statute := "Vergi Məcəlləsi 125.1.7, 124.1 (14 %)" },
              { kind := .services, rateBp := 1000, statute := "Vergi Məcəlləsi 125.1.5 works and services (10 %)" }] }

def corporate : Family :=
  corpFamily "1200 Mənfəət vergisi" azRegime (fun _ => "Vergi Məcəlləsi 105.1 (20 %), 121.1 (losses, 5 years)") azWht

def corporateUnsupported (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services) then
    ["withholding on services: art. 125.1.5 10 % taken; international transport/telecom (125.1.4, 6 %) and insurance (125.1.3, 4 %) not distinguished"] else [])
  ++ (if g.entity == .company && !g.company.flags.isEmpty then
    ["art. 106 exemptions and the 2025 incentive regimes (Law 98-VIIQD) not computed"] else [])
  ++ corpInputsUnread g false true true false

#guard (azRegime {}).citTax { profit := 1000000 } == 200000
#guard azWht.amount { kind := .royalty, amount := 100000 } == 14000
#guard (azRegime {}).citTax { profit := 1000000, lossesForward := 400000 } == 120000

end AzGlobal
