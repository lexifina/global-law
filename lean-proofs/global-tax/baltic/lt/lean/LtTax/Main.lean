import LtTax.Tax

/-! `lttax [--euromod]`. `--euromod` (round 15, convention flag for the EUROMOD grids only; statute mode is the
default): the 30-June parameters of `Tax.yearParamsJune30` (2022 child benefits at the BSI / VRP of 1 June 2022 for
the whole year). -/

def countryE (euromod : Bool) : TaxKernel.Country :=
  { code := "LT", name := "Lithuania", currency := "EUR", year := "2025",
    compute := fun c => if euromod then
      let o := LtTax.outWith (LtTax.yearParamsJune30 c.year) c
      { o with detail := o.detail ++ [TaxKernel.Out.dStr "convention" "EUROMOD (--euromod): 30 June parameters"] }
      else LtTax.out c }

def main (args : List String) : IO UInt32 := TaxKernel.countryMain (countryE (args.contains "--euromod")) args
