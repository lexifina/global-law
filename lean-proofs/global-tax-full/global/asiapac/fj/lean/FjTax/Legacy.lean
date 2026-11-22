import FjTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain FjTax.country args
