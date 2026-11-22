import GyGlobal.Pit
import TaxKernel.Global2

/-!
# GY 2025: Corporate family — no dated statute text reached (grade C)

* Corporation tax (Corporation Tax Act Cap. 81:03): tried MOLA volumes on the build server hold the Income Tax Act only; would unlock: Cap. 81:03 and the Fiscal Enactments 2024-2025.

**Pass 7 (2026-11-21), withholding:** Income Tax Act Cap. 81:01 (L.R.O. 1/2012, `world/B13-caribbean/gy/law/ita.txt`)
s. 39 (1): withholding tax at the Third Schedule rate (a) on any gross distribution made to a person not resident in
Guyana, (b) on any gross payment (other than the interest of (c)-(e)) to a non-resident not engaged in trade or business in
Guyana; Third Schedule Part I para 1 (as amended to Act 4 of 2003): 20 % on gross distributions and all payments. The
Fiscal Enactments Acts 2012-2026 held were searched: only the 2022 proviso on an individual's small savings interest.
Grade A. The corporation tax itself stays C (Cap. 81:03 L.R.O. 1/2012 reads 40 %/30 %/45 %; the later rate Acts not held).

**Pass 9 (2026-11-21), corporation tax (A):** Cap. 81:03 L.R.O. 1/2012 (MOLA volume 15, archived `gy/law/corporation_tax_act_cap81-03_mola.*`) s. 10: "(a) forty-five per cent of the chargeable profits of a telephone company; (b) forty per cent of the chargeable profits of a commercial company, other than a telephone company; and (c) thirty per cent of the chargeable profits of any other company". Corporation Tax (Amendment) Act No. 5 of 2017 (from the year of income 2017): (c) 30 % -> 27.5 %, new s. 10 (2) dual rate for mixed companies (non-commercial 27.5 %, commercial 40 %), "commercial activity" defined (trading in goods not manufactured by the company, commission agency, telecommunications, banking, non-life insurance), s. 10A minimum tax 2 % of turnover for a commercial company. Act No. 10 of 2019 (from 2019): (c) and s. 10 (2) (b) -> 25 %, new (d) small manufacturing/construction businesses 25 %. Act No. 3 of 2020 and the Fiscal Enactments Acts 2022-2026 change s. 7 (exemptions) only. The company type is not a canonical input: the flags "commercial" and "telephone" select (b) and (a); otherwise 25 %.

**Pass 10 (2026-11-21):** the s. 10 (1) type now comes from the kernel 2.5.0 input `company.sector` (`SectorCorp`, R2-P9-1) instead of the pass 9 flags: "telecom" (a) 45 %; "commercialTrading", "bank", "insurer" (b) 40 % (s. 2 definition of a commercial company, read in `gy/law/cta_cap81_03_wb.txt`), both with the s. 10A minimum of 2 % of turnover; any other sector or none (c) 25 % (ifAbsent := general).
-/

namespace GyGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon GyGlobal

def citStatute : String := "Corporation Tax Act Cap. 81:03 (L.R.O. 1/2012) s. 10 (1): (a) telephone company 45 %, (b) commercial company 40 %, (c) any other company 25 % (30 % -> 27.5 % by Act No. 5 of 2017 s. 2, -> 25 % by Act No. 10 of 2019 s. 3, from the year of income 2019); s. 10 (2) (Act 5/2017, 10/2019): companies with commercial and non-commercial activities: 40 % / 25 %; s. 10A (Act 5/2017 s. 3): minimum tax 2 % of turnover for a commercial company"

def wht : Wht :=
  { name := "Withholding tax (non-residents)",
    rules := [{ kind := .dividend, rateBp := 2000, statute := "ITA Cap. 81:01 s. 39 (1) (a), (b), Third Sched. Part I para 1 (4 of 2003): 20 % on gross distributions and payments to non-residents" },
              { kind := .interest, rateBp := 2000, statute := "ITA Cap. 81:01 s. 39 (1) (a), (b), Third Sched. Part I para 1 (4 of 2003): 20 % on gross distributions and payments to non-residents" },
              { kind := .royalty, rateBp := 2000, statute := "ITA Cap. 81:01 s. 39 (1) (a), (b), Third Sched. Part I para 1 (4 of 2003): 20 % on gross distributions and payments to non-residents" },
              { kind := .services, rateBp := 2000, statute := "ITA Cap. 81:01 s. 39 (1) (a), (b), Third Sched. Part I para 1 (4 of 2003): 20 % on gross distributions and payments to non-residents" }] }

/-- s. 10 (1) by the kernel 2.5.0 input `company.sector` (s. 2: a "commercial company" is one with at least 75 % of gross
income from trading in goods it did not manufacture, and includes any commission agency, any telecommunication company,
any licensed bank and any insurer other than long-term business): telecom (a) 45 %; commercialTrading, bank, insurer (b)
40 %; both with the s. 10A minimum of 2 % of turnover (a commercial company); any other sector or none (c) 25 %. -/
def gyCorp : SectorCorp :=
  { general := { regime := { name := "Corporation tax", sched := Schedule.flat 2500 } },
    statute := citStatute ++ " [s. 10 (1) (c): 25 %]", ifAbsent := .general,
    bySector := [
      { sectors := ["telecom"], rule := { regime := { name := "Corporation tax (telephone company)", sched := Schedule.flat 4500, minBp := 200 } },
        statute := citStatute ++ " [s. 10 (1) (a): 45 %; s. 10A minimum 2 % of turnover]" },
      { sectors := ["commercialTrading", "bank", "insurer"], rule := { regime := { name := "Corporation tax (commercial company)", sched := Schedule.flat 4000, minBp := 200 } },
        statute := citStatute ++ " [s. 10 (1) (b): 40 %; s. 10A minimum 2 % of turnover]" }] }

def citF : Family := gyCorp.family "Corporation tax" wht

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "treaty rates (s. 39 (3)) not modelled"
  ++ when (g.entity == .company && g.company.lossesForward != 0) "losses brought forward: the carry-forward rule was not read (kernel default offset)"
  ++ when (g.entity == .company && g.company.dividendsReceived != 0) "dividends received: taxed in profit as given (exemption not modelled)"
  ++ when (g.entity == .company) "company type read from company.sector (kernel 2.5.0): telecom 45 %; commercialTrading, bank, insurer 40 % (a long-term insurer is not a commercial company: give it another sector); absent or any other sector 25 % (the charge's statute says so); the s. 10 (2) split of a mixed company's profit, the s. 10 (1) (d) small-business rate and the s. 10A proviso not modelled"

#guard wht.amount { kind := .dividend, amount := 1000000 } == 200000
#guard wht.amount { kind := .interest, amount := 1000000 } == 200000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 200000
#guard wht.amount { kind := .services, amount := 1000000 } == 200000
#guard gyCorp.general.regime.citTax { profit := 1000000 } == 250000
#guard (gyCorp.bySector.map fun r => r.rule.regime.citTax { profit := 1000000 }) == [450000, 400000]

end GyGlobal.Corporate
