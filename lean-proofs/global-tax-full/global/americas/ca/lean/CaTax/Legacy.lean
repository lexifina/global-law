import CaTax.Household

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain CaTax.country args
