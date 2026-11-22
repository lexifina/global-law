import TaxKernel.Global2
import R5Common

/-!
# Türkiye 2025: KDV (5111); ÖTV (5121): list (I) motor fuels, list (III) (A) drinks, (III) (B) cigarettes

Sources:
* Katma Değer Vergisi Kanunu No. 3065 (mevzuat.gov.tr PDF, registry copy `registry/afm_data/fetch/TR/tr_3065.pdf`)
  art. 28: "Katma değer vergisi oranı, vergiye tabi her bir işlem için % 10'dur. Cumhurbaşkanı bu oranı, dört katına
  kadar artırmaya, % 1'e kadar indirmeye … farklı vergi oranları tespit etmeye … yetkilidir": the rates are set by
  decision.
* Cumhurbaşkanı Kararı No. 7346 (Resmî Gazete 7 July 2023, No. 32241, `law/kdv_karar7346_rg20230707-11.pdf`, OCR in
  `law/kdv_karar7346_ocr.txt`) art. 1: in BKK 2007/13033 art. 1(1)(a) "%18" becomes "%20" (general rate) and (c) "%8"
  becomes "%10"; in force on the third day after publication (art. 3); no later change of the general rate before 2026
  was found in the 2025 Resmî Gazete indexes checked (none read): **grade B**.
* The goods of lists (I) (1 %) and (II) (10 %) of BKK 2007/13033 are not read (the consolidated decision was not
  reachable: mevzuat.gov.tr answered empty, no archived copy): every good is taxed at 20 % and the entity is flagged.
* ÖTV (Özel Tüketim Vergisi Kanunu No. 4760), list (III) (A), non-alcoholic drinks: mevzuat.gov.tr text archived
  2023-07-12 (`law/mevzuat_4760_wayback20230712.txt`), "Uygulanacak Vergi Oranı (%)": 20.09 fruit juices with added
  sugar 10; 22.02 sweetened/flavoured waters and other non-alcoholic drinks 10; 2202.10.00.00.11 sade gazozlar 10,
  .12 meyvalı gazozlar 10, .13 kolalı gazozlar 35; 2202.91 alkolsüz biralar 10; no minimum specific amount. Footnote
  81: set by CK 540 (RG 31/12/2018, 4. Mük.) from 2019-01-01. GİB's list of ÖTV Presidential decisions
  (`law/gib_cbk_4760_list_20261121.json`) has no list (III) (A) decision on these goods between CK 540 and CK 10799
  (RG 31/12/2025, 5. Mük., in force that day, re-setting the same 10 / 35 %); CK 9309 (RG 25/12/2024) touched only
  spirits and nargile tobacco. Base (art. 11): the sale price before ÖTV; KDV is charged on the ÖTV-inclusive price
  (KDV Law art. 21): `beforeTax` with `vatBp` 2000 (the KDV rate this model applies to every good). Canonical
  `softDrinks` = sade/meyvalı gazoz (10 %); the TR-specific sub `cola` = kolalı gazoz (35 %); `sweetenedDrinks` and
  `energyDrinks` = 22.02 other drinks (10 %).
* ÖTV list (III) (B), cigarettes (2402.20, and 2402.90 substitute cigarettes): 4760 art. 11(2)(b) (asgari maktu
  per stick, maktu per 20-stick pack, pro rata for other packs), 11(4) (base: retail price to the final consumer,
  tax-inclusive: `.retail`), 11(5) (maktu plus the ad valorem tax, the latter not less than the asgari amount), so
  `ÖTV = maktu/20 · n + max(rate · price, asgari · n)` = kernel `max(specific + adValorem, minimum)` with
  `minimum = asgari + maktu/20` per stick. Art. 12(3): the asgari and maktu amounts last set are deemed revalued in
  January and July by TÜİK's six-month PPI change, from the day it is announced, unless a decision suspends it.
  Chain for 2025 (decisions in `law/`, scans read with tesseract, `law/*_ocr.txt`):
  - CK 8001 (RG 28/12/2023, from 1/1/2024): 57 %, asgari 1,4249, maktu 4,8058; art. 2 suspends 12(3) for Jan-Jun 2024.
  - 3/7/2024 revaluation +19,49 % (GİB e-beyanname notice of 02.08.2024, `law/gib_duyuru_otv3b_2024_2025.json`;
    the same 19,49 appears as June 2024's change from December in TÜİK's June 2025 table): asgari 1,7026.
  - CK 8958 (RG 14/9/2024, in force that day): 53,5 %, maktu 7,8000; asgari kept (GİB explanatory note).
  - 3/1/2025 revaluation +7,56 % (GİB e-beyanname notice of 03.02.2025, "03/01/2025 tarihinden itibaren ... %7,56"):
    asgari 1,8313, maktu 8,3897. CK 9309 (RG 25/12/2024) changed only spirits and nargile tobacco, no suspension.
  - CK 9583 (RG 15/3/2025, in force that day): 50 %, maktu 10,5000; asgari kept (GİB note and notice of 01.04.2025).
  - 3/7/2025 revaluation +15,71 %: TÜİK Yİ-ÜFE bulletin June 2025 (No. 53867, released 2025-07-03 10:00; Wayback
    2025-08-05, `law/tuik_yiufe_haziran2025_wayback20250805.html`): "Aralık ayına göre %15,71"; no decision suspends
    July 2025 (GİB list of ÖTV decisions): asgari 2,1190, maktu 12,1496.
  - CK 10520 (RG 24/10/2025, in force that day): 45 %, asgari 1,9750 (GİB note: lowered, consistent with 2,1190
    before), maktu 16,0000.
  - CK 10799 (RG 31/12/2025, 5. Mük., in force that day): 45 %, asgari 1,9750, maktu 17,2720.
  The revalued amounts are computed here (4 decimals, half up): GİB's own rounded figures were not found, so the
  cigarette rule is **grade B**. Other tobacco (24.03, per gram; cigars) is not computed.
* List (I) fuels: computed since pass 3n (section "List (I): motor fuels" below). List (III) (A) alcohol: computed since
  pass 3l (section "List (III) (A): alcoholic beverages" below).
-/

namespace TrGlobal
open TaxKernel TaxKernel.Global R5Common

def kdvGeneral : Int := 2000

def kdv : Vat := { name := "Katma Değer Vergisi (KDV)", standard := kdvGeneral }

def otvOf (sub : String) (bp : Int) (what : String) : ExciseRule :=
  { good := .nonAlcoholic, sub, name := "Özel Tüketim Vergisi (III) sayılı liste", adValoremBp := bp,
    valueBase := .beforeTax, vatBp := kdvGeneral,
    statute := s!"ÖTV Kanunu (III) sayılı liste (A) cetveli, CK 540 (2019): {what}" }

def otv : List ExciseRule :=
  [otvOf "softDrinks" 1000 "2202.10.00.00.11-12 sade/meyvalı gazozlar 10 %", otvOf "cola" 3500 "2202.10.00.00.13 kolalı gazozlar 35 %",
   otvOf "sweetenedDrinks" 1000 "22.02 / 20.09 10 %", otvOf "energyDrinks" 1000 "22.02 10 %"]

/-- Four-decimal half-up revaluation (art. 12(3)): `a` and the result in 1/10000 TL, `pctE2` the PPI change in 1/100 %. -/
def reval (a pctE2 : Int) : Int := (a * (10000 + pctE2) + 5000) / 10000

/-- List (III) (B) cigarettes in a window: `rateBp` ad valorem on the retail price, asgari per stick and maktu per
20-stick pack in 1/10000 TL. -/
def sigara (fromD toD : String) (rateBp asgariE4 maktuE4 : Int) (what : String) : ExciseRule :=
  { good := .cigarettes, name := "Özel Tüketim Vergisi (III) sayılı liste (B) cetveli",
    perUnitNum := maktuE4, perUnitDen := 200000, adValoremBp := rateBp, valueBase := .retail,
    minNum := asgariE4 * 20 + maktuE4, minDen := 200000, validFrom := fromD, validTo := toD,
    statute := s!"ÖTV Kanunu art. 11(2)(b), (4), (5), 12(3); 2402.20: {what}" }

def asgari24 : Int := reval 14249 1949   -- 3/7/2024
def asgari25a : Int := reval asgari24 756  -- 3/1/2025
def maktu25a : Int := reval 78000 756
def asgari25b : Int := reval asgari25a 1571 -- 3/7/2025
def maktu25b : Int := reval 105000 1571

#guard asgari24 == 17026
#guard (asgari25a, maktu25a) == (18313, 83897)
#guard (asgari25b, maktu25b) == (21190, 121496)

def tobacco : List ExciseRule :=
  [sigara "" "2025-01-03" 5350 asgari24 78000 "CK 8958 53,5 %, maktu 7,80; asgari 1,4249 (CK 8001) +19,49 % (3/7/2024)",
   sigara "2025-01-03" "2025-03-15" 5350 asgari25a maktu25a "53,5 %; art. 12(3) +7,56 % from 3/1/2025",
   sigara "2025-03-15" "2025-07-03" 5000 asgari25a 105000 "CK 9583 50 %, maktu 10,50 from 15/3/2025",
   sigara "2025-07-03" "2025-10-24" 5000 asgari25b maktu25b "art. 12(3) +15,71 % (TÜİK Yİ-ÜFE June 2025) from 3/7/2025",
   sigara "2025-10-24" "2025-12-31" 4500 19750 160000 "CK 10520 45 %, asgari 1,9750, maktu 16,00 from 24/10/2025",
   sigara "2025-12-31" "" 4500 19750 172720 "CK 10799 45 %, asgari 1,9750, maktu 17,2720 from 31/12/2025"]

/-! ## List (III) (A): alcoholic beverages (pass 3l)

ÖTV Kanunu 4760 art. 11(2)(a) (mevzuat consolidation, Wayback 2023-07-12, `law/mevzuat_4760_wayback20230712.txt`): the
asgari maktu amounts of list (III) (A) are per degree of alcohol in a litre for beer (2203.00), per litre for 22.04,
22.05 (2205.10.90.00.12 excepted) and 2206.00, and per litre of alcohol contained for the other goods. Applied rate and
amounts as set by **CK 5614** (RG 27/5/2022, footnotes 81, 83, 85 of the consolidation): beer 63 % / 4,4096; 22.04 wine
0 % / 21,6821; 2204.10 sparkling 146,4895; 22.05 221,0891; 2205.10.10 (≤ 18 %) 175,5698; 2205.10.90.00.12 (≥ 22 %),
2207.20, 22.08 602,4843; 2206.00 29,5849. CK 5614 suspended art. 12(3) for July-December 2022 except 2206.00 (GİB
notice 27/5/2022). Art. 12(3) PPI changes after that (TÜİK Yİ-ÜFE six-month change, from the announcement day):
3/7/2022 +61,68 % (2206.00 only; June 2024 bulletin table, Haziran 2022 column), 3/1/2023 +22,29 % (computed from the
Dec 2022 bulletin, +97,72 % on Dec 2021, and +61,68 %: 1,9772 / 1,6168), 3/7/2023 +14,82 %, 3/1/2024 +25,61 % (GİB
notice of 3/1/2024; CK 8001 suspended it for cigarettes only), 3/7/2024 +19,49 %, 3/1/2025 +7,56 %, 3/7/2025 +15,71 %.
**CK 9309** (RG 25/12/2024, in force on publication, no suspension) set 1.428,44 TL for 2205.10.90.00.12, 2207.20 and
22.08 (`law/ck9309_ocr.txt`). No other (III) (A) decision appears in GİB's notices from 2022 to 2025 (checked list of
`gibportal/duyuru` type 1). Rounding: 4 decimals half up at each step (as for cigarettes). Grade B (the decisions and
the law read; the 3/1/2023 step computed from TÜİK figures; absence of other decisions from GİB's notice list).
Beer: ÖTV = max(63 % of the price before ÖTV and KDV, asgari): with the price before taxes `b = n − ÖTV` (n net of
KDV) the ad valorem case is `0,63 n / 1,63`, so the duty is the larger of that and the asgari. Goods: `beer`;
`wine` (sub `""` 22.04, `"sparkling"` 2204.10, `"vermouth"` 22.05 by strength, `"fermented"` 2206.00);
`spirits` (22.08, per litre of pure alcohol). -/

/-- the PPI chain from the CK 5614 amount to 3/7/2024 (four steps; suspended July 2022) -/
def chain24 (a : Int) : Int := reval (reval (reval (reval a 2229) 1482) 2561) 1949

/-- `(validFrom, validTo, amount at 3/7/2024 or set by CK 9309 → amount in the window)` -/
def alkWindows : List (String × String × (Int → Int)) :=
  [("", "2025-01-03", id), ("2025-01-03", "2025-07-03", fun a => reval a 756),
   ("2025-07-03", "", fun a => reval (reval a 756) 1571)]

def ickiRule (good : Good) (sub : String) (lo hi : Int) (amtE4 : Int) (pure perDegree : Bool) (fromD toD what : String) :
    ExciseRule :=
  { good, sub, name := "Özel Tüketim Vergisi (III) sayılı liste (A) cetveli", minAbvBp := lo, maxAbvBp := hi,
    perUnitNum := if perDegree then amtE4 * 100 else amtE4, perUnitDen := 10000, onPureAlcohol := pure || perDegree,
    validFrom := fromD, validTo := toD, vatBp := kdvGeneral,
    statute := s!"ÖTV Kanunu art. 11(2)(a), 12(3); (III) (A) {what}; window {fromD}..{toD}" }

/-- wine and spirits rules of one window, most specific first (applied with `firstOnly`) -/
def ickiIn (w : String × String × (Int → Int)) : List ExciseRule :=
  let (f, t, up) := w
  let s9309 := up 14284400
  [ickiRule .wine "sparkling" (-1) 100000 (up (chain24 1464895)) false false f t "2204.10 köpüklü şaraplar (CK 5614 146,4895)",
   ickiRule .wine "vermouth" (-1) 1800 (up (chain24 1755698)) false false f t "2205.10.10 ≤ 18 % (CK 5614 175,5698)",
   ickiRule .wine "vermouth" 2199 100000 s9309 true false f t "2205.10.90.00.12 ≥ 22 %, per litre of alcohol (CK 9309 1.428,44)",
   ickiRule .wine "vermouth" 1800 2199 (up (chain24 2210891)) false false f t "22.05 (CK 5614 221,0891)",
   ickiRule .wine "fermented" (-1) 100000 (up (chain24 (reval 295849 6168))) false false f t "2206.00 (CK 5614 29,5849; +61,68 % 3/7/2022)",
   ickiRule .wine "" (-1) 100000 (up (chain24 216821)) false false f t "22.04 şaraplar (CK 5614 21,6821)",
   ickiRule .spirits "" (-1) 100000 s9309 true false f t "22.08 / 2207.20, per litre of alcohol (CK 9309 1.428,44)"]

/-- beer: asgari per degree and litre, and the 63 % ad valorem rule on the price before ÖTV and KDV -/
def biraAsgari (w : String × String × (Int → Int)) : ExciseRule :=
  let (f, t, up) := w
  ickiRule .beer "" (-1) 100000 (up (chain24 44096)) false true f t "2203.00 biralar, per degree and litre (CK 5614 4,4096; 63 %)"

def biraOran (w : String × String × (Int → Int)) : ExciseRule :=
  let (f, t, _) := w
  { good := .beer, name := "Özel Tüketim Vergisi (III) sayılı liste (A) cetveli", adValoremBp := 6300,
    valueBase := .beforeTax, vatBp := kdvGeneral, validFrom := f, validTo := t }

def biraCharges (g : CanonGlobal) : List Charge :=
  alkWindows.flatMap fun w =>
    let sp := biraAsgari w
    let ad := biraOran w
    (consumptionX g).filterMap fun (s, x) =>
      if sp.appliesTo g.year s x then
        let sx := sp.scaled g.year s x
        some (exciseCharge sp.name sx.1 (max (ad.dutyOn sx.1 sx.2) (sp.dutyOn sx.1 sx.2)) sp.statute)
      else none

def alcoholCharges (g : CanonGlobal) : List Charge :=
  biraCharges g ++ alkWindows.flatMap (fun w => exciseRuleCharges (ickiIn w) g (firstOnly := true))

#guard chain24 44096 == 92932
#guard (alkWindows.map fun (_, _, up) => up (chain24 44096)) == [92932, 99958, 115661]
#guard (alkWindows.map fun (_, _, up) => up 14284400) == [14284400, 15364301, 17778033]
#guard (alkWindows.map fun (_, _, up) => up (chain24 216821)) == [456945, 491490, 568703]
-- 1 litre of 5 % beer on 1/8/2025 at 120 TL: asgari 11,5661 × 5 = 57,83; 63 % case 0,63 × 100 / 1,63 = 38,65: 57
#guard (biraAsgari (alkWindows.getD 2 default)).dutyOn { good := .beer, amount := 120, quantity := 1000, abvBp := 500 } {} == 57
#guard (biraOran (alkWindows.getD 2 default)).dutyOn { good := .beer, amount := 120, quantity := 1000, abvBp := 500 } {} == 38
-- 0,7 l of 40 % spirits on 1/8/2025: 0,28 l × 1.777,8033 = 497,78
#guard ((ickiIn (alkWindows.getD 2 default)).getD 6 default).dutyOn { good := .spirits, amount := 1500, quantity := 700, abvBp := 4000 } {} == 497

/-! ## List (I): motor fuels (pass 3n)

ÖTV Kanunu 4760 art. 12(1): list (I) goods are taxed at the specific amounts set against them (per litre for petrol
and gas oil). **CK 9380** (RG 31/12/2024 No. 32769, in force on publication; GİB copy `law/tr_ck9380.pdf`, scanned,
`law/tr_ck9380_ocr.txt`; GİB explanatory note `law/tr_ck9380not.pdf`) art. 1, (A) cetveli: 2710.12.45 kurşunsuz benzin
95 oktan (also E10, others RON 95-98) **11,9819 TL/l**; 2710.12.49 kurşunsuz benzin 98 oktan **12,5605**; 2710.19.43.00.11
and 2710.20.11.00.11 motorin (≤ 0,001 % S) **11,2327**; art. 2: art. 12(5) not applied for January-June 2025.
Art. 12(5) (text as quoted in GİB's notices of 3/1/2024 and 3/7/2024, `law/tr_gib_duyuru1_otv.json`): the list (I)
amounts last set are deemed revalued in January and July by TÜİK's domestic PPI change over the last six months, from
the day it is announced. July 2025: TÜİK Yİ-ÜFE June 2025 (released 3/7/2025 10:00;
`law/tuik_yiufe_haziran2025_wayback20250805.html`, read in pass 3f): +15,71 % on December; no (I) decision between CK 9380 and CK 10799 in GİB's
list of ÖTV decisions (`law/gib_cbk_4760_list_20261121.json`): amounts from **3/7/2025** = CK 9380 × 1,1571 (4
decimals half up, as for list (III)): 13,8643 / 14,5338 / 12,9974. **CK 10799** (RG 31/12/2025, 5. Mük., in force on
publication, `law/ck10799_ocr.txt`): 95 oktan 14,8277, 98 oktan 15,5437, motorin 13,9006 from **31/12/2025**; its GİB
note (`law/tr_ck10799_abn.pdf`) says these are a 6,95 % rise in place of the PPI update due for July-December 2025,
i.e. on the July 2025 amounts: 14,8277 / 1,0695 = 13,8641, 15,5437 / 1,0695 = 14,5336, 13,9006 / 1,0695 = 12,9973,
within 0,0002 TL of the computed amounts (GİB's own July table not found): **grade B**. KDV is charged on the
ÖTV-inclusive price (the basket KDV line already reads the price paid). Goods: `petrol` (sub `""` = 95 oktan;
TR-specific sub `"98"`), `diesel` (motorin). Not computed: LPG/otogaz and natural gas (no kernel good), heating oil
(kalorifer yakıtı is taxed per kg), other list (I) goods. -/

/-- `(validFrom, validTo, petrol 95, petrol 98, motorin)` in 1/10000 TL per litre -/
def yakitWindows : List (String × String × Int × Int × Int) :=
  [("", "2025-07-03", 119819, 125605, 112327),
   ("2025-07-03", "2025-12-31", reval 119819 1571, reval 125605 1571, reval 112327 1571),
   ("2025-12-31", "", 148277, 155437, 139006)]

def yakitRule (good : Good) (sub : String) (amtE4 : Int) (fromD toD what : String) : ExciseRule :=
  { good, sub, name := "Özel Tüketim Vergisi (I) sayılı liste", perUnitNum := amtE4, perUnitDen := 10000,
    validFrom := fromD, validTo := toD,
    statute := s!"ÖTV Kanunu art. 12(1), (5); (I) sayılı liste (A) cetveli {what}; window {fromD}..{toD}" }

/-- one window, most specific first (applied with `firstOnly`) -/
def yakitIn (w : String × String × Int × Int × Int) : List ExciseRule :=
  let (f, t, b95, b98, mot) := w
  let src := if f == "" then "CK 9380" else if t == "" then "CK 10799" else "CK 9380 × 1,1571 (art. 12(5), 3/7/2025)"
  [yakitRule .petrol "98" b98 f t s!"2710.12.49 kurşunsuz benzin 98 oktan ({src})",
   yakitRule .petrol "" b95 f t s!"2710.12.45 kurşunsuz benzin 95 oktan ({src})",
   yakitRule .diesel "" mot f t s!"2710.19.43.00.11 motorin ({src})"]

def fuelCharges (g : CanonGlobal) : List Charge :=
  yakitWindows.flatMap (fun w => exciseRuleCharges (yakitIn w) g (firstOnly := true))

#guard (reval 119819 1571, reval 125605 1571, reval 112327 1571) == (138643, 145338, 129974)
-- 40 l of 95 octane on 1/8/2025: 40 × 13,8643 = 554,57
#guard ((yakitIn (yakitWindows.getD 1 default)).getD 1 default).dutyOn { good := .petrol, amount := 2400, quantity := 40000 } {} == 554
-- 50 l of motorin on 1/3/2025: 50 × 11,2327 = 561,64
#guard ((yakitIn (yakitWindows.getD 0 default)).getD 2 default).dutyOn { good := .diesel, amount := 2800, quantity := 50000 } {} == 561

def consumption : Family :=
  { name := "5111 KDV, 5121 ÖTV", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [kdv.basketCharge g.consumption "KDV Kanunu art. 28; BKK 2007/13033 art. 1(1)(a) as amended by CK 7346 (20 %)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [kdv.businessCharge g.company "KDV Kanunu art. 1, 28, 29 (deduction); CK 7346 (20 %)"] else [])
      ++ exciseRuleCharges otv g ++ exciseRuleCharges tobacco g ++ alcoholCharges g
      ++ fuelCharges g }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.isEmpty then [] else
    ["KDV: the 1 % and 10 % lists of BKK 2007/13033 were not read; every good is taxed at 20 %"])
  ++ (if g.consumption.any (fun s => s.good == .heatingOil || s.good == .tobaccoOther) then
    ["ÖTV list (I) heating oil (taxed per kg) and (III) (B) tobacco other than cigarettes: not computed"] else [])
  ++ (if g.consumption.any (fun s => (s.good == .petrol || s.good == .diesel) && s.quantity <= 0) then
    ["ÖTV list (I) fuels: line without quantity (ml): the specific amount per litre not applied"] else [])
  ++ (if g.consumption.any (fun s => (s.good == .beer || s.good == .wine || s.good == .spirits) && (s.quantity <= 0 || s.abvBp <= 0)) then
    ["ÖTV (III) (A) alcohol: line without quantity (ml) or strength (abvBp): the asgari maktu needs both"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes && s.quantity <= 0) then
    ["ÖTV cigarettes: line without quantity (sticks): maktu and asgari parts not applied"] else [])
  ++ (if (consumptionX g).any (fun (s, x) => s.good == .nonAlcoholic && x.sub == "") then
    ["ÖTV: nonAlcoholic lines without sub (softDrinks/cola/sweetenedDrinks/energyDrinks): no ÖTV applied"] else [])

#guard kdv.embedded { good := .food, amount := 12000 } == 2000
-- cola 35 % before KDV: 162 paid = (100 + 35) × 1.20
#guard (otv.getD 1 default).dutyOn { good := .nonAlcoholic, amount := 162 } { sub := "cola" } == 35
#guard (otv.getD 0 default).dutyOn { good := .nonAlcoholic, amount := 132 } { sub := "softDrinks" } == 10
-- 20 sticks at 100 TL on 1/8/2025: maktu 12,1496 + max(50 % × 100, 2,1190 × 20 = 42,38) = 62
#guard ((tobacco.getD 3 default).dutyOn { good := .cigarettes, amount := 100, quantity := 20000 } {}) == 62
-- a cheap pack (60 TL) under CK 10520: maktu 16 + max(27, 1,975 × 20 = 39,5) = 55
#guard ((tobacco.getD 4 default).dutyOn { good := .cigarettes, amount := 60, quantity := 20000 } {}) == 55
#guard kdv.net { turnover := 1000, sales := [{ good := .other, net := 1000 }], inputs := [{ good := .other, net := 500 }] } == 100

end TrGlobal
