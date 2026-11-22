import SbTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SbTax.country args
