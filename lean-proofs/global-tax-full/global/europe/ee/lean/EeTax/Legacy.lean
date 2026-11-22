import EeTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain EeTax.country args
