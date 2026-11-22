import CgTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain CgTax.country args
