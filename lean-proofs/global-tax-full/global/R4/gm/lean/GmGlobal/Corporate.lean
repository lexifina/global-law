import R4Common

/-!
# Gambia 2025: corporate income tax (1200) and withholding (generated from `R4/specs/gm.json`)

Sources: Gambia Revenue Authority VAT leaflet (registry fetch `global/registry/afm_data/fetch/GM/gm_vat.pdf.txt`, official secondary). Pass 10 (CIT/WHT): GRA brochures fetched from www.gra.gm/download-file/<id> (ids from `world/B10-anglophone-africa/gm/law/rescue2/gra_downloads.html`): 8d0c7954 'Corporation Income Tax', 8d0d0925 'Witholding Tax', 8d0c84c3 'Dividend Income Tax', in `R4/fetch/gm10/` (SHA256SUMS).

GRA brochure 'Corporation Income Tax' (published 21 Aug 2023): "3. What is the Corporation Tax Rate? The Corporation tax rate is the higher of: • 27% of net profit (2018) or • 1% of turnover on audited accounts (2% of turnover for unaudited accounts)." Worked example: "if X & Co. Ltd.'s turnover in 2018 is D5 million and the company's net profit is D1.5 million, then the company's tax liability ... will be D405,000"; "Losses carried forward within six years".

GRA brochure 'Withholding Tax on Contract Payments': "The following are the types of withholding tax; • 10% for payments to non-resident Contractors, Suppliers or Service Providers ..."; "9. Is the Payments Made a Final Tax? For non-resident contractors and subcontractors, the tax withheld is a final tax." GRA brochure 'Dividend Income Tax': "All resident companies or partnerships are liable to withheld dividend income tax on all dividend payments to resident and non-resident shareholders or partners. ... The dividend income tax rate is 15% of the gross amount of dividend paid."
-/

namespace GmGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Corporation income tax", sched := Schedule.flat 2700, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 100, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2700269
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 10000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 200000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 4000000
def whtR : Wht :=
  { name := "Withholding tax on payments to non-residents",
    rules := [{ kind := .services, rateBp := 1000, statute := "GRA 'Withholding Tax' brochure: non-resident contractors, suppliers or service providers 10 % (final)" },
              { kind := .dividend, rateBp := 1500, statute := "GRA 'Dividend Income Tax' brochure: 15 % of the gross dividend" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 100000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Corporation income tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Income and Value Added Tax Act 2012 (as amended; rate as stated by the GRA brochure 'Corporation Income Tax'): the higher of 27 % of net profit and 1 % of turnover (audited accounts; 2 % unaudited) [text version: GRA brochures as published on gra.gm on 21 August 2023 (the corporation-tax brochure dates its rate to 2018); Finance Acts 2024 and 2025 not held (flag)]" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["official secondary source: the brochure states the rate 'as of 2018' and is still the authority's published guide; Finance Acts 2019-2025 were not read (flagged)", "companies are taken to have audited accounts (1 % turnover minimum); the 2 % unaudited minimum and the six-year loss limit are not modelled", "interest and royalties paid abroad are not covered by the brochures held (not modelled)", "official secondary source; the Act's withholding schedule was not read"]

end GmGlobal
