import AtTax.Household

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain AtTax.country args
