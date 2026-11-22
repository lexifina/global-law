import NzTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain NzTax.country args
