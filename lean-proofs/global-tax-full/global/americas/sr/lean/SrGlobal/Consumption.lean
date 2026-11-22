import SrGlobal.Pit

/-!
# Suriname 2025: Belasting over de Toegevoegde Waarde (5111); excises grade C

Sources (Belastingdienst Suriname, wetgeving page, fetched 2026-11-21; `sr/law/`, ARCHIVE_INDEX.tsv): Wet Belasting over
de Toegevoegde Waarde 2022 (S.B. 2022 no. 121, Wet van 12 oktober 2022, in force 1 January 2023); nadere wijziging
S.B. 2022 no. 148 (Wet van 30 december 2022); nadere wijziging S.B. 2023 no. 126 (Wet van 5 september 2023, scanned:
OCR `btw_sb2023_126_wijz.ocr.txt`). Grade B (the 2023 amendment read from OCR; no later rate law on the Belastingdienst
list).
* **Art. 4 (1)**: "Het tarief van de belasting bedraagt 10 (tien) procent." Art. 4 (3) as inserted by S.B. 2022/148 I C:
  5 % on the goods and services in bijlage 4; art. 4 (4): 25 % on the goods in bijlage 3 (large cars, motorcycles over
  125 cm3, pleasure craft, small aircraft, arms, fireworks).
* **Bijlage 4** as replaced by S.B. 2023/126 I D (in force 1 November 2023, new art. 68 (8)): (a) water by the state
  undertaking for household use, and water in packs of 5 gallons or more; (b) "de levering van electriciteit en
  prestaties ter zake en kookgas"; (c) domestic goods transport. Motor fuel, at 5 % in the 2022/148 bijlage 4, is no
  longer listed: the general 10 % applies (explanatory note: items dropped from the annexes fall under the general rate).
* **Bijlage 2 (exempt)** as replaced by S.B. 2023/126 I B (in force 1 October 2023): medical professions; "het
  binnenlands vervoer van personen over de weg en te water"; hospitals; medical aids and medicines; "verzekering van
  lokale ziektekosten en levensverzekering"; recognised education and school materials; financial services; listed
  goods: fresh vegetables, fresh chicken, fresh fish, eggs, flour, bread and cassava bread, rice, padi, milk, soya oil,
  matches, contraceptives, disposable nappies, bath soap, toilet paper.
* The zero rate on the rent of dwellings (old bijlage 1 (c)) lapsed on 1 November 2023 (S.B. 2023/126 I G): rent is
  taxable at 10 % where the landlord is an ondernemer above the art. 21 threshold.
* **Art. 21 (1)**: an ondernemer with taxable turnover of "SRD 1.000.000,- ... of minder" a calendar year is relieved of
  the obligations (threshold).
* Food: only the bijlage 2 staples are exempt; other food is taxable at 10 % (food read as exempt: lower bound,
  flagged). Insurance read as the exempt local health and life cover; other insurance is taxable (flagged).
-/

namespace SrGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon SrGlobal

def vat : Vat :=
  { name := "Belasting over de Toegevoegde Waarde (BTW)", standard := 1000, reduced := 500, reduced2 := 2500, threshold := 1000000,
    classOf := fun gd => match gd with
      | .food | .medicines | .health | .education | .transport | .insurance | .financial => .exempt
      | .water | .electricity | .gas => .reduced
      | _ => .standard }

def vatStatute : String := "Wet BTW 2022 (S.B. 2022 no. 121) art. 4 (1) 10 %, art. 4 (3) 5 % bijlage 4, art. 4 (4) 25 % bijlage 3 (S.B. 2022 no. 148); bijlagen 2 and 4 as replaced by S.B. 2023 no. 126; art. 21 (1) SRD 1,000,000"

def vatF : Family := vatFamily "Belasting over de Toegevoegde Waarde (BTW)" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 13): Grondwet art. 155 lid 1: \"Belastingen worden geheven krachtens de wet\" (`sr/law/const_art-155.md`). No law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (the omzetbelasting was replaced by the BTW from 2023) (laws read include: Wet BTW 2022 (S.B. 2022 no. 121) art. 4, 21; Wet Inkomstenbelasting art. 47 lid 1: 36 percent; Wet Inkomstenbelasting 1922 art. 1 lid 3, art. 27 lid 2 (S.B. 2024 no. 3): not a binnenlandse bron of a non-resident: no tax, none withheld; Wet Dividendbelasting 1973 arts. 1-6 (S.B. 1981 no. 184, S.B. 1984 no. 109); 1.x model (see its summary.json); Wet Algemeen Pensioen 2014 (S.B. 2014 no. 113, 9 Sep 2014) art. 8: lid 1 3 % of the bijdragegrondslag)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food: only the bijlage 2 staples (fresh vegetables, chicken, fish, eggs, flour, bread, rice, milk, soya oil) are exempt; other food is taxable at 10 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .rent) "rent of dwellings: taxable at 10 % since 1 November 2023 (S.B. 2023/126), but a landlord with turnover of SRD 1,000,000 or less is not liable (art. 21): charged at 10 % (upper bound)"
  ++ when (g.consumption.any fun s => s.good == .insurance) "insurance read as exempt local health and life cover (bijlage 2); other insurance is taxable at 10 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) "accijnzen on alcohol, tobacco and fuel not modelled (Wet Accijnzen not reached)"

#guard vat.embedded { good := .clothing, amount := 1100 } == 100
#guard vat.embedded { good := .electricity, amount := 1050 } == 50
#guard vat.embedded { good := .petrol, amount := 1100 } == 100
#guard vat.embedded { good := .food, amount := 1100 } == 0
#guard vat.threshold == 1000000

end SrGlobal.Consumption
