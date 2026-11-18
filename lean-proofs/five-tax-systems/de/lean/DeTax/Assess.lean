import DeTax.Social

/-!
# The assessment (Veranlagung) of a household, VZ 2025

The order of EStG § 2:

* (1)–(2) **Einkünfte** of each kind: wages less the Arbeitnehmer-Pauschbetrag (§ 19, § 9a Nr. 1a), profit from
  selbständige Arbeit (§ 18, taken as given), the taxable part of a statutory pension less 102 € (§ 22 Nr. 1
  Satz 3 a aa, § 9a Nr. 3), rents (§ 21, taken as net), capital income less the Sparer-Pauschbetrag (§ 20 (9)) —
  the last only if the household asks for the tariff (§ 32d (6)); otherwise it stays outside (§ 2 (5b)) and is
  taxed at 25 % (§ 32d (1)).
* (3) **Gesamtbetrag der Einkünfte** = Summe der Einkünfte − Altersentlastungsbetrag (§ 24a) − Entlastungsbetrag
  für Alleinerziehende (§ 24b).
* (4) **Einkommen** = Gesamtbetrag − Sonderausgaben (Vorsorgeaufwendungen § 10 (1) Nr. 2, 3, 3a with (3), (4);
  donations § 10b (1) within 20 % of the Gesamtbetrag, or the Pauschbetrag of § 10c).
* (5) **zu versteuerndes Einkommen** = Einkommen − Freibeträge für Kinder (§ 32 (6)) where they beat the
  Kindergeld (§ 31 Satz 4).
* (6) **festzusetzende Einkommensteuer** = tariff tax (§ 32a (1) or (5)) + Kindergeld added back (§ 2 (6)
  Satz 3) + tax under § 32d (3)/(4).

Surtaxes: SolZG § 3 (2) and EStG § 51a (2) take the tax *with* the Freibeträge for every child, whatever the
Günstigerprüfung chose. § 32d (6) compares the "Einkommensteuer einschließlich Zuschlagsteuern" of both ways.

Mapping of the canonical household (stated assumptions):
* two married adults are assessed jointly (§ 26b, splitting § 32a (5)); otherwise each adult on their own;
* household-level amounts (interest, dividends, gains, rents, donations, pension contributions) are split equally
  between two adults;
* children under 18, and 18–24 taken to be in education (§ 32 (4) Nr. 2 a), count for Kindergeld and Freibeträge;
  older children do not;
* a married couple or a single adult has the full (doubled) Freibeträge per child (§ 32 (6) Satz 2, 3: for the
  single adult the other parent is taken to be absent) and sets the full Kindergeld against them; two unmarried
  adults are both parents: each has the single Freibeträge and half the Kindergeld (§ 31 Satz 4 Halbsatz 2);
* the Günstigerprüfung runs child by child, the Freibeträge of each further child tested on the income left after
  the earlier ones (R 31 (1) EStR-reading; see FINDINGS);
* wages of at most 6 672 € a year are a Minijob taxed at 2 % by the employer (§ 40a (2)) and stay out of the
  assessment (§ 40 (3)) — the employer's flat tax is not shown;
* the pension is a statutory pension that began in the year the person turned 65 (or in 2025 if younger), and its
  taxable share is applied to the 2025 amount (later increases, fully taxable, are not tracked);
* pension contributions are to a Basisrente (§ 10 (1) Nr. 2 b aa), deductible within § 10 (3) with the statutory
  ones; donations are to bodies of § 10b (1).
-/

namespace DeTax

structure Adult where
  age : Int
  wages : Int := 0
  selfEmployment : Int := 0
  pension : Int := 0
  deriving Repr

structure Household where
  id : String := ""
  year : Int := 2025
  adults : List Adult
  married : Bool := false
  children : List Int := []
  interest : Int := 0
  dividends : Int := 0
  capitalGains : Int := 0
  rentalIncome : Int := 0
  charitable : Int := 0
  pensionContributions : Int := 0
  deriving Repr

structure Opts where
  /-- Kirchensteuer rate in basis points (800 Bavaria/Baden-Württemberg, 900 elsewhere); 0: not a member. -/
  kistBp : Int := 0
  /-- Assess a married couple jointly (default) or individually (§ 26a, for comparison). -/
  joint : Bool := true
  /-- § 31 Günstigerprüfung child by child (default) or for all children together (GETTSIM's reading). -/
  perChild : Bool := true
  /-- Apply the § 32d (6) Günstigerprüfung for capital income (default; GETTSIM does not). -/
  opt32d6 : Bool := true
  /-- GETTSIM 1.3 readings everywhere they differ from the statute (tariff, Vorsorge, § 24a, contributions), to
  reproduce that referee and so attribute every difference; never used for results. -/
  g : Bool := false
  /-- The GETTSIM readings one at a time (for counting their effects): tariff, Vorsorge, § 24a, contributions. -/
  gTariff : Bool := false
  gVors : Bool := false
  gAlte : Bool := false
  gSv : Bool := false
  deriving Repr

/-- Children who count (§ 32 (3), (4) Satz 1 Nr. 2 a): under 25. -/
def eligibleKids (h : Household) : Int := (h.children.filter (· < 25)).length

/-- One assessment unit: one person, or a jointly assessed couple. Amounts in euros unless `C`. -/
structure VUnit where
  members : List (Adult × Sv)
  joint : Bool
  /-- Capital income, rents, donations, Basisrente contributions of the unit, in cents. -/
  capital : Int
  rental : Int
  charitable : Int
  basisrente : Int
  kids : Int
  /-- Freibeträge of § 32 (6) per child for this unit (9 600 € or 4 800 €). -/
  fbPerChild : Int
  /-- Kindergeld per child set against them in the Günstigerprüfung (3 060 € or 1 530 €). -/
  kgPerChild : Int
  alleinerziehend : Bool
  deriving Repr

/-- The year the pension began (assumption: the year the person turned 65, at the latest 2025). -/
def rentenbeginn (age : Int) : Int := min 2025 (2025 - age + 65)

/-- Einkünfte of one member, in cents: (wages § 19, self-employment § 18, pension § 22, wage counted for § 24a). -/
def memberEinkuenfte (a : Adult) (s : Sv) : Int × Int × Int × Int :=
  let w := if s.minijob then 0 else a.wages
  let e19 := w - min P.arbeitnehmerPausch w
  let rentC := ct a.pension * P.besteuerungsanteil (rentenbeginn a.age) / 1000
  let e22C := rentC - min (ct P.wkPausch22) rentC
  (ct e19, ct a.selfEmployment, e22C, ct w)

/-- **§ 24a**: for a member who "vor dem Beginn des Kalenderjahres ... das 64. Lebensjahr vollendet hatte" (aged 65
or more at the end of 2025), the percentage and cap of the year after the 64th birthday (`2090 − age`), applied to
the wage and the positive sum of the other Einkünfte except the pension; rounded up to the euro (as the PAP's
MRE4ALTE does). Result in cents.

`g` (GETTSIM 1.3, comparison only): the row of the year of the 64th birthday (`2089 − age`), nothing for rows before
2005, gross capital income in the base whatever its taxation (`capGrossC`), no rounding. -/
def altersentlastungC (age wageC otherC : Int) (g : Bool := false) (capGrossC : Int := 0) : Int :=
  if age < 65 then 0
  else if g then
    if 2089 - age < 2005 then 0 else
    let (rate, cap) := P.altersentlastung (2089 - age)
    min ((wageC + pos (otherC + capGrossC)) * rate / 1000) (ct cap)
  else
    let (rate, cap) := P.altersentlastung (2090 - age)
    ct (min (cdiv ((wageC + pos otherC) * rate) 100000) cap)

/-- **GETTSIM 1.3's tariff for 2025** (comparison only). GETTSIM does not use the statute's coefficients: it takes
the marginal rates at the thresholds (14 %, 23,97 %, 42 %, 45 %), derives each quadratic term as "(rate_fiv −
rate_iv) / (2 × (upper_thres − low_thres))" (0,0997 / 10 694 and 0,1803 / 102 074 instead of 932,30·10⁻⁸ and
176,64·10⁻⁸), makes the pieces continuous, evaluates them at the unrounded income `x = xC / (100·n)` (`n` = 2 for
splitting) and rounds once, `⌊n·f(x)⌋`. Exact rational arithmetic here; GETTSIM itself uses floating point. -/
def gettsimTariff (n xC : Int) : Int :=
  let q := 100 * n
  -- c2 = f(17 443) = 0,14·5 347 + 0,0997/10 694 · 5 347², as c2N / 106 940 000
  let c2N : Int := 14 * 1069400 * 5347 + 997 * 5347 * 5347
  -- c3 = f(68 480) = c2 + 0,2397·51 037 + 0,1803/102 074 · 51 037², as c3N / (106 940 000 · 1 020 740 000)
  let c3N : Int := c2N * 1020740000 + 2397 * 51037 * 102074 * 106940000 + 1803 * 51037 * 51037 * 106940000
  let D3 : Int := 106940000 * 1020740000
  -- c4 = c3 + 0,42·209 345
  let c4N : Int := c3N + 42 * 209345 * (D3 / 100)
  if xC < 12096 * q then 0
  else if xC < 17443 * q then
    let dN := xC - 12096 * q
    (n * (14 * 1069400 * dN * q + 997 * dN * dN)) / (106940000 * q * q)
  else if xC < 68480 * q then
    let eN := xC - 17443 * q
    (n * (c2N * 1020740000 * q * q + 2397 * eN * 102074 * 106940000 * q + 1803 * eN * eN * 106940000))
      / (D3 * q * q)
  else if xC < 277825 * q then
    (n * (c3N * q + 42 * (xC - 68480 * q) * (D3 / 100))) / (D3 * q)
  else
    (n * (c4N * q + 45 * (xC - 277825 * q) * (D3 / 100))) / (D3 * q)

/-- The result of assessing one unit one way (capital income at 25 % or in the tariff). Cents unless noted. -/
structure UnitResult where
  capInTariff : Bool
  summeEinkuenfte : Int
  altersentlastung : Int
  entlastungAE : Int
  gesamtbetrag : Int
  vorsorge : Int
  sonderausgabenOther : Int
  einkommen : Int
  /-- Number of children for whom the Freibeträge beat the Kindergeld. -/
  kidsFB : Int
  /-- zu versteuerndes Einkommen, whole euros. -/
  zve : Int
  /-- Tariff tax, whole euros. -/
  tarif : Int
  kindergeldAddBack : Int
  abgeltung : Int
  /-- SolZG § 3 (2) base (tariff part), whole euros. -/
  soliBase : Int
  soli : Int
  kist : Int
  /-- Kindergeld this unit keeps after the Günstigerprüfung (cents, a year). -/
  kindergeldKept : Int
  deriving Repr

/-- festzusetzende ESt (with the Kindergeld added back) plus surtaxes: what § 32d (6) compares. -/
def UnitResult.burden (r : UnitResult) : Int :=
  ct r.tarif + r.kindergeldAddBack + r.abgeltung + r.soli + r.kist

/-- **§ 10 (1) Nr. 2, 3, 3a; (3); (4)**: the deductible Vorsorgeaufwendungen of a unit, in cents. -/
def vorsorgeC (u : VUnit) : Int :=
  let n : Int := u.members.length
  let rvAll := (u.members.map fun (_, s) => s.rv + s.rvEmployer).foldl (· + ·) 0
  let rvEmployer := (u.members.map fun (_, s) => s.rvEmployer).foldl (· + ·) 0
  -- (3): "bis zu dem Höchstbeitrag zur knappschaftlichen Rentenversicherung"; doubled for spouses; "vermindert um
  -- den nach § 3 Nummer 62 steuerfreien Arbeitgeberanteil"
  let nr2 := min (rvAll + u.basisrente) (ct (n * P.hb10_3)) - rvEmployer
  let nr3 := (u.members.map fun (_, s) => s.kvBasis + s.pv).foldl (· + ·) 0
  let nr3a := (u.members.map fun (_, s) => s.av + (s.kv - s.kvBasis)).foldl (· + ·) 0
  let hb4 := ct ((u.members.map fun (_, s) => s.hb4).foldl (· + ·) 0)
  -- (4) Satz 4: if Nr. 3 alone exceeds the cap, it is deducted in full and Nr. 3a not at all
  let nr34 := max nr3 (min (nr3 + nr3a) hb4)
  pos nr2 + nr34

/-- GETTSIM 1.3's Vorsorgeaufwendungen (comparison only): RV of the employee plus private contributions up to the
cap, *without* the employer's share (§ 10 (3) Satz 1, 5 counts it against the cap); 4 % off every KV contribution
(also pensioners' and the self-employed's, who have no Krankengeld); 1 900 € a person; rounded up to the euro. -/
def vorsorgeGettsimC (u : VUnit) : Int :=
  let n : Int := u.members.length
  let sum (f : Sv → Int) : Int := (u.members.map fun (_, s) => f s).foldl (· + ·) 0
  let alters := min (sum (·.rv) + u.basisrente) (ct (n * P.hb10_3))
  -- in 1/100 cent: PV + 96 % of KV
  let basis := 100 * sum (·.pv) + 96 * sum (·.kv)
  let sonst := 100 * min (sum (·.av) + sum (·.pv) + sum (·.kv)) (ct (n * P.hb10_4Employee))
  ct (cdiv (100 * alters + max basis sonst) 10000)

/-- Assess one unit with capital income at 25 % (`capInTariff = false`) or in the tariff (`true`). -/
def assessUnit (o : Opts) (u : VUnit) (capInTariff : Bool) : UnitResult :=
  let n : Int := u.members.length
  let tarif (x : Int) : Int := if u.joint then t2025.estSplit x else t2025.est x
  -- the tariff on an amount in cents: § 32a (1) Satz 1 rounds it down to the euro first (GETTSIM does not)
  let tarifC (xC : Int) : Int := if o.g || o.gTariff then gettsimTariff (if u.joint then 2 else 1) xC else tarif (euroDown xC)
  -- capital income after the Sparer-Pauschbetrag (§ 20 (9): 1 000 €, 2 000 € jointly)
  let sparer := if u.joint then 2 * P.sparerPausch else P.sparerPausch
  let capNet := pos (u.capital - min (ct sparer) u.capital)
  let capShareC := if capInTariff then capNet / n else 0
  let rentShareC := u.rental / n
  let per := u.members.map fun (a, s) =>
    let (e19, e18, e22, wageC) := memberEinkuenfte a s
    let sum := e19 + e18 + e22 + rentShareC + capShareC
    let alte := altersentlastungC a.age wageC (e18 + rentShareC + capShareC) (o.g || o.gAlte) (u.capital / n)
    (sum, alte)
  let summe := (per.map (·.1)).foldl (· + ·) 0
  let alte := (per.map (·.2)).foldl (· + ·) 0
  -- § 24b (2): 4 260 €, plus 240 € for each further child
  let eab := if u.alleinerziehend ∧ u.kids > 0 then ct (P.entlastungAE + P.entlastungAEWeiteres * (u.kids - 1))
    else 0
  let gdE := summe - alte - eab
  let vors := if o.g || o.gVors then vorsorgeGettsimC u else vorsorgeC u
  -- § 10b (1): within 20 % of the Gesamtbetrag; § 10c: at least 36 € a person (72 € jointly)
  let spenden := min u.charitable (pos (gdE * P.spendenQuoteBp / 10000))
  let saOther := max (ct (P.sonderausgabenPausch * n)) spenden
  let eink := gdE - vors - saOther
  -- § 31 Satz 4: child by child, the Freibeträge are deducted when they save more tax than the Kindergeld
  let fbC := ct u.fbPerChild
  let kgC := ct u.kgPerChild
  let rec choose (k : Nat) (fuel : Nat) : Int :=
    match fuel with
    | 0 => k
    | f + 1 =>
      if (k : Int) ≥ u.kids then k
      else
        let saving := tarifC (eink - (k : Int) * fbC) - tarifC (eink - ((k : Int) + 1) * fbC)
        if ct saving > kgC then choose (k + 1) f else k
  -- the other reading: one comparison for all the children together (all Freibeträge or none)
  let allTogether : Int :=
    if ct (tarifC eink - tarifC (eink - u.kids * fbC)) > u.kids * kgC then u.kids else 0
  let kFB : Int := if o.perChild then choose 0 (u.kids.toNat + 1) else allTogether
  let zve := if o.g || o.gTariff then pos (euroDown (eink - kFB * fbC)) else euroDown (eink - kFB * fbC)
  let t := tarifC (eink - kFB * fbC)
  -- surtax base: Freibeträge for every child (SolZG § 3 (2); EStG § 51a (2))
  let soliBase := tarifC (eink - u.kids * fbC)
  -- § 32d (1): 25 %, or (e − 4q)/(4 + k) under church tax
  let abg := if capInTariff then 0 else (capNet * 10000) / (40000 + o.kistBp)
  let fg := ct (P.soliFreigrenze u.joint)
  let aC := ct soliBase
  let soliTarifMille := if aC > fg then min (P.soliRate * aC) (P.soliMilderung * (aC - fg)) else 0
  let soli := (soliTarifMille + P.soliRate * abg) / 1000
  let kist := (o.kistBp * (aC + abg)) / 10000
  { capInTariff, summeEinkuenfte := summe, altersentlastung := alte, entlastungAE := eab, gesamtbetrag := gdE,
    vorsorge := vors, sonderausgabenOther := saOther, einkommen := eink, kidsFB := kFB, zve, tarif := t,
    kindergeldAddBack := kFB * kgC, abgeltung := abg, soliBase, soli, kist,
    kindergeldKept := (u.kids - kFB) * kgC }

/-- **§ 32d (6)**: the tariff for capital income "wenn dies zu einer niedrigeren Einkommensteuer einschließlich
Zuschlagsteuern führt". -/
def bestUnit (o : Opts) (u : VUnit) : UnitResult :=
  let a := assessUnit o u false
  if u.capital ≤ 0 ∨ !o.opt32d6 then a else
  let b := assessUnit o u true
  if b.burden < a.burden then b else a

/-- The units of a household and each adult's contributions. -/
def units (o : Opts) (h : Household) : List VUnit :=
  let kids := eligibleKids h
  let childless := h.children.isEmpty
  let under25 : Int := (h.children.filter (· < 25)).length
  let svs := h.adults.map fun a => (a, svPerson a.age a.wages a.selfEmployment a.pension childless under25 (o.g || o.gSv))
  let capital := h.interest + h.dividends + h.capitalGains
  let n : Int := h.adults.length
  if h.adults.length = 2 ∧ h.married ∧ o.joint then
    [{ members := svs, joint := true, capital := ct capital, rental := ct h.rentalIncome, charitable := ct h.charitable,
       basisrente := ct h.pensionContributions, kids, fbPerChild := 2 * (P.kinderfreibetrag + P.bea),
       kgPerChild := 12 * P.kindergeldMonat, alleinerziehend := false }]
  else if h.adults.length = 2 then
    -- two adults assessed apart: each a parent with the single Freibeträge and half the Kindergeld
    svs.map fun m =>
      { members := [m], joint := false, capital := ct capital / n, rental := ct h.rentalIncome / n,
        charitable := ct h.charitable / n, basisrente := ct h.pensionContributions / n, kids,
        fbPerChild := P.kinderfreibetrag + P.bea, kgPerChild := 6 * P.kindergeldMonat,
        alleinerziehend := false }
  else
    svs.map fun m =>
      { members := [m], joint := false, capital := ct capital, rental := ct h.rentalIncome, charitable := ct h.charitable,
        basisrente := ct h.pensionContributions, kids, fbPerChild := 2 * (P.kinderfreibetrag + P.bea),
        kgPerChild := 12 * P.kindergeldMonat, alleinerziehend := h.adults.length = 1 }

/-- The household's result (cents). -/
structure Result where
  units : List (VUnit × UnitResult)
  incomeTax : Int
  soli : Int
  kist : Int
  employeeSocial : Int
  kindergeldPaid : Int
  kindergeldKept : Int
  deriving Repr

def assess (o : Opts) (h : Household) : Result :=
  let us := units o h
  let rs := us.map fun u => (u, bestUnit o u)
  let sum (f : UnitResult → Int) : Int := (rs.map fun (_, r) => f r).foldl (· + ·) 0
  let sv := (us.map fun u => (u.members.map fun (_, s) => s.total).foldl (· + ·) 0).foldl (· + ·) 0
  { units := rs,
    incomeTax := sum fun r => ct r.tarif + r.abgeltung,
    soli := sum (·.soli), kist := sum (·.kist), employeeSocial := sv,
    kindergeldPaid := ct (12 * P.kindergeldMonat * eligibleKids h),
    kindergeldKept := sum (·.kindergeldKept) }

end DeTax
