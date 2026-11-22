import ByTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain ByTax.country args
