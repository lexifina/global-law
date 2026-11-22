import R4Common

/-!
# Botswana 2025: VAT (5111) and excises (5121) (generated from `R4/specs/bw.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: the held income tax text is the new Act applying from 2026 (ita_amend_2026.txt: non-resident WHT dividends 10 %, interest 15 %, royalties 15 %, technical fees 15 %); the 2025 text and the VAT Act are not held. Pass 10 (CIT/WHT): BURS pages via Wayback (`web.archive.org/web/20250419134746id_/http://www.burs.org.bw/index.php/tax/income-tax/companies`, `…/20250917234502id_/…/tax/income-tax/other-withholding-taxes`), saved in `R4/fetch/bw10/`. The BURS site keeps stale pages: its VAT page (Wayback 26 Mar 2025) still prints a 12 % standard rate, and the withholding page refers to Additional Company Tax (pre-2011), so only statements that the Income Tax Act 2026 (`world/B09-southern-africa/bw/law/ita_amend_2026.txt`, Schedule 1, from 1 July 2026) does not contradict are used. The tax-rates page answers a bot-verification page (not bypassed).

Secondary-source sweep (2026-11-22): both guides put the standard rate at 14 %. Deloitte names as exempt: education, non-fee financial services, residential lettings, passenger transport other than tourist transport, prescription medicines and medical services (public or private); zero-rated: exports, some foodstuffs, LPG, farm fertiliser and some pesticides. PwC gives a BWP 1 million registration threshold. The BURS VAT page as captured on 26 March 2025 shows 12 %, which neither 2025 guide supports (taken as stale; recorded as a disagreement). Grade B: the Act was not read.


-/

namespace BwGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1400, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .education | .rent | .medicines | .health | .transport | .financial => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Value Added Tax Act Cap. 50:03 (Act not read). Rate and exemptions from two professional guides dated 2025 (facts only): PwC Worldwide Tax Summaries, Botswana, Corporate - Other taxes, section 'Value-added tax (VAT)', last reviewed 25 September 2025 (Wayback capture 2025-12-16, R4/fetch/swp/pwc_bw_corpother_wb20251216.txt; same 14 % in Individual - Other taxes, capture 2025-11-21); Deloitte International Tax, Botswana Highlights 2025 (updated January 2025), 'Value added tax' (R4/fetch/swp/deloitte_bw_2025.txt)"

-- the standard rate as printed: 14 % inside a tax-inclusive 11400
#guard vatX.embedded { good := .other, amount := 11400 } == 1400
#guard vatX.embedded { good := .education, amount := 10000 } == 0
#guard vatX.embedded { good := .rent, amount := 10000 } == 0
#guard vatX.embedded { good := .medicines, amount := 10000 } == 0

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["exempt here: education, residential rent, medicines, health, passenger transport, financial services (Deloitte 2025 list); fee-based financial services, over-the-counter medicines and tourist transport are taxable in the guide but cannot be told apart in the input", "zero-rated foodstuffs ('some foodstuffs' in the guide, no list): food is charged at 14 %", "excises not modelled: Botswana's own Schedule No. 1 Part 2A is not held: BURS's archived 'Tariff Volume I July 2025' holds Part 1 (customs) only and the Volume II captures are HTML stubs; no BURS statement that the SACU common rates apply was found"]

end BwGlobal
