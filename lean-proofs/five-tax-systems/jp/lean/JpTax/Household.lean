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
  unsupported : List String
  deriving Repr

def childRelative (c : Child) : Relative := { age := c.age, income := kyuyoShotoku c.wages }

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

def compute (h : Household) : Result :=
  let n := h.adults.length
  let socials := h.adults.map fun a => social a.wages a.age
  let rentals := splitAmount h.rentalIncome n
  let divs := if h.aggregateDividends then splitAmount h.dividends n else List.replicate n 0
  let declare := !h.aggregateDividends && h.declaredDividends
  let sepDivs := if h.aggregateDividends || declare then List.replicate n 0 else splitAmount h.dividends n
  let declDivs := if declare then splitAmount h.dividends n else List.replicate n 0
  let sepInts := splitAmount h.interest n
  let sepGains := if h.declaredGains then List.replicate n 0 else splitAmount h.capitalGains n
  let declGains := if h.declaredGains then splitAmount h.capitalGains n else List.replicate n 0
  let rels := h.children.map childRelative
  let childUnder23 := rels.any fun d => decide (d.age < 23) && d.fuyo
  let base : List PersonIn := (List.range n).map fun i =>
    let a := h.adults.getD i default
    { age := a.age, wages := a.wages, business := a.selfEmployment, pension := a.pension,
      rental := rentals.getD i 0, dividends := divs.getD i 0, ideco := 0, donations := 0,
      socialIns := (socials.getD i default).total, childUnder23, singleParent := false,
      singleParentMother := h.singleParentMother, spouse := none, dependants := [],
      sepInterest := sepInts.getD i 0, sepDividends := sepDivs.getD i 0, sepGains := sepGains.getD i 0,
      declDividends := declDivs.getD i 0, declGains := declGains.getD i 0 }
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
    let spouse : Option Relative :=
      if h.married && n = 2 && i = top then
        some { age := (h.adults.getD other default).age, income := incomes.getD other 0 }
      else none
    { p with ideco := idecos.getD i 0,
             donations := if i = top then pos h.charitable else 0,
             singleParent := single,
             spouse,
             dependants := if i = top then rels else [] }
  let outs := persons.map person
  let triples := (List.range n).map fun i => (persons.getD i default, outs.getD i default, socials.getD i default)
  let sumO (f : PersonOut → Int) := outs.foldl (fun acc o => acc + f o) 0
  let sepN := sumO (·.sepNational)
  let sepF := sumO (·.sepFukko)
  let sepLocal := sumO (·.sepLocal)
  { persons := triples,
    incomeTax := sumO (·.kijun) + sumO (·.minTax) + sepN,
    fukkoTotal := sumO (·.fukko) + sepF,
    localTax := sumO (·.loc.total) + sepLocal,
    employeeSocial := socials.foldl (fun acc s => acc + s.total) 0,
    benefits := teateYear (h.children.map (·.age)),
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
      (if h.year ≠ 2025 then ["only 令和7年分 (2025) is modelled; the 2025 law was applied"] else []) }

end JpTax
