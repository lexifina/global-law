import AgGlobal.Pit

/-!
# Antigua and Barbuda 2025: corporate income tax and withholding (1200)

Source: Income Tax Act Cap. 212 (Revised Laws 1992, laws.gov.ag `cap-212.pdf`, archived `ag/law/ita_cap212_1992.*`) with
the amending Acts read: No. 4 of 2003 (ss. 39, 40), No. 3 of 2008 (s. 32), No. 20 of 2022 (s. 32 (4)). Grade A.
* s. 32 (1) (b) (Act No. 3 of 2008 s. 4): the chargeable income of a company "for the period commencing on the 1st
  January 2008 ... and for subsequent income years" is charged "at the rate of twenty-five percent per dollar".
  Banks (s. 32 (3): 22.5 % with mortgage-rate conditions) and s. 32 (4) (Act No. 20 of 2022: banks, insurers,
  petroleum, energy and telecommunications companies, 10 %) are flagged, not modelled.
* s. 39 (1) (Act No. 4 of 2003 s. 5): interest, rent, annuities paid to a non-resident: 20 %, 25 % to a company; bank
  deposit interest exempt. s. 40 (1): any other payment to a non-resident that s. 5 makes chargeable (royalties, fees,
  dividends): 25 cents on every dollar.
-/

namespace AgGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon AgGlobal

def regime : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 2500 }

def citStatute : String := "Income Tax Act Cap. 212 s. 32 (1) (b) as substituted by Act No. 3 of 2008 s. 4: 25 % from 1 Jan 2008"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 2500, toCompany := some true, statute := "ITA Cap. 212 s. 39 (1) as substituted by Act No. 4 of 2003 s. 5: interest to a company 25 %" }, { kind := .interest, rateBp := 2000, toCompany := some false, statute := "ITA Cap. 212 s. 39 (1) as substituted by Act No. 4 of 2003 s. 5: interest to other persons 20 %" }, { kind := .royalty, rateBp := 2500, statute := "ITA Cap. 212 s. 40 (1): any other payment chargeable under s. 5 to a non-resident: 25 cents on every dollar" }, { kind := .services, rateBp := 2500, statute := "ITA Cap. 212 s. 40 (1): any other payment chargeable under s. 5 to a non-resident: 25 cents on every dollar" }, { kind := .dividend, rateBp := 2500, statute := "ITA Cap. 212 s. 40 (1): any other payment chargeable under s. 5 to a non-resident: 25 cents on every dollar (dividends are income under s. 5)" }] }

def citF : Family := corpFamily "1200 Income tax (companies)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "s. 32 (2)-(4) rates for banks (22.5 % with rate conditions), and the 10 % provision of s. 32 (4) (Act No. 20 of 2022) for banks, insurers, petroleum, energy and telecommunications companies not modelled; s. 33 dividend imputation not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "s. 39 (1) proviso: interest on bank deposits paid to non-residents exempt: not distinguished; treaty rates not modelled"

#guard regime.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .interest, amount := 1000000 } == 250000
#guard wht.amount { kind := .interest, amount := 1000000, toCompany := false } == 200000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 250000
#guard wht.amount { kind := .services, amount := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 250000

end AgGlobal.Corporate
