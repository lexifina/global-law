import TaxKernel.Global
import R5Common

/-!
# Egypt 2025: tax on the profits of juristic persons (1200)

Income Tax Law No 91 of 2005, art. 49 first paragraph as replaced by Presidential Decree-Law No 96 of 2015 (Official
Gazette 34 (cont.) of 20/8/2015, p. 4; ETA scan `sites/default/files/2024-03/law_no.96-2015.pdf`, Wayback 2024-05-22,
`law/eta_law_no.96-2015.pdf`; page image checked): "يقرب وعاء الضريبة إلى أقرب عشرة جنيهات أقل، ويخضع للضريبة بسعر
(22.5%) من صافى الأرباح السنوية". Later amending laws checked for art. 49: Law 30/2023 (refers to art. 49, does not
replace it) and Law 7/2024 (does not touch it). Art. 49's other paragraphs (Suez Canal Authority, EGPC and the Central
Bank 40 %; oil exploration and production 40.55 %) are not computed (flag `art49Special`).
**Grade A**. Not computed: art. 56 bis dividend tax (10 %, 5 % for holdings over 25 % kept two years), losses carried
forward (art. 29, not read here), the Law 6/2025 simplified regime for small enterprises (elective).
-/

namespace EgGlobal
open TaxKernel TaxKernel.Global R5Common

def it : CorpRegime := { name := "الضريبة على أرباح الأشخاص الاعتبارية", sched := Schedule.flat 2250 }

/-- art. 49: the base rounded down to the nearest EGP 10 before the 22.5 % rate (losses brought forward not offset: art. 29 not read). -/
def citBase (co : Company) : Int := divR .down (pos (it.beforeLosses co)) 10 * 10

def profitsTax (co : Company) : Int := divR .down (citBase co * 2250) 10000

/-- Withholding on payments to non-residents. ITL 91/2005 art. 56 (Official Gazette 23 (follow-up) of 9 June 2005,
p. 34, page image checked; ETA Wayback 2025-12-12 of `eta.gov.eg/sites/default/files/2024-03/law_no.91-2005.pdf`):
"تخضع للضريبة بسعر 20% المبالغ التي يدفعها … لغير المقيمين" incl. interest (1), royalties (2) and services (3); third
paragraph replaced by Law 30/2023. Art. 56 bis (Law 30/2023, OG 24 (follow-up) of 15 June 2023, p. 14, page image
checked): dividends to non-resident natural persons and to legal persons 10 %, 5 % where listed on the EGX. -/
def egWht : Wht :=
  { name := "الضريبة المستقطعة من المنبع",
    rules := [{ kind := .interest, rateBp := 2000, statute := "ITL 91/2005 art. 56(1) (20 %)" },
              { kind := .royalty, rateBp := 2000, statute := "ITL 91/2005 art. 56(2) (20 %)" },
              { kind := .services, rateBp := 2000, statute := "ITL 91/2005 art. 56(3) (20 %)" },
              { kind := .dividend, rateBp := 1000, statute := "ITL 91/2005 art. 56 bis (Law 30/2023) (10 %; 5 % if listed)" }] }

def corporate : Family :=
  { name := "1200 الضريبة على أرباح الأشخاص الاعتبارية", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      (if co.flags.contains "art49Special" then [] else [charge .cit it.name (it.beforeLosses co) (fun _ => citBase co) (fun _ => profitsTax co)
        (statute := "ITL 91/2005 art. 49 (22.5 %, Law 96/2015)")]) ++ egWht.charges co }

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true true true true
  ++ (if g.entity == .company && g.company.flags.contains "art49Special" then ["art. 49 special rates (40 %, 40.55 %) not computed"] else [])
  ++ (if g.entity == .company && g.company.dividendsPaid ≠ 0 then ["dividend tax on dividends paid to residents (art. 46 bis / 56 bis) not computed (payments abroad: art. 56 bis 10 % computed)"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .dividend || p.kind == .royalty || p.kind == .interest) then ["withholding: 5 % for EGX-listed shares (art. 56 bis), industrial know-how royalties and long-term loans exempt (art. 56) not distinguished"] else [])

-- 1,000,009 -> 1,000,000 x 22.5 % = 225,000
#guard profitsTax { profit := 1000009 } == 225000
#guard profitsTax { profit := 0 } == 0
#guard egWht.amount { kind := .services, amount := 100000 } == 20000
#guard egWht.amount { kind := .dividend, amount := 100000 } == 10000

end EgGlobal
