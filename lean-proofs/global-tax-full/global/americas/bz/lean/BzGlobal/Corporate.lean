import BzGlobal.Pit

/-!
# BZ 2025: corporate income tax (1200)

Income and Business Tax Act Cap. 55 s. 21 (1): "the tax upon the chargeable income of any person other than an employed person shall be charged at the rate of twenty-five per centum". Companies also pay business tax on gross receipts (Part XI), credited against the income tax: not read, flagged (grade B).

## FT review (2026-11-21, second pass): Income and Business Tax (Amendment) Act, 2024 (No. 40 of 2024)
Source: the Global law copy kept by the 1.x builder (`world/B13-caribbean/bz/law/gl_act_2024_40.txt`; in force
2024-12-11). Section 3 repeals and replaces s. 6: "(2) Commencing from the first day of the basis year 2020 and for
each subsequent year, no tax shall be charged upon the chargeable income of any person other than an employed person."
Section 6 repeals and replaces s. 21 (the 25 per centum of the old s. 21 (1) is gone; the new s. 21 keeps only the
business-tax credit and carry-forward); section 5 repeals s. 20. A company's income tax for 2025 is therefore nil;
companies pay the business tax on gross receipts (Part III), which is not a profit tax and is not modelled here.

**Pass 7 (2026-11-21), withholding on payments abroad:** Income and Business Tax Act Cap. 55 (Rev. Ed. 2020) s. 113: (2) a company paying a dividend deducts tax at the Schedule IX rate (para (h): 15 %); (3) management fees, rental of plant or equipment, technical services and insurance premiums paid to a non-resident: 25 %; (4) interest on loans to a non-resident: 15 %. Royalties are not listed: a cited 0. s. 113 (2A) (Act No. 12 of 2021 s. 6): no deduction from a dividend paid to a related party or to a non-EU-listed foreign company with no PE that self-certifies: those facts are not inputs, so the 15 % is kept and flagged. Grade A.
-/

namespace BzGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon BzGlobal

def regime : CorpRegime :=
  { name := "Income tax (persons other than employed persons)", sched := Schedule.flat 0 }

def citStatute : String := "Income and Business Tax Act Cap. 55 s. 6 (2) as substituted by Act No. 40 of 2024 s. 3: no tax upon the chargeable income of any person other than an employed person (basis years 2020 onwards)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 1500, statute := "Income and Business Tax Act Cap. 55 s. 113 (2), Sched. IX (h): 15 %" }, { kind := .interest, rateBp := 1500, statute := "Cap. 55 s. 113 (4): interest on loans to a non-resident 15 %" }, { kind := .services, rateBp := 2500, statute := "Cap. 55 s. 113 (3): management fees, technical services to a non-resident 25 %" }, { kind := .royalty, rateBp := 0, statute := "Cap. 55 s. 113 (1)-(4): royalties paid to a non-resident are not a payment the section lists: none withheld" }] }

def citF : Family := corpFamily "1200 Income tax (persons other than employed persons)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "dividend exemption of s. 113 (2A) (related party, or a self-certifying foreign company without PE) and the Minister's interest exemption orders (s. 113 (4) proviso) not modelled: 15 % kept"

#guard regime.citTax { profit := 1000000 } == 0
#guard wht.amount { kind := .dividend, amount := 1000000 } == 150000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 250000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 0

end BzGlobal.Corporate
