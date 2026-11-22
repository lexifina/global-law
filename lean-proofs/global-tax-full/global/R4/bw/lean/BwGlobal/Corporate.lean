import R4Common

/-!
# Botswana 2025: corporate income tax (1200) and withholding (generated from `R4/specs/bw.json`)

No usable 2025 text for these headings: the held income tax text is the new Act applying from 2026 (ita_amend_2026.txt: non-resident WHT dividends 10 %, interest 15 %, royalties 15 %, technical fees 15 %); the 2025 text and the VAT Act are not held. Pass 10 (CIT/WHT): BURS pages via Wayback (`web.archive.org/web/20250419134746id_/http://www.burs.org.bw/index.php/tax/income-tax/companies`, `…/20250917234502id_/…/tax/income-tax/other-withholding-taxes`), saved in `R4/fetch/bw10/`. The BURS site keeps stale pages: its VAT page (Wayback 26 Mar 2025) still prints a 12 % standard rate, and the withholding page refers to Additional Company Tax (pre-2011), so only statements that the Income Tax Act 2026 (`world/B09-southern-africa/bw/law/ita_amend_2026.txt`, Schedule 1, from 1 July 2026) does not contradict are used. The tax-rates page answers a bot-verification page (not bypassed).

BURS 'Companies' page (captured 19 April 2025): companies pay 22 % if resident and 30 % if not; approved manufacturing and IFSC companies pay 15 %, and pension and provident funds the Commissioner has not approved 7.5 %.

BURS 'Other Withholding Taxes' (captured 17 September 2025): management and consultancy fees (s. 58 and the Seventh Schedule), commercial royalties and interest paid to a non-resident bear a final 15 % of the gross amount. The Income Tax Act 2026 Schedule 1 (from 1 July 2026) keeps 15 % for interest, royalties and technical fees. Twelfth pass (kernel 2.3.0 grade-C withholding): dividend 15 %: ITA Cap. 52:01 s. 58, Seventh Schedule para 2 (b) (15 % on each dividend paid to a non-resident; BURS 'Withholding Taxes' 2025: 15 %, final)
-/

namespace BwGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Company tax", sched := Schedule.flat 2200, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2200219
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 220000
def whtR : Wht :=
  { name := "Withholding tax on payments to non-residents (s. 58, Seventh Schedule)",
    rules := [{ kind := .services, rateBp := 1500, statute := "s. 58, Seventh Schedule (BURS): management and consultancy fees to non-residents 15 %" },
              { kind := .royalty, rateBp := 1500, statute := "s. 58, Seventh Schedule (BURS): commercial royalties to non-residents 15 %" },
              { kind := .interest, rateBp := 1500, statute := "s. 58, Seventh Schedule (BURS): interest to non-residents 15 %" },
              { kind := .dividend, rateBp := 1500, statute := "ITA Cap. 52:01 s. 58, Seventh Schedule para 2 (b) (15 % on each dividend paid to a non-resident; BURS 'Withholding Taxes' 2025: 15 %, final)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Company tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Income Tax Act Cap. 52:01 (rate as stated by BURS 'Companies', Wayback 19 Apr 2025): resident companies 22 %" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["official secondary source; other BURS pages are stale (VAT 12 %, Additional Company Tax), so the 22 % statement is flagged; the Income Tax Act 2026 (from 1 July 2026) sets 24.5 % for other companies and does not apply to 2025", "manufacturing and IFSC companies (15 %) and non-resident companies (30 %) are not modelled", "dividends are not modelled: the BURS page prints 15 % next to a pre-2011 Additional Company Tax paragraph, while the Income Tax Act 2026 prints 10 %; the 2025 rate is not established", "official secondary source"]

end BwGlobal
