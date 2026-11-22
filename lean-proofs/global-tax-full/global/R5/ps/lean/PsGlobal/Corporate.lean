import TaxKernel.Global
import R5Common

/-!
# Palestine 2025: income tax on legal persons (1200)

Decree-Law No 8 of 2011 on Income Tax (قرار بقانون رقم (8) لسنة 2011م بشأن ضريبة الدخل) with its amendments, text from
Maqam (An-Najah University legislation database, maqam.najah.edu/legislation/139-142/; status "ساري النفاذ في الضفة
الغربية وغزة"; `law/ps_maqam_itl_dl8_2011*.txt`):
* art. 16(2) as replaced by Decree-Law 5/2015 art. 5: "تـُستوفى الضريبة على الدخل الخاضع للضريبة لأي شخص معنوي بنسبة
  (%15) باستثناء شركات الاتصالات والشركات التي تتمتع بامتياز أو احتكار في السوق الفلسطيني بحيث تخضع لنسبة (%20)".
* art. 7(21) added by Decree-Law 14/2016 art. 3: the first ILS 300,000 of a legal person's net income from agricultural
  activity is exempt.
* losses: offset against other income of the period, the balance carried to at most the five following periods.
Maqam lists no later amendment of art. 16 (DL 14/2016 is the last amending decree-law shown). Flags on the company:
`telecom` / `monopoly` (20 %), `agriculture` (whole profit agricultural: first 300,000 exempt).
**Grade A** (statute text read).
-/

namespace PsGlobal
open TaxKernel TaxKernel.Global R5Common

def citRate (co : Company) : Int :=
  if co.flags.contains "telecom" || co.flags.contains "monopoly" then 2000 else 1500

def it (co : Company) : CorpRegime := { name := "ضريبة الدخل على الشخص المعنوي", sched := Schedule.flat (citRate co) }

/-- art. 7(21): agricultural net income of a legal person exempt up to ILS 300,000. -/
def agriRelief (co : Company) : Company :=
  if co.flags.contains "agriculture" then { co with exemptIncome := co.exemptIncome + min 300000 (pos co.profit) } else co

/-- DL 8/2011 art. 31(2): a resident paying any taxable amount to a non-resident deducts 10 % as a final tax; art. 16(5)
as replaced by DL 4/2014 art. 3: 10 % on dividends withheld at source (DL 4/2014 art. 2 repealed the art. 7(14)
dividend exemption). Maqam texts `law/ps_maqam_itl_dl8_2011_139.txt`, `_140.txt`. -/
def psWht : Wht :=
  { name := "خصم الضريبة من المصدر",
    rules := [{ kind := .dividend, rateBp := 1000, statute := "DL 8/2011 art. 16(5) (DL 4/2014) (10 %)" },
              { kind := .interest, rateBp := 1000, statute := "DL 8/2011 art. 31(2) (10 %, final)" },
              { kind := .royalty, rateBp := 1000, statute := "DL 8/2011 art. 31(2) (10 %, final)" },
              { kind := .services, rateBp := 1000, statute := "DL 8/2011 art. 31(2) (10 %, final)" }] }

def corporate : Family :=
  { name := "1200 ضريبة الدخل (الشخص المعنوي)", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := agriRelief g.company
      [(it co).citCharge co s!"Decree-Law 8/2011 art. 16(2) as replaced by DL 5/2015 ({citRate co / 100} %); art. 7(21) (DL 14/2016)"]
      ++ psWht.charges g.company }

def corporateUnsupported (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["income tax: other exempt income (art. 7) and deduction limits taken as given; withholding on dividends paid to residents (10 %, DL 4/2014) not computed"]
  ++ (if g.company.lossesForward ≠ 0 then ["losses: offset in full (art. on loss relief limits the carry-forward to five periods)"] else [])

#guard ((it {}).citTax { profit := 1000000 }) == 150000
#guard psWht.amount { kind := .royalty, amount := 100000 } == 10000
#guard ((it { flags := ["telecom"] }).citTax { profit := 1000000 }) == 200000
#guard ((it {}).citTax (agriRelief { profit := 1000000, flags := ["agriculture"] })) == 105000

end PsGlobal
