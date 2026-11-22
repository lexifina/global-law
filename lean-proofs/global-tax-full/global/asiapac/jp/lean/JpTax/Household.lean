import JpTax.Person
import JpTax.Benefit

/-!
# From the canonical household to persons, and back

Japan taxes individuals: each adult has its own income tax and 住民税, and a married couple's spouse deductions depend on
the other spouse's 合計所得金額. Choices made here (each a statutory default or a stated assumption):

* **Dependants.** All children are claimed by the adult with the larger 総所得金額等 (所得税法施行令第219条第2項第2号: when
  the declarations do not settle it, "総所得金額、退職所得金額及び山林所得金額の合計額...が最も大きい居住者の扶養親族"); ties go
  to the first adult. Children have no income unless the (Japan-only) field `wages` is given.
* **Spouse.** In a married couple the spouse with the larger 合計所得金額 claims the other (配偶者控除 or 配偶者特別控除;
  第83条の2第2項第1号 forbids both claiming each other).
* **ひとり親.** One unmarried adult with a child is a ひとり親 (第2条第1項第31号; no de facto spouse assumed); two unmarried
  adults with children are taken to be a de facto couple, so neither is. For the 住民税 調整控除 (whose amount depends on
  the parent's sex) the single parent is taken to be the mother unless `jpSingleParentSex` is "M".
* **Investment income** (household totals, split equally between the adults when it matters, the odd yen to the first):
  interest on deposits is 源泉分離課税 (措置法第3条: 15 % + 復興 0.315 %; 地方税法第71条の6 利子割 5 %); listed-share
  dividends default to 確定申告不要 (措置法第8条の5: withheld at 15.315 % + 配当割 5 %, final, outside the 合計所得金額);
  `jpDividends: "aggregate"` taxes them with the other income instead (総合課税, with 配当控除); capital gains on listed
  shares are taken to be in a 特定口座 with withholding (措置法第37条の11, 第37条の11の5: 15.315 % + 株式等譲渡所得割 5 %,
  final). No NISA.
* **Rental income** (net) is split equally between the adults; **charitable** gifts are made by the adult with the larger
  総所得金額等 and are 特定寄附金 (第78条; e.g. to a 公益社団法人 or 認定NPO法人) not designated by the ward's ordinance, so
  they give no 住民税 credit.
* **pensionContributions** are iDeCo contributions (小規模企業共済等掛金控除, 第75条), given to the first adult up to its
  limit (確定拠出年金法施行令第36条: 23,000 yen a month for an employee without a company plan or a dependent spouse,
  68,000 for others), then to the second; anything above is ignored and reported.
-/

namespace JpTax

structure Adult where
  age : Int
  wages : Int
  selfEmployment : Int
  pension : Int
  deriving Repr, Inhabited

structure Child where
  age : Int
  wages : Int := 0
  deriving Repr, Inhabited

structure Household where
  id : String
  year : Int
  adults : List Adult
  married : Bool
  children : List Child
  interest : Int := 0
  dividends : Int := 0
  capitalGains : Int := 0
  rentalIncome : Int := 0
  charitable : Int := 0
  pensionContributions : Int := 0
  aggregateDividends : Bool := false
  declaredDividends : Bool := false   -- 申告分離課税 (措置法第8条の4) instead of 確定申告不要
  declaredGains : Bool := false       -- gains declared under 措置法第37条の11 instead of the 特定口座 withholding
  singleParentMother : Bool := true
  /-- `jpSpouseClaimant`: "best" (default), "higher" or "lower" (see `compute`) -/
  spouseClaimant : String := "best"
  /-- `jptax --oecd` (convention mode, never the default): the OECD's flat social-insurance rates (`socialOecd`) and its
  第28条第3項 formula for the 給与所得 at every wage. -/
  oecd : Bool := false
  deriving Repr, Inhabited

structure Result where
  persons : List (PersonIn × PersonOut × SocialOut)
  incomeTax : Int          -- 基準所得税額 + 15 % separate taxes
  fukkoTotal : Int         -- 復興特別所得税
  localTax : Int           -- 住民税 所得割 + 均等割 + 森林環境税 + 利子割/配当割/株式等譲渡所得割
  employeeSocial : Int
  benefits : Int
  sepNational : Int        -- the 15 % part of the separate taxes
  sepFukko : Int
  sepLocal : Int
  idecoIgnored : Int
  fuyoTeate : Int := 0     -- 児童扶養手当 (in `benefits`)
  unsupported : List String
  deriving Repr

def childRelative (c : Child) : Relative := { age := c.age, income := kyuyoShotoku c.wages }

/-- The child as a relative in tax year `y` (令和6年分: 給与所得 by that year's 別表第五, the 48 万 limit). -/
def childRelativeY (y : Int) (c : Child) : Relative :=
  { age := c.age, income := kyuyoShotokuY y c.wages, lim := douitsuLimitY y }

/-- Split `x` into `k` near-equal parts, the remainder to the first. -/
def splitAmount (x : Int) (k : Nat) : List Int :=
  if k = 0 then [] else
  let q := x / k
  (List.range k).map fun i => if i = 0 then x - q * ((k : Int) - 1) else q

def idecoCap (a : Adult) (spouseInsured : Bool) (married : Bool) : Int :=
  if a.age ≥ 65 then 0
  else if insuredEmployee a.wages then 276000
  else if married && spouseInsured && decide (a.wages + a.selfEmployment + a.pension < 1300000) then 276000
  else 816000

/-- 健康保険法第3条第7項 (被扶養者) with the 昭和52年 notice on income: a spouse "主としてその被保険者により生計を維持する
もの" whose yearly income is under 1,300,000 yen (1,800,000 from age 60) is covered by the insured spouse at no cost, and
is a 第3号被保険者 for the pension (国民年金法第7条第1項第3号). -/
def dependantCovered (h : Household) (i : Nat) : Bool :=
  let a := h.adults.getD i default
  let o := h.adults.getD (1 - i) default
  h.married && decide (h.adults.length = 2) && insuredEmployee o.wages && !insuredEmployee a.wages &&
    decide (a.wages + a.selfEmployment + a.pension < (if a.age ≥ 60 then 1800000 else 1300000))

def argmaxIdx (xs : List Int) : Nat :=
  (xs.zipIdx.foldl (fun (best : Option (Int × Nat)) (x, i) =>
    match best with
    | none => some (x, i)
    | some (bx, bi) => if x > bx then some (x, i) else some (bx, bi)) none).map (·.2) |>.getD 0

/-- 児童手当 (2024 rules): the 所得 of the higher earner, 総所得金額 less 80,000 yen (児童手当法施行令第3条). -/
def teateShotoku (outs : List PersonOut) (top : Nat) : Int := pos ((outs.getD top default).sogo - 80000)

/-- 扶養親族等 + 児童 of the claimant: the children and a 同一生計配偶者 (one taking a 配偶者控除). -/
def teateDeps (h : Household) (outs : List PersonOut) (top : Nat) : Int :=
  (if (outs.getD top default).dHaigusha > 0 then 1 else 0) + (h.children.length : Int)

/-- The household with the spouse claim made by the adult with the larger 合計所得金額 (`flip = false`) or by the other
adult (`flip = true`), and the children claimed as 扶養親族 by the larger income (`kidsFlip = false`) or by the other
adult; gifts and the 児童手当 claimant stay with the larger income. -/
def computeClaim (h : Household) (flip : Bool) (kidsFlip : Bool := false) : Result :=
  let n := h.adults.length
  let socials := h.adults.map fun a => if h.oecd then socialOecd a.wages a.age h.year else social a.wages a.age h.year
  let rentals := splitAmount h.rentalIncome n
  let divs := if h.aggregateDividends then splitAmount h.dividends n else List.replicate n 0
  let declare := !h.aggregateDividends && h.declaredDividends
  let sepDivs := if h.aggregateDividends || declare then List.replicate n 0 else splitAmount h.dividends n
  let declDivs := if declare then splitAmount h.dividends n else List.replicate n 0
  let sepInts := splitAmount h.interest n
  let sepGains := if h.declaredGains then List.replicate n 0 else splitAmount h.capitalGains n
  let declGains := if h.declaredGains then splitAmount h.capitalGains n else List.replicate n 0
  let rels := h.children.map (childRelativeY h.year)
  let childUnder23 := rels.any fun d => decide (d.age < 23) && d.fuyo
  let base : List PersonIn := (List.range n).map fun i =>
    let a := h.adults.getD i default
    { age := a.age, wages := a.wages, business := a.selfEmployment, pension := a.pension,
      rental := rentals.getD i 0, dividends := divs.getD i 0, ideco := 0, donations := 0,
      socialIns := (socials.getD i default).total, childUnder23, singleParent := false,
      singleParentMother := h.singleParentMother, spouse := none, dependants := [],
      sepInterest := sepInts.getD i 0, sepDividends := sepDivs.getD i 0, sepGains := sepGains.getD i 0,
      declDividends := declDivs.getD i 0, declGains := declGains.getD i 0, oecdKyuyo := h.oecd, year := h.year }
  let incomes := base.map fun p => gokei p (incomeParts p).2.2.2
  let top := argmaxIdx incomes
  -- iDeCo
  let insured := h.adults.map fun a => insuredEmployee a.wages
  let caps := (List.range n).map fun i =>
    idecoCap (h.adults.getD i default) (insured.getD (1 - i) false) h.married
  let (idecos, left) := caps.foldl (fun (acc : List Int × Int) c =>
    let take := min c (pos acc.2); (acc.1 ++ [take], acc.2 - take)) ([], pos h.pensionContributions)
  let single := n = 1 && !h.married && rels.any (·.fuyo)
  let persons : List PersonIn := (List.range n).map fun i =>
    let p := base.getD i default
    let other := 1 - i
    let claimant := if flip then 1 - top else top
    let holder := if kidsFlip then 1 - top else top
    let spouse : Option Relative :=
      if h.married && n = 2 && i = claimant then
        some { age := (h.adults.getD other default).age, income := incomes.getD other 0, lim := douitsuLimitY h.year }
      else none
    { p with ideco := idecos.getD i 0,
             donations := if i = top then pos h.charitable else 0,
             singleParent := single,
             spouse,
             dependants := if i = holder then rels else [] }
  let outs := persons.map person
  let triples := (List.range n).map fun i => (persons.getD i default, outs.getD i default, socials.getD i default)
  let sumO (f : PersonOut → Int) := outs.foldl (fun acc o => acc + f o) 0
  let sepN := sumO (·.sepNational)
  let sepF := sumO (·.sepFukko)
  let sepLocal := sumO (·.sepLocal)
  -- 児童扶養手当 (Benefit.lean): the single parent; 監護等児童 aged 18 or less; 加算対象扶養親族等 = the 扶養親族 children
  let fuyo : Int :=
    if single then
      let o := outs.getD 0 default
      let s := fuyoShotoku o.sogo (pos (o.kyuyo - o.adjust) + o.nenkin) (o.kyuyo + o.nenkin)
      fuyoYearY h.year (h.children.filter (fun c => decide (0 ≤ c.age ∧ c.age ≤ 18))).length s
        ((rels.filter (·.fuyo)).map (·.age))
    else 0
  { persons := triples,
    incomeTax := sumO (·.kijun) + sumO (·.minTax) + sepN,
    fukkoTotal := sumO (·.fukko) + sepF,
    localTax := sumO (fun o => if h.oecd then o.loc.oecdTotal else o.loc.total) + sepLocal,
    employeeSocial := socials.foldl (fun acc s => acc + s.total) 0,
    benefits := teateYearY h.year (h.children.map (·.age)) (teateShotoku outs top) (teateDeps h outs top) + fuyo,
    fuyoTeate := fuyo,
    sepNational := sepN, sepFukko := sepF, sepLocal := sepLocal,
    idecoIgnored := left,
    unsupported :=
      (if (List.range n).any (fun i =>
            let a := h.adults.getD i default
            !insuredEmployee a.wages && decide (a.wages + a.selfEmployment > 0) && decide (a.age < 60) &&
            !dependantCovered h i)
        then ["国民年金・国民健康保険 for adults who are not insured employees (not modelled; their 社会保険料控除 is 0)"]
        else []) ++
      (if h.adults.any (fun a => decide (a.age ≥ 65) && decide (a.pension > 0))
        then ["後期高齢者医療 / 国民健康保険 / 介護保険第1号 premiums of pensioners (not modelled)"] else []) ++
      (if left > 0 then ["pensionContributions above the iDeCo limits ignored"] else []) ++
      (if h.year = 2024 then ["令和6年分 (2024): 定額減税 (措置法第41条の3の3) included; 住民税 = 令和7年度; 調整給付 (cash, municipalities) not modelled"]
        else if h.year = 2022 ∨ h.year = 2023 then [s!"{h.year}: 所得税 of that year (no 定額減税), 住民税 of the following fiscal year (令和{h.year - 2017}年度), the old 児童手当 regime, that year's 児童扶養手当, 協会けんぽ 東京 and 雇用保険 rates"]
        else if h.year ≠ 2025 then ["only 令和4年分 to 令和7年分 are modelled; the 2025 law was applied"] else []) }

/-- **Who claims the spouse and the children** (monotonicity fix 2026-11-21, global/monoscan). 所得税法第83条の2第2項
(law/shotokuzeiho_2025-12-31.xml): "前項の規定は、同項に規定する生計を一にする配偶者が、次に掲げる場合に該当するときは、
適用しない。一 当該配偶者が前項に規定する居住者として同項の規定の適用を受けている場合" — only one spouse may claim, and the
statute does not say which: the couple chooses. The children are likewise the 扶養親族 of the parent whose 申告書 lists
them (所得税法施行令第219条第1項; its 第2項第2号, the larger 総所得金額等, applies only when the declarations do not settle
it). Both are elections; convention (DESIGN §6, as `krClaimant: "best"`): the four combinations (spouse claim by
either adult, all children with either adult) are computed and the one with the lowest national + 復興 + local tax is
taken (ties: the earlier default, the larger income claiming everything). Before, the larger 合計所得金額 always claimed
both, so the tax jumped when the incomes crossed. `jpSpouseClaimant` "higher" / "lower" fixes both claims on that
adult. -/
def compute (h : Household) : Result :=
  let total (r : Result) : Int := r.incomeTax + r.fukkoTotal + r.localTax
  let hi := computeClaim h false
  if !(h.married && h.adults.length = 2) || h.spouseClaimant == "higher" then hi
  else if h.spouseClaimant == "lower" then computeClaim h true true
  else
    [computeClaim h true false, computeClaim h false true, computeClaim h true true].foldl
      (fun best r => if total r < total best then r else best) hi

/- The scan's households (global/monoscan/evidence.md): business income 962 315 -> 1 061 130 beside a spouse's salary
1 710 911, two children. The claimed spouse deduction moves from one spouse to the other as the incomes cross; with
the election the couple's tax no longer falls (it was 56 212 -> 40 500 with the larger income always claiming). -/
private def scanHh (se : Int) : Household :=
  { id := "m", year := 2025, married := true, children := [{ age := 5 }, { age := 12 }],
    adults := [{ age := 40, wages := 0, selfEmployment := se, pension := 0 },
               { age := 38, wages := 1710911, selfEmployment := 0, pension := 0 }] }
private def tot (r : Result) : Int := r.incomeTax + r.fukkoTotal + r.localTax
#guard tot (compute (scanHh 962315)) ≤ tot (compute (scanHh 1061130))
#guard tot (compute (scanHh 1061130)) ≤ min (tot (computeClaim (scanHh 1061130) false)) (tot (computeClaim (scanHh 1061130) true))

end JpTax
