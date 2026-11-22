import BbGlobal.Pit

/-!
# Barbados 2025: corporation tax (1200)

Source: Income Tax (Amendment and Validation) Act, 2024-15, s. 6 (BRA, `bb/law/ita_2024-15.txt`, fetched 2026-11-21),
inserting Cap. 73 s. 43 (8): "With effect from income year 2024, commencing 1st January, 2024, the tax payable by a
company upon its taxable income shall be 9 per cent". Grade A. Not modelled: s. 43 (9) (a) 5.5 % for approved small
businesses with gross income of $2 000 000 or less (registration under Cap. 318C is not an input), (9) (b) and (11)
sliding rates (5.5/3/2.5/1 %) for international shipping and for in-scope MNE companies whose parent's jurisdiction has
no top-up tax; s. 43B 4.5 % on qualifying IP income. The Income Tax (Amendment) Act 2025-30 refers to these rates and
does not change them. Withholding on payments to non-residents not read.

**Pass 7 (2026-11-21), withholding on payments abroad:** dividends paid to a non-resident: ITA s. 65 (4) 15 %, cut to 5 % by Act 2018-54 s. 12 (b). Interest, royalties and management or technical fees (s. 64 (1) (e) (i), (vi), (vii)) and services in Barbados (s. 64E) bear "such amount as is prescribed": Income Tax Regulations 1969 reg. 6 not held: grade C.

**Pass 8 (2026-11-21), withholding on payments abroad:** Income Tax Regulations 1969 (made under ITA s. 84; L.R.O. 2007 text from bra.gov.bb, amended in 2010 and 2017 only in other regulations) Part XI: reg. 90 interest to a non-resident 15 %, reg. 90B royalties 15 %, reg. 93A management, administrative, technical or managerial services 15 %. Grade A.
-/

namespace BbGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon BbGlobal

def regime : CorpRegime :=
  { name := "Corporation tax", sched := Schedule.flat 900 }

def citStatute : String := "Income Tax Act Cap. 73 s. 43 (8) (Income Tax (Amendment and Validation) Act 2024-15 s. 6): 9 % from income year 2024"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 500, statute := "ITA Cap. 73 s. 65 (4) as amended by Act 2018-54 s. 12 (b): 5 % to a non-resident" }, { kind := .interest, rateBp := 1500, statute := "Income Tax Regulations 1969 (S.I. 1969 No. 109, L.R.O. 2007) reg. 90 (1): interest to a non-resident 15 % (Government securities exempt, reg. 90 (2))" }, { kind := .royalty, rateBp := 1500, statute := "Income Tax Regulations 1969 (S.I. 1969 No. 109, L.R.O. 2007) reg. 90B: royalties to a non-resident 15 %" }, { kind := .services, rateBp := 1500, statute := "Income Tax Regulations 1969 (S.I. 1969 No. 109, L.R.O. 2007) reg. 93A (1): management, administrative, technical or managerial services 15 %" }] }

def citF : Family := corpFamily "1200 Corporation tax" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "dividends out of exempt or untaxed profits (s. 64 (1) (e) (iv)) not distinguished"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "Income Tax Regulations 1969 reg. 93 (25 % on dividends out of exempt or untaxed profits), reg. 90A (rents 25 %) and reg. 93B (other services) not modelled; ITA amendments after Act 2018-54 not checked for s. 64"

#guard regime.citTax { profit := 1000000 } == 90000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 50000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 150000

end BbGlobal.Corporate
