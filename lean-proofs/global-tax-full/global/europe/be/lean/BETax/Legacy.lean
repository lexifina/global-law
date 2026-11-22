import BETax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain BETax.country args
