import UaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain UaTax.country args
