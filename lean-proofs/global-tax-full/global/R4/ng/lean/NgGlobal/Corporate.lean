import R4Common

/-!
# Nigeria 2025: corporate income tax (1200) and withholding (generated from `R4/specs/ng.json`)

No usable 2025 text for these headings: only Finance Act OCR fragments (2019-2023) are held; the 2025 consolidations (CITA, VAT Act) and the Nigeria Tax Act 2025 are not. Pass 9 (CIT): Finance Act 2019 (official gazette, firs.gov.ng/wp-content/uploads/2021/02/finance-act-2019-official-gazette-1.pdf via Wayback) and Finance Act 2021 (firs.gov.ng/wp-content/uploads/2022/04/Finance-Act-2021-Gazetted.pdf via Wayback), OCR (tesseract eng) in `R4/fetch/ng9/` (SHA256SUMS); Finance Act 2020 and 2023 OCR already held (`world/B02-g20/ng/law/`); Finance Act 2023 Part III amends CITA s. 14, 32, 34, 37 and the Second Schedule only. Finance Act 2022 not held (flagged). The Nigeria Tax Act 2025 applies from 2026. Thirteenth pass: FIRS public notice on withholding tax (Wayback copy of firs.gov.ng PUBLIC-NOTICE-ON-WHT-3.pdf, PDF dated 2015-06-10; `R4/fetch/p13/ng_wht_notice.pdf`) section 3 'Prevailing tax rates for WHT payments' (CITA Cap. C21 and the WHT regulations; final tax for non-residents). Fourteenth pass: Deduction of Tax at Source (Withholding) Regulations 2024, gazette copy (14 pages) saved as `R4/fetch/p14/ng_wht_regs2024.pdf`.

Finance Act 2019 s. 16: "Substitute for section 40 of CITA, a new section '40'— 40. There shall be levied and paid for each year of assessment in respect of total profits of every company, tax as follows, in the case of a— (a) small company, tax as provided under section 23 (1)(o) of this Act; (b) medium-sized company, tax at the rate of 20 Kobo for every Naira ; and (c) large company, tax at the rate of 30 Kobo for every Naira." Definitions: "'large company' means any company which is not a small or medium-sized company"; "'medium-sized company' means a company that earns gross turnover greater than N25,000,000 but less than N100,000,000"; "'small company' means a company that earns gross turnover of N25,000,000 or less." s. 14 (b): s. 33 (3) "(b) a company that earns gross turnover of less than N25,000,000 in the relevant year of assessment." Finance Act 2021 s. 10: "(2) For the purpose of subsection (1), the minimum tax to be levied and paid shall be 0.5% of gross turnover of the company less franked investment income: Provided that— (a) the applicable minimum tax is reduced to 0.25% for tax returns prepared and filed with respect to financial years ending on any date between 1 January 2020 and 31 December 2021".

First Schedule, non-resident recipients (corporate / non-corporate): dividend, interest 10 / 10; royalty 10 / 5; commission, consultancy, technical, management and professional fees 10 / 10 ('Higher rate for non-residents to serve as final tax'); supply of other services 5 / 5. Fourteenth pass (replaces the 2015 FIRS notice table).
-/

namespace NgGlobal
open TaxKernel TaxKernel.Global

def citB0 : CorpRegime :=
  { name := "Companies income tax (small company: profits exempt, s. 23 (1) (o))", sched := Schedule.flat 0, lossFull := -1, lossExcessBp := 10000 }

def minB0 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
def citB1 : CorpRegime :=
  { name := "Companies income tax (medium-sized company: 20 kobo per naira)", sched := Schedule.flat 2000, lossFull := -1, lossExcessBp := 10000 }

def minB1 : R4.MinTax := { bp := 50, fixed := 0, floor := 0, cap := -1, onAssets := false }
def citB2 : CorpRegime :=
  { name := "Companies income tax (large company: 30 kobo per naira)", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minB2 : R4.MinTax := { bp := 50, fixed := 0, floor := 0, cap := -1, onAssets := false }
/-- the band is chosen by the company's turnover -/
def citPick (co : Company) : CorpRegime × R4.MinTax :=
  if co.turnover ≤ 25000000 then (citB0, minB0) else if co.turnover ≤ 99999999 then (citB1, minB1) else (citB2, minB2)
#guard (let co : Company := { profit := 1250000, turnover := 12500000, lossesForward := 0 }; R4.corpTax (citPick co).1 (citPick co).2 co 1) == 0
#guard (let co : Company := { profit := 0, turnover := 12500000, lossesForward := 0 }; R4.corpTax (citPick co).1 (citPick co).2 co 1) == 0
#guard (let co : Company := { profit := 1250000, turnover := 25000000, lossesForward := 2500000 }; R4.corpTax (citPick co).1 (citPick co).2 co 1) == 0
#guard (let co : Company := { profit := 6250000, turnover := 62500000, lossesForward := 0 }; R4.corpTax (citPick co).1 (citPick co).2 co 1) == 1250000
#guard (let co : Company := { profit := 0, turnover := 62500000, lossesForward := 0 }; R4.corpTax (citPick co).1 (citPick co).2 co 1) == 312500
#guard (let co : Company := { profit := 6250000, turnover := 99999999, lossesForward := 12500000 }; R4.corpTax (citPick co).1 (citPick co).2 co 1) == 499999
#guard (let co : Company := { profit := 20000100, turnover := 200001000, lossesForward := 0 }; R4.corpTax (citPick co).1 (citPick co).2 co 1) == 6000030
#guard (let co : Company := { profit := 0, turnover := 200001000, lossesForward := 0 }; R4.corpTax (citPick co).1 (citPick co).2 co 1) == 1000005
#guard (let co : Company := { profit := 20000100, turnover := 200001000, lossesForward := 40000200 }; R4.corpTax (citPick co).1 (citPick co).2 co 1) == 1000005
def whtR : Wht :=
  { name := "Withholding tax (CITA, PITA; Withholding Regulations 2024)",
    rules := [{ kind := .dividend, rateBp := 1000, statute := "Deduction of Tax at Source (Withholding) Regulations 2024 (S.I. No. 34 of 2024, Official Gazette No. 168 Vol. 111 of 2 October 2024, Government Notice No. 37; effective 1 January 2025) reg. 3 (a) and First Schedule, non-resident columns (gazette copy via Wayback 2025-02-18, `R4/fetch/p14/ng_wht_regs2024.pdf`): Dividend, Interest 10 % (corporate and non-corporate, non-resident)" },
              { kind := .interest, rateBp := 1000, statute := "Deduction of Tax at Source (Withholding) Regulations 2024 (S.I. No. 34 of 2024, Official Gazette No. 168 Vol. 111 of 2 October 2024, Government Notice No. 37; effective 1 January 2025) reg. 3 (a) and First Schedule, non-resident columns (gazette copy via Wayback 2025-02-18, `R4/fetch/p14/ng_wht_regs2024.pdf`): Dividend, Interest 10 % (corporate and non-corporate, non-resident)" },
              { kind := .royalty, rateBp := 1000, toCompany := some true, statute := "Deduction of Tax at Source (Withholding) Regulations 2024 (S.I. No. 34 of 2024, Official Gazette No. 168 Vol. 111 of 2 October 2024, Government Notice No. 37; effective 1 January 2025) reg. 3 (a) and First Schedule, non-resident columns (gazette copy via Wayback 2025-02-18, `R4/fetch/p14/ng_wht_regs2024.pdf`): Royalty 10 % (corporate, non-resident)" },
              { kind := .royalty, rateBp := 500, toCompany := some false, statute := "Deduction of Tax at Source (Withholding) Regulations 2024 (S.I. No. 34 of 2024, Official Gazette No. 168 Vol. 111 of 2 October 2024, Government Notice No. 37; effective 1 January 2025) reg. 3 (a) and First Schedule, non-resident columns (gazette copy via Wayback 2025-02-18, `R4/fetch/p14/ng_wht_regs2024.pdf`): Royalty 5 % (non-corporate, non-resident)" },
              { kind := .services, rateBp := 1000, statute := "Deduction of Tax at Source (Withholding) Regulations 2024 (S.I. No. 34 of 2024, Official Gazette No. 168 Vol. 111 of 2 October 2024, Government Notice No. 37; effective 1 January 2025) reg. 3 (a) and First Schedule, non-resident columns (gazette copy via Wayback 2025-02-18, `R4/fetch/p14/ng_wht_regs2024.pdf`): Commission, consultancy, technical, management and professional fees 10 % (corporate and non-corporate, non-resident)" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 100000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 100000
#guard whtR.amount { kind := .royalty, amount := 1000000, toCompany := true } == 100000
#guard whtR.amount { kind := .royalty, amount := 1000000, toCompany := false } == 50000
#guard whtR.amount { kind := .services, amount := 1000000 } == 100000
def corporate : Family :=
  { name := "1200 Companies income tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge (citPick g.company).1 (citPick g.company).2 g.company "CITA Cap. C21 s. 40 as substituted by Finance Act 2019 s. 16 (small company: exempt under s. 23 (1) (o); medium-sized company 20 kobo per naira; large company 30 kobo per naira), s. 105 definitions (small: gross turnover N25,000,000 or less; medium: greater than N25,000,000 but less than N100,000,000); minimum tax s. 33 (2) as substituted by Finance Act 2021 s. 10 (0,5 % of gross turnover less franked investment income; 0,25 % only for 2020-2021) and s. 33 (3) (b) (Finance Act 2019 s. 14: not applicable below N25,000,000)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["Finance Act 2022 not held (flagged); the 2025 rates rest on FA 2019 (s. 40), FA 2021 (s. 33) and FA 2023 (no change to s. 23, 33 or 40)", "franked investment income is not deducted from the minimum-tax base; the four-year start-up exclusion and the other s. 33 (3) exclusions are not modelled; tertiary education tax (3 %) and other levies on profits are separate taxes, not modelled here", "services: the Schedule's consultancy / technical / management / professional fees line (10 %) is applied to every service payment abroad; 'supply or rendering of services other than those specifically listed' is 5 % (not distinguished)", "fourteenth pass: 2024 Regulations (gazetted, effective 1 January 2025) replace the 2015 FIRS notice; services to non-resident individuals 5 % -> 10 %"]

end NgGlobal
