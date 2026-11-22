import SbGlobal.Pit

/-!
# Solomon Islands 2025: company tax (1200) and withholding on payments to non-residents

Source: Income Tax Act (Cap. 123), Reprint as in force at 5 February 2024 (Legislation Act 2023), copied by the 1.x SB
builder (`cmp20/world/B14-pacific/sb/law/ita.txt`; later amendments not checked).
* **s. 33 (1)**: chargeable income of a person other than an individual or a company not incorporated in Solomon Islands
  "charged at the rate of thirty cents for every dollar"; (2) companies not incorporated there 35 cents (not modelled).
* **s. 36 (1)**: a resident company deducts tax from dividends: (a) resident shareholders 20 %; (b) non-resident
  shareholders "the rate prescribed in section 33(1)": 30 %.
* **s. 34, Sixth Schedule** (non-resident withholding): interest 15 cents in the dollar; professional services 20 %;
  royalties 15 cents; management services 35 cents; lease of property 10 cents.
-/

namespace SbGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat 3000 }

def citStatute : String := "Income Tax Act (Cap. 123) s. 33 (1) (30 cents in the dollar)"

def wht : Wht :=
  { name := "Non-resident withholding tax (Cap. 123 s. 34, s. 36)", rules := [
      { kind := .dividend, rateBp := 3000, statute := "Income Tax Act (Cap. 123) s. 36 (1) (b), s. 33 (1) (30 %)" },
      { kind := .interest, rateBp := 1500, statute := "Income Tax Act (Cap. 123) s. 34, Sixth Schedule (i) (15 cents in the dollar)" },
      { kind := .royalty, rateBp := 1500, statute := "Income Tax Act (Cap. 123) s. 34, Sixth Schedule (iii) (15 cents in the dollar)" },
      { kind := .services, rateBp := 2000, statute := "Income Tax Act (Cap. 123) s. 34, Sixth Schedule (ii) professional services (20 %)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard cit.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .dividend, amount := 1000 } == 300
#guard wht.amount { kind := .interest, amount := 1000 } == 150

end SbGlobal.Corporate
