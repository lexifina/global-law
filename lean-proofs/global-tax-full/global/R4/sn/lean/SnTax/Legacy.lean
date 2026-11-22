import SnTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SnTax.country args
