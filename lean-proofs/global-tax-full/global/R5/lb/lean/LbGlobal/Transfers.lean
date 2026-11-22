import TaxKernel.Global
import R5Common

/-!
# Lebanon 2025: inheritance duty (رسم الانتقال, 4300)

Decree-Law No 146 of 12/06/1959 (فرض رسم انتقال على الأموال المنقولة وغير المنقولة), texts from legiliban.ul.edu.lb
(law id 185602; amended-articles list `AmendedArticles.aspx?lawId=185602`):
* rate table annexed to the law as replaced by **Budget Law 324/2024 art. 50** (OG 7 of 15/02/2024; the 2025 budget,
  Decree 56/2025, leaves the table unchanged): duty by slices of each heir's taxable share, five classes of heirs:
  (1) descendants and spouses, (2) parents, (3) ascendants other than parents, brothers and sisters, (4) uncles, aunts,
  nephews and nieces, (5) all others. Slices (LBP) to 1.8 bn / 3.6 bn / 6 bn / 12 bn / 21 bn / above:
  3-5-7-10-12-12 %, 6-9-12-16-18-18 %, 9-12-16-20-24-24 %, 12-16-21-26-31-36 %, 16-21-27-33-39-45 %.
* art. 9(5) exempt part of each net share as replaced by **Decree 56/2025 art. 23** (2025 budget, OG 11 of 13/03/2025,
  in force on publication; `law/legiliban_budget2025_decree56.txt`): descendants, spouses and parents LBP 2,400 m;
  ascendants other than parents, brothers and sisters 960 m; other heirs 480 m. Before 13/03/2025 (Law 10/2022 wording)
  the amounts were a quarter of these (600 m / 240 m / 120 m): the kernel transfer carries no date, so the amounts in
  force from 13/03/2025 are used (flagged).
Classes from the kernel relation: child, grandchild, spouse -> 1; parent -> 2; sibling -> 3; nieceNephew -> 4;
otherRelative, unrelated, charity -> 5. The art. 9(5) add-ons (disabled child, minor child per year under 18, dependent
spouse and children, capped at 2,400 m) and gifts (art. 16 as changed by Decree 56/2025 art. 24, not read) are not
computed. **Grade A** (dated statute texts read).

# Lebanon 2025: proportional land-registry transfer fee on sales (رسم الفراغ, 4400; pass 3p)

Decree-Law No 20 of 18/12/1939 (legiliban law id 187892) art. 1 as amended: the registration and transfer fees follow
tables 1 and 2 annexed to Decree-Law No 148 of 12/06/1959 (law id 185599, `law/legiliban_dl148_1959.txt`). Table 2,
item 1 (sale of a real right in immovable property, other than waqf and sale with right of redemption; base the value of
the property or right) was **3 %** in 1959; **Budget Law No 10 of 15/11/2022 art. 92** (law id 307720; the new item is
printed as an image on legiliban, `law/legiliban_law10_2022_art92.png`) re-set it at **3 % for Lebanese and 5 % for
non-Lebanese** buyers and repealed contrary texts. Art. 3 of DL 20/1939 as replaced by art. 76 of the same law (from
15/11/2022): for built property the base is the rental value assessed by the built-property tax office x 30 where that
is higher than the price stated (the kernel's `assessed` value stands for it: base = max(price, assessed)).
The Budget Law 324/2024 (law id 330076) and the 2025 budget (Decree 56/2025) do not amend item 1 (searched for the fee's
name in their full texts), so the rates hold for all of 2025.
Buyer's nationality: the 1.x `nationality` field (top level or household; `national` by default); any other value takes
the 5 % rate. A company line is charged 3 % (a Lebanese company presumed; noted). Payer: the purchaser (the decrees read
do not name the payer; the conveyance is registered in the buyer's name): bearer the buying entity.
Fixed registry fees (Budget 2025 art. 32-34) are per act, not booked. **Grade B**: legiliban is the Lebanese
University's database (an unofficial reprint, flagged); the Official Gazette text was not read.
-/

namespace LbGlobal
open TaxKernel TaxKernel.Global R5Common

def intiqalSched (r0 r1 r2 r3 r4 r5 : Int) : Schedule :=
  Schedule.ofUpper [(1800000000, r0), (3600000000, r1), (6000000000, r2), (12000000000, r3), (21000000000, r4)] r5

def intiqal : InheritanceTax :=
  { name := "رسم الانتقال",
    classOf := fun r => match r with
      | .child | .grandchild | .spouse => 0
      | .parent => 1
      | .sibling => 2
      | .nieceNephew => 3
      | _ => 4,
    classes := [{ allowance := 2400000000, sched := intiqalSched 300 500 700 1000 1200 1200 },
                { allowance := 2400000000, sched := intiqalSched 600 900 1200 1600 1800 1800 },
                { allowance := 960000000, sched := intiqalSched 900 1200 1600 2000 2400 2400 },
                { allowance := 480000000, sched := intiqalSched 1200 1600 2100 2600 3100 3600 },
                { allowance := 480000000, sched := intiqalSched 1600 2100 2700 3300 3900 4500 }] }

/-- nationality of the buyer (1.x convention; `national` by default) -/
def lbNationality (g : CanonGlobal) : String :=
  match g.raw.getObjValAs? String "nationality" with
  | .ok s => s
  | .error _ => match g.household.raw.getObjValAs? String "nationality" with
    | .ok s => s
    | .error _ => "national"

/-- DL 148/1959 table 2 item 1 as replaced by Law 10/2022 art. 92: 3 % (Lebanese) / 5 % (non-Lebanese) -/
def rasmFaragh (lebanese : Bool) : TransferDuty :=
  { name := "رسم الفراغ (proportional transfer fee on sales)", sched := Schedule.flat (if lebanese then 300 else 500),
    higherOfAssessed := true }

def rasmFaraghStatute (lebanese : Bool) : String :=
  "DL 20/1939 art. 1, 3 (Law 10/2022 art. 76); DL 148/1959 table 2 item 1 as replaced by Law 10/2022 art. 92: " ++
  (if lebanese then "3 % (Lebanese buyer)" else "5 % (non-Lebanese buyer)")

def transfers : Family :=
  { name := "4300 رسم الانتقال; 4400 رسم الفراغ", covers := [.estate, .transactions],
    run := fun _ g _ =>
      intiqal.charges (g.transfers.filter (·.kind == .inheritance))
        "DL 146/1959 table (Budget Law 324/2024 art. 50), art. 9(5) (Decree 56/2025 art. 23)" ++
      (let leb := g.entity == .company || lbNationality g == "national"
       (rasmFaragh leb).charges g.purchases (rasmFaraghStatute leb)) }

def transfersUnsupported (g : CanonGlobal) : List String :=
  (if g.transfers.any (·.kind == .inheritance) then
    ["inheritance duty: art. 9(5) amounts in force from 13/03/2025 used (a quarter of them before); add-ons for minor, disabled or dependent heirs not computed"] else [])
  ++ (if g.transfers.any (·.kind == .gift) then ["gift duty (art. 16, Decree 56/2025 art. 24) not read; not computed"] else [])
  ++ (if g.entity == .company && g.purchases.any (fun p => (rasmFaragh true).kinds.contains p.kind) then
       ["4400 رسم الفراغ: company buyer charged at the Lebanese rate (3 %); a non-Lebanese company pays 5 % (nationality of a company not an input)"] else [])

-- a child's share of 4,200 m: 1,800 m taxable at 3 % = 54 m
#guard intiqal.tax { kind := .inheritance, value := 4200000000, relation := .child } == 54000000
-- an unrelated heir's 3,080 m: 2,600 m taxable: 1,800 m x 16 % + 800 m x 21 % = 288 m + 168 m
#guard intiqal.tax { kind := .inheritance, value := 3080000000, relation := .unrelated } == 456000000
#guard intiqal.tax { kind := .inheritance, value := 2400000000, relation := .spouse } == 0

-- 12 bn assessed above a 10 bn price: 3 % of 12 bn; a non-Lebanese buyer of 5 bn of land: 5 %
#guard (rasmFaragh true).amount { kind := .home, price := 10000000000, assessed := 12000000000 } == 360000000
#guard (rasmFaragh false).amount { kind := .land, price := 5000000000 } == 250000000

end LbGlobal
