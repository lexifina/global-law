import re, sys, pathlib
D = pathlib.Path.home() / "cmp/loop/jp/lean/JpTax"

def sub(path, old, new, count=1):
    p = D / path
    t = p.read_text()
    n = t.count(old)
    if n < 1:
        sys.exit(f"MISSING in {path}: {old[:80]!r}")
    if count == 1 and n != 1:
        sys.exit(f"AMBIGUOUS ({n}) in {path}: {old[:80]!r}")
    p.write_text(t.replace(old, new))

# Extras imports Tax+Social; Local imports Extras
sub("Extras.lean", "import JpTax.Local\nimport JpTax.Social", "import JpTax.Tax\nimport JpTax.Social")
sub("Local.lean", "import JpTax.Tax\n", "import JpTax.Tax\nimport JpTax.Extras\n")

# ---- Local.lean
sub("Local.lean", "  declGains : Int := 0      -- listed-share gains declared separately (附則第35条の2の2)\n",
    "  declGains : Int := 0      -- listed-share gains declared separately (附則第35条の2の2)\n"
    "  extraDed : Int := 0       -- loop: 医療費 / 生命保険料 / 地震保険料 / 寡婦 (住民税 amounts)\n"
    "  furusato : Int := 0       -- loop: 特例控除対象寄附金 (ふるさと納税)\n"
    "  oneStop : Bool := false   -- loop: 申告特例 (ワンストップ)\n"
    "  kisoIT : Int := 480000    -- loop: the 所得税 基礎控除 (for the 人的控除差調整額)\n"
    "  jutakuResidual : Int := 0 -- loop: 住宅借入金等特別控除 left over by the 所得税\n"
    "  taxableIT : Int := 0      -- loop: 所得税 課税総所得金額\n")
sub("Local.lean", "  shinrin : Int           -- 森林環境税 1,000\n",
    "  shinrin : Int           -- 森林環境税 1,000\n"
    "  jutakuPref : Int := 0\n  jutakuMuni : Int := 0\n  donPref : Int := 0\n  donMuni : Int := 0\n")
sub("Local.lean", "let ded := i.social + i.ideco + i.personal + kisoLocal g",
    "let ded := i.social + i.ideco + i.personal + kisoLocal g + i.extraDed")
sub("Local.lean",
    "  let pref := if notTaxed then 0 else trunc100 (afterRelief p tot excess)\n"
    "  let muni := if notTaxed then 0 else trunc100 (afterRelief m tot excess)\n",
    "  let pref0 := if notTaxed then 0 else afterRelief p tot excess\n"
    "  let muni0 := if notTaxed then 0 else afterRelief m tot excess\n"
    "  -- loop: 附則第5条の4の2 (住宅借入金等特別税額控除), then 第37条の2 / 第314条の7 (寄附金税額控除)\n"
    "  let jl := jutakuLocal i.jutakuResidual i.taxableIT i.kisoIT\n"
    "  let jP := min jl.1 pref0\n"
    "  let jM := min jl.2 muni0\n"
    "  let dl := donationLocal { furusato := i.furusato, oneStop := i.oneStop, total := g, base := base,\n"
    "      jintekiSa := choseiH i.chosei, kisoIT := i.kisoIT } (prefRaw - cPref) (muniRaw - cMuni)\n"
    "  let dP := min dl.1 (pref0 - jP)\n"
    "  let dM := min dl.2 (muni0 - jM)\n"
    "  let pref := trunc100 (pref0 - jP - dP)\n"
    "  let muni := trunc100 (muni0 - jM - dM)\n")
sub("Local.lean", "    shinrin := if kinto then 1000 else 0 }",
    "    shinrin := if kinto then 1000 else 0, jutakuPref := jP, jutakuMuni := jM, donPref := dP, donMuni := dM }")
t = (D / "Local.lean").read_text()
i = t.index("theorem localTax_pref_nonneg")
j = t.index("end JpTax", i)
t = t[:i] + "theorem localTax_pref_nonneg (i : LocalIn) : 0 ≤ (localTax i).pref := by\n  unfold localTax\n  exact trunc100_nonneg _\n\n" + t[j:]
(D / "Local.lean").write_text(t)

# ---- Person.lean
sub("Person.lean", "  declGains : Int := 0       -- listed-share gains declared (措置法第37条の11)\n",
    "  declGains : Int := 0       -- listed-share gains declared (措置法第37条の11)\n"
    "  aoiro : Int := 0           -- loop: 青色申告特別控除 claimed (措置法第25条の2)\n"
    "  shokibo : Int := 0         -- loop: 小規模企業共済掛金 (第75条第2項第1号)\n"
    "  medical : Int := 0         -- loop: 医療費 paid, net of reimbursements (第73条)\n"
    "  otc : Int := 0             -- loop: 特定一般用医薬品等購入費 (措置法第41条の17)\n"
    "  selfMed : Bool := false    -- loop: choose セルフメディケーション instead of 第73条\n"
    "  lifeIns : List Int := []   -- loop: 新生命保険料 [一般, 介護医療, 個人年金] (第76条)\n"
    "  earthquake : Int := 0      -- loop: 地震保険料 (第77条)\n"
    "  widow : Bool := false      -- loop: 寡婦 (第2条第1項第30号, 第80条)\n"
    "  furusato : Int := 0        -- loop: 特例控除対象寄附金 (ふるさと納税)\n"
    "  oneStop : Bool := false    -- loop: ワンストップ特例 (no 所得税 deduction; 申告特例控除額 instead)\n"
    "  housingBalance : Int := 0  -- loop: 住宅借入金等の年末残高 (措置法第41条)\n"
    "  housingLimit : Int := 0    -- loop: its 借入限度額\n"
    "  npo : Int := 0             -- loop: 認定NPO法人等への寄附 (措置法第41条の18の3)\n"
    "  npoAsCredit : Bool := false -- loop: 税額控除 instead of 第78条\n")
sub("Person.lean", "  loc : LocalOut\n  deriving Repr, Inhabited\n",
    "  loc : LocalOut\n  dMed : Int := 0\n  dLife : Int := 0\n  dQuake : Int := 0\n  dKafu : Int := 0\n"
    "  jutakuUsed : Int := 0\n  npoCr : Int := 0\n  deriving Repr, Inhabited\n")
t = (D / "Person.lean").read_text()
i = t.index("def incomeParts"); j = t.index("(k, a1 + a2, n, sogo)", i)
seg = t[i:j].replace("p.business", "(p.business - aoiroKojo p.aoiro p.business)")
(D / "Person.lean").write_text(t[:i] + seg + t[j:])
sub("Person.lean", "    hitorioyaFather := p.singleParent && !p.singleParentMother && decide (g ≤ 5000000),",
    "    hitorioyaFather := (p.singleParent && !p.singleParentMother && decide (g ≤ 5000000)) ||\n"
    "      (p.widow && !p.singleParent && decide (g ≤ 5000000)),")
sub("Person.lean", "  let dKifu := kifukinKojo p.donations g\n",
    "  let deductibleDon := p.donations + (if p.oneStop then 0 else pos p.furusato)\n"
    "  let dKifu := kifukinKojo (deductibleDon + (if p.npoAsCredit then 0 else pos p.npo)) g\n"
    "  let dMed := if p.selfMed then selfMedKojo p.otc else iryohiKojo p.medical g\n"
    "  let dLife := lifeKojo p.lifeIns\n"
    "  let dQuake := jishinKojo p.earthquake\n"
    "  let dKafu := if p.singleParent then 0 else kafuKojo p.widow g\n")
sub("Person.lean", "  let total := p.socialIns + p.ideco + dKifu +",
    "  let total := p.socialIns + p.ideco + p.shokibo + dMed + dLife + dQuake + dKafu + dKifu +")
sub("Person.lean", "  let kijun := kijunAgg + (tGain + tDiv) * 15 / 100\n",
    "  let kijun0 := kijunAgg + (tGain + tDiv) * 15 / 100\n"
    "  let jCredit := jutakuCredit p.housingBalance p.housingLimit g\n"
    "  let jUsed := min jCredit kijun0\n"
    "  let nCr := if p.npoAsCredit then npoCredit p.npo deductibleDon g (kijun0 - jUsed) else 0\n"
    "  let kijun := kijun0 - jUsed - nCr\n")
sub("Person.lean", "    { sogo := sogo, social := p.socialIns, ideco := p.ideco, personal := personalL,",
    "    { sogo := sogo, social := p.socialIns, ideco := p.ideco + p.shokibo, personal := personalL,\n"
    "      extraDed := dMed + lifeLocal p.lifeIns + jishinLocal p.earthquake +\n"
    "        (if p.singleParent then 0 else kafuLocal p.widow g),\n"
    "      furusato := pos p.furusato, oneStop := p.oneStop, kisoIT := dKiso,\n"
    "      jutakuResidual := jCredit - jUsed, taxableIT := taxable,")
sub("Person.lean", "      exempt295 := p.singleParent && decide (g ≤ 1350000),",
    "      exempt295 := (p.singleParent || p.widow) && decide (g ≤ 1350000),")
sub("Person.lean", "    loc := localTax li }",
    "    loc := localTax li, dMed, dLife, dQuake, dKafu, jutakuUsed := jUsed, npoCr := nCr }")

# ---- Household.lean
sub("Household.lean", "structure Household where\n",
    "/-- loop: per-adult extras (same order as `adults`). -/\n"
    "structure AdultExt where\n"
    "  bonus : Int := 0          -- one December bonus on top of `wages` (給与等; 標準賞与額)\n"
    "  ideco : Int := -1         -- this adult's iDeCo (overrides the household split when ≥ 0)\n"
    "  senjusha : Bool := false  -- 青色事業専従者 (第57条): never a 控除対象配偶者 / not employee-insured\n"
    "  aoiro : Int := 0\n  shokibo : Int := 0\n  medical : Int := 0\n  otc : Int := 0\n  selfMed : Bool := false\n"
    "  lifeIns : List Int := []\n  earthquake : Int := 0\n  widow : Bool := false\n  furusato : Int := 0\n"
    "  oneStop : Bool := false\n  housingBalance : Int := 0\n  housingLimit : Int := 0\n  npo : Int := 0\n"
    "  npoAsCredit : Bool := false\n  deriving Repr, Inhabited\n\n"
    "structure Household where\n")
sub("Household.lean", "  singleParentMother : Bool := true\n  deriving Repr, Inhabited\n",
    "  singleParentMother : Bool := true\n  ext : List AdultExt := []\n"
    "  claimants : List Int := []   -- loop: which adult claims each child (-1: the default, the top earner)\n"
    "  deriving Repr, Inhabited\n")
sub("Household.lean", "  let socials := h.adults.map fun a => social a.wages a.age\n",
    "  let exts := (List.range n).map fun i => h.ext.getD i default\n"
    "  let socials := (List.range n).map fun i =>\n"
    "    let a := h.adults.getD i default\n"
    "    let e := exts.getD i default\n"
    "    if e.senjusha then zeroSocial else socialB a.wages e.bonus a.age\n")
sub("Household.lean", "    { age := a.age, wages := a.wages, business",
    "    { age := a.age, wages := a.wages + (exts.getD i default).bonus, business")
sub("Household.lean", "    decide (a.wages + a.selfEmployment + a.pension < (if a.age ≥ 60 then 1800000 else 1300000))",
    "    decide (a.wages + (h.ext.getD i default).bonus + a.selfEmployment + a.pension <\n"
    "      (if a.age ≥ 60 then 1800000 else 1300000))")
sub("Household.lean", "  let single := n = 1",
    "  let idecos := (List.range n).map fun i =>\n"
    "    let e := exts.getD i default\n"
    "    if e.ideco ≥ 0 then min e.ideco (caps.getD i 0) else idecos.getD i 0\n"
    "  let claimantOf := fun (j : Nat) => let c := h.claimants.getD j (-1); if c < 0 then top else c.toNat\n"
    "  let single := n = 1")
sub("Household.lean",
    "      if h.married && n = 2 && i = top then",
    "      if h.married && n = 2 && i = top && !(exts.getD other default).senjusha then")
sub("Household.lean", "             dependants := if i = top then rels else [] }",
    "             dependants := (rels.zipIdx.filter (fun (_, j) => claimantOf j = i)).map (·.1),\n"
    "             aoiro := e.aoiro, shokibo := e.shokibo, medical := e.medical, otc := e.otc, selfMed := e.selfMed,\n"
    "             lifeIns := e.lifeIns, earthquake := e.earthquake, widow := e.widow, furusato := e.furusato,\n"
    "             oneStop := e.oneStop, housingBalance := e.housingBalance, housingLimit := e.housingLimit,\n"
    "             npo := e.npo, npoAsCredit := e.npoAsCredit }")
sub("Household.lean", "    let p := base.getD i default\n    let other := 1 - i\n",
    "    let p := base.getD i default\n    let other := 1 - i\n    let e := exts.getD i default\n")

# ---- Main.lean
sub("Main.lean", "    singleParentMother := jStr j \"jpSingleParentSex\" \"F\" != \"M\" }",
    "    singleParentMother := jStr j \"jpSingleParentSex\" \"F\" != \"M\",\n"
    "    claimants := (jArr j \"children\").toList.map fun c => jInt c \"claimant\" (-1),\n"
    "    ext := (jArr j \"adults\").toList.map fun a =>\n"
    "      { bonus := jInt a \"bonus\", ideco := jInt a \"ideco\" (-1), senjusha := jBool a \"senjusha\",\n"
    "        aoiro := jInt a \"aoiro\", shokibo := jInt a \"shokibo\", medical := jInt a \"medical\", otc := jInt a \"otc\",\n"
    "        selfMed := jBool a \"selfMed\",\n"
    "        lifeIns := (jArr a \"lifeIns\").toList.map fun x => match x with | .num n => numToInt n | _ => 0,\n"
    "        earthquake := jInt a \"earthquake\", widow := jBool a \"widow\", furusato := jInt a \"furusato\",\n"
    "        oneStop := jBool a \"oneStop\", housingBalance := jInt a \"housingBalance\",\n"
    "        housingLimit := jInt a \"housingLimit\", npo := jInt a \"npo\", npoAsCredit := jBool a \"npoCredit\" } }")
sub("Main.lean", "      (\"basic_kiso\", ji o.dKiso)]),",
    "      (\"basic_kiso\", ji o.dKiso), (\"medical_iryohi\", ji o.dMed), (\"life_seimei\", ji o.dLife),\n"
    "      (\"quake_jishin\", ji o.dQuake), (\"widow_kafu\", ji o.dKafu)]),\n"
    "    (\"housingCredit_jutaku\", ji o.jutakuUsed), (\"npoCredit\", ji o.npoCr),")
sub("Main.lean", "      (\"forestEnvironmentTax_shinrin\", ji o.loc.shinrin)]),",
    "      (\"forestEnvironmentTax_shinrin\", ji o.loc.shinrin),\n"
    "      (\"housingCredit\", ji (o.loc.jutakuPref + o.loc.jutakuMuni)),\n"
    "      (\"donationCredit\", ji (o.loc.donPref + o.loc.donMuni))]),")
print("patched")
