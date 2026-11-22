import CdTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain CdTax.country args
