import DeTax.Params

/-!
# Veranlagungszeiträume 2024 and 2025 (round 2, improve-continental)

`YP` holds every amount of `DeTax.P` (Params.lean, VZ 2025) under the same names, so that a function that starts
with `let P := ypFor yr` reads the year's amount wherever it wrote `P.x`. 2025 is `Params.lean` unchanged.

VZ 2024, each amount with its dated source (copies in `cmp/de/refs/bmf/`, `cmp/de/refs/bmfde/`,
`cmp/de/law/hist/`):
* § 32a (1) tariff 2024 as amended by the Gesetz zur Fortentwicklung des Steuerrechts und zur Anpassung des
  Einkommensteuertarifs (Steuerfortentwicklungsgesetz, BGBl. 2024 I Nr. 449, retroactive for VZ 2024): BMF
  "Tarifhistorie" (bmf-steuerrechner.de, 2025-10-14), "32. Einkommensteuertarif 2024": "a) bis 11.784 €
  (Grundfreibetrag): 0; b) 11.785 € bis 17.005 €: ESt = (954,80 * y + 1.400) * y; c) 17.006 € bis 66.760 €: ESt =
  (181,19 * z + 2.397) * z + 991,21; d) 66.761 € bis 277.825 €: ESt = 0,42 * zvE - 10.636,31; e) ab 277.826 €:
  ESt = 0,45 * zvE - 18.971,06".
* EStG amounts for 2024 (BMF "Datensammlung zur Steuerpolitik 2026", Tabelle 2.10, columns 2024): § 9a
  Arbeitnehmerpauschbetrag 1.230, § 20 (9) Sparer-Pauschbetrag 1.000, § 24b 4.260, § 32 (6) Kinderfreibetrag 3.306
  (Steuerfortentwicklungsgesetz, retroactive) and BEA 1.464, § 66 (1) Kindergeld 250 a month (Tabelle 2.8.1); § 10 (3)
  Höchstbetrag 27.566 (= 24,7 % x 111 600 knappschaftliche BBG, SVBezGrV 2024 § 4 (1) Nr. 2, aufgerundet); Tabelle
  2.11 SolZ Freigrenze 18.130 / 36.260.
* Social insurance 2024: SVBezGrV 2024 (BGBl. 2023 I Nr. 322) § 1 (1) Bezugsgröße 3 535 Euro a month, § 2 (2)
  62 100 Euro (KV/PV BBG), § 4 (1) Nr. 1 BBG RV 90 600 Euro; RV 18,6 % (unchanged, Beitragssatzbekanntmachung 2024);
  AV 2,6 % (SGB III § 341 (2)); KV 14,6 % (SGB V § 241) and the average Zusatzbeitrag 1,7 % for 2024 (BMG
  Bekanntmachung of 31 October 2023); PV 3,4 %, employee 1,7 %, childless + 0,6, - 0,25 per child from the second
  to the fifth (SGB XI § 55 as amended by the Pflegeunterstützungs- und -entlastungsgesetz, BGBl. 2023 I Nr. 155,
  from 1 July 2023); Geringfügigkeitsgrenze 538 Euro (SGB IV § 8 (1a): Mindestlohn 12,41 Euro (MiLoV4) x 130 / 3,
  aufgerundet); Übergangsbereich up to 2 000 Euro (SGB IV § 20 (2)); F = 28 / (18,6 + 3,4 + 2,6 + 14,6 + 1,7) =
  0,6846; minimum base for voluntary members 4 x 3 535 = 14 140 Euro a year, family insurance 3 535 / 7 = 505 Euro.
Not changed for 2024 (same wording 2024 and 2025): § 9a Nr. 3, § 10 (4), § 10c, § 10b, § 24b (2) increment, § 32d,
SolZG §§ 3-4 rates, the Krankengeld cut, the ermäßigter KV-Beitragssatz. The § 22 / § 24a tables are by year of
pension start / 64th birthday and are kept as in 2025 (pension households: flagged in `unsupported`).
VZ 2022 and 2023 are not modelled: mid-year changes (2022: Minijob and Übergangsbereich from 1 October,
Kinderbonus, Energiepreispauschale; 2023: PV 3,05 % to 3,4 % from 1 July) need monthly contributions.
-/

namespace DeTax

structure YP where
  year : Int
  tarif : Tarif
  arbeitnehmerPausch : Int
  wkPausch22 : Int
  sparerPausch : Int
  sonderausgabenPausch : Int
  hb10_3 : Int
  hb10_4 : Int
  hb10_4Employee : Int
  kvKrankengeldCutBp : Int
  spendenQuoteBp : Int
  entlastungAE : Int
  entlastungAEWeiteres : Int
  kinderfreibetrag : Int
  bea : Int
  kindergeldMonat : Int
  abgeltungBp : Int
  besteuerungsanteil : Int → Int
  altersentlastung : Int → Int × Int
  soliRate : Int
  soliMilderung : Int
  soliFreigrenze : Bool → Int
  rvEmployeeBp : Int
  avEmployeeBp : Int
  kvEmployeeBp : Int
  kvZusatzBp : Int
  kvErmaessigtBp : Int
  pvBp : Int
  pvEmployeeBp : Int
  pvKinderlosBp : Int
  pvAbschlagBp : Int
  bbgRV : Int
  bbgKV : Int
  minijobMonat : Int
  uebergangOG : Int
  faktorF : Int
  bezugsgroesseMonat : Int
  mindestBemessungJahrC : Int
  familienversicherungMonat : Int
  /-- PV rates in hundredths of a basis point (round 4), so that a year whose rate changed mid-year can carry the
  annual average exactly: full rate, employee half, childless surcharge, per-child Abschlag. -/
  pvFull100 : Int
  pvEmp100 : Int
  pvKl100 : Int
  pvAb100 : Int
  /-- Kindergeld a month by the child's rank (oldest = 1), § 66 (1); one-off Kinderbonus per child (2022). -/
  kgRank : Nat → Int
  kinderbonus : Int
  /-- § 10 (3) Satz 4-6: the share of Altersvorsorgeaufwendungen deductible (basis points; 94 % in 2022). -/
  altQuoteBp : Int
  /-- Energiepreispauschale per employee (EStG §§ 112-122 as inserted by the Steuerentlastungsgesetz 2022, BGBl. I
  2022 S. 749: § 112 (2) "Die Höhe der Energiepreispauschale beträgt 300 Euro"; § 119 (1): an employee's EPP is
  taxable as Arbeitslohn). 0 outside 2022. -/
  epp : Int

def y2025 : YP :=
  { year := 2025, tarif := t2025, arbeitnehmerPausch := P.arbeitnehmerPausch, wkPausch22 := P.wkPausch22,
    sparerPausch := P.sparerPausch, sonderausgabenPausch := P.sonderausgabenPausch, hb10_3 := P.hb10_3,
    hb10_4 := P.hb10_4, hb10_4Employee := P.hb10_4Employee, kvKrankengeldCutBp := P.kvKrankengeldCutBp,
    spendenQuoteBp := P.spendenQuoteBp, entlastungAE := P.entlastungAE,
    entlastungAEWeiteres := P.entlastungAEWeiteres, kinderfreibetrag := P.kinderfreibetrag, bea := P.bea,
    kindergeldMonat := P.kindergeldMonat, abgeltungBp := P.abgeltungBp, besteuerungsanteil := P.besteuerungsanteil,
    altersentlastung := P.altersentlastung, soliRate := P.soliRate, soliMilderung := P.soliMilderung,
    soliFreigrenze := P.soliFreigrenze, rvEmployeeBp := P.rvEmployeeBp, avEmployeeBp := P.avEmployeeBp,
    kvEmployeeBp := P.kvEmployeeBp, kvZusatzBp := P.kvZusatzBp, kvErmaessigtBp := P.kvErmaessigtBp,
    pvBp := P.pvBp, pvEmployeeBp := P.pvEmployeeBp, pvKinderlosBp := P.pvKinderlosBp,
    pvAbschlagBp := P.pvAbschlagBp, bbgRV := P.bbgRV, bbgKV := P.bbgKV, minijobMonat := P.minijobMonat,
    uebergangOG := P.uebergangOG, faktorF := P.faktorF, bezugsgroesseMonat := P.bezugsgroesseMonat,
    mindestBemessungJahrC := P.mindestBemessungJahrC, familienversicherungMonat := P.familienversicherungMonat,
    pvFull100 := 100 * P.pvBp, pvEmp100 := 100 * P.pvEmployeeBp, pvKl100 := 100 * P.pvKinderlosBp,
    pvAb100 := 100 * P.pvAbschlagBp, kgRank := fun _ => P.kindergeldMonat, kinderbonus := 0,
    altQuoteBp := 10000, epp := 0 }

/-- § 66 (1) 2023-2024: 250 Euro for every child (Datensammlung Tab. 2.8.1). -/
def kg250 (_ : Nat) : Int := 250

/-- § 32a (1) VZ 2024 (BMF Tarifhistorie, see the module doc). -/
def t2024 : Tarif where
  vz := 2024
  gfb := 11784
  e2 := 17005
  e3 := 66760
  e4 := 277825
  a2 := 95480
  b2 := 1400
  a3 := 18119
  b3 := 2397
  c3 := 99121
  r4 := 42
  c4 := 1063631
  r5 := 45
  c5 := 1897106

/-- SolZG 1995 § 3 (3) for 2024 (Datensammlung Tabelle 2.11): 18 130 / 36 260 Euro. -/
def soliFreigrenze2024 (joint : Bool) : Int := if joint then 36260 else 18130

def y2024 : YP :=
  { y2025 with
    year := 2024
    tarif := t2024
    hb10_3 := 27566
    kinderfreibetrag := 3306
    kindergeldMonat := 250
    soliFreigrenze := soliFreigrenze2024
    kvZusatzBp := 170
    pvBp := 340
    pvEmployeeBp := 170
    bbgRV := 90600
    bbgKV := 62100
    minijobMonat := 538
    faktorF := 6846
    bezugsgroesseMonat := 3535
    mindestBemessungJahrC := 1414000
    familienversicherungMonat := 505
    pvFull100 := 34000
    pvEmp100 := 17000
    kgRank := kg250 }

theorem hb10_3_2024_ok : y2024.hb10_3 = cdiv (2470 * 111600) 10000 := by decide
theorem minijob_2024_ok : y2024.minijobMonat = cdiv (1241 * 130) 300 := by decide
theorem faktorF_2024_ok : y2024.faktorF = rndHalf (280 * 10000) (186 + 34 + 26 + 146 + 17) := by decide

/-! ## VZ 2023 (round 4)

* § 32a (1) 2023: BMF Tarifhistorie "31. Einkommensteuertarif 2023": "a) bis 10.908 € (Grundfreibetrag): 0; b) 10.909 €
  bis 15.999 €: ESt = (979,18 * y + 1.400) * y; c) 16.000 € bis 62.809 €: ESt = (192,59 * z + 2.397) * z + 966,53;
  d) 62.810 € bis 277.825 €: ESt = 0,42 * zvE - 9.972,98; e) ab 277.826 €: ESt = 0,45 * zvE - 18.307,73".
* BMF Datensammlung 2026 Tab. 2.10 / 2.8.1 / 2.11 (column 2023): Arbeitnehmerpauschbetrag 1.230, Sparer-Pauschbetrag
  1.000, § 24b 4.260, Kinderfreibetrag 3.012 (x 2 = 6.024) + BEA 1.464, Kindergeld 250 a month, § 10 (3) Höchstbetrag
  26.528 (= 24,7 % x 107 400, SVBezGrV 2023 § 4 (1) Nr. 2), SolZ Freigrenze 17.543 / 35.086.
* SVBezGrV 2023 (BGBl. I 2022 S. 2128; gesetze-im-internet.de/svbezgrv_2023, saved in cmp/de/law/hist/): § 1 (1)
  Bezugsgröße 3 395 Euro a month, § 2 (2) 59 850 Euro (KV/PV BBG), § 4 (1) Nr. 1 87 600 Euro (RV BBG).
* KV 14,6 % + average Zusatzbeitrag 1,6 % (BMG Bekanntmachung for 2023); AV 2,6 % (SGB III § 341 (2), from 2023);
  RV 18,6 %; Geringfügigkeitsgrenze 520 Euro (Mindestlohn 12 Euro x 130 / 3); Übergangsbereich to 2 000 Euro
  (SGB IV § 20 (2) from 1.1.2023).
* PV: 1 January - 30 June 2023 3,05 %, employee 1,525 %, childless + 0,35, no per-child Abschlag (SGB XI § 55 before
  the PUEG); from 1 July 2023 3,4 %, employee 1,7 %, childless + 0,6, - 0,25 per child from the second to the fifth
  (PUEG, BGBl. 2023 I Nr. 155). With the pay spread evenly over the year the year's contribution is the annual base
  at the average of the two half-years: full 3,225 %, employee 1,6125 %, childless + 0,475 %, Abschlag 0,125 % per
  child (hundredths of a basis point: 32 250 / 16 125 / 4 750 / 1 250). Approximation stated: the Übergangsbereich
  factor F is taken as 0,6922 (= 28 / 40,45, the rates of the first half-year) for the whole year.
-/

def t2023 : Tarif where
  vz := 2023
  gfb := 10908
  e2 := 15999
  e3 := 62809
  e4 := 277825
  a2 := 97918
  b2 := 1400
  a3 := 19259
  b3 := 2397
  c3 := 96653
  r4 := 42
  c4 := 997298
  r5 := 45
  c5 := 1830773

def soliFreigrenze2023 (joint : Bool) : Int := if joint then 35086 else 17543

def y2023 : YP :=
  { y2025 with
    year := 2023
    tarif := t2023
    hb10_3 := 26528
    kinderfreibetrag := 3012
    kindergeldMonat := 250
    soliFreigrenze := soliFreigrenze2023
    kvZusatzBp := 160
    pvBp := 340
    pvEmployeeBp := 170
    bbgRV := 87600
    bbgKV := 59850
    minijobMonat := 520
    faktorF := 6922
    bezugsgroesseMonat := 3395
    mindestBemessungJahrC := 1358000
    familienversicherungMonat := 485
    pvFull100 := 32250
    pvEmp100 := 16125
    pvKl100 := 4750
    pvAb100 := 1250
    kgRank := kg250 }

theorem hb10_3_2023_ok : y2023.hb10_3 = cdiv (2470 * 107400) 10000 := by decide
theorem minijob_2023_ok : y2023.minijobMonat = cdiv (1200 * 130) 300 := by decide

/-! ## VZ 2022 (round 4)

* § 32a (1) 2022 as amended by the Steuerentlastungsgesetz 2022 (retroactive): BMF Tarifhistorie "30.
  Einkommensteuertarif 2022": "a) bis 10.347 € (Grundfreibetrag): 0; b) 10.348 € bis 14.926 €: ESt = (1.088,67 * y +
  1.400) * y; c) 14.927 € bis 58.596 €: ESt = (206,43 * z + 2.397) * z + 869,32; d) 58.597 € bis 277.825 €: ESt =
  0,42 * zvE - 9.336,45; e) ab 277.826 €: ESt = 0,45 * zvE - 17.671,20".
* BMF Datensammlung 2026 Tab. 2.10 / 2.8.1 / 2.11 (column 2022): Arbeitnehmerpauschbetrag 1.200, Sparer-Pauschbetrag
  801, § 24b 4.008, Kinderfreibetrag 2.810 + BEA 1.464, Kindergeld 219 / 219 / 225 / 250 (first, second, third, each
  further child), Altersvorsorgeaufwendungen 94 %, § 10 (3) Höchstbetrag 25.639 (= 24,7 % x 103 800), SolZ
  Freigrenze 16.956 / 33.912.
* § 66 (1) Satz 2 as inserted by the Steuerentlastungsgesetz 2022 (BGBl. I 2022 S. 749): a one-off 100 Euro for each
  child with a Kindergeld claim for July 2022 (Kinderbonus), part of the Kindergeld for § 31.
* SVBezGrV 2022 (BGBl. I 2021 S. 5044; cmp/de/law/hist/svbezgrv_2022): § 2 (1) Bezugsgröße 3 290 Euro a month,
  § 3 (1) RV ceiling 84 600 (knappschaftlich 103 800), § 4 (2) 58 050 Euro (KV/PV ceiling). KV 14,6 % + average
  Zusatzbeitrag 1,3 %; PV 3,05 % (employee 1,525), childless + 0,35 (SGB XI § 55 (3) from 1.1.2022), no per-child
  Abschlag; AV 2,4 %; RV 18,6 %.
* Two periods (pay spread evenly; each period's rules applied as an annual rate and weighted 9 : 3 months): January-
  September Geringfügigkeitsgrenze 450 Euro and Übergangsbereich to 1 300 Euro; from 1 October 2022 (Gesetz zur
  Erhöhung des Schutzes durch den gesetzlichen Mindestlohn, BGBl. I 2022 S. 969) 520 Euro and 1 600 Euro.
  Stated approximation: the employee base in the Übergangsbereich uses the October 2022 formula for both periods,
  with F = 0,7509 (January-September) and 0,7009 (October-December, = 28 / 39,95).
* Energiepreispauschale 2022 (§§ 112-122 EStG): 300 Euro for each employee with a (non-Minijob) wage, paid with the
  wage, taxable as Arbeitslohn (not a contribution base) and reported in `benefits` (cash) and detail. Not modelled:
  the EPP of the self-employed and the pensioners' EPP of December 2022 (flagged in `unsupported`).
-/

def t2022 : Tarif where
  vz := 2022
  gfb := 10347
  e2 := 14926
  e3 := 58596
  e4 := 277825
  a2 := 108867
  b2 := 1400
  a3 := 20643
  b3 := 2397
  c3 := 86932
  r4 := 42
  c4 := 933645
  r5 := 45
  c5 := 1767120

def soliFreigrenze2022 (joint : Bool) : Int := if joint then 33912 else 16956
def kg2022 (rank : Nat) : Int := if rank ≤ 2 then 219 else if rank = 3 then 225 else 250

/-- January-September 2022. -/
def y2022a : YP :=
  { y2025 with
    year := 2022
    tarif := t2022
    arbeitnehmerPausch := 1200
    sparerPausch := 801
    hb10_3 := 25639
    entlastungAE := 4008
    kinderfreibetrag := 2810
    kindergeldMonat := 219
    kgRank := kg2022
    kinderbonus := 100
    altQuoteBp := 9400
    epp := 300
    soliFreigrenze := soliFreigrenze2022
    avEmployeeBp := 120
    kvZusatzBp := 130
    pvBp := 305
    bbgRV := 84600
    bbgKV := 58050
    minijobMonat := 450
    uebergangOG := 1300
    faktorF := 7509
    bezugsgroesseMonat := 3290
    mindestBemessungJahrC := 1316000
    familienversicherungMonat := 470
    pvFull100 := 30500
    pvEmp100 := 15250
    pvKl100 := 3500
    pvAb100 := 0 }

/-- October-December 2022. -/
def y2022b : YP := { y2022a with minijobMonat := 520, uebergangOG := 1600, faktorF := 7009 }

theorem hb10_3_2022_ok : y2022a.hb10_3 = cdiv (2470 * 103800) 10000 := by decide

def ypFor (yr : Int) : YP :=
  if yr = 2022 then y2022a else if yr = 2023 then y2023 else if yr = 2024 then y2024 else y2025
def yearSupported (yr : Int) : Bool := yr = 2022 || yr = 2023 || yr = 2024 || yr = 2025

end DeTax
