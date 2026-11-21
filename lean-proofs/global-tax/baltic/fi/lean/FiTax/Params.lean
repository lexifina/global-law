import TaxKernel

/-!
# Finland, tax year 2025: parameters (every number cited; texts saved under `~/cmp20/baltic/fi/refs/`)

Unit of account: **cents** (the assessment computes taxes in euros and cents; Kela's and the OECD's published
figures are in cents). Rates in basis points (`TaxKernel.BP = 10000`).

Sources (Finlex consolidated texts, versions dated by their amending acts; fetched 2026-11-19):
* TVL = tuloverolaki 1535/1992, `refs/tvl_current.txt` (all versions; the 2025 text is the one amended by 702/2024
  "tuli voimaan 1.1.2025" and not yet by 1141/2025 "tuli voimaan 1.1.2026").
* Asteikkolaki = Laki vuoden 2025 tuloveroasteikosta 701/2024, `refs/asteikko_2025_701_2024.txt`.
* Yleisradioverolaki 484/2012 as amended by 920/2024 ("tuli voimaan 1.1.2025"), `refs/yleverolaki_484_2012.txt`.
* Sairausvakuutuslaki 1224/2004 18 luku, `refs/sairausvakuutuslaki_1224_2004.txt`; the 2025 rates from Verohallinto,
  "Sosiaalivakuutusmaksut" (table 2025), `refs/vero_sosiaalivakuutusmaksut.txt`, and Eläketurvakeskus,
  "Lakisääteiset sosiaalivakuutusmaksut Suomessa 2025", `refs/etk_2025.txt`.
* Lapsilisälaki 796/1992 7 § (1299/2023), `refs/lapsilisalaki_796_1992.txt`.
* Kela, "Paljonko voit saada eläkettä ja miten sitä verotetaan?" 2025 table, `refs/kela_elaketulo_verotaulukko.txt`.
* Municipal rate: Veronmaksajat, Verotietoa 98 (Kuntaverovertailu 2025) taulukko 9 "Helsinki 5,30"
  (source Kuntaliitto / Verohallinto), `refs/kuntaveroselvitys_2025_pdf.txt:1863`; weighted average 7,54 %:
  Kuntaliitto, "Kuntien veroprosentit 2025" ("Keskimääräinen tuloveroprosentti 7,54"), `refs/kuntaliitto_2025.txt:122`.
-/

namespace FiTax
open TaxKernel

/-- euros → cents -/
def eur (x : Int) : Int := 100 * x

/-! ## State income tax on earned income -/

/-- Asteikkolaki 701/2024 1 §: "Vuodelta 2025 toimitettavassa verotuksessa ... valtiolle ansiotulosta suoritettava
tulovero progressiivisen tuloveroasteikon mukaan": 0 → 12,64 %; 21 200 → 19 %; 31 500 → 30,25 %; 52 100 → 34 %;
88 200 → 41,75 %; 150 000 → 44,25 %. (Thresholds in cents.) -/
def stateSchedule : Schedule :=
  Schedule.ofList [(0, 1264), (eur 21200, 1900), (eur 31500, 3025), (eur 52100, 3400), (eur 88200, 4175),
    (eur 150000, 4425)]

/-- Asteikkolaki 701/2024 1 §, the column "Vero alarajan kohdalla, euroa": 2 679,68 / 4 636,68 / 10 868,18 /
23 142,18 / 48 943,68 (cents), as published. `Theorems.state_table_eq_formula` proves the column equals the rates. -/
def stateTable : List (Int × Int) :=
  [(0, 0), (eur 21200, 267968), (eur 31500, 463668), (eur 52100, 1086818), (eur 88200, 2314218),
    (eur 150000, 4894368)]

/-- TVL 124 § 4 mom (version 1510/2016, in force for 2025; 1141/2025 raised the threshold only from 2026):
"eläketulon lisäveroa 5,85 prosenttia siltä osin kuin eläketulo vähennettynä eläketulovähennyksen määrällä ylittää
47 000 euroa". -/
def pensionSurtaxRate : Int := 585
def pensionSurtaxThreshold : Int := eur 47000

/-! ## Capital income -/

/-- TVL 124 § 2 mom (785/2012): "Pääomatulosta suoritetaan tuloveroa 30 prosenttia ... Siltä osin kuin ...
verotettavan pääomatulon määrä ylittää 30 000 euroa, ... 34 prosenttia". -/
def capitalSchedule : Schedule := Schedule.ofList [(0, 3000), (eur 30000, 3400)]

/-- TVL 33 a § 1 mom: "Julkisesti noteeratusta yhtiöstä saadusta osingosta 85 prosenttia on pääomatuloa". -/
def listedDividendTaxable : Int := 8500
/-- TVL 33 b § 1 mom: unlisted dividends: "25 prosenttia on veronalaista pääomatuloa ... siihen määrään saakka, joka
vastaa ... osakkeen verovuoden matemaattiselle arvolle laskettua kahdeksan prosentin vuotuista tuottoa. Siltä osin
kuin ... osinkojen määrä ylittää 150 000 euroa, osingoista 85 prosenttia on pääomatuloa". -/
def unlistedReturnRate : Int := 800
def unlistedCapitalPart : Int := 2500
def unlistedLimit : Int := eur 150000
def unlistedCapitalPartAbove : Int := 8500
/-- TVL 33 b § 2 mom: "vuotuisen tuoton ylittävältä osalta osingosta 75 prosenttia on ansiotuloa". -/
def unlistedEarnedPart : Int := 7500

/-- TVL 131 § 1 mom (728/2004): "Alijäämähyvitys on pääomatulon tuloveroprosentin mukainen osuus ... alijäämästä,
kuitenkin enintään 1 400 euroa. ... korotettava 400 eurolla, jos ... alaikäinen lapsi, ja 800 eurolla, jos ...
kaksi tai useampia." (The first-home 2-point increase, 3-5 mom, was repealed by 702/2024 from 2025.) -/
def deficitRate : Int := 3000
def deficitMax : Int := eur 1400
def deficitChild1 : Int := eur 400
def deficitChild2 : Int := eur 800

/-! ## Deductions from net earned income (TVL 95-106 §; "valtion- ja kunnallisverotuksessa") -/

/-- TVL 95 § 1 mom 1 k (1510/2016): "tulonhankkimisvähennyksenä 750 euroa, kuitenkin enintään palkkatulon määrän". -/
def expenseDeduction : Int := eur 750

/-- TVL 106 § (702/2024, for 2025): "puhdas ansiotulo ... ei ole 4 115 euron määrää suurempi, siitä on vähennettävä
tämän tulon määrä ... ylittää täyden perusvähennyksen määrän, vähennystä pienennetään 18 prosentilla". -/
def basicTaper : Taper := { full := eur 4115, start := eur 4115, num := 18, den := 100 }

/-- Kela 2025 table (`refs/kela_elaketulo_verotaulukko.txt`, "Kokonaiseläkkeen ja nettoeläkkeen määrät 2025",
yksin asuva: työeläke "-", kansaneläke "783,41"): the full national pension of a single person, €/month. -/
def nationalPensionMonthly : Int := 78341

/-- TVL 100 § 2 mom: "täyden kansaneläkkeen määrä kerrotaan luvulla 1,173 ja tulo pyöristetään seuraavaan täyteen
kymmenen euron määrään": 783,41 × 12 × 1,173 = 11 027,28 → 11 030 € (cents, rounded up to 1 000 cents). -/
def pensionDeductionFull : Int := toMultiple .up 1000 (divR .up (nationalPensionMonthly * 12 * 1173) 1000)

/-- TVL 100 § 2 mom (702/2024): "eläketulovähennystä pienennetään 51 prosentilla ylimenevän osan määrästä. Siltä osin
kuin ... puhdas ansiotulo ylittää 22 500 euroa, vähennyksen määrä kuitenkin pienenee 19,6 prosentilla" — the reduction
as a schedule of net earned income (marginal 51 % from the full amount to 22 500, 19,6 % above). -/
def pensionReduction : Schedule :=
  Schedule.ofList [(0, 0), (pensionDeductionFull, 5100), (eur 22500, 1960)]

/-! ## Work income credit (työtulovähennys), TVL 125 § -/

/-- TVL 125 § 2 mom (702/2024, for 2025): "Vähennys on 18 prosenttia ... Vähennyksen enimmäismäärä on kuitenkin
3 225 euroa." -/
def workCreditRate : Int := 1800
def workCreditMax : Int := eur 3225
/-- TVL 125 § 2 mom: "puhtaan ansiotulon ylittäessä 24 250 euroa vähennyksen määrä pienenee 2,22 prosentilla ...
Siltä osin kuin ... ylittää 42 550 euroa, vähennyksen määrä kuitenkin pienenee 3,44 prosentilla" — the withdrawal
as a schedule of net earned income. -/
def workCreditTaper : Schedule := Schedule.ofList [(0, 0), (eur 24250, 222), (eur 42550, 344)]
/-- TVL 125 § 3 mom (1194/2023): "korotetaan 1 200 eurolla, jos verovelvollinen on täyttänyt 65 vuotta ennen
verovuoden alkua". -/
def workCreditAge65 : Int := eur 1200
/-- TVL 125 § 4 mom (added by 702/2024 for 2025): "korotetaan 50 eurolla jokaisesta alaikäisestä lapsesta ...
korotus myönnetään kaksinkertaisena niiden lasten osalta, joiden ainoa huoltaja hän on". -/
def workCreditChild : Int := eur 50

/-! ## Yleisradiovero -/

/-- Yleisradioverolaki 2 § 1 mom (920/2024, for 2025): "2,5 prosenttia ... puhtaan ansiotulon ja puhtaan pääomatulon
yhteismäärän ... 15 150 euroa ylittävästä osasta. Yleisradioveroa ei kuitenkaan ole suoritettava 160 euroa
enempää." -/
def yleRate : Int := 250
def yleThreshold : Int := eur 15150
def yleMax : Int := eur 160

/-! ## Municipal and church tax -/

/-- Helsinki 2025: "Helsinki 5,30" (Verotietoa 98, taulukko 9). TVL 130 § 1 mom: tax "kuntalain ... mukaan
vahvistetun tuloveroprosentin mukaan". -/
def helsinkiRate : Int := 530
/-- Weighted average municipal rate 2025, 7,54 % (Kuntaliitto; used by the OECD and Veronmaksajat). -/
def averageMunicipalRate : Int := 754
/-- TVL 130 § 2 mom: "Jos verovelvollisen tulo jää alle 10 euron, kunnallisveroa ei määrätä." -/
def municipalMinIncome : Int := eur 10

/-! ## Employee contributions 2025 -/

/-- Verohallinto, Sosiaalivakuutusmaksut, 2025 column: "Työntekijän eläkevakuutusmaksu: 17–52-vuotiaat sekä 63 vuotta
täyttäneet 7,15 %", "53–62-vuotiaat 8,65 %" (ETK 2025: "alle 53-vuotiailla ja yli 62-vuotiailla 7,15 prosenttia
palkasta ja 53–62-vuotiailla 8,65 prosenttia"). -/
def tyelRate : Int := 715
def tyelRate53 : Int := 865
/-- Verohallinto 2025: "Työntekijän osuus 0,59 %"; "Työttömyysvakuutusmaksua maksetaan, jos työntekijä on 18–64-vuotias". -/
def unemploymentRate : Int := 59
/-- Verohallinto 2025: "Päivärahamaksu 0,84 %; 0,00 %, jos tulot ovat alle 16 862 euroa" (sairausvakuutuslaki 18:15
3 mom: "Päivärahamaksua ei peritä, jos vuotuisen palkka- ja yrittäjätulon yhteismäärä alittaa" the indexed limit). -/
def dailyAllowanceRate : Int := 84
def dailyAllowanceLimit : Int := eur 16862
/-- Verohallinto 2025: "Sairaanhoitomaksu palkka- ja yrittäjätuloista 1,06 %"; sairausvakuutuslaki 18:20 2 mom: "peritään
kunnallisverotuksessa verotettavasta ansiotulosta"; 3 mom (693/2024): from other earned income "sairaanhoitomaksua
0,39 prosenttia" in addition, on the excess of the medical base over the daily-allowance base (4 mom) — 1,45 % on
pensions ("Sairaanhoitomaksu eläke- ja etuustuloista 1,45 %"). -/
def medicalRate : Int := 106
def medicalExtraRate : Int := 39

/-! ## Child benefit (lapsilisä), Lapsilisälaki 7 § (1299/2023) -/

/-- 7 § 1-2 mom: "94,88 euroa ... toisesta lapsesta 104,84 euroa, kolmannesta lapsesta 133,79 euroa, neljännestä
lapsesta 173,24 euroa ja jokaisesta seuraavasta lapsesta 192,69 euroa kalenterikuukaudessa" (cents/month). -/
def childBenefitBase (i : Nat) : Int :=
  match i with
  | 0 => 9488
  | 1 => 10484
  | 2 => 13379
  | 3 => 17324
  | _ => 19269
/-- 7 § 5 mom: under 3 "120,88 ... 130,84 ... 159,79 ... 199,24" = base + 26,00 €/month (from 1.4.2024). -/
def childBenefitUnder3 : Int := 2600
/-- 7 § 3 mom: "Yksinhuoltajan lapsesta lapsilisä maksetaan korotettuna 73,30 eurolla kalenterikuukaudessa." -/
def childBenefitSingle : Int := 7330
/-- Lapsilisälaki 1 §: paid for a child "alle 17-vuotiaasta" (until the month the child turns 17). -/
def childBenefitAgeLimit : Nat := 17

end FiTax
