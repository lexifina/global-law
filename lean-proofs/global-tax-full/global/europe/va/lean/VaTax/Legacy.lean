import VaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain VaTax.country args
