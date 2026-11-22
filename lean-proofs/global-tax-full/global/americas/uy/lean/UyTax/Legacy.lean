import UyTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain UyTax.country args
