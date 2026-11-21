import FiTax.Household

/-! The `fitax` exe: canonical households (JSONL) in, contract lines out (`TaxKernel.countryMain`).
incomeTax = state income tax on earned and capital income after credits (incl. eläketulon lisävero);
surtaxes = yleisradiovero; localIncomeTax = municipal (+ church, off by default) tax after credits;
employeeSocial = TyEL + unemployment + päivärahamaksu + sairaanhoitomaksu (after its share of credits);
benefits = lapsilisä. Helsinki 5,30 % unless `municipalRateBp` is given.

`--euromod` (round 15, convention flag for the EUROMOD grids only; statute mode is the default): EUROMOD's
published methodology, Country Report Finland 2022-2025 (software/euromod/country_reports/Y16_CR_FI.pdf, sha256
e4613d0f…9c32), § 2.7.7.2 "EUROMOD modelling": "There is no information in the EUROMOD data about municipal tax
rates and church tax rates and, thus, weighted average tax rates are used in simulations", with the rates of
Table 2.42 "Average municipal and church tax rates" (municipal 20,01 / 7,38 / 7,46 / 7,54 %, church 1,39 / 1,38 /
1,37 / 1,39 % for 2022-2025), and Table 2.1 (church income tax tincr_s: "Voluntary but simulated as compulsory").
So every taxpayer is assessed municipal and church tax at those averages (the church tax changes how the credits
are shared, 2.7.7). The church tax is then left out of the line, as EUROMOD's own income list leaves it out of
ils_tax: Annex Table A3.3, "church tax (not part of disposable income as it is voluntary); in order to include it,
set to "+" (tincr_s)"; it is reported in `detail.churchTaxNotInLine`. Explicit `municipalRateBp` / `churchRateBp`
inputs still win. -/

namespace FiTax

/-- EUROMOD Country Report FI, Table 2.42: (municipal, church) average rates in basis points by year. -/
def euromodRatesBp (y : Nat) : Int × Int :=
  if y = 2022 then (2001, 139) else if y = 2023 then (738, 138) else if y = 2024 then (746, 137) else (754, 139)

def setIfAbsent (j : Lean.Json) (k : String) (v : Int) : Lean.Json :=
  match j with
  | .obj _ => (match j.getObjVal? k with | .ok _ => j | .error _ => j.setObjVal! k (Lean.toJson v))
  | _ => j

/-- The household with the `--euromod` rates filled in. -/
def euromodCanon (c : TaxKernel.Canon) : TaxKernel.Canon :=
  let (m, ch) := euromodRatesBp c.year
  { c with raw := setIfAbsent (setIfAbsent c.raw "municipalRateBp" m) "churchRateBp" ch }

/-- Lapsilisä under EUROMOD's reference date, 30 June of the policy year (convention_policy.json
`euromod_convention_mode`: "Nowcasting prices" note Feb 2025, 1.3-1.4), applied to the two mid-year changes of
2022-2025: the December 2022 double payment (laki 983/2022, "tulee voimaan 9 päivänä joulukuuta 2022") was not in
force on 30 June 2022, so 2022 has 12 monthly amounts, not 13; the under-3 increase of 26 € (lapsilisälaki 7 § 5 mom
as in 1299/2023, applied from 1 April 2024) was in force on 30 June 2024, so 2024 has it for 12 months, not 9.
Other years are unchanged. -/
def childBenefitEuromod (c : TaxKernel.Canon) : Int :=
  let cb := childBenefit c
  if c.year = 2022 then cb * 12 / 13
  else if c.year = 2024 then
    cb + 3 * childBenefitUnder3 * (((c.children.map (·.age)).filter (· < 3)).length : Int)
  else cb

/-- `--euromod`: the line at the EUROMOD average rates, without the church tax (Table A3.3); lapsilisä at the
30-June parameters. -/
def outEuromod (c : TaxKernel.Canon) : TaxKernel.Out :=
  let c' := euromodCanon c
  let o := out c'
  let ch := toEur (sumBy (results (ratesOf c') c') (fun x => x.final.church))
  let cb := childBenefitEuromod c'
  { o with localIncomeTax := o.localIncomeTax - ch, benefits := toEur cb,
           detail := (o.detail.filter (fun kv => kv.1 != "childBenefitCents")) ++
             [TaxKernel.Out.d "childBenefitCents" cb, TaxKernel.Out.d "churchTaxNotInLine" ch,
              TaxKernel.Out.dStr "convention" "EUROMOD (--euromod): CR FI 2.7.7.2, Table 2.42, Table A3.3; 30 June"] }

def country (euromod : Bool := false) : TaxKernel.Country :=
  { code := "FI", name := "Finland (Helsinki)", currency := "EUR", year := "2025",
    compute := fun c => if euromod then outEuromod c else out c }
end FiTax

def main (args : List String) : IO UInt32 := TaxKernel.countryMain (FiTax.country (args.contains "--euromod")) args
