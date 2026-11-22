import GaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain GaTax.country args
