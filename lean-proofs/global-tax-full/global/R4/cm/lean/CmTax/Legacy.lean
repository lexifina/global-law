import CmTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain CmTax.country args
