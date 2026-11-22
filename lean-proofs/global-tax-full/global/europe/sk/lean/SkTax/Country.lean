import SkTax.Household

/-!
# `sktax`: the contract (canonical household in, one output line out)

Amounts in the contract are whole euros; the model computes in cents and reports euros rounded by § 47 (and the cent
values in `detail`). Slovak-only optional input fields:
* per adult: `skReceipts` (§ 6 ods. 1, 2 receipts, €), `skExpenses` (actual expenses, €; without it the § 6 ods. 10
  paušálne výdavky 60 % up to 20 000 € are used); without `skReceipts`, `selfEmployment` is the profit before
  contributions and also stands for the receipts; `skDds` (§ 11 ods. 8 contributions);
* per child: `skBirthMonth` (1–12), `skFromMonth` (1–12, e.g. the month of birth), `skStudent` (bool, for the prídavok),
  `skSchoolEntry` (bool: the child first starts the first grade this year, ZPD § 8 ods. 1 písm. b): +110 €);
* per household: `skSpouseEligible` (bool; default: married with a child under 18, § 11 ods. 4 písm. a)),
  `skBonusBy` (0/1: the adult claiming the bonus; default the better one), `skDivProfitYear` (the profit year a
  dividend is paid from; ≥ 2025 → 7 %, otherwise 10 %, § 52zzzb ods. 5), `skGainsExempt` (bool: listed securities
  held over a year, § 9 ods. 1 písm. k)).
Options: `--statute-taper` applies § 33 ods. 8 and 11 as worded on 1. 1. 2025 (the ods. 11 reduction on the claimant's
own base even when ods. 8 pooling is used); `--eurostat` (convention, Eurostat earn_net ESMS 3.4: "Income tax and social
security contributions parameters refer to the beginning of the fiscal year, i.e. changes occurring later during the year
are ignored"): § 33 ods. 8 and 11 as in force on 1. 1. 2025 (`zdp595_20250101`; the "navýšený základ dane" wording
appears only from the 15. 3. 2025 version), i.e. the same reading as `--statute-taper`; no other mid-year change of a
§ 11/§ 15/§ 33 parameter was found in the dated ZDP versions held (20250315, 20250401, 20250701, 20251201); ZSP/ZZP
mid-year versions are not held. Family allowance: the prídavok (ZPD § 8 ods. 1) is 60 € for every age 6-11 (no age
variation); the 110 € increase depends on the first school start, an event, not an age, so it is not added; `--school-entry-at-6` (convention, not statute: a child aged 6 at the end of
the year is taken to start the first grade that year, as Eurostat's earn_nt_net 2025 households do; without it the
increase needs `skSchoolEntry`, since the statute ties it to the actual school start, not to an age); the default is the text in force from 15. 3. 2025, which § 52zzzd applies to
the whole 2025 return (ods. 11 also on the "navýšený základ dane"), as Finančná správa computes it (FINDINGS F3).
-/

namespace SkTax
open TaxKernel Lean

def arrAt (j : Json) (k : String) (i : Nat) : Json :=
  match j.getObjVal? k with
  | .ok (.arr a) => a.getD i Json.null
  | _ => Json.null

def jInt? (j : Json) (k : String) : Option Int :=
  match j.getObjVal? k with
  | .ok (.num n) => some (numToInt n)
  | _ => none

def jBool? (j : Json) (k : String) : Option Bool :=
  match j.getObjVal? k with
  | .ok (.bool b) => some b
  | _ => none

def eur (x : Int) : Int := 100 * x

/-- The tax year: 2022-2025 are modelled (`years.json`); other years are computed with the nearest one. -/
def yearOf (c : Canon) : Nat := max 2022 (min 2025 c.year)

def toPerson (c : Canon) (i : Nat) (a : Adult) : Person :=
  let r := arrAt c.raw "adults" i
  let (rec, prof) := match jInt? r "skReceipts" with
    | some rc =>
      let ex := match jInt? r "skExpenses" with
        | some e => eur e
        | none => min (pctD (pos (eur rc)) pausalPct) pausalCap
      (eur rc, eur rc - ex)
    | none => (pos (eur a.selfEmployment), eur a.selfEmployment)
  { wages := eur a.wages, receipts := rec, profit := prof, pension := eur a.pension,
    dds := eur ((jInt? r "skDds").getD 0), year := yearOf c }

def toKids (c : Canon) (schoolAt6 : Bool := false) : List Kid :=
  c.children.zipIdx.map fun (k, i) =>
    let r := arrAt c.raw "children" i
    { age := k.age, birthMonth := (jInt? r "skBirthMonth").getD 0, fromMonth := (jInt? r "skFromMonth").getD 1,
      student := (jBool? r "skStudent").getD false,
      schoolEntry := (jBool? r "skSchoolEntry").getD (schoolAt6 && k.age == 6) }

def run (args : List String) (c : Canon) : HhOut × List Person :=
  let ps0 := c.adults.zipIdx.map fun (a, i) => toPerson c i a
  let n := ps0.length
  -- investment income: equal shares for a couple (§ 4 ods. 8), else adult 0
  let share (x : Int) (i : Nat) : Int :=
    if n == 2 && c.married then (if i == 0 then half1 x else half2 x) else (if i == 0 then x else 0)
  let gainsExempt := (c.bool? "skGainsExempt").getD false
  let ps := ps0.zipIdx.map fun (p, i) =>
    { p with rental := eur (share c.rentalIncome i),
             gains := if gainsExempt then 0 else eur (share c.capitalGains i),
             dds := if i == 0 then p.dds + eur c.pensionContributions else p.dds }
  let kids := toKids c (args.contains "--school-entry-at-6")
  let minor := kids.any fun k => decide (k.age < 18)
  let o : Opts :=
    { married := c.married, spouseEligible := (c.bool? "skSpouseEligible").getD (c.married && minor),
      bonusBy := (c.int? "skBonusBy").map Int.toNat, pooledTaper := !(args.contains "--statute-taper" || args.contains "--eurostat"),
      divRate := if yearOf c ≤ 2024 then divRateFor (yearOf c)
        else if 2025 ≤ (c.int? "skDivProfitYear").getD 2024 then divRateNew else divRateOld,
      year := yearOf c }
  (household ps kids (eur c.interest) (eur c.dividends) o, ps)

def toEur (x : Int) : Int := rh x 100

def personJson (x : Person × PersonOut × TaxOut) : Json :=
  let (_, p, t) := x
  Json.mkObj [("zd5_cents", toJson p.zd5), ("zd6_cents", toJson p.zd6), ("ncz_cents", toJson t.ncz),
    ("nczSpouse_cents", toJson t.nczSp), ("baseA_cents", toJson t.baseA), ("baseB_cents", toJson t.baseB),
    ("taxA_cents", toJson t.taxA), ("taxB_cents", toJson t.taxB), ("eeSocial_cents", toJson p.eeSocial),
    ("eeHealth_cents", toJson p.eeHealth), ("seSocial_cents", toJson p.seSocial), ("seHealth_cents", toJson p.seHealth),
    ("otherHealth_cents", toJson p.otherHealth)]

def outWith (args : List String) (c : Canon) : Out :=
  let (h, _) := run args c
  Out.make c "SK" "EUR" (toEur h.incomeTax) (employeeSocial := toEur h.contributions) (benefits := toEur h.pridavok)
    (detail := [Out.d "taxableIncome" (toEur h.taxable), Out.d "taxBeforeCredits" (toEur h.taxBeforeBonus),
      Out.d "taxBonus" (toEur h.bonus), Out.d "bonusBy" h.bonusBy, Out.d "withheldFinal" (toEur h.withheld),
      Out.d "incomeTax_cents" h.incomeTax, Out.d "taxBeforeBonus_cents" h.taxBeforeBonus,
      Out.d "taxable_cents" h.taxable, Out.d "bonus_cents" h.bonus, Out.d "contributions_cents" h.contributions,
      Out.d "pridavok_cents" h.pridavok, ("persons", Json.arr (h.persons.map personJson).toArray)])
    (unsupported := ["SZČO contributions in steady state (this year's income stands for last year's)",
      "tax losses and their carry-forward (§ 30) not modelled; a negative business base is set to 0",
      "prídavok: the príplatok k prídavku (§ 8 ods. 2) not modelled; the 110 € school-entry increase (§ 8 ods. 1 písm. b)) only with skSchoolEntry or --school-entry-at-6",
      "§ 33 ods. 9 (90 % domestic income) assumed met; § 11 ods. 4 eligibility via skSpouseEligible"] ++
      (if yearOf c ≤ 2024 then ["tax year " ++ toString (yearOf c) ++ ": § 11, § 15, § 33/§ 52zzn/§ 52zzp, prídavok, employee contributions and the dividend rate are year-specific (dated texts in refs/slovlex); the social ceiling uses the ŠÚ average wage of t-2 (no dated legal text held); SZČO bases, the § 6 ods. 10 / § 15 písm. a) bod 2 business amounts and the bonus meal-subsidy exclusion use 2025 rules"] else []))

def country : Country :=
  { code := "SK", name := "Slovakia", currency := "EUR", year := "2025", compute := outWith [],
    computeWith := outWith }

end SkTax
