import KrTax.Household

/-!
# The contract output (`~/cmp/shared/CONTRACT.md`)

`incomeTax` = national 소득세 (결정세액 of each spouse + 14 % 분리과세 withholding on 이자·배당) − 근로장려금 −
자녀장려금 (refundable, so it can be negative); `localIncomeTax` = 개인지방소득세 (10 %); `employeeSocial` = the four
employee premiums; `benefits` = 아동수당 (100,000 won a month for each child under 8). No surtaxes: 농어촌특별세 falls
only on reliefs this model does not grant.
-/

namespace KrTax
open TaxKernel Lean

def personJson (p : PersonIn) (o : PersonOut) : Json :=
  Json.mkObj [
    ("age", toJson p.age), ("totalWages_chongGeubyeo", toJson p.wages),
    ("earnedDeduction_47", toJson o.earnedDed), ("earnedIncome", toJson o.earnedInc),
    ("pensionIncome", toJson o.pensionInc), ("businessIncome", toJson p.biz),
    ("financialSeparate_14pct", toJson o.finSeparate), ("financialComprehensive_withGrossUp", toJson o.finInc),
    ("grossUp_17_3", toJson o.grossUp), ("comprehensiveIncome", toJson o.comprehensive),
    ("personalDeductions_50_51", toJson o.personalDed), ("pensionPremiumDeduction_51_3", toJson o.pensionPremDed),
    ("specialIncomeDeduction_52", toJson o.specialDed), ("taxableIncome", toJson o.taxable),
    ("calculatedTax_55_62", toJson o.calcTax), ("dividendCredit_56", toJson o.dividendCredit),
    ("earnedIncomeCredit_59", toJson o.earnedCr), ("childCredit_59_2", toJson o.childCr),
    ("pensionAccountCredit_59_3", toJson o.pensionAcctCr), ("donationCredit_59_4", toJson o.donationCr),
    ("standardCredit_59_4_9", toJson o.stdCr), ("usedStandardCredit", toJson o.usedStandard),
    ("determinedTax", toJson o.determined), ("separateWithholding", toJson o.sepTax),
    ("localIncomeTax", toJson (localIncomeTax o)),
    ("social", Json.mkObj [("pension", toJson o.soc.pension), ("health", toJson o.soc.health),
      ("longTermCare", toJson o.soc.ltc), ("employment", toJson o.soc.employment),
      ("healthOnOtherIncome_71", toJson o.soc.healthOther)])]

def unsupportedOf (c : Canon) : List String :=
  (if c.rentalIncome ≠ 0 then ["rentalIncome: 주택임대소득 (분리과세 option, 필요경비율) not modelled; counted only in the 장려금 총소득"] else [])
  ++ (if c.capitalGains ≠ 0 then ["capitalGains: listed shares of a non-major shareholder are not taxed (ITA §94①3가, 대주주 only); taken as such"] else [])
  ++ (if c.adults.any (fun a => a.selfEmployment ≠ 0) then ["selfEmployment: read as 사업소득금액 (net, books); 지역가입자 health premium on income only"] else [])
  ++ ["assets assumed below the 장려금 asset limits (STA §100의3①4)", "부녀자공제 (§51①3) needs the taxpayer's sex: not given",
      "보험료·의료비·교육비 세액공제, 신용카드 소득공제, 월세세액공제: no inputs"]
  ++ (if (c.year = 2022 ∨ c.year = 2023) ∧ c.children.any (fun k => k.age ≤ 1) then
      ["아동수당 추가지급 for children under 2 (아동수당법 §4⑤, 법률 제18579호; 부칙 제4조: children born from 2022-01-01; 부칙 제6조: "
        ++ "through 2023 an amount set by 보건복지부 고시 (2022: 30만–50만원; 2023: 30만원 이상, 법률 제19455호)) not included: the 고시 "
        ++ "was not located on law.go.kr"] else [])

/-- The household with the input's options. -/
def computeHh (c : Canon) : HhOut :=
  let std := match c.str? "krStandard" with
    | some "itemise" => some false
    | some "standard" => some true
    | _ => none
  let inc := !(c.bool? "krNoIncentives" |>.getD false)
  match c.str? "krClaimant" with
  | some "best" =>
    let a := household c 0 std inc
    let b := household c 1 std inc
    if b.net c.gross > a.net c.gross then b else a
  | _ => household c ((c.int? "krClaimant").getD 0).toNat std inc

def out (c : Canon) : Out :=
  let h := computeHh c
  let taxable := (h.persons.map (fun (_, o) => o.taxable)).foldl (· + ·) 0
  let ct := (h.persons.map (fun (_, o) => o.calcTax)).foldl (· + ·) 0
  Out.make c "KR" "KRW" h.incomeTax (localIncomeTax := h.localTax) (employeeSocial := h.social)
    (benefits := h.childAllowance)
    (detail := [Out.dStr "taxYear" (s!"{c.year} (귀속 {c.year}, calendar year); Seoul resident; 장려금 claimed May {c.year + 1}"),
      Out.d "taxableIncome" taxable, Out.d "taxBeforeCredits" ct,
      Out.d "earnedIncomeTaxCredit_geunroJangryeogeum" h.eitc, Out.d "childTaxCredit_janyeoJangryeogeum" h.ctc,
      Out.d "householdKind_0single_1oneEarner_2dualEarner" h.kind, Out.d "earnedTotal_chongGeubyeoDeung" h.earnedTotal,
      Out.d "totalIncome_chongSodeuk" h.totalIncome, Out.d "childAllowance_adongSudang" h.childAllowance,
      ("persons", Json.arr (h.persons.map (fun (p, o) => personJson p o)).toArray)])
    (unsupported := unsupportedOf c)

/-- **`--oecd` (convention mode only; never the statute default).** The OECD Taxing Wages conventions for Korea found
in FINDINGS F1, F6 and F7 (tests round 1, `~/cmp20/improve-emerging/IMPROVE.md`): the OECD's Korean families have two
children under 8 cared for at home (its CTGG of 4,800,000 = 2 × (아동수당 100,000 + 양육수당 100,000) × 12, and no
자녀세액공제), so a child aged 8 to 11 is read as 7 and `krHomeCare` is set; and the OECD's social-insurance arithmetic
(`socialOecd`: no 1,000-won truncation of the 기준소득월액, 장기요양 at 12.95 % of the health premium). Statute mode (no
flag) keeps the household's children and the statute (아동수당법 §4①, 소득세법 §59의2①, 국민연금법 시행령 §5①). -/
def oecdCanon (c : Canon) : Canon :=
  let raw := (c.raw.setObjVal! "krConvention" (Json.str "oecd")).setObjVal! "krHomeCare" (Json.bool true)
  { c with raw := raw,
           children := c.children.map (fun k => if 8 ≤ k.age ∧ k.age ≤ 11 then { k with age := 7 } else k) }

def country : Country :=
  { code := "KR", name := "South Korea (national + Seoul 개인지방소득세)", currency := "KRW", year := "2025",
    compute := out, computeWith := fun args c => if args.contains "--oecd" then out (oecdCanon c) else out c }

end KrTax
