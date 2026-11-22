import LsTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain LsTax.country args
