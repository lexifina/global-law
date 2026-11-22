import NOTax.Household

/-- `notax [--oecd]`: `--oecd` = the OECD Taxing Wages convention (unrounded lines, `NOTax.linesOecd`). -/
def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain (NOTax.country (args.contains "--oecd")) args
