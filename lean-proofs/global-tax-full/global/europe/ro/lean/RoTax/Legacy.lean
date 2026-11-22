import RoTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain RoTax.country args
