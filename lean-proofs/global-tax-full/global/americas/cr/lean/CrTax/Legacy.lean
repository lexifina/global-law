import CrTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain CrTax.country args
