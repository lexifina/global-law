import TaxKernel

/-!
# Cyprus 2025: parameters, each with its source (money in euro CENTS, rates in basis points)

Statute texts used (saved under `~/cmp20/southeast/cy/law/`):
* ITL = Ο περί Φορολογίας του Εισοδήματος Νόμος 118(I)/2002, CyLaw consolidation as of 9 Nov 2025 (laws up to
  47(I)/2025; Wayback copy of http://www.cylaw.org/nomoi/enop/non-ind/2002_1_118/full.html, file
  `itl_118_2002_as_of_2025-11-09.txt`) and the current consolidation (`itl_118_2002.txt`, which holds the 2026 reform
  244(I)/2025, in force 1.1.2026, art. 25 of that law).
* SDC = Ο περί Έκτακτης Εισφοράς για την Άμυνα της Δημοκρατίας Νόμος 117(I)/2002, as of 7 Nov 2025
  (`sdc_117_2002_as_of_2025-11-07.txt`) and current (`2002_1_117.txt`, reform 245(I)/2025 from 1.1.2026).
* GESY = Ο περί Γενικού Συστήματος Υγείας Νόμος 89(I)/2001 (`2001_1_89.txt`).
* SIL = Ο περί Κοινωνικών Ασφαλίσεων Νόμος 59(I)/2010 (`si_59_2010_as_of_2025-09-12.txt`).
* CBL = Ο περί Παροχής Επιδόματος Τέκνου Νόμος 167(I)/2002 (`child_benefit_167_2002.txt`).
* EUROMOD Country Report Cyprus 2022-2025 (JRC 2026, `euromod_Y16_CR_CY.txt`) where the applied 2025 figure is not
  printed in the statute (SI rates set under the actuarial-study proviso, indexed child benefit, SI ceiling).
-/

namespace CYTax
open TaxKernel

/-- ITL Second Schedule para 1(β) ("Από το φορολογικό έτος 2008 και μετέπειτα"): "Για κάθε ευρώ μέχρι €19.500 0%
… πάνω από €19.500 μέχρι €28.000 20% … €28.000 μέχρι €36.300 25% … €36.300 μέχρι €60.000 30% … πάνω από €60.000
35%". Thresholds in cents. -/
def scale2025 : Schedule :=
  Schedule.ofList [(0, 0), (1950000, 2000), (2800000, 2500), (3630000, 3000), (6000000, 3500)]

/-- ITL Second Schedule para 1(γ), added by 244(I)/2025 art. 24, "Από το φορολογικό έτος 2026 και μετέπειτα":
€22.000 / €32.000 / €42.000 / €72.000. Used only for the 2025→2026 timing findings. -/
def scale2026 : Schedule :=
  Schedule.ofList [(0, 0), (2200000, 2000), (3200000, 2500), (4200000, 3000), (7200000, 3500)]

/-- SIL art. 5(1)(στ) prints 8,9 % for the employee from 1.1.2024; the proviso to art. 5(1) lets the rates indicated
by the actuarial study apply instead ("θα επιβάλλονται τα υποδεικνυόμενα από την υπό αναφορά αναλογιστική μελέτη
ποσοστά"). Applied 2025 rate 8,8 % (EUROMOD CR Cyprus §2.7.1.3 Table 2.13; Eurostat earn_nt_net 2025 SOC =
11,45 % of gross = 8,8 + 2,65). FINDINGS F1. -/
def siEmployeeRate : Int := 880
/-- The rate printed in SIL art. 5(1)(στ) (kept for the finding). -/
def siEmployeeRateStatute : Int := 890
/-- Self-employed: SIL art. 12(ζ) prints 16,8 % from 2024; applied 16,6 % (EUROMOD CR §1.4). -/
def siSelfRate : Int := 1660
/-- Maximum insurable earnings 2025: €5.551 a month, €66.612 a year (EUROMOD CR §2.7.1.2; OEB circular
Αρ.α.257/2024 of 2 Dec 2024 quoting the Social Insurance Services). Annual cap for earnings paid evenly by month. -/
def siCeiling : Int := 6661200

/-- GESY art. 19(1)(α) "Κάθε μισθωτός σε ποσοστό 2,65% επί των αποδοχών του". -/
def gesyEmployee : Int := 265
/-- GESY art. 19(1)(γ) "κάθε αυτοτελώς εργαζόμενος σε ποσοστό 4,00%". -/
def gesySelf : Int := 400
/-- GESY art. 19(1)(δ) "κάθε συνταξιούχος σε ποσοστό 2,65%". -/
def gesyPension : Int := 265
/-- GESY art. 19(1)(ζ) "κάθε εισοδηματίας σε ποσοστό 2,65% επί του εισοδήματός του" (εισόδημα includes rent,
interest and dividends, art. 2). -/
def gesyIncome : Int := 265
/-- GESY art. 19(4)(α) "εισφορά καταβάλλεται μόνο επί του ποσού των εκατόν ογδόντα χιλιάδων ευρώ (€180.000)";
(β) order: emoluments, then pensions, then income. -/
def gesyCap : Int := 18000000

/-- SDC art. 3(2)(α) (2025 text): "σε ποσοστό δεκαεφτά τοις εκατόν (17%) στο ποσό του μερίσματος". -/
def sdcDividend : Int := 1700
/-- SDC art. 3(2)(β): interest "σε ποσοστό δεκαεπτά τοις εκατόν (17%)". -/
def sdcInterest : Int := 1700
/-- SDC art. 3(2)(β)(iii): total annual income incl. interest not over €12.000 → refund above 3 %. -/
def sdcInterestLow : Int := 300
def sdcInterestLowLimit : Int := 1200000
/-- SDC art. 3(2)(δ): rent "σε ποσοστό τρία τοις εκατόν (3%) επί του ποσού των ακαθαρίστων ενοικίων μειωμένων
κατά ποσοστό εικοσιπέντε τοις εκατόν (25%)". -/
def sdcRent : Int := 300
def sdcRentBase : Int := 7500

/-- ITL art. 9(2): "αφαιρείται ποσοστό είκοσι τοις εκατόν (20%) από το εν λόγω ακαθάριστο εισόδημα" (rent). -/
def rentDeduction : Int := 2000
/-- ITL art. 14 proviso (ii) (2025 text): the deduction "δεν θα μπορεί να υπερβεί το ένα πέμπτο του φορολογητέου
εισοδήματος … προτού αφαιρεθούν από αυτό οι εκπτώσεις που καθορίζονται στο παρόν άρθρο". -/
def art14CapNum : Int := 1
def art14CapDen : Int := 5

/-- ITL art. 8(21Α): "τo είκοσι τοις εκατόν (20%) της αμοιβής από πρώτη εργοδότηση … ή … (€8.550), οποιοδήποτε
είναι το μικρότερο". -/
def ex21ARate : Int := 2000
def ex21ACap : Int := 855000
/-- ITL art. 8(23Α): "τo πενήντα τοις εκατόν (50%) της αμοιβής …"; proviso (ii) "για οποιοδήποτε έτος στο οποίο η
αμοιβή … υπερβαίνει τις πενήντα πέντε χιλιάδες ευρώ (€55.000)". -/
def ex23ARate : Int := 5000
def ex23AThreshold : Int := 5500000

/-- CBL Schedule para 4, Table A (annual child benefit per dependent child, euros) as printed: rows 1, 2, 3, 4+
children; columns ≤ €19.500, ≤ €39.000, ≤ €49.000, ≤ €59.000 (col. 4 extended to €64.000 / €69.000 / no limit for
3 / 4 / 5+ children). -/
def cbTableStatute : List (List Int) :=
  [[588, 526, 470, 0], [705, 643, 470, 427], [1293, 1231, 940, 854], [2073, 1887, 1559, 1404]]

/-- CBL Schedule para 7: "Από την 1η Ιανουαρίου 2025, το ύψος του επιδόματος αναπροσαρμόζεται … κατά το ποσοστό
αύξησης του μέσου όρου της Αυτόματης Τιμαριθμικής Αναπροσαρμογής". The 2025 amounts actually paid (EUROMOD CR
§2.6.2.4 Table 2.6, 2025 block, and Eurostat earn_nt_net FAM) are the printed ones × 1,0187, in cents. -/
def cbTable2025 : List (List Int) :=
  [[59900, 53584, 47879, 0], [71818, 65502, 47879, 43498], [131718, 125402, 95758, 86997],
   [211177, 192229, 158815, 143025]]

/-- Column limits (cents): CBL Schedule para 2 and Table A headings; para 5: column (1) "ισούται με το αφορολόγητο
εισόδημα" and column (2) "το διπλάσιο" (19.500 / 39.000). -/
def cbCol1 : Int := 1950000
def cbCol2 : Int := 3900000
def cbCol3 : Int := 4900000
def cbCol4 : Int := 5900000
/-- Para 2(γ)/(δ) and the proviso to Table A: 3 children €64.000, 4 children €69.000, 5+ no limit. -/
def cbLimit (n : Nat) : Int :=
  if n ≤ 1 then 4900000 else if n = 2 then 5900000 else if n = 3 then 6400000 else if n = 4 then 6900000
  else 1000000000000

/-- CBL Schedule para 8-9 Table B (monthly single-parent benefit per child): €212 up to €39.000, €189 up to €49.000;
2025 paid amounts 215,96 / 192,53 (EUROMOD CR §2.6.3.4 Table 2.7 = printed × 1,0187). -/
def spMonthly2025Low : Int := 21596
def spMonthly2025High : Int := 19253
def spLimitLow : Int := 3900000
def spLimitHigh : Int := 4900000

/-- Dependent child: CBL art. 2 (up to 18; 20 in secondary education; 21 in the National Guard): the contract only
gives ages, so under 18. -/
def childAgeLimit : Nat := 18

/-! ## Tax years 2022-2024 (improvement round 2, 2026-11-19)

The ITL scale (Second Schedule 1(β), "Από το φορολογικό έτος 2008 και μετέπειτα"), the art. 14 one-fifth cap, the
GESY rates (art. 19, unchanged since 1.3.2020) and the CBL column limits (19.500 / 39.000 / 49.000 / 59.000) are the
same in 2022-2025. Year-specific: -/

/-- SIL art. 5(1)(ε) (`si_59_2010_as_of_2025-09-12.txt` l. 166): "21,5%, από το οποίο 8,3% καταβάλλεται από το
μισθωτό ... από το έτος εισφορών που αρχίζει κατά ή μετά την 1η Ιανουαρίου 2019" (until (στ) from 1.1.2024: 8,9 %
printed, 8,8 % applied, F1). Self-employed: art. 12 (στ) "20,5%, από το οποίο 15,6% καταβάλλεται από τον ίδιο ...
από την πρώτη Δευτέρα του έτους εισφορών 2019" (until (ζ): 16,8 % printed, 16,6 % applied from 2024). -/
def siEmployeeRateFor (year : Nat) (statute : Bool) : Int :=
  if year ≤ 2023 then 830 else if statute then siEmployeeRateStatute else siEmployeeRate
def siSelfRateFor (year : Nat) (statute : Bool) : Int :=
  if year ≤ 2023 then 1560 else if statute then 1680 else siSelfRate

/-- Maximum insurable earnings from the Gazette (improvement round 3, copies in
`~/cmp20/improve-central/refs/cy/kdp/`). Οι περί Κοινωνικών Ασφαλίσεων (Εισφορές) Κανονισμοί του 2010 (Κ.Δ.Π.
289/2010, Ε.Ε. Παρ. ΙΙΙ(Ι) Αρ. 4437, 9.7.2010) Καν. 8(1): "Το εβδομαδιαίο ανώτατο όριο ασφαλιστέων αποδοχών είναι
ίσο με το εξαπλάσιο του εβδομαδιαίου ποσού των βασικών ασφαλιστέων αποδοχών και το μηνιαίο αντίστοιχο όριο είναι
ίσο με τα δεκατρία τρίτα (13/3) του εβδομαδιαίου ανώτατου ορίου"; 8(2): rounded "στον πλησιέστερο αριθμό ακέραιων
ευρώ" (Καν. 8 untouched by the amending Κ.Δ.Π. 52/2012, 398/2013, 167/2017, 308/2020). The basic amount is set by
Council of Ministers decree under SIL art. 20, made each November/December: Κ.Δ.Π. 496/2021 (3.12.2021) €186,20 a
week; Κ.Δ.Π. 357/2023 (17.11.2023) €201,57; Κ.Δ.Π. 392/2024 (29.11.2024) €213,54. Each decree names the year it is
made in ("για το 2023") but is published at its end; the amount in force during contribution year `y` is the one
decreed in `y - 1` (the decree in force on 1 January), which is the reading that reproduces the Social Insurance
Services' published ceilings (2025: €5.551, OEB circular Αρ.α.257/2024; 2022 €4.840 and 2024 €5.239 as in
EUROMOD). The decree made in 2022 is not in CyLaw's 2022 or 2023 Κ.Δ.Π. index (searched for "Ασφαλισ",
"Αποδοχ"): 2023 keeps €5.005 a month (EUROMOD CR §2.7.1.2; it implies a 2022 basic amount of €192,42-192,58). -/
def basicWeeklyDecreed (madeIn : Nat) : Option Int :=
  if madeIn = 2021 then some 18620 else if madeIn = 2023 then some 20157 else if madeIn = 2024 then some 21354
  else none
/-- Καν. 8: monthly ceiling in cents from a weekly basic amount in cents. -/
def ceilingMonthlyOf (basicWeekly : Int) : Int :=
  let weekly := divR .halfUp (6 * basicWeekly) 100      -- whole euros (8(2))
  100 * divR .halfUp (13 * weekly) 3                     -- whole euros (8(2)), in cents
theorem ceilingMonthly_decrees :
    ceilingMonthlyOf 18620 = 484000 ∧ ceilingMonthlyOf 20157 = 523900 ∧ ceilingMonthlyOf 21354 = 555100 := by decide
def siCeilingFor (year : Nat) : Int :=
  match basicWeeklyDecreed (year - 1) with
  | some b => 12 * ceilingMonthlyOf b
  | none => if year = 2023 then 6006000 else siCeiling
theorem siCeilingFor_values :
    siCeilingFor 2022 = 5808000 ∧ siCeilingFor 2023 = 6006000 ∧ siCeilingFor 2024 = 6286800 ∧
    siCeilingFor 2025 = siCeiling := by decide

/-- CBL Schedule para 4 Table A as replaced by Law 98(I)/2024 art. 4(α) (Ε.Ε. Παρ. Ι(Ι) Αρ. 5006, 26.7.2024;
`~/cmp20/improve-central/refs/cy/2024_1_098.txt`), whose art. 5 reads "Η ισχύς του παρόντος Νόμου λογίζεται ότι
άρχισε την 1η Ιανουαρίου 2024": 588 / 526 / 470 / 0; 705 / 643 / 470 / 427; 1.293 / 1.231 / 940 / 854;
2.073 / 1.887 / 1.559 / 1.404 euros per child. The same law moved the para 7 indexation start from 2018 to 2025, so
2024 is paid at the printed amounts. -/
def cbTable2024 : List (List Int) :=
  [[58800, 52600, 47000, 0], [70500, 64300, 47000, 42700], [129300, 123100, 94000, 85400],
   [207300, 188700, 155900, 140400]]

/-- 2022 and 2023: CBL Table A as set by Law 118(I)/2017 (from 1.1.2018, `refs/cy/2017_1_118.txt`): 475 / 425 /
380 / 0; 570 / 520 / 380 / 345; 1.045 / 995 / 760 / 690; 1.675 / 1.525 / 1.260 / 1.135 euros, indexed "Από την 1
Ιανουαρίου 2018 ... κάθε 1 Ιανουαρίου" by the average Automatic Cost-of-Living Adjustment (para 7, 2017 text). The
indexed amounts are printed in no law; the paid amounts are EUROMOD CR Cyprus 2022-2025 Table 2.6 (source: Welfare
Benefit Services): every cell is the 2018 amount x 1,0451 (2022) and x 1,1368 (2023). -/
def cbTable2022 : List (List Int) :=
  [[49642, 44417, 39714, 0], [59571, 54345, 39714, 36056], [109213, 103987, 79428, 72112],
   [175054, 159378, 131683, 118619]]
def cbTable2023 : List (List Int) :=
  [[53998, 48314, 43198, 0], [64798, 59114, 43198, 39220], [118796, 113112, 86397, 78439],
   [190414, 173362, 143237, 129027]]

def cbTableFor (year : Nat) : List (List Int) :=
  if year ≤ 2022 then cbTable2022 else if year = 2023 then cbTable2023 else if year = 2024 then cbTable2024
  else cbTable2025

/-- CBL Schedule para 2(β) before Law 46(I)/2025: 59.000 euros for two children "και στην περίπτωση περισσότερων
εξαρτώμενων τέκνων αυξάνεται κατά πέντε χιλιάδες ευρώ (€5.000) για κάθε επιπρόσθετο τέκνο" (118(I)/2017);
46(I)/2025 art. 3(α) removed the limit for five or more children (2025). -/
def cbLimitFor (year : Nat) (n : Nat) : Int :=
  if year ≥ 2025 then cbLimit n
  else if n ≤ 1 then 4900000 else 5900000 + 500000 * ((n : Int) - 2)

/-- Table B (single-parent benefit, monthly per child): 2024 Law 98(I)/2024 art. 4(δ) "€ 212" / "€ 189"; 2022-2023
the 118(I)/2017 amounts 180 / 160 euros indexed under para 7, paid 188,12 / 167,22 (2022) and 204,62 / 181,89 (2023)
(EUROMOD CR Table 2.7, source: Grants and Benefits Services). -/
def spMonthlyFor (year : Nat) : Int × Int :=
  if year ≤ 2022 then (18812, 16722) else if year = 2023 then (20462, 18189)
  else if year = 2024 then (21200, 18900) else (spMonthly2025Low, spMonthly2025High)

/-! ## Eurostat convention `--eurostat` (round 10): a no-op for Cyprus
Eurostat earn_net ESMS 3.4 ("parameters refer to the beginning of the fiscal year"; "the most generous" family allowance
within ages 6-11; tests/data/_methodology/earn_net_esms.htm, sha256 89ab2734...). Checked in the dated texts used by
this model: in 2022-2025 the SI rate, the GESY rate, the insurable-earnings ceiling and the ITL scale change only on
1 January, and the child benefit (Table A) and single-parent benefit (Table B) do not vary with age within 6-11. The
flag is accepted and changes nothing (400 households per year, round 10). -/

end CYTax
