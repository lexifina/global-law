import HtTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain HtTax.country args
