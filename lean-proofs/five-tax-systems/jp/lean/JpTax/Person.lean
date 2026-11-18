import JpTax.Local
import JpTax.Social

/-!
# The income tax and the 住民税 of one person (所得税法第21条, the order of the computation)

第21条第1項: 一 classify income and compute each kind; 二 the 総所得金額 (第22条); 三 subtract the 所得控除 to get the
課税総所得金額 (第89条第2項); 四 apply the rate (第89条第1項); 五 subtract the 配当控除 (第92条).
-/

namespace JpTax

/-- What one adult has, after the household has been split into persons. -/
structure PersonIn where
  age : Int
  wages : Int            -- 給与等の収入金額
  business : Int         -- 事業所得の金額 (net profit, 白色申告: no 青色申告特別控除)
  pension : Int          -- 公的年金等の収入金額
  rental : Int           -- 不動産所得の金額 (net)
  dividends : Int        -- 配当所得 taxed with the other income (総合課税), else 0
  ideco : Int            -- 小規模企業共済等掛金 (iDeCo)
  donations : Int        -- 特定寄附金
  socialIns : Int        -- 社会保険料 paid (the employee contributions)
  childUnder23 : Bool    -- has an 扶養親族 under 23 (措置法第41条の3の11第1項)
  singleParent : Bool    -- ひとり親 (第2条第1項第31号), before the income test
  singleParentMother : Bool
  spouse : Option Relative   -- the spouse this person claims (配偶者控除 / 配偶者特別控除)
  dependants : List Relative -- the relatives this person claims (扶養控除, 特定親族特別控除)
  sepInterest : Int := 0     -- this person's 一般利子等 (措置法第3条, 源泉分離課税)
  sepDividends : Int := 0    -- listed-share dividends left to 確定申告不要 (措置法第8条の5)
  sepGains : Int := 0        -- listed-share gains in a 特定口座 with withholding (措置法第37条の11の5)
  declDividends : Int := 0   -- listed-share dividends declared under 申告分離課税 (措置法第8条の4)
  declGains : Int := 0       -- listed-share gains declared (措置法第37条の11)
  deriving Repr, Inhabited

structure PersonOut where
  kyuyo : Int            -- 給与所得 (別表第五 / 第28条)
  adjust : Int           -- 所得金額調整控除
  nenkin : Int           -- 公的年金等に係る雑所得
  sogo : Int             -- 総所得金額 (the 合計所得金額 adds declared listed-share income: `gokei`)
  dSocial : Int
  dIdeco : Int
  dKifukin : Int
  dHitorioya : Int
  dHaigusha : Int
  dTokubetsu : Int
  dFuyo : Int
  dTokuteiShinzoku : Int
  dKiso : Int
  taxable : Int          -- 課税総所得金額
  sanshutsu : Int        -- 第89条
  haito : Int            -- 配当控除 (yen, as taken)
  kijun : Int            -- 所得税 on the 総所得金額 after 配当控除
  declTaxable : Int      -- 上場株式等に係る課税譲渡所得等 + 課税配当所得等 (declared, after the leftover deductions)
  minTax : Int           -- 措置法第41条の19 (基準所得金額 above 330,000,000 yen)
  fukko : Int            -- 復興特別所得税 on kijun + minTax
  national : Int         -- 所得税 + 復興特別所得税 declared, cut to 100 yen
  sepNational : Int      -- 15 % withheld on interest, dividends, gains
  sepFukko : Int         -- 0.315 % withheld with it
  sepLocal : Int         -- 利子割, 配当割, 株式等譲渡所得割 (5 %)
  loc : LocalOut
  deriving Repr, Inhabited

/-- The 総所得金額 and its parts. -/
def incomeParts (p : PersonIn) : Int × Int × Int × Int :=
  let k := kyuyoShotoku p.wages
  let a1 := adjust1 p.wages p.childUnder23
  -- 公的年金等控除: "公的年金等に係る雑所得以外の合計所得金額", computed without the pension (and so without 第2項)
  let other := pos (pos (k - a1) + p.business + p.rental + p.dividends) + pos p.declDividends + pos p.declGains
  let n := nenkinZatsu p.pension other (decide (p.age ≥ 65))
  let a2 := adjust2 (k - a1) n
  let kAfter := pos (k - a1 - a2)
  -- 第69条 損益通算: business and rental losses come off the other income; a net loss leaves nil (第70条 carry-forward
  -- not modelled)
  let sogo := pos (kAfter + n + p.business + p.rental + p.dividends)
  (k, a1 + a2, n, sogo)

/-- Counts for the 住民税 tables and limits. -/
def choseiFacts (p : PersonIn) (g : Int) : ChoseiFacts :=
  let spouseKojo := match p.spouse with
    | some s => decide (s.income ≤ douitsuLimit ∧ g ≤ 10000000)
    | none => false
  let spouseSpecial := match p.spouse with
    | some s => if s.income > douitsuLimit ∧ s.income ≤ 1330000 ∧ g ≤ 10000000 then some s.income else none
    | none => none
  let ks := p.dependants.filter (·.kojoTaisho)
  let tok := (ks.filter (·.tokutei)).length
  let roj := (ks.filter (·.rojin)).length
  { g, spouseKojo, spouseOld := (match p.spouse with | some s => decide (s.age ≥ 70) | none => false),
    spouseSpecialIncome := spouseSpecial,
    fuyoIppan := (ks.length : Int) - tok - roj, fuyoTokutei := tok, fuyoRojin := roj,
    hitorioyaFather := p.singleParent && !p.singleParentMother && decide (g ≤ 5000000),
    hitorioyaMother := p.singleParent && p.singleParentMother && decide (g ≤ 5000000) }

def sumBy (l : List Relative) (f : Relative → Int) : Int := l.foldl (fun acc d => acc + f d) 0

/-- 措置法第3条第1項, 第8条の5 (with 第9条の3), 第37条の11 and 第37条の11の4, with 復興財源確保法第28条: 15.315 % withheld at
source, cut to the yen on the whole (同法第31条第2項); returns (所得税 15 %, 復興特別所得税 the rest). -/
def separate (x : Int) : Int × Int :=
  let x := pos x
  let total := x * 15315 / 100000
  let it := x * 15 / 100
  (it, total - it)

/-- **措置法第41条の19第1項** (from 令和7年分): "その年分の基準所得金額が三億三千万円を超えるもの...については、当該超える
部分の金額の百分の二十二・五に相当する金額からその年分の基準所得税額を控除した金額に相当する所得税を課する". 基準所得金額
(第2項): the 総所得金額 etc. computed as if 確定申告不要 (第8条の5) were not used, plus listed-share dividends and gains;
deposit interest under 第3条 is not in it, and its tax is not in the 基準所得税額 (第3項第1号). -/
def minimumTax (kijunShotoku kijunZei : Int) : Int :=
  pos ((kijunShotoku - 330000000) * 225 / 1000 - kijunZei)

/-- 合計所得金額 (所得税法第2条第1項第30号), read with 措置法第8条の4第3項第1号 and 第37条の11第6項 (第37条の10第6項第1号):
the separately declared listed-share dividends and gains count in it. -/
def gokei (p : PersonIn) (sogo : Int) : Int := sogo + pos p.declDividends + pos p.declGains

def person (p : PersonIn) : PersonOut :=
  let (k, adj, n, sogo) := incomeParts p
  let g := gokei p sogo
  let spouseOld := match p.spouse with | some s => decide (s.age ≥ 70) | none => false
  let sIncome := match p.spouse with | some s => some s.income | none => none
  let dHaigusha := match sIncome with | some s => haigushaKojo g s spouseOld | none => 0
  let dTokubetsu := match sIncome with | some s => haigushaTokubetsu g s | none => 0
  let dFuyo := sumBy p.dependants fuyoKojo
  let dTS := sumBy p.dependants tokuteiShinzokuKojo
  let dHitori := hitorioyaKojo p.singleParent g
  let dKifu := kifukinKojo p.donations g
  let dKiso := kisoKojo g
  let total := p.socialIns + p.ideco + dKifu + dHitori + dHaigusha + dTokubetsu + dFuyo + dTS + dKiso
  let taxable := trunc1000 (sogo - total)
  -- 第87条第2項 read with 措置法第8条の4第3項第3号 and 第37条の11第6項: deductions the 総所得金額 cannot absorb come off the
  -- declared listed-share gains, then the declared dividends (the order of the 申告書 第三表), each base cut to 1,000 yen
  let left := pos (total - sogo)
  let tGain := trunc1000 (pos p.declGains - left)
  let tDiv := trunc1000 (pos p.declDividends - pos (left - pos p.declGains))
  let san := tax89 taxable
  -- 第92条 read with 措置法第8条の4第3項第4号: the 1,000万 test on 課税総所得金額 plus 課税配当所得等
  let kijunAgg := afterHaito san (taxable + tDiv) p.dividends
  -- 措置法第8条の4第1項, 第37条の11第1項: 15 % of the declared bases
  let kijun := kijunAgg + (tGain + tDiv) * 15 / 100
  let (iN, iF) := separate p.sepInterest
  let (dN, dF) := separate p.sepDividends
  let (gN, gF) := separate p.sepGains
  let minT := minimumTax (g + pos p.sepDividends + pos p.sepGains) (kijun + dN + gN)
  -- 住民税
  let dHaiL := match sIncome with | some s => haigushaLocal g s spouseOld | none => 0
  let dTokL := match sIncome with | some s => tokubetsuLocal g s | none => 0
  let personalL := hitorioyaLocal p.singleParent g + dHaiL + dTokL + sumBy p.dependants fuyoLocal +
    sumBy p.dependants tokuteiShinzokuLocal
  let nCount : Int :=
    (match p.spouse with | some s => if s.income ≤ douitsuLimit then 1 else 0 | none => 0) +
    ((p.dependants.filter (fun d => d.fuyo && (decide (d.age < 16) || d.kojoTaisho))).length : Int)
  let li : LocalIn :=
    { sogo := sogo, social := p.socialIns, ideco := p.ideco, personal := personalL,
      chosei := choseiFacts p g, n := nCount,
      exempt295 := p.singleParent && decide (g ≤ 1350000), haito := p.dividends,
      declDividends := p.declDividends, declGains := p.declGains }
  { kyuyo := k, adjust := adj, nenkin := n, sogo := sogo,
    dSocial := p.socialIns, dIdeco := p.ideco, dKifukin := dKifu, dHitorioya := dHitori,
    dHaigusha := dHaigusha, dTokubetsu := dTokubetsu, dFuyo := dFuyo, dTokuteiShinzoku := dTS,
    dKiso := dKiso, taxable := taxable, sanshutsu := san, haito := san - kijunAgg, kijun := kijun,
    declTaxable := tGain + tDiv, minTax := minT, fukko := fukko (kijun + minT), national := nationalPayable (kijun + minT),
    sepNational := iN + dN + gN, sepFukko := iF + dF + gF,
    sepLocal := pos p.sepInterest * 5 / 100 + pos p.sepDividends * 5 / 100 + pos p.sepGains * 5 / 100,
    loc := localTax li }

end JpTax
