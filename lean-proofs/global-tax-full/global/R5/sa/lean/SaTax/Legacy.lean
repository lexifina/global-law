import SaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SaTax.country args
