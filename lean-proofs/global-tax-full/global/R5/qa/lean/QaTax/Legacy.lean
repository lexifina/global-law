import QaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain QaTax.country args
