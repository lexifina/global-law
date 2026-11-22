import SkTax.Social

/-!
# Daň z príjmov fyzickej osoby (ZDP 595/2003, 2025), in cents

1. Čiastkové základy dane: § 5 ods. 8 (wages − employee contributions), § 6 ods. 1, 2 (business: receipts − expenses,
   actual or 60 % up to 20 000 € under § 6 ods. 10, then − contributions paid), § 6 ods. 3 (rent) and § 8 (other income,
   e.g. gains on securities), after the § 9 ods. 1 písm. g), i) exemption of 500 € in total.
2. § 11: nezdaniteľné časti (taxpayer, spouse, DDS) reduce only the § 5 and § 6 ods. 1, 2 bases, first the § 5 base
   (§ 11 ods. 12).
3. § 4 ods. 1: TWO tax bases: (a) § 5 base after NČZD + § 6 ods. 3, 4 + § 8; (b) § 6 ods. 1, 2 base after NČZD.
4. § 15 písm. a): (a) at 19 % / 25 % above 176,8 × ŽM; (b) at 15 % if business receipts ≤ 100 000 €, otherwise
   19 % / 25 % with its OWN 176,8 × ŽM threshold (bod 3a/3b). Tax rounded by § 47.
5. § 33: daňový bonus (refundable), § 32a: zamestnanecká prémia.
-/

namespace SkTax
open TaxKernel

/-- § 15 písm. a) bod 1 (and bod 3): 19 % up to 176,8 × ŽM = 48 441,43 €, 25 % above (kernel `Schedule`, cents × bp). -/
def sched : Schedule := Schedule.ofList [(0, rate19), (4844143, rate25)]

theorem sched_threshold : (4844143 : Int) = th1768 := by decide

/-- Tax on a base (cents), § 47 halves up. -/
def taxSched (b : Int) : Int := rh (sched.ticks (pos b)) 10000

/-- Tax on the § 4 ods. 1 písm. b) base: 15 % when the § 6 ods. 1, 2 receipts are ≤ 100 000 €, else § 15 písm. a) bod 3. -/
def taxBiz (b receipts : Int) : Int := if receipts ≤ smallBizLimit then pctH (pos b) rate15 else taxSched b

/-! ## § 11 nezdaniteľné časti -/

/-- § 11 ods. 2: NČZD na daňovníka for the base `zd` (sum of the § 5 and § 6 ods. 1, 2 bases): 21 × ŽM up to
92,8 × ŽM, then 44,2 × ŽM − ¼ zd (each step rounded by § 47), never below 0. -/
def nczTaxpayer (zd : Int) : Int := if zd ≤ ncz928 then ncz21 else pos (ncz442 - rh zd 4)

/-- § 11 ods. 6: a pensioner's NČZD is reduced by the pension (zero when the pension exceeds it). -/
def nczWithPension (zd pension : Int) : Int := if 0 < pension then pos (nczTaxpayer zd - pension) else nczTaxpayer zd

/-- § 11 ods. 3: NČZD na manželku (manžela), claimant's base `zd`, spouse's own income `own` (§ 11 ods. 4 písm. b):
income less compulsory contributions). -/
def nczSpouse (zd own : Int) : Int :=
  if zd ≤ th1768 then (if own ≤ 0 then sp192 else pos (sp192 - own))
  else pos (pos (sp634 - rh zd 4) - own)

/-! ## Tax year `y` versions (2022-2024: the same § 11 / § 15 text with that year's ŽM, `Params.zmFor`) -/

def schedY (y : Nat) : Schedule := Schedule.ofList [(0, rate19), (zmTimesY y 1768, rate25)]
def taxSchedY (y : Nat) (b : Int) : Int := rh ((schedY y).ticks (pos b)) 10000
def taxBizY (y : Nat) (b receipts : Int) : Int :=
  if receipts ≤ smallBizLimit then pctH (pos b) rate15 else taxSchedY y b
def nczTaxpayerY (y : Nat) (zd : Int) : Int :=
  if zd ≤ zmTimesY y 928 then zmTimesY y 210 else pos (zmTimesY y 442 - rh zd 4)
def nczWithPensionY (y : Nat) (zd pension : Int) : Int :=
  if 0 < pension then pos (nczTaxpayerY y zd - pension) else nczTaxpayerY y zd
def nczSpouseY (y : Nat) (zd own : Int) : Int :=
  if zd ≤ zmTimesY y 1768 then (if own ≤ 0 then zmTimesY y 192 else pos (zmTimesY y 192 - own))
  else pos (pos (zmTimesY y 634 - rh zd 4) - own)

theorem schedY_2025 : schedY 2025 = sched := by decide
theorem taxSchedY_2025 (b : Int) : taxSchedY 2025 b = taxSched b := by
  simp [taxSchedY, taxSched, schedY_2025]
theorem nczTaxpayerY_2025 (zd : Int) : nczTaxpayerY 2025 zd = nczTaxpayer zd := by
  unfold nczTaxpayerY nczTaxpayer ncz928 ncz21 ncz442; simp only [zmTimesY_2025] <;> rfl
theorem nczSpouseY_2025 (zd own : Int) : nczSpouseY 2025 zd own = nczSpouse zd own := by
  unfold nczSpouseY nczSpouse th1768 sp192 sp634; simp only [zmTimesY_2025] <;> rfl

/-! ## § 33 daňový bonus -/

/-- A child for § 33 / ZPD: age at the end of 2025; `birthMonth` (1–12) when the birthday's month matters (0: age
treated as constant all year); `fromMonth` the first month the child is in the household (birth: § 33 ods. 5). -/
structure Kid where
  age : Int := 0
  birthMonth : Int := 0
  fromMonth : Int := 1
  student : Bool := false
  /-- the child first starts the first grade of základná škola during the year (ZPD § 8 ods. 1 písm. b)) -/
  schoolEntry : Bool := false
  deriving Repr, Inhabited

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

/-- § 33 ods. 1: the month's bonus for a child; "poslednýkrát za kalendárny mesiac, v ktorom dieťa dovŕši 15 (18) rokov":
at the start of month `m` the child is `age − 1` if the birthday falls in month `m` or later. -/
def Kid.monthly (k : Kid) (m : Int) : Int :=
  if m < k.fromMonth then 0 else
    let a := if m ≤ k.birthMonth then k.age - 1 else k.age
    if a < 15 then bonusUnder15 else if a < 18 then bonus15to18 else 0

def Kid.entitlement (k : Kid) : Int := sumInts (months.map k.monthly)
def Kid.nMonths (k : Kid) : Int := sumInts (months.map fun m => if 0 < k.monthly m then 1 else 0)

/-- § 33 ods. 6 and 10: the cap for month `m`: the percentage for the number of children claimed that month, of 1/12
of the base, to the cent (Finančná správa 790897, otázka 4: "3250*0,29/12*10" = 785,40). -/
def capMonth (kids : List Kid) (base m : Int) : Int :=
  let n := sumInts (kids.map fun k => if 0 < k.monthly m then 1 else 0)
  rh (pos base * bonusPct n) 120000

/-- § 33 ods. 1, 6, 10: the bonus before the ods. 11 reduction. -/
def cappedBonus (kids : List Kid) (base : Int) : Int :=
  sumInts (months.map fun m => min (sumInts (kids.map (·.monthly m))) (capMonth kids base m))

/-- § 33 ods. 11: "nárok na daňový bonus na každé jedno vyživované dieťa sa znižuje o 1/10 rozdielu" between the base
and 25 740 €; for a child claimed only part of the year, by that part (Finančná správa 790897, otázka 6: "426/12*2"). -/
def Kid.reduction (k : Kid) (base : Int) : Int := rh (pos (base - bonusTaperStart) * k.nMonths) 120

def taperedBonus (kids : List Kid) (base : Int) : Int :=
  sumInts (kids.map fun k => pos (k.entitlement - k.reduction base))

/-- The annual bonus with the cap computed on `capBase` and the reduction on `taperBase`. -/
def bonus (kids : List Kid) (capBase taperBase : Int) : Int :=
  min (cappedBonus kids capBase) (taperedBonus kids taperBase)

def fullEntitlement (kids : List Kid) : Int := sumInts (kids.map (·.entitlement))

/-- § 33 ods. 8: a claimant whose base does not carry the whole bonus may add the other parent's base "na účely
výpočtu výšky nároku na daňový bonus podľa odsekov 1 a 6". `pooledTaper`: the Finančná správa reading that the ods. 11
reduction is then also computed on the increased base: the text in force from 15. 3. 2025 ("alebo navýšený základ dane
(čiastkový základ dane) podľa odseku 8"), applied to the whole 2025 return by § 52zzzd, and Finančná správa (podpora
790897); `false`: the text of 1. 1. 2025 (ods. 8 named only ods. 1 and 6). The pooling is optional ("môže"), so the better result is taken. -/
def claimBonus (kids : List Kid) (own other : Int) (pooledTaper : Bool := true) : Int :=
  let plain := bonus kids own own
  if cappedBonus kids own < fullEntitlement kids then
    max plain (bonus kids (own + pos other) (if pooledTaper then own + pos other else own))
  else plain

/-- Withholding (ZDP § 35 ods. 5 with § 33 ods. 11 per month, Finančná správa "Zmeny platné od 1.1.2025" bod 4): the
month's bonus on the month's base `b`: each child's amount less 1/10 of the excess over 2 145 €, capped at the
percentage of the month's base. -/
def monthBonus (kids : List Kid) (m b : Int) : Int :=
  let red := rh (pos (b - bonusTaperStartMonthly)) 10
  let n := sumInts (kids.map fun k => if 0 < k.monthly m then 1 else 0)
  min (sumInts (kids.map fun k => pos (k.monthly m - red))) (pctH (pos b) (bonusPct n))

/-! ## The bonus in 2022-2024 -/

/-- Age at the start of month `m` (the birthday month still counts at the lower age: "poslednýkrát za kalendárny
mesiac, v ktorom dieťa dovŕši"). -/
def Kid.ageAt (k : Kid) (m : Int) : Int := if m ≤ k.birthMonth then k.age - 1 else k.age

/-- 2023-2024 (§ 52zzp ods. 4): 140 € under 18, 50 € for a nezaopatrené dieťa of 18 or more (`student`, to 25). -/
def Kid.monthly2324 (k : Kid) (m : Int) : Int :=
  if m < k.fromMonth then 0 else
    let a := k.ageAt m
    if a < 18 then bonus2324Under18 else if k.student ∧ a < 25 then bonus2324Adult else 0

/-- 2022 under § 33 ods. 1 (version 1. 1. 2022) with letter a) amount `amt` (`Params.bonus22a`: 47,14 / 43,60 /
23,57 € for the whole of 2022 under § 52zd ods. 7; `bonus22aH2` = `bonus22a`): under 6, 6 to 15, an older nezaopatrené
dieťa (under 18 here, or a student to 25). -/
def Kid.monthly22old (amt : Int) (k : Kid) (m : Int) : Int :=
  if m < k.fromMonth then 0 else
    let a := k.ageAt m
    if a < 6 then bonus22b amt else if a < 15 then bonus22c amt
    else if a < 18 ∨ (k.student ∧ a < 25) then amt else 0

/-- July-December 2022 (§ 52zzn ods. 3): 70 € under 15, 40 € for an older nezaopatrené dieťa. -/
def Kid.monthly22new (k : Kid) (m : Int) : Int :=
  if m < k.fromMonth then 0 else
    let a := k.ageAt m
    if a < 15 then bonus22H2Under15 else if a < 18 ∨ (k.student ∧ a < 25) then bonus22H2Over15 else 0

/-- Months `ms`, monthly amounts `amt`, capped each month at `pctF n` of 1/12 of `base` (§ 33 ods. 6 and 10 of
2023-2024; § 52zzn ods. 8 of 2022: the percentage "z polovice základu dane" for the six months July-December, i.e.
1/12 of the base per month). -/
def cappedWith (ms : List Int) (amt : Kid → Int → Int) (kids : List Kid) (base : Int) : Int :=
  sumInts (ms.map fun m =>
    let n := sumInts (kids.map fun k => if 0 < amt k m then 1 else 0)
    min (sumInts (kids.map fun k => amt k m)) (rh (pos base * bonusPct2224 n) 120000))

def uncappedWith (ms : List Int) (amt : Kid → Int → Int) (kids : List Kid) : Int :=
  sumInts (ms.map fun m => sumInts (kids.map fun k => amt k m))

/-- 2023-2024: § 52zzp ods. 4 amounts, § 33 ods. 6 cap, § 33 ods. 8 pooling of the other parent's base for the cap
(versions 1. 1. 2023 and 1. 1. 2024; no ods. 11 withdrawal in those years). -/
def claimBonus2324 (kids : List Kid) (own other : Int) : Int :=
  let plain := cappedWith months Kid.monthly2324 kids own
  if plain < uncappedWith months Kid.monthly2324 kids then
    max plain (cappedWith months Kid.monthly2324 kids (own + pos other))
  else plain

def h1 : List Int := [1, 2, 3, 4, 5, 6]
def h2 : List Int := [7, 8, 9, 10, 11, 12]

/-- 2022: January-June § 33 (version 1. 1. 2022), uncapped, only for a claimant with § 5 income (or § 6 ods. 1, 2
income) of at least 6 × the minimum wage; July-December § 52zzn ods. 3 and 8 (capped, no income test), unless the
§ 33 of 30. 6. 2022 gives more for those months (§ 52zzn ods. 1). No pooling of bases in 2022. -/
def claimBonus2022 (kids : List Kid) (own : Int) (oldTest : Bool) : Int :=
  let oldH1 := if oldTest then uncappedWith h1 (Kid.monthly22old bonus22a) kids else 0
  let oldH2 := if oldTest then uncappedWith h2 (Kid.monthly22old bonus22aH2) kids else 0
  oldH1 + max oldH2 (cappedWith h2 Kid.monthly22new kids own)

/-! ## § 32a zamestnanecká prémia -/

/-- § 32a ods. 3 for an employee with only § 5 ods. 1 písm. a) income `w` (cents) and minimum wage `mw` (monthly):
19 % of (NČZD 21 × ŽM − the § 5 ods. 8 base of max(w, 12 × mw)), when positive; nothing below 6 × mw. -/
def premia (mw w : Int) : Int :=
  if w < 6 * mw then 0 else
    let base := zd5Of (max w (12 * mw))
    if base < ncz21 then pctH (ncz21 - base) rate19 else 0

end SkTax
