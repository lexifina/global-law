import MkGlobal.Pit

/-!
# MK 2025: Social family not reached (grade C)

* 2200 Employer social contributions and payroll taxes (Закон за придонеси од задолжително социјално осигурување (paid by the employee only)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)

* **2200 not levied (cited, gap pass, grade A)**: Закон за придонеси од задолжително социјално осигурување (Сл. весник 142/2008 и измени) чл. 12-13, чл. 25 (ред. 247/2018); Службен весник на РМ; read from lexifina/north-macedonia-law `zakon 142/2008, 247/2018` (commit d2f9cfbe2, e97dd9870, in force 2008 / 1.1.2019): the insured worker is the payer of every contribution (pension 18,8 %, health 7,5 %, injury 0,5 %, unemployment 1,2 % of gross pay, čl. 25); the employer only calculates and remits them (čl. 12-13): they are employee contributions (2100), none is borne by the employer (texts in force in 2025 (no later change to čl. 12-13, 25 in the repository))
-/

namespace MkGlobal.Social
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .sscEmployer, why := "the insured worker is the payer of every contribution (pension 18,8 %, health 7,5 %, injury 0,5 %, unemployment 1,2 % of gross pay, čl. 25); the employer only calculates and remits them (čl. 12-13): they are employee contributions (2100), none is borne by the employer" }]

def notes : List String := ["MK 2200 gap pass: not levied (cited, A)"]

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end MkGlobal.Social
