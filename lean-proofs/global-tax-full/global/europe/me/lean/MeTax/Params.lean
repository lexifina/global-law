import TaxKernel.World

/-!
# Montenegro 2025: parameters, each with its dated source (euro cents inside, whole euros out)

Sources. Global law corpus `montenegro/national/acts` (Službeni list Crne Gore) holds the Zakon o porezu na dohodak
fizičkih lica (SL RCG 65/2001) as enacted and each amending law as its own act; the 2025 text is the base law plus
67/2019, 59/2021, 146/2021, 152/2022 (`zakon/2022/334487`), **88/2024** and 133/2025 (in force 2025-11-19, interest on
government bonds only). 88/2024 is **not in Global law**: read from the official gazette sluzbenilist.me/propisi/373333
(page images OCR'd with tesseract, numbers checked against the images; `../src/sl88/`); it takes effect 1 January 2025
(član 26) and does not change the employment rates of član 10 stav 1 tačka 1. 160/2025 applies only from 2026-01-01.
Contributions: Zakon o doprinosima za obavezno socijalno osiguranje (SL CG 13/07), član 15 as amended by 94/2024
(`zakon/2024/373700`, applied from 1 October 2024); član 17 (health) deleted by 145/2021 from 2022-01-01; član 18.
Surtax: municipal decision; default **Opština Žabljak**, Odluka o prirezu porezu na dohodak fizičkih lica
(sluzbenilist.me/propisi/310754, in the record on 2025-06-01).
-/

namespace MeTax
open TaxKernel

/-- Član 10 stav 1 tačka 1 (152/2022): "0% na iznos oporezivog dohotka do 700,00€, 9% ... od 700,01€ do 1.000,00€,
15% ... od 1.000,01€" (monthly personal income), in cents. -/
def monthlySchedule : Schedule := Schedule.ofList [(0, 0), (70000, 900), (100000, 1500)]
/-- The Ministry's instruction (Uputstvo, SL CG 3/22, član 1) prints "27,00€+15%" above 1 000 €: the column form. -/
def printedMonthly : List CumRow := [⟨0, 0, 0⟩, ⟨70000, 0, 900⟩, ⟨100000, 2700, 1500⟩]

/-- Član 10 stav 1 tačka 2 (146/2021): self-employment, annual: 9 % from 8 400,01 to 12 000, 15 % above (no tax up
to 8 400: the 9 % band starts at 8 400,01; 88/2024 član 4 only narrows tačka 2 to "alineja 1"), in cents. -/
def annualSelfSchedule : Schedule := Schedule.ofList [(0, 0), (840000, 900), (1200000, 1500)]

/-- Član 10 stav 1 tačka 3: 15 % on the other incomes of član 12 stav 2 tač. 3 do 8 (property, capital, capital gains,
...). -/
def otherRate : Int := 1500

/-- Član 15 (base law): "Oporezivi prihod od ličnih primanja predstavljaju bruto primanja". -/
def wageBaseIsGross : Bool := true

/-- Zakon o doprinosima član 15 stav 1 tačka 1 (94/2024): pension "na teret osiguranika 10,0%". -/
def pensionEmployee : Int := 1000
/-- Član 18 tačka 1: unemployment "na teret osiguranika 0,5%". -/
def unemploymentEmployee : Int := 50

/-- Odluka o prirezu (Žabljak, 2018) član 3: "Stopa prireza ... iznosi 13% od poreske osnovice" (the base is the tax,
član 2). -/
def surtaxRate : Int := 1300

end MeTax
