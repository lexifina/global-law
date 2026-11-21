import DKTax.Household

/-! `dktax [--oecd] [--euromod]`: `--oecd` = the OECD Taxing Wages conventions for Denmark (`Household.ofCanonWith`).

`--euromod` (round 15, convention flag for the EUROMOD grids only; statute mode is the default): EUROMOD's published
methodology, Country Report Denmark 2022-2025 (software/euromod/country_reports/Y16_CR_DK.pdf, sha256 92c278ee…dd5f),
§ 2.7.3.3 (Table 2.28, average kommuneskat 25,0 / 25,0 / 25,1 / 25,1 % for 2022-2025: "EUROMOD modelling: Since it
is not possible to distinguish among municipalities in the EU-SILC, the average tax rate is applied") and § 2.7.4.3
(Table 2.29, average kirkeskat 0,87 % in every year, "the average tax rate is applied"); church tax is in EUROMOD's
ils_tax (Annex Table A3.3, "Direct taxes (ils_tax): ... church tax (Kirkeskat) (tcr_s)"). Every adult is taken as
a church member: § 2.7.4.3 assigns membership at random to 75 % of the population; the grid households carry no
membership input, and the flag assumes membership (a household attribute, recorded as such in IMPROVE.md round 15).
Explicit `municipalRate7` / `churchRate7` / `church` inputs still win; `--oecd` is not implied. -/

namespace DKTax

/-- EUROMOD Country Report DK, Tables 2.28-2.29: (kommuneskat, kirkeskat) in 10⁻⁷. -/
def euromodRates7 (y : Nat) : Int × Int :=
  if y = 2022 ∨ y = 2023 then (2500000, 87000) else (2510000, 87000)

def setIfAbsent (j : Lean.Json) (k : String) (v : Lean.Json) : Lean.Json :=
  match j with
  | .obj _ => (match j.getObjVal? k with | .ok _ => j | .error _ => j.setObjVal! k v)
  | _ => j

def euromodCanon (c : TaxKernel.Canon) : TaxKernel.Canon :=
  let (m, ch) := euromodRates7 c.year
  { c with raw := setIfAbsent (setIfAbsent (setIfAbsent c.raw "municipalRate7" (Lean.toJson m))
      "churchRate7" (Lean.toJson ch)) "church" (Lean.toJson true) }

def countryE (oecdFlag euromod : Bool) : TaxKernel.Country :=
  { code := "DK", name := "Denmark (København)", currency := "DKK", year := "2025",
    compute := fun c => if euromod then
      let o := out oecdFlag (euromodCanon c)
      { o with detail := o.detail ++ [TaxKernel.Out.dStr "convention"
          "EUROMOD (--euromod): CR DK 2.7.3.3 Table 2.28, 2.7.4.3 Table 2.29"] }
      else out oecdFlag c }

end DKTax

def main (args : List String) : IO UInt32 :=
  TaxKernel.countryMain (DKTax.countryE (args.contains "--oecd") (args.contains "--euromod")) args
