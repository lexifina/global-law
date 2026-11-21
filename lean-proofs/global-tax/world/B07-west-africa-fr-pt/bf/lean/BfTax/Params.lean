import TaxKernel.World

/-!
# Burkina Faso 2025: parameters, each with its dated source (whole francs CFA)

Sources (copies in `../src/`):
* Code général des impôts, "Edition officielle 2023 (à jour des dispositions de la loi de finances 2023)", DGI
  (archived official copy of `dgi.bf/wp-content/uploads/2023/08/Code-general-des-impots-a-jour-avec-la-LF-2023.pdf`,
  Wayback 20240714173657; dgi.bf does not answer from our hosts). Arts. 105-119 (IUTS), 120-128 (IRF), 129-149 (IRCM).
* Loi de finances 2024 and loi de finances rectificative 2024 (archived official copies of dgi.bf, scanned; OCR in
  `LF-2024.ocr.txt`, `LFR-2024.ocr.txt`) and the DGI booklet "nouvelles mesures fiscales de la loi de finances exercice
  2024": none amends arts. 105-149.
* Décret n° 2003-252/PRES/PM/MTEJ (LegiBurkina, scanned; OCR checked by eye), art. 2: employee 5,5 % (assurance vieillesse).
* The loi de finances 2025 was NOT reached (LegiBurkina's index has no 2025 finance law; dgi.bf unreachable): every amount
  here is the 2023 code's, carried to 2025 (access B).
-/

namespace BfTax
open TaxKernel

/-- Art. 112: "Les taux applicables au revenu mensuel imposable": 0 à 30.000: 0 %; 30.100 à 50.000: 12,10 %; 50.100 à
80.000: 13,90 %; 80.100 à 120.000: 15,70 %; 120.100 à 170.000: 18,40 %; 170.100 à 250.000: 21,70 %; 250.100 et
au-dessus: 25 %. Rates in hundredths of a basis point would be exact; 12,10 % = 1210 bp. Reading: the gaps of 100 F
("30.000" / "30.100") are read as continuous bands with limits at 30 000, 50 000, ... (no rounding rule is printed). -/
def monthly : Schedule :=
  Schedule.ofList [(0, 0), (30000, 1210), (50000, 1390), (80000, 1570), (120000, 1840), (170000, 2170), (250000, 2500)]

/-- Art. 111: deductions from gross pay: pension contributions "dans la limite de 8 % du salaire de base"; "un
abattement forfaitaire de 25 % du salaire de base pour frais et charges professionnels. Cet abattement est réduit à
20 % pour les catégories supérieures ... « P », « A », et « B »". -/
def pensionDedCap : Int := 800
def abatOrdinary : Int := 2500
def abatSuperior : Int := 2000

/-- Art. 113 1) (Loi n° 042-2018/AN art. 25): "réduction d'impôt pour charges de famille": 1 charge 8 %, 2 charges 10 %,
3 charges 12 %, 4 charges 14 %. Charges (2)): children "mineurs ou infirmes ou âgés de moins de vingt-cinq (25) ans
lorsqu'ils poursuivent leurs études", orphans in the household, "c) un conjoint", all "à condition de ne pas avoir de
revenus distincts de ceux du salarié". -/
def chargeRate (n : Int) : Int :=
  if n ≤ 0 then 0 else if n == 1 then 800 else if n == 2 then 1000 else if n == 3 then 1200 else 1400

/-- Reading: "mineurs" = under 18. -/
def childAgeLimit : Nat := 18

/-- Décret 2003-252 art. 2: "La participation du travailleur est fixée à 5,5% au titre de la branche Assurance
vieillesse." The ceiling of art. 3 (by reference to art. 22 of the 1972 code) was not read: none applied. -/
def cnssEmployee : Int := 550

/-- Art. 125 1): net rental income = gross rent less "un abattement forfaitaire de 50 %"; art. 126: "tranche de 0 à
100.000 francs CFA : 18 % ; au-dessus de 100.000 francs CFA : 25 %" (per month or period of the lease: reading,
monthly). -/
def rentAbat : Int := 5000
def irfMonthly : Schedule := Schedule.ofList [(0, 1800), (100000, 2500)]

/-- Art. 140: IRCM 25 % on income from claims, "réduit de moitié pour les intérêts ... des comptes de dépôt ... d'une
banque" (12,5 %); "12,5 % pour tous autres produits" of securities (dividends). -/
def bankInterestRate : Int := 1250
def dividendRate : Int := 1250

end BfTax
