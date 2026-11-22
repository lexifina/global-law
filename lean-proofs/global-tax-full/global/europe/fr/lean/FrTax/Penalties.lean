import FrTax.Basic

/-!
# Penalties and late-payment interest on the income tax (CGI art. 1727 – 1732, 1758 A; LPF art. L. 62)

Written from the articles as in force for the income years 2017 – 2025 (france-law record, files
`codes/code-general-des-impots-cgi/<art>.md`; LPF art. L. 62 from the global-law record). Every function takes
the rights in question (whole euros), the dates and the kind of failure, and returns whole euros. Nothing here
is used by the tax model; the file only adds definitions and theorems.

* **Intérêt de retard, art. 1727.** III: "Le taux de l'intérêt de retard est de 0,20 % par mois" (loi n° 2017-1775,
  art. 55, for interest running from 1 January 2018; made permanent by loi n° 2020-1721, art. 68); 0,40 % before.
  IV, 1: counted "à compter du premier jour du mois suivant celui au cours duquel l'impôt devait être acquitté
  jusqu'au dernier jour du mois du paiement"; for the income tax the start is "le 1er juillet de l'année suivant
  celle au titre de laquelle l'imposition est établie" (cessation cases, art. 201 – 204: "le premier jour du
  quatrième mois suivant celui de l'expiration du délai de déclaration"). IV, 3: with art. 1728 the count stops
  at "le dernier jour du mois de la proposition de rectification ou du mois au cours duquel la déclaration ou
  l'acte a été déposé"; IV, 4: with art. 1729, at the month of the proposition de rectification. IV, 2: it stops
  when the 10 % of art. 1730 applies. II, 4: none "sauf manquement délibéré, lorsque l'insuffisance des chiffres
  déclarés n'excède pas le vingtième de la base d'imposition".
* **Droit à l'erreur.** Art. 1727, V (loi n° 2018-727, ESSOC, art. 5; rectifying returns filed from 11 August 2018):
  "Le montant dû au titre de l'intérêt de retard est réduit de 50 % en cas de dépôt spontané [...] d'une
  déclaration rectificative". LPF art. L. 62: a regularisation during a control costs "un montant égal à 70 % de
  l'intérêt de retard".
* **Late or missing return.** Art. 1728, 1: 10 % (no formal notice, or filed within thirty days of one), 40 %
  (not filed within thirty days of a formal notice), 80 % (occult activity). For the income tax art. 1758 A
  replaces the 10 % of 1728, 1, a (1758 A, III): 10 %, "portée à 20 % en cas de dépôt tardif effectué dans les
  trente jours d'une mise en demeure"; 1758 A also charges 10 % on a good-faith insufficiency not corrected
  spontaneously or within thirty days of a request (1758 A, II, a), and gives way to 1728 b, c, 1729 and 1732 a.
* **Insufficiencies.** Art. 1729: 40 % manquement délibéré; 80 % abus de droit (40 % when the taxpayer neither
  had the main initiative nor was the main beneficiary); 80 % manœuvres frauduleuses. Art. 1732, a: 100 %
  (opposition to a control). Art. 1729 A, 1: several rates on one return are computed "en ajoutant les
  rehaussements aux éléments déclarés en suivant l'ordre décroissant des différents taux applicables"; 1729 A, 2:
  on a late return the 1728 rate applies to all the rights, but a higher 1729 rate takes its place on the rights
  from the reassessments. Art. 1728, 4: late categorical returns, the tax shared "proportionnellement aux revenus
  représentatifs de chaque infraction", unless the rate of the global return is higher.
* **Late payment.** Art. 1730: 10 % of sums in a roll not paid "dans les quarante-cinq jours suivant la date de
  mise en recouvrement du rôle [...] sans que cette majoration puisse être appliquée avant le 15 septembre pour
  les impôts établis au titre de l'année en cours". Art. 1729 G (withholding, from income 2019): 10 %, and when
  the shortfall exceeds 30 %, half the shortfall in per cent.

Rounding: art. 1657, 1, "Il en est de même du montant des majorations": each amount is rounded half up to the
euro (`rnd`). Rates are in hundredths of a per cent (0,20 % = 20) for interest and in per cent for majorations.
-/

namespace FrTax.Penalties

open FrTax

/-! ## Dates -/

structure Date where
  y : Int
  m : Int
  d : Int
  deriving Repr, DecidableEq

/-- Months since year 0 (January of year `y` is `12 y`). -/
def Date.mi (t : Date) : Int := 12 * t.y + (t.m - 1)

/-- Days since 1 March of year 0 (proleptic Gregorian calendar; for years ≥ 0). -/
def Date.days (t : Date) : Int :=
  let y := if t.m ≤ 2 then t.y - 1 else t.y
  let era := y / 400
  let yoe := y - era * 400
  let mp := (t.m + 9) % 12
  let doy := (153 * mp + 2) / 5 + t.d - 1
  era * 146097 + yoe * 365 + yoe / 4 - yoe / 100 + doy

/-- The first month counted for income `n` (art. 1727, IV, 1, second paragraph): July of `n + 1`. -/
def irStart (n : Int) : Date := ⟨n + 1, 7, 1⟩

/-- Cessation cases, art. 201 – 204 (art. 1727, IV, 1, fourth paragraph): the first day of the fourth month after
the month in which the return was due. -/
def cessationStart (deadline : Date) : Date :=
  let k := deadline.mi + 4
  ⟨k / 12, k % 12 + 1, 1⟩

/-! ## Intérêt de retard (art. 1727) -/

/-- The first month at the 0,20 % rate: January 2018. -/
def cut : Int := 12 * 2018

/-- Months counted from the first day of `start`'s month to the last day of `stop`'s month. -/
def months (start stop : Date) : Int := max 0 (stop.mi - start.mi + 1)

/-- Months of the period before 2018 (0,40 %) and from 2018 (0,20 %). -/
def monthsOld (start stop : Date) : Int := max 0 (min stop.mi (cut - 1) - start.mi + 1)
def monthsNew (start stop : Date) : Int := max 0 (stop.mi - max start.mi cut + 1)

/-- The sum of the monthly rates over the period, in hundredths of a per cent. -/
def rateSum (start stop : Date) : Int := 40 * monthsOld start stop + 20 * monthsNew start stop

/-- Reductions of the interest: none; LPF L. 62 (70 % is due); art. 1727, V (halved). -/
inductive Relief
  | none
  | l62
  | spontaneous
  deriving Repr, DecidableEq

def Relief.num : Relief → Int | .none => 1 | .l62 => 7 | .spontaneous => 1
def Relief.den : Relief → Int | .none => 1 | .l62 => 10 | .spontaneous => 2

/-- Interest on `base` (whole euros) from `start` to `stop`, with a relief; rounded to the euro. -/
def interest (base : Int) (start stop : Date) (r : Relief := .none) : Int :=
  rnd (base * rateSum start stop * r.num) (10000 * r.den)

/-- Art. 1727, II, 4: no interest when the insufficiency is at most a twentieth of the base after control,
except for a deliberate failure. -/
def tolerance (insufficiency baseAfter : Int) (deliberate : Bool) : Bool :=
  !deliberate && 20 * insufficiency ≤ baseAfter

/-! ## Majorations -/

/-- The failure on an income-tax return. -/
inductive Failure
  /-- Return filed on time, insufficiency corrected spontaneously or within 30 days of a request: none. -/
  | corrected
  /-- Good-faith insufficiency not so corrected: 10 % (art. 1758 A, I). -/
  | goodFaith
  /-- Return filed late without formal notice: 10 % (art. 1758 A, I; replaces 1728, 1, a). -/
  | lateSpontaneous
  /-- Return filed within 30 days of a formal notice: 20 % (art. 1758 A, I, second paragraph). -/
  | lateWithin30
  /-- Not filed within 30 days of a formal notice: 40 % (art. 1728, 1, b). -/
  | lateAfterNotice
  /-- Occult activity: 80 % (art. 1728, 1, c). -/
  | occult
  /-- Manquement délibéré: 40 % (art. 1729, a). -/
  | deliberate
  /-- Abus de droit: 80 %, or 40 % when the taxpayer had neither the main initiative nor the main benefit
  (art. 1729, b). -/
  | abuse (main : Bool)
  /-- Manœuvres frauduleuses: 80 % (art. 1729, c). -/
  | fraud
  /-- Opposition to a control (évaluation d'office, LPF L. 74): 100 % (art. 1732, a). -/
  | opposition
  deriving Repr, DecidableEq

/-- The rate in per cent. -/
def Failure.rate : Failure → Int
  | .corrected => 0
  | .goodFaith => 10
  | .lateSpontaneous => 10
  | .lateWithin30 => 20
  | .lateAfterNotice => 40
  | .occult => 80
  | .deliberate => 40
  | .abuse true => 80
  | .abuse false => 40
  | .fraud => 80
  | .opposition => 100

/-- The failures that art. 1728 itself charges (for the income tax its 10 % is replaced by art. 1758 A). -/
def Failure.is1728 : Failure → Bool
  | .lateAfterNotice | .occult => true
  | _ => false
def Failure.is1729 : Failure → Bool
  | .deliberate | .abuse _ | .fraud => true
  | _ => false

/-- Art. 1728, 1 as written (all taxes): the rate for a return that was due on `deadline`, filed on `filed`
(none: never filed), after a formal notice received on `notice` (if any). -/
def rate1728 (deadline : Date) (filed : Option Date) (notice : Option Date) (occult : Bool) : Int :=
  if occult then 80 else
  match filed, notice with
  | some f, _ => if f.days ≤ deadline.days then 0 else
      match notice with
      | some n => if f.days ≤ n.days + 30 then 10 else 40
      | none => 10
  | none, some _ => 40
  | none, none => 10

/-- The failure for a late income-tax return, from the dates (art. 1758 A and 1728). `none` when on time. -/
def lateFailure (deadline : Date) (filed : Option Date) (notice : Option Date) (occult : Bool) : Option Failure :=
  if occult then some .occult else
  match filed with
  | some f => if f.days ≤ deadline.days then none else
      match notice with
      | some n => if f.days ≤ n.days + 30 then some .lateWithin30 else some .lateAfterNotice
      | none => some .lateSpontaneous
  | none => match notice with
      | some _ => some .lateAfterNotice
      | none => some .lateSpontaneous

/-- A majoration: `rate` per cent of `rights`, rounded. -/
def majo (rate rights : Int) : Int := rnd (rate * rights) 100

/-- Art. 1729 A, 1: strata. `t0` is the tax on the declared items; `layers` are the reassessments with their rate
and the tax once that layer and the layers before it are added, in decreasing order of rate. Returns, per
layer, the extra tax and its majoration. -/
def strata (t0 : Int) : List (Int × Int) → List (Int × Int)
  | [] => []
  | (r, t) :: rest => (t - t0, majo r (pos (t - t0))) :: strata t rest

def strataTotal (t0 : Int) (layers : List (Int × Int)) : Int :=
  (strata t0 layers).foldl (fun a x => a + x.2) 0

/-- Order the reassessments by decreasing rate and compute the tax after each, from a tax function of the
total income: art. 1729 A, 1. -/
def insertDesc (x : Int × Int) : List (Int × Int) → List (Int × Int)
  | [] => [x]
  | y :: ys => if x.1 ≥ y.1 then x :: y :: ys else y :: insertDesc x ys
def sortDesc (xs : List (Int × Int)) : List (Int × Int) := xs.foldr insertDesc []

def layersOf (tax : Int → Int) (income : Int) : List (Int × Int) → List (Int × Int)
  | [] => []
  | (r, a) :: rest => (r, tax (income + a)) :: layersOf tax (income + a) rest

def majoByRate (tax : Int → Int) (income : Int) (adds : List (Int × Int)) : Int :=
  strataTotal (tax income) (layersOf tax income (sortDesc adds))

/-- Art. 1728, 4: late global return with late categorical returns. `tax` is the tax of the late global return,
`globalRate` its rate, `parts` the categorical incomes (rate, income) and `total` the total income. If the global
rate is at least every categorical rate it applies to the whole tax; otherwise each categorical rate applies to
the tax shared in proportion to its income, the global rate to the rest. -/
def lateSplit (tax globalRate total : Int) (parts : List (Int × Int)) : Int :=
  if parts.all (fun p => p.1 ≤ globalRate) then majo globalRate tax else
  let shares := parts.map (fun p => (p.1, rnd (tax * p.2) total))
  let rest := tax - shares.foldl (fun a s => a + s.2) 0
  shares.foldl (fun a s => a + majo s.1 s.2) 0 + majo globalRate rest

/-- Art. 1729 A, 2: a late return (rate `lateRate` on its own rights `tLate`) with reassessments whose rights `tAdd`
carry a 1729 rate `rate1729` (0 when none): the late rate applies to all the rights, but a higher 1729 rate
replaces it on the reassessments' rights. -/
def lateWithReassessment (lateRate tLate tAdd rate1729 : Int) : Int :=
  if rate1729 > lateRate then majo lateRate tLate + majo rate1729 tAdd else majo lateRate (tLate + tAdd)

/-- Art. 1730: 10 % of the sum not paid by the limit: 45 days after the roll is put into collection, and not
before 15 September for a tax of the current year. -/
def payLimit (recouvrement : Date) (currentYear : Bool) : Int :=
  if currentYear then max (recouvrement.days + 45) (Date.days ⟨recouvrement.y, 9, 15⟩) else recouvrement.days + 45
def latePayment (unpaid : Int) (recouvrement : Date) (currentYear : Bool) (paid : Date) : Int :=
  if paid.days > payLimit recouvrement currentYear then majo 10 unpaid else 0

/-- Art. 1729 G, 2: downward modulation of the withholding. `due` is what the withholding would have been,
`paid` what was withheld. Over a 10 % shortfall: 10 %; over 30 %: half the shortfall in per cent. Returns the
rate in hundredths of a per cent and the majoration. -/
def modulationRate (due paid : Int) : Int :=
  let short := due - paid
  if 10 * short ≤ due then 0 else if 10 * short ≤ 3 * due then 1000 else rnd (10000 * short) (2 * due)
def modulationMajo (due paid : Int) : Int := rnd (modulationRate due paid * pos (due - paid)) 10000

/-! ## Theorems -/

theorem months_mono {start stop stop' : Date} (h : stop.mi ≤ stop'.mi) :
    months start stop ≤ months start stop' := by
  unfold months; omega

theorem rateSum_mono {start stop stop' : Date} (h : stop.mi ≤ stop'.mi) :
    rateSum start stop ≤ rateSum start stop' := by
  unfold rateSum monthsOld monthsNew; omega

theorem rateSum_nonneg (start stop : Date) : 0 ≤ rateSum start stop := by
  unfold rateSum monthsOld monthsNew; omega

/-- **The interest grows with the delay**: for a non-negative base and any relief, a later stop never gives less. -/
theorem interest_mono_delay {base : Int} {start stop stop' : Date} (r : Relief) (hb : 0 ≤ base)
    (h : stop.mi ≤ stop'.mi) : interest base start stop r ≤ interest base start stop' r := by
  unfold interest
  have hn : 0 ≤ r.num := by cases r <;> decide
  have hd : 0 < 10000 * r.den := by cases r <;> decide
  apply rnd_mono hd
  apply Int.mul_le_mul_of_nonneg_right _ hn
  exact Int.mul_le_mul_of_nonneg_left (rateSum_mono h) hb

/-- **The interest grows with the base.** -/
theorem interest_mono_base {base base' : Int} (start stop : Date) (r : Relief) (h : base ≤ base') :
    interest base start stop r ≤ interest base' start stop r := by
  unfold interest
  have hn : 0 ≤ r.num := by cases r <;> decide
  have hd : 0 < 10000 * r.den := by cases r <;> decide
  apply rnd_mono hd
  apply Int.mul_le_mul_of_nonneg_right _ hn
  exact Int.mul_le_mul_of_nonneg_right h (rateSum_nonneg start stop)

/-- **0,20 % a month from 2018**: a period that starts in or after January 2018 costs 20 hundredths of a per cent
per month counted. -/
theorem rateSum_from2018 (start stop : Date) (h : cut ≤ start.mi) :
    rateSum start stop = 20 * months start stop := by
  unfold rateSum monthsOld monthsNew months; omega

/-- **0,40 % a month before 2018.** -/
theorem rateSum_before2018 (start stop : Date) (h : stop.mi < cut) :
    rateSum start stop = 40 * months start stop := by
  unfold rateSum monthsOld monthsNew months; omega

/-- The two periods add up to the whole period. -/
theorem months_split (start stop : Date) :
    monthsOld start stop + monthsNew start stop = months start stop := by
  unfold monthsOld monthsNew months; omega

/-- Before rounding, the interest of an income-tax assessment for income `n ≥ 2017` is exactly
`base × 0,20 % × months`, counted from July `n + 1`. -/
theorem ir_interest_rate (n : Int) (stop : Date) (h : 2017 ≤ n) :
    rateSum (irStart n) stop = 20 * months (irStart n) stop := by
  apply rateSum_from2018; simp only [irStart, Date.mi, cut]; omega

/-- One month of interest on 10 000 € from July 2025: 20 €. -/
example : interest 10000 (irStart 2024) ⟨2025, 7, 31⟩ = 20 := by decide

/-- **The reliefs never cost more**: the halved interest (art. 1727, V) and the 70 % of L. 62 are at most the
full interest. -/
theorem relief_le {base : Int} (start stop : Date) (r : Relief) (hb : 0 ≤ base) :
    interest base start stop r ≤ interest base start stop .none := by
  unfold interest Relief.num Relief.den
  have hx : 0 ≤ base * rateSum start stop := Int.mul_nonneg hb (rateSum_nonneg start stop)
  generalize base * rateSum start stop = x at hx
  unfold rnd
  cases r <;> simp only [Int.mul_one] <;> omega

theorem rate1728_cases (dl : Date) (f n : Option Date) (o : Bool) :
    rate1728 dl f n o = 0 ∨ rate1728 dl f n o = 10 ∨ rate1728 dl f n o = 40 ∨ rate1728 dl f n o = 80 := by
  unfold rate1728
  repeat' split
  all_goals simp

/-- **Majoration rates of art. 1728 are 10, 40 or 80 %** (whenever a majoration is due). -/
theorem rate1728_mem (dl : Date) (f n : Option Date) (o : Bool) (h : rate1728 dl f n o ≠ 0) :
    rate1728 dl f n o = 10 ∨ rate1728 dl f n o = 40 ∨ rate1728 dl f n o = 80 := by
  have := rate1728_cases dl f n o; omega

/-- **Rates of art. 1728 and 1729 are 10, 40 or 80 %.** -/
theorem rate_1728_1729_mem (f : Failure) (h : f.is1728 = true ∨ f.is1729 = true) :
    f.rate = 10 ∨ f.rate = 40 ∨ f.rate = 80 := by
  cases f <;> simp_all [Failure.is1728, Failure.is1729, Failure.rate] <;> rename_i b <;> cases b <;> simp

/-- **Art. 1729 rates are 40 or 80 %.** -/
theorem rate_1729_mem (f : Failure) (h : f.is1729 = true) : f.rate = 40 ∨ f.rate = 80 := by
  cases f <;> simp_all [Failure.is1729, Failure.rate] <;> rename_i b <;> cases b <;> simp

/-- **Every income-tax majoration rate is 0, 10, 20, 40, 80 or 100 %.** -/
theorem rate_mem (f : Failure) :
    f.rate ∈ ([0, 10, 20, 40, 80, 100] : List Int) := by
  cases f <;> simp [Failure.rate] <;> rename_i b <;> cases b <;> simp

/-- A higher failure never costs less: the majoration is monotone in the rate. -/
theorem majo_mono_rate {r r' x : Int} (hx : 0 ≤ x) (h : r ≤ r') : majo r x ≤ majo r' x := by
  unfold majo
  exact rnd_mono (by decide) (Int.mul_le_mul_of_nonneg_right h hx)

/-- The strata add up: whatever the order, the extra tax of the layers is the tax after all of them less the
declared tax (art. 1729 A, 1 splits the extra tax, it does not change it). -/
def lastTax (t0 : Int) : List (Int × Int) → Int
  | [] => t0
  | (_, t) :: rest => lastTax t rest

theorem strata_sum (t0 : Int) (layers : List (Int × Int)) :
    (strata t0 layers).foldl (fun a x => a + x.1) 0 = lastTax t0 layers - t0 := by
  suffices ∀ (acc t0 : Int) (l : List (Int × Int)),
      (strata t0 l).foldl (fun a x => a + x.1) acc = acc + (lastTax t0 l - t0) by
    simpa using this 0 t0 layers
  intro acc t0 l
  induction l generalizing acc t0 with
  | nil => simp [strata, lastTax]
  | cons x rest ih =>
    obtain ⟨r, t⟩ := x
    simp only [strata, List.foldl_cons, lastTax]
    rw [ih]
    omega

/-- **Art. 1729 G: the modulation rate never exceeds 50 %** (half of a shortfall of at most 100 %). -/
theorem modulationRate_le (due paid : Int) (hd : 0 < due) (hp : 0 ≤ paid) : modulationRate due paid ≤ 5000 := by
  unfold modulationRate rnd
  dsimp only
  split
  · omega
  · split
    · omega
    · have h1 : 2 * (10000 * (due - paid)) + 2 * due ≤ 5000 * (2 * (2 * due)) + 2 * due := by omega
      have : (2 * (10000 * (due - paid)) + 2 * due) / (2 * (2 * due)) ≤ 5000 := by
        apply (Int.ediv_le_iff_le_mul (by omega)).2
        omega
      exact this

/-! ## Checks against the BOFiP's worked examples (each by `decide`) -/

/-- BOI-CF-INF-10-20-30-20 § 10, exemple 1: tax 5 372 declared, 12 142 after the deliberate layer, 13 298 after the
good-faith layer: majorations 2 708 and 0 (total 2 708). -/
example : strataTotal 5372 [(40, 12142), (0, 13298)] = 2708 := by decide
/-- Exemple 2: 80 % layer to 15 996, 40 % layer to 19 880: 8 499 + 1 554 = 10 053. -/
example : strataTotal 5372 [(80, 15996), (40, 19880)] = 10053 := by decide
/-- BOI-CF-INF-10-20-10 § 80: tax 9 830, BNC 16 000 at 40 %, rest at 10 %, total income 51 000: 1 909. -/
example : lateSplit 9830 10 51000 [(40, 16000)] = 1909 := by decide
/-- BOI-CF-INF-10-20-30-10 § 30, exemples 1 and 2: 537 + 2 708 = 3 245; good faith: 1 214. -/
example : lateWithReassessment 10 5372 6770 40 = 3245 := by decide
example : lateWithReassessment 10 5372 6770 0 = 1214 := by decide

end FrTax.Penalties
