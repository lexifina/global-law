import StTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain StTax.country args
