import TaxKernel

/-!
# Greece 2025: parameters, each with its source

Money is in **euro cents** (Int): the Greek return (εκκαθαριστικό) computes tax to the cent. Rates are basis points.

Statute: Κώδικας Φορολογίας Εισοδήματος (ΚΦΕ), ν. 4172/2013, read in the official administrative codification of
the Ministry of National Economy and Finance (ΥΠΕΘΟΟ, ΑΔΑ Ε7ΔΠΗ-Φ32, 06.04.2026,
https://diavgeia.gov.gr/doc/Ε7ΔΠΗ-Φ32; local copy `law/src/kfe_codif.txt`). That codification prints the text as in
force after ν. 5246/2025 (tax year 2026) and gives every earlier wording, with the years it applied to, in its
footnotes; the 2025 wordings used below are those footnotes (cited "codif. fn N", with the page). Global law holds
only the 2013 text and this codification, so its "as in force on 2025-06-30" answer is the 2013 text (FINDINGS F9).
-/

namespace GRTax
open TaxKernel

/-- Euros to cents. -/
def eur (x : Int) : Int := 100 * x

/-! ## Art. 15 par. 1: the scale for wages, pensions and business profits -/

/-- ΚΦΕ art. 15 par. 1 as replaced by ν. 4646/2019 art. 6, "εφαρμόζεται για εισοδήματα που αποκτώνται από
01.01.2020" until the tax year 2025 (codif. fn 78, p. 190-191): "0-10.000 9% / 10.001-20.000 22% /
20.001-30.000 28% / 30.001-40.000 36% / 40.001 44%". Thresholds in cents. -/
def scale2020 : Schedule :=
  Schedule.ofList [(0, 900), (eur 10000, 2200), (eur 20000, 2800), (eur 30000, 3600), (eur 40000, 4400)]

/-- ΚΦΕ art. 15 par. 1(α) as replaced by ν. 5246/2025 art. 3 par. 1, for income "από το φορολογικό έτος 2026"
(codif. fn 78): "0-10.000 9% 10.000,01 - 20.000 20% 20.000,01 - 30.000 26% 30.000,01 - 40.000 34%
40.000,01 - 60.000 39% >60.000 44%". Used only for `year = 2026` (versioned-law comparisons). -/
def scale2026base : List (Int × Int) :=
  [(0, 900), (eur 10000, 2000), (eur 20000, 2600), (eur 30000, 3400), (eur 40000, 3900), (eur 60000, 4400)]

/-- ΚΦΕ art. 15 par. 1(β)-(ε) (2026): second band 18/16/9 % with 1/2/3 children, 0 % for the first two bands with
4+ children; third band 24/22/20/18 % for 1-4 children, "μειώνεται περαιτέρω κατά δύο ποσοστιαίες μονάδες (2%) για
κάθε επιπλέον εξαρτώμενο τέκνο άνω των τεσσάρων"; under 25: 0 % and 26-30: 9 % on the first two bands. -/
def scale2026 (kids : Nat) (age : Nat) : Schedule :=
  let b2 : Int := if kids ≥ 4 then 0 else if kids = 3 then 900 else if kids = 2 then 1600 else if kids = 1 then 1800 else 2000
  let b1 : Int := if kids ≥ 4 then 0 else 900
  let b3 : Int := if kids = 0 then 2600 else if kids ≤ 4 then 2600 - 200 * (kids : Int) else max 0 (1800 - 200 * ((kids : Int) - 4))
  let young : Option Int := if age ≤ 25 then some 0 else if age ≤ 30 then some (if kids ≥ 4 then 0 else 900) else none
  let (b1, b2) := match young with | some r => (min b1 r, min b2 r) | none => (b1, b2)
  Schedule.ofList [(0, b1), (eur 10000, b2), (eur 20000, b3), (eur 30000, 3400), (eur 40000, 3900), (eur 60000, 4400)]

def scaleFor (year : Nat) (kids : Nat) (age : Nat) : Schedule :=
  if year ≥ 2026 then scale2026 kids age else scale2020

/-! ## Art. 16: μείωση φόρου (the tax reduction) -/

/-- ΚΦΕ art. 16 par. 1, second sentence as replaced by ν. 5045/2023 art. 43, "η ισχύς του αρχίζει από το
φορολογικό έτος 2024" (codif. fn 98-100, p. 196-197): 777 € without children; "εννιακόσια (900) ευρώ ... ένα (1)
εξαρτώμενο τέκνο, ... χίλια εκατόν είκοσι (1.120) ... δύο (2) ..., ... χίλια τριακόσια σαράντα (1.340) ... τρία (3)
..., ... χίλια πεντακόσια ογδόντα (1.580) ... τέσσερα (4) ... και ... χίλια επτακόσια ογδόντα (1.780) ευρώ για πέντε
(5) εξαρτώμενα τέκνα". Third sentence, left as written by ν. 4646/2019: "Για κάθε επιπλέον εξαρτώμενο τέκνο μετά
το τέταρτο, η μείωση του φόρου αυξάνεται κατά διακόσια είκοσι (220) ευρώ". Five children: the listed 1,780
(the explicit amount); six or more: 1,780 + 220 per child after the fifth (the reading AADE applies; the literal
"after the fourth" would give 1,800 for five: FINDINGS F2). -/
def credit2024 (kids : Nat) : Int :=
  match kids with
  | 0 => eur 777 | 1 => eur 900 | 2 => eur 1120 | 3 => eur 1340 | 4 => eur 1580
  | n + 5 => eur 1780 + eur 220 * (n : Int)

/-- The literal reading of the third sentence for five or more children: 1,580 + 220 per child after the
fourth (F2). -/
def credit2024literal (kids : Nat) : Int :=
  if kids ≥ 5 then eur 1580 + eur 220 * ((kids : Int) - 4) else credit2024 kids

/-- ΚΦΕ art. 16 par. 1 as replaced by ν. 4646/2019 art. 9 for income from 01.01.2020 (tax years 2020-2023;
codif. fn 98, p. 197): 777 / "οκτακόσια δέκα (810)" / 900 / 1,120 / 1,340 for 0-4 children, + 220 per child after
the fourth. -/
def credit2020 (kids : Nat) : Int :=
  match kids with
  | 0 => eur 777 | 1 => eur 810 | 2 => eur 900 | 3 => eur 1120
  | n + 4 => eur 1340 + eur 220 * (n : Int)

def creditFull (year : Nat) (kids : Nat) : Int :=
  if year ≥ 2024 then credit2024 kids else credit2020 kids

/-- ΚΦΕ art. 16 par. 2 (ν. 4646/2019 art. 9, unchanged in 2024-2025): "Για φορολογητέο εισόδημα από μισθωτές
υπηρεσίες και συντάξεις, το οποίο υπερβαίνει το ποσό των δώδεκα χιλιάδων (12.000) ευρώ, το ποσό της μείωσης
μειώνεται κατά είκοσι (20) ευρώ ανά χίλια (1.000) ευρώ ... Οι προβλέψεις του προηγούμενου εδαφίου δεν εφαρμόζονται
για φορολογούμενους με πέντε (5) εξαρτώμενα τέκνα και άνω." 20 per 1,000 = 2 per 100, applied continuously (as
the OECD's BTC and the εκκαθαριστικό do), rounded down to the cent. -/
def creditTaper (year : Nat) (kids : Nat) : Taper :=
  if kids ≥ 5 then Taper.fixed (creditFull year kids)
  else { full := creditFull year kids, start := eur 12000, num := 2, den := 100 }

/-! ## Art. 11: dependent children -/

/-- ΚΦΕ art. 11 par. 1(β): "άγαμα τέκνα, εφόσον: είναι ανήλικα έως 18 ετών ή είναι ενήλικα έως 25 ετών και
φοιτούν ..." (students, registered unemployed, conscripts). The canonical household gives ages only: children under
18 count; children 18-24 count when the input says `gr_childrenInEducation: true`. Par. 2: not a dependant if own
taxable income > 3,000 € (children are assumed to have none). -/
def dependantAgeLimit : Nat := 18
def studentAgeLimit : Nat := 25

/-! ## Art. 40: capital income; art. 39: rents; art. 42: shares -/

/-- ΚΦΕ art. 40 par. 1 (ν. 4646/2019 art. 24, from 1.1.2020; codif. fn 267): "Τα μερίσματα φορολογούνται με
συντελεστή πέντε τοις εκατό (5%)." Withheld at source, final (art. 64). -/
def dividendRate : Int := 500
/-- ΚΦΕ art. 40 par. 2: "Οι τόκοι φορολογούνται με συντελεστή δεκαπέντε τοις εκατό (15%)". -/
def interestRate : Int := 1500
/-- ΚΦΕ art. 40 par. 4 as in force for 2020-2025 (ν. 4646/2019 art. 7 par. 2; codif. fn 269, p. 251): "0 -
12.000 15% / 12.001 – 35.000 35% / 35.001 - 45%" (rents taxed separately, "αυτοτελώς"). -/
def rentScale2020 : Schedule := Schedule.ofList [(0, 1500), (eur 12000, 3500), (eur 35000, 4500)]
/-- ΚΦΕ art. 40 par. 4 from the tax year 2026 (ν. 5246/2025 art. 8): "0 - 12.000 15% / 12.000,01 – 24.000 25% /
24.000,01 – 36.000 35% / >36.000 45%". -/
def rentScale2026 : Schedule := Schedule.ofList [(0, 1500), (eur 12000, 2500), (eur 24000, 3500), (eur 36000, 4500)]
def rentScale (year : Nat) : Schedule := if year ≥ 2026 then rentScale2026 else rentScale2020
/-- ΚΦΕ art. 39 (as codified, par. on deductions): gross rent is reduced by "πέντε τοις εκατό (5%) για δαπάνες
επισκευής, συντήρησης, ανακαίνισης". -/
def rentDeduction : Int := 500
/-- ΚΦΕ art. 42 par. 1-2: a gain on listed shares is taxed at 15 % (art. 43) only for a holding "τουλάχιστον
μισό τοις εκατό (0,5%)" of the company's capital; the canonical `capitalGains` (long-held listed shares, a portfolio
holding) is therefore exempt unless `gr_substantialHolding: true`. -/
def gainRate : Int := 1500

/-! ## Art. 15 par. 6: the card-spending requirement -/

/-- ΚΦΕ art. 15 par. 6(β): required card spending "τριάντα τοις εκατό (30%) του πραγματικού εισοδήματος που
προέρχεται από μισθωτή εργασία – συντάξεις και επιχειρηματική δραστηριότητα και μέχρι είκοσι χιλιάδες (20.000)
ευρώ δαπανών"; the tax is increased by the shortfall "πολλαπλασιαζόμενης με συντελεστή είκοσι δύο τοις εκατό
(22%)". Applied only when the input gives `gr_cardSpending1/2` (euros); otherwise the requirement is assumed met. -/
def cardShare : Int := 3000
def cardCap : Int := eur 20000
def cardPenaltyRate : Int := 2200

/-! ## Art. 28Α: minimum presumed income of a sole trader (ν. 5073/2023 art. 15, tax years 2023+) -/

/-- ΚΦΕ art. 28Α par. 2(α): the presumed minimum is "το ετήσιο ποσό του μικτού κατώτατου μισθού ... όπως ισχύει
κατά την τελευταία ημέρα του αντίστοιχου φορολογικού έτους, προσαυξανόμενου κατά δέκα τοις εκατό (10%)" for each
three-year period after the second; capped at 50,000 €. The 2025 minimum wage is **not verified from a primary
source in this work** (lead: 880 € a month from 1.4.2025, 14 payments): the rule runs only when the input gives
`gr_minWageMonthly` (euros) and `gr_yearsInBusiness`. -/
def presumedCap : Int := eur 50000

/-! ## Employee social contributions (e-ΕΦΚΑ), dependent employment, KPK 101 -/

/-- Employee contribution rate 2025: 13.37 % of all earnings. Evidence: (1) e-ΕΦΚΑ Εγκύκλιος 40/2024 (ΑΔΑ
97ΙΝ46ΜΑΠΣ-73Λ) on ν. 5162/2024 art. 12 (amending ν. 4387/2016 art. 41 par. 1): from 01/01/2025 the health
in-kind rate "μειώνονται ... κατά μισή (0,50) ποσοστιαία μονάδα ... για ασφαλισμένο", giving 1.65 % in kind +
0.40 % in cash = 2.05 % for the employee; (2) the OECD Taxing Wages records for Greece give exactly 13.87 % in 2023
and 2024 and 13.37 % in 2025 (EECSSC / GEBT, all eight household types). The split of the other 11.32 % (main
pension, supplementary pension, ΔΥΠΑ) is not verified here from a primary text. Audit round 8: e-ΕΦΚΑ Εγκύκλιος
5/2024 (`improve-central/refs/gr/egk5_2024.pdf`) states the branch totals from 01.01.2024, "για κύρια σύνταξη ... το
ποσοστό ασφαλιστικών εισφορών του κλάδου ανέρχεται σε 13,33%" and "για υγειονομική περίθαλψη ... 6,95% (παροχές σε
είδος 6,45%, σε χρήμα 0,50%)", but not the employee/employer split, so the employee shares stay unverified. -/
def employeeRate (year : Nat) : Int := if year ≥ 2025 then 1337 else 1387

/-- Monthly ceiling of insurable earnings, ν. 4387/2016 art. 38 par. 2: "από 01.01.2025, στο ποσό των 7.572,62
ευρώ (€) μηνιαίως" (e-ΕΦΚΑ Εγκύκλιος 3/2025). Annual wages are taken as paid in 14 instalments (12 months, the
Christmas bonus, the Easter bonus and the holiday allowance, which together equal two months), so the annual
ceiling is 14 × 7,572.62 (modelling convention, FINDINGS M1). Earlier years: `monthlyCeilingFor` below (cited per
year, round 3). -/
def monthlyCeiling : Int := 757262
def payments : Int := 14

/-- Earlier years (improvement round 3, copies in `~/cmp20/improve-central/refs/gr/`): ν. 4387/2016 art. 38 par. 2 as
quoted in e-ΕΦΚΑ Εγκύκλιος 8/13.02.2024 (ΑΔΑ 68Φ346ΜΑΠΣ-ΘΞ4, `egk8_2024.pdf`): "Το ανώτατο όριο ασφαλιστέων
αποδοχών ... ορίζεται στο ποσό των έξι χιλιάδων πεντακοσίων (6.500) ευρώ, αναπροσαρμοζόμενο από την 1.1.2023 έως
31.12.2024 κατ' έτος με διαπιστωτική πράξη ... κατά το ποσοστό μεταβολής του μέσου ετήσιου γενικού δείκτη τιμών
καταναλωτή του προηγούμενου έτους": 2022 €6.500; 2023 €7.126,94 (Δ.15/Δ'/9801/30.01.2023, ΦΕΚ Β' 1063/24.02.2023, as
cited in e-ΕΦΚΑ Εγκύκλιος 5/2024, `egk5_2024.pdf`); 2024 €7.373,53 (Δ.15/Δ'/3201/16.1.2024, ΦΕΚ Β' 410/22.1.2024:
"προσαυξάνεται κατά 3,46% και διαμορφώνεται στο ποσό των 7.373,53 ευρώ", Εγκύκλιος 8/2024); 2025 as above. -/
def monthlyCeilingFor (year : Nat) : Int :=
  if year ≤ 2022 then 650000 else if year = 2023 then 712694 else if year = 2024 then 737353 else monthlyCeiling

def efka (year : Nat) : Contribution :=
  { name := "EFKA", sched := Schedule.flat (employeeRate year), ceiling := payments * monthlyCeilingFor year,
    round := Rule.unitHalfUp }

/-! ## Tax year 2022 (improvement round 2, 2026-11-19) -/

/-- January-May 2022: ν. 4387/2016 art. 97 as in force (e-ΕΦΚΑ Γενικό Έγγραφο 226245/17.05.2022, ΑΔΑ
Ψ27Ζ46ΜΑΠΣ-ΖΞΖ, copy `~/cmp20/improve-central/refs/gr/efka_226245_2022.txt`): "από 01.06.2022 ... Το συνολικό
ποσοστό εισφορών διαμορφώνεται/μειώνεται σε 6% (από 6,50%), επιμεριζόμενο εξίσου ... σε ασφαλισμένο και εργοδότη"
(supplementary pension branch): the employee's share falls from 3.25 % to 3 % on 1 June 2022. The other branches are
taken at the 2023 total (`employeeRate 2023` = 13.87 %, whose evidence is stated above): 14.12 % before June 2022,
13.87 % from June. -/
def employeeRate2022H1 : Int := 1412

/-- The share of a year's pay at the January-May rate: of the 14 instalments of `payments`, the January-May
salaries (5) and the Easter bonus (half a month, due before Easter, 24 April 2022): 5.5 / 14 = 11 / 28 (the same
14-instalment convention as `payments`; the Christmas bonus and the holiday allowance fall after June). -/
def oldRateNum : Int := 11
def oldRateDen : Int := 28

def efka2022H1 : Contribution :=
  { name := "EFKA 2022 Jan-May", sched := Schedule.flat employeeRate2022H1,
    ceiling := divR .down (payments * monthlyCeilingFor 2022 * oldRateNum) oldRateDen, round := Rule.unitHalfUp }
def efka2022H2 : Contribution :=
  { name := "EFKA 2022 Jun-Dec", sched := Schedule.flat 1387,
    ceiling := payments * monthlyCeilingFor 2022 - divR .down (payments * monthlyCeilingFor 2022 * oldRateNum) oldRateDen,
    round := Rule.unitHalfUp }

/-- Convention (`--oecd`, not statute): the OECD spreads the year's pay evenly over 12 months, so 5/12 of it is
at the January-May rate (OECD Taxing Wages 2022 convention; the bonuses are not dated). -/
def oldRateNumOecd : Int := 5
def oldRateDenOecd : Int := 12

/-- Convention (`--eurostat`, NOT statute): Eurostat earn_net ESMS 3.4, "Income tax and social security contributions
parameters refer to the beginning of the fiscal year, i.e. changes occurring later during the year are ignored"
(tests/data/_methodology/earn_net_esms.htm, sha256 89ab2734...): the rate of 1 January applies all year. Only 2022
has a mid-year change (14.12 % until 31 May); 2023-2025 have none, so the flag changes nothing there. -/
def efka2022Jan : Contribution :=
  { name := "EFKA 2022 (rate of 1 January)", sched := Schedule.flat employeeRate2022H1,
    ceiling := payments * monthlyCeilingFor 2022, round := Rule.unitHalfUp }

/-- Convention (`--euromod`, NOT statute; round 15): EUROMOD's legislative parameters are those in force on 30 June of
the policy year ("Legislative parameters of the tax system are referred in EM to 30 June": EUROMOD "Nowcasting prices"
note, Feb 2025, sections 1.3-1.4, software/euromod/model/Documentation, sha256 64eb954e350abd1c...;
tests/convention_policy.json "euromod_convention_mode", GR entry). No GR country report is available locally, so the
general rule applies: the rate in force on 30 June 2022 (13.87 %, after the 1 June 2022 cut of the supplementary
pension share, e-ΕΦΚΑ 226245/17.05.2022) for the whole of 2022. 2023-2025 have no mid-year EFKA change. -/
def efka2022Jun : Contribution :=
  { name := "EFKA 2022 (rate of 30 June)", sched := Schedule.flat 1387,
    ceiling := payments * monthlyCeilingFor 2022, round := Rule.unitHalfUp }

/-- The employee contribution of the year on annual wages `w` (cents). -/
def efkaAmount (year : Nat) (w : Int) (oecd : Bool := false) (es : Bool := false) (em : Bool := false) : Int :=
  if year = 2022 && em then efka2022Jun.amount w else
  if year = 2022 && es then efka2022Jan.amount w else
  if year = 2022 then
    let w1 := if oecd then divR .down (w * oldRateNumOecd) oldRateDenOecd else divR .down (w * oldRateNum) oldRateDen
    efka2022H1.amount w1 + efka2022H2.amount (w - w1)
  else (efka year).amount w

/-- ΚΦΕ art. 43Α par. 3 (scale as in the codification, the ν. 4472/2017 replacement having been repealed by ν.
4618/2019 before it applied; codif. fn 316): "0 – 12.000 0% / 12.001 - 20.000 2,20% / 20.001 - 30.000 5,00% /
30.001 - 40.000 6,50% / 40.001 - 65.000 7,50% / 65.001 - 220.000 9,00% / >220.000 10,00%". -/
def solidarityScale : Schedule :=
  Schedule.ofList [(0, 0), (eur 12000, 220), (eur 20000, 500), (eur 30000, 650), (eur 40000, 750),
    (eur 65000, 900), (eur 220000, 1000)]

/-- ΚΦΕ art. 72 par. 74 (codif. fn 308): "Για το φορολογικό έτος 2022 απαλλάσσονται από την ειδική εισφορά
αλληλεγγύης του άρθρου 43Α τα εισοδήματα που προβλέπονται στο άρθρο αυτό, με εξαίρεση τα εισοδήματα από μισθωτή
εργασία στον δημόσιο τομέα και τις συντάξεις. ... Η ειδική εισφορά αλληλεγγύης του άρθρου 43Α καταργείται για όλα
τα εισοδήματα του άρθρου αυτού που αποκτώνται από την 1η.1.2023 και εφεξής." So in 2022 only pensions and
public-sector wages (net of contributions) bear it; nothing from 2023. -/
def solidarity (year : Nat) (base : Int) : Int :=
  if year = 2022 then solidarityScale.tax Rule.unitHalfUp (pos base) else 0

/-! ## Child benefit (επίδομα παιδιού, OPEKA form A21), ν. 4512/2018 art. 214 -/

/-- ν. 4512/2018 art. 214 par. 4 (ΦΕΚ Α' 5/17.01.2018, p. 170): equivalence scale "πρώτος γονέας: στάθμιση 1,
δεύτερος γονέας: στάθμιση 1/2, κάθε εξαρτώμενο τέκνο: στάθμιση 1/4. Ειδικά για τις μονογονεϊκές οικογένειες, το
πρώτο εξαρτώμενο τέκνο έχει στάθμιση 1/2". In quarters. -/
def scaleQuarters (parents : Nat) (kids : Nat) : Int :=
  if kids = 0 then 4 * (parents : Int) else
  if parents ≥ 2 then 4 + 2 + (kids : Int) else 4 + 2 + ((kids : Int) - 1)

/-- Art. 214 par. 5-6: categories of equivalised income "έως έξι χιλιάδες (6.000)", "από 6.001 έως 10.000",
"από 10.001 έως 15.000"; monthly amounts 70/42/28 € for each of the first two children and 140/84/56 € for "το
τρίτο και κάθε εξαρτώμενο τέκνο πέραν του τρίτου" (amounts confirmed unchanged on the OPEKA page
https://www.opeka.gr/oikogeneies/epidoma-paidiou-a21/, read 2026-11-19). Returns the annual benefit in cents. -/
def childBenefitAnnual (equivCents : Int) (kids : Nat) : Int :=
  let (a, b) : Int × Int :=
    if equivCents ≤ eur 6000 then (70, 140) else if equivCents ≤ eur 10000 then (42, 84)
    else if equivCents ≤ eur 15000 then (28, 56) else (0, 0)
  let k : Int := kids
  eur 12 * (a * min k 2 + b * pos (k - 2))

/-- Art. 214 par. 8: children count while unmarried and "δεν υπερβαίνουν το 18ο έτος" (to 24 in tertiary
education). -/
def benefitAgeLimit : Nat := 18

end GRTax
