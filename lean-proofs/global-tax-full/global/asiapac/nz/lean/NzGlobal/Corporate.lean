import NzGlobal.Pit

/-!
# New Zealand 2025-26: company tax and NRWT (1200)

Income Tax Act 2007: company rate read in Sch. 1 Part A cl. 2 (version as at 10 July 2026 via the Internet Archive, unchanged since 2011: A, session 8); NRWT rates read in ss. RF 7 and RF 8 (session 12, A).
* **Sch. 1 Part A cl. 2**: companies 28 %.
* **subpart RF**: s. RF 7 (2) general rate for NRWT "payment x 0.15" (interest, royalties); s. RF 8 (2) dividends not fully
  imputed "dividend payment x 0.3".

**Session 12 (year in force), withholding grade A.** Income Tax Act 2007, version as at 1 January 2026 (legislation.govt.nz
PDF `act/public/2007/97/en/2026-01-01.pdf`, Internet Archive 2026-03-19; extract `nz/law/nz_ita2007_RF7-RF9_v20260101.txt`):
s. RF 7 (general rate 0.15) carries no amendment note and s. RF 8 (dividends 0.3) none after 2017, so both rates applied
throughout 2024-25 and 2025-26: no split. Not modelled: approved issuer levy (s. RF 12, 0 % NRWT with 2 % levy), treaty
rates, fully imputed dividends with supplementary dividends (s. RF 9: 15 % / 0 %), non-resident contractors' tax.
-/

namespace NzGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat 2800 }

def citStatute : String := "ITA 2007 Sch. 1 Part A cl. 2"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 3000, statute := "ITA 2007 s. RF 8 (2) (dividend not fully imputed, x 0.3)" },
      { kind := .interest, rateBp := 1500, statute := "ITA 2007 s. RF 7 (2) (x 0.15)" },
      { kind := .royalty, rateBp := 1500, statute := "ITA 2007 s. RF 7 (2) (x 0.15)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["imputation credits, the approved issuer levy and the 15 % rate on fully imputed dividends not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 280000
#guard wht.amount { kind := .dividend, amount := 1000 } == 300
#guard wht.amount { kind := .interest, amount := 1000 } == 150
#guard wht.amount { kind := .royalty, amount := 1000 } == 150

end NzGlobal.Corporate
