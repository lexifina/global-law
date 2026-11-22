import HrTax.Household

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain HrTax.country args
