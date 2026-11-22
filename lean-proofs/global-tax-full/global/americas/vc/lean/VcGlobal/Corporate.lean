import VcGlobal.Pit

/-!
# Saint Vincent and the Grenadines 2025: corporation tax and withholding (1200)

Source: Inland Revenue Department page "Taxes" (ird.gov.vc, Wayback capture 25 Apr 2025,
`vc/law/ird_taxes_wb20250425.html`, ARCHIVE_INDEX.tsv). CIT: "This is a tax paid by all incorporated companies on profits
derived from their business activities ... What is the current rate? Twenty-Eight percent (28%)". WHT: "a tax levied on
income earned by non-resident persons rendering services to a resident person ... Standard rate on services 20% |
Rental 10% | CARICOM - Royalties, Interest and Management Fees only 15%". Grade B (official page; the Income Tax Act
Cap. 435 and the Finance Act No. 10 of 2023 were not read: the latter is a scan without text). The CARICOM 15 % rate
needs the recipient's residence (not an input): not applied; interest, royalties and dividends to other non-residents:
no rate on the page, not modelled.

**Pass 8 (2026-11-21), withholding on payments abroad:** Income Tax Act Cap. 435 s. 66 and the Third Schedule: a payer of interest (para 1 (1) (b)), royalties, licence and branding fees ((d), Act No. 5 of 2019), management charges (e) or commissions and fees (f) to a non-resident deducts 20 % (para 3 (c)), real estate rentals 10 % (para 3 (a)), final; dividends of a resident company are not chargeable income of a non-resident (s. 30 (2); (j) as amended by Act No. 20 of 2020): a cited 0. Corporation tax: Fifth Schedule item 2 as amended by the Finance Act 2023: 28 %. Grade A (replaces the IRD page, grade B).
-/

namespace VcGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon VcGlobal

def regime : CorpRegime :=
  { name := "Corporation tax", sched := Schedule.flat 2800 }

def citStatute : String := "Income Tax Act Cap. 435 Fifth Sched. item 2 as amended by the Finance Act 2023 (No. 10 of 2023): 28 % on every dollar of a company's chargeable income"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 2000, statute := "ITA Cap. 435 s. 66, Third Sched. para 3 (c): 20 % of every dollar, final (para 1 (1) (b) interest)" }, { kind := .royalty, rateBp := 2000, statute := "ITA Cap. 435 s. 66, Third Sched. para 3 (c): 20 % of every dollar, final (para 1 (1) (d) as substituted by Act No. 5 of 2019: royalties, licence and branding fees)" }, { kind := .services, rateBp := 2000, statute := "ITA Cap. 435 s. 66, Third Sched. para 3 (c): 20 % of every dollar, final (para 1 (1) (e) management charge, (f) commission or fee)" }, { kind := .rent, rateBp := 1000, statute := "ITA Cap. 435 Third Sched. para 3 (a): real estate rentals 10 %" }, { kind := .dividend, rateBp := 0, statute := "ITA Cap. 435 s. 30 (2): a dividend from a resident company is not chargeable income of a non-resident; Third Sched. para 1 (1) (a) deleted, (j) excludes such dividends (Act No. 20 of 2020): none withheld" }] }

def citF : Family := corpFamily "1200 Corporation tax" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "Third Sched. para 1 (1) (f) proviso (hoteliers' and exporters' commissions abroad exempt) and treaty rates (s. 66 (3)) not modelled"

#guard regime.citTax { profit := 1000000 } == 280000
#guard wht.amount { kind := .interest, amount := 1000000 } == 200000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 200000
#guard wht.amount { kind := .services, amount := 1000000 } == 200000
#guard wht.amount { kind := .rent, amount := 1000000 } == 100000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 0

end VcGlobal.Corporate
