import PaGlobal.Pit

/-!
# Panama 2025: impuesto sobre la renta de personas jurídicas (1200)

Source: Ley 8 de 2010 (`world/.../pa/src/ley8_2010.txt`): grade B (later amendments not checked).
* Código Fiscal art. 699 as amended: "2011 y siguientes 25%". The alternative minimum (CAIR: 4,67 % of gross taxable
  income for taxable income above B/.1,500,000) is not modelled.
* Dividends: "una cuota de participación del diez por ciento (10%)" withheld (Código Fiscal art. 733): applied to
  dividends paid abroad.

**Pass 8 (2026-11-21), withholding on payments abroad:** interest, royalties and service fees remitted to non-residents: income tax at the 25 % rate on 50 % of the remittance, 12.5 % effective (PwC Worldwide Tax Summaries, Panama, reviewed 4 Aug 2026; facts only). The Código Fiscal text was not reachable (Órgano Judicial PDF 403; Gaceta Oficial behind a script check): grade B.

**FT review 7 (year in force):** the PwC facts are re-cited to the page reviewed 19 August 2025 (Internet Archive 2025-09-10): the same 10 % / 12.5 % rates.
-/

namespace PaGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon PaGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre la renta (personas jurídicas)", sched := Schedule.flat 2500 }

def citStatute : String := "Código Fiscal art. 699 (Ley 8/2010): 25 %"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 1000, statute := "Código Fiscal art. 733 (10 %)" }, { kind := .interest, rateBp := 1250, statute := "Código Fiscal (remittances to non-residents: the 25 % art. 699 rate on 50 % of the amount): 12.5 % (PwC Worldwide Tax Summaries, Panama, reviewed 4 Aug 2026)" }, { kind := .royalty, rateBp := 1250, statute := "Código Fiscal (remittances to non-residents: the 25 % art. 699 rate on 50 % of the amount): 12.5 % (PwC Worldwide Tax Summaries, Panama, reviewed 4 Aug 2026)" }, { kind := .services, rateBp := 1250, statute := "Código Fiscal (remittances to non-residents: the 25 % art. 699 rate on 50 % of the amount): 12.5 % (PwC Worldwide Tax Summaries, Panama, reviewed 4 Aug 2026)" }] }

def citF : Family := corpFamily "1200 Impuesto sobre la renta (personas jurídicas)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "CAIR (art. 699 par. 1: 4,67 % of gross taxable income above B/.1,500,000) not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "Código Fiscal text on remittances abroad not read (Órgano Judicial copy 403, Gaceta Oficial behind a script check): the 12.5 % effective rate is the PwC summary's; exemptions (art. 708) not modelled"

#guard regime.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 100000
#guard wht.amount { kind := .interest, amount := 1000000 } == 125000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 125000
#guard wht.amount { kind := .services, amount := 1000000 } == 125000

end PaGlobal.Corporate
