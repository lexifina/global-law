import UzTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain UzTax.country args
