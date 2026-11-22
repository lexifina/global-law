import R4Common

/-!
# Malawi 2025: corporate income tax (1200) and withholding (generated from `R4/specs/mw.json`)

Pass 10: Malawi Revenue Authority downloads via Wayback (`www.mra.mw/assets/upload/downloads/…`, `www.mra.mw/admin/storage/download_files/…`; CDX `url=mra.mw&matchType=domain&filter=mimetype:application/pdf`) and the MalawiLII media copy of the Value Added Tax (Amendment) (No. 2) Act 2025 (`media.malawilii.org/media/legislation/15246/…`, the Government Printer's gazette bundle with Acts 36 and 37 of 2025), in `R4/fetch/mw10/` (scanned Acts OCRed, tesseract eng). Not held: the principal Acts (Cap. 41:01, Cap. 42:02), the 2023 Taxation amendment, the non-resident tax schedule.

Act No. 14 of 2020 s. 4 (new Eleventh Schedule): "Income tax shall be charged as follows— ... (c) in the case of all companies other than companies engaged in mining operations ..., thirty per cent of taxable income except that in the case of companies operating in priority industries ... the applicable rate shall be either— (i) zero per cent ...; or (ii) fifteen per cent: Provided that an additional tax of five per cent of taxable income shall be charged in respect of all companies not incorporated in Malawi". Act No. 12 of 2024 (published 19 April 2024) s. 7: "The Eleventh Schedule to the principal Act is amended— (a) under paragraph (c), by deleting subparagraph (ii) and substituting therefor, a new subparagraph (ii) as follows— '(ii) an additional tax of ten percent shall be charged on any taxable income above ten billion kwacha;'". MRA notice 'New income tax rates effective 19th April 2024': "b. Companies incorporated in Malawi 30%; c. Companies incorporated outside Malawi 35%". Act No. 36 of 2025 (from 30 December 2025) lowers the threshold to K5 billion and adds a 0.5 % minimum alternative tax (not applied to 2025).


-/

namespace MwGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Income tax on companies", sched := (Schedule.ofUpper [(10000000000, 3000)] 4000), lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3000299
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 300000
#guard R4.corpTax citR minT { profit := 9999999999, turnover := 100000000000, lossesForward := 0 } 1 == 2999999999
#guard R4.corpTax citR minT { profit := 10000000777, turnover := 100000000000, lossesForward := 0 } 1 == 3000000310
def corporate : Family :=
  { name := "1200 Income tax on companies", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Taxation Act Cap. 41:01 Eleventh Schedule para (c) as replaced by the Taxation (Amendment) Act 2020 (Act No. 14 of 2020: all companies 30 % of taxable income) and amended by the Taxation (Amendment) Act 2024 (Act No. 12 of 2024 s. 7 (a): additional tax of 10 % on taxable income above K10 billion)" (step := 1)] }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["the 2023 Taxation amendment that restructured paragraph (c) was not read; the 30 % rate rests on the 2020 Schedule and the MRA's April 2024 notice", "priority-industry rates, the 5 % surcharge on companies not incorporated in Malawi and mining resource rent tax are not modelled; the K5 billion threshold and the minimum alternative tax of Act No. 36 of 2025 apply from 30 December 2025 (not split)", "withholding on payments abroad not modelled: the non-resident tax of Taxation Act s. 76A exists (Act 6/2022 Fourteenth Schedule note 7 (b): 'interest payable to a person, not being a person resident in Malawi, whose income is liable to non-resident tax under section 76A'; Act 12/2024 s. 4 amends s. 76A (1)) but its rate is not in the amending Acts held; no cited 0 (the tax exists)"]

end MwGlobal
