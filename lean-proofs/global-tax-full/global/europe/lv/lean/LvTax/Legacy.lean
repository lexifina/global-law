import LvTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain LvTax.country args
