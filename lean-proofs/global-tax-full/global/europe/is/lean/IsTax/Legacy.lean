import IsTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain IsTax.country args
