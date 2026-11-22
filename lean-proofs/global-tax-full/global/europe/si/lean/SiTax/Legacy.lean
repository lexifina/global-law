import SiTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain SiTax.country args
