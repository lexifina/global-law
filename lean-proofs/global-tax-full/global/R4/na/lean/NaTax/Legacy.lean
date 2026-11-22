import NaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain NaTax.country args
