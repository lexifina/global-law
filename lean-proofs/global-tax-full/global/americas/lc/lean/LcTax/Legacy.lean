import LcTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain LcTax.country args
