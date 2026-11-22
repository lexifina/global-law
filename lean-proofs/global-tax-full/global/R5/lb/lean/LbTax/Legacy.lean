import LbTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain LbTax.country args
