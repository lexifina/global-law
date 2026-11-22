import MhGlobal.Pit

/-!
# Marshall Islands 2025: tax on gross revenues (5113), no tax on business profits, non-resident tax on services

Source: Income Tax Act 1989 (48 MIRC Ch. 1), RMI Nitijela consolidation "Amended By ... P.L. 2024-14, P.L. 2025-34"
(`cmp20/world/B14-pacific/mh/law/1989-0050_5.txt`); Net Profit Tax Act 2025 (48 MIRC Ch. 7, `2025-0038A_1.txt`).
* **§ 109**: "$80 per year upon that portion of the amount of gross revenues ... which does not exceed $10,000 per year;
  and ... three percent (3%) per year upon that portion ... in excess of $10,000" (P.L. 1991-134): `grt`, booked as
  5113 (a gross-receipts tax) as for the FSM.
* **Net Profit Tax Act 2025 § 705** (16 % net profit tax) **§ 749 (2)**: "This Chapter shall apply to tax years
  commencing on or after October 1, 2026": no tax on business profits in 2025 (cited absence).
* **§ 117**: "a non-resident tax of ten percent (10%) on the gross income earned by every non-resident person in respect
  of services provided ... relating to any client in the Marshall Islands", withheld by the client (§ 118). No
  withholding on dividends, interest or royalties paid abroad in ch. 1 (explicit 0 % rules, cited).
-/

namespace MhGlobal.Corporate
open TaxKernel TaxKernel.Global

def wht : Wht :=
  { name := "Non-resident tax (Income Tax Act 1989 § 117)", rules := [
      { kind := .services, rateBp := 1000, statute := "Income Tax Act 1989 § 117 (10 % of the gross fee for services), § 118 (withheld by the client)" },
      { kind := .dividend, rateBp := 0, statute := "Income Tax Act 1989: no tax on dividends paid abroad (Part VI taxes services only)" },
      { kind := .interest, rateBp := 0, statute := "Income Tax Act 1989: no tax on interest paid abroad (Part VI taxes services only)" },
      { kind := .royalty, rateBp := 0, statute := "Income Tax Act 1989: no tax on royalties paid abroad (Part VI taxes services only)" }] }

/-- § 109: $80 on the first $10,000 of gross revenue, 3 % above. -/
def grt (t : Int) : Int := if t ≤ 0 then 0 else 80 + divR .down (300 * pos (t - 10000)) BP
def grtCharge (co : Company) : Charge :=
  charge .salesTax "Tax on gross revenues (§ 109)" co.turnover id grt (statute := "48 MIRC Ch. 1 § 109")

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit, .salesTax],
     run := fun _ g _ => if g.entity != .company then [] else
       wht.charges g.company
       ++ [grtCharge g.company] }]

def absent : List Absent :=
  [{ oecd := .cit, why := "Income Tax Act 1989 taxes wages, gross revenues and non-residents' service fees only; the Net Profit Tax Act 2025 (16 %, § 705) applies to tax years commencing on or after 1 October 2026 (§ 749 (2))" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard grt 5000 == 80
#guard grt 110000 == 3080
#guard wht.amount { kind := .services, amount := 1000 } == 100

end MhGlobal.Corporate
