import TaxKernel.World

/-!
# San Marino 2025: parameters (euro cents inside, whole euros out)

Source: Global law `san-marino/national/acts/imposta-generale-sui-redditi/legge-2013-166` (Legge 166/2013, IGR), the
publisher's current text of 2025-12-22 (current-only record; copy in `../src/`). The 2025 wording is rebuilt as follows:
* art. 148 c. 8: "Fino al 31 dicembre 2025 gli articoli 13, 16, 17, 25, 102, 103 e 104 si applicano nel tenore
  seguente" (files `art-16--2.md`, `art-17--2.md`, `art-25--2.md`, ...): the 2025 detrazioni (art. 16) and tariff rule
  (art. 17).
* Allegato C art. C1 c. 1 (tariff) is the 2013 text (footnote 93: Legge 141/2025 art. 51 changed only c. 2); C1 c. 3 (the
  9 000 € deduction) was abrogated by Legge 141/2025 art. 55 and is read from footnote 93 ("Testo originario"), in force
  in 2025 as the 2026 reform's companion of art. 148 c. 8 (reading R1 in FINDINGS).
* art. 24 c. 4 (2013 text; Legge 141/2025 art. 10 changed only cc. 3, 5, 6), art. 26 (pension abatements).
* art. 14 in its pre-141/2025 wording (footnote: c. 1 a) electronic-payment spending in San Marino, c. 2 cap "differenza
  tra €9.000,00 e l'importo della deduzione di cui all'Allegato C, articolo C1, comma 3"): household input
  `sm_smacSpending` (default 0: an assumption).
-/

namespace SmTax
open TaxKernel

/-- Allegato C art. C1 c. 1: "sino a €10.000,00 9% da €10.000,01 a €18.000,00 13% ... a €28.000,00 17% ... a
€38.000,00 21% ... a €50.000,00 25% ... a €65.000,00 28% ... a €80.000,00 31% Oltre €80.000,00 35%" (cents). -/
def tariff : Schedule := Schedule.ofList
  [(0, 900), (1000000, 1300), (1800000, 1700), (2800000, 2100), (3800000, 2500), (5000000, 2800), (6500000, 3100), (8000000, 3500)]

/-- Art. 24 c. 4: employment income "al netto dei contributi previdenziali ed assistenziali obbligatori a carico del
lavoratore dipendente e di un abbattimento forfettario pari al 7% e sino ad un massimo di €2.800,00". -/
def empAbatementRate : Int := 700
def empAbatementCapC : Int := 280000

/-- Art. 26 c. 1: pensions net of "20% per i redditi fino a 13.000,00 euro; 12% ... fino ai 19.500,00 euro; 9% ... fino
ai 26.000,00 euro; 7% oltre i 26.000,00 euro" (a band schedule of the abatement, cents). -/
def pensionAbatement : Schedule := Schedule.ofList [(0, 2000), (1300000, 1200), (1950000, 900), (2600000, 700)]

/-- Allegato C art. C1 c. 3 (2013 text, footnote 93): "si deduce un importo massimo di €9.000,00 ... per la parte
corrispondente al rapporto tra l'ammontare di €40.000,00, diminuito del reddito ..., e l'importo di €31.000,00 ... si
computano le prime quattro cifre decimali". -/
def c3MaxC : Int := 900000
def c3TopC : Int := 4000000
def c3SpanC : Int := 3100000

/-- Art. 14 c. 2 (pre-141/2025): spending deduction up to 9 000 € less the C1 c. 3 deduction. -/
def spendingCapC : Int := 900000

/-- Art. 16 (2025 wording) c. 1: "a) euro 250,00 ... per il coniuge a carico"; "b) euro 250,00 ... per ogni figlio a
carico"; c. 7: "+20 per cento qualora il numero dei familiari a carico superi le due unità"; c. 9: "Per i redditi di
cui agli articoli 24, 25 e 26 di imponibile fino ad euro 15.000,00 ... si detraggono dall'imposta euro 100,00". -/
def spouseCreditC : Int := 25000
def childCreditC : Int := 25000
def familyUplift : Int := 2000
def lowIncomeLimitC : Int := 1500000
def lowIncomeCreditC : Int := 10000

end SmTax
