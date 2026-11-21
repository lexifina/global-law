import TaxKernel.World

/-!
# Liechtenstein 2025: parameters, each with its dated source (whole CHF; Rappen inside)

Sources: Lilex, the government's legal database (gesetze.li; the link Global law gives for each act); each act read in
the consolidated version whose header says it is the one for 2025 (copies in `../src/`):
* Steuergesetz (SteG, LGBl. 2010 Nr. 340, LR 640.0): `konso/pdf/2010340000?version=33`, "Fassung: 01.01.2025", the
  later of the two 2025 versions (it includes LGBl. 2025 Nr. 541, applied from the 2025 assessment, Art. 23); the
  version list on `konso/2010340000/meta` shows 01.01.2025 - 31.12.2025.
* AHVG (LGBl. 1952 Nr. 29, LR 831.10): version 58, "Fassung: 01.01.2025".
* IVG (LGBl. 1960 Nr. 5, LR 831.20): version 42, "Fassung: 01.01.2024" (the next version is not before 2026).
* ALVG (LGBl. 2010 Nr. 452, LR 837.0): version 19, "Fassung: 01.01.2023" (the next, version 20, is 01.01.2026).
-/

namespace LiTax
open TaxKernel

/-- A tariff row "rate · x − subtract" from `lo` (CHF; rate in bp). -/
structure Row where
  lo : Int
  rate : Int
  sub : Int

/-- SteG Art. 19 Abs. 1 Bst. a (all taxpayers): "bis 15 855 Franken (Grundfreibetrag): 0; von 15 856 Franken bis 21 140
Franken: 0,01 · x - 159; ... 0,03 · x - 581; 0,04 · x - 1 004; 0,05 · x - 1 744; 0,06 · x - 2 801; 0,065 · x - 3 488;
0,07 · x - 4 334; von 211 401 Franken oder mehr: 0,08 · x - 6 448". -/
def tariffA : List Row := [⟨0, 0, 0⟩, ⟨15856, 100, 159⟩, ⟨21141, 300, 581⟩, ⟨42281, 400, 1004⟩, ⟨73991, 500, 1744⟩,
  ⟨105701, 600, 2801⟩, ⟨137411, 650, 3488⟩, ⟨169121, 700, 4334⟩, ⟨211401, 800, 6448⟩]
/-- Art. 19 Abs. 1 Bst. b (single parents in the sense of the Familienzulagengesetz). -/
def tariffB : List Row := [⟨0, 0, 0⟩, ⟨23784, 100, 238⟩, ⟨31711, 300, 872⟩, ⟨63421, 400, 1506⟩, ⟨110986, 500, 2616⟩,
  ⟨158551, 600, 4202⟩, ⟨206116, 650, 5232⟩, ⟨253681, 700, 6501⟩, ⟨317101, 800, 9672⟩]
/-- Art. 19 Abs. 1 Bst. c (spouses assessed jointly). -/
def tariffC : List Row := [⟨0, 0, 0⟩, ⟨31711, 100, 317⟩, ⟨42281, 300, 1163⟩, ⟨84561, 400, 2008⟩, ⟨147981, 500, 3488⟩,
  ⟨211401, 600, 5602⟩, ⟨274821, 650, 6976⟩, ⟨338241, 700, 8667⟩, ⟨422801, 800, 12895⟩]

/-- Art. 16 Abs. 2 Bst. c: from employment income "1 600 Franken" (Gewinnungskosten). -/
def employmentExpenses : Int := 1600
/-- Art. 16 Abs. 3 Bst. a: per child "ein Betrag von 12 700 Franken". -/
def childDeduction : Int := 12700
/-- Art. 16 Abs. 2 Bst. d: AHV/IV pensions: deduct "70 % der Einkünfte". -/
def pensionDeductionRate : Int := 7000
/-- Art. 75 Abs. 3: the Gemeindezuschlag is set yearly by the municipal council, "darf aber 150 % nicht unterschreiten
und 250 % nicht übersteigen". Default municipality Vaduz; its 2025 rate was not reached: the statutory minimum is used
and flagged (unsupported). -/
def gemeindeZuschlagMin : Int := 15000

/-- AHVG Art. 38 Abs. 1 (2025): "wird ein Beitrag von 4.025 % erhoben" (employee). -/
def ahv : Int := 4025 -- in 1/100 000 (4.025 %)
/-- IVG Art. (Beiträge) Abs. 3: "für Arbeitnehmer und Arbeitgeber je 0.675 %". -/
def iv : Int := 675 -- 0.675 %
/-- ALVG Art. 4 Abs. 2-3: 1 % up to the maximum insured earnings, "je zur Hälfte"; Art. 30 Abs. 2: "Der Höchstbetrag des
versicherten Verdienstes beträgt 126 000" Franken. -/
def alv : Int := 500 -- 0.5 %
def alvCeiling : Int := 126000
/-- Rates above are in hundred-thousandths. -/
def TBP : Int := 100000

end LiTax
