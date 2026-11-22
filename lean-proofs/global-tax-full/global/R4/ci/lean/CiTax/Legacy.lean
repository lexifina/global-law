import CiTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain CiTax.country args
