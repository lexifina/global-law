import HuTax.Household

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain HuTax.country args
