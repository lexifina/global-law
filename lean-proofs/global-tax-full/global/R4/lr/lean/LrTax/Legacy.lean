import LrTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain LrTax.country args
