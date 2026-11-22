import FmTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain FmTax.country args
