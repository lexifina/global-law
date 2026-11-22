import CnTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain CnTax.country args
