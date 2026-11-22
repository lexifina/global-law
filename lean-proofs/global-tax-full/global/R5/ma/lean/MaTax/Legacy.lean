import MaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MaTax.country args
