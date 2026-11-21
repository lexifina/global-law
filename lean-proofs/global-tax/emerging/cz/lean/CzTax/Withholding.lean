import CzTax.Household

/-!
# Monthly withholding (zálohy, § 38h ZDP) against the annual tax (roční zúčtování, § 38ch)

One employer, prohlášení signed (§ 38k odst. 4), the same gross wage `m` every month.

* § 38h odst. 1: "Základ pro výpočet zálohy do 100 Kč se zaokrouhlí na celé koruny nahoru a nad 100 Kč na celé
  stokoruny nahoru" — monthly rounding **up**, where the annual § 16 odst. 2 rounds the base **down**.
* § 38h odst. 2: 15 % up to 3 × average wage a month (139 671 Kč), 23 % above; odst. 3: rounded up to the crown.
* § 38h odst. 4, § 35d odst. 2–4: minus 1/12 of the sleva na poplatníka (2 570 Kč) and 1/12 of the child amounts
  (1 267 / 1 860 / 2 320 Kč); a monthly bonus "alespoň 50 Kč", paid only if the month's wage reaches half the
  minimum wage "zaokrouhlené na celé koruny dolů" (10 400 Kč). The sleva na manžela is not available monthly
  (§ 35d odst. 1 lists only § 35ba odst. 1 písm. a), c) až e)).
-/

namespace CzTax

/-- § 38h odst. 1: the monthly base rounded up (to the crown up to 100 Kč, else to the hundred). -/
def monthBase (m : Int) : Int := if m ≤ 100 then pos m else ceilTo 100 m

/-- § 38h odst. 2–3: the monthly záloha before credits. -/
def zaloha (m : Int) : Int :=
  let b := monthBase m
  cdiv (15 * min b monthlyThreshold23 + 23 * pos (b - monthlyThreshold23)) 100

/-- One month: (záloha after credits, bonus paid). `kids` = yearly § 35c amount claimed. -/
def monthWithholding (m kids : Int) : Int × Int :=
  let z := zaloha m
  let sleva := creditUsed z (slevaPoplatnik / 12)
  let after := z - sleva
  let kidsM := kids / 12
  let cs := creditUsed after kidsM
  let bonusRaw := kidsM - cs
  let bonus := if bonusRaw ≥ monthlyBonusMin && m ≥ monthlyBonusIncomeMin then bonusRaw else 0
  (after - cs, bonus)

/-- Twelve months of the same wage: total withheld minus total monthly bonuses. -/
def yearWithheld (m kids : Int) : Int :=
  let (z, b) := monthWithholding m kids
  12 * (z - b)

/-- The annual tax of the same employee (§ 16, § 35ba, § 35c), no other income or deductions. -/
def annualTax (m kids : Int) : Int := (computeTax { wages := 12 * m, childCredits := kids }).finalTax

/-- Over- (positive) or under-withholding for the year, settled in the roční zúčtování. -/
def settlement (m kids : Int) : Int := yearWithheld m kids - annualTax m kids

end CzTax
