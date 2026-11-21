import TaxKernel.World

/-!
# Timor-Leste: wage income tax, income tax on other income, social security, 2025

Access tier A. Sources (Jornal da República, official PDFs saved in `tl/law/`, sha256 in `tl/law/SHA256SUMS`):
* Lei n.º 8/2008, de 30 de junho, Lei Tributária (Série I, N.º 26, 2008; `jr2008_no26.pdf`), republished in its
  current wording by Lei n.º 5/2019, de 27 de agosto (Série I, N.º 33 B, 2019; `lei5_2019.pdf`); the only later change,
  Lei n.º 17/2023 art. 8 (Série I, N.º 32 A, 2023), rewrites the definition of a permanent establishment (art. 1 u))
  and nothing on wages. The State Budget law for 2025 (Lei n.º 8/2024, Série I, N.º 46 F) does not amend the tax law.
  - art. 20: "O imposto sobre salários incide sobre os rendimentos obtidos ... a título de salário ... às taxas
    estabelecidas no Anexo V"; Anexo V 1 a) resident: "US$ 0 - US$ 500 0%; Acima de US$ 500 10% do montante do salário
    acima de US$ 500" (monthly taxable wages); 1 b) non-resident 10 % of all wages.
  - art. 25: wage tax withheld at source discharges the employee (final tax).
  - art. 27 (1) e) income-tax base excludes "os salários sujeitos a imposto sobre salários"; art. 26 + Anexo VI a)
    resident individual "US$0 - US$ 6.000 0%; Superior a US$ 6.000 10%" (annual taxable income).
* Decreto-Lei n.º 20/2017 (regime de inscrição e obrigação contributiva), art. 10 as republished by Decreto-Lei
  n.º 30/2021 (Série I, N.º 49, 2021-12-09): "A taxa contributiva é fixada em 10%, cabendo respetivamente 6% e 4% à
  entidade empregadora e ao trabalhador ... mantendo-se em aplicação ... até que seja aprovado o novo valor"; no
  ceiling for private-sector employees (the cap at the top of the civil-service pay scale applies to State employees).
Currency: US dollar (whole dollars). Unit: individual. Wages are assumed evenly paid over 12 months.
-/

namespace TlTax
open TaxKernel

/-- Anexo V 1 a): monthly wage tax of a resident, 10 % above US$ 500. -/
def wageSched : Schedule := Schedule.flatAbove 500 1000
def wageTaxMonthly (m : Int) : Int := wageSched.tax Rule.unitDown (pos m)
def wageTax (annual : Int) : Int := perPeriod 12 wageTaxMonthly annual

/-- Anexo VI a): annual income tax of a resident individual on non-wage income, 10 % above US$ 6,000. -/
def incomeSched : Schedule := Schedule.flatAbove 6000 1000

/-- DL 20/2017 art. 10: employee contribution 4 %, no ceiling. -/
def social : Contribution := { name := "INSS", sched := Schedule.flat 400 }

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let wt := sumInts (c.adults.map fun a => wageTax a.wages)
  let other (i : Nat) (a : Adult) : Int := pos a.selfEmployment + pos (share c.rentalIncome i)
  let otherIncs := (c.adults.zip (List.range c.adults.length)).map fun (a, i) => other i a
  let it := sumInts (otherIncs.map fun x => incomeSched.tax Rule.unitDown x)
  let ss := sumInts (c.adults.map fun a => social.amount a.wages)
  Out.make c "TL" "USD" (wt + it) (employeeSocial := ss)
    (detail := [Out.d "wageTax" wt, Out.d "incomeTaxOtherIncome" it, Out.d "taxableIncome" (sumInts otherIncs)])
    (unsupported := (if c.interest ≠ 0 ∨ c.dividends ≠ 0 then ["interest and dividends: withholding regime (Lei 8/2008 art. 53-56) and exemptions not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: business-asset gains only (art. 27 (2)); not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: tax treatment not modelled"] else []))

def country : Country := { code := "TL", name := "Timor-Leste", currency := "USD", year := "2025", compute := out }

theorem sched_progressive : wageSched.progressive = true := by decide
def sched : Schedule := wageSched

/- Anexo V: nothing at US$ 500 a month; 10 % of the excess above. -/
#guard wageTaxMonthly 500 = 0 ∧ wageTaxMonthly 1500 = 100
#guard wageTax 18000 = 12 * 100

end TlTax
