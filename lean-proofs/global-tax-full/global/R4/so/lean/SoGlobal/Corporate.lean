import R4Common

/-!
# Somalia 2025: corporate income tax (1200) and withholding (generated from `R4/specs/so.json`)

No usable 2025 text for these headings: Law 37 and the 2020 Inland Revenue law OCR held; not mapped in this pass. Pass 10 (CIT/WHT): Law No. 37 of 11 May 2025 (Income Tax Law, Somali text, OCR `world/B10-anglophone-africa/so/law/law37_ocr.txt` of sharciga_cashuurta_dakhliga_37.pdf): First Schedule art. 3 and 5, art. 91-92, 105-106. The 2020 'Xeerarka Maaliyadda' held is the public financial management regulation (no tax rates).

Law 37/2025 First Schedule, Qodobka 3-aad "Boqolleeyda Canshuurta Dakhliga ee Lagu Dabaqaayo Shirkadaha (Rate of Income Tax for Corporations): Dakhliga canshuur-galka ah ee Shirkaddaha ee sanad canshuureedka waxa lagu canshuuraayaa boqolkiiba shan iyo toban (15%) oo ah boqolleey siman." (the taxable income of corporations for the tax year is taxed at fifteen percent, a flat rate). Art. 106: the Law enters into force when approved by Parliament and signed by the President (signed 11 May 2025); art. 105 (3) (b): the former law continues to apply to tax obligations for tax years ending before that date.

First Schedule Qodobka 5-aad (Rates of Withholding Tax) (1) "t) lacag-bixinnada lagu dabaqaayo Qodobka 91-aad (investment returns): i. haddii ay tahay faa'idada saamiga (dividend), waxaa lagu canshuurayaa boqolkiiba shan (5%); ii. haddii ay tahay faa'idada ka dhalata qaamaha (returns on debt claims), waxaa lagu canshuurayaa boqolkiiba toban (10%); ... v. hadii ay tahay khidmadda kheyraadka dabiiciga ah ama khidmadda xuquuqda milkiyadda (royalty), waxaa lagu canshuurayaa boqolkiiba shan iyo toban (15%); j) lacag-bixinnada lagu dabaqaayo Qodobka 92-aad (service fees): ... ii. haddii ay tahay khidmadaha adeegga ee lagu sheegay Qodobka 92(1) (t), waxaa lagu canshuurayaa boqolkiiba toban (10%)". Art. 91 (1): a resident (including a Somali permanent establishment) paying a dividend, natural-resource fee, rent, return on a debt claim or royalty sourced in Somalia withholds at the art. 5 rate; art. 92 (1) (t): a service fee or insurance premium sourced in Somalia paid to a non-resident.
-/

namespace SoGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Income tax on corporations", sched := Schedule.flat 1500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 1500149
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 150000
def whtR : Wht :=
  { name := "Withholding tax on Somali-source payments (Law 37/2025 art. 91-92)",
    rules := [{ kind := .dividend, rateBp := 500, statute := "First Schedule art. 5 (1) (t) (i): dividends 5 %" },
              { kind := .interest, rateBp := 1000, statute := "First Schedule art. 5 (1) (t) (ii): returns on debt claims 10 %" },
              { kind := .royalty, rateBp := 1500, statute := "First Schedule art. 5 (1) (t) (v): royalties and natural-resource fees 15 %" },
              { kind := .services, rateBp := 1000, statute := "First Schedule art. 5 (1) (j) (ii): service fees under art. 92 (1) (t) (paid to a non-resident) 10 %" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 50000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 100000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 100000
def corporate : Family :=
  { name := "1200 Income tax on corporations", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Law No. 37 of 2025 (Income Tax Law) First Schedule art. 3 (rate of income tax for corporations: 15 % flat); art. 4 (1): Somali permanent establishments at the same rate" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["Law 37 took effect on 11 May 2025; the former law governs only tax years ending before then, so the 15 % rate applies to the whole 2025 tax year", "the OCR prints 'boqolkiiba' as 'bogolkiiba' and 'oo' as '00'", "whether the withholding is the non-resident's final tax was not established from the OCR (art. 94 not read); it is applied as the statutory withholding on the payment", "insurance premiums paid to non-residents (5 %) and rents (5 % / 10 %) are not modelled lines"]

end SoGlobal
