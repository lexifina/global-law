import JmGlobal.Pit

/-!
# Jamaica 2025: income tax on companies (1200)

Source: Tax Administration Jamaica, Technical Advisory 2014/09/IT "2014 Income Tax Rates" (July 2014; Wayback capture
2024-07-19, `jm/law/taj_technical_advisory_2014-09-IT.pdf`, ARCHIVE_INDEX.tsv): "General Income Tax Rates (Section 30 of
the Income Tax Act) With effect from January 1, 2014 (Headline Rates): Regulated Companies 33 1/3% | Unregulated
Companies including large unregulated 25%"; regulated companies are those regulated by the Financial Services
Commission, the Office of Utilities Regulation, the Bank of Jamaica or the Ministry of Finance. Grade B (official
guidance; the Act's s. 30 was not legible in the held scan and later amendments were not checked). The 33 1/3 % rate
for regulated companies, building societies (30 %) and life assurance companies (15 %) need the company's regulator
(not an input): not modelled. Minimum business tax and withholding on payments abroad not read.

**Pass 7 (2026-11-21), withholding on payments abroad:** Income Tax Act s. 40 (1): a resident paying a non-resident interest, royalties, annuities, rent, industrial or commercial information or advice, management or technical services, or plant hire deducts 33 1/3 cents in the dollar (25 cents to an individual). The TAJ Technical Advisory 2014/09/IT lists the 2014 cut to 25 % for unregulated companies only for ss. 38, 39 and 48A, not s. 40. Dividends to non-residents not found in the consolidation: grade C.

**Pass 8 (2026-11-21), withholding on payments abroad:** dividends paid to non-resident companies and individuals: 15 % (PwC Worldwide Tax Summaries, Jamaica, reviewed 29 Sep 2026; facts only): grade B.

**FT review 7 (year in force):** dividends to non-residents: PwC reviewed 3 March 2025 (Internet Archive 2025-08-03) gives 33 1/3 % (companies) and 25 % (individuals), reviewed 12 August 2025 (Internet Archive 2025-12-16) 15 %: a change during 2025 whose provision and date are not held; the rule is withdrawn (grade C).
-/

namespace JmGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon JmGlobal

def regime : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 2500 }

def citStatute : String := "Income Tax Act s. 30 as amended by the Fiscal Incentives (Miscellaneous Provisions) Act (from 1 Jan 2014): unregulated companies 25 %"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 3333, toCompany := some true, statute := "ITA s. 40 (1) (MOJ consolidation, Wayback 2025-02-04): 33 1/3 cents in the dollar to a person other than an individual" }, { kind := .royalty, rateBp := 3333, toCompany := some true, statute := "ITA s. 40 (1) (MOJ consolidation, Wayback 2025-02-04): 33 1/3 cents in the dollar to a person other than an individual" }, { kind := .services, rateBp := 3333, toCompany := some true, statute := "ITA s. 40 (1) (MOJ consolidation, Wayback 2025-02-04): 33 1/3 cents in the dollar to a person other than an individual" }, { kind := .interest, rateBp := 2500, toCompany := some false, statute := "ITA s. 40 (1) (MOJ consolidation, Wayback 2025-02-04): 25 cents in the dollar to an individual" }, { kind := .royalty, rateBp := 2500, toCompany := some false, statute := "ITA s. 40 (1) (MOJ consolidation, Wayback 2025-02-04): 25 cents in the dollar to an individual" }, { kind := .services, rateBp := 2500, toCompany := some false, statute := "ITA s. 40 (1) (MOJ consolidation, Wayback 2025-02-04): 25 cents in the dollar to an individual" }] }

def citF : Family := corpFamily "1200 Income tax (companies)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "regulated companies 33 1/3 %, building societies 30 %, life assurance 15 % not modelled (the regulator is not an input); minimum business tax not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "s. 40 rates read from pages authorised by L.N. 2008-2011 of the consolidation: a later change to s. 40 not checked"
  ++ when (g.entity == .company && g.company.paymentsAbroad.any (·.kind == .dividend)) "1200 withholding on dividends to non-residents not computed (grade C): the rate changed during 2025 (PwC: 33 1/3 % companies / 25 % individuals as reviewed 3 March 2025; 15 % as reviewed 12 August 2025); the amending provision and its date not read"

#guard regime.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .interest, amount := 1000000 } == 333300
#guard wht.amount { kind := .royalty, amount := 1000000 } == 333300
#guard wht.amount { kind := .services, amount := 1000000 } == 333300
#guard wht.amount { kind := .interest, amount := 1000000, toCompany := false } == 250000
#guard wht.amount { kind := .royalty, amount := 1000000, toCompany := false } == 250000
#guard wht.amount { kind := .services, amount := 1000000, toCompany := false } == 250000

end JmGlobal.Corporate
