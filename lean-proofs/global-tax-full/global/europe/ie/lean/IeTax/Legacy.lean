import IeTax.Household

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain IeTax.country args
