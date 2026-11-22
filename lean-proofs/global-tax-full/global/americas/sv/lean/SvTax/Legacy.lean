import SvTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SvTax.country args
